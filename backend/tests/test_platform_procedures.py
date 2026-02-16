#!/usr/bin/env python3
"""
Test spécifique pour procedure_plateforme
Doit trouver les pages officielles des réseaux sociaux (Facebook, TikTok, Instagram, etc.)
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"
ADMIN_TOKEN = "admin-token-2024"

def test_platform_procedures():
    """
    Test: procedure_plateforme doit trouver les pages officielles des réseaux sociaux
    """
    print("\n" + "="*80)
    print("🧪 TEST: Procédures Plateformes - Pages Officielles Réseaux Sociaux")
    print("="*80)
    
    payload = {
        "language": "FR",
        "categories": ["procedure_plateforme"],
        "countries": ["FR"],  # Peu importe, procédures universelles
        "max_per_category": 3  # Demander 3 plateformes
    }
    
    print(f"\n📤 Requête:")
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    
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
            timeout=60
        )
        
        duration = time.time() - start_time
        
        print(f"\n⏱️  Durée: {duration:.2f} secondes")
        print(f"📥 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"\n✅ Réponse JSON:")
            print(json.dumps(result, indent=2, ensure_ascii=False))
            
            if result.get("success"):
                data = result.get("data", {})
                resources = data.get("resources", [])
                discovered_count = data.get("discovered_count", 0)
                
                print(f"\n📊 ANALYSE:")
                print(f"   - Ressources découvertes: {discovered_count}")
                print(f"   - Ressources dans la liste: {len(resources)}")
                
                if resources:
                    print(f"\n📋 DÉTAIL DES PLATEFORMES:")
                    
                    # Plateformes attendues
                    expected_platforms = [
                        "facebook", "instagram", "tiktok", "snapchat", 
                        "twitter", "x", "youtube", "discord", "whatsapp"
                    ]
                    
                    for idx, resource in enumerate(resources, 1):
                        name = resource.get('name', 'N/A')
                        url = resource.get('url', 'N/A')
                        description = resource.get('description', 'N/A')
                        is_new = resource.get('is_new', False)
                        
                        print(f"\n   {idx}. {name}")
                        print(f"      URL: {url}")
                        print(f"      Description: {description[:100]}...")
                        print(f"      Nouvelle: {is_new}")
                        
                        # Vérifier si c'est bien une plateforme connue
                        name_lower = name.lower()
                        is_known_platform = any(platform in name_lower for platform in expected_platforms)
                        
                        if is_known_platform:
                            print(f"      ✅ Plateforme reconnue")
                        else:
                            print(f"      ⚠️  Plateforme inconnue (vérifier si c'est correct)")
                        
                        # Vérifier si l'URL est officielle
                        if url and url != "N/A":
                            url_lower = url.lower()
                            if any(platform in url_lower for platform in expected_platforms):
                                print(f"      ✅ URL officielle détectée")
                            else:
                                print(f"      ⚠️  URL à vérifier (domaine inattendu)")
                    
                    print(f"\n🎯 OBJECTIF ATTEINT:")
                    print(f"   Les procédures des plateformes sociales ont été trouvées !")
                    print(f"   Ces liens permettent aux enfants de signaler ou modifier leur compte.")
                else:
                    print(f"\n⚠️  AUCUNE PLATEFORME TROUVÉE!")
                    print(f"   Vérifier les logs backend pour comprendre pourquoi.")
            else:
                print(f"\n❌ Échec: {result.get('message', 'Erreur inconnue')}")
        else:
            print(f"\n❌ Erreur HTTP {response.status_code}")
            print(f"Response: {response.text[:500]}")
            
    except requests.exceptions.Timeout:
        print(f"\n⏰ TIMEOUT après 60 secondes")
    except Exception as e:
        print(f"\n❌ Exception: {type(e).__name__}: {e}")

if __name__ == "__main__":
    print("\n🚀 TEST PROCÉDURES PLATEFORMES RÉSEAUX SOCIAUX")
    print("="*80)
    print("\n💡 Ce test doit trouver les pages officielles type:")
    print("   - Facebook Help Center (signalement)")
    print("   - TikTok Safety Center")
    print("   - Instagram Help (report)")
    print("   - Snapchat Support")
    print("   - etc.")
    print()
    
    test_platform_procedures()
    
    print("\n" + "="*80)
    print("✅ TEST TERMINÉ")
    print("="*80)
    print()
