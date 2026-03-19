# Backend — Resource Discovery Platform

API FastAPI de découverte, validation et export de ressources d'aide contre la cyberviolence.

---

## Démarrage rapide

```bash
# Créer et activer le venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Configurer les clés API (voir section Configuration)
cp .env.example .env  # ou créer manuellement

# Lancer le serveur
./start_server.sh        # produit — port 8000
# ou
python3 admin_api.py     # direct uvicorn
```

Le serveur écoute sur `http://0.0.0.0:8000`.  
Documentation interactive : `http://localhost:8000/docs`

---

## Configuration

Fichier `.env` à créer à la racine de `backend/` :

```bash
# Fournisseur LLM actif (gemini | openrouter)
LLM_PROVIDER=gemini

# Clé Google Gemini — https://ai.google.dev
GEMINI_API_KEY=AIza...

# Clé OpenRouter (fournisseur alternatif)
OPENROUTER_API_KEY=sk-or-...
```

Le fournisseur actif peut aussi être changé à chaud via `POST /admin/config/llm-provider`.

---

## Structure des fichiers

```
backend/
├── admin_api.py              # Point d'entrée FastAPI (thin — délègue tout aux routers)
├── constants.py              # Données statiques (pays par langue, tokens, etc.)
├── response_service.py       # Helpers ResponseService / ErrorHandler / OperationLogger
├── requirements.txt
├── config.json               # Configuration persistante pays/langues (géré par ConfigManager)
├── working_resources.json    # Ressources en cours de workflow (discovered → rag_ready)
├── rag_resources.json        # Ressources finalisées, prêtes pour le RAG
│
├── routers/                  # Couche HTTP — un fichier par domaine
│   ├── auth.py               # verify_admin_token (Bearer admin-token-2024)
│   ├── health.py             # GET /, /health, /admin/endpoints
│   ├── config.py             # /admin/config/*, /admin/workflow/*, /admin/export/*
│   ├── geographic.py         # /geographic/*
│   ├── discovery.py          # /discover-by-category/*, /discover-batch/*
│   ├── sources.py            # /sources/*, /manage-rag-source
│   └── admin_ops.py          # /admin/duplicates/*, /admin/deduplicate
│
└── core/                     # Couche métier — aucune dépendance FastAPI
    ├── llm_manager.py        # Abstraction LLM (Gemini / OpenRouter)
    ├── category_prompts.py   # Génération de prompts par catégorie
    ├── api_adapter.py        # Orchestration des découvertes LLM
    ├── workflow_manager.py   # State machine + persistance JSON
    ├── config_manager.py     # CRUD config.json (pays/langues/search_terms)
    ├── geo_discovery.py      # Découverte dynamique des pays par langue
    ├── dual_validation.py    # Validation en deux phases (geo + critique)
    ├── deduplication_service.py
    ├── priority_discovery_service.py
    ├── criteria_validation.py
    ├── content_scraper.py
    ├── bulk_scraper.py
    ├── extracted_data.py
    └── resource_models.py    # Modèles Pydantic / enums métier
```

---

## Authentification

Toutes les routes sensibles (`/admin/*`, `/geographic/discover`, `/discover-batch/*`) exigent :

```
Authorization: Bearer admin-token-2024
```

Le token est défini dans `constants.py` (`ADMIN_TOKEN_DEV`). La vérification est centralisée dans `routers/auth.py` — les routers obtiennent la dépendance via `Depends(verify_admin_token)`.

---

## Routes API

### Santé & Métadonnées

| Méthode | Route | Description |
|---------|-------|-------------|
| `GET` | `/health` | État du serveur, provider LLM actif, stats ressources |
| `GET` | `/admin/endpoints` | Liste toutes les routes enregistrées |

---

### Configuration — `/admin/config/*`

Gestion dynamique des langues et des pays (persisté dans `config.json`).

| Méthode | Route | Auth | Description |
|---------|-------|------|-------------|
| `GET` | `/admin/config/llm-providers` | — | Fournisseurs LLM disponibles |
| `POST` | `/admin/config/llm-provider` | — | Changer le fournisseur actif à chaud |
| `GET` | `/admin/config/countries-languages` | — | Toute la configuration (langues + pays) |
| `GET` | `/admin/config/countries-languages/{language}` | — | Config d'une langue |
| `PUT` | `/admin/config/countries-languages/{language}` | ✅ | Mettre à jour une langue |
| `POST` | `/admin/config/countries-languages/{language}/countries` | ✅ | Ajouter un pays |
| `DELETE` | `/admin/config/countries-languages/{language}/countries/{country_code}` | ✅ | Supprimer un pays |
| `DELETE` | `/admin/config/countries-languages/{language}` | ✅ | Supprimer une langue |
| `POST` | `/admin/config/countries-languages/{language}/auto-populate` | ✅ | Découvrir automatiquement les pays via `geo_discovery` |
| `GET` | `/admin/config/stats` | — | Stats globales (nb langues, pays, ressources) |

**Contraintes Pydantic sur `LanguageConfig` :** max 10 pays par langue, `country_code` 2-3 caractères ISO.

---

### Workflow & Export — `/admin/workflow/`, `/admin/export/`, `/admin/sync-rag`

| Méthode | Route | Description |
|---------|-------|-------------|
| `GET` | `/admin/workflow/status` | État du workflow (compteurs par statut) |
| `GET` | `/admin/export/rag-ready` | Export JSON des ressources `rag_ready` |
| `POST` | `/admin/sync-rag` | Synchronise `working_resources.json` → `rag_resources.json` |
| `GET` | `/admin/geographic-discovery` | Résumé de la dernière découverte géographique |
| `GET` | `/admin/sources-validation` | Résumé des sources en attente de validation |

---

### Découverte géographique — `/geographic/*`

| Méthode | Route | Auth | Description |
|---------|-------|------|-------------|
| `GET` | `/geographic/countries` | — | Config pays statique (`constants.py`) |
| `GET` | `/geographic/countries-by-language/{language}` | — | Pays pour une langue (max 5, via `geo_discovery`) |
| `GET` | `/geographic/countries-dynamic/{language}` | — | idem, max configurable |
| `POST` | `/geographic/discover` | ✅ | **Lance une découverte multi-catégories** |
| `GET` | `/geographic/results` | — | Ressources en statut `geo_pending` |
| `POST` | `/geographic/clear-cache` | ✅ | Vide le cache `geo_discovery` |
| `POST` | `/geographic/validate-batch` | ✅ | Valider / rejeter des ressources en lot |

**Body de `/geographic/discover` :**
```json
{
  "language": "FR",
  "categories": ["signalement_autorite", "procedure_plateforme", "service_support"],
  "countries": ["France", "Belgique", "Canada"],
  "max_per_category": 3
}
```

---

### Découverte par catégorie — `/discover-by-category/*`, `/discover-batch/*`

| Méthode | Route | Auth | Description |
|---------|-------|------|-------------|
| `POST` | `/discover-by-category/{category}` | ✅ | Découverte ciblée sur un pays |
| `POST` | `/discover-batch/category-multi-countries` | ✅ | Une catégorie × plusieurs pays |
| `POST` | `/discover-batch/all-platforms` | ✅ | Toutes les procédures plateformes (Instagram, TikTok…) |
| `POST` | `/discover-batch/language-complete` | ✅ | Toutes catégories × tous pays d'une langue |
| `GET` | `/categories/stats/{country_code}` | — | Progression lean par catégorie pour un pays |

**Catégories valides (V2) :**

| Catégorie | Description | Alias |
|-----------|-------------|-------|
| `service_support` | Services nationaux d'aide contre la cyberviolence | — |
| `procedure_plateforme` | Procédures de signalement sur les plateformes (Instagram, TikTok, Discord…) | — |
| `signalement_autorite` | Plateformes gouvernementales de signalement (PHAROS, BKA…) | — |
| `contact_urgence` | *(Deprecated V1 — redirige vers `service_support`)* | alias |

---

### Sources & Validation — `/sources/*`

| Méthode | Route | Description |
|---------|-------|-------------|
| `GET` | `/sources` | Liste des ressources (filtre optionnel `?status=`) |
| `GET` | `/sources/summary` | Stats par pays et par catégorie (filtre `?status=`) |
| `GET` | `/sources/{id}` | Détail complet d'une ressource + historique de validation |
| `PATCH` | `/sources/{id}` | Modifier les champs éditables d'une ressource (sauf `rag_ready`) |
| `POST` | `/sources/{id}/validate` | Valider une ressource — enchaîne les transitions automatiques selon le statut courant |
| `POST` | `/sources/{id}/reject` | Rejeter une ressource — transition vers l'état terminal correspondant |
| `POST` | `/manage-rag-source` | Gérer les ressources exportées : `delete` ou `revert_to_pending` |

**Champs éditables via `PATCH /sources/{id}` :** `name`, `website`, `direct_link`, `phone`, `email`, `description`, `action_type`, `is_governmental`, `scope_audience`, `scope_violence`, `scope_anonymous`.

**Chaînes de transitions automatiques :**
- `geo_pending` → validate → `geo_validated` → `critical_pending` (en une opération)
- `critical_pending` → validate → `critical_validated` → `rag_ready` + écriture dans `rag_resources.json` (en une opération)
- `geo_pending` → reject → `geo_rejected` (terminal)
- `critical_pending` → reject → `critical_rejected` (terminal)

---

### Administration — `/admin/duplicates/*`, `/admin/deduplicate`, `/admin/discovery-*`, `/admin/migration/*`

| Méthode | Route | Description |
|---------|-------|-------------|
| `GET` | `/admin/duplicates/analyze` | Détecter les doublons dans `working_resources.json` |
| `POST` | `/admin/duplicates/cleanup` | Nettoyer les doublons détectés |
| `POST` | `/admin/duplicates/analyzed` | Marquer des ressources comme analysées |
| `POST` | `/admin/deduplicate` | Déduplication complète en une passe |
| `GET` | `/admin/discovery-status/{country}` | Progression de la découverte pour un pays (par catégorie) |
| `GET` | `/admin/discovery-due/{country}` | Catégories non encore découvertes pour un pays |
| `POST` | `/admin/migration/from-unified` | Migration depuis un fichier unifié legacy |

---

## Workflow des ressources

```
discovered
    │
    ▼
geo_pending  ──reject──▶  geo_rejected (terminal)
    │
  approve
    │
    ▼
geo_validated
    │
    ▼
critical_pending  ──reject──▶  critical_rejected (terminal)
    │
  approve
    │
    ▼
critical_validated
    │
    ▼
rag_ready (terminal — exporté dans rag_resources.json)
```

La machine d'états est implémentée dans `core/workflow_manager.py` (`WorkflowStatus.VALID_TRANSITIONS`).  
Les transitions invalides lèvent une exception. Toutes les ressources vivent dans `working_resources.json` jusqu'à leur promotion en `rag_ready`.

---

## Pipeline de découverte LLM

```
POST /geographic/discover
        │
        ▼
api_adapter.start_geographic_discovery_multi_categories()
        │
        ├── pour chaque catégorie :
        │       │
        │       ▼
        │   category_prompts.generate_prompt(category, country, language)
        │       │  → prompt EN (langue pivot)
        │       │
        │       ▼
        │   llm_manager.generate(prompt, system_prompt=CategoryPrompts.get_system_prompt(language))
        │       │  → Gemini : system_prompt préfixé dans le user message
        │       │  → OpenRouter : { "role": "system" } natif
        │       │
        │       ▼
        │   api_adapter._parse_llm_response()
        │       │  → regex multi-champs très tolérant
        │       │  → labels toujours en EN (Name:, URL:, DirectLink:, …)
        │       │
        │       ▼
        │   workflow_manager.add_resource(status="geo_pending")
        │
        ▼
working_resources.json (persisté)
```

---

## Gestion des prompts

### Stratégie langue pivot (EN)

Tous les prompts métier sont rédigés en anglais dans `core/category_prompts.py`.  
La langue de réponse est contrôlée par un **system_prompt** transmis séparément au LLM :

```python
# category_prompts.py
CategoryPrompts.get_system_prompt("JA")
# → "You are a research assistant … Always respond entirely in Japanese.
#    Keep the field label names exactly as written in the prompt (do not translate them)."
```

Avantage : n'importe quel code ISO 639-1 fonctionne (`JA`, `KO`, `AR`, `ZH`…) grâce à `langcodes`.

### Format de réponse LLM attendu

Les prompts imposent des labels de champs fixes (en anglais) pour que le parser reste robuste quel que soit la langue du contenu :

```
Name: [valeur traduite]
URL: https://...
DirectLink: https://...
Description: [valeur traduite]
Phone: ...
Audience: [minors | all]
ViolenceType: [cyberviolence | all]
Anonymous: [yes | no]
Governmental: [yes | no]
```

### Parser (`_parse_llm_response`)

Implémenté dans `api_adapter.py`, le parser est **très tolérant** :
- regex `re.search` (pas `re.match`) — accepte l'indentation et les préfixes
- fallbacks multiples pour le nom (ligne sans `:`  si aucun label reconnu)
- détection automatique URLs et numéros de téléphone sans label
- normalisation des booléens multilingues (`oui/yes/sí/sim/ja` → `True`)

### Exclusion des doublons inter-appels

À chaque tentative d'une boucle de découverte, les noms déjà trouvés sont injectés dans le prompt :
```
⛔ ABSOLUTELY AVOID these already found resources: 3018, e-Enfance, Signal pour signaler
```

---

## Gestion LLM (`core/llm_manager.py`)

| Provider | Classe | Clé env | Notes |
|----------|--------|---------|-------|
| Google Gemini | `GeminiClient` | `GEMINI_API_KEY` | `google-generativeai` 0.3.x — system_prompt préfixé dans le user message |
| OpenRouter | `OpenRouterClient` | `OPENROUTER_API_KEY` | REST `/v1/chat/completions` — system_prompt via `{"role":"system"}` |

**Retry logic :** 3 tentatives, délai exponentiel. Rate-limiting HTTP 429 → attente 60 s × tentative.

**Changement à chaud :**
```bash
curl -X POST http://localhost:8000/admin/config/llm-provider?provider=openrouter \
  -H "Authorization: Bearer admin-token-2024"
```

---

## Configuration pays/langues (`core/config_manager.py`)

La configuration live est dans `config.json` (pas dans `constants.py` qui reste statique).

**Modèles Pydantic :**
- `CountryConfig` : `country_name`, `country_code` (2-3 chars ISO), `flag`, `organizations_count`
- `LanguageConfig` : `name`, `code` (2 chars), `search_terms`, `countries` (max 10)

**Auto-populate :** `POST /admin/config/countries-languages/{language}/auto-populate` interroge `geo_discovery.get_countries_by_language()` (API REST Countries + fallback `guaranteed_countries`) et convertit les codes pays en emojis drapeaux via `chr(0x1F1E0 + ord(c))`.

---

## Données de test rapides

```bash
# Health check
curl http://localhost:8000/health

# Liste des langues configurées
curl http://localhost:8000/admin/config/countries-languages

# Lancer une découverte (authentifié)
curl -X POST http://localhost:8000/geographic/discover \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer admin-token-2024" \
  -d '{
    "language": "FR",
    "categories": ["service_support"],
    "countries": ["France"],
    "max_per_category": 2
  }'

# Voir les ressources en attente
curl http://localhost:8000/sources?status=geo_pending
```

---

## Export RAG

### Rôle de l'application

Ce backend est un **producteur de documents** pour un système RAG externe déjà existant. Il ne contient aucune logique de RAG. Son rôle est de découvrir, valider et structurer des ressources d'aide en ligne, puis de les exporter sous forme de documents JSON complets et exploitables directement par un pipeline RAG.

### Persistance en deux couches

| Fichier | Contenu | Usage |
|---------|---------|-------|
| `working_resources.json` | Toutes les ressources, tous statuts confondus | Source de vérité interne, lecture/écriture permanente |
| `rag_resources.json` | Sous-ensemble `rag_ready` uniquement, format plat 17 champs | Consommé par le RAG externe |

`rag_resources.json` est mis à jour automatiquement à chaque promotion d'une ressource au statut `rag_ready`. Au démarrage du serveur, `sync_rag_data()` resynchronise ce fichier depuis `working_resources.json` pour corriger toute désynchronisation.

### Chemins vers `rag_ready`

Une ressource peut atteindre le statut terminal `rag_ready` par trois chemins :

1. **Workflow complet** : `discovered → geo_pending → geo_validated → critical_pending → critical_validated → rag_ready`
2. **Promotion directe depuis `critical_validated`** : validation manuelle via `POST /manage-rag-source`
3. **Promotion directe depuis `geo_validated`** : saut de l'étape critique via `POST /manage-rag-source`

### Schéma d'un document RAG

Chaque document présent dans `rag_resources.json` contient les 17 champs suivants :

| Champ | Type | Description |
|-------|------|-------------|
| `organization_name` | `string` | Nom de l'organisation ou de la ressource |
| `description` | `string` | Description complète du service |
| `website` | `string` | URL principale du site |
| `direct_link` | `string` | URL directe vers la page de contact ou d'aide |
| `phone` | `string` | Numéro de téléphone de contact |
| `email` | `string` | Adresse email de contact |
| `country_name` | `string` | Nom du pays en clair |
| `country_code` | `string` | Code ISO 3166-1 alpha-2 du pays |
| `language` | `string` | Code ISO 639-1 de la langue (ex. `FR`, `EN`, `JA`) |
| `category` | `string` | Catégorie métier (`service_support`, `procedure_plateforme`, `signalement_autorite`) |
| `action_type` | `string` | Type d'action proposée (`chat`, `phone`, `form`, `email`, `hotline`) |
| `is_governmental` | `boolean` | Indique si la ressource est gouvernementale |
| `scope_audience` | `string` | Public cible (`minors`, `all`) |
| `scope_violence` | `string` | Type de violence adressé (`cyberviolence`, `all`) |
| `scope_anonymous` | `boolean` | Indique si le contact est anonyme |
| `confidence_score` | `float` | Score de confiance attribué lors de la découverte (0.0 – 1.0) |
| `finalized_at` | `string` | Horodatage ISO 8601 de la promotion au statut `rag_ready` |

### Endpoint d'export

```
GET /admin/export/rag-ready
Authorization: Bearer <token>
```

Réponse :

```json
{
  "success": true,
  "total": 42,
  "export_timestamp": "2024-01-15T10:30:00.000000",
  "summary": {
    "by_language": { "FR": 18, "EN": 12, "ES": 7, "DE": 5 },
    "by_category": {
      "service_support": 20,
      "procedure_plateforme": 15,
      "signalement_autorite": 7
    }
  },
  "documents": [
    {
      "id": "uuid-de-la-ressource",
      "organization_name": "e-Enfance / 3018",
      "description": "Service national d'aide aux victimes de cyberharcèlement...",
      "website": "https://www.e-enfance.org",
      "direct_link": "https://www.e-enfance.org/signaler-une-situation/",
      "phone": "3018",
      "email": "",
      "country_name": "France",
      "country_code": "FR",
      "language": "FR",
      "category": "service_support",
      "action_type": "hotline",
      "is_governmental": false,
      "scope_audience": "minors",
      "scope_violence": "cyberviolence",
      "scope_anonymous": true,
      "confidence_score": 0.92,
      "finalized_at": "2024-01-15T10:30:00.000000"
    }
  ]
}
```

Le champ `id` est l'identifiant UUID interne de la ressource dans `working_resources.json`. Le tableau `documents` est une liste plate — chaque entrée est auto-suffisante pour l'ingestion RAG.
