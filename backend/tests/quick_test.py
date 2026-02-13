#!/usr/bin/env python3
"""
Test rapide - Vérification configuration OK
Usage: python tests/quick_test.py
"""
import requests
import sys

BASE_URL = "http://localhost:8001"
TOKEN = "dev_token_123"
HEADERS = {"Authorization": f"Bearer {TOKEN}"}

def quick_test():
    """Test rapide: vérifier que l'API config fonctionne"""
    
    print("🧪 Test rapide API Configuration...")
    
    try:
        # Test 1: Backend accessible ?
        print("\n1️⃣  Test connexion backend...", end=" ")
        r = requests.get(f"{BASE_URL}/health", timeout=3)
        if r.status_code == 200:
            print("✅")
        else:
            print(f"❌ Status {r.status_code}")
            return False
        
        # Test 2: Routes config accessibles ?
        print("2️⃣  Test authentification...", end=" ")
        r = requests.get(f"{BASE_URL}/admin/config/stats", headers=HEADERS, timeout=3)
        if r.status_code == 200:
            print("✅")
        elif r.status_code == 401:
            print(f"❌ Token invalide")
            return False
        else:
            print(f"❌ Status {r.status_code}")
            return False
        
        # Test 3: Configuration chargée ?
        print("3️⃣  Test configuration...", end=" ")
        r = requests.get(f"{BASE_URL}/admin/config/countries-languages", headers=HEADERS, timeout=3)
        if r.status_code == 200:
            data = r.json()
            langs = data.get('total_languages', 0)
            countries = data.get('total_countries', 0)
            print(f"✅ ({langs} langues, {countries} pays)")
        else:
            print(f"❌ Status {r.status_code}")
            return False
        
        # Test 4: Stats accessibles ?
        print("4️⃣  Test statistiques...", end=" ")
        r = requests.get(f"{BASE_URL}/admin/config/stats", headers=HEADERS, timeout=3)
        if r.status_code == 200:
            stats = r.json().get('stats', {})
            version = stats.get('version', 'N/A')
            print(f"✅ (version {version})")
        else:
            print(f"❌ Status {r.status_code}")
            return False
        
        print("\n" + "="*50)
        print("✅ Tous les tests rapides réussis !")
        print("="*50)
        print("\n💡 Pour tests complets: python tests/test_config_api.py")
        return True
        
    except requests.exceptions.ConnectionError:
        print("\n❌ Backend inaccessible !")
        print("💡 Démarrer le serveur: cd backend && python admin_api.py")
        return False
    except Exception as e:
        print(f"\n❌ Erreur: {e}")
        return False

if __name__ == "__main__":
    success = quick_test()
    sys.exit(0 if success else 1)
