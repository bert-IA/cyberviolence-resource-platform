# 🏗️ Architecture React - Discussion Pédagogique

**Date**: 2026-02-10  
**Objectif**: Définir une architecture React professionnelle et production-ready

---

## 🎯 Contraintes & Objectifs

### Besoins Identifiés
✅ **Production-ready** : Architecture scalable et maintenable  
✅ **Structure propre** : Organisation claire et logique  
✅ **Admin dashboard** : Interface d'administration (pas public-facing)  
✅ **CRUD complexe** : Gestion workflow multi-étapes  
✅ **API REST** : Backend FastAPI déjà existant sur port 8001  

### Contexte Technique Existant
- **Backend**: FastAPI (Python) - Port 8001
- **Auth**: Token bearer `admin-token-2024` (à améliorer)
- **Endpoints**: ~20 endpoints API documentés
- **Workflow**: 5 statuts (discovered → geo_pending → geo_validated → critical_pending → critical_validated → rag_ready)
- **Données**: JSON via working_resources.json

---

## 🤔 Questions Architecturales Clés

### 1️⃣ TypeScript ou JavaScript ?

**Question formateur** : Quel est ton niveau de confort avec TypeScript ?

#### Option A : TypeScript dès le début
**Avantages** ✅
- Typage fort → moins d'erreurs runtime
- Autocomplétion IDE puissante
- Refactoring plus sûr
- Standard moderne pour apps production
- Type-safe avec les réponses API

**Inconvénients** ❌
- Courbe d'apprentissage ajoutée
- Setup initial plus complexe
- Peut ralentir au début

**Best practice** : TypeScript est le standard pour apps production en 2026

#### Option B : JavaScript puis migration progressive
**Avantages** ✅
- Démarrage rapide
- Focus sur React sans distraction TypeScript
- Migration progressive possible

**Inconvénients** ❌
- Moins de sécurité
- Plus d'erreurs potentielles
- Migration future coûteuse

**🎓 Question pour toi** : As-tu déjà utilisé TypeScript ? Es-tu prêt à l'apprendre en même temps que React ?

**Ma recommandation** : TypeScript dès le début (je t'expliquerai les types au fur et à mesure)

---

### 2️⃣ State Management : Quelle solution ?

**Contexte** : Ton app a besoin de partager des états (user auth, workflow status, resources list)

#### Option A : Context API (natif React)
```
Complexité: ⭐⭐☆☆☆
Setup: Simple
Performance: Moyenne
```

**Avantages** ✅
- Natif React (pas de dépendance)
- Simple pour petites apps
- Parfait pour auth et thème

**Inconvénients** ❌
- Re-renders inutiles si mal utilisé
- Verbeux pour état complexe
- Pas de devtools puissants

**Quand utiliser** : Auth globale, configuration, thème

#### Option B : Zustand (recommandé pour toi)
```
Complexité: ⭐⭐☆☆☆
Setup: Très simple
Performance: Excellente
```

**Avantages** ✅
- API minimale et intuitive
- Pas de boilerplate
- Excellent perf (pas de Context)
- Devtools disponibles
- Parfait pour CRUD complexe

**Inconvénients** ❌
- Dépendance externe (petite)
- Moins connu que Redux

**Exemple Zustand** :
```typescript
// store/resources.ts
import create from 'zustand'

interface ResourcesStore {
  resources: Resource[]
  loading: boolean
  fetchResources: () => Promise<void>
  updateResource: (id: string, data: Partial<Resource>) => void
}

const useResourcesStore = create<ResourcesStore>((set) => ({
  resources: [],
  loading: false,
  fetchResources: async () => {
    set({ loading: true })
    const data = await api.getResources()
    set({ resources: data, loading: false })
  },
  updateResource: (id, data) => 
    set(state => ({
      resources: state.resources.map(r => 
        r.id === id ? { ...r, ...data } : r
      )
    }))
}))
```

#### Option C : Redux Toolkit
```
Complexité: ⭐⭐⭐⭐☆
Setup: Complexe
Performance: Excellente
```

**Avantages** ✅
- Standard industrie
- Devtools puissants
- Middleware riche
- Très scalable

**Inconvénients** ❌
- Verbeux (beaucoup de code)
- Courbe d'apprentissage raide
- Overkill pour petites apps

**Quand utiliser** : Apps très complexes, équipes grandes

#### Option D : TanStack Query (React Query)
```
Complexité: ⭐⭐⭐☆☆
Setup: Moyen
Performance: Excellente
```

**Avantages** ✅
- Gestion cache automatique
- Optimistic updates natifs
- Refetch automatique
- État loading/error automatique
- **PARFAIT pour apps CRUD avec API**

**Inconvénients** ❌
- Paradigme différent (pas de store global classique)
- Dépendance importante

**Exemple TanStack Query** :
```typescript
// hooks/useResources.ts
import { useQuery, useMutation } from '@tanstack/react-query'

export const useResources = (status?: string) => {
  return useQuery({
    queryKey: ['resources', status],
    queryFn: () => api.getResources(status)
  })
}

export const useUpdateResource = () => {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: (data: UpdateResourceData) => 
      api.updateResource(data.id, data),
    onSuccess: () => {
      queryClient.invalidateQueries(['resources'])
    }
  })
}

// Usage dans composant
const { data, isLoading, error } = useResources('critical_pending')
const updateMutation = useUpdateResource()
```

**🎓 Question pour toi** : 
- Veux-tu apprendre un pattern de state management (Zustand) OU un pattern de data fetching (TanStack Query) ?
- Es-tu à l'aise avec le concept de cache et d'invalidation de queries ?

**Ma recommandation** : 
- **Context API** pour auth uniquement
- **TanStack Query** pour toutes les données API (ressources, critères, etc.)
- **Zustand** si besoin d'état UI global (modals, notifications)

---

### 3️⃣ Bibliothèque UI : Quel Design System ?

**Contexte** : Admin dashboard qui doit être fonctionnel et pro (pas besoin design ultra-custom)

#### Option A : Tailwind CSS
```
Philosophie: Utility-first
Customisation: ⭐⭐⭐⭐⭐
Composants: À construire
Bundle: Très optimisé
```

**Avantages** ✅
- Flexibilité totale
- Petits bundles (tree-shaking)
- Pas de styles overrides
- Très populaire (2026)

**Inconvénients** ❌
- Dois créer tous les composants
- Classes CSS longues
- Pas de composants complexes (datepicker, etc.)

#### Option B : shadcn/ui + Tailwind (⭐ RECOMMANDÉ)
```
Philosophie: Copy-paste components
Customisation: ⭐⭐⭐⭐⭐
Composants: 40+ prêts
Bundle: Optimisé
```

**Avantages** ✅
- Composants Radix UI (accessibilité)
- Tailwind pour style
- Code dans TON projet (pas node_modules)
- Customisable à 100%
- Composants complexes inclus
- **Standard moderne 2026**

**Inconvénients** ❌
- Nécessite Tailwind
- Plus de setup initial

**Composants inclus** : Table, Form, Select, Dialog, Toast, Command Palette, etc.

#### Option C : Material-UI (MUI)
```
Philosophie: Component library complète
Customisation: ⭐⭐⭐☆☆
Composants: 100+ prêts
Bundle: Lourd
```

**Avantages** ✅
- Composants très riches
- Design Material Google
- Ecosystème mature
- Data Grid puissant

**Inconvénients** ❌
- Bundles volumineux
- Overrides CSS complexes
- Look "Material" difficile à changer

#### Option D : Ant Design
```
Philosophie: Enterprise UI
Customisation: ⭐⭐⭐☆☆
Composants: 50+ prêts
Bundle: Moyen
```

**Avantages** ✅
- **Parfait pour admin dashboards**
- Table, Form, Upload très complets
- Design pro et cohérent
- Moins lourd que MUI

**Inconvénients** ❌
- Look "enterprise" marqué
- Moins flexible que Tailwind

**🎓 Question pour toi** :
- Préfères-tu contrôler le style CSS (Tailwind) ou avoir des composants prêts (MUI/Ant) ?
- Veux-tu apprendre Tailwind (très demandé marché) ?

**Ma recommandation** : 
1. **shadcn/ui + Tailwind** (moderne, flexible, production-ready)
2. **Ant Design** si tu veux aller vite sans apprendre Tailwind

---

### 4️⃣ Router : React Router v6 ou TanStack Router ?

#### Option A : React Router v6 (Standard)
```
Popularité: ⭐⭐⭐⭐⭐
Type-safety: Moyenne
Features: Complètes
```

**Avantages** ✅
- Standard de facto React
- Documentation riche
- Communauté énorme
- Stable et mature

**Inconvénients** ❌
- Pas type-safe nativement
- Moins de features modernes

#### Option B : TanStack Router (Moderne)
```
Popularité: ⭐⭐⭐☆☆
Type-safety: ⭐⭐⭐⭐⭐
Features: Très avancées
```

**Avantages** ✅
- Type-safe à 100%
- Intégration TanStack Query
- Search params type-safe
- Route loading states

**Inconvénients** ❌
- Plus récent (moins de ressources)
- Courbe d'apprentissage

**🎓 Question pour toi** : Veux-tu apprendre le standard (React Router) ou la technologie moderne (TanStack) ?

**Ma recommandation** : **React Router v6** (standard, plus simple pour apprendre)

---

### 5️⃣ Build Tool : Vite ou Create React App ?

#### Option A : Vite (⭐ RECOMMANDÉ 2026)
```
Vitesse: ⚡⚡⚡⚡⚡
Dev Server: Instantané
Production: Optimisé
```

**Avantages** ✅
- HMR ultra-rapide
- Build optimisé
- Standard moderne
- Support TypeScript natif

**Inconvénients** ❌
- Moins de templates que CRA

#### Option B : Create React App
```
Vitesse: ⭐⭐⭐☆☆
Dev Server: Lent
Production: Correct
```

**Avantages** ✅
- Setup zero config
- Très documenté

**Inconvénients** ❌
- **Plus maintenu officiellement (deprecated)**
- Très lent
- Build lourd

**🎓 Pas vraiment une question** : Vite est le standard en 2026, CRA est obsolète.

**Ma recommandation** : **Vite** sans hésitation

---

## 🏛️ Structure de Dossiers Proposée

### Structure Production-Ready

```
critical-resources-admin/
├── public/
│   └── favicon.ico
├── src/
│   ├── assets/              # Images, fonts, etc.
│   │   ├── images/
│   │   └── icons/
│   │
│   ├── components/          # Composants réutilisables
│   │   ├── ui/             # Composants UI basiques (shadcn/ui)
│   │   │   ├── button.tsx
│   │   │   ├── input.tsx
│   │   │   ├── table.tsx
│   │   │   └── ...
│   │   ├── layout/         # Layout components
│   │   │   ├── Header.tsx
│   │   │   ├── Sidebar.tsx
│   │   │   └── MainLayout.tsx
│   │   └── features/       # Composants métier réutilisables
│   │       ├── ResourceCard.tsx
│   │       ├── StatusBadge.tsx
│   │       └── CriteriaChecklist.tsx
│   │
│   ├── pages/               # Pages/Routes
│   │   ├── Dashboard.tsx
│   │   ├── Discovery.tsx
│   │   ├── GeographicValidation.tsx
│   │   ├── CriticalValidation.tsx
│   │   ├── DetailedValidation.tsx
│   │   └── RAGFormatting.tsx
│   │
│   ├── features/            # Features avec logique métier
│   │   ├── discovery/
│   │   │   ├── components/
│   │   │   ├── hooks/
│   │   │   └── api.ts
│   │   ├── validation/
│   │   │   ├── components/
│   │   │   ├── hooks/
│   │   │   └── api.ts
│   │   └── ...
│   │
│   ├── hooks/               # Custom hooks globaux
│   │   ├── useAuth.ts
│   │   ├── useResources.ts
│   │   └── useDebounce.ts
│   │
│   ├── services/            # Services API
│   │   ├── api.ts          # Client axios/fetch
│   │   ├── resources.ts    # Endpoints resources
│   │   ├── validation.ts   # Endpoints validation
│   │   └── auth.ts         # Endpoints auth
│   │
│   ├── lib/                 # Utilities et helpers
│   │   ├── utils.ts        # Fonctions helpers
│   │   ├── constants.ts    # Constantes
│   │   └── validators.ts   # Fonctions validation
│   │
│   ├── types/               # Types TypeScript
│   │   ├── resource.ts
│   │   ├── api.ts
│   │   └── workflow.ts
│   │
│   ├── store/               # State management (si Zustand)
│   │   ├── auth.ts
│   │   └── ui.ts
│   │
│   ├── routes/              # Configuration routing
│   │   └── index.tsx
│   │
│   ├── App.tsx              # Composant racine
│   ├── main.tsx             # Entry point
│   └── index.css            # Styles globaux
│
├── .env.example             # Variables env exemple
├── .env.local               # Variables env local (pas commité)
├── .gitignore
├── package.json
├── tsconfig.json            # Config TypeScript
├── vite.config.ts           # Config Vite
├── tailwind.config.js       # Config Tailwind (si utilisé)
└── README.md
```

### Alternative : Feature-First (Plus scalable)

```
src/
├── features/
│   ├── discovery/
│   │   ├── components/
│   │   ├── hooks/
│   │   ├── api/
│   │   ├── types/
│   │   └── pages/
│   ├── validation/
│   └── rag/
├── shared/                  # Code partagé
│   ├── components/ui/
│   ├── hooks/
│   ├── lib/
│   └── types/
└── app/                     # Config app
    ├── routes/
    ├── store/
    └── providers/
```

**🎓 Question pour toi** : Préfères-tu une structure "par type" (classique) ou "par feature" (moderne) ?

**Ma recommandation** : Structure classique pour démarrer, migration feature-first si projet grandit

---

## 📋 Stack Recommandée (Ma Proposition)

### Core
- ✅ **React 18** (dernière version)
- ✅ **TypeScript** (type-safety)
- ✅ **Vite** (build tool)

### Routing
- ✅ **React Router v6** (routing standard)

### State & Data
- ✅ **TanStack Query** (data fetching, cache)
- ✅ **Zustand** (état UI global)
- ✅ **Context API** (auth uniquement)

### UI
- ✅ **Tailwind CSS** (utility-first)
- ✅ **shadcn/ui** (composants prêts)
- ✅ **Radix UI** (primitives accessibles)

### Forms
- ✅ **react-hook-form** (gestion forms)
- ✅ **zod** (validation schemas)

### API
- ✅ **axios** (client HTTP)

### Testing
- ✅ **Vitest** (test runner)
- ✅ **React Testing Library** (tests composants)

### Dev Tools
- ✅ **ESLint** (linting)
- ✅ **Prettier** (formatting)
- ✅ **TanStack Query Devtools** (debug queries)

---

## 🎯 Prochaines Étapes

### Décisions à Prendre Ensemble

1. **TypeScript ou JavaScript ?**
   - Ma recommandation : TypeScript
   - Ta décision : ?

2. **State Management ?**
   - Ma recommandation : TanStack Query + Zustand
   - Ta décision : ?

3. **UI Library ?**
   - Ma recommandation : shadcn/ui + Tailwind
   - Ta décision : ?

4. **Structure dossiers ?**
   - Ma recommandation : Structure classique
   - Ta décision : ?

### Une Fois Décidé

- [ ] Créer checklist setup projet
- [ ] Préparer commandes installation
- [ ] Définir architecture API service layer
- [ ] Créer composants de base
- [ ] Implémenter première page (Discovery)

---

## 💬 Réponses et Décisions Prises

### Réponses de Bert

1. **Niveau TypeScript** : ✅ Intermédiaire
2. **Tailwind** : ✅ Oui, prêt à l'utiliser (a déjà fait projet e-commerce sans Tailwind)
3. **Priorité** : ✅ Qualité du code maximale
4. **Tests** : ✅ Après (pas dès le début)

---

## ✅ STACK FINALE VALIDÉE

### ⚙️ Technologies Confirmées

#### Core Stack
| Technologie | Version | Justification |
|-------------|---------|---------------|
| **React** | 18.x | Standard moderne, Server Components ready |
| **TypeScript** | 5.x | Type-safety, niveau intermédiaire de Bert |
| **Vite** | 5.x | Build ultra-rapide, standard 2026 |
| **Node.js** | 20.x LTS | Dernière version LTS |

#### Routing & Navigation
| Technologie | Justification |
|-------------|---------------|
| **React Router v6** | Standard industrie, documentation riche |

#### State Management & Data Fetching
| Technologie | Usage | Justification |
|-------------|-------|---------------|
| **TanStack Query (React Query)** | Data fetching API | Cache automatique, optimistic updates, perfect pour CRUD |
| **Zustand** | État UI global | Simple, performant, minimal boilerplate |
| **Context API** | Auth uniquement | Natif React, suffisant pour auth |

#### UI & Styling
| Technologie | Usage | Justification |
|-------------|-------|---------------|
| **Tailwind CSS** | Utility-first CSS | Bert veut l'apprendre, standard moderne |
| **shadcn/ui** | Composants UI | Copie-colle, customisable, accessibilité intégrée |
| **Radix UI** | Primitives UI | Base de shadcn/ui, accessibilité WCAG |
| **Lucide React** | Icons | Icons modernes, tree-shakeable |

#### Forms & Validation
| Technologie | Usage | Justification |
|-------------|-------|---------------|
| **react-hook-form** | Gestion formulaires | Performant, peu de re-renders |
| **zod** | Validation schemas | Type-safe, intégration TypeScript |

#### HTTP & API
| Technologie | Usage | Justification |
|-------------|-------|---------------|
| **axios** | Client HTTP | Interceptors, error handling facile |

#### Dev Tools & Quality
| Technologie | Usage | Justification |
|-------------|-------|---------------|
| **ESLint** | Linting | Qualité code (priorité Bert) |
| **Prettier** | Formatting | Cohérence code |
| **TypeScript** | Type checking | Type-safety |
| **TanStack Query Devtools** | Debug | Visualiser cache et queries |

#### Testing (Phase ultérieure)
| Technologie | Usage | Notes |
|-------------|-------|-------|
| **Vitest** | Test runner | Compatible Vite, à ajouter plus tard |
| **React Testing Library** | Tests composants | À ajouter plus tard |

---

## 🏗️ Architecture Finale Retenue

### Structure de Dossiers (Classique)

```
critical-resources-admin-react/
├── public/
│   └── favicon.ico
│
├── src/
│   ├── assets/
│   │   ├── images/
│   │   └── icons/
│   │
│   ├── components/
│   │   ├── ui/                    # shadcn/ui components
│   │   │   ├── button.tsx
│   │   │   ├── input.tsx
│   │   │   ├── table.tsx
│   │   │   ├── card.tsx
│   │   │   ├── dialog.tsx
│   │   │   ├── select.tsx
│   │   │   └── toast.tsx
│   │   │
│   │   ├── layout/                # Layout components
│   │   │   ├── Header.tsx
│   │   │   ├── Sidebar.tsx
│   │   │   ├── MainLayout.tsx
│   │   │   └── PageHeader.tsx
│   │   │
│   │   └── features/              # Business components
│   │       ├── ResourceCard.tsx
│   │       ├── StatusBadge.tsx
│   │       ├── CriteriaChecklist.tsx
│   │       └── WorkflowStepper.tsx
│   │
│   ├── pages/                     # Pages/Routes
│   │   ├── Dashboard.tsx
│   │   ├── Discovery.tsx
│   │   ├── GeographicValidation.tsx
│   │   ├── CriticalList.tsx
│   │   ├── DetailedValidation.tsx
│   │   └── RAGFormatting.tsx
│   │
│   ├── hooks/                     # Custom hooks
│   │   ├── useAuth.ts
│   │   ├── useResources.ts        # TanStack Query hooks
│   │   ├── useValidation.ts
│   │   └── useDebounce.ts
│   │
│   ├── services/                  # API Layer
│   │   ├── api.ts                 # Axios instance + interceptors
│   │   ├── resources.ts           # Resources endpoints
│   │   ├── validation.ts          # Validation endpoints
│   │   ├── discovery.ts           # Discovery endpoints
│   │   └── auth.ts                # Auth endpoints
│   │
│   ├── lib/                       # Utilities
│   │   ├── utils.ts               # Helper functions (cn, etc.)
│   │   ├── constants.ts           # App constants
│   │   ├── validators.ts          # Validation helpers
│   │   └── formatters.ts          # Data formatters
│   │
│   ├── types/                     # TypeScript types
│   │   ├── resource.ts
│   │   ├── api.ts
│   │   ├── workflow.ts
│   │   └── validation.ts
│   │
│   ├── store/                     # Zustand stores
│   │   ├── authStore.ts
│   │   └── uiStore.ts
│   │
│   ├── routes/                    # Routing config
│   │   └── index.tsx
│   │
│   ├── App.tsx                    # Root component
│   ├── main.tsx                   # Entry point
│   └── index.css                  # Global styles + Tailwind
│
├── .env.example
├── .env.local
├── .gitignore
├── .eslintrc.cjs
├── .prettierrc
├── package.json
├── tsconfig.json
├── tsconfig.node.json
├── vite.config.ts
├── tailwind.config.js
├── postcss.config.js
├── components.json              # shadcn/ui config
└── README.md
```

---

## 🎯 Principes de Développement Adoptés

### Qualité du Code (Priorité)
✅ **TypeScript strict mode** activé  
✅ **ESLint** avec règles strictes  
✅ **Prettier** pour formatting automatique  
✅ **Convention de nommage** cohérente (PascalCase composants, camelCase fonctions)  
✅ **Composants petits** et réutilisables  
✅ **Separation of Concerns** stricte (UI / Logic / Data)  

### Patterns React à Suivre
✅ **Custom hooks** pour logique métier  
✅ **Composition** over inheritance  
✅ **Props drilling évité** (Context/Zustand)  
✅ **Error boundaries** pour gestion erreurs  
✅ **Lazy loading** pour pages  
✅ **Memoization** quand nécessaire (pas systématique)  

### Architecture API
✅ **Service layer** dédié (pas de fetch direct dans composants)  
✅ **TanStack Query** pour cache et état async  
✅ **Axios interceptors** pour auth et errors  
✅ **Type-safe** API responses avec Zod  
✅ **Optimistic updates** pour meilleure UX  

---

## 📋 Plan d'Implémentation

### Phase 1 : Setup Projet (Jour 1)
- [ ] Initialiser projet Vite + React + TypeScript
- [ ] Installer dépendances (TanStack Query, Zustand, etc.)
- [ ] Setup Tailwind CSS + shadcn/ui
- [ ] Configurer ESLint + Prettier
- [ ] Créer structure dossiers
- [ ] Setup Axios + interceptors
- [ ] Créer types de base

### Phase 2 : Fondations (Jour 2)
- [ ] Créer AuthContext + store Zustand
- [ ] Implémenter Layout (Header, Sidebar)
- [ ] Setup React Router avec routes
- [ ] Créer composants UI de base (Button, Input, Card)
- [ ] Implémenter système de notifications (Toast)

### Phase 3 : Features (Jours 3-7)
- [ ] Page Dashboard (vue d'ensemble)
- [ ] Page Discovery (recherche ressources)
- [ ] Page Geographic Validation (batch validation)
- [ ] Page Critical List (liste rapide)
- [ ] Page Detailed Validation (édition détaillée)
- [ ] Page RAG Formatting

### Phase 4 : Polish (Jour 8)
- [ ] Gestion erreurs globale
- [ ] Loading states
- [ ] Responsive design
- [ ] Optimisations performance
- [ ] Documentation README

### Phase 5 : Tests (ultérieur)
- [ ] Setup Vitest + React Testing Library
- [ ] Tests composants critiques
- [ ] Tests hooks custom
- [ ] Tests d'intégration

---

## 🎓 Approche Pédagogique Confirmée

### Ce que je vais faire en tant que formateur

✅ **Expliquer chaque concept** avant implémentation  
✅ **Proposer plusieurs approches** avec trade-offs  
✅ **Poser questions** pour te faire réfléchir  
✅ **Valider tes choix** et signaler pièges  
✅ **Montrer bonnes pratiques** TypeScript/React  
✅ **Guider** vers qualité code maximale (ta priorité)  

### Ce que je ne ferai PAS

❌ Écrire code sans explication  
❌ Faire choix techniques sans ton input  
❌ Sauter étapes de compréhension  
❌ Donner solution directe sans réflexion  

---

## 🚀 Prochaine Étape Immédiate

**Action** : Créer le guide "JOUR_1_SETUP.md" avec :
- Commandes d'installation complètes
- Configuration fichiers (vite.config, tsconfig, etc.)
- Setup Tailwind + shadcn/ui
- Création structure dossiers
- Premier composant React avec TypeScript

**Es-tu prêt à démarrer le Jour 1 ?** 🎓

---

## 📝 Résumé Décisions

| Question | Décision | Raison |
|----------|----------|--------|
| TypeScript | ✅ OUI | Niveau intermédiaire, qualité code prioritaire |
| Tailwind CSS | ✅ OUI | Bert veut l'apprendre, standard moderne |
| shadcn/ui | ✅ OUI | Composants accessibles + customisables |
| TanStack Query | ✅ OUI | Perfect pour CRUD avec API REST |
| React Router v6 | ✅ OUI | Standard, bien documenté |
| Tests | ⏸️ PLUS TARD | Focus formation React d'abord |
| ESLint/Prettier | ✅ OUI | Qualité code prioritaire |
| Zustand | ✅ OUI | État UI global simple |

**Date validation** : 2026-02-10  
**Validé par** : Bert (apprenant) + GitHub Copilot (formateur)
