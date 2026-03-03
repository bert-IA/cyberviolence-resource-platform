"""
Router : Découverte par catégorie (batch & single)
Endpoints : /discover-by-category/*, /discover-batch/*, /categories/*

V2 : les catégories valides sont mises à jour (association_locale supprimée)
"""

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import JSONResponse
import logging

from core.api_adapter import get_api_adapter
from routers.auth import verify_admin_token

logger = logging.getLogger(__name__)

# ─── Catégories valides V2 ───────────────────────────────────────────────────
# Changement V2 : association_locale → service_support
VALID_CATEGORIES_V2 = [
    "service_support",        # 🆕 V2 : support national (ex contact_urgence élargi)
    "procedure_plateforme",   # ✅ Inchangé
    "signalement_autorite",   # ✅ Inchangé
    "contact_urgence",        # ⚠️  Maintenu pour backward compat (alias service_support)
]

router = APIRouter(tags=["Discovery"])


@router.post("/discover-by-category/{category}")
async def discover_by_category(category: str, request: Request, admin_id: str = Depends(verify_admin_token)):
    """
    Découverte ciblée par catégorie (stratégie lean).

    Catégories V2 :
    - service_support       : Services nationaux d'aide (gouvernementaux en priorité)
    - procedure_plateforme  : Procédures officielles plateformes (inclut Discord, WhatsApp...)
    - signalement_autorite  : Autorités légales de signalement
    - contact_urgence       : Alias de service_support (backward compat)
    """
    try:
        data = await request.json()
        country_code = data.get("country_code")
        language = data.get("language", "FR")
        max_resources = data.get("max_resources", 4)

        if category not in VALID_CATEGORIES_V2:
            raise HTTPException(
                status_code=400,
                detail=f"Catégorie invalide. Catégories valides: {', '.join(VALID_CATEGORIES_V2)}"
            )
        if not country_code:
            raise HTTPException(status_code=400, detail="country_code requis")

        # Normalisation V2 : contact_urgence → service_support
        effective_category = "service_support" if category == "contact_urgence" else category

        specialized_params = {}
        if effective_category == "procedure_plateforme":
            specialized_params["platform_name"] = data.get("platform_name", "Instagram")

        adapter = get_api_adapter()
        result = await adapter.start_category_discovery(
            category=effective_category,
            country_code=country_code,
            language=language,
            max_resources=max_resources,
            admin_id="admin_user",
            **specialized_params,
        )
        return JSONResponse(content=result)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur discover_by_category/{category}: {e}")
        return JSONResponse(status_code=500, content={"success": False, "message": str(e), "data": {"category": category, "discovered_count": 0}})


@router.post("/discover-batch/category-multi-countries")
async def discover_category_multi_countries(request: Request, admin_id: str = Depends(verify_admin_token)):
    """
    Découverte d'une catégorie sur plusieurs pays d'une langue.

    Body: { "category": "service_support", "language": "FR",
            "country_codes": ["FR","BE","CH","CA"], "max_resources_per_country": 3 }
    """
    try:
        data = await request.json()
        category = data.get("category")
        language = data.get("language")
        country_codes = data.get("country_codes", [])
        max_per_country = data.get("max_resources_per_country", 3)

        if not all([category, language, country_codes]):
            raise HTTPException(status_code=400, detail="Paramètres manquants: category, language, country_codes")

        adapter = get_api_adapter()
        results = await adapter.start_batch_discovery_multi_countries(
            category=category, language=language,
            country_codes=country_codes, max_resources_per_country=max_per_country,
            admin_id="admin_user",
        )
        return {"success": True, "message": f"Découverte {category} terminée pour {len(country_codes)} pays", "data": results}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur découverte multi-pays: {e}")
        return JSONResponse(status_code=500, content={"success": False, "message": str(e)})


@router.post("/discover-batch/all-platforms")
async def discover_all_platforms_country(request: Request, admin_id: str = Depends(verify_admin_token)):
    """
    Découverte de toutes les procédures plateformes pour un pays.
    V2 : Discord, WhatsApp, Telegram ajoutés aux plateformes par défaut.

    Body: { "country_code": "FR", "language": "FR",
            "platforms": ["Instagram","Facebook","TikTok","Discord","WhatsApp","Telegram"],
            "max_resources_per_platform": 2 }
    """
    try:
        data = await request.json()
        country_code = data.get("country_code")
        language = data.get("language")
        # V2 : plateformes de dialogue ajoutées
        platforms = data.get("platforms", ["Instagram", "Facebook", "TikTok", "Discord", "WhatsApp", "Telegram", "Snapchat"])
        max_per_platform = data.get("max_resources_per_platform", 2)

        if not country_code or not language:
            raise HTTPException(status_code=400, detail="country_code et language requis")

        adapter = get_api_adapter()
        results = await adapter.start_batch_discovery_all_platforms(
            country_code=country_code, language=language,
            platforms=platforms, max_resources_per_platform=max_per_platform,
            admin_id="admin_user",
        )
        return {"success": True, "message": f"Découverte plateformes terminée pour {country_code}", "data": results}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur découverte plateformes: {e}")
        return JSONResponse(status_code=500, content={"success": False, "message": str(e)})


@router.post("/discover-batch/language-complete")
async def discover_language_complete(request: Request, admin_id: str = Depends(verify_admin_token)):
    """
    Découverte complète lean strategy pour une langue.

    Body: { "language": "FR", "country_codes": ["FR","BE","CH"],
            "categories": ["service_support","procedure_plateforme","signalement_autorite"] }
    """
    try:
        data = await request.json()
        language = data.get("language")
        country_codes = data.get("country_codes", [])
        categories = data.get("categories", ["service_support", "procedure_plateforme", "signalement_autorite"])

        if not language or not country_codes:
            raise HTTPException(status_code=400, detail="language et country_codes requis")

        adapter = get_api_adapter()
        results = await adapter.start_complete_lean_discovery(
            language=language, country_codes=country_codes,
            categories=categories, admin_id="admin_user",
        )
        return {"success": True, "message": f"Découverte lean complète pour {language}", "data": results}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur découverte complète: {e}")
        return JSONResponse(status_code=500, content={"success": False, "message": str(e)})


@router.get("/categories/stats/{country_code}")
async def get_category_stats(country_code: str):
    """Statistiques de progression par catégorie pour un pays (targets lean)"""
    try:
        adapter = get_api_adapter()
        stats = adapter.workflow_manager.get_category_stats_by_country(country_code)

        # V2 : targets mis à jour (association_locale → service_support)
        lean_targets = {
            "service_support":      3,
            "contact_urgence":      3,  # backward compat
            "procedure_plateforme": 5,
            "signalement_autorite": 4,
        }

        enriched_stats = {}
        total_discovered = total_target = 0

        for category, current_count in stats.items():
            target = lean_targets.get(category, 4)
            enriched_stats[category] = {
                "current": current_count,
                "target": target,
                "progress": min(current_count / target * 100, 100) if target > 0 else 0,
                "completed": current_count >= target,
            }
            total_discovered += current_count
            total_target += target

        return JSONResponse(content={
            "success": True,
            "data": {
                "country_code": country_code,
                "categories": enriched_stats,
                "totals": {
                    "discovered": total_discovered,
                    "target": total_target,
                    "global_progress": min(total_discovered / total_target * 100, 100) if total_target > 0 else 0,
                },
                "lean_strategy": {
                    "max_per_country": 12,
                    "current_total": total_discovered,
                    "remaining_capacity": max(12 - total_discovered, 0),
                },
            },
        })

    except Exception as e:
        logger.error(f"Erreur get_category_stats/{country_code}: {e}")
        return JSONResponse(status_code=500, content={"success": False, "message": str(e)})
