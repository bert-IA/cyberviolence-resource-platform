# 🚀 Jour 1 : Setup Projet React - Guide Complet

**Date** : 2026-02-10  
**Objectif** : Initialiser le projet React avec toute la stack validée  
**Durée estimée** : 2-3 heures  

---

## ✅ Prérequis

### Vérifications avant de démarrer

Ouvre un terminal et vérifie les versions :

```bash
# Node.js (doit être >= 20.x)
node --version

# npm (doit être >= 10.x)
npm --version

# git (pour versioning)
git --version
```

**Si Node < 20.x** : Installe la dernière version LTS depuis [nodejs.org](https://nodejs.org)

---

## 📦 Étape 1 : Créer le Projet Vite

### 1.1 Initialisation

```bash
# Va dans le dossier parent (pas dans critical_resources_admin)
cd ~/ProjetAI/old-stopcyberviolences-chatbot

# Crée le projet React avec Vite
npm create vite@latest critical-resources-admin-react -- --template react-ts

# Entre dans le dossier
cd critical-resources-admin-react
```

**🎓 Explication** :
- `vite@latest` : Utilise la dernière version de Vite
- `--template react-ts` : Template React avec TypeScript préconfiguré
- Vite crée le projet avec structure de base et configs

### 1.2 Vérification structure créée

```bash
# Liste les fichiers créés
ls -la
```

Tu devrais voir :
```
.
├── node_modules/         (pas encore, après npm install)
├── public/
├── src/
├── .gitignore
├── index.html
├── package.json
├── tsconfig.json
├── tsconfig.node.json
└── vite.config.ts
```

### 1.3 Installation dépendances de base

```bash
npm install
```

**🎓 Explication** : Installe React, React-DOM, Vite et toutes les dépendances de base définies dans package.json

### 1.4 Test rapide

```bash
npm run dev
```

**Résultat attendu** :
```
VITE v5.x.x  ready in xxx ms

➜  Local:   http://localhost:5173/
➜  Network: use --host to expose
```

Ouvre http://localhost:5173/ dans ton navigateur → Tu devrais voir la page Vite + React.

**🎓 Concept** : Vite lance un dev server avec HMR (Hot Module Replacement) ultra-rapide.

**Arrête le serveur** : `Ctrl+C` dans le terminal

---

## 🎨 Étape 2 : Installer Tailwind CSS

### 2.1 Installation des packages

```bash
npm install -D tailwindcss postcss autoprefixer
```

**🎓 Explication** :
- `tailwindcss` : Framework CSS utility-first
- `postcss` : Outil de transformation CSS (requis par Tailwind)
- `autoprefixer` : Ajoute préfixes CSS automatiquement (-webkit-, etc.)
- `-D` : Dépendances de développement uniquement

### 2.2 Initialisation Tailwind

```bash
npx tailwindcss init -p
```

**🎓 Explication** :
- Crée `tailwind.config.js` (configuration Tailwind)
- Crée `postcss.config.js` (configuration PostCSS)
- `-p` : Inclut PostCSS automatiquement

### 2.3 Configuration Tailwind

Ouvre `tailwind.config.js` et remplace le contenu :

```javascript
/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}
```

**🎓 Explication** :
- `content` : Chemins où Tailwind cherche les classes CSS utilisées
- Tree-shaking : Seules les classes utilisées sont incluses dans le build final

### 2.4 Import Tailwind dans CSS

Ouvre `src/index.css` et **remplace tout** par :

```css
@tailwind base;
@tailwind components;
@tailwind utilities;
```

**🎓 Explication** :
- `@tailwind base` : Reset CSS + styles de base
- `@tailwind components` : Classes composants (boutons, forms, etc.)
- `@tailwind utilities` : Classes utilitaires (flex, grid, colors, etc.)

### 2.5 Test Tailwind

Ouvre `src/App.tsx` et remplace par :

```tsx
function App() {
  return (
    <div className="min-h-screen bg-slate-100 flex items-center justify-center">
      <div className="bg-white p-8 rounded-lg shadow-lg">
        <h1 className="text-3xl font-bold text-blue-600">
          Tailwind fonctionne ! 🎉
        </h1>
        <p className="mt-4 text-gray-600">
          Critical Resources Admin - React Edition
        </p>
      </div>
    </div>
  )
}

export default App
```

Relance le serveur :
```bash
npm run dev
```

**Résultat attendu** : Une belle card centrée avec le titre bleu.

**🎓 Question formateur** : Comprends-tu comment les classes Tailwind fonctionnent ?
- `bg-slate-100` : Fond gris clair
- `flex items-center justify-center` : Flexbox centré
- `p-8` : Padding 2rem (8 × 0.25rem)

---

## 🧩 Étape 3 : Installer shadcn/ui

### 3.1 Installation CLI shadcn/ui

```bash
npx shadcn@latest init
```

**Questions interactives** (réponds) :
```
✔ Would you like to use TypeScript? … yes
✔ Which style would you like to use? › New York
✔ Which color would you like to use as base color? › Slate
✔ Where is your global CSS file? › src/index.css
✔ Would you like to use CSS variables for colors? … yes
✔ Are you using a custom tailwind prefix eg. tw-? … no
✔ Where is your tailwind.config.js located? › tailwind.config.js
✔ Configure the import alias for components: › @/components
✔ Configure the import alias for utils: › @/lib/utils
✔ Are you using React Server Components? … no
```

**🎓 Explication** :
- **Style New York** : Plus moderne et épuré que "Default"
- **Slate** : Couleur neutre (gris) pour admin
- **CSS variables** : Permet de changer le thème facilement
- **Import alias `@/`** : Import propre (`@/components/ui/button` au lieu de `../../components/ui/button`)

### 3.2 Configuration des alias TypeScript

Ouvre `tsconfig.json` et vérifie que `compilerOptions` contient :

```json
{
  "compilerOptions": {
    // ... autres options existantes
    "baseUrl": ".",
    "paths": {
      "@/*": ["./src/*"]
    }
  }
}
```

**Si absent**, ajoute ces lignes dans `compilerOptions`.

### 3.3 Configuration Vite pour les alias

Ouvre `vite.config.ts` et remplace par :

```typescript
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
})
```

**🎓 Explication** : Configure Vite pour résoudre `@/` vers `./src/`

### 3.4 Installation des composants de base

```bash
# Installe les composants shadcn/ui dont on aura besoin
npx shadcn@latest add button
npx shadcn@latest add input
npx shadcn@latest add card
npx shadcn@latest add table
npx shadcn@latest add dialog
npx shadcn@latest add select
npx shadcn@latest add toast
npx shadcn@latest add badge
```

**🎓 Concept important** : 
- shadcn/ui **copie les composants dans ton projet** (pas dans node_modules)
- Tu possèdes le code → tu peux le modifier librement
- Les composants apparaissent dans `src/components/ui/`

### 3.5 Test d'un composant shadcn/ui

Remplace `src/App.tsx` par :

```tsx
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'

function App() {
  return (
    <div className="min-h-screen bg-slate-100 p-8">
      <Card className="max-w-md mx-auto">
        <CardHeader>
          <CardTitle>shadcn/ui fonctionne ! 🎨</CardTitle>
          <CardDescription>
            Composants accessibles et customisables
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <Button>Bouton Primary</Button>
          <Button variant="secondary">Bouton Secondary</Button>
          <Button variant="outline">Bouton Outline</Button>
        </CardContent>
      </Card>
    </div>
  )
}

export default App
```

**Résultat** : Card avec 3 boutons stylés différemment.

**🎓 Question** : Vois-tu comment les composants sont importés avec `@/` ?

---

## 📚 Étape 4 : Installer React Router

### 4.1 Installation

```bash
npm install react-router-dom
```

### 4.2 Test basique du routing

Crée `src/pages/Dashboard.tsx` :

```tsx
export default function Dashboard() {
  return (
    <div className="p-8">
      <h1 className="text-3xl font-bold">Dashboard</h1>
      <p className="mt-4">Page principale de l'admin</p>
    </div>
  )
}
```

Crée `src/pages/Discovery.tsx` :

```tsx
export default function Discovery() {
  return (
    <div className="p-8">
      <h1 className="text-3xl font-bold">Discovery</h1>
      <p className="mt-4">Recherche de nouvelles ressources</p>
    </div>
  )
}
```

Remplace `src/App.tsx` :

```tsx
import { BrowserRouter, Routes, Route, Link } from 'react-router-dom'
import Dashboard from './pages/Dashboard'
import Discovery from './pages/Discovery'

function App() {
  return (
    <BrowserRouter>
      <div className="min-h-screen bg-slate-100">
        {/* Navigation simple */}
        <nav className="bg-white shadow-sm p-4 space-x-4">
          <Link to="/" className="text-blue-600 hover:underline">Dashboard</Link>
          <Link to="/discovery" className="text-blue-600 hover:underline">Discovery</Link>
        </nav>

        {/* Routes */}
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/discovery" element={<Discovery />} />
        </Routes>
      </div>
    </BrowserRouter>
  )
}

export default App
```

**Test** : Clique sur les liens → Les pages changent sans rechargement !

**🎓 Concepts React Router** :
- `<BrowserRouter>` : Wrapper pour activer le routing
- `<Routes>` : Container des routes
- `<Route path="/x" element={<Component />}>` : Définit une route
- `<Link to="/x">` : Navigation sans rechargement page

---

## 🔌 Étape 5 : Installer State Management & Data Fetching

### 5.1 Installation TanStack Query

```bash
npm install @tanstack/react-query
npm install -D @tanstack/react-query-devtools
```

**🎓 Explication** :
- `@tanstack/react-query` : Gestion data fetching et cache
- `react-query-devtools` : Outil debug (dev only)

### 5.2 Installation Zustand

```bash
npm install zustand
```

**🎓 Explication** : State management global simple

### 5.3 Installation Axios

```bash
npm install axios
```

---

## 🛠️ Étape 6 : Installer Outils Qualité Code

### 6.1 Installation ESLint (déjà inclus par Vite)

Vite inclut ESLint de base. Vérifie `.eslintrc.cjs` existe.

### 6.2 Installation Prettier

```bash
npm install -D prettier eslint-config-prettier eslint-plugin-prettier
```

Crée `.prettierrc` à la racine :

```json
{
  "semi": false,
  "singleQuote": true,
  "tabWidth": 2,
  "trailingComma": "es5",
  "printWidth": 100
}
```

Crée `.prettierignore` :

```
node_modules
dist
build
.git
```

### 6.3 Configuration ESLint + Prettier

Ouvre `.eslintrc.cjs` et ajoute prettier dans `extends` :

```javascript
module.exports = {
  root: true,
  env: { browser: true, es2020: true },
  extends: [
    'eslint:recommended',
    'plugin:@typescript-eslint/recommended',
    'plugin:react-hooks/recommended',
    'prettier' // Ajoute cette ligne
  ],
  // ... reste de la config
}
```

### 6.4 Scripts npm

Ouvre `package.json` et ajoute dans `"scripts"` :

```json
{
  "scripts": {
    "dev": "vite",
    "build": "tsc && vite build",
    "lint": "eslint . --ext ts,tsx --report-unused-disable-directives --max-warnings 0",
    "preview": "vite preview",
    "format": "prettier --write \"src/**/*.{ts,tsx,json,css,md}\"",
    "format:check": "prettier --check \"src/**/*.{ts,tsx,json,css,md}\""
  }
}
```

**Test** :
```bash
npm run format
```

**Résultat** : Tous les fichiers sont formatés automatiquement.

---

## 📁 Étape 7 : Créer la Structure de Dossiers

### 7.1 Supprime les fichiers exemple

```bash
# Supprime les fichiers Vite par défaut
rm src/App.css
rm src/assets/react.svg
rm public/vite.svg
```

### 7.2 Crée la structure complète

```bash
# Depuis la racine du projet
cd src

# Crée tous les dossiers
mkdir -p assets/images assets/icons
mkdir -p components/layout components/features
mkdir -p pages
mkdir -p hooks
mkdir -p services
mkdir -p lib
mkdir -p types
mkdir -p store
mkdir -p routes
```

**Vérification** :
```bash
tree src -d -L 2
```

Tu devrais voir :
```
src/
├── assets/
│   ├── images/
│   └── icons/
├── components/
│   ├── ui/         (déjà créé par shadcn)
│   ├── layout/
│   └── features/
├── hooks/
├── lib/            (déjà créé par shadcn)
├── pages/
├── routes/
├── services/
├── store/
└── types/
```

---

## 📝 Étape 8 : Créer les Fichiers Fondamentaux

### 8.1 Configuration API (Axios)

Crée `src/services/api.ts` :

```typescript
import axios from 'axios'

// URL de ton backend FastAPI
const API_BASE_URL = 'http://localhost:8001'

// Instance Axios configurée
export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Interceptor pour ajouter le token d'auth
api.interceptors.request.use(
  (config) => {
    // TODO: Récupérer le token depuis le store auth
    const token = 'admin-token-2024' // Temporaire
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Interceptor pour gérer les erreurs globalement
api.interceptors.response.use(
  (response) => response,
  (error) => {
    // Gestion erreurs globale
    console.error('API Error:', error.response?.data || error.message)
    return Promise.reject(error)
  }
)
```

**🎓 Concepts** :
- **Axios instance** : Configuration réutilisable
- **Interceptors request** : Modifie chaque requête (ajoute token)
- **Interceptors response** : Gère les erreurs globalement

### 8.2 Types de base

Crée `src/types/resource.ts` :

```typescript
export type WorkflowStatus =
  | 'discovered'
  | 'geo_pending'
  | 'geo_validated'
  | 'critical_pending'
  | 'critical_validated'
  | 'rag_ready'

export interface Resource {
  resource_id: string
  organization_name: string
  name: string
  website?: string
  phone?: string
  email?: string
  description?: string
  country_code: string
  language: string
  workflow_status: WorkflowStatus
  validation_history: ValidationHistoryEntry[]
  created_at: string
  updated_at: string
}

export interface ValidationHistoryEntry {
  status: WorkflowStatus
  timestamp: string
  validator?: string
  notes?: string
}
```

**🎓 TypeScript** : 
- `type` pour union types (`'discovered' | 'geo_pending'`)
- `interface` pour objets complexes
- `?` = propriété optionnelle

### 8.3 Constants

Crée `src/lib/constants.ts` :

```typescript
export const WORKFLOW_STATUS_LABELS = {
  discovered: 'Découverte',
  geo_pending: 'Validation Géo en Attente',
  geo_validated: 'Validée Géographiquement',
  critical_pending: 'Validation Critique en Attente',
  critical_validated: 'Validée Critiquement',
  rag_ready: 'Prête pour RAG',
} as const

export const API_ENDPOINTS = {
  resources: '/sources',
  validate: '/sources/validate',
  discover: '/discover-by-category',
} as const
```

**🎓 TypeScript** : `as const` rend l'objet readonly → meilleure inférence de types

### 8.4 Store Auth (Zustand)

Crée `src/store/authStore.ts` :

```typescript
import { create } from 'zustand'

interface AuthState {
  token: string | null
  isAuthenticated: boolean
  login: (token: string) => void
  logout: () => void
}

export const useAuthStore = create<AuthState>((set) => ({
  token: 'admin-token-2024', // Temporaire
  isAuthenticated: true,
  login: (token) => set({ token, isAuthenticated: true }),
  logout: () => set({ token: null, isAuthenticated: false }),
}))
```

**🎓 Zustand** :
- `create<Interface>()` : Définit le store
- `set()` : Modifie l'état
- Hook `useAuthStore()` directement dans composants

### 8.5 Setup TanStack Query

Remplace `src/main.tsx` :

```tsx
import React from 'react'
import ReactDOM from 'react-dom/client'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { ReactQueryDevtools } from '@tanstack/react-query-devtools'
import App from './App.tsx'
import './index.css'

// Configuration TanStack Query
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false, // Pas de refetch au focus
      retry: 1, // 1 seul retry en cas d'erreur
      staleTime: 5 * 60 * 1000, // Données fresh pendant 5 min
    },
  },
})

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <QueryClientProvider client={queryClient}>
      <App />
      <ReactQueryDevtools initialIsOpen={false} />
    </QueryClientProvider>
  </React.StrictMode>
)
```

**🎓 TanStack Query** :
- `QueryClient` : Configuration cache global
- `staleTime` : Durée avant que données soient "stale"
- `ReactQueryDevtools` : Outil debug (bouton en bas à gauche)

---

## 🎨 Étape 9 : Créer le Layout de Base

### 9.1 Composant Header

Crée `src/components/layout/Header.tsx` :

```tsx
import { Button } from '@/components/ui/button'
import { useAuthStore } from '@/store/authStore'

export default function Header() {
  const logout = useAuthStore((state) => state.logout)

  return (
    <header className="bg-white border-b border-gray-200 px-6 py-4">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">
            Critical Resources Admin
          </h1>
          <p className="text-sm text-gray-500">
            Gestion des ressources anti-cyberharcèlement
          </p>
        </div>
        <Button variant="outline" onClick={logout}>
          Déconnexion
        </Button>
      </div>
    </header>
  )
}
```

### 9.2 Composant Sidebar

Crée `src/components/layout/Sidebar.tsx` :

```tsx
import { Link, useLocation } from 'react-router-dom'
import { cn } from '@/lib/utils'

const navigation = [
  { name: 'Dashboard', href: '/' },
  { name: 'Discovery', href: '/discovery' },
  { name: 'Validation Géographique', href: '/geo-validation' },
  { name: 'Validation Critique', href: '/critical-validation' },
  { name: 'Formatage RAG', href: '/rag-formatting' },
]

export default function Sidebar() {
  const location = useLocation()

  return (
    <aside className="w-64 bg-white border-r border-gray-200 min-h-screen p-4">
      <nav className="space-y-2">
        {navigation.map((item) => {
          const isActive = location.pathname === item.href
          return (
            <Link
              key={item.name}
              to={item.href}
              className={cn(
                'block px-4 py-2 rounded-md text-sm font-medium transition-colors',
                isActive
                  ? 'bg-blue-600 text-white'
                  : 'text-gray-700 hover:bg-gray-100'
              )}
            >
              {item.name}
            </Link>
          )
        })}
      </nav>
    </aside>
  )
}
```

**🎓 Concepts** :
- `useLocation()` : Hook pour connaître la route actuelle
- `cn()` : Fonction shadcn pour merger les classes Tailwind conditionnellement

### 9.3 Composant MainLayout

Crée `src/components/layout/MainLayout.tsx` :

```tsx
import { ReactNode } from 'react'
import Header from './Header'
import Sidebar from './Sidebar'

interface MainLayoutProps {
  children: ReactNode
}

export default function MainLayout({ children }: MainLayoutProps) {
  return (
    <div className="min-h-screen bg-slate-50">
      <Header />
      <div className="flex">
        <Sidebar />
        <main className="flex-1 p-8">{children}</main>
      </div>
    </div>
  )
}
```

**🎓 TypeScript** :
- `ReactNode` : Type pour children (peut être n'importe quel élément React)
- `interface Props` : Typage des props du composant

### 9.4 Intégration dans App

Remplace `src/App.tsx` :

```tsx
import { BrowserRouter, Routes, Route } from 'react-router-dom'
import MainLayout from './components/layout/MainLayout'
import Dashboard from './pages/Dashboard'
import Discovery from './pages/Discovery'

function App() {
  return (
    <BrowserRouter>
      <MainLayout>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/discovery" element={<Discovery />} />
          {/* TODO: Ajouter les autres routes */}
        </Routes>
      </MainLayout>
    </BrowserRouter>
  )
}

export default App
```

---

## ✅ Étape 10 : Vérification Finale

### 10.1 Test du build

```bash
npm run build
```

**Résultat attendu** : `dist/` folder créé sans erreurs TypeScript.

### 10.2 Test du linting

```bash
npm run lint
```

**Résultat attendu** : Aucune erreur.

### 10.3 Test du formatage

```bash
npm run format
```

**Résultat attendu** : Tous les fichiers formatés.

### 10.4 Test du serveur dev

```bash
npm run dev
```

Ouvre http://localhost:5173/ :
- ✅ Header visible avec titre et bouton déconnexion
- ✅ Sidebar avec 5 liens
- ✅ Dashboard et Discovery cliquables
- ✅ React Query Devtools en bas à gauche

---

## 📋 Checklist Jour 1 Complète

- [ ] Node.js >= 20.x installé
- [ ] Projet Vite + React + TypeScript créé
- [ ] Tailwind CSS configuré et testé
- [ ] shadcn/ui installé avec 8 composants
- [ ] React Router v6 installé et testé
- [ ] TanStack Query configuré avec devtools
- [ ] Zustand installé (store auth créé)
- [ ] Axios configuré avec interceptors
- [ ] ESLint + Prettier configurés
- [ ] Structure de dossiers créée
- [ ] Types de base définis (`resource.ts`)
- [ ] Constants créées (`constants.ts`)
- [ ] Layout complet (Header + Sidebar + MainLayout)
- [ ] 2 pages créées (Dashboard, Discovery)
- [ ] Build production fonctionne
- [ ] Dev server fonctionne

---

## 🎯 Prochaine Étape : Jour 2

**Objectif** : Créer ton premier hook TanStack Query pour fetcher les ressources depuis l'API FastAPI.

**On abordera** :
1. Comment créer un service API pour les ressources
2. Comment créer un custom hook `useResources()`
3. Comment afficher les données dans un tableau shadcn/ui
4. Comment gérer loading states et erreurs
5. **Concepts pédagogiques** : Différence entre state local et data fetching

**Es-tu prêt à passer au Jour 2 après avoir terminé le Jour 1 ?** 🚀

---

**🎓 Question formateur finale du Jour 1** :
- Comprends-tu la différence entre Zustand (state UI) et TanStack Query (data API) ?
- Es-tu à l'aise avec les imports `@/` ?
- Vois-tu comment le routing fonctionne avec React Router ?

Note tes questions pour qu'on en discute avant de démarrer Jour 2 ! 📝
