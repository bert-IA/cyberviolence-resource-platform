"""
Router : Découverte géographique
Endpoints : /geographic/*
"""

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import JSONResponse
import logging

from core.api_adapter import get_api_adapter
from constants import SUPPORTED_LANGUAGES, COUNTRIES_CONFIG
from response_service import ResponseService, OperationLogger
from routers.auth import verify_admin_token

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Geographic"])


@router.get("/geographic/countries")
async def get_geographic_countries():
    """Configuration des pays pour la découverte géographique"""
    return {
        "success": True,
        "data": {
            "supported_languages": SUPPORTED_LANGUAGES,
            "total_countries": sum(len(c) for c in COUNTRIES_CONFIG.values()),
            "countries_by_language": COUNTRIES_CONFIG,
        },
    }


@router.get("/geographic/countries-by-language/{language}")
async def get_countries_by_language(language: str):
    """Retourne les pays pour une langue donnée (stratégie lean : 5 pays max)"""
    try:
        from core.geo_discovery import get_countries_for_language
        countries = await get_countries_for_language(language.upper(), 5)
        return {
            "success": True,
            "language": language.upper(),
            "countries": countries,
            "total_countries": len(countries),
            "all_countries_option": {
                "label": f"🌍 Tous les pays {language.upper()}",
                "codes": [c["code"] for c in countries],
            },
        }
    except Exception as e:
        logger.error(f"Erreur récupération pays pour {language}: {e}")
        return {"success": False, "error": str(e), "language": language}


@router.get("/geographic/countries-dynamic/{language}")
async def get_countries_dynamic(language: str, max_countries: int = 10):
    """Découverte dynamique des pays via API externe"""
    try:
        from core.geo_discovery import get_countries_for_language
        countries = await get_countries_for_language(language.upper(), max_countries)
        return {"success": True, "language": language.upper(), "countries": countries, "total": len(countries)}
    except Exception as e:
        logger.error(f"Erreur countries-dynamic/{language}: {e}")
        return {"success": False, "error": str(e)}


@router.post("/geographic/discover")
async def start_geographic_discovery(
    request: Request,
    admin_id: str = Depends(verify_admin_token),
):
    """
    Démarre la découverte géographique.
    Supporte une ou plusieurs catégories.
    """
    try:
        data = await request.json()
        language = data.get("language", "FR")
        categories = data.get("categories", [])
        category = data.get("category", "")
        countries = data.get("countries", [])
        max_per_category = data.get("max_per_category", 3)

        # Résolution des catégories (backward compat)
        if categories:
            categories_list = categories
        elif category:
            categories_list = [category]
        else:
            categories_list = ["emergency", "procedure", "authority", "local"]

        logger.info(f"Démarrage découverte: lang={language}, cats={categories_list}, countries={countries}")

        adapter = get_api_adapter()
        if len(categories_list) > 1:
            result = await adapter.start_geographic_discovery_multi_categories(
                language, categories_list, countries, max_per_category, admin_id
            )
        else:
            result = await adapter.start_geographic_discovery(
                language, categories_list[0], countries, max_per_category, admin_id
            )
        return JSONResponse(content=result)

    except Exception as e:
        logger.error(f"Erreur start_geographic_discovery: {e}", exc_info=True)
        return JSONResponse(status_code=500, content={"success": False, "message": str(e), "data": {"estimated_duration": "N/A"}})


@router.get("/geographic/results")
async def get_geographic_results(language: str = None):
    """Résultats de découverte en attente de validation géographique"""
    try:
        adapter = get_api_adapter()
        result = adapter.get_geographic_results(language)
        return ResponseService.success(data=result, message="Résultats de découverte géographique")
    except Exception as e:
        OperationLogger.log_error("get_geographic_results", e)
        return ResponseService.error(message=str(e), additional={"data": {"discovered_resources": []}})


@router.post("/geographic/clear-cache")
async def clear_geographic_cache(admin_id: str = Depends(verify_admin_token)):
    """Vide le cache géographique"""
    try:
        from core.geo_discovery import geo_discovery
        geo_discovery.clear_cache()
        return ResponseService.success(data={}, message="Cache géographique vidé avec succès")
    except Exception as e:
        OperationLogger.log_error("clear_geographic_cache", e)
        return ResponseService.server_error(e)


@router.post("/geographic/validate-batch")
async def validate_geographic_batch(request: Request, admin_id: str = Depends(verify_admin_token)):
    """Validation géographique en lot (approve / reject)"""
    try:
        data = await request.json()
        action = data.get("action")
        resource_ids = data.get("resource_ids", [])

        if not action or not resource_ids:
            raise HTTPException(status_code=400, detail="Action et resource_ids requis")

        adapter = get_api_adapter()
        result = adapter.validate_geographic_batch(action, resource_ids, "admin_user")
        return JSONResponse(content=result)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur validate_geographic_batch: {e}")
        return JSONResponse(status_code=500, content={"success": False, "message": str(e), "data": {"processed_resources": []}})
