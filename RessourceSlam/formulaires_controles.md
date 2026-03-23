# Les formulaires contrôlés en React

## Le problème de base

En HTML classique, un `<input>` gère lui-même sa valeur. Vous tapez "Bonjour" dans un champ, la valeur "Bonjour" existe dans le DOM — mais React n'en sait rien. Si vous demandez à React "quelle est la valeur de ce champ ?", il ne peut pas vous répondre.

C'est un problème parce que React est censé être **la seule source de vérité** de votre interface.

---

## La solution : relier l'input à un état React

Un formulaire contrôlé, c'est un formulaire où **chaque champ est connecté à un `useState`**. React contrôle la valeur, d'où le nom.

```tsx
function MonFormulaire() {
    const [nom, setNom] = useState('')

    return (
        <input
            value={nom}                          // ← React impose la valeur
            onChange={(e) => setNom(e.target.value)}  // ← React met à jour à chaque frappe
        />
    )
}
```

Ce qui se passe à chaque frappe :
1. L'utilisateur tape une lettre
2. `onChange` se déclenche
3. `setNom` met à jour l'état
4. React re-rend le composant avec la nouvelle valeur dans `value`

L'input n'a pas de mémoire propre — c'est React qui tient à jour la valeur.

---

## Le cas pratique : édition d'une ressource existante

Dans votre page RAG, vous ne partez pas d'un formulaire vide. Vous chargez une ressource depuis l'API, et vous initialisez le formulaire avec ses valeurs existantes.

```tsx
function ResourceForm({ resource }: { resource: Resource }) {
    const [form, setForm] = useState({
        name: resource.name,
        description: resource.description,
        direct_link: resource.direct_link,
        phone: resource.phone ?? '',
    })

    const handleChange = (field: string, value: string) => {
        setForm(prev => ({ ...prev, [field]: value }))
    }

    return (
        <div>
            <input
                value={form.name}
                onChange={(e) => handleChange('name', e.target.value)}
            />
            <textarea
                value={form.description}
                onChange={(e) => handleChange('description', e.target.value)}
            />
            {/* etc. */}
        </div>
    )
}
```

`setForm(prev => ({ ...prev, [field]: value }))` — cette ligne mérite d'être comprise :
- `prev` = l'état actuel du formulaire (tous les champs)
- `{ ...prev }` = on copie tous les champs existants
- `[field]: value` = on écrase uniquement le champ qui a changé

---

## Le piège classique : initialiser depuis une prop qui arrive en retard

Si la ressource est chargée de manière asynchrone, `resource` peut être `undefined` au premier rendu. Il faut gérer ce cas :

```tsx
function ResourceForm({ resource }: { resource: Resource | null }) {
    const [form, setForm] = useState<Record<string, string> | null>(null)

    // useEffect se déclenche quand resource arrive
    useEffect(() => {
        if (resource) {
            setForm({
                name: resource.name,
                description: resource.description,
                direct_link: resource.direct_link,
                phone: resource.phone ?? '',
            })
        }
    }, [resource])  // ← se relance si resource change (ex: on sélectionne une autre ressource)

    if (!form) return <p>Chargement…</p>

    // ... rendu du formulaire
}
```

Le `[resource]` dans le tableau de dépendances du `useEffect` est crucial : si l'utilisateur sélectionne une autre ressource dans la liste, le formulaire se réinitialise avec les nouvelles valeurs.

---

## Détecter les modifications non sauvegardées

Vous pouvez comparer l'état actuel du formulaire avec les valeurs d'origine pour savoir si quelque chose a changé :

```tsx
const hasChanges = resource && form && (
    form.name !== resource.name ||
    form.description !== resource.description ||
    form.direct_link !== resource.direct_link
)

// Puis dans le rendu :
{hasChanges && <span className="text-orange-500">● Modifications non sauvegardées</span>}
```

---

## Ce qu'on envoie à l'API

À la validation, on envoie les valeurs du formulaire via `PATCH /sources/{id}`, puis on appelle `POST /sources/{id}/validate`.

```tsx
const handleSaveAndValidate = async () => {
    // 1. Sauvegarder les modifications si nécessaire
    if (hasChanges) {
        await patchResource(resource.id, form)
    }
    // 2. Valider la ressource
    await validateResource(resource.id)
}
```

Ces deux opérations sont séquentielles — vous ne pouvez pas valider avant que le PATCH soit terminé.

---

## Résumé

| Concept | Ce que ça veut dire |
|---------|-------------------|
| Formulaire contrôlé | Chaque `<input>` a un `value=` et un `onChange=` |
| Source de vérité | L'état React, pas le DOM |
| Initialisation depuis l'API | `useEffect` + `setState` quand la donnée arrive |
| `[resource]` en dépendance | Le formulaire se réinitialise si on change de ressource |
| Détection de changements | Comparaison avant/après pour afficher un indicateur |

---

---

# Le composant Modal en React

## Qu'est-ce qu'un modal ?

Un modal est une fenêtre qui s'affiche **par-dessus** le reste de la page. Pendant qu'il est ouvert, l'utilisateur ne peut pas interagir avec le contenu en dessous — le modal capte toute l'attention.

Exemples : confirmation de suppression, formulaire d'édition, aperçu détaillé.

---

## Comment React affiche un modal

Un modal n'est **pas** une page séparée ni une route. C'est un composant conditionnel rendu dans le même arbre React, avec un positionnement CSS qui lui permet de couvrir tout l'écran.

La logique est simple :

```tsx
// Dans le composant parent
{selectedResource !== null && (
    <MonModal resource={selectedResource} onClose={() => setSelectedResource(null)} />
)}
```

Quand `selectedResource` est `null` → le modal n'existe pas dans le DOM.  
Quand `selectedResource` contient une ressource → le modal apparaît.

---

## La structure CSS d'un modal

Un modal est composé de deux couches :

**Couche 1 — l'overlay** : un div qui couvre toute la fenêtre, semi-transparent, pour obscurcir le fond.
```
position: fixed    → couvre tout, ignore le scroll
inset: 0           → de 0 à 0 sur tous les côtés (haut, bas, gauche, droite)
z-index élevé      → s'affiche au-dessus de tout
fond semi-transparent
```

**Couche 2 — la boîte de dialogue** : le contenu visible, centré dans l'overlay.
```
background blanc
padding, border-radius
overflow-y: auto   → scrollable si le contenu est long
largeur max définie
```

En Tailwind, l'overlay ressemble à :
```
fixed inset-0 bg-black/50 flex items-center justify-center z-50
```

---

## Les props d'un modal de validation

Un modal reçoit tout ce dont il a besoin depuis son parent — il ne fetch rien lui-même.

Props typiques pour `RagValidationModal` :

| Prop | Type | Rôle |
|---|---|---|
| `resource` | `Resource` | La ressource à afficher/éditer |
| `onClose` | `() => void` | Appelé quand l'utilisateur ferme le modal |
| `onValidate` | `(id: string) => void` | Appelé quand l'utilisateur clique "Valider" |
| `onReject` | `(id: string) => void` | Appelé quand l'utilisateur clique "Rejeter" |

Le modal **ne gère pas** les mutations directement — il délègue au parent via les callbacks.  
Sauf `usePatchResource` — les modifications du formulaire sont locales au modal.

---

## Le cycle de vie du modal dans ce projet

1. Utilisateur clique "Voir détails" sur une `ResourceCard`
2. `setSelectedResource(resource)` dans `RagPage`
3. `selectedResource !== null` → `RagValidationModal` est monté
4. `useEffect([resource])` initialise le formulaire avec les valeurs de la ressource
5. Utilisateur modifie des champs → état local du formulaire mis à jour
6. Utilisateur clique "Valider" :
   - Si des champs ont changé → `patchMutation.mutate(...)` d'abord
   - Puis `onValidate(resource.id)` est appelé → géré par `RagPage`
7. `onValidate` appelle `validateMutation.mutate(id)` dans `RagPage`
8. `onSuccess` → `setSelectedResource(null)` → modal démonté
9. La liste se rafraîchit, la ressource disparaît de la liste

---

## Fermer le modal en cliquant sur l'overlay

Pattern classique : cliquer sur le fond sombre ferme le modal, mais cliquer sur la boîte elle-même ne le ferme pas.

```tsx
// Sur l'overlay : ferme le modal
<div onClick={onClose}>
    {/* Sur la boîte : stoppe la propagation du clic */}
    <div onClick={(e) => e.stopPropagation()}>
        {/* contenu */}
    </div>
</div>
```

`e.stopPropagation()` empêche le clic sur la boîte de "remonter" jusqu'à l'overlay.

---

## Résumé modal

| Concept | Ce que ça veut dire |
|---|---|
| Affichage conditionnel | `{selectedResource && <Modal />}` |
| Overlay | `fixed inset-0` couvre tout l'écran |
| `stopPropagation` | Clic sur la boîte ne ferme pas le modal |
| Props callbacks | Le modal délègue valider/rejeter au parent |
| `useEffect([resource])` | Formulaire réinitialisé à chaque ouverture |

---

---

# Le Context API React

## Pourquoi le Context API ?

Dans une application React, les données circulent normalement **de parent à enfant** via les props. Ça fonctionne bien pour 1 ou 2 niveaux, mais quand une donnée doit traverser 5 composants pour atteindre le bon endroit, on parle de **prop drilling** — passer une prop à travers tous les intermédiaires même s'ils ne l'utilisent pas.

```
App
 └── MainLayout  (reçoit user, ne l'utilise pas)
       └── Sidebar  (reçoit user, ne l'utilise pas)
             └── UserAvatar  (utilise user ← le seul qui en a besoin)
```

Le **Context API** résout ça : il permet de rendre une valeur accessible à **n'importe quel composant de l'arbre**, sans la passer manuellement à chaque étage.

---

## Les 3 instructions à connaître

### 1. `createContext` — créer le contexte

```tsx
import { createContext } from 'react'

// On définit la forme des données du contexte
interface AuthContextType {
    token: string | null
    login: (password: string) => Promise<boolean>
    logout: () => void
}

// On crée le contexte avec une valeur par défaut
export const AuthContext = createContext<AuthContextType | null>(null)
```

`createContext` crée un "canal de communication" global. La valeur par défaut ne sert que si un composant consomme le contexte sans avoir de Provider au-dessus — en pratique on la met à `null` et on gère ce cas.

---

### 2. `Provider` — distribuer la valeur

Le Provider est le composant qui **fournit** la valeur à tous ses enfants. Il se place haut dans l'arbre (souvent dans `main.tsx` ou `App.tsx`) pour que toute l'app y ait accès.

```tsx
export function AuthProvider({ children }: { children: React.ReactNode }) {
    const [token, setToken] = useState<string | null>(
        localStorage.getItem('admin_token')  // persistance entre les rechargements
    )

    const login = async (password: string): Promise<boolean> => {
        // On vérifie le mot de passe en appelant le backend
        const response = await fetch('http://localhost:8000/health', {
            headers: { Authorization: `Bearer ${password}` }
        })
        if (response.ok) {
            setToken(password)
            localStorage.setItem('admin_token', password)
            return true
        }
        return false
    }

    const logout = () => {
        setToken(null)
        localStorage.removeItem('admin_token')
    }

    return (
        <AuthContext.Provider value={{ token, login, logout }}>
            {children}
        </AuthContext.Provider>
    )
}
```

---

### 3. `useContext` — consommer la valeur

N'importe quel composant enfant peut lire la valeur du contexte avec `useContext` :

```tsx
import { useContext } from 'react'
import { AuthContext } from '../contexts/AuthContext'

function Sidebar() {
    const auth = useContext(AuthContext)

    return (
        <button onClick={auth?.logout}>
            Se déconnecter
        </button>
    )
}
```

En pratique, on crée un **hook personnalisé** pour encapsuler `useContext` et gérer le cas null :

```tsx
export function useAuth() {
    const context = useContext(AuthContext)
    if (!context) throw new Error('useAuth doit être utilisé dans AuthProvider')
    return context
}

// Utilisation dans un composant :
const { token, login, logout } = useAuth()
```

---

## Ce qui va se passer dans l'application

Le faux login de `resource-discovery-platform` va fonctionner ainsi :

### Flux de connexion

```
App démarre
    │
    ├── AuthProvider lit localStorage
    │       ├── token présent → utilisateur déjà connecté
    │       └── pas de token → redirection LoginPage
    │
    ▼
LoginPage
    ├── Formulaire : champ mot de passe
    └── handleSubmit()
            │
            ▼
        login(password)  [dans AuthContext]
            ├── GET /health avec Authorization: Bearer <password>
            ├── 200 OK → token stocké dans state + localStorage → redirect /
            └── 401/erreur → toast.error('Mot de passe incorrect')
```

### Flux de protection des routes

```tsx
// ProtectedRoute : redirige vers /login si pas de token
function ProtectedRoute() {
    const { token } = useAuth()
    return token ? <Outlet /> : <Navigate to="/login" />
}

// Dans App.tsx :
<Route element={<ProtectedRoute />}>
    <Route element={<MainLayout />}>
        <Route path="/" element={<MenuPage />} />
        <Route path="/rag" element={<RagPage />} />
        {/* toutes les routes protégées */}
    </Route>
</Route>
```

### Ce qui change dans `api.ts`

Au lieu du token hardcodé :
```ts
// Avant
export const AUTH_TOKEN = 'Bearer admin-token-2024'

// Après : on lit le token depuis le localStorage
export const getAuthHeader = () => ({
    Authorization: `Bearer ${localStorage.getItem('admin_token') ?? ''}`
})
```

### Résumé des fichiers à créer/modifier

| Fichier | Action | Rôle |
|---------|--------|------|
| `src/contexts/AuthContext.tsx` | Créer | Contexte + Provider + `useAuth` hook |
| `src/pages/LoginPage.tsx` | Créer | Formulaire mot de passe |
| `src/components/layout/ProtectedRoute.tsx` | Créer | Garde les routes privées |
| `src/App.tsx` | Modifier | Entourer les routes avec `AuthProvider` + `ProtectedRoute` |
| `src/services/api.ts` | Modifier | Remplacer `AUTH_TOKEN` par `getAuthHeader()` |
