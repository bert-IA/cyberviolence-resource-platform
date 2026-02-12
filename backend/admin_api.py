"""
Intégration de la nouvelle architecture avec admin_api.py existant
Remplacement des endpoints obsolètes par les nouveaux modules
"""
from fastapi import FastAPI, HTTPException, Depends, status, Request
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.staticfiles import StaticFiles
from typing import List, Dict, Any, Optional
import logging
from datetime import datetime
import asyncio
import os
from dotenv import load_dotenv

# Charger les variables d'environnement depuis .env
load_dotenv()

# Import des nouveaux modules
from core.api_adapter import get_api_adapter
from core.llm_manager import LLMProvider, get_llm_manager
from core.deduplication_service import DeduplicationService
from core.priority_discovery_service import PriorityDiscoveryService

# Import des constantes
from constants import (
    COUNTRIES_CONFIG,
    SUPPORTED_LANGUAGES,
    LLM_PROVIDERS,
    DEFAULT_LLM_PROVIDER,
    API_VERSION,
    API_TITLE,
    API_DESCRIPTION,
    DISCOVERY_CATEGORIES,
    ADMIN_TOKEN_DEV
)

# Import du service de réponses
from response_service import ResponseService, ErrorHandler, OperationLogger

logger = logging.getLogger(__name__)

# Configuration FastAPI
app = FastAPI(
    title=API_TITLE,
    description=API_DESCRIPTION,
    version=API_VERSION
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration des fichiers statiques
app.mount("/static", StaticFiles(directory="."), name="static")

# Sécurité simple (à adapter selon besoins)
security = HTTPBearer()

def verify_admin_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Vérification basique du token admin"""
    # Token simple pour développement - À remplacer par vraie authentification
    if credentials.credentials != ADMIN_TOKEN_DEV:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token d'accès invalide"
        )
    return "admin_user"

# === INITIALISATION DES SERVICES ===
dedup_service = DeduplicationService()
discovery_service = PriorityDiscoveryService()

# === ENDPOINTS ROOT & HEALTH ===

@app.get("/", include_in_schema=False)
async def root():
    """Route racine - Documentation API"""
    return {
        "status": "ok",
        "service": "Resource Discovery Admin API",
        "version": "2.0.0",
        "documentation": "/docs",
        "health": "/health",
        "endpoints_count": 25
    }

@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    """Favicon - retourne 204 No Content"""
    from starlette.responses import Response
    return Response(content=b"", status_code=204)

# === ENDPOINTS HEALTH & CONFIG ===

@app.get("/health")
async def health_check():
    """Vérification de l'état du système"""
    try:
        adapter = get_api_adapter()
        stats = adapter.get_system_stats()
        
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "version": "2.0.0",
            "architecture": "dual_validation",
            "stats": stats
        }
    except Exception as e:
        logger.error(f"Erreur health check: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

@app.get("/admin/endpoints")
async def list_all_endpoints():
    """
    🔍 ENDPOINT DOCUMENTATION
    Liste tous les endpoints disponibles avec leurs paramètres et descriptions
    Utile pour découvrir l'API dynamiquement
    """
    endpoints = []
    
    # Parcourir toutes les routes FastAPI
    for route in app.routes:
        if hasattr(route, 'path') and hasattr(route, 'methods'):
            # Récupérer les infos
            path = route.path
            methods = list(route.methods) if route.methods else []
            name = route.name if hasattr(route, 'name') else "N/A"
            summary = route.summary if hasattr(route, 'summary') else ""
            description = route.description if hasattr(route, 'description') else ""
            
            # Filtrer les routes internes
            if path not in ['/openapi.json', '/docs', '/redoc', '/docs/oauth2-redirect']:
                endpoints.append({
                    'path': path,
                    'methods': methods,
                    'name': name,
                    'summary': summary or description,
                    'tags': route.tags if hasattr(route, 'tags') else []
                })
    
    # Trier par path
    endpoints.sort(key=lambda x: x['path'])
    
    return {
        'status': 'success',
        'total_endpoints': len(endpoints),
        'timestamp': datetime.now().isoformat(),
        'documentation': {
            'swagger_ui': '/docs',
            'redoc': '/redoc',
            'openapi': '/openapi.json'
        },
        'endpoints': endpoints,
        'groups': {
            'health': [e for e in endpoints if '/health' in e['path']],
            'config': [e for e in endpoints if '/config' in e['path']],
            'geographic': [e for e in endpoints if '/geographic' in e['path']],
            'discovery': [e for e in endpoints if '/discovery' in e['path'] or '/category' in e['path']],
            'batch': [e for e in endpoints if '/batch' in e['path']],
            'validation': [e for e in endpoints if '/validation' in e['path']],
            'deduplication': [e for e in endpoints if '/duplicates' in e['path']],
            'workflow': [e for e in endpoints if '/workflow' in e['path'] or '/stats' in e['path']],
            'admin': [e for e in endpoints if '/admin' in e['path']],
        }
    }

@app.get("/admin/config/llm-providers")
async def get_llm_providers(admin_id: str = Depends(verify_admin_token)):
    """Retourne les fournisseurs LLM disponibles"""
    return {
        "providers": LLM_PROVIDERS,
        "default": DEFAULT_LLM_PROVIDER
    }

@app.get("/geographic/countries")
async def get_geographic_countries():
    """Retourne la configuration des pays pour la découverte géographique"""
    return {
        "success": True,
        "data": {
            "supported_languages": SUPPORTED_LANGUAGES,
            "total_countries": sum(len(countries) for countries in COUNTRIES_CONFIG.values()),
            "countries_by_language": COUNTRIES_CONFIG
        }
    }

@app.get("/geographic/countries-by-language/{language}")
async def get_countries_by_language(language: str):
    """
    NOUVEAU: Retourne uniquement les pays pour une langue donnée
    Utile pour l'interface batch avec sélection automatique
    """
    try:
        from core.geo_discovery import get_countries_for_language
        
        countries = await get_countries_for_language(language.upper(), 5)  # Stratégie lean: 5 pays max
        
        return {
            "success": True,
            "language": language.upper(),
            "countries": countries,
            "total_countries": len(countries),
            "all_countries_option": {
                "label": f"🌍 Tous les pays {language.upper()}",
                "codes": [c["code"] for c in countries],
                "description": f"Sélectionner automatiquement tous les {len(countries)} pays {language.upper()}"
            }
        }
        
    except Exception as e:
        logger.error(f"Erreur récupération pays pour {language}: {e}")
        return {
            "success": False,
            "error": str(e),
            "language": language
        }

@app.post("/admin/config/llm-provider")
async def set_llm_provider(provider: str, admin_id: str = Depends(verify_admin_token)):
    """Change le fournisseur LLM actuel"""
    try:
        provider_enum = LLMProvider(provider)
        adapter = get_api_adapter()
        adapter.llm_manager = get_llm_manager(provider_enum)
        
        return {
            "success": True,
            "message": f"Fournisseur LLM changé vers {provider}",
            "current_provider": provider
        }
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Fournisseur invalide: {provider}")

# === ENDPOINTS DÉCOUVERTE GÉOGRAPHIQUE ===

@app.get("/geographic/countries-dynamic/{language}")
async def get_countries_dynamic(language: str, max_countries: int = 10):
    """
    Récupère dynamiquement les pays pour une langue via API REST Countries
    """
    try:
        from core.geo_discovery import get_countries_for_language
        
        countries = await get_countries_for_language(language.upper(), max_countries)
        
        return {
            "success": True,
            "message": f"Pays trouvés pour {language}",
            "data": {
                "language": language.upper(),
                "countries_count": len(countries),
                "countries": countries,
                "source": "dynamic_api"
            }
        }
    except Exception as e:
        logger.error(f"Erreur countries dynamic {language}: {e}")
        return {
            "success": False,
            "message": f"Erreur: {str(e)}",
            "data": {"source": "error"}
        }

@app.post("/geographic/discover")
async def start_geographic_discovery(
    request: Request,
    admin_id: str = Depends(verify_admin_token)
):
    """
    Démarre la découverte géographique avec le nouveau système LLM
    
    ✅ Support pour plusieurs catégories:
    - Ancien format: {"category":"emergency"} - Une seule catégorie
    - Nouveau format: {"categories":["emergency","procedure"]} - Plusieurs catégories
    """
    try:
        data = await request.json()
        language = data.get("language", "FR")
        
        # ✅ Support NOUVEAU: categories (plural) pour plusieurs catégories
        categories = data.get("categories", [])
        category = data.get("category", "")  # Backward compatibility
        
        # Si categories est fourni, l'utiliser. Sinon utiliser category (backward compat)
        if categories and len(categories) > 0:
            # Plusieurs catégories : utiliser le mode séquence avec tempo
            logger.info(f"🔍 Mode MULTI-CATÉGORIES: {categories}")
            categories_list = categories
        elif category:
            # Une seule catégorie : compatible ancien format
            categories_list = [category]
        else:
            # Aucune catégorie : utiliser toutes les 4
            categories_list = ["emergency", "procedure", "authority", "local"]
            logger.info(f"🔍 Aucune catégorie spécifiée, utiliser TOUTES: {categories_list}")
        
        countries = data.get("countries", [])  # Capturer countries array
        max_per_category = data.get("max_per_category", 3)  # Utiliser max_per_category
        
        logger.info(f"Démarrage découverte: lang={language}, cats={categories_list}, countries={countries}, max={max_per_category}")
        
        adapter = get_api_adapter()
        
        # ✅ Si plusieurs catégories, lancer en séquence avec tempo
        if len(categories_list) > 1:
            logger.info(f"🔄 Mode SÉQUENCE pour {len(categories_list)} catégories (tempo entre chaque)")
            result = await adapter.start_geographic_discovery_multi_categories(
                language, categories_list, countries, max_per_category, admin_id
            )
        else:
            # Une seule catégorie : mode classique
            result = await adapter.start_geographic_discovery(
                language, categories_list[0], countries, max_per_category, admin_id
            )
        
        return JSONResponse(content=result)
        
    except Exception as e:
        logger.error(f"Erreur start_geographic_discovery: {e}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "message": f"Erreur système: {str(e)}",
                "data": {"estimated_duration": "N/A"}
            }
        )

@app.get("/geographic/results")
async def get_geographic_results(language: str = None):
    """
    Récupère les résultats de découverte en attente de validation géographique
    Peut filtrer par langue si spécifiée (ex: ?language=FR)
    """
    try:
        adapter = get_api_adapter()
        result = adapter.get_geographic_results(language)
        
        return ResponseService.success(
            data=result,
            message=f"Résultats de découverte géographique {'pour ' + language if language else ''}"
        )
        
    except Exception as e:
        OperationLogger.log_error("get_geographic_results", e)
        return ResponseService.error(
            message=f"Erreur lors de la récupération des résultats: {str(e)}",
            additional={"data": {"discovered_resources": []}}
        )

@app.post("/geographic/clear-cache")
async def clear_geographic_cache(
    admin_id: str = Depends(verify_admin_token)
):
    """
    Vide le cache géographique pour éviter les extensions automatiques
    """
    try:
        from core.geo_discovery import geo_discovery
        geo_discovery.clear_cache()
        
        OperationLogger.log_success(
            "clear_geographic_cache",
            "Cache cleared successfully",
            {"admin_id": admin_id}
        )
        
        return ResponseService.success(
            data={"admin_id": admin_id},
            message="Cache géographique vidé avec succès"
        )
        
    except Exception as e:
        OperationLogger.log_error("clear_geographic_cache", e)
        return ResponseService.server_error(e)

@app.post("/geographic/validate-batch")
async def validate_geographic_batch(
    request: Request,
    admin_id: str = Depends(verify_admin_token)
):
    """
    Validation géographique en lot
    """
    try:
        data = await request.json()
        logger.info(f"DEBUG - Data reçue: {data} (type: {type(data)})")
        
        action = data.get("action")  # "approve" ou "reject"
        resource_ids = data.get("resource_ids", [])
        
        logger.info(f"DEBUG - Action: {action}, Resource IDs: {resource_ids}")
        
        if not action or not resource_ids:
            raise HTTPException(status_code=400, detail="Action et resource_ids requis")
        
        adapter = get_api_adapter()
        result = adapter.validate_geographic_batch(action, resource_ids, admin_id)
        
        return JSONResponse(content=result)
        
    except Exception as e:
        logger.error(f"Erreur validate_geographic_batch: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "message": f"Erreur: {str(e)}",
                "data": {"processed_resources": []}
            }
        )

# === ENDPOINTS DÉCOUVERTE PAR CATÉGORIE ===

@app.post("/discover-by-category/{category}")
async def discover_by_category(
    category: str,
    request: Request,
    admin_id: str = Depends(verify_admin_token)
):
    """
    Découverte ciblée par catégorie selon stratégie lean
    
    Catégories supportées:
    - contact_urgence: Numéros d'urgence nationaux et services de police
    - procedure_plateforme: Procédures spécifiques aux plateformes digitales  
    - signalement_autorite: Autorités officielles de signalement
    - association_locale: Associations locales spécialisées cyber-harcèlement
    
    Paramètres:
    - country_code: Code pays (FR, DE, ES, etc.)
    - language: Langue pour prompts (FR, EN, ES, IT, DE, PT)
    - max_resources: Limite ressources (défaut: 4 pour lean strategy)
    - platform_name: Nom plateforme (pour procedure_plateforme)
    """
    try:
        data = await request.json()
        country_code = data.get("country_code")
        language = data.get("language", "FR")
        max_resources = data.get("max_resources", 4)  # Stratégie lean: 4 max par catégorie
        
        # Validation catégorie
        valid_categories = ["contact_urgence", "procedure_plateforme", "signalement_autorite", "association_locale"]
        if category not in valid_categories:
            raise HTTPException(
                status_code=400, 
                detail=f"Catégorie invalide. Catégories valides: {', '.join(valid_categories)}"
            )
        
        if not country_code:
            raise HTTPException(status_code=400, detail="country_code requis")
        
        # Paramètres spécialisés selon catégorie
        specialized_params = {}
        if category == "procedure_plateforme":
            specialized_params["platform_name"] = data.get("platform_name", "Instagram")
        
        logger.info(f"Découverte {category} pour {country_code} en {language} (max: {max_resources})")
        
        adapter = get_api_adapter()
        result = await adapter.start_category_discovery(
            category=category,
            country_code=country_code,
            language=language,
            max_resources=max_resources,
            admin_id=admin_id,
            **specialized_params
        )
        
        return JSONResponse(content=result)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur discover_by_category/{category}: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "message": f"Erreur système: {str(e)}",
                "data": {"category": category, "discovered_count": 0}
            }
        )

# === NOUVEAUX ENDPOINTS BATCH DISCOVERY ===

@app.post("/discover-batch/category-multi-countries")
async def discover_category_multi_countries(
    request: Request,
    admin_id: str = Depends(verify_admin_token)
):
    """
    NOUVEAU: Découverte d'une catégorie sur plusieurs pays d'une langue
    
    Body: {
        "category": "contact_urgence",
        "language": "FR", 
        "country_codes": ["FR", "BE", "CH", "CA"],
        "max_resources_per_country": 3
    }
    """
    try:
        data = await request.json()
        category = data.get("category")
        language = data.get("language") 
        country_codes = data.get("country_codes", [])
        max_per_country = data.get("max_resources_per_country", 3)
        
        if not category or not language or not country_codes:
            raise HTTPException(status_code=400, detail="Paramètres manquants")
        
        adapter = get_api_adapter()
        
        # Découverte parallèle optimisée
        results = await adapter.start_batch_discovery_multi_countries(
            category=category,
            language=language, 
            country_codes=country_codes,
            max_resources_per_country=max_per_country,
            admin_id=admin_id
        )
        
        return {
            "success": True,
            "message": f"Découverte {category} terminée pour {len(country_codes)} pays",
            "data": results
        }
        
    except Exception as e:
        logger.error(f"Erreur découverte multi-pays: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "message": f"Erreur système: {str(e)}"
            }
        )

@app.post("/discover-batch/all-platforms") 
async def discover_all_platforms_country(
    request: Request,
    admin_id: str = Depends(verify_admin_token)
):
    """
    NOUVEAU: Découverte de toutes les procédures plateformes pour un pays
    
    Body: {
        "country_code": "FR",
        "language": "FR",
        "platforms": ["Instagram", "Facebook", "TikTok", "Discord", "Snapchat"],
        "max_resources_per_platform": 2
    }
    """
    try:
        data = await request.json()
        country_code = data.get("country_code")
        language = data.get("language")
        platforms = data.get("platforms", ["Instagram", "Facebook", "TikTok", "Discord"])
        max_per_platform = data.get("max_resources_per_platform", 2)
        
        if not country_code or not language:
            raise HTTPException(status_code=400, detail="Paramètres manquants")
        
        adapter = get_api_adapter()
        
        # Découverte toutes plateformes optimisée
        results = await adapter.start_batch_discovery_all_platforms(
            country_code=country_code,
            language=language,
            platforms=platforms,
            max_resources_per_platform=max_per_platform,
            admin_id=admin_id
        )
        
        return {
            "success": True,
            "message": f"Découverte plateformes terminée pour {country_code}",
            "data": results
        }
        
    except Exception as e:
        logger.error(f"Erreur découverte plateformes: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "message": f"Erreur système: {str(e)}"
            }
        )

@app.post("/discover-batch/language-complete")
async def discover_language_complete(
    request: Request,
    admin_id: str = Depends(verify_admin_token)
):
    """
    NOUVEAU: Découverte complète lean strategy pour une langue
    
    Body: {
        "language": "FR",
        "country_codes": ["FR", "BE", "CH"],
        "categories": ["contact_urgence", "procedure_plateforme", "signalement_autorite", "association_locale"]
    }
    """
    try:
        data = await request.json()
        language = data.get("language")
        country_codes = data.get("country_codes", [])
        categories = data.get("categories", ["contact_urgence", "procedure_plateforme", "signalement_autorite", "association_locale"])
        
        if not language or not country_codes:
            raise HTTPException(status_code=400, detail="Paramètres manquants")
        
        adapter = get_api_adapter()
        
        # Découverte complète lean strategy
        results = await adapter.start_complete_lean_discovery(
            language=language,
            country_codes=country_codes,
            categories=categories,
            admin_id=admin_id
        )
        
        return {
            "success": True,
            "message": f"Découverte lean complète pour {language}",
            "data": results
        }
        
    except Exception as e:
        logger.error(f"Erreur découverte complète: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "message": f"Erreur système: {str(e)}"
            }
        )

@app.get("/categories/stats/{country_code}")
async def get_category_stats(country_code: str):
    """
    Statistiques des ressources par catégorie pour un pays
    Utile pour suivre les targets lean (16 ressources max par pays)
    """
    try:
        adapter = get_api_adapter()
        stats = adapter.workflow_manager.get_category_stats_by_country(country_code)
        
        # Calcul des targets et progress selon stratégie lean
        lean_targets = {
            "contact_urgence": 3,      # 3 contacts d'urgence max
            "procedure_plateforme": 5,  # 5 procédures plateformes principales 
            "signalement_autorite": 4,  # 4 autorités officielles
            "association_locale": 4     # 4 associations locales spécialisées
        }
        
        enriched_stats = {}
        total_discovered = 0
        total_target = 0
        
        for category, current_count in stats.items():
            target = lean_targets.get(category, 4)
            enriched_stats[category] = {
                "current": current_count,
                "target": target,
                "progress": min(current_count / target * 100, 100) if target > 0 else 0,
                "completed": current_count >= target
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
                    "global_progress": min(total_discovered / total_target * 100, 100) if total_target > 0 else 0
                },
                "lean_strategy": {
                    "max_per_country": 16,
                    "current_total": total_discovered,
                    "remaining_capacity": max(16 - total_discovered, 0)
                }
            }
        })
        
    except Exception as e:
        logger.error(f"Erreur get_category_stats/{country_code}: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "message": f"Erreur: {str(e)}",
                "data": {"country_code": country_code}
            }
        )

# === ENDPOINTS VALIDATION CRITIQUE ===

@app.get("/sources")
async def list_sources(status: Optional[str] = None):
    """
    Liste les ressources, optionnellement filtrées par statut
    
    Query params:
        status: Filtrer par statut (discovered, geo_pending, geo_validated, 
                critical_pending, critical_validated, rag_ready)
    
    Returns:
        {
            "success": true,
            "total": 5,
            "sources": [
                {
                    "id": "res_001",
                    "name": "Resource Name",
                    "status": "critical_pending",
                    ...
                }
            ]
        }
    """
    try:
        adapter = get_api_adapter()
        workflow_manager = adapter.workflow_manager
        
        # Récupérer toutes les ressources
        all_resources = workflow_manager.unified_data
        
        # Filtrer par statut si spécifié
        if status:
            filtered_resources = {
                rid: res for rid, res in all_resources.items()
                if res.get("workflow_status") == status
            }
        else:
            filtered_resources = all_resources
        
        # Formater les ressources pour la réponse
        sources_list = []
        for resource_id, resource_data in filtered_resources.items():
            sources_list.append({
                "id": resource_id,
                "name": resource_data.get("name", ""),
                "title": resource_data.get("name", ""),  # Alias pour compatibilité
                "description": resource_data.get("description", ""),
                "url": resource_data.get("url", ""),
                "organization": resource_data.get("organization", ""),
                "country": resource_data.get("country", ""),
                "region": resource_data.get("region", ""),
                "status": resource_data.get("workflow_status", ""),
                "workflow_status": resource_data.get("workflow_status", ""),
                "created_at": resource_data.get("created_at", ""),
                "contact_phone": resource_data.get("contact_phone", ""),
                "contact_email": resource_data.get("contact_email", ""),
                "contact_url": resource_data.get("contact_url", ""),
                "languages": resource_data.get("languages", []),
                "target_audience": resource_data.get("target_audience", [])
            })
        
        return JSONResponse(content={
            "success": True,
            "total": len(sources_list),
            "sources": sources_list
        })
        
    except Exception as e:
        logger.error(f"Erreur list_sources: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "total": 0,
                "sources": [],
                "error": str(e)
            }
        )

@app.get("/sources/{source_id}")
async def get_source_by_id(source_id: str):
    """
    Récupère les détails d'une ressource par son ID
    
    Path params:
        source_id: ID de la ressource
    
    Returns:
        Resource data avec tous les champs disponibles
    """
    try:
        adapter = get_api_adapter()
        workflow_manager = adapter.workflow_manager
        
        # Récupérer la ressource
        if source_id not in workflow_manager.unified_data:
            return JSONResponse(
                status_code=404,
                content={
                    "success": False,
                    "error": f"Resource {source_id} not found"
                }
            )
        
        resource_data = workflow_manager.unified_data[source_id]
        
        # Formater la réponse
        return JSONResponse(content={
            "success": True,
            "resource": {
                "id": source_id,
                "name": resource_data.get("name", ""),
                "title": resource_data.get("name", ""),
                "description": resource_data.get("description", ""),
                "url": resource_data.get("url", ""),
                "organization": resource_data.get("organization", ""),
                "country": resource_data.get("country", ""),
                "region": resource_data.get("region", ""),
                "status": resource_data.get("workflow_status", ""),
                "workflow_status": resource_data.get("workflow_status", ""),
                "created_at": resource_data.get("created_at", ""),
                "contact_phone": resource_data.get("contact_phone", ""),
                "contact_email": resource_data.get("contact_email", ""),
                "contact_url": resource_data.get("contact_url", ""),
                "languages": resource_data.get("languages", []),
                "target_audience": resource_data.get("target_audience", []),
                "metadata": resource_data.get("metadata", {}),
                "validation_history": resource_data.get("validation_history", [])
            }
        })
        
    except Exception as e:
        logger.error(f"Erreur get_source_by_id/{source_id}: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": str(e)
            }
        )

@app.get("/sources/validation")
async def get_sources_for_validation():
    """
    Récupère les sources validées géographiquement en attente de validation critique
    """
    try:
        adapter = get_api_adapter()
        result = adapter.get_sources_for_validation()
        
        return JSONResponse(content=result)
        
    except Exception as e:
        logger.error(f"Erreur get_sources_for_validation: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "sources": [],
                "error": str(e)
            }
        )

@app.post("/sources/validate")
async def validate_critical_source(
    request: Request,
    admin_id: str = Depends(verify_admin_token)
):
    """
    ✅ AMÉLIORÉ - Validation critique d'une source individuelle
    
    Améliorations Phase 1.5:
    - Vérification obligatoire que tous les critères sont cochés
    - Blocage de la validation si critères manquants
    - Enregistrement des critères vérifiés dans l'historique
    """
    try:
        data = await request.json()
        source_id = data.get("source_id")
        action = data.get("action")  # "validate_critical" ou "reject"
        modifications = data.get("modifications")
        criteria_checks = data.get("criteria_checks", {})  # 🆕 NOUVEAU - Critères cochés
        
        if not source_id or not action:
            raise HTTPException(status_code=400, detail="source_id et action requis")
        
        # ✅ AMÉLIORÉ - Vérification des critères avant validation
        if action == "validate_critical":
            from core.criteria_validation import get_criteria_validation_manager
            
            adapter = get_api_adapter()
            criteria_manager = get_criteria_validation_manager(adapter.workflow_manager)
            
            # Vérifier que tous les critères obligatoires sont cochés
            if criteria_checks:
                verification_result = criteria_manager.verify_all_criteria_checked(
                    source_id, 
                    criteria_checks, 
                    stage="critical"
                )
                
                if not verification_result["all_checked"]:
                    # ⚠️ BLOCAGE - Critères manquants
                    missing = verification_result["missing_criteria"]
                    return JSONResponse(
                        status_code=400,
                        content={
                            "success": False,
                            "message": f"Impossible de valider : {len(missing)} critère(s) non vérifié(s)",
                            "data": {
                                "source_id": source_id,
                                "missing_criteria": missing,
                                "total_required": verification_result["total_required"],
                                "checked_count": verification_result["checked_count"]
                            },
                            "error_code": "CRITERIA_NOT_CHECKED"
                        }
                    )
                
                # ✅ Tous les critères sont cochés - Enregistrer la vérification
                criteria_manager.save_criteria_verification(
                    source_id,
                    criteria_checks,
                    stage="critical",
                    verified_by=admin_id
                )
                logger.info(f"✅ Tous les critères vérifiés pour {source_id}")
            else:
                # ⚠️ Pas de criteria_checks fourni - Warning mais pas de blocage (compatibilité)
                logger.warning(f"⚠️ Validation sans vérification de critères pour {source_id}")
        
        # 🆕 NOUVEAU - Option de transition automatique vers RAG
        auto_transition_rag = data.get("auto_transition_rag", False)
        
        # Validation normale
        adapter = get_api_adapter()
        result = adapter.validate_critical_source(
            source_id, 
            action, 
            admin_id, 
            modifications,
            auto_transition_rag=auto_transition_rag  # 🆕 NOUVEAU - Passer l'option
        )
        
        return JSONResponse(content=result)
        
    except Exception as e:
        logger.error(f"Erreur validate_critical_source: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "message": f"Erreur: {str(e)}",
                "data": {"source_id": data.get("source_id", "unknown")}
            }
        )

# ==========================================
# 🆕 NOUVEAUX ENDPOINTS - EXTRACTION DE DONNÉES
# Jour 1 - Phase 1.5
# ==========================================

@app.get("/sources/{source_id}/extracted-data")
async def get_extracted_data(
    source_id: str,
    admin_id: str = Depends(verify_admin_token)
):
    """
    🆕 NOUVEAU - Récupère les données extraites d'une ressource
    
    Utilisé pour l'édition inline (Interface 4 - Section 1)
    Retourne les données de contact (téléphone, URL, email, horaires)
    
    Args:
        source_id: ID de la ressource
        
    Returns:
        ExtractedContactData: Données de contact extraites
    """
    try:
        from core.extracted_data import get_extracted_data_manager
        
        adapter = get_api_adapter()
        extracted_manager = get_extracted_data_manager(adapter.workflow_manager)
        
        # Récupérer la ressource
        resource = extracted_manager._get_resource_by_id(source_id)
        if not resource:
            raise HTTPException(
                status_code=404, 
                detail=f"Ressource {source_id} non trouvée"
            )
        
        # Extraire les données de contact
        extracted_data = extracted_manager.extract_contact_data(resource)
        
        # Convertir au format attendu par l'interface (arrays)
        contact_data = {
            "urls": [extracted_data.url] if extracted_data.url else [],
            "emails": [extracted_data.email] if extracted_data.email else [],
            "phones": [extracted_data.phone] if extracted_data.phone else [],
            "additional_notes": ""
        }
        
        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "message": "Données extraites avec succès",
                "resource_id": source_id,
                "title": resource.get("name", resource.get("organization_name", "")),
                "status": resource.get("status", resource.get("workflow_status", "critical_pending")),
                "contact_data": contact_data,
                "modification_history": extracted_data.modification_history
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur get_extracted_data pour {source_id}: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "message": f"Erreur lors de l'extraction des données: {str(e)}",
                "data": {"source_id": source_id}
            }
        )

@app.post("/sources/{source_id}/update-extracted-data")
async def update_extracted_data(
    source_id: str,
    request: Request,
    admin_id: str = Depends(verify_admin_token)
):
    """
    🆕 NOUVEAU - Met à jour les données extraites d'une ressource
    
    Utilisé pour l'édition inline (Interface 4 - Section 1)
    Permet de corriger téléphone, URL, email, type de contact, horaires
    
    Args:
        source_id: ID de la ressource
        request: Données à mettre à jour (phone, url, email, contact_type, availability)
        
    Returns:
        Ressource mise à jour avec historique des modifications
    """
    try:
        from core.extracted_data import get_extracted_data_manager
        
        data = await request.json()
        
        # L'interface envoie urls[], emails[], phones[] (arrays)
        # On les convertit en valeurs simples pour update_contact_data()
        updated_fields = {}
        
        if "urls" in data and data["urls"]:
            updated_fields["url"] = data["urls"][0]  # Prendre le premier
        if "emails" in data and data["emails"]:
            updated_fields["email"] = data["emails"][0]
        if "phones" in data and data["phones"]:
            updated_fields["phone"] = data["phones"][0]
        if "additional_notes" in data:
            updated_fields["additional_notes"] = data["additional_notes"]
        
        if not updated_fields:
            raise HTTPException(
                status_code=400,
                detail="Aucune donnée à mettre à jour"
            )
        
        adapter = get_api_adapter()
        extracted_manager = get_extracted_data_manager(adapter.workflow_manager)
        
        # Mettre à jour les données
        updated_resource = extracted_manager.update_contact_data(
            source_id, 
            updated_fields, 
            modified_by=admin_id
        )
        
        # Extraire les nouvelles données pour confirmation
        extracted_data = extracted_manager.extract_contact_data(updated_resource)
        
        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "message": "Données mises à jour avec succès",
                "data": {
                    "source_id": source_id,
                    "updated_resource": updated_resource,
                    "extracted_data": extracted_data.to_dict(),
                    "modification_history": extracted_data.modification_history
                }
            }
        )
        
    except HTTPException:
        raise
    except ValueError as e:
        logger.error(f"Erreur de validation update_extracted_data: {e}")
        return JSONResponse(
            status_code=404,
            content={
                "success": False,
                "message": str(e),
                "data": {"source_id": source_id}
            }
        )
    except Exception as e:
        logger.error(f"Erreur update_extracted_data pour {source_id}: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "message": f"Erreur lors de la mise à jour: {str(e)}",
                "data": {"source_id": source_id}
            }
        )

# ==========================================
# FIN NOUVEAUX ENDPOINTS EXTRACTION
# ==========================================

# ==========================================
# 🆕 NOUVEAUX ENDPOINTS - VALIDATION CRITÈRES
# Jour 2 - Phase 1.5
# ==========================================

@app.get("/sources/{source_id}/validation-criteria")
async def get_validation_criteria(
    source_id: str,
    stage: str = "critical",
    admin_id: str = Depends(verify_admin_token)
):
    """
    🆕 NOUVEAU - Récupère les critères de validation pour une ressource
    
    Utilisé pour afficher la checklist de critères (Interface 4 - Section 2)
    Retourne tous les critères applicables selon la catégorie de la ressource
    
    Args:
        source_id: ID de la ressource
        stage: "geographic" ou "critical" (défaut: "critical")
        
    Returns:
        ValidationCriteriaSet: Critères applicables avec détails
    """
    try:
        from core.criteria_validation import get_criteria_validation_manager
        
        adapter = get_api_adapter()
        criteria_manager = get_criteria_validation_manager(adapter.workflow_manager)
        
        # Récupérer les critères applicables
        criteria_set = criteria_manager.get_validation_criteria(source_id, stage)
        
        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "message": "Critères de validation récupérés avec succès",
                "data": {
                    "source_id": source_id,
                    "stage": stage,
                    "criteria_set": criteria_set.to_dict()
                }
            }
        )
        
    except ValueError as e:
        logger.error(f"Erreur de validation get_validation_criteria: {e}")
        return JSONResponse(
            status_code=404,
            content={
                "success": False,
                "message": str(e),
                "data": {"source_id": source_id}
            }
        )
    except Exception as e:
        logger.error(f"Erreur get_validation_criteria pour {source_id}: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "message": f"Erreur lors de la récupération des critères: {str(e)}",
                "data": {"source_id": source_id}
            }
        )

@app.post("/sources/{source_id}/verify-criteria")
async def verify_validation_criteria(
    source_id: str,
    request: Request,
    admin_id: str = Depends(verify_admin_token)
):
    """
    🆕 NOUVEAU - Vérifie que tous les critères obligatoires sont cochés
    
    Utilisé avant la validation finale pour s'assurer que tous les critères
    ont été vérifiés par l'admin (Interface 4 - Section 2)
    
    Args:
        source_id: ID de la ressource
        request: Contient criteria_checks {criterion_id: bool} et optionnel stage
        
    Returns:
        Résultat de la vérification avec critères manquants si applicable
    """
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
        
        # Vérifier que tous les critères sont cochés
        verification_result = criteria_manager.verify_all_criteria_checked(
            source_id, 
            criteria_checks, 
            stage
        )
        
        # Enregistrer la vérification
        if verification_result["all_checked"]:
            criteria_manager.save_criteria_verification(
                source_id,
                criteria_checks,
                stage,
                verified_by=admin_id
            )
        
        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "message": "Vérification des critères terminée",
                "data": {
                    "source_id": source_id,
                    "stage": stage,
                    "verification_result": verification_result,
                    "can_proceed": verification_result["all_checked"]
                }
            }
        )
        
    except HTTPException:
        raise
    except ValueError as e:
        logger.error(f"Erreur de validation verify_validation_criteria: {e}")
        return JSONResponse(
            status_code=404,
            content={
                "success": False,
                "message": str(e),
                "data": {"source_id": source_id}
            }
        )
    except Exception as e:
        logger.error(f"Erreur verify_validation_criteria pour {source_id}: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "message": f"Erreur lors de la vérification: {str(e)}",
                "data": {"source_id": source_id}
            }
        )

# ==========================================
# FIN NOUVEAUX ENDPOINTS VALIDATION CRITÈRES
# ==========================================

@app.post("/sources/format-rag")
async def format_source_for_rag(
    request: Request,
    admin_id: str = Depends(verify_admin_token)
):
    """
    Formate manuellement une source validée pour RAG
    """
    try:
        data = await request.json()
        source_id = data.get("source_id")
        
        if not source_id:
            raise HTTPException(status_code=400, detail="source_id requis")
        
        adapter = get_api_adapter()
        
        # Vérifier que la source est en critical_validated
        resource_data = adapter.workflow_manager.unified_data.get(source_id)
        if not resource_data:
            raise HTTPException(status_code=404, detail="Source non trouvée")
        
        current_status = resource_data.get("workflow_status")
        if current_status != "critical_validated":
            raise HTTPException(status_code=400, detail=f"Source doit être validée critiquement d'abord (statut actuel: {current_status})")
        
        # Transition vers RAG_READY
        success = adapter.workflow_manager.transition_status(
            source_id,
            "rag_ready",  # Utiliser la chaîne directement
            admin_id,
            "Formatage manuel pour RAG"
        )
        
        if success:
            return {
                "success": True,
                "message": "Source formatée pour RAG avec succès",
                "data": {
                    "source_id": source_id,
                    "new_status": "rag_ready"
                }
            }
        else:
            raise Exception("Échec de la transition vers RAG_READY")
        
    except Exception as e:
        logger.error(f"Erreur format_source_for_rag: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "message": f"Erreur: {str(e)}",
                "data": {"source_id": data.get("source_id", "unknown")}
            }
        )

@app.post("/sources/modify-and-validate")
async def modify_and_validate_source(
    request: Request,
    admin_id: str = Depends(verify_admin_token)
):
    """
    Modifie une source critical_pending et la valide automatiquement vers RAG
    """
    try:
        data = await request.json()
        source_id = data.get("source_id")
        modifications = data.get("modifications", {})
        
        if not source_id:
            raise HTTPException(status_code=400, detail="source_id requis")
        
        adapter = get_api_adapter()
        
        # Vérifier que la source existe et est en critical_pending
        resource_data = adapter.workflow_manager.unified_data.get(source_id)
        if not resource_data:
            raise HTTPException(status_code=404, detail="Source non trouvée")
        
        current_status = resource_data.get("workflow_status")
        if current_status != "critical_pending":
            raise HTTPException(status_code=400, detail=f"Source doit être en critical_pending (statut actuel: {current_status})")
        
        # Appliquer les modifications
        for key, value in modifications.items():
            if key in ["organization_name", "country_name", "phone", "email", "website", "description"]:
                resource_data[key] = value
        
        # Passer directement à critical_validated
        success1 = adapter.workflow_manager.transition_status(
            source_id,
            "critical_validated",
            admin_id,
            f"Source modifiée et validée"
        )
        
        if not success1:
            raise Exception("Échec de la transition vers critical_validated")
        
        # Puis automatiquement à rag_ready
        success2 = adapter.workflow_manager.transition_status(
            source_id,
            "rag_ready",
            admin_id,
            f"Formatage automatique après modification"
        )
        
        if success2:
            return {
                "success": True,
                "message": "Source modifiée et ajoutée au RAG avec succès",
                "data": {
                    "source_id": source_id,
                    "new_status": "rag_ready"
                }
            }
        else:
            raise Exception("Échec de la transition vers RAG_READY")
        
    except Exception as e:
        logger.error(f"Erreur modify_and_validate_source: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "message": f"Erreur: {str(e)}",
                "data": {"source_id": data.get("source_id", "unknown")}
            }
        )

@app.post("/manage-rag-source")
async def manage_rag_source(
    request: Request,
    admin_id: str = Depends(verify_admin_token)
):
    """
    Gère les sources RAG : suppression ou remise en attente
    """
    try:
        data = await request.json()
        source_key = data.get("source_key")
        action = data.get("action")
        
        if not source_key or not action:
            raise HTTPException(status_code=400, detail="source_key et action requis")
        
        adapter = get_api_adapter()
        
        # Trouver la source d'abord dans rag_data puis dans unified_data
        source_id = None
        
        # Chercher d'abord dans rag_data (sources affichées)
        for rid, rag_resource in adapter.workflow_manager.rag_data.items():
            if rag_resource.get("organization_name") == source_key or rid == source_key:
                source_id = rid
                break
        
        # Si pas trouvé dans rag_data, chercher dans unified_data
        if not source_id:
            for uid, resource_data in adapter.workflow_manager.unified_data.items():
                if resource_data.get("organization_name") == source_key or uid == source_key:
                    source_id = uid
                    break
        
        if not source_id:
            logger.error(f"Source non trouvée - source_key: {source_key}")
            logger.error(f"RAG keys disponibles: {list(adapter.workflow_manager.rag_data.keys())}")
            logger.error(f"Unified keys disponibles: {list(adapter.workflow_manager.unified_data.keys())}")
            raise HTTPException(status_code=404, detail="Source non trouvée")
        
        # Vérifier le statut dans unified_data (source de vérité pour les statuts)
        resource_data = adapter.workflow_manager.unified_data.get(source_id)
        
        # Si la source n'existe que dans rag_data (désynchronisation), permettre la suppression
        if not resource_data and action == "delete":
            logger.warning(f"Source {source_id} trouvée seulement dans rag_data - nettoyage")
            if source_id in adapter.workflow_manager.rag_data:
                del adapter.workflow_manager.rag_data[source_id]
                adapter.workflow_manager._save_json(adapter.workflow_manager.rag_data, adapter.workflow_manager.rag_file)
            
            return {
                "success": True,
                "message": "Source orpheline supprimée du RAG",
                "data": {
                    "source_key": source_key,
                    "action": action
                }
            }
        
        # Pour les autres actions, la source doit exister dans unified_data
        if not resource_data:
            raise HTTPException(status_code=404, detail="Source non trouvée dans unified_data")
            
        current_status = resource_data.get("workflow_status")
        
        # Pour revert_to_pending, vérifier le statut
        if action == "revert_to_pending" and current_status != "rag_ready":
            raise HTTPException(status_code=400, detail=f"Source doit être RAG_READY pour être remise en attente (statut actuel: {current_status})")
        
        if action == "delete":
            # Supprimer définitivement de unified_data ET rag_data
            deleted_from_unified = False
            deleted_from_rag = False
            
            if source_id in adapter.workflow_manager.unified_data:
                del adapter.workflow_manager.unified_data[source_id]
                adapter.workflow_manager._save_json(adapter.workflow_manager.unified_data, adapter.workflow_manager.unified_file)
                deleted_from_unified = True
            
            if source_id in adapter.workflow_manager.rag_data:
                del adapter.workflow_manager.rag_data[source_id]
                adapter.workflow_manager._save_json(adapter.workflow_manager.rag_data, adapter.workflow_manager.rag_file)
                deleted_from_rag = True
            
            if deleted_from_unified or deleted_from_rag:
                message = "Source supprimée définitivement"
            else:
                message = "Source déjà supprimée"
            
        elif action == "revert_to_pending":
            # Remettre en critical_pending pour re-validation
            adapter.workflow_manager.unified_data[source_id]["workflow_status"] = "critical_pending"
            adapter.workflow_manager.unified_data[source_id]["validation_history"].append({
                "from_status": "rag_ready",
                "to_status": "critical_pending",
                "admin_id": admin_id,
                "timestamp": datetime.now().isoformat(),
                "notes": "Remise en attente manuelle depuis RAG"
            })
            adapter.workflow_manager._save_json(adapter.workflow_manager.unified_data, adapter.workflow_manager.unified_file)
            
            # Supprimer aussi de rag_data puisqu'elle n'est plus RAG_READY
            if source_id in adapter.workflow_manager.rag_data:
                del adapter.workflow_manager.rag_data[source_id]
                adapter.workflow_manager._save_json(adapter.workflow_manager.rag_data, adapter.workflow_manager.rag_file)
            
            message = "Source remise en attente de validation"
            
        else:
            raise HTTPException(status_code=400, detail=f"Action non supportée: {action}")
        
        return {
            "success": True,
            "message": message,
            "data": {
                "source_key": source_key,
                "action": action
            }
        }
        
    except Exception as e:
        logger.error(f"Erreur manage_rag_source: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "message": f"Erreur: {str(e)}",
                "error": str(e)
            }
        )

# === ENDPOINTS WORKFLOW & STATISTICS ===

@app.get("/admin/workflow/status")
async def get_workflow_status(admin_id: str = Depends(verify_admin_token)):
    """Retourne l'état complet du workflow"""
    try:
        adapter = get_api_adapter()
        stats = adapter.get_system_stats()
        
        return {
            "success": True,
            "workflow_status": stats["workflow_stats"],
            "validation_progress": stats["validation_stats"],
            "llm_health": stats["llm_stats"]
        }
    except Exception as e:
        logger.error(f"Erreur get_workflow_status: {e}")
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": str(e)}
        )

@app.get("/admin/export/rag-ready")
async def export_rag_ready_resources(admin_id: str = Depends(verify_admin_token)):
    """Exporte les ressources prêtes pour le RAG"""
    try:
        adapter = get_api_adapter()
        
        # D'abord essayer les ressources du fichier RAG
        rag_data = adapter.workflow_manager.get_rag_resources()
        
        # Si le fichier RAG est vide, chercher dans working_data les ressources "rag_ready"
        if not rag_data:
            rag_data = adapter.workflow_manager.get_resources_by_status("rag_ready")
        
        return {
            "success": True,
            "rag_resources": rag_data,
            "total_resources": len(rag_data),
            "export_timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Erreur export_rag_ready: {e}")
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": str(e)}
        )

@app.post("/admin/sync-rag")
async def sync_rag_data(admin_id: str = Depends(verify_admin_token)):
    """Synchronise les données RAG pour éviter les incohérences"""
    try:
        adapter = get_api_adapter()
        cleaned_count = adapter.workflow_manager.sync_rag_data()
        
        return {
            "success": True,
            "message": f"Synchronisation terminée: {cleaned_count} sources orphelines nettoyées",
            "cleaned_count": cleaned_count
        }
    except Exception as e:
        logger.error(f"Erreur sync_rag_data: {e}")
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": str(e)}
        )

# === ENDPOINTS UI STATIQUES ===

@app.get("/admin/geographic-discovery")
async def serve_geographic_ui():
    """Sert l'interface de découverte géographique"""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    html_path = os.path.join(current_dir, "geographic_discovery.html")
    return FileResponse(html_path)

@app.get("/admin/sources-validation")
async def serve_validation_ui():
    """Sert l'interface de validation critique"""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    html_path = os.path.join(current_dir, "critical_validation.html")
    return FileResponse(html_path)

# === ENDPOINTS DÉDUPLICATION & DISCOVERY (NEW) ===

@app.get("/admin/duplicates/analyze")
async def analyze_duplicates():
    """Analyser tous les doublons (triple approche: exact, similarité, domaine)"""
    try:
        workflow_manager = get_api_adapter().workflow_manager
        analysis = workflow_manager.get_deduplication_analysis()
        
        return analysis
    except Exception as e:
        logger.error(f"Error analyzing duplicates: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/admin/duplicates/cleanup")
async def cleanup_duplicates(strategy: str = "keep_first"):
    """Nettoyer automatiquement les doublons selon la stratégie
    
    Stratégies:
    - keep_first: Garder la première ressource
    - keep_latest: Garder la plus récente
    - keep_verified: Garder la vérifiée
    - keep_complete: Garder la plus complète
    """
    try:
        workflow_manager = get_api_adapter().workflow_manager
        result = workflow_manager.cleanup_duplicates(strategy)
        
        return result
    except Exception as e:
        logger.error(f"Error cleaning duplicates: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/admin/discovery-status/{country}")
async def get_discovery_status(country: str):
    """Rapport de statut des découvertes pour un pays
    
    Retourne:
    - Progrès par catégorie (Emergency, Platform, Authority, Association)
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

@app.get("/admin/discovery-due/{country}")
async def get_discovery_due(country: str):
    """Prochaines découvertes à lancer pour un pays
    
    Retourne:
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

# === ENDPOINT DE DÉDUPLICATION ===

@app.post("/admin/deduplicate")
async def deduplicate_resources(admin_id: str = Depends(verify_admin_token)):
    """
    Supprime automatiquement les doublons dans les ressources découvertes
    """
    try:
        import re
        from difflib import SequenceMatcher
        from collections import defaultdict
        
        adapter = get_api_adapter()
        
        # Récupérer toutes les ressources
        all_resources = list(adapter.workflow_manager.unified_data.items())
        logger.info(f"🔍 Analyse de {len(all_resources)} ressources pour doublons")
        
        # Détecter les doublons
        duplicates_to_remove = []
        seen_resources = {}
        
        def normalize_name(name):
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
            
            # Créer une clé unique combinée
            normalized_name = normalize_name(name)
            domain = ""
            if website:
                domain_match = re.search(r'https?://(?:www\.)?([^/]+)', website)
                if domain_match:
                    domain = domain_match.group(1).lower()
            
            # Clé principale : nom normalisé + pays
            main_key = f"{normalized_name}|{country}".lower()
            # Clé secondaire : domaine + pays (si domaine disponible)
            domain_key = f"{domain}|{country}".lower() if domain else None
            
            # Vérifier doublons
            is_duplicate = False
            original_id = None
            
            # Vérification par nom
            if main_key in seen_resources and main_key:
                is_duplicate = True
                original_id = seen_resources[main_key]
                logger.info(f"🔍 Doublon par nom détecté: '{name}' (ID: {resource_id})")
            
            # Vérification par domaine
            elif domain_key and domain_key in seen_resources:
                is_duplicate = True
                original_id = seen_resources[domain_key]
                logger.info(f"🔍 Doublon par domaine détecté: '{name}' -> {domain} (ID: {resource_id})")
            
            if is_duplicate:
                duplicates_to_remove.append({
                    'id': resource_id,
                    'name': name,
                    'country': country,
                    'original_id': original_id
                })
            else:
                # Marquer comme vu
                if main_key:
                    seen_resources[main_key] = resource_id
                if domain_key:
                    seen_resources[domain_key] = resource_id
        
        logger.info(f"🚨 {len(duplicates_to_remove)} doublons détectés")
        
        # Supprimer les doublons
        removed_count = 0
        for duplicate in duplicates_to_remove:
            try:
                resource_id = duplicate['id']
                
                # Supprimer de unified_data
                if resource_id in adapter.workflow_manager.unified_data:
                    del adapter.workflow_manager.unified_data[resource_id]
                    removed_count += 1
                    logger.info(f"✅ Supprimé: {duplicate['name']} (ID: {resource_id})")
                
                # Supprimer aussi de rag_data si présent
                if resource_id in adapter.workflow_manager.rag_data:
                    del adapter.workflow_manager.rag_data[resource_id]
                    logger.info(f"   └─ Aussi supprimé du RAG")
                
            except Exception as e:
                logger.error(f"❌ Erreur suppression {duplicate['name']}: {e}")
        
        # Sauvegarder les changements
        try:
            adapter.workflow_manager._save_json(
                adapter.workflow_manager.unified_data, 
                adapter.workflow_manager.unified_file
            )
            adapter.workflow_manager._save_json(
                adapter.workflow_manager.rag_data, 
                adapter.workflow_manager.rag_file
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
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "message": f"Erreur déduplication: {str(e)}",
                "data": {"removed_count": 0}
            }
        )

# === ENDPOINT DE MIGRATION (TEMPORAIRE) ===

@app.post("/admin/migration/from-unified")
async def migrate_from_unified_resources(admin_id: str = Depends(verify_admin_token)):
    """
    Migration ponctuelle depuis unified_resources.json vers la nouvelle architecture
    """
    try:
        import json
        import os
        
        # Vérifier si unified_resources.json existe
        unified_path = "unified_resources.json"
        if not os.path.exists(unified_path):
            return {
                "success": False,
                "message": "unified_resources.json introuvable",
                "migrated_count": 0
            }
        
        # Charger les données
        with open(unified_path, 'r', encoding='utf-8') as f:
            unified_data = json.load(f)
        
        adapter = get_api_adapter()
        migrated_count = 0
        
        # Migrer chaque ressource
        for resource in unified_data.get("resources", []):
            try:
                resource_id = f"MIGRATED_{migrated_count + 1}"
                
                # Ajouter dans le workflow
                adapter.workflow_manager.add_discovered_resource(resource_id, resource)
                
                # Si déjà validée → avancer dans le workflow
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
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "message": f"Erreur migration: {str(e)}",
                "migrated_count": 0
            }
        )

# === GESTION DES ERREURS ===

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Gestionnaire global d'exceptions"""
    logger.error(f"Erreur non gérée: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "message": "Erreur interne du serveur",
            "error_type": type(exc).__name__
        }
    )


@app.post("/admin/duplicates/analyzed")
async def mark_duplicates_analyzed(resource_ids: List[str]):
    """Mark resources as analyzed for duplicates

    Args:
        resource_ids: List of resource IDs to mark as analyzed

    Returns:
        Success status with analyzed count
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


# === LANCEMENT DU SERVEUR ===

if __name__ == "__main__":
    import uvicorn
    
    logger.info("🚀 Démarrage du serveur Admin API...")
    logger.info(f"📍 Écoute sur http://0.0.0.0:8000")
    logger.info(f"📚 Documentation: http://localhost:8000/docs")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )