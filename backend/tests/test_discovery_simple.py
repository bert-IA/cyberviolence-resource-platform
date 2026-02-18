"""
Test simple pour diagnostiquer le problème de découverte
"""
import requests
import json
import time

BASE_URL = "http://localhost:8000"
HEADERS = {
    "Content-Type": "application/json",
    "Authorization": "Bearer admin-token-2024"
}

def test_discovery_emergency():
    """Test découverte avec catégorie emergency"""
    print("\n" + "="*60)
    print("🔍 TEST DISCOVERY - EMERGENCY")
    print("="*60)
    
    payload = {
        "language": "FR",
        "categories": ["emergency"],  # Une seule catégorie pour test simple
        "countries": ["FR"],           # Un seul pays
        "max_per_category": 1          # Une seule ressource
    }
    
    print(f"\n📤 Payload envoyé:")
    print(json.dumps(payload, indent=2))
    
    print(f"\n⏳ Envoi POST {BASE_URL}/geographic/discover...")
    start_time = time.time()
    
    try:
        response = requests.post(
            f"{BASE_URL}/geographic/discover",
            json=payload,
            headers=HEADERS,
            timeout=60  # 60 secondes max
        )
        
        elapsed = time.time() - start_time
        print(f"⏱️  Temps écoulé: {elapsed:.2f}s")
        
        print(f"\n📊 Status Code: {response.status_code}")
        print(f"📊 Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"\n✅ Réponse JSON:")
            print(json.dumps(data, indent=2, ensure_ascii=False))
            
            # Analyse détaillée
            if data.get("success"):
                discovered = data.get("data", {}).get("discovered_count", 0)
                resources = data.get("data", {}).get("resources", [])
                
                print(f"\n📈 Analyse:")
                print(f"   - Découvertes: {discovered}")
                print(f"   - Ressources dans liste: {len(resources)}")
                
                if discovered == 0:
                    print("\n⚠️  PROBLÈME: 0 ressources découvertes")
                    print("   Vérifier les logs backend pour:")
                    print("   - Connexion LLM réussie ?")
                    print("   - Prompt généré ?")
                    print("   - Réponse LLM reçue ?")
                    print("   - Parsing réussi ?")
                else:
                    print("\n✅ Découverte OK!")
                    for idx, res in enumerate(resources, 1):
                        print(f"\n   Ressource {idx}:")
                        print(f"     - Nom: {res.get('name')}")
                        print(f"     - Pays: {res.get('country')}")
                        print(f"     - Catégorie: {res.get('category')}")
                        print(f"     - New: {res.get('is_new')}")
            else:
                print(f"\n❌ Échec: {data.get('message')}")
        else:
            print(f"\n❌ Erreur HTTP {response.status_code}")
            print(response.text)
            
    except requests.Timeout:
        print(f"\n⏰ TIMEOUT après 60s - Le LLM prend trop de temps")
    except Exception as e:
        print(f"\n❌ Exception: {type(e).__name__}: {e}")

def test_discovery_procedure_platform():
    """Test découverte avec catégorie procedure_plateforme (celle qui fonctionne)"""
    print("\n" + "="*60)
    print("🔍 TEST DISCOVERY - PROCEDURE PLATEFORME (référence qui marche)")
    print("="*60)
    
    payload = {
        "language": "FR",
        "categories": ["procedure_plateforme"],
        "countries": [],  # Pas de pays pour procedure_plateforme
        "max_per_category": 1
    }
    
    print(f"\n📤 Payload envoyé:")
    print(json.dumps(payload, indent=2))
    
    print(f"\n⏳ Envoi POST {BASE_URL}/geographic/discover...")
    start_time = time.time()
    
    try:
        response = requests.post(
            f"{BASE_URL}/geographic/discover",
            json=payload,
            headers=HEADERS,
            timeout=30
        )
        
        elapsed = time.time() - start_time
        print(f"⏱️  Temps écoulé: {elapsed:.2f}s")
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"\n✅ Réponse (procedure_plateforme):")
            print(json.dumps(data, indent=2, ensure_ascii=False))
            
            if data.get("success"):
                discovered = data.get("data", {}).get("discovered_count", 0)
                print(f"\n✅ procedure_plateforme: {discovered} ressources")
        else:
            print(f"\n❌ Erreur HTTP {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"\n❌ Exception: {type(e).__name__}: {e}")

if __name__ == "__main__":
    print("\n🚀 DIAGNOSTIC DÉCOUVERTE DE RESSOURCES")
    print("="*80)
    
    # Test 1 : procedure_plateforme (référence qui marche)
    test_discovery_procedure_platform()
    
    print("\n" + "="*80)
    print("⏳ Attente 3s entre les tests...")
    time.sleep(3)
    
    # Test 2 : emergency (celui qui ne marche pas)
    test_discovery_emergency()
    
    print("\n" + "="*80)
    print("🏁 Tests terminés - Analyser les différences")
    print("="*80)
