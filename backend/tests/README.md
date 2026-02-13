# 🧪 Tests API Configuration

Tests automatisés pour valider les routes CRUD de configuration pays/langues.

## Prérequis

```bash
pip install requests
```

## Démarrer le backend

**Terminal 1 - Démarrer le serveur** :
```bash
cd /home/bert/resource-discovery-platform/backend
source venv/bin/activate  # Si tu utilises un venv
python admin_api.py
# Ou: uvicorn admin_api:app --reload --port 8001
```

## Exécuter les tests

**Terminal 2 - Lancer les tests** :
```bash
cd /home/bert/resource-discovery-platform/backend
python tests/test_config_api.py
```

## Tests inclus

1. ✅ **GET** `/admin/config/countries-languages` - Récupérer toute la config
2. ✅ **GET** `/admin/config/countries-languages/FR` - Config langue spécifique
3. ✅ **POST** `/admin/config/countries-languages/FR/countries` - Ajouter pays
4. ✅ **PUT** `/admin/config/countries-languages/IT` - Mettre à jour langue
5. ✅ **DELETE** `/admin/config/countries-languages/FR/countries/MC` - Supprimer pays
6. ✅ **GET** `/admin/config/stats` - Statistiques
7. ✅ **PUT** `/admin/config/countries-languages/TEST` - Créer nouvelle langue
8. ✅ **DELETE** `/admin/config/countries-languages/TEST` - Supprimer langue
9. ✅ **Validation** - Test limite 5 pays par langue

## Résultat attendu

```
============================================================
  🧪 TESTS API Configuration Pays/Langues
  📡 Backend: http://localhost:8001
============================================================

✅ Backend accessible ✅

============================================================
  TEST 1: GET /admin/config/countries-languages
============================================================

✅ Configuration récupérée
ℹ️  Langues: 6
ℹ️  Pays total: 27
  • FR: Français - 5 pays
  • EN: English - 5 pays
  • ES: Español - 5 pays
  • IT: Italiano - 3 pays
  • DE: Deutsch - 3 pays
  • PT: Português - 2 pays

[...tests 2-9...]

============================================================
  RÉSUMÉ DES TESTS
============================================================

✅ PASS - Récupérer toute la config
✅ PASS - Récupérer config langue FR
✅ PASS - Ajouter pays Monaco à FR
✅ PASS - Mettre à jour langue IT
✅ PASS - Supprimer pays MC de FR
✅ PASS - Récupérer statistiques
✅ PASS - Créer nouvelle langue TEST
✅ PASS - Supprimer langue TEST
✅ PASS - Validation limite 5 pays

============================================================
  Résultat: 9/9 tests réussis (100%)
============================================================
```

## Tests avec curl (alternatif)

Si tu préfères tester manuellement avec curl :

```bash
# 1. Récupérer toute la config
curl -H "Authorization: Bearer dev_token_123" \
  http://localhost:8001/admin/config/countries-languages | jq

# 2. Récupérer config FR
curl -H "Authorization: Bearer dev_token_123" \
  http://localhost:8001/admin/config/countries-languages/FR | jq

# 3. Ajouter un pays
curl -X POST -H "Authorization: Bearer dev_token_123" \
  -H "Content-Type: application/json" \
  -d '{
    "country_name": "Monaco",
    "country_code": "MC",
    "flag": "🇲🇨",
    "search_terms": ["cyberviolence", "harcèlement"],
    "search_terms_count": 2,
    "organizations_count": 3
  }' \
  http://localhost:8001/admin/config/countries-languages/FR/countries | jq

# 4. Statistiques
curl -H "Authorization: Bearer dev_token_123" \
  http://localhost:8001/admin/config/stats | jq
```

## Configuration

Si ton serveur tourne sur un autre port ou avec un autre token :

```python
# Modifier dans test_config_api.py
BASE_URL = "http://localhost:VOTRE_PORT"
TOKEN = "VOTRE_TOKEN"  # Voir constants.py → ADMIN_TOKEN_DEV
```

## Troubleshooting

### ❌ Backend inaccessible
```
Solution: Démarrer le serveur
cd backend && python admin_api.py
```

### ❌ 401 Unauthorized
```
Solution: Vérifier le token dans constants.py
TOKEN doit correspondre à ADMIN_TOKEN_DEV
```

### ❌ Module 'requests' not found
```bash
pip install requests
```

## Documentation API

Une fois le backend démarré, accéder à :
- Swagger UI: http://localhost:8001/docs
- ReDoc: http://localhost:8001/redoc
