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
