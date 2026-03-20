# Frontend — Resource Discovery Platform

Interface d'administration React pour piloter la découverte, la validation et l'export RAG de ressources d'aide contre la cyberviolence.

---

## Démarrage rapide

```bash
# Depuis le dossier frontend/
npm install
npm run dev
```

L'application est disponible sur `http://localhost:5173`.

> Le backend doit tourner sur `http://localhost:8000` (voir `backend/README.md`).

---

## Configuration

L'URL du backend est définie dans `src/services/api.ts` :

```ts
export const API_BASE_URL = 'http://localhost:8000'
export const AUTH_TOKEN = 'Bearer admin-token-2024'
```

Modifier ces valeurs directement pour pointer vers un backend distant.

---

## Stack technique

| Outil | Version | Rôle |
|-------|---------|------|
| React | 19 | UI |
| TypeScript | 5.9 | Typage statique |
| Vite | 7 | Build & dev server |
| TanStack Query | 5 | Fetching & cache serveur |
| React Router | 7 | Routing SPA |
| Tailwind CSS | 3.4 | Styles utilitaires |
| react-hot-toast | 2 | Notifications |

---

## Scripts disponibles

| Commande | Description |
|----------|-------------|
| `npm run dev` | Lance le serveur de développement (port 5173) |
| `npm run build` | Compile TypeScript + build de production dans `dist/` |
| `npm run preview` | Prévisualise le build de production localement |
| `npm run lint` | Analyse statique ESLint |

---

## Structure des fichiers

```
frontend/src/
├── main.tsx                    # Point d'entrée — QueryClient + BrowserRouter
├── App.tsx                     # Déclaration des routes
│
├── pages/
│   ├── MenuPage.tsx            # Accueil — navigation vers les modules
│   ├── ConfigurationPage.tsx   # Gestion des langues et pays (config.json)
│   ├── DiscoveryPage.tsx       # Lancement des découvertes LLM
│   ├── ValidationPage/         # Validation geo_pending → geo_validated
│   │   ├── Index.tsx           # Orchestrateur — stepper (overview → review)
│   │   ├── OverviewStep.tsx    # Sélection des ressources à valider
│   │   └── ReviewStep.tsx      # Validation/rejet une par une
│   ├── RagPage.tsx             # Validation RAG (critical_pending → rag_ready)
│   └── NotFound.tsx            # Route 404
│
├── components/
│   ├── layout/
│   │   ├── MainLayout.tsx      # Shell principal — Sidebar + Outlet
│   │   └── Sidebar.tsx         # Navigation latérale
│   ├── features/
│   │   ├── DiscoveryForm.tsx           # Formulaire de découverte LLM
│   │   ├── DiscoveredResourcesList.tsx # Liste des ressources découvertes
│   │   ├── DiscoveredResourceCard.tsx  # Carte d'une ressource découverte
│   │   ├── ResourcesList.tsx           # Liste générique (validation)
│   │   ├── ResourceCard.tsx            # Carte ressource avec actions
│   │   ├── ValidationActions.tsx       # Boutons valider/rejeter groupés
│   │   ├── RagValidationModal.tsx      # Modal détail + édition + actions RAG
│   │   ├── AddResourceModal.tsx        # Modal ajout manuel d'une ressource
│   │   └── LanguageCard.tsx            # Carte langue (page Configuration)
│   └── ui/
│       ├── Button.tsx          # Composant bouton générique
│       ├── AppHeader.tsx       # En-tête de page
│       ├── ErrorMessage.tsx    # Affichage d'erreur
│       ├── LoadingSpinner.tsx  # Indicateur de chargement
│       ├── ExpandableText.tsx  # Texte tronqué / expandable
│       └── LinkButton.tsx      # Bouton lien externe
│
├── hooks/                      # TanStack Query — un hook par opération API
│   ├── useResources.ts                 # GET /sources?status=
│   ├── useResourceById.ts              # GET /sources/{id}
│   ├── useResourceByStatus.ts          # GET /sources (filtré)
│   ├── useResourceStats.ts             # GET /admin/config/stats
│   ├── useDiscoverResources.ts         # POST /geographic/discover
│   ├── useValidateResource.ts          # POST /sources/{id}/validate
│   ├── useRejectResource.ts            # POST /sources/{id}/reject
│   ├── usePatchResource.ts             # PATCH /sources/{id}
│   ├── useValidateBatch.ts             # POST /geographic/validate-batch
│   ├── useValidationWorkflow.ts        # Orchestration multi-étapes
│   └── useCountriesLanguagesConfig.ts  # GET /admin/config/countries-languages
│
├── services/
│   └── api.ts                  # Interfaces TypeScript + fonctions fetch
│
└── utils/
    └── formatters.ts           # Helpers de formatage (dates, labels, etc.)
```

---

## Pages & fonctionnalités

### `/` — Menu
Tableau de bord avec accès rapide à chaque module.

### `/configuration` — Configuration
Gestion des langues et des pays utilisés pour les découvertes. Wrappé sur le backend `GET/PUT /admin/config/countries-languages`.

### `/decouverte` — Découverte
Formulaire pour lancer une découverte LLM (`POST /geographic/discover`). Affiche les ressources trouvées avec leur score de confiance.

### `/validation` — Validation géographique
Stepper en deux étapes :
1. **Overview** — liste des ressources `geo_pending` avec sélection groupée
2. **Review** — validation ou rejet une par une, avec transitions automatiques `geo_pending → geo_validated → critical_pending`

### `/rag` — Validation RAG
Deux onglets :
- **À valider** — ressources `critical_pending` : modal d'édition + Valider / Rejeter
- **Validées** — ressources `rag_ready` : lecture seule (actions d'édition masquées)

Ajout manuel possible via le bouton "+ Ajout Manuel".

---

## Flux de données

```
Hook (TanStack Query)
    │  useQuery / useMutation
    ▼
services/api.ts
    │  fetch()
    ▼
Backend FastAPI   http://localhost:8000
```

TanStack Query gère le cache, le refetch automatique et l'invalidation après mutation. Chaque mutation invalide les queries dépendantes pour forcer un rechargement des listes.
