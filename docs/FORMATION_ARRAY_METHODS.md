# 🎓 Formation : Méthodes de Tableaux JavaScript/React

**Objectif** : Maîtriser `.map()`, `.filter()` et `.reduce()` - les 3 piliers de React !

---

## 📚 Table des matières

1. [`.map()` - Transformer](#1-map---transformer)
2. [`.filter()` - Filtrer](#2-filter---filtrer)  
3. [`.reduce()` - Réduire/Agréger](#3-reduce---réduireagréger)
4. [Chaînage de méthodes](#4-chaînage-de-méthodes)
5. [Exercices pratiques](#5-exercices-pratiques)

---

## 1. `.map()` - Transformer

### 🎯 Concept
**Transformer** chaque élément d'un tableau en un **nouveau tableau de même longueur**.

### 📖 Signature
```typescript
array.map((element, index) => {
  return nouveauElement
})
```

### ✅ Exemple simple : Doubler des nombres
```javascript
const nombres = [1, 2, 3, 4]
const doubles = nombres.map(n => n * 2)

console.log(doubles) // [2, 4, 6, 8]
```

### 🎨 Exemple React : Afficher une liste
```tsx
const fruits = ['Pomme', 'Banane', 'Orange']

return (
  <ul>
    {fruits.map((fruit, index) => (
      <li key={index}>{fruit}</li>
    ))}
  </ul>
)
```

**Résultat HTML** :
```html
<ul>
  <li>Pomme</li>
  <li>Banane</li>
  <li>Orange</li>
</ul>
```

### 🔑 Points clés
- ✅ Retourne un **nouveau tableau** (même longueur)
- ✅ **N'altère pas** le tableau original
- ✅ Toujours utiliser une **`key` unique** en React
- ❌ Ne PAS utiliser pour des effets de bord (préférer `.forEach()`)

### 💡 Quand utiliser `.map()` ?
- ☑️ Afficher une liste en JSX
- ☑️ Transformer des données (ex: extraire une propriété)
- ☑️ Formater des valeurs

---

## 2. `.filter()` - Filtrer

### 🎯 Concept
**Sélectionner** uniquement les éléments qui respectent une **condition**.

### 📖 Signature
```typescript
array.filter((element, index) => {
  return boolean // true = garder, false = éliminer
})
```

### ✅ Exemple simple : Nombres pairs
```javascript
const nombres = [1, 2, 3, 4, 5, 6]
const pairs = nombres.filter(n => n % 2 === 0)

console.log(pairs) // [2, 4, 6]
```

### 🎨 Exemple React : Filtrer des ressources
```tsx
const resources = [
  { id: 1, name: 'A', is_new: true },
  { id: 2, name: 'B', is_new: false },
  { id: 3, name: 'C', is_new: true }
]

const newResources = resources.filter(r => r.is_new)

return (
  <div>
    <h3>Nouvelles ressources : {newResources.length}</h3>
    {newResources.map(r => <Card key={r.id} name={r.name} />)}
  </div>
)
```

### 🔑 Points clés
- ✅ Retourne un **nouveau tableau** (longueur ≤ originale)
- ✅ Teste chaque élément avec une **fonction de prédicat**
- ✅ **N'altère pas** le tableau original
- ⚠️ Si aucun élément ne correspond → tableau vide `[]`

### 💡 Quand utiliser `.filter()` ?
- ☑️ Afficher seulement certains éléments (ex: actifs, validés)
- ☑️ Supprimer les doublons (avec logique personnalisée)
- ☑️ Recherche/filtrage en temps réel

---

## 3. `.reduce()` - Réduire/Agréger

### 🎯 Concept
**Transformer** un tableau en une **seule valeur** (nombre, objet, nouveau tableau).

### 📖 Signature
```typescript
array.reduce((acc, element) => {
  // Logique de transformation
  return acc // Retourner l'accumulateur modifié
}, valeurInitiale)
```

**Paramètres** :
- `acc` = **Accumulateur** (le résultat en construction)
- `element` = **Élément actuel** du tableau
- `valeurInitiale` = Valeur de `acc` à la 1ère itération

### ✅ Exemple simple : Somme de nombres
```javascript
const nombres = [10, 20, 30]

const somme = nombres.reduce((acc, n) => {
  return acc + n
}, 0) // acc commence à 0

console.log(somme) // 60

// Déroulé :
// Itération 1: acc = 0,  n = 10  → retourne 0 + 10 = 10
// Itération 2: acc = 10, n = 20  → retourne 10 + 20 = 30
// Itération 3: acc = 30, n = 30  → retourne 30 + 30 = 60
```

### 🎨 Exemple React : Grouper par catégorie
```typescript
const resources = [
  { name: 'A', category: 'urgent' },
  { name: 'B', category: 'local' },
  { name: 'C', category: 'urgent' }
]

const grouped = resources.reduce((acc, resource) => {
  // Créer la catégorie si elle n'existe pas
  if (!acc[resource.category]) {
    acc[resource.category] = []
  }
  // Ajouter la ressource à sa catégorie
  acc[resource.category].push(resource)
  return acc // ⚠️ CRUCIAL !
}, {} as Record<string, typeof resources>)

console.log(grouped)
// {
//   urgent: [{ name: 'A', ... }, { name: 'C', ... }],
//   local: [{ name: 'B', ... }]
// }
```

### 🔑 Points clés
- ✅ La **valeur initiale** détermine le type de `acc`
  - `0` → Nombre
  - `""` → String
  - `[]` → Tableau
  - `{}` → Objet
- ✅ **TOUJOURS retourner `acc`** à chaque itération
- ⚠️ Plus complexe que `.map()` et `.filter()`, mais très puissant

### 💡 Quand utiliser `.reduce()` ?
- ☑️ Calculer une somme, moyenne, min/max
- ☑️ Grouper par propriété
- ☑️ Transformer structure de données (tableau → objet)
- ☑️ Compter occurrences

---

## 4. Chaînage de méthodes

### 🎯 Concept
Combiner plusieurs méthodes pour des transformations complexes.

### ✅ Exemple : Pipeline de données
```javascript
const users = [
  { name: 'Alice', age: 25, active: true },
  { name: 'Bob', age: 30, active: false },
  { name: 'Charlie', age: 35, active: true },
  { name: 'David', age: 28, active: true }
]

// Objectif : Noms des utilisateurs actifs de plus de 25 ans, en MAJUSCULES
const result = users
  .filter(u => u.active)           // 1. Garder que les actifs
  .filter(u => u.age > 25)         // 2. Garder que > 25 ans
  .map(u => u.name.toUpperCase())  // 3. Extraire noms en majuscules

console.log(result) // ['CHARLIE', 'DAVID']
```

### 🎨 Exemple React : Trier et grouper
```tsx
const resources = [
  { id: 1, name: 'A', category: 'urgent', is_new: true },
  { id: 2, name: 'B', category: 'local', is_new: false },
  { id: 3, name: 'C', category: 'urgent', is_new: true }
]

const categoryOrder = ['urgent', 'local']

// 1. Filtrer nouvelles ressources
const newResources = resources.filter(r => r.is_new)

// 2. Grouper par catégorie
const grouped = newResources.reduce((acc, r) => {
  if (!acc[r.category]) acc[r.category] = []
  acc[r.category].push(r)
  return acc
}, {})

// 3. Transformer en tableau trié
const sorted = categoryOrder
  .map(cat => ({
    category: cat,
    resources: grouped[cat] || []
  }))
  .filter(group => group.resources.length > 0)

// 4. Afficher
return (
  <>
    {sorted.map(group => (
      <div key={group.category}>
        <h3>{group.category}</h3>
        {group.resources.map(r => <Card key={r.id} {...r} />)}
      </div>
    ))}
  </>
)
```

### 🔑 Ordre d'exécution optimal
```
1. .filter()  → Réduire la quantité de données
2. .map()     → Transformer ce qui reste
3. .reduce()  → Agréger si nécessaire
```

---

## 5. Exercices pratiques

### 🏋️ Exercice 1 : `.map()` basique
**Données** :
```javascript
const prices = [10, 25, 50, 100]
```

**Objectif** : Ajouter 20% de TVA à chaque prix.

**Solution attendue** : `[12, 30, 60, 120]`

<details>
<summary>💡 Solution</summary>

```javascript
const pricesWithTVA = prices.map(price => price * 1.2)
```

</details>

---

### 🏋️ Exercice 2 : `.filter()` basique
**Données** :
```javascript
const users = [
  { name: 'Alice', age: 17 },
  { name: 'Bob', age: 22 },
  { name: 'Charlie', age: 16 }
]
```

**Objectif** : Garder uniquement les utilisateurs majeurs (≥ 18 ans).

<details>
<summary>💡 Solution</summary>

```javascript
const adults = users.filter(user => user.age >= 18)
// Résultat : [{ name: 'Bob', age: 22 }]
```

</details>

---

### 🏋️ Exercice 3 : `.reduce()` - Somme
**Données** :
```javascript
const cart = [
  { name: 'Pomme', price: 3 },
  { name: 'Pain', price: 2 },
  { name: 'Lait', price: 1.5 }
]
```

**Objectif** : Calculer le total du panier.

<details>
<summary>💡 Solution</summary>

```javascript
const total = cart.reduce((acc, item) => acc + item.price, 0)
// Résultat : 6.5
```

</details>

---

### 🏋️ Exercice 4 : `.reduce()` - Grouper
**Données** :
```javascript
const animals = [
  { name: 'Chat', type: 'mammifère' },
  { name: 'Aigle', type: 'oiseau' },
  { name: 'Chien', type: 'mammifère' },
  { name: 'Moineau', type: 'oiseau' }
]
```

**Objectif** : Grouper par `type`.

**Résultat attendu** :
```javascript
{
  mammifère: [{ name: 'Chat', ... }, { name: 'Chien', ... }],
  oiseau: [{ name: 'Aigle', ... }, { name: 'Moineau', ... }]
}
```

<details>
<summary>💡 Solution</summary>

```javascript
const grouped = animals.reduce((acc, animal) => {
  if (!acc[animal.type]) {
    acc[animal.type] = []
  }
  acc[animal.type].push(animal)
  return acc
}, {})
```

</details>

---

### 🏋️ Exercice 5 : Chaînage complet
**Données** :
```javascript
const products = [
  { name: 'Laptop', price: 1000, stock: 5, available: true },
  { name: 'Mouse', price: 20, stock: 0, available: true },
  { name: 'Keyboard', price: 50, stock: 10, available: false },
  { name: 'Monitor', price: 300, stock: 3, available: true }
]
```

**Objectif** : 
1. Garder seulement les produits disponibles (`available: true`)
2. Garder seulement ceux en stock (`stock > 0`)
3. Extraire uniquement les noms
4. Trier par ordre alphabétique

**Résultat attendu** : `['Laptop', 'Monitor']`

<details>
<summary>💡 Solution</summary>

```javascript
const result = products
  .filter(p => p.available)
  .filter(p => p.stock > 0)
  .map(p => p.name)
  .sort()
```

</details>

---

## 🎓 Récapitulatif

| Méthode | Retourne | Longueur | Usage principal |
|---------|----------|----------|-----------------|
| `.map()` | Nouveau tableau | **Identique** | Transformation 1-1 |
| `.filter()` | Nouveau tableau | **≤ original** | Sélection conditionnelle |
| `.reduce()` | **N'importe quoi** | **1 valeur** | Agrégation/Groupement |

### 🚀 Prochaines étapes

1. **Pratiquez** chaque exercice dans la console de votre navigateur
2. **Réécrivez** votre `DiscoveredResourcesList.tsx` en comprenant chaque ligne
3. **Expérimentez** avec vos propres données

**Questions ?** Relisez la section concernée et testez les exemples ! 💪

---

**Auteur** : Formation React - Expert Pédagogue  
**Date** : 2026  
**Licence** : Usage pédagogique libre
