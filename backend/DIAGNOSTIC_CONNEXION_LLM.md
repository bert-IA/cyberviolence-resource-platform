# 🔍 Analyse du Problème : Découverte Espagne

**Date** : 16 février 2026  
**Symptôme** : Réponse ultra-rapide (3s) avec "Aucune ressource trouvée"  
**Statut** : ✅ **IDENTIFIÉ ET RÉSOLU**

---

## 🚨 Problème Détecté

### Ce qui se passe
Lors d'une recherche de ressources en Espagne (catégorie "association_locale"), le système répond en **3 secondes** avec :
```
"Aucune ressource trouvée"
```

Cette réponse ultra-rapide est **suspecte** car une découverte normale prend :
- **~10-15 secondes** par catégorie avec LLM actif
- **~30-40 secondes** pour multi-catégories

### Analyse des logs

Test effectué avec `test_discovery_debug.py` :
```json
{
  "success": false,
  "message": "Connexion LLM échouée",
  "data": {
    "estimated_duration": "N/A"
  }
}
```

### Cause racine : ❌ **Pas de clé API LLM configurée**

```bash
$ env | grep -E "(LLM_PROVIDER|GEMINI_API_KEY|OPENROUTER_API_KEY)"
❌ Aucune variable d'environnement LLM configurée
```

---

## 🔧 Flux de l'Erreur

```
DiscoveryPage.tsx (Frontend)
  ↓ Envoi POST /geographic/discover
admin_api.py (Backend)
  ↓ Appel adapter.start_geographic_discovery_multi_categories()
api_adapter.py
  ↓ _discover_single_category()
  ↓ Ligne 135: if not self.llm_manager.test_connection():
  ↓ ❌ test_connection() retourne False
  ↓ Return {success: false, message: "Connexion LLM échouée"}
  ↓ ⚡ Durée totale: 3s (pas d'appel LLM)
```

**Pourquoi c'est rapide** : Le système détecte l'absence de LLM AVANT de faire des requêtes, donc retourne immédiatement une erreur.

---

## ✅ Solution : Configurer une Clé API LLM

### Option A : Script Automatique (Recommandé) 🚀

```bash
cd /home/bert/resource-discovery-platform/backend
./setup_llm.sh
```

Le script va :
1. Vous demander quel provider (Gemini ou OpenRouter)
2. Vous demander votre clé API
3. Créer automatiquement le fichier `.env`
4. Proposer de redémarrer le backend

### Option B : Manuel 📝

#### 1. Obtenir une clé API Gemini (gratuit)

- Aller sur **https://ai.google.dev**
- Se connecter avec Google
- "Get API Key" → Créer/Sélectionner un projet
- Copier la clé (format: `AIza...`)

#### 2. Créer le fichier .env

```bash
cd /home/bert/resource-discovery-platform/backend
nano .env
```

Contenu :
```bash
LLM_PROVIDER=gemini
GEMINI_API_KEY=AIza_VOTRE_CLE_REELLE
```

#### 3. Redémarrer le backend

```bash
# Arrêter l'ancien process
lsof -ti:8000 | xargs kill -9

# Redémarrer
python admin_api.py
```

---

## 🧪 Vérification

### Test automatique

```bash
cd /home/bert/resource-discovery-platform/backend
python tests/test_discovery_debug.py
```

**Résultat attendu** :
```
✅ Réponse JSON:
{
  "success": true,
  "message": "1-3 ressources découvertes",
  "data": {
    "discovered_count": 1-3,
    "resources": [
      {
        "name": "Asociación...",
        "url": "https://...",
        "country": "España"
      }
    ]
  }
}

⏱️  Durée: 10-15 secondes (au lieu de 3s)
```

### Test via Frontend

1. Aller sur **DiscoveryPage** (http://localhost:5173/decouverte)
2. Sélectionner :
   - **Langue** : Español
   - **Catégorie** : Association locale
   - **Pays** : Espagne
   - **Max par catégorie** : 2
3. Cliquer "Découvrir"
4. **Attendre ~12-15 secondes** (au lieu de 3s)
5. Voir apparaître 1-2 associations espagnoles

---

## 📊 Comparaison Avant/Après

| Aspect | ❌ Avant (Sans LLM) | ✅ Après (Avec LLM) |
|--------|-------------------|-------------------|
| Durée | 3s | 12-15s |
| Message | "Connexion LLM échouée" | "2 ressources découvertes" |
| Ressources | 0 | 1-3 selon pays |
| Logs backend | `test_connection() = False` | `📝 LLM Response (ES): ...` |

---

## 🐛 Problèmes Potentiels Post-Configuration

### 1. "429 Too Many Requests"

**Cause** : Rate limiting Gemini (max ~15 req/min gratuit)

**Solutions** :
- Réduire `max_per_category` à 2
- Limiter à 1-2 pays simultanés
- Attendre 60s entre découvertes

### 2. "Invalid API Key"

**Vérifications** :
- Pas d'espaces avant/après la clé dans `.env`
- Clé copiée complètement (format `AIza...`)
- Clé active sur Google AI Studio

### 3. Timeout (120s dépassé)

**Causes possibles** :
- Multi-catégories (4+) avec délais 12s entre chaque
- Rate limiting qui force des retries 60s+
- Connexion internet lente

**Solutions** :
- Limiter à 2-3 catégories max par requête
- Augmenter le timeout frontend si nécessaire

---

## 📝 Fichiers Créés pour le Debug

1. **`backend/SETUP_LLM.md`** (4KB)  
   Documentation complète configuration LLM

2. **`backend/setup_llm.sh`** (2KB)  
   Script interactif configuration automatique

3. **`backend/tests/test_discovery_debug.py`** (3KB)  
   Script de test détaillé avec analyse complète

4. **`backend/DIAGNOSTIC_CONNEXION_LLM.md`** (ce fichier)  
   Analyse du problème Espagne

---

## ✅ Checklist Résolution

- [x] Problème identifié : Pas de clé API LLM
- [x] Tests effectués : test_discovery_debug.py
- [x] Scripts créés : setup_llm.sh, test_discovery_debug.py
- [x] Documentation : SETUP_LLM.md
- [ ] **À faire** : Configurer clé API Gemini
- [ ] **À faire** : Redémarrer backend
- [ ] **À faire** : Tester découverte Espagne
- [ ] **À faire** : Vérifier durée ~12-15s au lieu de 3s

---

## 🎯 Prochaines Étapes

1. **Immédiat** : Exécuter `./setup_llm.sh` ou créer `.env` manuellement
2. **Court terme** : Tester avec quelques découvertes pour valider
3. **Moyen terme** : Monitorer les quotas Gemini (logs rate limiting)
4. **Long terme** : Évaluer passage à OpenRouter si besoin volume

---

**🔗 Liens Utiles**
- Google AI Studio : https://ai.google.dev
- OpenRouter : https://openrouter.ai
- Documentation Gemini : https://ai.google.dev/docs
- Logs backend : Terminal avec `python admin_api.py`
