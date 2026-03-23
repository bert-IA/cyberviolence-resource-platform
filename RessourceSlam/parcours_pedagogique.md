# Parcours pédagogique — Exercice SLAM

## Vue d'ensemble

Ce parcours se déroule sur **11 semaines**. Vous construisez l'application par couches successives : base de données d'abord, API ensuite, interface en dernier. Chaque semaine s'appuie sur la précédente — ne sautez pas d'étape.

---

## Compétences visées

| Compétence | Semaines |
|-----------|---------|
| Modélisation relationnelle | S1 |
| ORM async (SQLAlchemy + Alembic) | S2–S3 |
| API REST avec FastAPI | S3–S6 |
| Authentification JWT | S5 |
| Contrat API / frontend | S6–S7 |
| Workflow métier multi-étapes | S6 |
| State management React (Context API) | S7–S8 |
| Variables d'environnement et sécurité | S5, S9 |
| Déploiement VPS (Nginx, SSL) | S10–S11 |

---

## Semaine par semaine

### S1 — Modélisation de la base de données

Vous concevez le schéma à partir des besoins métier (voir [contexte_metier.md](contexte_metier.md)).

**Livrable :** un fichier `schema.sql` avec les 4 tables (`languages`, `countries`, `resources`, `workflow_events`) et les index.

Questions à vous poser :
- Quels champs sont obligatoires ? Lesquels peuvent être nuls ?
- Où mettre les contraintes `NOT NULL`, `REFERENCES`, `DEFAULT` ?
- Pourquoi une table `workflow_events` séparée plutôt qu'un champ `status_history` dans `resources` ?

---

### S2 — Mise en place de l'environnement

Vous configurez l'environnement de développement complet.

**Livrables :**
- Docker PostgreSQL fonctionnel
- Projet FastAPI initialisé avec SQLAlchemy async
- Première migration Alembic qui crée les tables

```bash
# Initialiser Alembic dans votre projet
alembic init alembic

# Générer une migration à partir de vos modèles SQLAlchemy
alembic revision --autogenerate -m "create tables"

# Appliquer la migration
alembic upgrade head
```

---

### S3 — Modèles SQLAlchemy et seed

Vous écrivez les modèles Python qui représentent vos tables, puis vous injectez les données de départ.

**Livrables :**
- `models/resource.py`, `models/country.py`, `models/language.py`, `models/workflow_event.py`
- Script `seed.py` qui insère les 50 ressources fictives fournies

Point de vigilance : le modèle SQLAlchemy et le schéma Pydantic sont deux choses différentes. Le modèle SQLAlchemy parle à la BDD. Le schéma Pydantic valide les données entrantes et formate les réponses.

---

### S4 — Premiers endpoints : lecture

Vous implémentez les routes GET avec filtres et pagination.

**Livrables :**
- `GET /resources` avec filtres `?status=`, `?category=`, `?country=`
- `GET /resources/{id}`
- `GET /resources/summary` (comptages par statut)

Vous utilisez `Depends(get_db)` pour injecter la session en base dans chaque endpoint. C'est le pattern standard FastAPI — prenez le temps de le comprendre.

---

### S5 — Authentification JWT

Vous ajoutez la couche d'authentification. Toutes les routes de modification seront protégées.

**Livrables :**
- Table `users` (ou utilisateurs en dur pour commencer)
- `POST /auth/token` → retourne un JWT
- `GET /users/me` → profil de l'utilisateur connecté
- Dépendance `get_current_user` réutilisable dans tous les endpoints protégés

```python
# Dépendance réutilisable
async def get_current_user(token: str = Depends(oauth2_scheme), db = Depends(get_db)):
    payload = jose.jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    user = await db.get(User, payload["sub"])
    if not user:
        raise HTTPException(status_code=401)
    return user
```

**Variables d'environnement :** `SECRET_KEY` et `DATABASE_URL` ne doivent jamais être en dur dans le code. Utilisez un fichier `.env` et la librairie `python-dotenv`. Ajoutez `.env` à votre `.gitignore` immédiatement.

---

### S6 — Endpoints de modification et workflow

Vous implémentez les routes qui font évoluer les ressources dans le workflow.

**Livrables :**
- `PATCH /resources/{id}` — modifier les champs éditables
- `POST /resources/{id}/validate` — faire avancer le statut
- `POST /resources/{id}/reject` — rejeter avec notes
- À chaque transition, un `workflow_event` est inséré en base

Le workflow à implémenter :

```
discovered → geo_pending → geo_validated → critical_pending → critical_validated → rag_ready
                        ↘ geo_rejected                     ↘ critical_rejected
```

Chaque transition est une règle métier. Vous pouvez les encoder dans un dictionnaire :

```python
APPROVE_CHAINS = {
    "geo_pending":      ["geo_validated", "critical_pending"],
    "critical_pending": ["critical_validated", "rag_ready"],
}
REJECT_TARGETS = {
    "geo_pending":      "geo_rejected",
    "critical_pending": "critical_rejected",
}
```

---

### S7 — Contrat API et démarrage du frontend

Vous documentez le contrat entre votre API et le frontend, puis vous initialisez le projet React.

**Livrables :**
- Documentation des endpoints dans `api_contract.md` (URL, méthode, corps, réponse)
- Projet React + Vite initialisé
- Premier appel `fetch()` vers `GET /resources` qui affiche des données à l'écran

Le contrat API est le document que vous vous passeriez si le frontend et le backend étaient développés par des personnes différentes. Soyez précis sur les types et les cas d'erreur.

---

### S8 — AuthContext et routes protégées

Vous implémentez la gestion de l'authentification côté React.

**Livrables :**
- `AuthContext` qui stocke le token et expose `login` / `logout`
- Page `/login` avec formulaire
- `PrivateRoute` qui redirige vers `/login` si pas de token
- Token injecté automatiquement dans tous les appels API

```typescript
// contexts/AuthContext.tsx
export function AuthProvider({ children }: { children: React.ReactNode }) {
    const [token, setToken] = useState<string | null>(
        localStorage.getItem('token')
    )

    const login = async (username: string, password: string) => {
        const res = await fetch('/auth/token', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password }),
        })
        const { access_token } = await res.json()
        setToken(access_token)
        localStorage.setItem('token', access_token)
    }

    const logout = () => {
        setToken(null)
        localStorage.removeItem('token')
    }

    return (
        <AuthContext.Provider value={{ token, login, logout }}>
            {children}
        </AuthContext.Provider>
    )
}
```

---

### S9 — Interface de validation

Vous construisez l'interface principale : la liste des ressources à valider et les actions associées.

**Livrables :**
- Liste des ressources filtrables par statut et catégorie
- Fiche détail avec formulaire d'édition
- Boutons Valider / Rejeter avec confirmation
- Affichage de l'historique des transitions

Utilisez TanStack Query pour gérer les appels API. Il s'occupe du cache, des états de chargement et du rechargement automatique après une mutation.

---

### S10 — Déploiement

Vous mettez l'application en ligne sur le VPS partagé.

**Livrables :**
- Backend FastAPI lancé avec `gunicorn` + `uvicorn workers`
- Frontend buildé et servi par Nginx
- SSL Let's Encrypt configuré
- Variables d'environnement de production dans un `.env` sur le serveur (jamais dans le dépôt)

```bash
# Build du frontend
npm run build
# Les fichiers statiques sont dans dist/ — Nginx les sert directement

# Lancer le backend en production
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 127.0.0.1:8001
```

---

### S11 — Finalisation et bonus

Vous nettoyez, testez et présentez.

**Livrables obligatoires :**
- Tests des endpoints principaux (pytest + httpx)
- README à jour avec instructions d'installation et de lancement

**Bonus (au choix) :**
- Export RAG : `GET /export/rag-ready` qui retourne les ressources finalisées en JSON structuré
- Pagination côté frontend avec TanStack Query
- Recherche full-text PostgreSQL sur le nom et la description

---

## Points de vigilance récurrents

**Ne mettez jamais de secrets dans le code.** `SECRET_KEY`, mots de passe, clés API — tout ça va dans `.env`, jamais dans un fichier versionné.

**Séparez les schémas Pydantic des modèles SQLAlchemy.** Un modèle SQLAlchemy représente une table. Un schéma Pydantic représente ce que l'API accepte ou retourne. Ce sont deux objets distincts même s'ils ont des champs similaires.

**Committez souvent, par petites étapes.** Un commit = une fonctionnalité ou une correction. Vous devez pouvoir revenir en arrière sans perdre plusieurs heures de travail.

**Lisez les messages d'erreur entièrement.** FastAPI et SQLAlchemy produisent des erreurs très détaillées. La réponse est presque toujours dans le message.
