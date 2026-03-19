"""
Constantes et données partagées - Élimine la redondance
"""

# === CONFIGURATION DES PAYS PAR LANGUE ===
COUNTRIES_CONFIG = {
    "FR": [
        {"country_name": "France", "country_code": "FR", "flag": "🇫🇷", "search_terms": ["cyberviolence", "cyberharcèlement", "harcèlement en ligne"], "search_terms_count": 3, "organizations_count": 15},
        {"country_name": "Belgique", "country_code": "BE", "flag": "🇧🇪", "search_terms": ["cyberviolence", "harcèlement", "cyberharcèlement"], "search_terms_count": 3, "organizations_count": 8},
        {"country_name": "Suisse", "country_code": "CH", "flag": "🇨🇭", "search_terms": ["cyberviolence", "cybermobbing", "harcèlement"], "search_terms_count": 3, "organizations_count": 12},
        {"country_name": "Canada", "country_code": "CA", "flag": "🇨🇦", "search_terms": ["cyberviolence", "cyberharcèlement", "intimidation"], "search_terms_count": 3, "organizations_count": 20},
        {"country_name": "Luxembourg", "country_code": "LU", "flag": "🇱🇺", "search_terms": ["cyberviolence", "harcèlement", "cybermobbing"], "search_terms_count": 3, "organizations_count": 5}
    ],
    "EN": [
        {"country_name": "United Kingdom", "country_code": "GB", "flag": "🇬🇧", "search_terms": ["cyberbullying", "cyberviolence", "online harassment"], "search_terms_count": 3, "organizations_count": 25},
        {"country_name": "United States", "country_code": "US", "flag": "🇺🇸", "search_terms": ["cyberbullying", "online harassment", "digital abuse"], "search_terms_count": 3, "organizations_count": 40},
        {"country_name": "Canada", "country_code": "CA", "flag": "🇨🇦", "search_terms": ["cyberbullying", "cyberviolence", "online safety"], "search_terms_count": 3, "organizations_count": 20},
        {"country_name": "Australia", "country_code": "AU", "flag": "🇦🇺", "search_terms": ["cyberbullying", "online harassment", "digital safety"], "search_terms_count": 3, "organizations_count": 18},
        {"country_name": "Ireland", "country_code": "IE", "flag": "🇮🇪", "search_terms": ["cyberbullying", "online abuse", "digital harassment"], "search_terms_count": 3, "organizations_count": 10}
    ],
    "ES": [
        {"country_name": "España", "country_code": "ES", "flag": "🇪🇸", "search_terms": ["ciberacoso", "ciberviolencia", "acoso online"], "search_terms_count": 3, "organizations_count": 22},
        {"country_name": "México", "country_code": "MX", "flag": "🇲🇽", "search_terms": ["ciberacoso", "ciberviolencia", "acoso digital"], "search_terms_count": 3, "organizations_count": 16},
        {"country_name": "Argentina", "country_code": "AR", "flag": "🇦🇷", "search_terms": ["ciberacoso", "violencia digital", "acoso virtual"], "search_terms_count": 3, "organizations_count": 14},
        {"country_name": "Colombia", "country_code": "CO", "flag": "🇨🇴", "search_terms": ["ciberacoso", "ciberviolencia", "matoneo virtual"], "search_terms_count": 3, "organizations_count": 12},
        {"country_name": "Chile", "country_code": "CL", "flag": "🇨🇱", "search_terms": ["ciberacoso", "ciberbullying", "acoso digital"], "search_terms_count": 3, "organizations_count": 10}
    ],
    "IT": [
        {"country_name": "Italia", "country_code": "IT", "flag": "🇮🇹", "search_terms": ["cyberbullismo", "violenza digitale", "molestie online"], "search_terms_count": 3, "organizations_count": 18},
        {"country_name": "Svizzera", "country_code": "CH", "flag": "🇨🇭", "search_terms": ["cyberbullismo", "sicurezza digitale"], "search_terms_count": 2, "organizations_count": 12},
        {"country_name": "San Marino", "country_code": "SM", "flag": "🇸🇲", "search_terms": ["cyberbullismo", "protezione online"], "search_terms_count": 2, "organizations_count": 3}
    ],
    "DE": [
        {"country_name": "Deutschland", "country_code": "DE", "flag": "🇩🇪", "search_terms": ["cybermobbing", "cybergewalt", "online-belästigung"], "search_terms_count": 3, "organizations_count": 30},
        {"country_name": "Österreich", "country_code": "AT", "flag": "🇦🇹", "search_terms": ["cybermobbing", "cybergewalt", "digitale gewalt"], "search_terms_count": 3, "organizations_count": 15},
        {"country_name": "Schweiz", "country_code": "CH", "flag": "🇨🇭", "search_terms": ["cybermobbing", "cybergewalt", "online-mobbing"], "search_terms_count": 3, "organizations_count": 12}
    ],
    "PT": [
        {"country_name": "Portugal", "country_code": "PT", "flag": "🇵🇹", "search_terms": ["ciberbullying", "violência digital", "assédio online"], "search_terms_count": 3, "organizations_count": 14},
        {"country_name": "Brasil", "country_code": "BR", "flag": "🇧🇷", "search_terms": ["cyberbullying", "violência digital", "assédio virtual"], "search_terms_count": 3, "organizations_count": 25}
    ]
}

# === LANGUES SUPPORTÉES ===
SUPPORTED_LANGUAGES = ["FR", "EN", "ES", "IT", "DE", "PT"]

# === LLM PROVIDERS ===
LLM_PROVIDERS = [
    {"name": "Gemini AI", "id": "gemini", "status": "available"},
    {"name": "OpenRouter", "id": "openrouter", "status": "available"}, 
    {"name": "Local Model", "id": "local", "status": "beta"}
]

# === CONSTANTES API ===
DEFAULT_LLM_PROVIDER = "gemini"
API_VERSION = "2.0.0"
API_TITLE = "resource discovery Critical admin API"
API_DESCRIPTION = "API d'administration des ressources critiques avec système de validation dual"

# === STRATÉGIE LEAN ===
LEAN_MAX_COUNTRIES_PER_LANGUAGE = 5
LEAN_MAX_RESOURCES_PER_COUNTRY = 16

# === CATÉGORIES DE DÉCOUVERTE V2 ===
DISCOVERY_CATEGORIES = {
    "service_support": {
        "label": "Services d'assistance",
        "description": "Services nationaux d'aide aux victimes de cyberviolence (priorité gouvernementale)",
        "default_count": 3,
        "v2": True,
    },
    "procedure_plateforme": {
        "label": "Procédures plateforme",
        "description": "Procédures officielles des plateformes (réseaux sociaux, messageries)",
        "default_count": 5,
        "v2": True,
    },
    "signalement_autorite": {
        "label": "Signalement autorités",
        "description": "Autorités légales de signalement (police, PHAROS, cybermalveillance.gouv.fr)",
        "default_count": 4,
        "v2": True,
    },
}

# === LABELS PAYS (source unique — ne pas dupliquer dans les routers) ===
COUNTRY_LABELS: dict = {
    "FR": "France",
    "BE": "Belgique",
    "CH": "Suisse",
    "LU": "Luxembourg",
    "MC": "Monaco",
    "ES": "Espagne",
    "IT": "Italie",
    "DE": "Allemagne",
    "AT": "Autriche",
    "PT": "Portugal",
    "BR": "Brésil",
    "CA": "Canada",
    "US": "États-Unis",
    "GB": "Royaume-Uni",
    "IE": "Irlande",
    "AU": "Australie",
    "MX": "Mexique",
    "AR": "Argentine",
    "CO": "Colombie",
    "CL": "Chili",
    "SM": "Saint-Marin",
}

# === STATUTS DE WORKFLOW ===
WORKFLOW_STATUSES = {
    "discovered": "Ressource découverte",
    "geo_pending": "En attente validation géographique",
    "geo_validated": "Validée géographiquement",
    "critical_pending": "En attente validation critique",
    "critical_validated": "Validée critiquement",
    "rag_ready": "Prêt pour RAG",
    "rejected": "Rejetée"
}

# === MESSAGES D'ERREUR STANDARDS ===
ERROR_MESSAGES = {
    "auth_failed": "Token d'accès invalide",
    "not_found": "Ressource non trouvée",
    "invalid_action": "Action invalide",
    "missing_params": "Paramètres manquants",
    "system_error": "Erreur interne du serveur"
}

# === CONSTANTES DE SÉCURITÉ ===
ADMIN_TOKEN_DEV = "admin-token-2024"  # À remplacer par vraie authentification en prod
