# Contexte métier — Exercice SLAM

## Ce que vous allez construire

Vous allez reconstruire, en version simplifiée, une **plateforme de découverte et de validation de ressources d'aide contre la cyberviolence**.

Concrètement : l'application permet à un administrateur de recenser, qualifier et valider des ressources (associations, lignes d'écoute, plateformes de signalement) disponibles dans différents pays et langues. Une fois validées, ces ressources sont exportées vers un système d'IA externe.

L'application d'origine tourne en production. Vous en implémentez le cœur.

---

## Les acteurs

| Acteur | Rôle |
|--------|------|
| **Admin (votre rôle côté front)** | Découvre, valide et rejette les ressources via l'interface web |
| **LLM (Gemini / OpenRouter)** | Dans l'application complète, découvre automatiquement de nouvelles ressources — **retiré de l'exercice** |
| **Système RAG externe** | Consomme les ressources finalisées pour alimenter un assistant IA — **hors périmètre** |

Dans cet exercice, vous jouez le rôle de l'admin : vous construisez l'API qu'il utilise et l'interface qui l'affiche.

---

## Les ressources

Vous allez gérer trois catégories :

| Catégorie | Description | Exemples |
|-----------|-------------|---------|
| `service_support` | Services nationaux d'aide aux victimes de cyberviolence | 3018 (France), Net Écoute |
| `procedure_plateforme` | Procédures de signalement sur les plateformes digitales | Signalement Instagram, TikTok Safety |
| `signalement_autorite` | Plateformes gouvernementales de signalement | PHAROS (France), BKA (Allemagne) |

Chaque ressource porte des informations de contact (téléphone, URL, lien direct), de périmètre (public cible, type de violence, anonymat) et de gouvernance (officielle ou non).

---

## Pourquoi cet exemple et pas un CRUD classique

**Le domaine a du sens.** Vous comprenez immédiatement à quoi sert ce que vous codez. C'est différent d'un CRUD de gestion de stock.

**La complexité est réelle.** Un workflow de validation multi-étapes, des filtres combinés, un historique d'actions — ce sont des problèmes que vous retrouverez dans tous vos projets professionnels.

**La stack est celle du marché.** PostgreSQL + FastAPI + React, c'est exactement ce que les entreprises utilisent aujourd'hui. Ce que vous acquérez ici est directement transférable.

**Vous voyez la destination.** L'application complète (que vous pouvez explorer dans le dépôt) intègre un pipeline LLM, un système de prompts multi-langue, un moteur de déduplication. Vous n'implémentez pas tout ça — mais vous en voyez le but. Il y a une vraie progression visible.

---

## Ce que vous n'implémentez pas (et pourquoi)

L'exercice retire tout ce qui n'est pas au cœur des apprentissages visés :

| Retiré | Pourquoi |
|--------|----------|
| Pipeline LLM (découverte automatique) | Dépendance externe, complexité infra |
| Système de prompts multi-langue | Hors périmètre SLAM |
| Déduplication automatique | Algorithme métier avancé |
| Export RAG | Optionnel — vous pouvez l'ajouter en bonus |

**Ce que vous implémentez :**
- Le modèle de données complet (ressources, pays, langues)
- Le workflow de validation à plusieurs étapes
- Les endpoints REST avec filtres, pagination et authentification
- L'interface React qui consomme l'API

---

## Données de départ

Un fichier SQL de seed vous est fourni avec **50 ressources fictives** couvrant 5 pays et 3 catégories, réparties dans différents statuts du workflow. Vous avez des données dès le premier jour — vous pouvez tester vos requêtes immédiatement sans attendre d'avoir tout construit.
