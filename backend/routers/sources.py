"""
Router Sources — /sources/*, /manage-rag-source

Responsabilités :
  - Lecture des ressources (liste, détail, stats)
  - Modification des champs éditables (PATCH)
  - Validation/rejet individuel (chaînes de transitions automatiques)
  - Gestion post-export RAG (suppression, remise en attente)

Dépendances internes :
  - services/resource_mapper.py  → mapping JSON → contrat API (source unique de vérité)
  - core/workflow_manager.py     → transitions d'état et persistance
"""
from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.responses import JSONResponse
from typing import Optional
import logging
from datetime import datetime

from core.api_adapter import get_api_adapter
from services.resource_mapper import map_resource_to_api, map_resources_list
from routers.auth import verify_admin_token

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Sources"])

# ─── Champs modifiables par l'admin ──────────────────────────────────────────
# Toute modification de cette liste impacte PATCH et la validation métier.
EDITABLE_FIELDS = {
    "name", "website", "direct_link", "phone", "email",
    "description", "action_type", "is_governmental",
    "scope_audience", "scope_violence", "scope_anonymous",
}

# ─── Chaînes de transitions « approve » par statut ───────────────────────────
# Quand on approuve, plusieurs transitions peuvent s'enchaîner automatiquement.
# geo_pending → geo_validated → critical_pending  (intermédiaire non visible)
# critical_pending → critical_validated → rag_ready
APPROVE_CHAINS = {
    "geo_pending":      ["geo_validated", "critical_pending"],
    "critical_pending": ["critical_validated", "rag_ready"],
}

REJECT_TARGETS = {
    "geo_pending":      "geo_rejected",
    "critical_pending": "critical_rejected",
}


def _apply_transitions(wm, resource_id: str, targets: list[str], admin_id: str, notes: str) -> None:
    """Applique une chaîne de transitions. Lève une exception dès que l'une échoue."""
    for target in targets:
        ok = wm.transition_status(resource_id, target, admin_id, notes)
        if not ok:
            raise ValueError(f"Transition vers '{target}' refusée par le workflow_manager")


# ─── ROUTES FIXES (avant les routes paramétriques) ───────────────────────────

@router.get("/sources/summary")
async def get_sources_summary(status: Optional[str] = "geo_pending"):
    """Stats groupées par pays et catégorie pour un statut de workflow donné."""
    try:
        adapter = get_api_adapter()
        resources = adapter.workflow_manager.get_resources_by_status(status)

        by_country: dict = {}
        by_category: dict = {}

        for resource_data in resources.values():
            code  = resource_data.get("country_code", "unknown")
            label = resource_data.get("country_name", code)
            entry = by_country.setdefault(code, {"count": 0, "label": label})
            entry["count"] += 1

            category = resource_data.get("metadata", {}).get("category", "unknown")
            by_category[category] = by_category.get(category, 0) + 1

        return JSONResponse(content={
            "success": True,
            "status_filtered": status,
            "total_pending": len(resources),
            "by_country": by_country,
            "by_category": by_category,
        })

    except Exception as e:
        logger.error(f"Erreur get_sources_summary: {e}")
        return JSONResponse(status_code=500, content={
            "success": False,
            "status_filtered": status,
            "total_pending": 0,
            "by_country": {},
            "by_category": {},
        })


@router.get("/sources")
async def list_sources(status: Optional[str] = None):
    """Liste les ressources, filtrées optionnellement par workflow_status."""
    try:
        adapter = get_api_adapter()
        wm = adapter.workflow_manager
        raw = wm.get_resources_by_status(status) if status else wm.unified_data
        sources = map_resources_list(raw)

        return JSONResponse(content={
            "success": True,
            "total": len(sources),
            "sources": sources,
        })

    except Exception as e:
        logger.error(f"Erreur list_sources: {e}")
        return JSONResponse(status_code=500, content={
            "success": False,
            "total": 0,
            "sources": [],
        })


@router.post("/manage-rag-source")
async def manage_rag_source(request: Request, admin_id: str = Depends(verify_admin_token)):
    """
    Actions post-export sur les ressources RAG.

    Actions supportées :
      - delete          → suppression définitive (working_resources.json + rag_resources.json)
      - revert_to_pending → remet en critical_pending et retire de rag_resources.json
    """
    try:
        data = await request.json()
        source_key = data.get("source_key")
        action     = data.get("action")

        if not source_key or not action:
            raise HTTPException(status_code=400, detail="source_key et action requis")

        adapter = get_api_adapter()
        wm = adapter.workflow_manager

        # Résolution de l'ID : accepte UUID ou nom d'organisation
        source_id = None
        for rid, res in {**wm.rag_data, **wm.unified_data}.items():
            if rid == source_key or res.get("organization_name") == source_key or res.get("name") == source_key:
                source_id = rid
                break

        if action == "delete":
            deleted = False
            for store, filename in [(wm.unified_data, wm.unified_file), (wm.rag_data, wm.rag_file)]:
                if source_id and source_id in store:
                    del store[source_id]
                    wm._save_json(store, filename)
                    deleted = True
            return JSONResponse(content={
                "success": True,
                "message": "Ressource supprimée définitivement" if deleted else "Ressource introuvable",
                "data": {"source_key": source_key, "action": action},
            })

        if not source_id or source_id not in wm.unified_data:
            raise HTTPException(status_code=404, detail="Ressource non trouvée")

        resource_data  = wm.unified_data[source_id]
        current_status = resource_data.get("workflow_status", "")

        if action == "revert_to_pending":
            if current_status != "rag_ready":
                raise HTTPException(
                    status_code=400,
                    detail=f"La ressource doit être rag_ready pour être remise en attente (statut : {current_status})"
                )
            resource_data["workflow_status"] = "critical_pending"
            resource_data.setdefault("validation_history", []).append({
                "from_status": "rag_ready",
                "to_status":   "critical_pending",
                "admin_id":    admin_id,
                "timestamp":   datetime.now().isoformat(),
                "notes":       "Remise en attente manuelle",
            })
            wm._save_json(wm.unified_data, wm.unified_file)

            if source_id in wm.rag_data:
                del wm.rag_data[source_id]
                wm._save_json(wm.rag_data, wm.rag_file)

            return JSONResponse(content={
                "success": True,
                "message": "Ressource remise en critical_pending",
                "data": {"source_key": source_key, "action": action},
            })

        raise HTTPException(status_code=400, detail=f"Action non supportée : {action}")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur manage_rag_source: {e}")
        return JSONResponse(status_code=500, content={"success": False, "message": str(e)})


# ─── ROUTES PARAMÉTRIQUES ────────────────────────────────────────────────────

@router.get("/sources/{source_id}")
async def get_source_by_id(source_id: str):
    """Détail complet d'une ressource."""
    try:
        adapter = get_api_adapter()
        wm = adapter.workflow_manager

        if source_id not in wm.unified_data:
            raise HTTPException(status_code=404, detail=f"Ressource {source_id} non trouvée")

        mapped = map_resource_to_api(source_id, wm.unified_data[source_id])
        mapped["validation_history"] = wm.unified_data[source_id].get("validation_history", [])

        return JSONResponse(content={"success": True, "resource": mapped})

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur get_source_by_id/{source_id}: {e}")
        return JSONResponse(status_code=500, content={"success": False, "error": str(e)})


@router.patch("/sources/{source_id}")
async def patch_source(source_id: str, request: Request, admin_id: str = Depends(verify_admin_token)):
    """
    Modifie les champs éditables d'une ressource.

    - Accepté pour tous les statuts sauf rag_ready.
    - Seuls les champs déclarés dans EDITABLE_FIELDS sont appliqués.
    """
    try:
        data = await request.json()
        adapter = get_api_adapter()
        wm = adapter.workflow_manager

        resource_data = wm.unified_data.get(source_id)
        if not resource_data:
            raise HTTPException(status_code=404, detail="Ressource non trouvée")

        current_status = resource_data.get("workflow_status", "")
        if current_status == "rag_ready":
            raise HTTPException(
                status_code=400,
                detail="Impossible de modifier une ressource déjà exportée en rag_ready"
            )

        updated = {k: v for k, v in data.items() if k in EDITABLE_FIELDS}
        if not updated:
            raise HTTPException(
                status_code=400,
                detail=f"Aucun champ éditable fourni. Champs acceptés : {sorted(EDITABLE_FIELDS)}"
            )

        resource_data.update(updated)
        resource_data.setdefault("modification_history", []).append({
            "timestamp":   datetime.now().isoformat(),
            "modified_by": admin_id,
            "fields":      list(updated.keys()),
        })
        wm._save_json(wm.unified_data, wm.unified_file)

        return JSONResponse(content={
            "success": True,
            "message": f"{len(updated)} champ(s) mis à jour",
            "data": {
                "source_id":      source_id,
                "updated_fields": updated,
                "workflow_status": current_status,
            },
        })

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur patch_source/{source_id}: {e}")
        return JSONResponse(status_code=500, content={"success": False, "message": str(e)})


@router.post("/sources/{source_id}/validate")
async def validate_source(source_id: str, admin_id: str = Depends(verify_admin_token)):
    """
    Valide une ressource selon son statut courant.

    geo_pending      → geo_validated → critical_pending   (intermédiaire automatique)
    critical_pending → critical_validated → rag_ready     (écrit dans rag_resources.json)
    """
    try:
        adapter = get_api_adapter()
        wm = adapter.workflow_manager

        resource_data = wm.unified_data.get(source_id)
        if not resource_data:
            raise HTTPException(status_code=404, detail="Ressource non trouvée")

        current_status = resource_data.get("workflow_status", "")
        chain = APPROVE_CHAINS.get(current_status)
        if not chain:
            raise HTTPException(
                status_code=400,
                detail=f"La ressource n'est pas dans un statut validable (statut : {current_status})"
            )

        _apply_transitions(wm, source_id, chain, admin_id, "Validation manuelle")

        final_status = resource_data.get("workflow_status", "")
        return JSONResponse(content={
            "success": True,
            "message": f"Ressource validée → {final_status}",
            "data": {"source_id": source_id, "new_status": final_status},
        })

    except HTTPException:
        raise
    except ValueError as e:
        logger.error(f"Erreur de transition validate_source/{source_id}: {e}")
        return JSONResponse(status_code=422, content={"success": False, "message": str(e)})
    except Exception as e:
        logger.error(f"Erreur validate_source/{source_id}: {e}")
        return JSONResponse(status_code=500, content={"success": False, "message": str(e)})


@router.post("/sources/{source_id}/reject")
async def reject_source(source_id: str, admin_id: str = Depends(verify_admin_token)):
    """
    Rejette une ressource selon son statut courant.

    geo_pending      → geo_rejected      (terminal)
    critical_pending → critical_rejected (terminal)
    """
    try:
        adapter = get_api_adapter()
        wm = adapter.workflow_manager

        resource_data = wm.unified_data.get(source_id)
        if not resource_data:
            raise HTTPException(status_code=404, detail="Ressource non trouvée")

        current_status = resource_data.get("workflow_status", "")
        target = REJECT_TARGETS.get(current_status)
        if not target:
            raise HTTPException(
                status_code=400,
                detail=f"La ressource n'est pas dans un statut rejectable (statut : {current_status})"
            )

        _apply_transitions(wm, source_id, [target], admin_id, "Rejet manuel")

        return JSONResponse(content={
            "success": True,
            "message": f"Ressource rejetée → {target}",
            "data": {"source_id": source_id, "new_status": target},
        })

    except HTTPException:
        raise
    except ValueError as e:
        logger.error(f"Erreur de transition reject_source/{source_id}: {e}")
        return JSONResponse(status_code=422, content={"success": False, "message": str(e)})
    except Exception as e:
        logger.error(f"Erreur reject_source/{source_id}: {e}")
        return JSONResponse(status_code=500, content={"success": False, "message": str(e)})
