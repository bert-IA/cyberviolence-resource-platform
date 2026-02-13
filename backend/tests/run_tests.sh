#!/bin/bash

# Script de lancement des tests
# Usage: ./tests/run_tests.sh [quick|full]

echo "🧪 Resource Discovery Platform - Tests API Configuration"
echo "=========================================================="

# Couleurs
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Vérifier que le backend tourne
echo -e "\n${YELLOW}1️⃣  Vérification backend...${NC}"
if curl -s http://localhost:8001/health > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Backend accessible${NC}"
else
    echo -e "${RED}❌ Backend inaccessible !${NC}"
    echo -e "${YELLOW}💡 Démarrer le serveur: python admin_api.py${NC}"
    exit 1
fi

# Installer dépendances si nécessaire
echo -e "\n${YELLOW}2️⃣  Vérification dépendances...${NC}"
if ! python3 -c "import requests" 2>/dev/null; then
    echo -e "${YELLOW}📦 Installation de requests...${NC}"
    pip install -r tests/requirements_test.txt
fi
echo -e "${GREEN}✅ Dépendances OK${NC}"

# Lancer les tests
echo -e "\n${YELLOW}3️⃣  Lancement des tests...${NC}"
echo "=========================================================="

if [ "$1" == "quick" ]; then
    echo -e "\n${YELLOW}Mode: Test rapide${NC}\n"
    python3 tests/quick_test.py
    EXIT_CODE=$?
else
    echo -e "\n${YELLOW}Mode: Tests complets${NC}\n"
    python3 tests/test_config_api.py
    EXIT_CODE=$?
fi

echo ""
echo "=========================================================="

if [ $EXIT_CODE -eq 0 ]; then
    echo -e "${GREEN}✅ Tests terminés avec succès !${NC}"
else
    echo -e "${RED}❌ Certains tests ont échoué${NC}"
fi

exit $EXIT_CODE
