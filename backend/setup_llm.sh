#!/bin/bash

# Script de configuration rapide du LLM
# Usage: ./setup_llm.sh

set -e

BACKEND_DIR="$(cd "$(dirname "$0")" && pwd)"
ENV_FILE="$BACKEND_DIR/.env"

echo "🚀 Configuration LLM - Resource Discovery Platform"
echo "=================================================="
echo ""

# Vérifier si .env existe déjà
if [ -f "$ENV_FILE" ]; then
    echo "⚠️  Le fichier .env existe déjà"
    echo "Contenu actuel:"
    echo "----------------"
    cat "$ENV_FILE"
    echo "----------------"
    echo ""
    read -p "Voulez-vous le remplacer? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "❌ Configuration annulée"
        exit 0
    fi
fi

echo ""
echo "📋 Choisissez votre provider LLM:"
echo "  1) Google Gemini (Gratuit, recommandé)"
echo "  2) OpenRouter (Payant, flexible)"
echo ""
read -p "Choix (1 ou 2): " choice

case $choice in
    1)
        echo ""
        echo "🌟 Configuration Gemini"
        echo "➡️  Obtenir une clé sur: https://ai.google.dev"
        echo ""
        read -p "Entrez votre clé API Gemini (AIza...): " api_key
        
        if [[ ! $api_key =~ ^AIza ]]; then
            echo "⚠️  Attention: Les clés Gemini commencent généralement par 'AIza'"
            read -p "Continuer quand même? (y/N): " -n 1 -r
            echo
            if [[ ! $REPLY =~ ^[Yy]$ ]]; then
                exit 1
            fi
        fi
        
        cat > "$ENV_FILE" << EOF
# Configuration LLM - Gemini
LLM_PROVIDER=gemini
GEMINI_API_KEY=$api_key
EOF
        echo "✅ Fichier .env créé avec Gemini"
        ;;
        
    2)
        echo ""
        echo "💰 Configuration OpenRouter"
        echo "➡️  Obtenir une clé sur: https://openrouter.ai"
        echo ""
        read -p "Entrez votre clé API OpenRouter (sk-or-...): " api_key
        
        if [[ ! $api_key =~ ^sk-or- ]]; then
            echo "⚠️  Attention: Les clés OpenRouter commencent par 'sk-or-'"
            read -p "Continuer quand même? (y/N): " -n 1 -r
            echo
            if [[ ! $REPLY =~ ^[Yy]$ ]]; then
                exit 1
            fi
        fi
        
        cat > "$ENV_FILE" << EOF
# Configuration LLM - OpenRouter
LLM_PROVIDER=openrouter
OPENROUTER_API_KEY=$api_key
EOF
        echo "✅ Fichier .env créé avec OpenRouter"
        ;;
        
    *)
        echo "❌ Choix invalide"
        exit 1
        ;;
esac

echo ""
echo "📄 Contenu de .env:"
echo "----------------"
cat "$ENV_FILE"
echo "----------------"
echo ""

# Vérifier si le backend tourne
if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null 2>&1 ; then
    echo "⚠️  Le backend est déjà en cours d'exécution sur le port 8000"
    echo ""
    read -p "Voulez-vous le redémarrer? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "⏹️  Arrêt du backend..."
        lsof -ti:8000 | xargs kill -9 2>/dev/null || true
        sleep 1
        echo "🚀 Démarrage du backend..."
        python admin_api.py &
        BACKEND_PID=$!
        sleep 2
        
        if ps -p $BACKEND_PID > /dev/null; then
            echo "✅ Backend démarré (PID: $BACKEND_PID)"
        else
            echo "❌ Erreur lors du démarrage du backend"
            exit 1
        fi
    fi
else
    echo "🚀 Démarrer le backend avec:"
    echo "   python admin_api.py"
fi

echo ""
echo "🧪 Tester la configuration avec:"
echo "   python tests/test_discovery_debug.py"
echo ""
echo "📚 Documentation complète: ./SETUP_LLM.md"
echo ""
echo "✅ Configuration terminée !"
