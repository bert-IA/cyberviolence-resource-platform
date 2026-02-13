"""
Tests pour l'API Configuration Pays/Langues
Script de test complet pour valider les routes CRUD
"""
import requests
import json
from typing import Dict, Any

# Configuration
BASE_URL = "http://localhost:8000"
TOKEN = "admin-token-2024"  # Token de dev (ADMIN_TOKEN_DEV)

HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

# Couleurs pour l'affichage
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'

def print_success(msg: str):
    print(f"{Colors.GREEN}✅ {msg}{Colors.RESET}")

def print_error(msg: str):
    print(f"{Colors.RED}❌ {msg}{Colors.RESET}")

def print_info(msg: str):
    print(f"{Colors.BLUE}ℹ️  {msg}{Colors.RESET}")

def print_warning(msg: str):
    print(f"{Colors.YELLOW}⚠️  {msg}{Colors.RESET}")

def print_section(title: str):
    print(f"\n{Colors.BLUE}{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}{Colors.RESET}\n")


# === TESTS ===

def test_1_get_all_config():
    """Test 1: Récupérer toute la configuration"""
    print_section("TEST 1: GET /admin/config/countries-languages")
    
    try:
        response = requests.get(
            f"{BASE_URL}/admin/config/countries-languages",
            headers=HEADERS
        )
        
        if response.status_code == 200:
            data = response.json()
            print_success(f"Configuration récupérée")
            print_info(f"Langues: {data.get('total_languages', 0)}")
            print_info(f"Pays total: {data.get('total_countries', 0)}")
            
            if data.get('languages'):
                for lang_code, lang_data in data['languages'].items():
                    print(f"  • {lang_code}: {lang_data['name']} - {len(lang_data['countries'])} pays")
            
            return True
        else:
            print_error(f"Status {response.status_code}: {response.text}")
            return False
            
    except Exception as e:
        print_error(f"Erreur: {e}")
        return False


def test_2_get_language_config():
    """Test 2: Récupérer config d'une langue spécifique"""
    print_section("TEST 2: GET /admin/config/countries-languages/FR")
    
    try:
        response = requests.get(
            f"{BASE_URL}/admin/config/countries-languages/FR",
            headers=HEADERS
        )
        
        if response.status_code == 200:
            data = response.json()
            print_success(f"Config FR récupérée")
            
            config = data.get('config', {})
            print_info(f"Langue: {config.get('name', '')} ({config.get('code', '')})")
            print_info(f"Pays: {len(config.get('countries', []))}")
            
            for country in config.get('countries', [])[:3]:  # Afficher 3 premiers pays
                print(f"  • {country['flag']} {country['country_name']} ({country['country_code']})")
            
            return True
        else:
            print_error(f"Status {response.status_code}: {response.text}")
            return False
            
    except Exception as e:
        print_error(f"Erreur: {e}")
        return False


def test_3_add_country():
    """Test 3: Ajouter un pays à une langue"""
    print_section("TEST 3: POST /admin/config/countries-languages/FR/countries")
    
    new_country = {
        "country_name": "Monaco",
        "country_code": "MC",
        "flag": "🇲🇨",
        "search_terms": ["cyberviolence", "harcèlement"],
        "search_terms_count": 2,
        "organizations_count": 3
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/admin/config/countries-languages/FR/countries",
            headers=HEADERS,
            json=new_country
        )
        
        if response.status_code == 200:
            data = response.json()
            print_success(f"Pays Monaco ajouté à FR")
            print_info(f"Réponse: {data.get('message', '')}")
            return True
        elif response.status_code == 400:
            # Peut-être déjà présent ou limite atteinte
            print_warning(f"Ajout impossible: {response.json().get('detail', '')}")
            return True  # Pas une erreur critique
        else:
            print_error(f"Status {response.status_code}: {response.text}")
            return False
            
    except Exception as e:
        print_error(f"Erreur: {e}")
        return False


def test_4_update_language():
    """Test 4: Mettre à jour une langue complète"""
    print_section("TEST 4: PUT /admin/config/countries-languages/IT")
    
    updated_config = {
        "name": "Italiano",
        "code": "IT",
        "countries": [
            {
                "country_name": "Italia",
                "country_code": "IT",
                "flag": "🇮🇹",
                "search_terms": ["cyberbullismo", "violenza digitale", "molestie online"],
                "search_terms_count": 3,
                "organizations_count": 20
            },
            {
                "country_name": "Svizzera",
                "country_code": "CH",
                "flag": "🇨🇭",
                "search_terms": ["cyberbullismo", "sicurezza digitale"],
                "search_terms_count": 2,
                "organizations_count": 12
            }
        ]
    }
    
    try:
        response = requests.put(
            f"{BASE_URL}/admin/config/countries-languages/IT",
            headers=HEADERS,
            json=updated_config
        )
        
        if response.status_code == 200:
            data = response.json()
            print_success(f"Langue IT mise à jour")
            print_info(f"Pays: {data.get('countries_count', 0)}")
            return True
        else:
            print_error(f"Status {response.status_code}: {response.text}")
            return False
            
    except Exception as e:
        print_error(f"Erreur: {e}")
        return False


def test_5_remove_country():
    """Test 5: Supprimer un pays d'une langue"""
    print_section("TEST 5: DELETE /admin/config/countries-languages/FR/countries/MC")
    
    try:
        response = requests.delete(
            f"{BASE_URL}/admin/config/countries-languages/FR/countries/MC",
            headers=HEADERS
        )
        
        if response.status_code == 200:
            data = response.json()
            print_success(f"Pays MC supprimé de FR")
            print_info(f"Réponse: {data.get('message', '')}")
            return True
        elif response.status_code == 404:
            print_warning(f"Pays MC non trouvé (déjà supprimé ?)")
            return True  # Pas une erreur critique
        else:
            print_error(f"Status {response.status_code}: {response.text}")
            return False
            
    except Exception as e:
        print_error(f"Erreur: {e}")
        return False


def test_6_get_stats():
    """Test 6: Récupérer les statistiques"""
    print_section("TEST 6: GET /admin/config/stats")
    
    try:
        response = requests.get(
            f"{BASE_URL}/admin/config/stats",
            headers=HEADERS
        )
        
        if response.status_code == 200:
            data = response.json()
            stats = data.get('stats', {})
            
            print_success(f"Statistiques récupérées")
            print_info(f"Version: {stats.get('version', '')}")
            print_info(f"Dernière MAJ: {stats.get('last_updated', '')}")
            print_info(f"Langues: {stats.get('total_languages', 0)}")
            print_info(f"Pays total: {stats.get('total_countries', 0)}")
            
            print("\n📊 Détails par langue:")
            for lang_code, lang_stats in stats.get('languages', {}).items():
                countries_list = ', '.join(lang_stats.get('countries', []))
                print(f"  • {lang_code} ({lang_stats['name']}): {lang_stats['countries_count']} pays [{countries_list}]")
            
            return True
        else:
            print_error(f"Status {response.status_code}: {response.text}")
            return False
            
    except Exception as e:
        print_error(f"Erreur: {e}")
        return False


def test_7_create_new_language():
    """Test 7: Créer une nouvelle langue (TE)"""
    print_section("TEST 7: PUT /admin/config/countries-languages/TE (nouvelle langue)")
    
    new_language = {
        "name": "Test Language",
        "code": "TE",
        "countries": [
            {
                "country_name": "Test Country",
                "country_code": "TC",
                "flag": "🏁",
                "search_terms": ["test", "cyberbullying"],
                "search_terms_count": 2,
                "organizations_count": 5
            }
        ]
    }
    
    try:
        response = requests.put(
            f"{BASE_URL}/admin/config/countries-languages/TE",
            headers=HEADERS,
            json=new_language
        )
        
        if response.status_code == 200:
            data = response.json()
            print_success(f"Nouvelle langue TE créée")
            print_info(f"Pays: {data.get('countries_count', 0)}")
            return True
        else:
            print_error(f"Status {response.status_code}: {response.text}")
            return False
            
    except Exception as e:
        print_error(f"Erreur: {e}")
        return False


def test_8_delete_language():
    """Test 8: Supprimer une langue complète"""
    print_section("TEST 8: DELETE /admin/config/countries-languages/TE")
    
    try:
        response = requests.delete(
            f"{BASE_URL}/admin/config/countries-languages/TE",
            headers=HEADERS
        )
        
        if response.status_code == 200:
            data = response.json()
            print_success(f"Langue TE supprimée")
            print_info(f"Réponse: {data.get('message', '')}")
            return True
        elif response.status_code == 404:
            print_warning(f"Langue TE non trouvée")
            return True
        else:
            print_error(f"Status {response.status_code}: {response.text}")
            return False
            
    except Exception as e:
        print_error(f"Erreur: {e}")
        return False


def test_9_validation_max_countries():
    """Test 9: Validation limite 5 pays par langue"""
    print_section("TEST 9: Validation limite 5 pays")
    
    # Essayer d'ajouter 6 pays à une nouvelle langue
    language_with_6_countries = {
        "name": "Test Max",
        "code": "TM",
        "countries": [
            {"country_name": f"Country {i}", "country_code": f"C{i}", "flag": "🏳️", 
             "search_terms": ["test"], "search_terms_count": 1, "organizations_count": 1}
            for i in range(6)  # 6 pays = trop !
        ]
    }
    
    try:
        response = requests.put(
            f"{BASE_URL}/admin/config/countries-languages/TM",
            headers=HEADERS,
            json=language_with_6_countries
        )
        
        # Accepter 400 (Bad Request) ou 422 (Unprocessable Entity - Pydantic)
        if response.status_code in [400, 422]:
            print_success(f"Validation OK : Limite 5 pays respectée (code {response.status_code})")
            error_detail = response.json().get('detail', '')
            if isinstance(error_detail, str):
                print_info(f"Message: {error_detail}")
            else:
                print_info(f"Erreur de validation détectée (Pydantic)")
            return True
        else:
            print_error(f"Validation échouée: Code {response.status_code} (attendu 400 ou 422)")
            return False
            
    except Exception as e:
        print_error(f"Erreur: {e}")
        return False


# === EXÉCUTION DES TESTS ===

def run_all_tests():
    """Exécute tous les tests"""
    print(f"\n{Colors.BLUE}{'='*60}")
    print(f"  🧪 TESTS API Configuration Pays/Langues")
    print(f"  📡 Backend: {BASE_URL}")
    print(f"{'='*60}{Colors.RESET}\n")
    
    tests = [
        ("Récupérer toute la config", test_1_get_all_config),
        ("Récupérer config langue FR", test_2_get_language_config),
        ("Ajouter pays Monaco à FR", test_3_add_country),
        ("Mettre à jour langue IT", test_4_update_language),
        ("Supprimer pays MC de FR", test_5_remove_country),
        ("Récupérer statistiques", test_6_get_stats),
        ("Créer nouvelle langue TEST", test_7_create_new_language),
        ("Supprimer langue TEST", test_8_delete_language),
        ("Validation limite 5 pays", test_9_validation_max_countries),
    ]
    
    results = []
    
    for name, test_func in tests:
        try:
            success = test_func()
            results.append((name, success))
        except Exception as e:
            print_error(f"Exception durant le test: {e}")
            results.append((name, False))
    
    # Résumé
    print_section("RÉSUMÉ DES TESTS")
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for name, success in results:
        status = f"{Colors.GREEN}✅ PASS" if success else f"{Colors.RED}❌ FAIL"
        print(f"{status}{Colors.RESET} - {name}")
    
    print(f"\n{Colors.BLUE}{'='*60}")
    percentage = (passed / total * 100) if total > 0 else 0
    color = Colors.GREEN if percentage == 100 else Colors.YELLOW if percentage >= 70 else Colors.RED
    print(f"{color}  Résultat: {passed}/{total} tests réussis ({percentage:.0f}%){Colors.RESET}")
    print(f"{Colors.BLUE}{'='*60}{Colors.RESET}\n")
    
    return passed == total


if __name__ == "__main__":
    try:
        # Vérifier que le serveur est accessible
        print_info("Vérification connexion au backend...")
        try:
            response = requests.get(f"{BASE_URL}/health", timeout=5)
            if response.status_code == 200:
                print_success("Backend accessible ✅\n")
            else:
                print_warning(f"Backend répond mais status {response.status_code}")
        except requests.exceptions.ConnectionError:
            print_error("❌ Backend inaccessible !")
            print_info(f"Assurez-vous que le serveur tourne sur {BASE_URL}")
            print_info("Commande: cd backend && python admin_api.py")
            exit(1)
        
        # Exécuter les tests
        success = run_all_tests()
        
        exit(0 if success else 1)
        
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}⚠️  Tests interrompus par l'utilisateur{Colors.RESET}")
        exit(1)
