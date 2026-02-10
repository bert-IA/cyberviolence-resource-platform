# 🌍 Resource Discovery Platform

**Platform d'administration pour la découverte, validation et gestion de ressources d'aide contre le cyberharcèlement.**

## 📋 Vue d'ensemble

Ce projet permet aux administrateurs de :
- 🔍 **Découvrir** des ressources via LLM (Google Gemini) dans 6 langues et 30+ pays
- ✅ **Valider** les ressources (géographique + critères qualité)
- 📊 **Extraire** les données de contact (téléphone, email, URL)
- 🤖 **Préparer** pour intégration RAG (chatbot)

## 🏗️ Architecture

```
resource-discovery-platform/
├── backend/          → FastAPI + Python 3.11 + Google Gemini LLM
├── frontend/         → React 18 + TypeScript + Vite (en cours)
└── docs/             → Documentation technique
```

## 🚀 Quick Start - Backend

### Prérequis
- Python 3.11+
- Clé API Google Gemini (gratuite sur https://ai.google.dev)

### Installation

```bash
cd backend

# Créer l'environnement virtuel
python3 -m venv venv
source venv/bin/activate

# Installer les dépendances
pip install -r requirements.txt

# Configurer l'environnement
cp .env.example .env  # Puis éditer avec ta clé API
```

### Configuration `.env`

```bash
# Provider LLM (gemini recommandé)
LLM_PROVIDER=gemini

# Clé API Google Gemini
GEMINI_API_KEY=AIza...  # Obtenir sur https://ai.google.dev

# Optionnel: OpenRouter (backup)
OPENROUTER_API_KEY=sk-or-v1-...
```

### Démarrage

```bash
# Mode développement (auto-reload)
uvicorn admin_api:app --reload --host 0.0.0.0 --port 8001

# Ou mode production
python3 admin_api.py
```

**API disponible sur** : http://localhost:8001

**Health check** : http://localhost:8001/health

## 🔗 Endpoints Principaux

### Découverte Géographique
```bash
POST /geographic/discover
Content-Type: application/json
Authorization: Bearer admin-token-2024

{
  "language": "FR",
  "categories": ["emergency", "local"],
  "countries": ["FR", "BE"],
  "max_per_category": 3
}
```

### Validation Batch
```bash
POST /geographic/validate-batch
Content-Type: application/json
Authorization: Bearer admin-token-2024

{
  "action": "approve",  // ou "reject"
  "resource_ids": ["DISCOVERED_FR_1", "DISCOVERED_FR_2"]
}
```

### Extraction de Données
```bash
GET /sources/{resource_id}/extracted-data
Authorization: Bearer admin-token-2024
```

## 🌐 Langues Supportées

- 🇫🇷 Français (FR)
- 🇬🇧 English (EN)
- 🇪🇸 Español (ES)
- 🇩🇪 Deutsch (DE)
- 🇮🇹 Italiano (IT)
- 🇵🇹 Português (PT)

## 📊 Workflow

```
1. Découverte (LLM)
   ↓
2. Validation Géographique (Admin)
   ↓
3. Validation Critères (Admin)
   ↓
4. Extraction Données (Automatique)
   ↓
5. RAG Ready (Chatbot)
```

## 🧪 Tests

```bash
cd backend
source venv/bin/activate

# Tester la connexion LLM
python3 list_gemini_models.py

# Health check
curl http://localhost:8001/health
```

## 📚 Documentation

- [Architecture Complète](docs/DECOUVERTE_SYSTEME_EXISTANT.md)
- [Guide React](docs/JOUR_1_SETUP.md) (frontend à venir)
- [Workflow Métier](docs/ANALYSE_WORKFLOW_METIER.md)

## 🛠️ Technologies

**Backend:**
- FastAPI 0.104+
- Python 3.11+
- Google Gemini 2.5 Flash (LLM)
- PostgreSQL (optionnel pour analytics)

**Frontend (à venir):**
- React 18
- TypeScript
- Vite
- TanStack Query
- Tailwind CSS

## 📝 Licence

Projet privé - StopCyberViolences

## 👥 Contributeurs

Développé avec ❤️ pour aider dans la lutte contre le cyberharcèlement.
