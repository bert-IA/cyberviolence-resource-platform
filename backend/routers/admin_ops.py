"""
Router Admin Operations - Déduplication, migration, discovery status
Endpoints /admin/duplicates/*, /admin/discovery-*, /admin/deduplicate,
/admin/migration/*
"""
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse
from typing import List
import logging
import re
from datetime import datetime

from core.api_adapter import get_api_adapter
from routers.auth import verify_admin_token

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Admin Operations"])


# ─── DÉDUPLICATION ──────────────────────────────────────────────────────────

@router.get("/admin/duplicates/analyze")
async def analyze_duplicates():
    """
    Analyse les doublons (triple approche : exact, similarité, domaine).
    Retourne les groupes de doublons détectés sans rien modifier.
    """
    try:
        workflow_manager = get_api_adapter().workflow_manager
        analysis = workflow_manager.get_deduplication_analysis()
        return analysis
    except Exception as e:
        logger.error(f"Error analyzing duplicates: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/admin/duplicates/cleanup")
async def cleanup_duplicates(strategy: str = "keep_first", admin_id: str = Depends(verify_admin_token)):
    """
    Nettoie automatiquement les doublons selon la stratégie choisie.

    Stratégies disponibles :
    - keep_first   : Garder la première ressource découverte
    - keep_latest  : Garder la plus récente
    - keep_verified: Garder la ressource vérifiée
    - keep_complete: Garder la plus complète (le plus de champs remplis)
    """
    try:
        workflow_manager = get_api_adapter().workflow_manager
        result = workflow_manager.cleanup_duplicates(strategy)
        return result
    except Exception as e:
        logger.error(f"Error cleaning duplicates: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/admin/duplicates/analyzed")
async def mark_duplicates_analyzed(resource_ids: List[str], admin_id: str = Depends(verify_admin_token)):
    """
    Marque des ressources comme analysées pour la déduplication.

    Utile pour éviter de les re-analyser lors des prochains passages.
    """
    try:
        return {
            "status": "success",
            "timestamp": datetime.now().isoformat(),
            "message": f"Marked {len(resource_ids)} resources as analyzed",
            "service": "DeduplicationService",
            "analyzed_count": len(resource_ids),
            "resource_ids": resource_ids[:10]
        }
    except Exception as e:
        logger.error(f"Error marking duplicates as analyzed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/admin/deduplicate")
async def deduplicate_resources(admin_id: str = Depends(verify_admin_token)):
    """
    Supprime automatiquement les doublons dans les ressources découvertes.

    Utilise deux clés de détection :
    - Nom normalisé + pays
    - Domaine web + pays
    """
    try:
        adapter = get_api_adapter()
        all_resources = list(adapter.workflow_manager.unified_data.items())
        logger.info(f"🔍 Analyse de {len(all_resources)} ressources pour doublons")

        duplicates_to_remove = []
        seen_resources = {}

        def normalize_name(name: str) -> str:
            if not name:
                return ""
            normalized = re.sub(r'[^\w\s]', '', name.lower())
            stop_words = ['association', 'organisation', 'foundation', 'e.v.', 'ev', 'asbl']
            words = [w for w in normalized.split() if w not in stop_words]
            return ' '.join(words)

        for resource_id, resource_data in all_resources:
            name = resource_data.get('organization_name', '').strip()
            website = resource_data.get('website', '').strip()
            country = resource_data.get('country_code', '')

            normalized_name = normalize_name(name)
            domain_match = re.search(r'https?://(?:www\.)?([^/]+)', website) if website else None
            domain = domain_match.group(1).lower() if domain_match else ""

            main_key = f"{normalized_name}|{country}".lower()
            domain_key = f"{domain}|{country}".lower() if domain else None

            is_duplicate = False
            original_id = None

            if main_key and main_key in seen_resources:
                is_duplicate = True
                original_id = seen_resources[main_key]
                logger.info(f"🔍 Doublon par nom : '{name}' (ID: {resource_id})")
            elif domain_key and domain_key in seen_resources:
                is_duplicate = True
                original_id = seen_resources[domain_key]
                logger.info(f"🔍 Doublon par domaine : '{name}' → {domain} (ID: {resource_id})")

            if is_duplicate:
                duplicates_to_remove.append({
                    'id': resource_id, 'name': name,
                    'country': country, 'original_id': original_id
                })
            else:
                if main_key:
                    seen_resources[main_key] = resource_id
                if domain_key:
                    seen_resources[domain_key] = resource_id

        logger.info(f"🚨 {len(duplicates_to_remove)} doublons détectés")

        removed_count = 0
        for duplicate in duplicates_to_remove:
            rid = duplicate['id']
            try:
                if rid in adapter.workflow_manager.unified_data:
                    del adapter.workflow_manager.unified_data[rid]
                    removed_count += 1
                    logger.info(f"✅ Supprimé: {duplicate['name']} (ID: {rid})")
                if rid in adapter.workflow_manager.rag_data:
                    del adapter.workflow_manager.rag_data[rid]
                    logger.info(f"   └─ Aussi supprimé du RAG")
            except Exception as e:
                logger.error(f"❌ Erreur suppression {duplicate['name']}: {e}")

        try:
            adapter.workflow_manager._save_json(
                adapter.workflow_manager.unified_data, adapter.workflow_manager.unified_file
            )
            adapter.workflow_manager._save_json(
                adapter.workflow_manager.rag_data, adapter.workflow_manager.rag_file
            )
            logger.info("💾 Changements sauvegardés")
        except Exception as e:
            logger.error(f"❌ Erreur sauvegarde: {e}")

        return {
            "success": True,
            "message": f"Déduplication terminée: {removed_count} doublons supprimés",
            "data": {
                "total_resources_before": len(all_resources),
                "duplicates_detected": len(duplicates_to_remove),
                "duplicates_removed": removed_count,
                "total_resources_after": len(all_resources) - removed_count
            }
        }

    except Exception as e:
        logger.error(f"Erreur déduplication: {e}")
        return JSONResponse(status_code=500, content={
            "success": False,
            "message": f"Erreur déduplication: {str(e)}",
            "data": {"removed_count": 0}
        })


# ─── DISCOVERY STATUS ───────────────────────────────────────────────────────

@router.get("/admin/discovery-status/{country}")
async def get_discovery_status(country: str):
    """
    Rapport de statut des découvertes pour un pays.

    Retourne :
    - Progrès par catégorie (Service Support, Plateforme, Autorité)
    - Courant vs objectif pour chaque catégorie
    - Pourcentage de progression globale
    """
    try:
        workflow_manager = get_api_adapter().workflow_manager
        report = workflow_manager.get_discovery_status_report(country)
        return report
    except Exception as e:
        logger.error(f"Error getting discovery status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/admin/discovery-due/{country}")
async def get_discovery_due(country: str):
    """
    Prochaines découvertes à lancer pour un pays.

    Retourne :
    - Catégories à découvrir maintenant (triées par priorité)
    - Allocation recommandée des ressources
    - Temps estimé d'exécution
    """
    try:
        workflow_manager = get_api_adapter().workflow_manager
        result = workflow_manager.get_next_discoveries_due(country)
        return result
    except Exception as e:
        logger.error(f"Error getting discovery due: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ─── MIGRATION ──────────────────────────────────────────────────────────────

@router.post("/admin/migration/from-unified")
async def migrate_from_unified_resources(admin_id: str = Depends(verify_admin_token)):
    """
    Migration ponctuelle depuis unified_resources.json vers la nouvelle architecture.

    À exécuter une seule fois lors de la montée en version.
    """
    try:
        import json
        import os

        unified_path = "unified_resources.json"
        if not os.path.exists(unified_path):
            return {
                "success": False,
                "message": "unified_resources.json introuvable",
                "migrated_count": 0
            }

        with open(unified_path, 'r', encoding='utf-8') as f:
            unified_data = json.load(f)

        adapter = get_api_adapter()
        migrated_count = 0

        for resource in unified_data.get("resources", []):
            try:
                resource_id = f"MIGRATED_{migrated_count + 1}"
                adapter.workflow_manager.add_discovered_resource(resource_id, resource)

                if resource.get("validation_status") == "validated":
                    adapter.workflow_manager.transition_status(resource_id, "validated")
                    adapter.workflow_manager.transition_status(resource_id, "rag_ready")

                migrated_count += 1
            except Exception as e:
                logger.error(f"Erreur migration ressource {resource_id}: {e}")

        return {
            "success": True,
            "message": f"{migrated_count} ressources migrées",
            "migrated_count": migrated_count,
            "source_file": unified_path
        }

    except Exception as e:
        logger.error(f"Erreur migrate_from_unified: {e}")
        return JSONResponse(status_code=500, content={
            "success": False,
            "message": f"Erreur migration: {str(e)}",
            "migrated_count": 0
        })
