# 🔄 Workflow des Données : Configuration Pays

> **Document pédagogique** : Flux de données complet depuis le clic sur "Configuration Pays" jusqu'à l'affichage final.

---

## 📋 Table des matières

1. [Vue d'ensemble](#vue-densemble)
2. [Étape 1 : Click sur le bouton](#étape-1--click-sur-le-bouton)
3. [Étape 2 : Propagation du callback](#étape-2--propagation-du-callback)
4. [Étape 3 : Changement d'état et re-render](#étape-3--changement-détat-et-re-render)
5. [Étape 4 : Montage de ConfigurationPage](#étape-4--montage-de-configurationpage)
6. [Étape 5 : Appel API via React Query](#étape-5--appel-api-via-react-query)
7. [Étape 6 : Transmission des données aux composants enfants](#étape-6--transmission-des-données-aux-composants-enfants)
8. [Étape 7 : Rendu final](#étape-7--rendu-final)
9. [Résumé des concepts clés](#résumé-des-concepts-clés)

---

## Vue d'ensemble

### 🎯 Objectif
Comprendre comment React gère le flux de données depuis une **interaction utilisateur** (click) jusqu'à l'**affichage** des données venant du backend.

### 🗺️ Schéma général

```
┌─────────────────────────────────────────────────────────────────┐
│                         UTILISATEUR                             │
│                    👆 Click "Configuration Pays"                │
└────────────────────────────────┬────────────────────────────────┘
                                 ↓
┌─────────────────────────────────────────────────────────────────┐
│  ÉTAPE 1-3 : Gestion de la navigation (React State)            │
│  Header → MainApp → setCurrentPage('configuration')            │
└────────────────────────────────┬────────────────────────────────┘
                                 ↓
┌─────────────────────────────────────────────────────────────────┐
│  ÉTAPE 4 : Montage du composant ConfigurationPage              │
│  React crée l'instance du composant                             │
└────────────────────────────────┬────────────────────────────────┘
                                 ↓
┌─────────────────────────────────────────────────────────────────┐
│  ÉTAPE 5 : Récupération des données (React Query)              │
│  useCountriesConfig → fetch API → Backend                      │
└────────────────────────────────┬────────────────────────────────┘
                                 ↓
┌─────────────────────────────────────────────────────────────────┐
│  ÉTAPE 6-7 : Affichage (Props drilling)                        │
│  data → LanguageCard (props) → Rendu HTML                      │
└─────────────────────────────────────────────────────────────────┘
```

---

## Étape 1 : Click sur le bouton

### 📂 Fichier : `frontend/src/components/ui/Header.tsx`

**Ce qui se passe :**  
L'utilisateur clique sur le bouton "Configuration Pays" dans le header.

### 💻 Code concerné

```tsx
export function Header<TPage extends string>({
    navigationItems,    // ← Reçu de MainApp
    currentPage,        // ← Reçu de MainApp
    onNavigate          // ← Callback reçu de MainApp
}: HeaderProps<TPage>) {
    return (
        <nav className="flex gap-2">
            {navigationItems.map((item) => (
                <Button
                    key={item.value}
                    onClick={() => onNavigate(item.value)}
                    //              ^^^^^^^^^ ^^^^^^^^^^
                    //              Callback  Argument: 'configuration'
                >
                    {item.label}  {/* "Configuration Pays" */}
                </Button>
            ))}
        </nav>
    )
}
```

### 🎓 Concepts clés

**Props reçues par Header :**
```typescript
{
    navigationItems: [
        { label: 'Configuration Pays', value: 'configuration' },
        { label: 'Découverte Ressource', value: 'discovery' }
    ],
    currentPage: 'discovery',              // État actuel
    onNavigate: (page) => setCurrentPage(page)  // Callback de MainApp
}
```

**Flux événementiel :**
```
Click → onClick() → onNavigate('configuration') → Remonte vers MainApp
```

---

## Étape 2 : Propagation du callback

### 📂 Fichier : `frontend/src/components/layout/MainApp.tsx`

**Ce qui se passe :**  
Le callback `onNavigate` passé à Header est en réalité une fonction définie dans MainApp.

### 💻 Code concerné

```tsx
export function MainApp({ onDemoClick }: MainAppProps) {
    // 🔵 État local : quelle page est affichée ?
    const [currentPage, setCurrentPage] = useState<PageType>('configuration')
    
    // 🟢 Données de navigation
    const navigationItems: NavigationItem<PageType>[] = [
        { label: 'Configuration Pays', value: 'configuration' },
        { label: 'Découverte Ressource', value: 'discovery' }
    ]

    return (
        <QueryClientProvider client={queryClient}>
            <Header
                title="Interface de découvertes des ressources"
                userName='Admin'
                navigationItems={navigationItems}
                currentPage={currentPage}
                onNavigate={(page: PageType) => setCurrentPage(page)}
                //         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
                //         Fonction anonyme passée en prop
            />
            
            <main>
                {currentPage === 'configuration' && <ConfigurationPage />}
                {currentPage === 'discovery' && <DiscoveryPage />}
            </main>
        </QueryClientProvider>
    )
}
```

### 🎓 Concepts clés

**Pattern callback (Props drilling inversé) :**

```
┌─────────────────────────────────────────────────────────────┐
│ MainApp (parent)                                            │
│                                                             │
│ const [currentPage, setCurrentPage] = useState('config')   │
│                       ^^^^^^^^^^^^^^^^                      │
│                       Fonction de modification d'état       │
│                                                             │
│ <Header onNavigate={(page) => setCurrentPage(page)} />     │
│         ^^^^^^^^^^                                          │
│         Prop callback                                       │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ↓ Passage de la fonction
                        
┌───────────────────────┴─────────────────────────────────────┐
│ Header (enfant)                                             │
│                                                             │
│ const { onNavigate } = props                                │
│                                                             │
│ <Button onClick={() => onNavigate('configuration')} />     │
│                         ^^^^^^^^^^                          │
│                         Appel de la fonction parent !       │
└─────────────────────────────────────────────────────────────┘
```

**Le callback permet à l'enfant (Header) de modifier l'état du parent (MainApp) !**

---

## Étape 3 : Changement d'état et re-render

### 📂 Fichier : `frontend/src/components/layout/MainApp.tsx`

**Ce qui se passe :**  
`setCurrentPage('configuration')` déclenche un **re-render** de MainApp.

### 💻 Cycle de mise à jour React

```tsx
// AVANT le click
const [currentPage, setCurrentPage] = useState<PageType>('discovery')
//     ^^^^^^^^^^^
//     État : 'discovery'

// APPEL du callback depuis Header
setCurrentPage('configuration')
//             ^^^^^^^^^^^^^^^
//             Nouvelle valeur

// React déclenche un re-render
// APRÈS le re-render
const [currentPage, setCurrentPage] = useState<PageType>('discovery')
//     ^^^^^^^^^^^
//     État : 'configuration' maintenant !
```

### 🎓 Concepts clés

**Re-render en cascade :**

```
setCurrentPage('configuration')
      ↓
React détecte un changement d'état
      ↓
MainApp se re-render
      ↓
Tous les enfants de MainApp se re-render aussi
      ↓
Rendu conditionnel :
  {currentPage === 'configuration' && <ConfigurationPage />}
   ^^^^^^^^^^^^                       ^^^^^^^^^^^^^^^^^^^
   TRUE maintenant !                  Composant monté
```

**Avant vs Après :**

```tsx
// AVANT
{currentPage === 'configuration' && <ConfigurationPage />}  ← FALSE, pas rendu
{currentPage === 'discovery' && <DiscoveryPage />}          ← TRUE, rendu

// APRÈS
{currentPage === 'configuration' && <ConfigurationPage />}  ← TRUE, rendu !
{currentPage === 'discovery' && <DiscoveryPage />}          ← FALSE, démonté
```

---

## Étape 4 : Montage de ConfigurationPage

### 📂 Fichier : `frontend/src/pages/ConfigurationPage.tsx`

**Ce qui se passe :**  
React crée une instance de ConfigurationPage et exécute son code.

### 💻 Code concerné

```tsx
export function ConfigurationPage() {
    // 🔵 Hook React Query : récupération des données
    const { data, isLoading, error, refetch } = useCountriesConfig()
    //      ^^^^  ^^^^^^^^^  ^^^^^              ^^^^^^^^^^^^^^^^^
    //      Props retournées par React Query

    // 🔍 DEBUG (temporaire)
    console.log('📊 Countries config:', data)
    
    return (
        <div className="max-w-7xl mx-auto p-6">
            {/* Affichage conditionnel selon l'état */}
            {isLoading && <LoadingSpinner />}
            {error && <ErrorMessage error={error} />}
            {data && (
                <div className="grid grid-cols-1 lg:grid-cols-6 gap-3">
                    {data.supported_languages.map(langCode => (
                        <LanguageCard
                            key={langCode}
                            languageCode={langCode}
                            countries={data.countries_by_language[langCode]}
                        />
                    ))}
                </div>
            )}
        </div>
    )
}
```

### 🎓 Concepts clés

**Cycle de vie du composant :**

```
1. React crée l'instance de ConfigurationPage
2. Exécute le code de la fonction
3. Appelle useCountriesConfig() ← Hook custom
4. Retourne du JSX
5. React convertit le JSX en éléments DOM
6. Affichage à l'écran
```

**ConfigurationPage ne reçoit AUCUNE prop :**
```tsx
<ConfigurationPage />  ← Pas de props !
//                 ^^
//                 Composant autonome
```

Pourquoi ? Parce que **le hook `useCountriesConfig` gère tout** !

---

## Étape 5 : Appel API via React Query

### 📂 Fichier : `frontend/src/hooks/useCountriesConfig.ts`

**Ce qui se passe :**  
React Query gère automatiquement l'appel API, le cache, et l'état de chargement.

### 💻 Code concerné

```tsx
import { useQuery } from '@tanstack/react-query'
import { API_BASE_URL, AUTH_TOKEN } from '../services/api'

interface CountriesConfig {
    supported_languages: string[]
    total_countries: number
    countries_by_language: Record<string, Country[]>
}

export function useCountriesConfig() {
    return useQuery({
        // 🔑 Clé unique pour le cache
        queryKey: ['config', 'countries'],
        
        // 🌐 Fonction qui fait l'appel HTTP
        queryFn: async () => {
            const response = await fetch(
                `${API_BASE_URL}/geographic/countries`,
                { headers: { 'Authorization': AUTH_TOKEN } }
            )

            if (!response.ok) {
                throw new Error(`Erreur API: ${response.status}`)
            }

            const data = await response.json()
            // Backend retourne : { success: true, data: {...} }
            // On extrait juste la partie "data"
            return data.data as CountriesConfig
        },
        
        // ⏱️ Cache : données valides pendant 30 minutes
        staleTime: 1000 * 60 * 30,
    })
}
```

### 🎓 Concepts clés

**Cycle de vie de React Query :**

```
1️⃣ Premier appel de useCountriesConfig()
   ↓
   React Query vérifie le cache avec queryKey: ['config', 'countries']
   ↓
   Cache vide → Lance queryFn()
   ↓
2️⃣ Pendant le fetch
   { data: undefined, isLoading: true, error: null }
   ↓
   ConfigurationPage affiche <LoadingSpinner />
   ↓
3️⃣ Réponse du backend
   {
     "success": true,
     "data": {
       "supported_languages": ["FR", "EN", "ES", "IT", "DE", "PT"],
       "total_countries": 23,
       "countries_by_language": { ... }
     }
   }
   ↓
4️⃣ Extraction de data.data
   return data.data as CountriesConfig
   ↓
5️⃣ React Query met à jour
   { data: {...}, isLoading: false, error: null }
   ↓
   ConfigurationPage se re-render automatiquement !
   ↓
6️⃣ Cache actif (30 minutes)
   Si useCountriesConfig() est rappelé → données depuis le cache (instantané)
```

**Structure des données retournées :**

```typescript
// Ce que React Query retourne
{
    data: {
        supported_languages: ["FR", "EN", "ES", "IT", "DE", "PT"],
        total_countries: 23,
        countries_by_language: {
            "FR": [
                { country_name: "France", country_code: "FR", flag: "🇫🇷" },
                { country_name: "Belgique", country_code: "BE", flag: "🇧🇪" },
                ...
            ],
            "EN": [...],
            ...
        }
    },
    isLoading: false,
    error: null,
    refetch: () => void  // Fonction pour re-fetch manuellement
}
```

---

## Étape 6 : Transmission des données aux composants enfants

### 📂 Fichier : `frontend/src/pages/ConfigurationPage.tsx`

**Ce qui se passe :**  
ConfigurationPage itère sur les langues et passe les données à LanguageCard via **props**.

### 💻 Code concerné

```tsx
{data && (  // ← Affichage uniquement si data existe
    <div className="grid grid-cols-1 lg:grid-cols-6 gap-3">
        {data.supported_languages.map(langCode => {
            //   ^^^^                   ^^^^^^^^
            //   Prop de data          Variable de boucle
            
            // 🎯 Extraction des pays pour cette langue
            const countries = data.countries_by_language[langCode] || []
            //                ^^^^ Objet                ^^^^^^^^ Clé
            //                                          Accès dynamique !
            
            return (
                <LanguageCard
                    key={langCode}
                    languageCode={langCode}     // ← PROP
                    languageName={langCode}     // ← PROP
                    countries={countries}       // ← PROP
                />
            )
        })}
    </div>
)}
```

### 🎓 Concepts clés

**Props drilling (passage de props parent → enfant) :**

```
┌──────────────────────────────────────────────────────────┐
│ ConfigurationPage (parent)                               │
│                                                          │
│ const { data } = useCountriesConfig()                   │
│                                                          │
│ data.supported_languages.map(langCode => {              │
│     const countries = data.countries_by_language[lang]  │
│                                                          │
│     return <LanguageCard                                │
│         languageCode={langCode}      ← Prop string      │
│         countries={countries}        ← Prop array       │
│     />                                                   │
│ })                                                       │
└────────────────────────┬─────────────────────────────────┘
                         ↓ Passage de props
                         
┌────────────────────────┴─────────────────────────────────┐
│ LanguageCard (enfant)                                    │
│                                                          │
│ function LanguageCard({                                 │
│     languageCode,    ← Reçoit "FR"                      │
│     countries        ← Reçoit [{...}, {...}, ...]       │
│ }: LanguageCardProps) {                                 │
│     // Utilise les props pour afficher                  │
│     return <div>{languageCode}: {countries.length}</div>│
│ }                                                        │
└──────────────────────────────────────────────────────────┘
```

**Exemple concret pour la langue française :**

```tsx
// Dans ConfigurationPage
langCode = "FR"
countries = data.countries_by_language["FR"]
          = [
              { country_name: "France", country_code: "FR", flag: "🇫🇷" },
              { country_name: "Belgique", country_code: "BE", flag: "🇧🇪" },
              { country_name: "Suisse", country_code: "CH", flag: "🇨🇭" },
              { country_name: "Canada", country_code: "CA", flag: "🇨🇦" },
              { country_name: "Luxembourg", country_code: "LU", flag: "🇱🇺" }
            ]

// Props passées à LanguageCard
<LanguageCard
    languageCode="FR"
    countries={[...5 pays]}
/>
```

---

## Étape 7 : Rendu final

### 📂 Fichier : `frontend/src/components/features/LanguageCard.tsx`

**Ce qui se passe :**  
LanguageCard reçoit les props et affiche les informations.

### 💻 Code concerné

```tsx
interface LanguageCardProps {
    languageCode: string
    languageName: string
    countries: Country[]
}

const LANGUAGE_NAMES: Record<string, string> = {
    'FR': 'Français',
    'EN': 'English',
    'ES': 'Español',
    'IT': 'Italiano',
    'DE': 'Deutsch',
    'PT': 'Português',
}

export function LanguageCard({ 
    languageCode,   // ← Reçu en prop : "FR"
    countries       // ← Reçu en prop : [{...}, {...}, ...]
}: LanguageCardProps) {

    return (
        <div className="bg-white rounded-lg shadow-md p-6">
            {/* Header Langue */}
            <div>
                <h3 className="text-xl font-bold">
                    {LANGUAGE_NAMES[languageCode] || languageCode}
                    {/* LANGUAGE_NAMES["FR"] = "Français" */}
                </h3>
                <p className="text-sm">
                    Code : <span>{languageCode}</span>
                    {/* Affiche : "FR" */}
                </p>
            </div>

            <div>
                <div className="text-2xl font-bold">
                    {countries.length}
                    {/* Affiche : 5 (nombre de pays) */}
                </div>
                <div>Pays</div>
            </div>

            {/* Liste des pays */}
            <div>
                {countries.map(country => (
                    <div key={country.country_code}>
                        <p>
                            {country.country_name}
                            <span>({country.country_code})</span>
                        </p>
                        {/* Affiche : France (FR) */}
                    </div>
                ))}
            </div>
        </div>
    )
}
```

### 🎓 Concepts clés

**Déstructuration de props :**

```tsx
// ❌ Sans déstructuration
function LanguageCard(props: LanguageCardProps) {
    return <div>{props.languageCode}</div>  // Verbeux
}

// ✅ Avec déstructuration (code actuel)
function LanguageCard({ languageCode, countries }: LanguageCardProps) {
    return <div>{languageCode}</div>  // Plus court !
}
```

**Map sur un tableau (itération) :**

```tsx
countries.map(country => ...)
//       ^^^
//       Méthode de tableau JavaScript
//       Transforme chaque élément en JSX

// Équivalent impératif :
const elements = []
for (let i = 0; i < countries.length; i++) {
    const country = countries[i]
    elements.push(<div key={country.country_code}>...</div>)
}
return elements

// React préfère la syntaxe fonctionnelle (map)
```

**HTML final généré (simplifié) :**

```html
<div class="bg-white rounded-lg shadow-md p-6">
    <div>
        <h3 class="text-xl font-bold">Français</h3>
        <p class="text-sm">Code : <span>FR</span></p>
    </div>
    
    <div>
        <div class="text-2xl font-bold">5</div>
        <div>Pays</div>
    </div>
    
    <div>
        <div><p>France <span>(FR)</span></p></div>
        <div><p>Belgique <span>(BE)</span></p></div>
        <div><p>Suisse <span>(CH)</span></p></div>
        <div><p>Canada <span>(CA)</span></p></div>
        <div><p>Luxembourg <span>(LU)</span></p></div>
    </div>
</div>
```

---

## Résumé des concepts clés

### 🎯 Patterns React utilisés

| Pattern | Description | Exemple dans notre code |
|---------|-------------|------------------------|
| **Props** | Passage de données parent → enfant | `<LanguageCard languageCode="FR" />` |
| **Callback Props** | Passage de fonction enfant → parent | `<Header onNavigate={(page) => ...} />` |
| **State (useState)** | Gestion d'état local | `const [currentPage, setCurrentPage] = useState()` |
| **Custom Hook** | Logique réutilisable | `useCountriesConfig()` |
| **Conditional Rendering** | Affichage conditionnel | `{data && <div>...</div>}` |
| **List Rendering** | Affichage de liste | `{data.map(item => ...)}` |

### 🔄 Flux de données résumé

```
┌──────────┐     ┌─────────┐     ┌────────────────┐     ┌──────────────┐
│ Click    │────▶│ Callback│────▶│ State Change   │────▶│ Re-render    │
│ Button   │     │ onNav   │     │ setCurrentPage │     │ MainApp      │
└──────────┘     └─────────┘     └────────────────┘     └──────────────┘
                                                              │
                                                              ↓
┌──────────────────────────────────────────────────────────────────────┐
│ Mount ConfigurationPage → useCountriesConfig() → fetch API          │
└────────────────────────────────┬─────────────────────────────────────┘
                                 ↓
┌──────────────────────────────────────────────────────────────────────┐
│ React Query returns { data, isLoading, error }                      │
└────────────────────────────────┬─────────────────────────────────────┘
                                 ↓
┌──────────────────────────────────────────────────────────────────────┐
│ ConfigurationPage passes props → LanguageCard → Render HTML         │
└──────────────────────────────────────────────────────────────────────┘
```

### 📚 Points importants à retenir

1. **Unidirectional Data Flow** : Les données descendent (props), les événements remontent (callbacks)
2. **React Query** : Gère automatiquement le cache, le loading, et les erreurs
3. **Props immutables** : Les enfants ne modifient JAMAIS les props reçues
4. **Key dans les listes** : Obligatoire pour que React identifie les éléments (`key={langCode}`)
5. **Re-render intelligent** : React ne re-render que les composants dont l'état ou les props changent

### 🎓 Pour aller plus loin

**Questions de compréhension :**

1. Que se passe-t-il si on clique 2 fois de suite sur "Configuration Pays" ?
   → React détecte que `currentPage` est déjà `'configuration'`, pas de re-render

2. Pourquoi utilise-t-on `data &&` avant d'afficher le contenu ?
   → Pour éviter d'accéder à `data.supported_languages` quand `data` est `undefined`

3. Que fait React Query si on change de page puis on revient ?
   → Les données sont dans le cache, affichage instantané (pas de re-fetch)

4. Peut-on passer des fonctions en props ?
   → Oui ! C'est exactement ce qu'on fait avec `onNavigate`

5. Pourquoi `languageCode` apparaît 3 fois (clé, prop languageCode, prop languageName) ?
   → `key` pour React, `languageCode` pour identifier la langue, `languageName` pour l'affichage (redondant dans notre cas)

---

## 🔗 Fichiers impliqués

```
frontend/src/
├── components/
│   ├── layout/
│   │   └── MainApp.tsx             ← Gestion navigation, QueryClient
│   ├── ui/
│   │   └── Header.tsx              ← Boutons navigation
│   └── features/
│       └── LanguageCard.tsx        ← Affichage d'une langue
├── pages/
│   └── ConfigurationPage.tsx       ← Orchestration affichage config
├── hooks/
│   └── useCountriesConfig.ts       ← Logique fetch API
└── services/
    └── api.ts                      ← Constantes API (URL, token)
```

---

**📅 Document créé le :** 12 février 2026  
**👨‍🏫 Pour :** Apprentissage React - Flux de données  
**🎯 Objectif :** Comprendre le cycle complet d'une interaction utilisateur
