# 🎓 Migration React - Plan de Formation

**Apprenant**: Bert  
**Formateur**: GitHub Copilot  
**Approche**: Pédagogique (pas de code sans compréhension)

---

## 🎯 Objectif Global

Migrer l'admin des ressources critiques vers une **SPA React moderne** en apprenant les best practices pas à pas.

---

## 📋 Phase Actuelle : MVP HTML (3-4 jours)

**Statut**: ⏳ À démarrer

### Objectif
Créer `admin_dashboard.html` avec navigation hash-based pour valider le workflow métier avant React.

### Ce qui sera construit
- Interface 1 : Discovery (recherche ressources)
- Interface 2 : Geographic Validation (validation batch par pays)
- Interface 3 : Critical Validation (liste rapide avec actions bulk)
- Interface 5 : RAG Formatting (formatage pour indexation chatbot)

### Apprentissages pour React
- Quelles données fetcher et quand
- Quels composants réutilisables identifier
- Quelle logique métier extraire en custom hooks
- Quel state management (global vs local)

---

## 🚀 Phase Suivante : Migration React

### Jour 1 : Fondations
- [ ] Architecture dossiers (`/components`, `/pages`, `/hooks`, `/services`, `/utils`)
- [ ] Setup projet (Vite vs CRA - choix justifié)
- [ ] Structure composant React (props, state, effects)
- [ ] TypeScript ou JavaScript ? (recommandation avec trade-offs)

### Jour 2 : State Management
- [ ] Choix architecture state (Context API vs Redux vs Zustand)
- [ ] Patterns de state lifting et composition
- [ ] Custom hooks pour logique métier réutilisable
- [ ] Gestion erreurs et loading states

### Jour 3 : Routing & Navigation
- [ ] React Router v6 (routes, nested routes, paramètres)
- [ ] Routes protégées (authentification admin)
- [ ] Layout pattern pour UI cohérente
- [ ] Navigation programmatique et liens

### Jour 4 : Composants & Formulaires
- [ ] Composants réutilisables (Button, Input, Card, Table)
- [ ] Form handling (react-hook-form recommandé)
- [ ] Validation formulaires (zod/yup)
- [ ] Feedback utilisateur (toasts, modals)

### Jour 5 : Intégration API
- [ ] Service layer pour appels API
- [ ] React Query / TanStack Query (recommandé) vs useEffect
- [ ] Gestion cache et invalidation
- [ ] Optimistic updates

### Jour 6 : UI/UX Avancée
- [ ] Bibliothèque UI (Tailwind vs Material-UI vs Chakra - choix justifié)
- [ ] Thème et design tokens
- [ ] Responsive design
- [ ] Animations et transitions

### Jour 7 : Tests & Qualité
- [ ] React Testing Library (tests métier, pas implémentation)
- [ ] Tests composants et hooks
- [ ] Tests d'intégration
- [ ] Coverage et CI/CD

### Jour 8 : Performance & Production
- [ ] Optimisation (React.memo, useMemo, useCallback)
- [ ] Code splitting et lazy loading
- [ ] Build production et analyse bundle
- [ ] Déploiement

---

## 📚 Concepts React Clés à Maîtriser

### Fondamentaux
- [ ] JSX et composition
- [ ] Props et prop drilling
- [ ] State local vs state global
- [ ] Lifecycle et useEffect
- [ ] Event handling

### Hooks Essentiels
- [ ] useState
- [ ] useEffect
- [ ] useContext
- [ ] useReducer
- [ ] useMemo / useCallback
- [ ] Custom hooks

### Patterns Avancés
- [ ] Compound components
- [ ] Render props
- [ ] Higher-Order Components (HOC)
- [ ] Context pattern
- [ ] Provider pattern

---

## 🎓 Méthodologie Pédagogique

### Principes
1. **Comprendre avant coder** : Explication des concepts d'abord
2. **Choix justifiés** : Toujours expliquer le "pourquoi"
3. **Options multiples** : Présenter plusieurs approches avec trade-offs
4. **Questions guidées** : Te faire réfléchir à la solution
5. **Code progressif** : Construire étape par étape
6. **Validation** : Tester et valider chaque étape

### Ce que je fais
✅ Expliquer concepts et patterns  
✅ Montrer plusieurs options  
✅ Poser questions pour te faire réfléchir  
✅ Valider tes choix  
✅ Signaler pièges et erreurs courantes  
✅ Guider vers best practices  

### Ce que je ne fais PAS
❌ Écrire code sans que tu comprennes  
❌ Faire choix techniques à ta place  
❌ Sauter des explications  
❌ Donner solution directe sans réflexion  

---

## 📝 Notes et Décisions

### Décisions Architecturales
_À remplir au fur et à mesure_

**State Management choisi**: ?  
**Router choisi**: React Router v6  
**Bibliothèque UI choisie**: ?  
**TypeScript ou JS**: ?  
**Tests framework**: React Testing Library  

### Questions à Résoudre
- [ ] TypeScript dès le début ou migration progressive ?
- [ ] Authentification : JWT stocké où (localStorage vs cookie) ?
- [ ] Structure API service : axios vs fetch ?
- [ ] Gestion des erreurs : toast vs modal vs inline ?

---

## 🔗 Ressources Utiles

### Documentation Officielle
- [React Docs](https://react.dev) - Nouvelle doc avec hooks first
- [React Router](https://reactrouter.com/en/main)
- [React Testing Library](https://testing-library.com/docs/react-testing-library/intro/)

### Apprentissage
- [React Patterns](https://reactpatterns.com/)
- [Kent C. Dodds Blog](https://kentcdodds.com/blog) - Best practices React

---

## 📊 Suivi de Progression

| Phase | Status | Date Début | Date Fin | Notes |
|-------|--------|------------|----------|-------|
| Jour 0 : Plan | ✅ | 2026-02-10 | 2026-02-10 | Documentation créée |
| MVP HTML | ⏳ | - | - | À démarrer |
| React Jour 1 | ⏸️ | - | - | Après MVP |
| React Jour 2 | ⏸️ | - | - | - |
| React Jour 3 | ⏸️ | - | - | - |
| React Jour 4 | ⏸️ | - | - | - |
| React Jour 5 | ⏸️ | - | - | - |
| React Jour 6 | ⏸️ | - | - | - |
| React Jour 7 | ⏸️ | - | - | - |
| React Jour 8 | ⏸️ | - | - | - |

---

## 💡 Prochaine Action

**Maintenant** : Démarrer MVP HTML ou discuter architecture React cible ?

**Options** :
- **Option A** : Démarrer MVP HTML (valider workflow métier)
- **Option B** : Discuter architecture React (vision globale d'abord)
- **Option C** : Explorer concept React spécifique qui t'inquiète

**Ta décision** : _À compléter_

---

**Dernière mise à jour** : 2026-02-10  
**Prochaine revue** : Après choix de l'option A/B/C
