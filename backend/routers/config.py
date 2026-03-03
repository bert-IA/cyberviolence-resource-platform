"""
Router : Configuration (LLM, Pays/Langues, Workflow, Export)
Endpoints : /admin/config/*, /admin/workflow/*, /admin/export/*, /admin/sync-rag
"""

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse, FileResponse
import logging
import os
from datetime import datetime

from core.llm_manager import LLMProvider, get_llm_manager
from core.api_adapter import get_api_adapter
from core.config_manager import (
    get_config_manager,
    CountryConfig,
    LanguageConfig,
    handle_config_error,
)
from constants import LLM_PROVIDERS, DEFAULT_LLM_PROVIDER

logger = logging.getLogger(__name__)

# Import de la dépendance d'authentification depuis le module principal
# (définie une seule fois dans admin_api.py)
def get_verify_token():
    """Import différé pour éviter les imports circulaires"""
    from admin_api import verify_admin_token
    return verify_admin_token


router = APIRouter(tags=["Configuration"])


# ─── LLM ────────────────────────────────────────────────────────────────────

@router.get("/admin/config/llm-providers")
async def get_llm_providers(admin_id: str = Depends(lambda: None)):
    return {"providers": LLM_PROVIDERS, "default": DEFAULT_LLM_PROVIDER}


@router.post("/admin/config/llm-provider")
async def set_llm_provider(provider: str):
    try:
        provider_enum = LLMProvider(provider)
        adapter = get_api_adapter()
        adapter.llm_manager = get_llm_manager(provider_enum)
        return {"success": True, "message": f"Fournisseur LLM changé vers {provider}", "current_provider": provider}
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Fournisseur invalide: {provider}")


# ─── Pays / Langues (CRUD) ───────────────────────────────────────────────────

@router.get("/admin/config/countries-languages")
async def get_all_countries_languages():
    try:
        config_manager = get_config_manager()
        languages = config_manager.get_all_languages()
        return {
            "success": True,
            "message": "Configuration récupérée",
            "languages": {code: lang.model_dump() for code, lang in languages.items()},
            "total_languages": len(languages),
            "total_countries": sum(len(lang.countries) for lang in languages.values()),
        }
    except Exception as e:
        raise handle_config_error(e, "récupération configuration")


@router.get("/admin/config/countries-languages/{language}")
async def get_language_config(language: str):
    try:
        config_manager = get_config_manager()
        lang_config = config_manager.get_language(language)
        if not lang_config:
            raise HTTPException(status_code=404, detail=f"Langue {language} non trouvée")
        return {"success": True, "language": language.upper(), "config": lang_config.model_dump()}
    except HTTPException:
        raise
    except Exception as e:
        raise handle_config_error(e, f"récupération langue {language}")


@router.put("/admin/config/countries-languages/{language}")
async def update_language_config(language: str, config: LanguageConfig):
    try:
        if config.code.upper() != language.upper():
            raise HTTPException(status_code=400, detail=f"Code langue incohérent: {config.code} != {language}")
        config_manager = get_config_manager()
        config_manager.update_language(language, config)
        return {"success": True, "message": f"Langue {language} mise à jour", "countries_count": len(config.countries)}
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise handle_config_error(e, f"mise à jour langue {language}")


@router.post("/admin/config/countries-languages/{language}/countries")
async def add_country_to_language(language: str, country: CountryConfig):
    try:
        config_manager = get_config_manager()
        config_manager.add_country_to_language(language, country)
        return {"success": True, "message": f"Pays {country.country_code} ajouté à {language}", "country": country.model_dump()}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise handle_config_error(e, f"ajout pays à {language}")


@router.delete("/admin/config/countries-languages/{language}/countries/{country_code}")
async def remove_country_from_language(language: str, country_code: str):
    try:
        config_manager = get_config_manager()
        config_manager.remove_country_from_language(language, country_code)
        return {"success": True, "message": f"Pays {country_code} supprimé de {language}"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise handle_config_error(e, f"suppression pays {country_code}")


@router.delete("/admin/config/countries-languages/{language}")
async def delete_language(language: str):
    try:
        config_manager = get_config_manager()
        config_manager.delete_language(language)
        return {"success": True, "message": f"Langue {language} supprimée"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise handle_config_error(e, f"suppression langue {language}")


@router.get("/admin/config/stats")
async def get_config_stats():
    try:
        config_manager = get_config_manager()
        return {"success": True, "stats": config_manager.get_stats()}
    except Exception as e:
        raise handle_config_error(e, "récupération statistiques")


# ─── Workflow / Export / Sync ────────────────────────────────────────────────

@router.get("/admin/workflow/status")
async def get_workflow_status():
    try:
        adapter = get_api_adapter()
        stats = adapter.get_system_stats()
        return {
            "success": True,
            "workflow_status": stats["workflow_stats"],
            "validation_progress": stats["validation_stats"],
            "llm_health": stats["llm_stats"],
        }
    except Exception as e:
        logger.error(f"Erreur get_workflow_status: {e}")
        return JSONResponse(status_code=500, content={"success": False, "error": str(e)})


@router.get("/admin/export/rag-ready")
async def export_rag_ready_resources():
    try:
        adapter = get_api_adapter()
        rag_data = adapter.workflow_manager.get_rag_resources()
        if not rag_data:
            rag_data = adapter.workflow_manager.get_resources_by_status("rag_ready")
        return {
            "success": True,
            "rag_resources": rag_data,
            "total_resources": len(rag_data),
            "export_timestamp": datetime.now().isoformat(),
        }
    except Exception as e:
        logger.error(f"Erreur export_rag_ready: {e}")
        return JSONResponse(status_code=500, content={"success": False, "error": str(e)})


@router.post("/admin/sync-rag")
async def sync_rag_data():
    try:
        adapter = get_api_adapter()
        cleaned_count = adapter.workflow_manager.sync_rag_data()
        return {"success": True, "message": f"Synchronisation terminée: {cleaned_count} sources orphelines nettoyées", "cleaned_count": cleaned_count}
    except Exception as e:
        logger.error(f"Erreur sync_rag_data: {e}")
        return JSONResponse(status_code=500, content={"success": False, "error": str(e)})


# ─── UI statiques ────────────────────────────────────────────────────────────

@router.get("/admin/geographic-discovery")
async def serve_geographic_ui():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    return FileResponse(os.path.join(current_dir, "..", "geographic_discovery.html"))


@router.get("/admin/sources-validation")
async def serve_validation_ui():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    return FileResponse(os.path.join(current_dir, "..", "critical_validation.html"))
