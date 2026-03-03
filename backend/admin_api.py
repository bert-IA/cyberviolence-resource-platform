"""
Admin API - Point d'entrée principal (thin entry point)
Toute la logique métier est déléguée aux routers modulaires.

Architecture :
    routers/health.py      → GET /, /favicon.ico, /health, /admin/endpoints
    routers/config.py      → /admin/config/*, /admin/workflow/status, /admin/export/*, ...
    routers/geographic.py  → /geographic/*
    routers/discovery.py   → /discover-by-category/*, /discover-batch/*, /categories/stats/*
    routers/sources.py     → /sources/*, /manage-rag-source
    routers/admin_ops.py   → /admin/duplicates/*, /admin/discovery-*, /admin/deduplicate, ...
"""
from dotenv import load_dotenv
load_dotenv()  # Charge .env AVANT toute initialisation des modules LLM

import logging
logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s %(name)s: %(message)s"
)

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from typing import List, Dict, Any, Optional
from datetime import datetime
import os
from dotenv import load_dotenv

# Charger les variables d'environnement depuis .env
load_dotenv()

# Import des nouveaux modules
from core.api_adapter import get_api_adapter
from core.llm_manager import LLMProvider, get_llm_manager
from core.deduplication_service import DeduplicationService
from core.priority_discovery_service import PriorityDiscoveryService

# Import du module d'authentification centralisé
from routers.auth import verify_admin_token  # noqa: F401 — réexporté pour backward compat

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

# verify_admin_token est importé depuis routers/auth.py
# (accessible ici pour backward compat si besoin)


# === INITIALISATION DES SERVICES ===
dedup_service = DeduplicationService()
discovery_service = PriorityDiscoveryService()

# === ENREGISTREMENT DES ROUTERS ===
from routers import health, config, geographic, discovery, sources, admin_ops

app.include_router(health.router)
app.include_router(config.router)
app.include_router(geographic.router)
app.include_router(discovery.router)
app.include_router(sources.router)
app.include_router(admin_ops.router)


# === GESTIONNAIRE GLOBAL D'EXCEPTIONS ===

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Intercepte toutes les exceptions non gérées"""
    logger.error(f"Erreur non gérée: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "message": "Erreur interne du serveur",
            "error_type": type(exc).__name__
        }
    )


# === LANCEMENT DU SERVEUR ===

if __name__ == "__main__":
    import uvicorn

    logger.info("🚀 Démarrage du serveur Admin API...")
    logger.info("📍 Écoute sur http://0.0.0.0:8000")
    logger.info("📚 Documentation: http://localhost:8000/docs")

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
