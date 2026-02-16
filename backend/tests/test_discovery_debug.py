#!/usr/bin/env python3
"""
Script de test pour analyser en détail la découverte de ressources
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"
ADMIN_TOKEN = "admin-token-2024"

def test_discovery_espagne_local():
    """
    Test spécifique: Espagne, catégorie association_locale
    """
    print("\n" + "="*80)
    print("🧪 TEST: Découverte Espagne - Association Locale")
    print("="*80)
    
    # Paramètres du test
    payload = {
        "language": "ES",
        "categories": ["association_locale"],
        "countries": ["ES"],  # Code pays Espagne
        "max_per_category": 3
    }
    
    print(f"\n📤 Requête envoyée:")
    print(json.dumps(payload, indent=2))
    
    headers = {
        "Authorization": f"Bearer {ADMIN_TOKEN}",
        "Content-Type": "application/json"
    }
    
    # Envoyer la requête
    print(f"\n⏳ Envoi POST {BASE_URL}/geographic/discover...")
    start_time = time.time()
    
    try:
        response = requests.post(
            f"{BASE_URL}/geographic/discover",
            json=payload,
            headers=headers,
            timeout=120  # 2 minutes max
        )
        
        duration = time.time() - start_time
        
        print(f"\n⏱️  Durée: {duration:.2f} secondes")
        print(f"📥 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"\n✅ Réponse JSON:")
            print(json.dumps(result, indent=2, ensure_ascii=False))
            
            # Analyser les résultats
            if result.get("success"):
                data = result.get("data", {})
                resources = data.get("resources", [])
                discovered_count = data.get("discovered_count", 0)
                
                print(f"\n📊 ANALYSE:")
                print(f"   - Ressources découvertes: {discovered_count}")
                print(f"   - Ressources dans la liste: {len(resources)}")
                print(f"   - Catégories: {data.get('categories', [])}")
                print(f"   - Langue: {data.get('language', 'N/A')}")
                
                if resources:
                    print(f"\n📋 DÉTAIL DES RESSOURCES:")
                    for idx, resource in enumerate(resources, 1):
                        print(f"\n   {idx}. {resource.get('name', 'N/A')}")
                        print(f"      URL: {resource.get('url', 'N/A')}")
                        print(f"      Pays: {resource.get('country', 'N/A')}")
                        print(f"      Catégorie: {resource.get('category', 'N/A')}")
                else:
                    print(f"\n⚠️  AUCUNE RESSOURCE TROUVÉE!")
                    print(f"\n🔍 HYPOTHÈSES:")
                    print(f"   1. Le LLM n'a pas été appelé (vérifier les logs backend)")
                    print(f"   2. Le LLM a répondu mais parsing a échoué")
                    print(f"   3. Les ressources ont été filtrées/rejetées")
                    print(f"   4. Problème de configuration pays/langue")
            else:
                print(f"\n❌ Échec: {result.get('message', 'Erreur inconnue')}")
        else:
            print(f"\n❌ Erreur HTTP {response.status_code}")
            print(f"Response: {response.text[:500]}")
            
    except requests.exceptions.Timeout:
        print(f"\n⏰ TIMEOUT après 120 secondes")
    except Exception as e:
        print(f"\n❌ Exception: {type(e).__name__}: {e}")

def test_discovery_multi_pays():
    """
    Test avec plusieurs pays pour comparaison
    """
    print("\n" + "="*80)
    print("🧪 TEST: Découverte Multi-Pays - Local")
    print("="*80)
    
    payload = {
        "language": "FR",
        "categories": ["local"],
        "countries": ["FR", "BE"],  # France et Belgique
        "max_per_category": 2
    }
    
    print(f"\n📤 Requête:")
    print(json.dumps(payload, indent=2))
    
    headers = {
        "Authorization": f"Bearer {ADMIN_TOKEN}",
        "Content-Type": "application/json"
    }
    
    print(f"\n⏳ Envoi POST {BASE_URL}/geographic/discover...")
    start_time = time.time()
    
    try:
        response = requests.post(
            f"{BASE_URL}/geographic/discover",
            json=payload,
            headers=headers,
            timeout=120
        )
        
        duration = time.time() - start_time
        print(f"\n⏱️  Durée: {duration:.2f} secondes")
        print(f"📥 Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            discovered = result.get("data", {}).get("discovered_count", 0)
            print(f"\n✅ Ressources découvertes: {discovered}")
        
    except Exception as e:
        print(f"\n❌ Exception: {e}")

if __name__ == "__main__":
    print("\n🚀 DÉMARRAGE DES TESTS DE DEBUG DÉCOUVERTE")
    print("="*80)
    
    # Test 1: Espagne - Association Locale (le cas problématique)
    test_discovery_espagne_local()
    
    # Test 2: Multi-pays pour comparaison
    print("\n" + "="*80)
    input("Appuyez sur Entrée pour lancer le test multi-pays...")
    test_discovery_multi_pays()
    
    print("\n" + "="*80)
    print("✅ TESTS TERMINÉS")
    print("="*80)
    print("\n💡 PROCHAINES ÉTAPES:")
    print("   1. Analyser les logs du backend (INFO, WARNING, ERROR)")
    print("   2. Vérifier si le LLM a été appelé (logs '📝 LLM Response')")
    print("   3. Vérifier le parsing (logs '_parse_llm_response')")
    print("   4. Vérifier les filtres de validation/déduplication")
    print()
