"""
Router Sources - Gestion des ressources découvertes
Endpoints /sources/* et /manage-rag-source
"""
from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.responses import JSONResponse
from typing import Optional
import logging
from datetime import datetime

from core.api_adapter import get_api_adapter
from services.resource_mapper import map_resource_to_api
from routers.auth import verify_admin_token

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Sources"])


# ─── ENDPOINTS FIXES D'ABORD (avant les routes paramétriques) ──────────────

@router.get("/sources/summary")
async def get_sources_summary(status: Optional[str] = "discovered"):
    """
    Statistiques groupées des ressources pour vue synthèse

    Query params:
        status: Filtrer par statut (discovered, geo_validated, rag_ready)
    """
    try:
        adapter = get_api_adapter()
        workflow_manager = adapter.workflow_manager

        resources = workflow_manager.get_resources_by_status(status)

        country_labels = {
            # Europe francophone
            "FR": "France", "BE": "Belgique", "CH": "Suisse",
            "LU": "Luxembourg", "MC": "Monaco",
            # Europe
            "ES": "Espagne", "IT": "Italie", "DE": "Allemagne",
            "PT": "Portugal", "GB": "Royaume-Uni", "NL": "Pays-Bas",
            "AT": "Autriche", "PL": "Pologne", "SE": "Suède",
            "NO": "Norvège", "DK": "Danemark", "FI": "Finlande",
            "IE": "Irlande", "GR": "Grèce", "CZ": "Tchéquie",
            # Amériques
            "US": "États-Unis", "CA": "Canada",
            "MX": "Mexique", "AR": "Argentine", "BR": "Brésil",
            "CO": "Colombie", "CL": "Chili", "PE": "Pérou",
            # Océanie & autres
            "AU": "Australie", "NZ": "Nouvelle-Zélande",
            # Zone internationale
            "INTER": "International",
        }

        by_country = {}
        by_category = {}
        for resource_id, resource_data in resources.items():
            country_code = resource_data.get("country_code", "unknown")
            by_country[country_code] = by_country.get(country_code, 0) + 1

            category = resource_data.get("metadata", {}).get("category", "unknown")
            by_category[category] = by_category.get(category, 0) + 1

        by_country_formatted = {
            code: {"count": count, "label": country_labels.get(code, code)}
            for code, count in by_country.items()
        }

        return JSONResponse(content={
            "success": True,
            "status_filtered": status,
            "total_pending": len(resources),
            "by_country": by_country_formatted,
            "by_category": by_category
        })

    except Exception as e:
        logger.error(f"Erreur get_sources_summary: {e}")
        return JSONResponse(status_code=500, content={
            "success": False,
            "status_filtered": status,
            "total_pending": 0,
            "by_country": {},
            "by_category": {},
            "error": str(e)
        })


@router.get("/sources/validation")
async def get_sources_for_validation():
    """Récupère les sources geo_validated en attente de validation critique"""
    try:
        adapter = get_api_adapter()
        result = adapter.get_sources_for_validation()
        return JSONResponse(content=result)
    except Exception as e:
        logger.error(f"Erreur get_sources_for_validation: {e}")
        return JSONResponse(status_code=500, content={
            "success": False,
            "sources": [],
            "error": str(e)
        })


@router.post("/sources/validate")
async def validate_critical_source(request: Request, admin_id: str = Depends(verify_admin_token)):
    """
    Validation critique d'une source individuelle.
    Vérifie les critères obligatoires avant de valider.
    """
    try:
        data = await request.json()
        source_id = data.get("source_id")
        action = data.get("action")
        modifications = data.get("modifications")
        criteria_checks = data.get("criteria_checks", {})
        auto_transition_rag = data.get("auto_transition_rag", False)

        if not source_id or not action:
            raise HTTPException(status_code=400, detail="source_id et action requis")

        adapter = get_api_adapter()

        if action == "validate_critical" and criteria_checks:
            from core.criteria_validation import get_criteria_validation_manager
            criteria_manager = get_criteria_validation_manager(adapter.workflow_manager)
            verification_result = criteria_manager.verify_all_criteria_checked(
                source_id, criteria_checks, stage="critical"
            )
            if not verification_result["all_checked"]:
                missing = verification_result["missing_criteria"]
                return JSONResponse(status_code=400, content={
                    "success": False,
                    "message": f"Impossible de valider : {len(missing)} critère(s) non vérifié(s)",
                    "data": {
                        "source_id": source_id,
                        "missing_criteria": missing,
                        "total_required": verification_result["total_required"],
                        "checked_count": verification_result["checked_count"]
                    },
                    "error_code": "CRITERIA_NOT_CHECKED"
                })
            criteria_manager.save_criteria_verification(
                source_id, criteria_checks, stage="critical", verified_by="admin_user"
            )

        result = adapter.validate_critical_source(
            source_id, action, "admin_user", modifications,
            auto_transition_rag=auto_transition_rag
        )
        return JSONResponse(content=result)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur validate_critical_source: {e}")
        return JSONResponse(status_code=500, content={
            "success": False,
            "message": f"Erreur: {str(e)}",
            "data": {"source_id": data.get("source_id", "unknown")}
        })


@router.post("/sources/format-rag")
async def format_source_for_rag(request: Request, admin_id: str = Depends(verify_admin_token)):
    """Formate manuellement une source validated pour RAG"""
    try:
        data = await request.json()
        source_id = data.get("source_id")
        if not source_id:
            raise HTTPException(status_code=400, detail="source_id requis")

        adapter = get_api_adapter()
        resource_data = adapter.workflow_manager.unified_data.get(source_id)
        if not resource_data:
            raise HTTPException(status_code=404, detail="Source non trouvée")

        current_status = resource_data.get("workflow_status")
        if current_status != "critical_validated":
            raise HTTPException(
                status_code=400,
                detail=f"Source doit être validée critiquement d'abord (statut actuel: {current_status})"
            )

        success = adapter.workflow_manager.transition_status(
            source_id, "rag_ready", "admin_user", "Formatage manuel pour RAG"
        )

        if success:
            return {"success": True, "message": "Source formatée pour RAG avec succès",
                    "data": {"source_id": source_id, "new_status": "rag_ready"}}
        raise Exception("Échec de la transition vers RAG_READY")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur format_source_for_rag: {e}")
        return JSONResponse(status_code=500, content={
            "success": False,
            "message": f"Erreur: {str(e)}",
            "data": {"source_id": data.get("source_id", "unknown")}
        })


@router.post("/sources/modify-and-validate")
async def modify_and_validate_source(request: Request, admin_id: str = Depends(verify_admin_token)):
    """Modifie une source critical_pending et la valide automatiquement vers RAG"""
    try:
        data = await request.json()
        source_id = data.get("source_id")
        modifications = data.get("modifications", {})

        if not source_id:
            raise HTTPException(status_code=400, detail="source_id requis")

        adapter = get_api_adapter()
        resource_data = adapter.workflow_manager.unified_data.get(source_id)
        if not resource_data:
            raise HTTPException(status_code=404, detail="Source non trouvée")

        current_status = resource_data.get("workflow_status")
        if current_status != "critical_pending":
            raise HTTPException(
                status_code=400,
                detail=f"Source doit être en critical_pending (statut actuel: {current_status})"
            )

        allowed_fields = [
            # Champs V1
            "organization_name", "country_name", "phone", "email", "website", "description",
            # Champs V2
            "direct_link", "is_governmental", "action_type", "platform_name",
            "scope_audience", "scope_violence", "scope_anonymous",
        ]
        for key, value in modifications.items():
            if key in allowed_fields:
                resource_data[key] = value

        success1 = adapter.workflow_manager.transition_status(
            source_id, "critical_validated", "admin_user", "Source modifiée et validée"
        )
        if not success1:
            raise Exception("Échec de la transition vers critical_validated")

        success2 = adapter.workflow_manager.transition_status(
            source_id, "rag_ready", "admin_user", "Formatage automatique après modification"
        )
        if success2:
            return {"success": True,
                    "message": "Source modifiée et ajoutée au RAG avec succès",
                    "data": {"source_id": source_id, "new_status": "rag_ready"}}
        raise Exception("Échec de la transition vers RAG_READY")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur modify_and_validate_source: {e}")
        return JSONResponse(status_code=500, content={
            "success": False,
            "message": f"Erreur: {str(e)}",
            "data": {"source_id": data.get("source_id", "unknown")}
        })


# ─── ENDPOINTS PARAMÉTRIQUES (après les routes fixes) ──────────────────────

@router.get("/sources")
async def list_sources(status: Optional[str] = None):
    """
    Liste les ressources, optionnellement filtrées par statut.
    Utilise resource_mapper pour un mapping cohérent JSON→API.
    """
    try:
        adapter = get_api_adapter()
        all_resources = adapter.workflow_manager.unified_data

        filtered = {
            rid: res for rid, res in all_resources.items()
            if not status or res.get("workflow_status") == status
        }

        sources_list = [map_resource_to_api(rid, res) for rid, res in filtered.items()]

        return JSONResponse(content={
            "success": True,
            "total": len(sources_list),
            "sources": sources_list
        })

    except Exception as e:
        logger.error(f"Erreur list_sources: {e}")
        return JSONResponse(status_code=500, content={
            "success": False,
            "total": 0,
            "sources": [],
            "error": str(e)
        })


@router.get("/sources/{source_id}/extracted-data")
async def get_extracted_data(source_id: str):
    """Récupère les données extraites d'une ressource (téléphone, URL, email)"""
    try:
        from core.extracted_data import get_extracted_data_manager

        adapter = get_api_adapter()
        extracted_manager = get_extracted_data_manager(adapter.workflow_manager)

        resource = extracted_manager._get_resource_by_id(source_id)
        if not resource:
            raise HTTPException(status_code=404, detail=f"Ressource {source_id} non trouvée")

        extracted_data = extracted_manager.extract_contact_data(resource)
        contact_data = {
            "urls": [extracted_data.url] if extracted_data.url else [],
            "emails": [extracted_data.email] if extracted_data.email else [],
            "phones": [extracted_data.phone] if extracted_data.phone else [],
            "additional_notes": ""
        }

        return JSONResponse(status_code=200, content={
            "success": True,
            "message": "Données extraites avec succès",
            "resource_id": source_id,
            "title": resource.get("name", resource.get("organization_name", "")),
            "status": resource.get("status", resource.get("workflow_status", "critical_pending")),
            "contact_data": contact_data,
            "modification_history": extracted_data.modification_history
        })

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur get_extracted_data pour {source_id}: {e}")
        return JSONResponse(status_code=500, content={
            "success": False,
            "message": f"Erreur lors de l'extraction des données: {str(e)}",
            "data": {"source_id": source_id}
        })


@router.post("/sources/{source_id}/update-extracted-data")
async def update_extracted_data(source_id: str, request: Request, admin_id: str = Depends(verify_admin_token)):
    """Met à jour les données extraites d'une ressource (édition inline)"""
    try:
        from core.extracted_data import get_extracted_data_manager

        data = await request.json()

        updated_fields = {}
        if "urls" in data and data["urls"]:
            updated_fields["url"] = data["urls"][0]
        if "emails" in data and data["emails"]:
            updated_fields["email"] = data["emails"][0]
        if "phones" in data and data["phones"]:
            updated_fields["phone"] = data["phones"][0]
        if "additional_notes" in data:
            updated_fields["additional_notes"] = data["additional_notes"]

        if not updated_fields:
            raise HTTPException(status_code=400, detail="Aucune donnée à mettre à jour")

        adapter = get_api_adapter()
        extracted_manager = get_extracted_data_manager(adapter.workflow_manager)
        updated_resource = extracted_manager.update_contact_data(
            source_id, updated_fields, modified_by="admin_user"
        )
        extracted_data = extracted_manager.extract_contact_data(updated_resource)

        return JSONResponse(status_code=200, content={
            "success": True,
            "message": "Données mises à jour avec succès",
            "data": {
                "source_id": source_id,
                "updated_resource": updated_resource,
                "extracted_data": extracted_data.to_dict(),
                "modification_history": extracted_data.modification_history
            }
        })

    except HTTPException:
        raise
    except ValueError as e:
        logger.error(f"Erreur de validation update_extracted_data: {e}")
        return JSONResponse(status_code=404, content={
            "success": False, "message": str(e), "data": {"source_id": source_id}
        })
    except Exception as e:
        logger.error(f"Erreur update_extracted_data pour {source_id}: {e}")
        return JSONResponse(status_code=500, content={
            "success": False,
            "message": f"Erreur lors de la mise à jour: {str(e)}",
            "data": {"source_id": source_id}
        })


@router.get("/sources/{source_id}/validation-criteria")
async def get_validation_criteria(source_id: str, stage: str = "critical"):
    """Récupère les critères de validation pour une ressource"""
    try:
        from core.criteria_validation import get_criteria_validation_manager

        adapter = get_api_adapter()
        criteria_manager = get_criteria_validation_manager(adapter.workflow_manager)
        criteria_set = criteria_manager.get_validation_criteria(source_id, stage)

        return JSONResponse(status_code=200, content={
            "success": True,
            "message": "Critères de validation récupérés avec succès",
            "data": {
                "source_id": source_id,
                "stage": stage,
                "criteria_set": criteria_set.to_dict()
            }
        })

    except ValueError as e:
        return JSONResponse(status_code=404, content={
            "success": False, "message": str(e), "data": {"source_id": source_id}
        })
    except Exception as e:
        logger.error(f"Erreur get_validation_criteria pour {source_id}: {e}")
        return JSONResponse(status_code=500, content={
            "success": False,
            "message": f"Erreur lors de la récupération des critères: {str(e)}",
            "data": {"source_id": source_id}
        })


@router.post("/sources/{source_id}/verify-criteria")
async def verify_validation_criteria(source_id: str, request: Request, admin_id: str = Depends(verify_admin_token)):
    """Vérifie que tous les critères obligatoires sont cochés avant validation finale"""
    try:
        from core.criteria_validation import get_criteria_validation_manager

        data = await request.json()
        criteria_checks = data.get("criteria_checks", {})
        stage = data.get("stage", "critical")

        if not criteria_checks:
            raise HTTPException(
                status_code=400,
                detail="criteria_checks requis (dict {criterion_id: bool})"
            )

        adapter = get_api_adapter()
        criteria_manager = get_criteria_validation_manager(adapter.workflow_manager)
        verification_result = criteria_manager.verify_all_criteria_checked(
            source_id, criteria_checks, stage
        )

        if verification_result["all_checked"]:
            criteria_manager.save_criteria_verification(
                source_id, criteria_checks, stage, verified_by="admin_user"
            )

        return JSONResponse(status_code=200, content={
            "success": True,
            "message": "Vérification des critères terminée",
            "data": {
                "source_id": source_id,
                "stage": stage,
                "verification_result": verification_result,
                "can_proceed": verification_result["all_checked"]
            }
        })

    except HTTPException:
        raise
    except ValueError as e:
        return JSONResponse(status_code=404, content={
            "success": False, "message": str(e), "data": {"source_id": source_id}
        })
    except Exception as e:
        logger.error(f"Erreur verify_validation_criteria pour {source_id}: {e}")
        return JSONResponse(status_code=500, content={
            "success": False,
            "message": f"Erreur lors de la vérification: {str(e)}",
            "data": {"source_id": source_id}
        })


@router.get("/sources/{source_id}")
async def get_source_by_id(source_id: str):
    """Récupère les détails d'une ressource par son ID"""
    try:
        adapter = get_api_adapter()
        workflow_manager = adapter.workflow_manager

        if source_id not in workflow_manager.unified_data:
            return JSONResponse(status_code=404, content={
                "success": False,
                "error": f"Resource {source_id} not found"
            })

        resource_data = workflow_manager.unified_data[source_id]
        mapped = map_resource_to_api(source_id, resource_data)
        # Ajouter les champs étendus non présents dans map_resource_to_api
        mapped.update({
            "metadata": resource_data.get("metadata", {}),
            "validation_history": resource_data.get("validation_history", []),
            "contact_url": resource_data.get("contact_url", ""),
            "languages": resource_data.get("languages", []),
            "target_audience": resource_data.get("target_audience", []),
        })

        return JSONResponse(content={"success": True, "resource": mapped})

    except Exception as e:
        logger.error(f"Erreur get_source_by_id/{source_id}: {e}")
        return JSONResponse(status_code=500, content={"success": False, "error": str(e)})


# ─── GESTION RAG ────────────────────────────────────────────────────────────

@router.post("/manage-rag-source")
async def manage_rag_source(request: Request, admin_id: str = Depends(verify_admin_token)):
    """Gère les sources RAG : suppression ou remise en attente"""
    try:
        data = await request.json()
        source_key = data.get("source_key")
        action = data.get("action")

        if not source_key or not action:
            raise HTTPException(status_code=400, detail="source_key et action requis")

        adapter = get_api_adapter()
        source_id = None

        # Chercher d'abord dans rag_data
        for rid, rag_resource in adapter.workflow_manager.rag_data.items():
            if rag_resource.get("organization_name") == source_key or rid == source_key:
                source_id = rid
                break

        # Sinon dans unified_data
        if not source_id:
            for uid, resource_data in adapter.workflow_manager.unified_data.items():
                if resource_data.get("organization_name") == source_key or uid == source_key:
                    source_id = uid
                    break

        if not source_id:
            raise HTTPException(status_code=404, detail="Source non trouvée")

        resource_data = adapter.workflow_manager.unified_data.get(source_id)

        # Source orpheline dans rag_data seulement
        if not resource_data and action == "delete":
            logger.warning(f"Source {source_id} trouvée seulement dans rag_data - nettoyage")
            if source_id in adapter.workflow_manager.rag_data:
                del adapter.workflow_manager.rag_data[source_id]
                adapter.workflow_manager._save_json(
                    adapter.workflow_manager.rag_data, adapter.workflow_manager.rag_file
                )
            return {"success": True, "message": "Source orpheline supprimée du RAG",
                    "data": {"source_key": source_key, "action": action}}

        if not resource_data:
            raise HTTPException(status_code=404, detail="Source non trouvée dans unified_data")

        current_status = resource_data.get("workflow_status")

        if action == "revert_to_pending" and current_status != "rag_ready":
            raise HTTPException(
                status_code=400,
                detail=f"Source doit être RAG_READY pour être remise en attente (statut actuel: {current_status})"
            )

        if action == "delete":
            deleted_from_unified = False
            deleted_from_rag = False

            if source_id in adapter.workflow_manager.unified_data:
                del adapter.workflow_manager.unified_data[source_id]
                adapter.workflow_manager._save_json(
                    adapter.workflow_manager.unified_data, adapter.workflow_manager.unified_file
                )
                deleted_from_unified = True

            if source_id in adapter.workflow_manager.rag_data:
                del adapter.workflow_manager.rag_data[source_id]
                adapter.workflow_manager._save_json(
                    adapter.workflow_manager.rag_data, adapter.workflow_manager.rag_file
                )
                deleted_from_rag = True

            message = "Source supprimée définitivement" if (deleted_from_unified or deleted_from_rag) else "Source déjà supprimée"

        elif action == "revert_to_pending":
            adapter.workflow_manager.unified_data[source_id]["workflow_status"] = "critical_pending"
            adapter.workflow_manager.unified_data[source_id].setdefault("validation_history", []).append({
                "from_status": "rag_ready",
                "to_status": "critical_pending",
                "admin_id": "admin_user",
                "timestamp": datetime.now().isoformat(),
                "notes": "Remise en attente manuelle depuis RAG"
            })
            adapter.workflow_manager._save_json(
                adapter.workflow_manager.unified_data, adapter.workflow_manager.unified_file
            )
            if source_id in adapter.workflow_manager.rag_data:
                del adapter.workflow_manager.rag_data[source_id]
                adapter.workflow_manager._save_json(
                    adapter.workflow_manager.rag_data, adapter.workflow_manager.rag_file
                )
            message = "Source remise en attente de validation"

        else:
            raise HTTPException(status_code=400, detail=f"Action non supportée: {action}")

        return {"success": True, "message": message,
                "data": {"source_key": source_key, "action": action}}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur manage_rag_source: {e}")
        return JSONResponse(status_code=500, content={
            "success": False,
            "message": f"Erreur: {str(e)}",
            "error": str(e)
        })
