# 🚀 Guide de Développement React - Resource Discovery Platform

**Projet** : Resource Discovery Platform  
**Stack** : React 18 + TypeScript + TanStack Query + Tailwind CSS  
**Backend** : FastAPI (localhost:8000)  
**Objectif** : Interface d'administration pour découvrir et gérer des ressources critiques

---

## 📋 Table des Matières

1. [Architecture & Structure du Projet](#architecture)
2. [Outils React Utilisés](#outils-react)
3. [Configuration Initiale](#configuration)
4. [Service API - Communication Backend](#service-api)
5. [Hooks Personnalisés - TanStack Query](#hooks)
6. [Composants UI Réutilisables](#composants-ui)
7. [Composants Features - Logique Métier](#composants-features)
8. [Pages - Assemblage Final](#pages)
9. [Workflow Complet des Données](#workflow)

---

## 📁 Architecture & Structure du Projet {#architecture}

### Structure des Dossiers

```
src/
├── main.tsx                    # Point d'entrée (QueryClientProvider)
├── App.tsx                     # Composant racine
│
├── services/
│   └── api.ts                  # Toutes les fonctions d'appels API
│
├── hooks/
│   ├── useDiscoverResources.ts # Hook pour découverte
│   ├── useResources.ts         # Hook pour liste ressources
│   ├── useCountriesConfig.ts   # Hook pour configuration pays
│   └── useValidateResource.ts  # Hook pour validation
│
├── components/
│   ├── ui/                     # Composants génériques réutilisables
│   │   ├── Button.tsx
│   │   ├── LoadingSpinner.tsx
│   │   ├── ErrorMessage.tsx
│   │   └── Header.tsx
│   │
│   ├── features/               # Composants métier spécifiques
│   │   ├── DiscoveryForm.tsx
│   │   ├── DiscoveredResourceCard.tsx
│   │   ├── DiscoveredResourcesList.tsx
│   │   └── LanguageCard.tsx
│   │
│   └── layout/
│       └── MainApp.tsx         # Layout principal avec navigation
│
└── pages/
    ├── ConfigurationPage.tsx   # Page configuration pays/langues
    └── DiscoveryPage.tsx       # Page découverte ressources
```

### Principe d'Organisation

🎯 **Séparation par responsabilité** :
- **services/** : Communication pure avec le backend (fetch API)
- **hooks/** : Logique React Query (cache, loading, error)
- **components/ui/** : Composants visuels génériques (Button, Spinner)
- **components/features/** : Composants métier (DiscoveryForm, ResourceCard)
- **pages/** : Assemblage des composants en pages complètes

---

## 🧰 Outils React Utilisés {#outils-react}

### 1. **React 18 - Hooks Fondamentaux**

#### useState - Gérer l'état local

```tsx
const [count, setCount] = useState(0)  // État simple
const [user, setUser] = useState<User | null>(null)  // État complexe avec TypeScript
```

**Quand l'utiliser** :
- ✅ État local à un composant (ex: formulaire ouvert/fermé)
- ✅ État UI simple (compteur, toggle)
- ❌ Données API (utilisez TanStack Query à la place)

---

#### useEffect - Effets de bord

```tsx
useEffect(() => {
  // Code exécuté après le render
  console.log('Composant monté ou count a changé')
  
  // Cleanup (nettoyage)
  return () => {
    console.log('Composant démonté ou avant prochain effet')
  }
}, [count])  // Dépendances : re-exécute si count change
```

**Quand l'utiliser** :
- ✅ Appels API manuels (mais préférez TanStack Query)
- ✅ Subscriptions (WebSocket, événements)
- ✅ Effets synchronisés avec des props/state

---

### 2. **TanStack Query (React Query v5) - Gestion des Données API**

**Pourquoi TanStack Query ?**
- ✅ **Cache intelligent** : Pas de requêtes dupliquées
- ✅ **Loading/Error automatiques** : `isLoading`, `error` gérés
- ✅ **Synchronisation** : Invalidation de cache automatique
- ✅ **Retry & Refetch** : Gestion d'erreurs intégrée

#### useQuery - Lire des données (GET)

```tsx
const { data, isLoading, error } = useQuery({
  queryKey: ['resources', 'discovered'],  // Clé unique pour le cache
  queryFn: () => fetchResources('discovered')  // Fonction async qui retourne les données
})
```

**Flow complet** :
1. Premier appel → `isLoading: true` → Fetch API
2. Données reçues → `data` rempli → Mise en cache
3. Re-montage du composant → Données **instantanées** depuis le cache
4. Après `staleTime` (5 min) → Refetch en arrière-plan

#### useMutation - Modifier des données (POST/PATCH/DELETE)

```tsx
const mutation = useMutation({
  mutationFn: (filters) => discoverResources(filters),
  onSuccess: () => {
    // Invalider le cache pour refetch
    queryClient.invalidateQueries({ queryKey: ['resources'] })
  }
})

// Déclencher la mutation
mutation.mutate(filters)

// États disponibles
mutation.isPending  // En cours ?
mutation.data       // Résultat
mutation.error      // Erreur si échec
```

**Flow complet** :
1. User clique "Rechercher" → `mutation.mutate(filters)`
2. `isPending: true` → Bouton disabled
3. Appel API POST `/geographic/discover`
4. **Succès** → `onSuccess()` exécuté → Cache invalidé
5. Toutes les queries `['resources', ...]` se refetch automatiquement

---

### 3. **TypeScript - Sécurité des Types**

#### Interfaces pour les données

```tsx
interface Resource {
  id: string
  name: string
  description: string
  country: string
  contact_phone: string
  // ...
}

interface DiscoveryFilters {
  language: string
  categories: string[]
  countries: string[]
  max_per_category: number
}
```

**Avantages** :
- ✅ Autocompletion dans VSCode
- ✅ Erreurs détectées avant exécution
- ✅ Documentation intégrée (les types = la doc)

#### Props typées pour composants

```tsx
interface ButtonProps {
  label: string
  onClick: () => void
  variant?: 'primary' | 'secondary'  // Optional avec union type
  disabled?: boolean
}

function Button({ label, onClick, variant = 'primary', disabled }: ButtonProps) {
  // ...
}
```

---

### 4. **Tailwind CSS - Styling Utility-First**

```tsx
<div className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow">
  <h2 className="text-xl font-bold text-gray-900 mb-2">
    Titre
  </h2>
</div>
```

**Classes courantes** :
- **Layout** : `flex`, `grid`, `p-4` (padding), `m-2` (margin)
- **Colors** : `bg-blue-500`, `text-gray-900`
- **Responsive** : `lg:grid-cols-3` (3 colonnes sur grand écran)
- **States** : `hover:bg-gray-100`, `disabled:opacity-50`

---

## ⚙️ Configuration Initiale {#configuration}

### Fichier : `src/main.tsx`

**Rôle** : Point d'entrée de l'application React. Configure TanStack Query globalement.

```tsx
import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.tsx'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { ReactQueryDevtools } from '@tanstack/react-query-devtools'

// 1️⃣ Configuration du QueryClient (paramètres globaux)
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 1000 * 60 * 5,        // 5 min : données "fraîches" pendant 5 min
      gcTime: 1000 * 60 * 10,          // 10 min : garde en cache 10 min après inutilisé
      refetchOnWindowFocus: false,     // Ne pas refetch au retour sur l'onglet
      retry: 1,                        // Réessayer 1 fois si échec
    },
  },
})

// 2️⃣ Render de l'application avec les Providers
createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <QueryClientProvider client={queryClient}>
      <App />
      <ReactQueryDevtools initialIsOpen={false} />
    </QueryClientProvider>
  </StrictMode>,
)
```

**📖 Explications** :

**StrictMode** : Mode de développement qui détecte les erreurs potentielles  
**QueryClientProvider** : Rend React Query disponible dans toute l'app  
**ReactQueryDevtools** : Panneau de debug (coin bas-droite) pour voir le cache

**Options de configuration** :
- `staleTime` : Temps pendant lequel les données sont considérées "fraîches" (pas de refetch)
- `gcTime` : Temps de garde en cache après que personne n'utilise les données
- `retry` : Nombre de tentatives si l'API échoue

---

### Fichier : `src/components/layout/MainApp.tsx`

**Rôle** : Layout principal avec navigation par onglets (Configuration | Découverte).

```tsx
import { useState } from 'react'
import { ConfigurationPage } from '../../pages/ConfigurationPage'
import { DiscoveryPage } from '../../pages/DiscoveryPage'
import { Header, type NavigationItem } from '../ui/Header'

type MainAppPageType = 'configuration' | 'discovery'

export function MainApp() {
  // 🎯 État local : quelle page est active
  const [currentPage, setCurrentPage] = useState<MainAppPageType>('discovery')

  // 📋 Items de navigation pour le Header
  const navigationItems: NavigationItem<MainAppPageType>[] = [
    { label: 'Configuration Pays', value: 'configuration' },
    { label: 'Découverte Ressource', value: 'discovery' }
  ]

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header avec navigation */}
      <Header
        title="INTERFACE DE DÉCOUVERTE DES RESSOURCES"
        userName='Admin'
        navigationItems={navigationItems}
        currentPage={currentPage}
        onNavigate={setCurrentPage}  // Callback pour changer de page
      />

      {/* Affichage conditionnel de la page active */}
      <main>
        {currentPage === 'configuration' && <ConfigurationPage />}
        {currentPage === 'discovery' && <DiscoveryPage />}
      </main>
    </div>
  )
}
```

**📖 Explications** :

**Pattern "State-driven UI"** : L'UI est déterminée par le state `currentPage`  
**Conditional Rendering** : `{condition && <Component />}` affiche le composant si vrai  
**Callback Props** : `onNavigate={setCurrentPage}` passe la fonction de mise à jour au Header

**Flow de navigation** :
1. User clique "Découverte" dans Header
2. Header appelle `onNavigate('discovery')`
3. `setCurrentPage('discovery')` change le state
4. React re-rend → `<DiscoveryPage />` s'affiche

---

## 🌐 Service API - Communication Backend {#service-api}

### Fichier : `src/services/api.ts`

**Rôle** : Centralise TOUS les appels API vers le backend FastAPI. Aucun fetch dans les composants !

#### Configuration de Base

```typescript
export const API_BASE_URL = 'http://localhost:8000'
export const AUTH_TOKEN = 'Bearer admin-token-2024'
```

#### Interfaces TypeScript

```typescript
// Ressource découverte (retournée par /geographic/discover)
export interface DiscoveredResource {
  id: string
  name: string
  country: string
  phone: string
  email: string
  confidence: number      // Score de confiance (0-1)
  category: string        // Type de ressource
  description: string
  is_new: boolean         // Nouvelle ressource ou existante ?
  duplicate_reason?: string  // Si doublon, pourquoi
}

// Filtres pour la découverte
export interface DiscoveryFilters {
  language: string
  categories: string[]
  countries: string[]
  max_per_category: number
}

// Réponse de la découverte
export interface DiscoveryResponse {
  success: boolean
  message: string
  total_discovered: number
  newly_discovered: DiscoveredResource[]
  estimated_duration?: string
}
```

#### Fonction : `discoverResources()` - POST /geographic/discover

```typescript
export async function discoverResources(
  filters: DiscoveryFilters
): Promise<DiscoveryResponse> {
  
  // 1️⃣ Appel HTTP POST
  const response = await fetch(`${API_BASE_URL}/geographic/discover`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': AUTH_TOKEN
    },
    body: JSON.stringify(filters)
  })

  // 2️⃣ Vérification erreur HTTP
  if (!response.ok) {
    throw new Error(`Erreur API: ${response.status}`)
  }

  // 3️⃣ Parsing JSON
  const backendResponse = await response.json()

  // 4️⃣ Transformation de la structure backend → frontend
  return {
    success: backendResponse.success,
    message: backendResponse.message,
    total_discovered: backendResponse.data.discovered_count,
    newly_discovered: backendResponse.data.resources,
    estimated_duration: backendResponse.data.estimated_duration
  }
}
```

**📖 Explications** :

**Pourquoi throw Error ?** : TanStack Query détecte les erreurs et remplit automatiquement `error`  
**Transformation de données** : Le backend retourne une structure, on l'adapte pour le frontend  
**Type de retour** : `Promise<DiscoveryResponse>` permet à TanStack Query de typer automatiquement `data`

**Flow complet** :
```
User submit formulaire
    ↓
Hook appelle discoverResources(filters)
    ↓
fetch() → POST /geographic/discover
    ↓
Backend traite (LLM, recherche, etc.)
    ↓
Backend retourne JSON
    ↓
Transformation et return
    ↓
TanStack Query met en cache
    ↓
Composant affiche les résultats
```

---

#### Autres Fonctions API

```typescript
// GET /sources (avec filtre optionnel)
export async function fetchResources(status?: string): Promise<Resource[]> {
  const url = status
    ? `${API_BASE_URL}/sources?status=${status}`
    : `${API_BASE_URL}/sources`

  const response = await fetch(url, {
    headers: { 'Authorization': AUTH_TOKEN }
  })

  if (!response.ok) {
    throw new Error(`Erreur API: ${response.status}`)
  }

  const data = await response.json()
  return data.sources || []
}

// GET /sources/:id
export async function fetchResourceById(id: string): Promise<Resource> {
  const response = await fetch(`${API_BASE_URL}/sources/${id}`, {
    headers: { 'Authorization': AUTH_TOKEN }
  })

  if (!response.ok) {
    throw new Error(`Erreur API: ${response.status}`)
  }

  const data = await response.json()
  return data.resource
}

// POST /sources/validate
export async function validateCriticalSource(
  request: ValidateSourceRequest
): Promise<{ success: boolean; message: string }> {
  const response = await fetch(`${API_BASE_URL}/sources/validate`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': AUTH_TOKEN
    },
    body: JSON.stringify(request)
  })

  if (!response.ok) {
    throw new Error(`Erreur validation: ${response.status}`)
  }

  return response.json()
}
```

**Pattern commun** :
1. Construire l'URL (avec ou sans paramètres)
2. fetch() avec headers appropriés
3. Vérifier `response.ok`
4. Parser JSON et retourner

---

## 🎣 Hooks Personnalisés - TanStack Query {#hooks}

**Rôle** : Encapsuler la logique React Query pour réutilisation. Un hook = une opération API.

### Hook : `useDiscoverResources` - Mutation pour découvrir

**Fichier** : `src/hooks/useDiscoverResources.ts`

```typescript
import { useMutation } from '@tanstack/react-query'
import { discoverResources } from '../services/api'
import type { DiscoveryFilters } from '../services/api'

export function useDiscoverResources() {
  return useMutation({
    mutationFn: (filters: DiscoveryFilters) => discoverResources(filters),
  })
}
```

**📖 Explications** :

**useMutation** : Pour les opérations qui **modifient** des données (POST/PATCH/DELETE)  
**mutationFn** : La fonction à appeler (prend `filters` en paramètre)  
**Return** : Objet avec `mutate()`, `isPending`, `data`, `error`, etc.

**Utilisation dans un composant** :
```tsx
const discovery = useDiscoverResources()

// Lancer la découverte
discovery.mutate(filters)

// États disponibles
discovery.isPending   // true pendant l'appel API
discovery.data        // Résultat (DiscoveryResponse)
discovery.error       // Error si échec
discovery.variables   // Paramètres passés à mutate()
```

---

### Hook : `useResources` - Query pour lister ressources

**Fichier** : `src/hooks/useResources.ts`

```typescript
import { useQuery } from '@tanstack/react-query'
import { fetchResources } from '../services/api'

export function useResources(status?: string) {
  return useQuery({
    queryKey: ['resources', status],  // Cache séparé par status
    queryFn: () => fetchResources(status),
    staleTime: 1000 * 60 * 2,  // 2 minutes (plus court que le défaut global)
  })
}
```

**📖 Explications** :

**useQuery** : Pour les opérations de **lecture** (GET)  
**queryKey** : Identifiant unique du cache. `['resources', 'discovered']` ≠ `['resources', 'validated']`  
**queryFn** : Fonction qui retourne les données  
**staleTime local** : Override la config globale (2 min au lieu de 5 min)

**Utilisation** :
```tsx
const { data, isLoading, error } = useResources('discovered')

if (isLoading) return <LoadingSpinner />
if (error) return <ErrorMessage error={error} />
return <ResourcesList resources={data} />
```

**Cache automatique** :
```
1er appel : isLoading → fetch API → data
2ème appel : data instantanément depuis cache (pas de loading !)
Après 2 min : refetch en arrière-plan
```

---

### Hook : `useCountriesConfig` - Configuration pays

**Fichier** : `src/hooks/useCountriesConfig.ts`

```typescript
import { useQuery } from '@tanstack/react-query'

interface Country {
  country_name: string
  country_code: string
  flag: string
  search_terms: string[]
}

interface CountriesConfig {
  supported_languages: string[]
  total_countries: number
  countries_by_language: Record<string, Country[]>
}

export function useCountriesConfig() {
  return useQuery({
    queryKey: ['config', 'countries'],
    queryFn: async () => {
      const response = await fetch('http://localhost:8000/geographic/countries', {
        headers: { 'Authorization': 'Bearer admin-token-2024' }
      })
      if (!response.ok) throw new Error(`Erreur: ${response.status}`)
      const data = await response.json()
      return data.data as CountriesConfig
    },
    staleTime: 1000 * 60 * 30, // 30 minutes (config change rarement)
  })
}
```

**Pourquoi staleTime long ?** : La configuration pays/langues change très rarement, on peut garder en cache longtemps.

---

### Hook : `useValidateResource` - Validation avec invalidation

**Fichier** : `src/hooks/useValidateResource.ts`

```typescript
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { validateCriticalSource } from '../services/api'

export function useValidateResource() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (request) => validateCriticalSource(request),
    onSuccess: () => {
      // 🔄 Invalider le cache pour refetch automatiquement
      queryClient.invalidateQueries({ queryKey: ['resources'] })
    },
  })
}
```

**📖 Explications** :

**useQueryClient** : Accès au client pour manipuler le cache  
**onSuccess** : Callback exécuté après succès  
**invalidateQueries** : Force le refetch de toutes les queries qui matchent

**Flow complet** :
```
User clique "Valider"
    ↓
mutation.mutate(request)
    ↓
POST /sources/validate
    ↓
Backend met à jour la ressource
    ↓
onSuccess() → invalidateQueries(['resources'])
    ↓
Toutes les queries ['resources', ...] refetch automatiquement
    ↓
Listes mises à jour partout dans l'app 🎉
```

---

## 🧱 Composants UI Réutilisables {#composants-ui}

**Rôle** : Composants génériques sans logique métier, réutilisables partout.

### Composant : `Button`

**Fichier** : `src/components/ui/Button.tsx`

```tsx
interface ButtonProps {
  label: string
  onClick: () => void
  variant?: 'primary' | 'secondary' | 'tab' | 'tab-active'
  disabled?: boolean
  type?: 'button' | 'submit' | 'reset'
}

function Button({
  label,
  onClick,
  variant = 'primary',
  disabled = false,
  type = 'button'
}: ButtonProps) {
  
  const baseStyles = "px-4 py-2 rounded-lg font-medium transition-colors"
  
  const variantStyles = {
    primary: "bg-purple-500 text-white hover:bg-purple-600",
    secondary: "bg-green-500 text-white hover:bg-green-600",
    tab: "bg-gray-100 text-gray-700 hover:bg-gray-200",
    'tab-active': "bg-blue-600 text-white"
  }[variant]

  const disabledStyles = disabled
    ? "opacity-50 cursor-not-allowed"
    : "cursor-pointer"

  return (
    <button
      type={type}
      onClick={onClick}
      disabled={disabled}
      className={`${baseStyles} ${variantStyles} ${disabledStyles}`}
    >
      {label}
    </button>
  )
}

export default Button
```

**📖 Explications** :

**Props typées** : Interface définit le contrat du composant  
**Variants** : 4 styles différents selon l'usage (primary, secondary, tab, tab-active)  
**Conditional styling** : Styles ajoutés selon `disabled`  
**Type HTML** : `type="submit"` pour les formulaires, `type="button"` par défaut

**Utilisation** :
```tsx
<Button 
  label="Rechercher" 
  onClick={handleSearch} 
  variant="primary" 
  disabled={isPending}
/>
```

---

### Composant : `LoadingSpinner`

**Fichier** : `src/components/ui/LoadingSpinner.tsx`

```tsx
export function LoadingSpinner() {
  return (
    <div className="flex items-center justify-center p-8">
      <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
      <span className="ml-3 text-gray-600">Chargement...</span>
    </div>
  )
}
```

**📖 Explications** :

**animate-spin** : Animation Tailwind (rotation continue)  
**border-b-2** : Bordure inférieure pour effet spinner  
**Simple et réutilisable** : Pas de props, juste un affichage

**Utilisation** :
```tsx
{isLoading && <LoadingSpinner />}
```

---

### Composant : `ErrorMessage`

**Fichier** : `src/components/ui/ErrorMessage.tsx`

```tsx
import Button from './Button'

interface ErrorMessageProps {
  error: Error | unknown
  onRetry?: () => void
}

export function ErrorMessage({ error, onRetry }: ErrorMessageProps) {
  const message = error instanceof Error 
    ? error.message 
    : 'Une erreur est survenue'
  
  return (
    <div className="bg-red-50 border border-red-200 rounded-lg p-4">
      <div className="flex items-start">
        <span className="text-2xl mr-3">❌</span>
        <div className="flex-1">
          <h3 className="text-sm font-medium text-red-800">Erreur</h3>
          <p className="mt-1 text-sm text-red-700">{message}</p>
          {onRetry && (
            <div className="mt-3">
              <Button
                label="🔄 Réessayer"
                onClick={onRetry}
                variant="secondary"
              />
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
```

**📖 Explications** :

**Type guard** : `error instanceof Error` vérifie le type  
**Props optionnelle** : `onRetry?` peut être undefined  
**Conditional rendering** : Bouton affiché seulement si `onRetry` fourni

**Utilisation** :
```tsx
{error && (
  <ErrorMessage 
    error={error} 
    onRetry={() => mutation.mutate(variables)} 
  />
)}
```

---

## 🎯 Composants Features - Logique Métier {#composants-features}

**Rôle** : Composants spécifiques à l'application, avec logique métier.

### Composant : `DiscoveryForm`

**Fichier** : `src/components/features/DiscoveryForm.tsx`

**Rôle** : Formulaire de recherche avec sélection langue, pays, catégories.

```tsx
import React, { useState } from 'react'
import type { DiscoveryFilters } from '../../services/api'
import Button from '../ui/Button'

interface DiscoveryFormProps {
  onSubmit: (filters: DiscoveryFilters) => void
  loading: boolean
}

const LANGUAGES = [
  { code: 'FR', name: 'Français', countries: ['France', 'Belgique', 'Suisse', 'Canada', 'Sénégal'] },
  { code: 'EN', name: 'English', countries: ['UK', 'USA', 'Australia', 'Canada', 'New Zealand'] },
  { code: 'ES', name: 'Español', countries: ['España', 'México', 'Argentina', 'Colombia', 'Perú'] },
  { code: 'DE', name: 'Deutsch', countries: ['Deutschland', 'Österreich', 'Schweiz'] },
  { code: 'PT', name: 'Português', countries: ['Portugal', 'Brasil', 'Angola', 'Moçambique'] },
]

const CATEGORIES = [
  { value: 'contact_urgence', label: 'Contacts d\'urgence' },
  { value: 'procedure_plateforme', label: 'Procédures plateformes' },
  { value: 'signalement_autorite', label: 'Signalement autorités' },
  { value: 'association_locale', label: 'Associations locales' },
]

export function DiscoveryForm({ onSubmit, loading }: DiscoveryFormProps) {
  // 📝 États locaux du formulaire
  const [language, setLanguage] = useState('FR')
  const [selectedCategories, setSelectedCategories] = useState<string[]>(['contact_urgence'])
  const [selectedCountries, setSelectedCountries] = useState<string[]>([])
  const [maxPerCategory, setMaxPerCategory] = useState(3)

  // Langue courante (pour afficher les pays correspondants)
  const currentLanguage = LANGUAGES.find(l => l.code === language)

  // 🔄 Toggle catégorie (ajouter/retirer)
  const handleCategoryToggle = (category: string) => {
    setSelectedCategories(prev =>
      prev.includes(category)
        ? prev.filter(c => c !== category)
        : [...prev, category]
    )
  }

  // 🔄 Toggle pays
  const handleCountryToggle = (country: string) => {
    setSelectedCountries(prev =>
      prev.includes(country)
        ? prev.filter(c => c !== country)
        : [...prev, country]
    )
  }

  // ✅ Soumission du formulaire
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()  // Empêche rechargement page
    onSubmit({
      language,
      categories: selectedCategories,
      countries: selectedCountries,
      max_per_category: maxPerCategory,
    })
  }

  return (
    <form onSubmit={handleSubmit} className="bg-white rounded-lg shadow-md p-6 space-y-6">
      {/* Sélection Langue */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          🌍 Langue
        </label>
        <select
          value={language}
          onChange={(e) => {
            setLanguage(e.target.value)
            setSelectedCountries([])  // Reset pays quand langue change
          }}
          className="w-full px-3 py-2 border border-gray-300 rounded-md"
        >
          {LANGUAGES.map(lang => (
            <option key={lang.code} value={lang.code}>
              {lang.name}
            </option>
          ))}
        </select>
      </div>

      {/* Sélection Catégories (Checkboxes) */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          📁 Catégories ({selectedCategories.length} sélectionnées)
        </label>
        <div className="space-y-2">
          {CATEGORIES.map(cat => (
            <label key={cat.value} className="flex items-center gap-2 p-2 hover:bg-gray-50 rounded cursor-pointer">
              <input
                type="checkbox"
                checked={selectedCategories.includes(cat.value)}
                onChange={() => handleCategoryToggle(cat.value)}
                className="w-4 h-4"
              />
              <span className="text-sm">{cat.label}</span>
            </label>
          ))}
        </div>
      </div>

      {/* Sélection Pays */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          🗺️ Pays ({selectedCountries.length} sélectionnés)
        </label>
        <div className="space-y-2">
          {currentLanguage?.countries.map(country => (
            <label key={country} className="flex items-center gap-2 p-2 hover:bg-gray-50 rounded cursor-pointer">
              <input
                type="checkbox"
                checked={selectedCountries.includes(country)}
                onChange={() => handleCountryToggle(country)}
                className="w-4 h-4"
              />
              <span className="text-sm">{country}</span>
            </label>
          ))}
        </div>
      </div>

      {/* Slider : Max par catégorie */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          🔢 Max par catégorie : {maxPerCategory}
        </label>
        <input
          type="range"
          min="1"
          max="10"
          value={maxPerCategory}
          onChange={(e) => setMaxPerCategory(Number(e.target.value))}
          className="w-full"
        />
      </div>

      {/* Bouton Submit */}
      <Button
        type="submit"
        label={loading ? '⏳ Recherche en cours...' : '🔍 Lancer la découverte'}
        onClick={() => {}}  // Géré par onSubmit du form
        variant="primary"
        disabled={loading || selectedCategories.length === 0}
      />
    </form>
  )
}
```

**📖 Explications Détaillées** :

#### États locaux (useState)
```tsx
const [language, setLanguage] = useState('FR')
```
- Chaque champ du formulaire a son propre state
- `useState<string[]>([])` pour les listes (catégories, pays)
- `useState(3)` pour le nombre (maxPerCategory)

#### Toggle pattern (ajouter/retirer d'une liste)
```tsx
const handleCategoryToggle = (category: string) => {
  setSelectedCategories(prev =>
    prev.includes(category)      // Si déjà présent
      ? prev.filter(c => c !== category)  // → Retirer
      : [...prev, category]       // Sinon → Ajouter
  )
}
```

#### Soumission de formulaire
```tsx
const handleSubmit = (e: React.FormEvent) => {
  e.preventDefault()  // ⚠️ Important : empêche rechargement page
  onSubmit({ language, categories: selectedCategories, ... })
}
```

#### Props callback
```tsx
interface DiscoveryFormProps {
  onSubmit: (filters: DiscoveryFilters) => void  // Fonction fournie par parent
  loading: boolean  // État fourni par parent
}
```

Le **parent** (DiscoveryPage) contrôle ce qui se passe après submit :
```tsx
<DiscoveryForm 
  onSubmit={(filters) => discovery.mutate(filters)}
  loading={discovery.isPending}
/>
```

---

### Composant : `DiscoveredResourceCard`

**Fichier** : `src/components/features/DiscoveredResourceCard.tsx`

**Rôle** : Affiche une ressource découverte avec son score de confiance.

```tsx
import type { DiscoveredResource } from '../../services/api'

interface DiscoveredResourceCardProps {
  resource: DiscoveredResource
}

export function DiscoveredResourceCard({ resource }: DiscoveredResourceCardProps) {
  // 🎨 Couleur selon le score de confiance
  const confidenceColor = 
    resource.confidence >= 0.8 ? 'bg-green-100 text-green-800' :
    resource.confidence >= 0.5 ? 'bg-yellow-100 text-yellow-800' :
    'bg-red-100 text-red-800'

  return (
    <div className="bg-white rounded-lg shadow-md p-6 mb-4 hover:shadow-lg transition-shadow">
      {/* Header */}
      <div className="flex justify-between items-start mb-3">
        <h3 className="text-lg font-semibold text-gray-900">
          {resource.name}
        </h3>
        <div className="flex gap-2">
          {/* Badge : Nouveau ou Existant */}
          {resource.is_new && (
            <span className="px-2 py-1 text-xs font-medium rounded-full bg-blue-100 text-blue-800">
              🆕 Nouveau
            </span>
          )}
          {/* Badge : Score de confiance */}
          <span className={`px-2 py-1 text-xs font-medium rounded-full ${confidenceColor}`}>
            {Math.round(resource.confidence * 100)}%
          </span>
        </div>
      </div>

      {/* Description */}
      {resource.description && (
        <p className="text-gray-600 text-sm mb-3 line-clamp-2">
          {resource.description}
        </p>
      )}

      {/* Infos */}
      <div className="flex flex-wrap gap-3 text-sm text-gray-700">
        <span>🌍 {resource.country}</span>
        {resource.phone && <span>📞 {resource.phone}</span>}
        {resource.email && <span>📧 {resource.email}</span>}
        <span className="px-2 py-1 bg-gray-100 rounded text-xs">
          {resource.category}
        </span>
      </div>

      {/* Raison de doublon si applicable */}
      {resource.duplicate_reason && (
        <div className="mt-3 p-2 bg-orange-50 border border-orange-200 rounded text-sm text-orange-800">
          ⚠️ Doublon : {resource.duplicate_reason}
        </div>
      )}
    </div>
  )
}
```

**📖 Explications** :

**Conditional styling** : Couleur du badge selon `confidence`
```tsx
const confidenceColor = 
  resource.confidence >= 0.8 ? 'bg-green-100 text-green-800' :  // Vert si > 80%
  resource.confidence >= 0.5 ? 'bg-yellow-100 text-yellow-800' : // Jaune si 50-80%
  'bg-red-100 text-red-800'  // Rouge si < 50%
```

**Conditional rendering** : Éléments affichés seulement si les données existent
```tsx
{resource.phone && <span>📞 {resource.phone}</span>}
{resource.duplicate_reason && <div>⚠️ Doublon</div>}
```

**Tailwind utility** : `line-clamp-2` limite la description à 2 lignes

---

### Composant : `DiscoveredResourcesList`

**Fichier** : `src/components/features/DiscoveredResourcesList.tsx`

**Rôle** : Affiche la liste complète des ressources avec filtres et stats.

```tsx
import { useState } from 'react'
import type { DiscoveredResource } from '../../services/api'
import { DiscoveredResourceCard } from './DiscoveredResourceCard'

interface DiscoveredResourcesListProps {
  resources: DiscoveredResource[]
}

export function DiscoveredResourcesList({ resources }: DiscoveredResourcesListProps) {
  const [filterNew, setFilterNew] = useState<boolean | null>(null)  // null = tous

  // 📊 Calcul des statistiques
  const stats = {
    total: resources.length,
    new: resources.filter(r => r.is_new).length,
    existing: resources.filter(r => !r.is_new).length,
    duplicates: resources.filter(r => r.duplicate_reason).length,
  }

  // 🔍 Filtrage
  const filteredResources = resources.filter(resource => {
    if (filterNew === null) return true  // Afficher tous
    return resource.is_new === filterNew
  })

  if (resources.length === 0) {
    return (
      <div className="text-center py-12 text-gray-500 bg-gray-50 rounded-lg">
        <span className="text-4xl mb-2 block">📭</span>
        Aucune ressource découverte
      </div>
    )
  }

  return (
    <div>
      {/* Stats */}
      <div className="grid grid-cols-4 gap-4 mb-6">
        <div className="bg-white p-4 rounded-lg shadow text-center">
          <div className="text-2xl font-bold text-gray-900">{stats.total}</div>
          <div className="text-sm text-gray-600">Total</div>
        </div>
        <div className="bg-white p-4 rounded-lg shadow text-center">
          <div className="text-2xl font-bold text-blue-600">{stats.new}</div>
          <div className="text-sm text-gray-600">Nouvelles</div>
        </div>
        <div className="bg-white p-4 rounded-lg shadow text-center">
          <div className="text-2xl font-bold text-gray-600">{stats.existing}</div>
          <div className="text-sm text-gray-600">Existantes</div>
        </div>
        <div className="bg-white p-4 rounded-lg shadow text-center">
          <div className="text-2xl font-bold text-orange-600">{stats.duplicates}</div>
          <div className="text-sm text-gray-600">Doublons</div>
        </div>
      </div>

      {/* Filtres */}
      <div className="flex gap-2 mb-4">
        <button
          onClick={() => setFilterNew(null)}
          className={`px-4 py-2 rounded ${filterNew === null ? 'bg-blue-600 text-white' : 'bg-gray-100'}`}
        >
          Toutes ({stats.total})
        </button>
        <button
          onClick={() => setFilterNew(true)}
          className={`px-4 py-2 rounded ${filterNew === true ? 'bg-blue-600 text-white' : 'bg-gray-100'}`}
        >
          Nouvelles ({stats.new})
        </button>
        <button
          onClick={() => setFilterNew(false)}
          className={`px-4 py-2 rounded ${filterNew === false ? 'bg-blue-600 text-white' : 'bg-gray-100'}`}
        >
          Existantes ({stats.existing})
        </button>
      </div>

      {/* Liste */}
      <div className="space-y-4">
        {filteredResources.map(resource => (
          <DiscoveredResourceCard key={resource.id} resource={resource} />
        ))}
      </div>

      {/* Message si filtre vide */}
      {filteredResources.length === 0 && (
        <div className="text-center py-8 text-gray-500">
          Aucune ressource dans ce filtre
        </div>
      )}
    </div>
  )
}
```

**📖 Explications** :

**Calcul de stats** :
```tsx
const stats = {
  total: resources.length,
  new: resources.filter(r => r.is_new).length,  // Compte les nouveaux
  duplicates: resources.filter(r => r.duplicate_reason).length,
}
```

**Filtrage avec state** :
```tsx
const [filterNew, setFilterNew] = useState<boolean | null>(null)
// null = tous, true = nouveaux, false = existants

const filteredResources = resources.filter(resource => {
  if (filterNew === null) return true
  return resource.is_new === filterNew
})
```

**Styling conditionnel des boutons de filtre** :
```tsx
className={`px-4 py-2 rounded ${filterNew === null ? 'bg-blue-600 text-white' : 'bg-gray-100'}`}
```

---

## 📄 Pages - Assemblage Final {#pages}

### Page : `DiscoveryPage`

**Fichier** : `src/pages/DiscoveryPage.tsx`

**Rôle** : Page complète de découverte. Orchestre le DiscoveryForm et l'affichage des résultats.

```tsx
import { useDiscoverResources } from '../hooks/useDiscoverResources'
import { DiscoveryForm } from '../components/features/DiscoveryForm'
import { DiscoveredResourcesList } from '../components/features/DiscoveredResourcesList'
import { LoadingSpinner } from '../components/ui/LoadingSpinner'
import { ErrorMessage } from '../components/ui/ErrorMessage'

export function DiscoveryPage() {
  // 🎣 Hook TanStack Query pour la découverte
  const discovery = useDiscoverResources()

  // 📝 Handler : soumission du formulaire
  const handleSearch = (filters: any) => {
    discovery.mutate(filters)
  }

  return (
    <div className="max-w-7xl mx-auto p-6">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">
          🔍 Découverte de Ressources
        </h1>
        <p className="mt-2 text-gray-600">
          Recherchez des ressources par langue, pays et catégorie
        </p>
      </div>

      {/* Layout : Formulaire + Résultats */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        {/* Colonne 1/3 : Formulaire */}
        <div className="lg:col-span-1">
          <DiscoveryForm
            onSubmit={handleSearch}
            loading={discovery.isPending}
          />
        </div>

        {/* Colonne 2/3 : Résultats */}
        <div className="lg:col-span-2">
          
          {/* État 1 : Chargement */}
          {discovery.isPending && <LoadingSpinner />}

          {/* État 2 : Erreur */}
          {discovery.error && (
            <ErrorMessage
              error={discovery.error}
              onRetry={() => discovery.mutate(discovery.variables!)}
            />
          )}

          {/* État 3 : Succès */}
          {discovery.data && (
            <>
              <div className="mb-4 p-4 bg-green-50 border border-green-200 rounded-lg">
                <p className="text-green-800 font-medium">
                  ✅ {discovery.data.total_discovered} ressource(s) découverte(s)
                </p>
                {discovery.data.estimated_duration && (
                  <p className="text-sm text-green-700 mt-1">
                    Durée estimée : {discovery.data.estimated_duration}
                  </p>
                )}
              </div>

              <DiscoveredResourcesList 
                resources={discovery.data.newly_discovered || []} 
              />
            </>
          )}

          {/* État 4 : Initial (aucune recherche lancée) */}
          {!discovery.isPending && !discovery.data && !discovery.error && (
            <div className="text-center py-16 bg-gray-50 rounded-lg">
              <span className="text-6xl mb-4 block">🔎</span>
              <p className="text-gray-600 text-lg">
                Configurez vos filtres et lancez une recherche
              </p>
            </div>
          )}

        </div>
      </div>
    </div>
  )
}
```

**📖 Explications Détaillées** :

#### Pattern "4 États"

Toute page avec appel API doit gérer **4 états** :

1. **Initial** : Aucune action lancée
```tsx
{!isPending && !data && !error && <MessageInitial />}
```

2. **Loading** : Requête en cours
```tsx
{isPending && <LoadingSpinner />}
```

3. **Error** : Requête échouée
```tsx
{error && <ErrorMessage error={error} onRetry={...} />}
```

4. **Success** : Données reçues
```tsx
{data && <AffichageResultats data={data} />}
```

#### Retry intelligent

```tsx
onRetry={() => discovery.mutate(discovery.variables!)}
```

- `discovery.variables` : TanStack Query garde les derniers paramètres passés à `mutate()`
- Permet de relancer la même requête avec les mêmes filtres

#### Layout responsive

```tsx
<div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
  <div className="lg:col-span-1">Formulaire</div>
  <div className="lg:col-span-2">Résultats</div>
</div>
```

- **Mobile** : 1 colonne (formulaire au-dessus, résultats en-dessous)
- **Desktop** : 3 colonnes (formulaire 1/3, résultats 2/3)

---

### Page : `ConfigurationPage`

**Fichier** : `src/pages/ConfigurationPage.tsx`

**Rôle** : Affiche la configuration des langues et pays supportés.

```tsx
import { useCountriesConfig } from '../hooks/useCountriesConfig'
import { LanguageCard } from '../components/features/LanguageCard'
import { LoadingSpinner } from '../components/ui/LoadingSpinner'
import { ErrorMessage } from '../components/ui/ErrorMessage'

export function ConfigurationPage() {
  const { data, isLoading, error, refetch } = useCountriesConfig()

  // État : Chargement
  if (isLoading) return <LoadingSpinner />

  // État : Erreur
  if (error) return <ErrorMessage error={error} onRetry={refetch} />

  // État : Pas de données (ne devrait jamais arriver)
  if (!data) return <div>Aucune configuration disponible</div>

  // 📊 Calculs statistiques
  const totalOrganizations = Object.values(data.countries_by_language)
    .flat()
    .reduce((sum, c) => sum + c.organizations_count, 0)

  return (
    <div className="max-w-7xl mx-auto p-6">
      {/* Header avec stats globales */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-4">
          🗺️ Configuration Pays & Langues
        </h1>
        
        <div className="grid grid-cols-3 gap-4">
          <div className="bg-white p-4 rounded-lg shadow text-center">
            <div className="text-3xl font-bold text-blue-600">
              {data.supported_languages.length}
            </div>
            <div className="text-sm text-gray-600">Langues supportées</div>
          </div>
          <div className="bg-white p-4 rounded-lg shadow text-center">
            <div className="text-3xl font-bold text-green-600">
              {data.total_countries}
            </div>
            <div className="text-sm text-gray-600">Pays configurés</div>
          </div>
          <div className="bg-white p-4 rounded-lg shadow text-center">
            <div className="text-3xl font-bold text-purple-600">
              {totalOrganizations}
            </div>
            <div className="text-sm text-gray-600">Organisations</div>
          </div>
        </div>
      </div>

      {/* Grille de cartes par langue */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {data.supported_languages.map(languageCode => (
          <LanguageCard
            key={languageCode}
            languageCode={languageCode}
            countries={data.countries_by_language[languageCode] || []}
          />
        ))}
      </div>

      {/* Info footer */}
      <div className="mt-8 p-4 bg-blue-50 border border-blue-200 rounded-lg">
        <p className="text-sm text-blue-800">
          💡 Cette configuration détermine les pays et langues disponibles pour la découverte de ressources.
        </p>
      </div>
    </div>
  )
}
```

**📖 Explications** :

**Calcul total organisations** :
```tsx
const totalOrganizations = Object.values(data.countries_by_language)
  .flat()  // Aplatit tous les tableaux de pays en un seul
  .reduce((sum, c) => sum + c.organizations_count, 0)  // Somme
```

**Guard clauses** : Sortie anticipée pour les cas d'erreur
```tsx
if (isLoading) return <LoadingSpinner />
if (error) return <ErrorMessage error={error} onRetry={refetch} />
if (!data) return <div>Aucune donnée</div>

// Ici, TypeScript sait que data existe et n'est pas undefined
```

---

## 🔄 Workflow Complet des Données {#workflow}

### Schéma : De l'Action Utilisateur aux Données Affichées

```
┌─────────────────────────────────────────────────────────────┐
│ 1️⃣ ACTION UTILISATEUR                                      │
│    User remplit formulaire et clique "Rechercher"           │
└─────────────────┬───────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────┐
│ 2️⃣ COMPOSANT : DiscoveryForm                               │
│    - e.preventDefault() empêche rechargement                │
│    - handleSubmit() crée objet DiscoveryFilters            │
│    - Appelle onSubmit(filters) fourni par parent           │
└─────────────────┬───────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────┐
│ 3️⃣ PAGE : DiscoveryPage                                    │
│    handleSearch = (filters) => discovery.mutate(filters)    │
│    → Déclenche la mutation TanStack Query                   │
└─────────────────┬───────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────┐
│ 4️⃣ HOOK : useDiscoverResources                             │
│    useMutation({                                            │
│      mutationFn: (filters) => discoverResources(filters)    │
│    })                                                       │
│    → TanStack Query exécute mutationFn                      │
│    → discovery.isPending = true                             │
└─────────────────┬───────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────┐
│ 5️⃣ SERVICE API : discoverResources()                       │
│    - fetch() POST /geographic/discover                      │
│    - Headers : Content-Type, Authorization                  │
│    - Body : JSON.stringify(filters)                         │
└─────────────────┬───────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────┐
│ 6️⃣ BACKEND FASTAPI                                          │
│    - Reçoit la requête                                      │
│    - Appelle le LLM (OpenAI/autre)                          │
│    - Recherche ressources                                   │
│    - Déduplique                                             │
│    - Retourne JSON avec les ressources                      │
└─────────────────┬───────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────┐
│ 7️⃣ SERVICE API : Transformation                            │
│    - Parse response.json()                                  │
│    - Transforme structure backend → frontend                │
│    - Return DiscoveryResponse                               │
└─────────────────┬───────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────┐
│ 8️⃣ TANSTACK QUERY : Mise en Cache                          │
│    - discovery.isPending = false                            │
│    - discovery.data = résultat                              │
│    - Mise en cache (pas de queryKey car mutation)           │
└─────────────────┬───────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────┐
│ 9️⃣ PAGE : React Re-render                                  │
│    {discovery.data && <DiscoveredResourcesList />}          │
│    → Condition vraie, composant affiché                     │
└─────────────────┬───────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────┐
│ 🔟 COMPOSANT : DiscoveredResourcesList                      │
│    - Reçoit resources en props                              │
│    - Calcule stats (total, nouveaux, doublons)              │
│    - Map sur resources → DiscoveredResourceCard pour chaque │
└─────────────────┬───────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────┐
│ 1️⃣1️⃣ USER VOIT LES RÉSULTATS                              │
│    ✅ Liste de ressources découvertes                       │
│    📊 Statistiques                                          │
│    🎨 Cartes avec infos et badges                           │
└─────────────────────────────────────────────────────────────┘
```

### Points Clés du Workflow

#### 🔄 Flux de Données Unidirectionnel

React suit un flux **top-down** (du parent vers les enfants) :
```
App → MainApp → DiscoveryPage → DiscoveryForm
                      ↓
                 (onSubmit callback)
                      ↓
                DiscoveryPage reçoit les filtres
                      ↓
                Appelle discovery.mutate()
```

#### 📦 Props vs State

**State** : Données qui peuvent changer dans le composant
```tsx
const [language, setLanguage] = useState('FR')  // State local
```

**Props** : Données passées par le parent (lecture seule)
```tsx
function DiscoveryForm({ onSubmit, loading }: Props) {
  // onSubmit et loading viennent du parent
}
```

#### 🔄 Pattern "Lift State Up"

Si 2 composants ont besoin du même state, on le "remonte" au parent commun :
```
MainApp (state: currentPage)
   ↓
Header (props: currentPage, onNavigate)
   ↓
User clique → onNavigate('discovery')
   ↓
MainApp change currentPage
   ↓
Re-render avec nouvelle page
```

---

### Workflow : Invalidation de Cache

Scénario : User valide une ressource

```
┌─────────────────────────────────────────────────────────────┐
│ 1️⃣ User clique "Valider"                                    │
└─────────────────┬───────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────┐
│ 2️⃣ Hook : useValidateResource                              │
│    mutation.mutate(request)                                 │
└─────────────────┬───────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────┐
│ 3️⃣ API : POST /sources/validate                            │
│    Backend met à jour la ressource                          │
└─────────────────┬───────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────┐
│ 4️⃣ onSuccess callback                                       │
│    queryClient.invalidateQueries(['resources'])             │
│    → Force le refetch de toutes les queries resources       │
└─────────────────┬───────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────┐
│ 5️⃣ TanStack Query Refetch                                  │
│    - useResources('pending') refetch                        │
│    - useResources('validated') refetch                      │
│    - Toutes les listes se mettent à jour automatiquement    │
└─────────────────────────────────────────────────────────────┘
```

**Pourquoi c'est puissant ?**
- ✅ **Pas de prop drilling** : Pas besoin de passer des callbacks partout
- ✅ **Synchronisation globale** : Tous les composants se mettent à jour
- ✅ **Code simple** : Juste `invalidateQueries()` !

---

## 🎓 Checklist de Développement

### Phase 1 : Configuration Initiale
- [ ] Créer le projet Vite : `npm create vite@latest`
- [ ] Installer dépendances : `npm install @tanstack/react-query`
- [ ] Configurer TanStack Query dans `main.tsx`
- [ ] Créer la structure de dossiers (services, hooks, components, pages)

### Phase 2 : Service API
- [ ] Créer `services/api.ts`
- [ ] Définir toutes les interfaces TypeScript
- [ ] Implémenter `discoverResources()`
- [ ] Implémenter `fetchResources()`
- [ ] Tester les fonctions avec curl ou Postman

### Phase 3 : Hooks Personnalisés
- [ ] Créer `useDiscoverResources()` avec useMutation
- [ ] Créer `useResources()` avec useQuery
- [ ] Créer `useCountriesConfig()` avec useQuery
- [ ] Créer `useValidateResource()` avec invalidateQueries

### Phase 4 : Composants UI
- [ ] Créer `Button.tsx` (4 variants)
- [ ] Créer `LoadingSpinner.tsx`
- [ ] Créer `ErrorMessage.tsx`
- [ ] Créer `Header.tsx` avec navigation

### Phase 5 : Composants Features
- [ ] Créer `DiscoveryForm.tsx` (formulaire complexe avec états)
- [ ] Créer `DiscoveredResourceCard.tsx`
- [ ] Créer `DiscoveredResourcesList.tsx` (avec filtres et stats)
- [ ] Créer `LanguageCard.tsx`

### Phase 6 : Pages
- [ ] Créer `DiscoveryPage.tsx` (orchestration complète)
- [ ] Créer `ConfigurationPage.tsx`
- [ ] Tester les 4 états (initial, loading, error, success)

### Phase 7 : Layout & Navigation
- [ ] Créer `MainApp.tsx` avec navigation par onglets
- [ ] Intégrer dans `App.tsx`
- [ ] Tester la navigation

### Phase 8 : Tests & Validation
- [ ] Tester découverte avec différents filtres
- [ ] Vérifier le cache TanStack Query (devtools)
- [ ] Tester les erreurs (backend éteint)
- [ ] Vérifier le responsive (mobile/desktop)

---

## 🚀 Commandes Utiles

```bash
# Développement
npm run dev                    # Lance le serveur de dev (port 5173)

# Build production
npm run build                  # Compile l'app pour production
npm run preview                # Preview du build de production

# Outils
npm run lint                   # Vérifie les erreurs ESLint
```

---

## 📚 Ressources & Documentation

- **React** : https://react.dev/
- **TanStack Query** : https://tanstack.com/query/latest
- **TypeScript** : https://www.typescriptlang.org/
- **Tailwind CSS** : https://tailwindcss.com/

---

**Dernière mise à jour** : Guide de développement complet  
**Statut** : 📝 Prêt pour développement pas à pas  
**Version Frontend** : React 18 + TanStack Query v5
