# 📘 Workflow Découverte de Ressources avec TanStack Query

## 🎯 Analyse de ta compréhension

### ✅ Ce que tu as BIEN compris

1. **Sidebar → DiscoveryPage** : Navigation correcte via React Router
2. **Formulaire DiscoveryForm** : Capture des critères de recherche  Les filtres du formulaire sont simplement passés à l'API
3. **Cache** : Les données sont mises en cache (TanStack Query le fait automatiquement)
4. **POST API** : Génération d'un prompt adapté côté backend
5. **Réponse en tableau** : Liste des ressources découvertes


## 🔄 Workflow Complet : De A à Z

### Vue d'ensemble

```
┌─────────────────────────────────────────────────────────────────┐
│  1. USER            2. FORM         3. HOOK      4. API         │
│  remplit         →  valide       →  envoie    →  traite         │
│  formulaire         données         POST         prompt         │
│                                                                  │
│  7. UI              6. HOOK         5. BACKEND                   │
│  affiche         ←  stocke       ←  retourne                   │
│  résultats          cache           ressources                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📝 Étape 1 : User remplit le formulaire

### Dans DiscoveryForm.tsx

```tsx
export function DiscoveryForm({ onSubmit, loading }: DiscoveryFormProps) {
    // 🎯 STATE LOCAL (React useState)
    const [language, setLanguage] = useState('FR')
    const [selectedCategories, setSelectedCategories] = useState(['contact_urgence'])
    const [selectedCountries, setSelectedCountries] = useState<string[]>([])
    const [maxPerCategory, setMaxPerCategory] = useState(3)
    
    // User sélectionne :
    // - Langue : FR
    // - Catégories : contact_urgence, association_locale
    // - Pays : France, Belgique
    // - Max : 5
}
```

**🎓 Concept React : State local**
- `useState` = mémoire temporaire du composant
- Change quand user interagit (select, checkbox, input)
- ❌ PAS de cache TanStack Query ici
- ✅ Juste du state React classique

---

## 📤 Étape 2 : Validation et envoi du formulaire

### Quand user clique "Rechercher"

```tsx
const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()  // ← Empêche rechargement page
    
    // 🎯 Construit l'objet de filtres
    onSubmit({
        language: 'FR',
        categories: ['contact_urgence', 'association_locale'],
        countries: ['France', 'Belgique'],
        max_per_category: 5,
    })
}
```

**Flow :**
1. User clique "Rechercher"
2. `handleSubmit` est appelé
3. `onSubmit(filters)` est appelé (prop passée par parent)
4. Les filtres remontent à `DiscoveryPage`

---

## 🔗 Étape 3 : DiscoveryPage reçoit et transmet

### Dans DiscoveryPage.tsx

```tsx
export function DiscoveryPage() {
    // 🎯 Hook TanStack Query (useMutation)
    const discovery = useDiscoverResources()
    
    // 📨 Fonction qui reçoit les filtres du formulaire
    const handleSearch = (filters: any) => {
        discovery.mutate(filters)  // ← Lance la requête API !
    }
    
    return (
        <div>
            <DiscoveryForm
                onSubmit={handleSearch}  // ← Passe la fonction au formulaire
                loading={discovery.isPending}  // ← État de chargement
            />
            
            {/* Affichage conditionnel selon état */}
            {discovery.isPending && <LoadingSpinner />}
            {discovery.error && <ErrorMessage />}
            {discovery.data && <DiscoveredResourcesList resources={discovery.data} />}
        </div>
    )
}
```

**🎓 Rôle de DiscoveryPage :**
- ✅ Chef d'orchestre : coordonne Form + Hook + Affichage
- ✅ Gère les états : loading, error, success
- ❌ NE fait PAS d'appel API directement

---

## ⚡ Étape 4 : TanStack Query useMutation

### Dans useDiscoverResources.ts (ton hook)

```tsx
import { useMutation } from '@tanstack/react-query'

export function useDiscoverResources() {
    return useMutation({
        mutationFn: (filters: DiscoveryFilters) => discoverResources(filters)
        //          ^^^^^^^^^^^^^^^^^^^^^^^^^    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
        //          Reçoit les filtres du form   Appelle la fonction API
    })
}
```

### Quand tu appelles `discovery.mutate(filters)` :

```
┌───────────────────────────────────────────────────────────┐
│  TanStack Query fait AUTOMATIQUEMENT :                    │
├───────────────────────────────────────────────────────────┤
│  1. discovery.isPending = true  (état loading)            │
│  2. Appelle discoverResources(filters)                    │
│  3. Attend la réponse...                                  │
│  4. Si succès :                                           │
│     - discovery.data = réponse                            │
│     - discovery.isPending = false                         │
│     - Cache la réponse automatiquement ✨                 │
│  5. Si erreur :                                           │
│     - discovery.error = erreur                            │
│     - discovery.isPending = false                         │
└───────────────────────────────────────────────────────────┘
```

**🚀 Magic de TanStack Query :**
- Gère automatiquement : `isPending`, `data`, `error`
- Cache la réponse (tu peux la réutiliser sans refaire l'appel)
- Re-rend le composant quand l'état change

---

## 🌐 Étape 5 : Appel API (fonction fetch)

### Dans api.ts

```tsx
export async function discoverResources(
    filters: DiscoveryFilters
): Promise<DiscoveryResponse> {
    // 🎯 Appel HTTP POST vers le backend
    const response = await fetch(`${API_BASE_URL}/geographic/discover`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': AUTH_TOKEN
        },
        body: JSON.stringify(filters)  // ← Envoie les filtres en JSON
    })
    
    if (!response.ok) {
        throw new Error(`Erreur API: ${response.status}`)
    }
    
    const backendResponse = await response.json()
    
    // 🔄 Transformation backend → frontend
    return {
        success: backendResponse.success,
        message: backendResponse.message,
        total_discovered: backendResponse.data.discovered_count,
        newly_discovered: backendResponse.data.resources,
        estimated_duration: backendResponse.data.estimated_duration
    }
}
```

**Ce qui part vers le backend :**
```json
{
  "language": "FR",
  "categories": ["contact_urgence", "association_locale"],
  "countries": ["France", "Belgique"],
  "max_per_category": 5
}
```

---

## 🤖 Étape 6 : Backend traite (LLM + Prompt)

### Côté backend Python (admin_api.py)

```python
@app.post("/geographic/discover")
async def discover_resources(request: DiscoveryRequest):
    # 1. Reçoit les filtres
    filters = {
        "language": request.language,  # FR
        "categories": request.categories,  # ["contact_urgence"]
        "countries": request.countries,  # ["France", "Belgique"]
        "max_per_category": request.max_per_category  # 5
    }
    
    # 2. Génère un prompt adapté avec LLM
    prompt = f"""
    Trouve {filters['max_per_category']} ressources de type 
    {filters['categories']} pour les pays {filters['countries']} 
    en langue {filters['language']}.
    
    Format de réponse attendu : JSON avec name, country, phone, email, etc.
    """
    
    # 3. Appelle l'IA (OpenAI, Anthropic, etc.)
    llm_response = await llm.generate(prompt)
    
    # 4. Parse et structure les résultats
    resources = parse_llm_response(llm_response)
    
    # 5. Retourne au frontend
    return {
        "success": True,
        "message": "Découverte réussie",
        "data": {
            "discovered_count": len(resources),
            "resources": resources
        }
    }
```

**🎓 Le backend :**
- Génère un **prompt intelligent** adapté aux filtres
- Appelle un **LLM** (ChatGPT, Claude, etc.)
- Parse la réponse de l'IA
- Retourne des données structurées

---

## 📦 Étape 7 : TanStack Query cache la réponse

### Cache automatique

```tsx
// Après le retour de l'API, TanStack Query fait :

discovery.data = {
    success: true,
    message: "5 ressources découvertes",
    total_discovered: 5,
    newly_discovered: [
        {
            id: "res_1",
            name: "SOS Victimes France",
            country: "France",
            phone: "+33 1 23 45 67 89",
            email: "contact@sosvictimes.fr",
            category: "contact_urgence",
            confidence: 0.95
        },
        // ... 4 autres ressources
    ]
}

// 🎯 Ces données sont AUTOMATIQUEMENT :
// - Stockées en cache mémoire (RAM)
// - Accessibles via discovery.data
// - Conservées tant que la page n'est pas rechargée
```

**🚀 Avantages du cache :**
- Si tu navigues vers une autre page puis reviens → données toujours là
- Pas besoin de refaire l'appel API
- Performance optimale

---

## 🖼️ Étape 8 : Affichage dans l'UI

### Rendu conditionnel dans DiscoveryPage

```tsx
export function DiscoveryPage() {
    const discovery = useDiscoverResources()
    
    return (
        <div>
            {/* 🔄 Pendant le chargement */}
            {discovery.isPending && (
                <LoadingSpinner />
            )}
            
            {/* ❌ En cas d'erreur */}
            {discovery.error && (
                <ErrorMessage error={discovery.error} />
            )}
            
            {/* ✅ Quand les données sont disponibles */}
            {discovery.data && (
                <DiscoveredResourcesList 
                    resources={discovery.data.newly_discovered}
                    total={discovery.data.total_discovered}
                />
            )}
        </div>
    )
}
```

**États possibles :**
1. **Initial** : Rien affiché (formulaire vide)
2. **Pending** : Spinner de chargement
3. **Error** : Message d'erreur avec bouton retry
4. **Success** : Liste des ressources découvertes

---

## 🎓 Concepts clés TanStack Query

### useMutation vs useQuery

| Aspect | `useQuery` | `useMutation` |
|--------|-----------|---------------|
| **Quand** | Au chargement du composant | Quand user déclenche action |
| **Méthode HTTP** | GET (lecture) | POST/PUT/DELETE (écriture) |
| **Cache** | Cache activé par défaut | Cache désactivé (mais data reste) |
| **Usage** | Charger liste pays | Créer/modifier ressource |
| **Exemple** | `useCountriesConfig()` | `useDiscoverResources()` |

### useMutation : Propriétés importantes

```tsx
const mutation = useMutation({
    mutationFn: (data) => apiCall(data)
})

// Propriétés accessibles :
mutation.isPending   // Boolean : requête en cours ?
mutation.isError     // Boolean : erreur ?
mutation.isSuccess   // Boolean : succès ?
mutation.data        // Données de la réponse (ou undefined)
mutation.error       // Objet erreur (ou null)
mutation.variables   // Paramètres passés à mutate()

// Méthodes :
mutation.mutate(params)      // Lancer la requête
mutation.reset()             // Reset tous les états
```

---

## 📊 Diagramme de séquence complet

```
User                DiscoveryForm       DiscoveryPage       useDiscoverResources    API Backend         TanStack Query
│                        │                    │                      │                    │                    │
│ Remplit formulaire     │                    │                      │                    │                    │
├───────────────────────>│                    │                      │                    │                    │
│                        │                    │                      │                    │                    │
│ Clique "Rechercher"    │                    │                      │                    │                    │
├───────────────────────>│                    │                      │                    │                    │
│                        │ onSubmit(filters)  │                      │                    │                    │
│                        ├───────────────────>│                      │                    │                    │
│                        │                    │ mutate(filters)      │                    │                    │
│                        │                    ├─────────────────────>│                    │                    │
│                        │                    │                      │ isPending = true   │                    │
│                        │                    │                      ├───────────────────>│                    │
│                        │                    │                      │                    │                    │
│                        │                    │                      │ POST /discover     │                    │
│                        │                    │                      ├───────────────────>│                    │
│                        │                    │                      │                    │ LLM génère prompt  │
│                        │                    │                      │                    │ Parse réponse      │
│                        │                    │                      │                    │                    │
│                        │                    │                      │ Response (JSON)    │                    │
│                        │                    │                      │<───────────────────┤                    │
│                        │                    │                      │                    │                    │
│                        │                    │                      │ data = response    │                    │
│                        │                    │                      │ isPending = false  │                    │
│                        │                    │                      ├───────────────────>│ Cache response     │
│                        │                    │                      │                    │                    │
│                        │ Re-render (data)   │                      │                    │                    │
│ <──────────────────────┼────────────────────┤                      │                    │                    │
│ Affiche ressources     │                    │                      │                    │                    │
```

---

## 🔑 Points clés à retenir

### 1. Séparation des responsabilités

```
DiscoveryForm        = Capture données formulaire (state local)
DiscoveryPage        = Orchestration (hook + affichage)
useDiscoverResources = Logique TanStack Query (mutation)
api.ts               = Appel HTTP vers backend
Backend              = Génération prompt LLM + traitement
```

### 2. Le cache TanStack Query

```tsx
// ❌ Tu n'écris JAMAIS :
localStorage.setItem('discovery', JSON.stringify(data))

// ✅ TanStack Query fait AUTOMATIQUEMENT :
// - Stockage en mémoire (découverte)
// - Gestion des états (isPending, error, data)
// - Re-render des composants quand data change
```

### 3. Flow de données unidirectionnel

```
User Input  →  Form State  →  Mutation  →  API  →  Cache  →  UI Display
(saisie)      (useState)     (mutate)    (POST)  (auto)    (data)
```

---

## 🎯 Exercice de compréhension

**Question 1 :** Où sont stockées les données du formulaire avant l'envoi ?
<details>
<summary>Réponse</summary>
Dans le state local du composant DiscoveryForm via `useState`
</details>

**Question 2 :** Qui appelle réellement l'API backend ?
<details>
<summary>Réponse</summary>
La fonction `discoverResources()` dans api.ts, déclenchée par TanStack Query via `useMutation`
</details>

**Question 3 :** Que fait TanStack Query automatiquement après la réponse API ?
<details>
<summary>Réponse</summary>
- Met à jour `discovery.data` avec la réponse
- Change `discovery.isPending` à false
- Cache la réponse en mémoire
- Re-rend les composants qui utilisent ces données
</details>

**Question 4 :** Si je navigue vers ConfigurationPage puis reviens, les résultats de découverte sont-ils perdus ?
<details>
<summary>Réponse</summary>
Non ! TanStack Query conserve `discovery.data` en cache tant que la page n'est pas rechargée (F5)
</details>

---

## 🚀 Pour aller plus loin

### Options avancées de useMutation

```tsx
export function useDiscoverResources() {
    const queryClient = useQueryClient()
    
    return useMutation({
        mutationFn: (filters) => discoverResources(filters),
        
        // 🎯 Callbacks optionnels
        onSuccess: (data) => {
            console.log('✅ Découverte réussie:', data)
            // Invalider d'autres queries si besoin
            queryClient.invalidateQueries({ queryKey: ['resources'] })
        },
        
        onError: (error) => {
            console.error('❌ Erreur découverte:', error)
        },
        
        onSettled: () => {
            console.log('🏁 Requête terminée (succès ou erreur)')
        }
    })
}
```

### Optimistic Updates (avancé)

```tsx
// Mettre à jour l'UI AVANT la réponse API
// (pour une UX ultra-rapide)
useMutation({
    mutationFn: discoverResources,
    onMutate: async (filters) => {
        // Afficher immédiatement "Recherche en cours..." dans l'UI
        return { optimisticData: "Recherche lancée..." }
    }
})
```

---

## 📚 Ressources complémentaires

- [TanStack Query Docs - Mutations](https://tanstack.com/query/latest/docs/react/guides/mutations)
- [React Hook Form + TanStack Query](https://tanstack.com/query/latest/docs/react/examples/react/react-hook-form)
- [Cache Management](https://tanstack.com/query/latest/docs/react/guides/caching)

---

## ✅ Checklist de compréhension

- [ ] Je comprends la différence entre state local (useState) et cache TanStack Query
- [ ] Je sais quand utiliser `useQuery` vs `useMutation`
- [ ] Je comprends le rôle de `mutate()` et `isPending`
- [ ] Je sais que le cache est automatique (pas de localStorage manuel)
- [ ] Je comprends le flow : Form → Page → Hook → API → Cache → UI
- [ ] Je sais que c'est le backend qui génère le prompt LLM, pas le frontend

---

**🎓 Formateur React - Session Pédagogique complète**
*Créé pour comprendre le workflow de découverte de ressources A→Z*
