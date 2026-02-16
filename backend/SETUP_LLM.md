# 🔧 Configuration LLM - Guide Complet

## 🚨 Problème Détecté

La découverte de ressources échoue avec le message :
```
"Connexion LLM échouée"
```

**Cause** : Aucune clé API LLM n'est configurée dans les variables d'environnement.

---

## ✅ Solution : Configurer une Clé API LLM

### Option 1 : Google Gemini (Recommandé - Gratuit) 🌟

#### Étape 1 : Obtenir une clé API Gemini

1. Aller sur [Google AI Studio](https://ai.google.dev)
2. Se connecter avec un compte Google
3. Cliquer sur "Get API Key"
4. Créer un nouveau projet ou sélectionner un existant
5. Copier la clé API (format : `AIza...`)

**Avantages** :
- ✅ Gratuit (quota généreux)
- ✅ Rapide et performant
- ✅ Bonne qualité de réponses en français et autres langues

#### Étape 2 : Configurer le Backend

Créer le fichier `.env` dans `/backend` :

```bash
cd /home/bert/resource-discovery-platform/backend
cat > .env << 'EOF'
# Configuration LLM
LLM_PROVIDER=gemini
GEMINI_API_KEY=AIza_VOTRE_CLE_ICI

# OU alternative avec GOOGLE_API_KEY
# GOOGLE_API_KEY=AIza_VOTRE_CLE_ICI
EOF
```

**Remplacer** `AIza_VOTRE_CLE_ICI` par votre vraie clé API.

---

### Option 2 : OpenRouter (Payant mais Flexible) 💰

#### Étape 1 : Obtenir une clé OpenRouter

1. Aller sur [OpenRouter](https://openrouter.ai)
2. Créer un compte
3. Ajouter des crédits ($5 minimum recommandé)
4. Générer une clé API dans Settings > API Keys
5. Copier la clé (format : `sk-or-...`)

**Avantages** :
- ✅ Accès à plusieurs modèles (Claude, GPT, Gemini, etc.)
- ✅ Contrôle du budget
- ✅ Fallback automatique entre modèles

#### Étape 2 : Configurer le Backend

```bash
cd /home/bert/resource-discovery-platform/backend
cat > .env << 'EOF'
# Configuration LLM
LLM_PROVIDER=openrouter
OPENROUTER_API_KEY=sk-or-VOTRE_CLE_ICI
EOF
```

---

## 🚀 Vérification de la Configuration

### 1. Vérifier que le fichier `.env` existe

```bash
cd /home/bert/resource-discovery-platform/backend
cat .env
```

Vous devriez voir :
```
LLM_PROVIDER=gemini
GEMINI_API_KEY=AIza...
```

### 2. Redémarrer le Backend

**Important** : Le backend doit être redémarré pour charger les variables d'environnement.

```bash
# Arrêter le backend actuel
lsof -ti:8000 | xargs kill -9

# Redémarrer avec .env chargé
cd /home/bert/resource-discovery-platform/backend
python admin_api.py
```

### 3. Tester la Connexion LLM

```bash
cd /home/bert/resource-discovery-platform/backend
python tests/test_discovery_debug.py
```

**Résultat attendu** :
```
✅ Ressources découvertes: 1-3
```

Au lieu de :
```
❌ Échec: Connexion LLM échouée
```

---

## 🐛 Dépannage

### Problème : "Clé API Gemini manquante"

**Solution** :
1. Vérifier que `.env` contient bien `GEMINI_API_KEY=AIza...`
2. Vérifier qu'il n'y a pas d'espaces autour du `=`
3. Redémarrer le backend

### Problème : "429 Too Many Requests"

**Cause** : Rate limiting de l'API (trop de requêtes trop rapidement)

**Solutions** :
- Attendre 60 secondes
- Réduire `max_per_category` dans la requête (ex: 2 au lieu de 3)
- Pour Gemini gratuit : limiter à ~15 requêtes/minute

### Problème : "Invalid API Key"

**Solutions** :
1. Vérifier que la clé API est correcte (copier-coller sans espaces)
2. Pour Gemini : vérifier sur [Google AI Studio](https://ai.google.dev) que la clé est active
3. Pour OpenRouter : vérifier que le compte a des crédits

---

## 📊 Configuration Avancée

### Variables d'Environnement Disponibles

```bash
# backend/.env

# Provider LLM (gemini ou openrouter)
LLM_PROVIDER=gemini

# Clés API
GEMINI_API_KEY=AIza...           # Pour Gemini
GOOGLE_API_KEY=AIza...           # Alternative pour Gemini
OPENROUTER_API_KEY=sk-or-...     # Pour OpenRouter

# Paramètres optionnels
LLM_TEMPERATURE=0.0              # Créativité (0.0 = déterministe)
LLM_MAX_TOKENS=1000              # Longueur max réponse
LLM_TIMEOUT=30                   # Timeout en secondes
LLM_MAX_RETRIES=3                # Nombre de tentatives
```

### Tester avec Python directement

```python
import os
os.environ['LLM_PROVIDER'] = 'gemini'
os.environ['GEMINI_API_KEY'] = 'AIza...'

from core.llm_manager import LLMManager

manager = LLMManager()
success = manager.test_connection()
print(f"✅ Connexion: {success}")

if success:
    response = manager.generate("Trouve une association contre le cyberharcèlement en Espagne")
    print(response.content)
```

---

## 🎯 Récapitulatif : Étapes Minimales

1. **Obtenir une clé API Gemini** sur https://ai.google.dev
2. **Créer `.env`** avec `GEMINI_API_KEY=AIza...`
3. **Redémarrer le backend** : `python admin_api.py`
4. **Tester** : Aller sur DiscoveryPage et lancer une recherche

---

## 📝 Notes Importantes

### Sécurité

⚠️ **JAMAIS** commit le fichier `.env` sur Git !

Le `.gitignore` devrait contenir :
```
.env
*.env
```

### Quotas Gemini Gratuit

- **Limite** : ~15 requêtes/minute
- **Quota journalier** : Très généreux (plusieurs centaines)
- **Conseils** :
  - Limiter `max_per_category` à 2-3
  - Le backend a déjà un délai de 5s entre requêtes
  - Pour tests : utiliser 1-2 pays maximum

### Coûts OpenRouter

- **~$0.001-0.005** par requête (selon modèle)
- **Budget recommandé** : $5 pour ~1000-5000 découvertes
- **Modèles disponibles** :
  - `google/gemini-2.0-flash-exp:free` (gratuit)
  - `anthropic/claude-3-haiku` (économique)
  - `openai/gpt-3.5-turbo` (équilibré)

---

## ✅ Checklist Finale

- [ ] Clé API obtenue (Gemini ou OpenRouter)
- [ ] Fichier `.env` créé dans `/backend`
- [ ] Clé API copiée dans `.env` (format correct)
- [ ] Backend redémarré
- [ ] Test de connexion réussi
- [ ] Découverte fonctionne sur DiscoveryPage

---

**Besoin d'aide ?** Vérifier les logs du backend pour voir les erreurs détaillées.
