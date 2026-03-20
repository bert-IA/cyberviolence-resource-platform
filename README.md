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
├── backend/          → FastAPI + Python 3.12 + Google Gemini LLM
└── frontend/         → React 19 + TypeScript + Vite
```

## 🚀 Quick Start

### Prérequis
- Python 3.11+
- Node.js 18+
- Clé API Google Gemini (gratuite sur https://ai.google.dev)

---

### Backend

```bash
cd backend

# Créer l'environnement virtuel
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Installer les dépendances
pip install -r requirements.txt

# Configurer les variables d'environnement
cp .env.example .env
# Éditer .env et renseigner clé API

# Démarrer le serveur
./start_server.sh
# ou manuellement :
uvicorn admin_api:app --reload --host 0.0.0.0 --port 8000
```

API disponible sur : http://localhost:8000
Health check : http://localhost:8000/health

---

### Frontend

```bash
cd frontend

# Installer les dépendances
npm install

# Démarrer en mode développement
npm run dev
```

Interface disponible sur : http://localhost:5173

---

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

## 🛠️ Technologies

**Backend:**
- FastAPI 0.104+
- Python 3.11+
- Google Gemini 2.5 Flash (LLM)
- PostgreSQL (optionnel pour analytics)

**Frontend :**
- React 19
- TypeScript
- Vite
- TanStack Query
- Tailwind CSS

## 📝 Licence

Projet privé - StopCyberViolences

## 👥 Contributeurs

Développé avec ❤️ pour aider dans la lutte contre le cyberharcèlement.
