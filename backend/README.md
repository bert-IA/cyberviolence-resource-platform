# Backend - Resource Discovery Platform

API FastAPI pour la découverte et validation de ressources.

## Installation Rapide

```bash
# Créer venv
python3 -m venv venv
source venv/bin/activate

# Installer dépendances
pip install -r requirements.txt

# Démarrer
uvicorn admin_api:app --reload --host 0.0.0.0 --port 8001
```

## Configuration

Créer un fichier `.env` :

```bash
LLM_PROVIDER=gemini
GEMINI_API_KEY=AIza...  # Obtenir sur https://ai.google.dev
```

## Scripts Utiles

```bash
# Lister les modèles Gemini disponibles
python3 list_gemini_models.py

# Démarrer le serveur
./start_server.sh

# Arrêter le serveur
./stop_server.sh
```

## Structure

```
backend/
├── core/                    # Modules métier
│   ├── llm_manager.py       # Gestion LLM (Gemini/OpenRouter)
│   ├── api_adapter.py       # Adapter legacy
│   ├── geo_discovery.py     # Découverte géographique
│   ├── dual_validation.py   # Validation dual-phase
│   └── ...
├── admin_api.py             # Point d'entrée FastAPI
├── constants.py             # Configuration
├── response_service.py      # Réponses standardisées
└── requirements.txt         # Dépendances Python
```

## Tests

```bash
# Health check
curl http://localhost:8001/health

# Test découverte
curl -X POST http://localhost:8001/geographic/discover \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer admin-token-2024" \
  -d '{
    "language": "FR",
    "categories": ["emergency"],
    "countries": ["FR"],
    "max_per_category": 1
  }'
```

Voir [../docs/](../docs/) pour plus de détails.
