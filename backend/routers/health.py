"""
Router : Health & Documentation
Endpoints : /, /favicon.ico, /health, /admin/endpoints

Concept pédagogique :
  Un APIRouter est un "mini-app" FastAPI.
  On lui donne un prefix et des tags pour l'organisation Swagger.
  Puis dans admin_api.py on fait : app.include_router(router)
"""

from fastapi import APIRouter
from fastapi.responses import JSONResponse
from datetime import datetime
import logging

from core.api_adapter import get_api_adapter

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Health"])


@router.get("/", include_in_schema=False)
async def root():
    """Route racine - Documentation API"""
    return {
        "status": "ok",
        "service": "Resource Discovery Admin API",
        "version": "2.0.0",
        "documentation": "/docs",
        "health": "/health",
    }


@router.get("/favicon.ico", include_in_schema=False)
async def favicon():
    from starlette.responses import Response
    return Response(content=b"", status_code=204)


@router.get("/health")
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


@router.get("/admin/endpoints")
async def list_all_endpoints():
    """Liste tous les endpoints disponibles"""
    from fastapi import FastAPI
    # Import app depuis le module principal pour lister les routes
    import sys
    app = sys.modules.get("admin_api") and getattr(sys.modules["admin_api"], "app", None)
    if not app:
        return {"error": "app non disponible", "endpoints": []}

    endpoints = []
    for route in app.routes:
        if hasattr(route, "path") and hasattr(route, "methods"):
            path = route.path
            methods = list(route.methods) if route.methods else []
            if path not in ["/openapi.json", "/docs", "/redoc", "/docs/oauth2-redirect"]:
                endpoints.append({
                    "path": path,
                    "methods": methods,
                    "name": getattr(route, "name", "N/A"),
                    "summary": getattr(route, "summary", "") or getattr(route, "description", ""),
                    "tags": getattr(route, "tags", []),
                })

    endpoints.sort(key=lambda x: x["path"])
    return {
        "status": "success",
        "total_endpoints": len(endpoints),
        "timestamp": datetime.now().isoformat(),
        "endpoints": endpoints,
    }
