# Architecture technique — Exercice SLAM

## Vue d'ensemble

L'application que vous allez construire suit une architecture **3-tiers classique** : votre navigateur ne parle jamais directement à la base de données. Toute la logique métier et l'accès aux données passent par l'API.

```
Navigateur (React + Vite)       ← vous codez l'interface ici
        │
        │  HTTP / fetch()  — JSON
        ▼
API REST (FastAPI — Python)     ← vous codez les endpoints ici
        │
        │  SQLAlchemy (ORM async)
        ▼
Base de données (PostgreSQL)    ← vous modélisez le schéma ici
```

Chaque couche a une responsabilité unique. Si vous trouvez que votre frontend contient de la logique métier, ou que votre BDD contient des calculs — c'est un signal que quelque chose n'est pas au bon endroit.

---

## Ton environnement de développement

### Mise en route locale

Vous faites tourner les trois couches en local :

```bash
# PostgreSQL via Docker (pas besoin d'installer PostgreSQL sur votre machine)
docker run -e POSTGRES_PASSWORD=dev -p 5432:5432 postgres:16

# Backend FastAPI
cd backend && uvicorn main:app --reload

# Frontend React
cd frontend && npm run dev
```

### Déploiement (VPS partagé par groupe)

Pour la mise en production, votre groupe partage un serveur avec les autres groupes :

```
VPS — 2 vCPU / 4 Go RAM (Hetzner CX22 ≈ 4 €/mois)
  ├── PostgreSQL 16
  │     └── 1 base par groupe  (ex: slam_groupe_a, slam_groupe_b)
  ├── FastAPI — 1 instance par groupe (ports 8001, 8002…)
  └── Nginx — reverse proxy + SSL Let's Encrypt
              /groupe-a/ → localhost:8001
              /groupe-b/ → localhost:8002
```

Ce n'est pas un détail : configurer Nginx et SSL sur un vrai serveur, c'est ce que vous ferez en entreprise. Profitez de l'exercice pour le faire une première fois dans un contexte encadré.

---

## Base de données

### Pourquoi PostgreSQL et pas SQLite

SQLite serait techniquement suffisant pour ce volume de données. On choisit PostgreSQL parce qu'il vous oblige à acquérir des automatismes réels : connexion distante, variables d'environnement, droits utilisateurs, chaîne de connexion. Ce sont des gestes que vous répéterez sur tous vos projets pro — autant les apprendre maintenant.

### Schéma — 4 tables

```sql
-- Langues
CREATE TABLE languages (
    code         VARCHAR(5)   PRIMARY KEY,   -- FR, EN, JA
    name         TEXT         NOT NULL,
    search_terms JSONB                        -- termes de recherche associés
);

-- Pays (reliés à une langue principale)
CREATE TABLE countries (
    code          VARCHAR(3)  PRIMARY KEY,   -- FR, DE, INTER
    name          TEXT        NOT NULL,
    flag          VARCHAR(10),
    language_code VARCHAR(5)  REFERENCES languages(code)
);

-- Ressources — table centrale
CREATE TABLE resources (
    id               TEXT        PRIMARY KEY,
    name             TEXT        NOT NULL,
    description      TEXT,
    website          TEXT,
    direct_link      TEXT,
    phone            TEXT,
    email            TEXT,
    country_code     VARCHAR(3)  REFERENCES countries(code),
    language_code    VARCHAR(5)  REFERENCES languages(code),
    category         TEXT        NOT NULL,   -- service_support | procedure_plateforme | signalement_autorite
    action_type      TEXT,
    is_governmental  BOOLEAN     DEFAULT FALSE,
    scope_audience   TEXT,
    scope_violence   TEXT,
    scope_anonymous  BOOLEAN     DEFAULT FALSE,
    confidence_score FLOAT       DEFAULT 0.0,
    workflow_status  TEXT        NOT NULL DEFAULT 'discovered',
    created_at       TIMESTAMP   DEFAULT CURRENT_TIMESTAMP,
    finalized_at     TIMESTAMP
);

-- Historique des transitions de workflow
CREATE TABLE workflow_events (
    id          SERIAL      PRIMARY KEY,
    resource_id TEXT        REFERENCES resources(id) ON DELETE CASCADE,
    from_status TEXT,
    to_status   TEXT        NOT NULL,
    admin_id    TEXT,
    notes       TEXT,
    created_at  TIMESTAMP   DEFAULT CURRENT_TIMESTAMP
);
```

### Pourquoi pas d'héritage de tables

Les 3 catégories de ressources partagent 95 % des colonnes. L'héritage de table (pattern CTI ou table inheritance PostgreSQL) ajouterait de la complexité pour un gain marginal. Une colonne `category` + quelques colonnes nullables suffisent. L'héritage serait justifié si chaque sous-type avait des dizaines de champs spécifiques — ce n'est pas le cas ici.

### Index utiles

```sql
-- Les filtres les plus fréquents
CREATE INDEX idx_resources_status   ON resources(workflow_status);
CREATE INDEX idx_resources_category ON resources(category);
CREATE INDEX idx_resources_country  ON resources(country_code);
```

---

## Stack backend

| Composant | Technologie | Rôle |
|-----------|------------|------|
| Framework API | FastAPI | Routing, validation, doc auto Swagger |
| ORM | SQLAlchemy 2 (async) | Accès BDD, modèles Python |
| Driver | asyncpg | Connexion async PostgreSQL |
| Migrations | Alembic | Versioning du schéma BDD |
| Auth | python-jose + passlib | Génération et vérification JWT |
| Validation | Pydantic v2 | Schémas des requêtes et réponses |

```
pip install fastapi sqlalchemy[asyncio] asyncpg alembic
pip install python-jose passlib[bcrypt] pydantic
```

### Connexion à la BDD

```python
# core/database.py
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "postgresql+asyncpg://user:password@localhost/slam_db"

engine = create_async_engine(DATABASE_URL)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
```

Les endpoints reçoivent la session via `Depends(get_db)` — pattern standard FastAPI.

### Authentification JWT

```
POST /auth/token   ← login (username + password → JWT)
GET  /users/me     ← profil de l'utilisateur connecté

Header pour toutes les routes protégées :
Authorization: Bearer <token>
```

---

## Stack frontend

| Composant | Technologie | Rôle |
|-----------|------------|------|
| Framework | React 18 | UI composants |
| Build | Vite | Dev server + bundler |
| Routing | React Router v6 | Navigation SPA |
| Requêtes | TanStack Query | Cache, loading states, refetch |
| Auth | Context API | Token global, protection des routes |
| Styles | Tailwind CSS | Utilitaire CSS |

### AuthContext — pattern essentiel

```typescript
// contexts/AuthContext.tsx
const AuthContext = createContext<AuthContextType | null>(null)

export function AuthProvider({ children }) {
    const [token, setToken] = useState<string | null>(
        localStorage.getItem('token')
    )

    const login = async (username: string, password: string) => {
        const res = await fetch('/auth/token', {
            method: 'POST',
            body: JSON.stringify({ username, password })
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

export const useAuth = () => useContext(AuthContext)
```

Le token stocké dans le Context est injecté dans chaque requête. Les routes protégées redirigent vers `/login` si le token est absent.

---

## Choix Next.js vs React seul

Next.js n'est **pas recommandé** pour cet exercice. La confusion est fréquente : Next.js permet d'accéder à la BDD directement depuis les Server Components, sans API séparée. Mais ce n'est pas ce modèle ici. On a une API FastAPI indépendante — React n'a donc pas besoin de Next.js. Ajouter Next.js introduirait une complexité (SSR, routing file-based, Server vs Client components) qui masquerait les concepts fondamentaux à enseigner : séparation frontend/backend, contrat API, AuthContext.

**Règle simple :** Next.js si pas d'API séparée ou si SEO critique. React + Vite si API REST existante ou exercice pédagogique.
