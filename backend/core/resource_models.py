"""
Modèles de données étendus pour les catégories de ressources spécialisées
Selon la logique de sourcing définie dans logic_sourcing_ressources.md
"""

from enum import Enum
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict

class ResourceCategory(Enum):
    """4 catégories cibles minimales selon la stratégie lean"""
    CONTACT_URGENCE = "contact_urgence"           # 📞 Numéros directs d'aide
    PROCEDURE_PLATEFORME = "procedure_plateforme" # 🛠️ Steps signalement/blocage  
    SIGNALEMENT_AUTORITE = "signalement_autorite" # ⚖️ Procédures officielles
    ASSOCIATION_LOCALE = "association_locale"     # 🏢 Aide professionnelle locale
    
    # Maintien de la compatibilité avec l'existant
    SERVICES_SUPPORT = "services_support"         # 🤝 Existant (généraliste)

class UrgencyLevel(Enum):
    """Niveau d'urgence pour prioriser les ressources"""
    IMMEDIATE = "immediate"    # Urgence immédiate (hotlines 24h)
    NORMAL = "normal"         # Aide standard (horaires bureau)
    INFORMATION = "information" # Ressources informatives

class ContactType(Enum):
    """Type de contact pour faciliter l'intégration chatbot"""
    PHONE = "phone"          # Numéro de téléphone
    ONLINE = "online"        # Chat/formulaire en ligne
    EMAIL = "email"          # Contact email
    FORM = "form"           # Formulaire web
    APP = "app"             # Application mobile

class Availability(Enum):
    """Disponibilité du service"""
    ALWAYS = "24h"                    # 24h/7j
    BUSINESS_HOURS = "business_hours" # Horaires bureau
    SPECIFIC_SCHEDULE = "specific_schedule" # Horaires spécifiques

class OfficialStatus(Enum):
    """Statut officiel pour validation"""
    GOVERNMENT = "government"         # Gouvernemental
    CERTIFIED = "certified"          # Agréé officiellement
    APPROVED = "approved"            # Approuvé par autorités
    PRIVATE_TRUSTED = "private_trusted" # Privé mais fiable

class TestStatus(Enum):
    """Statut de test/vérification"""
    VERIFIED = "verified"    # Testé et fonctionnel
    PENDING = "pending"      # En attente de test
    FAILED = "failed"        # Test échoué
    NOT_TESTED = "not_tested" # Pas encore testé

@dataclass
class ResourceMetadata:
    """Métadonnées enrichies selon les nouvelles exigences"""
    
    # Nouvelles métadonnées obligatoires
    category: ResourceCategory
    urgency_level: UrgencyLevel
    contact_type: ContactType
    availability: Availability
    official_status: OfficialStatus
    test_status: TestStatus = TestStatus.NOT_TESTED
    
    # Métadonnées optionnelles spécialisées
    platform_name: Optional[str] = None          # Pour PROCEDURE_PLATEFORME
    authority_name: Optional[str] = None          # Pour SIGNALEMENT_AUTORITE
    specialization: Optional[str] = None          # Pour ASSOCIATION_LOCALE
    service_scope: Optional[str] = None           # Portée géographique
    
    # Métadonnées de validation
    last_verified: Optional[str] = None           # Date dernière vérification
    verification_notes: Optional[str] = None      # Notes de vérification
    update_frequency: Optional[str] = None        # Fréquence de mise à jour
    
    def to_dict(self) -> Dict[str, Any]:
        """Conversion en dictionnaire pour JSON"""
        result = {}
        for key, value in asdict(self).items():
            if isinstance(value, Enum):
                result[key] = value.value
            else:
                result[key] = value
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ResourceMetadata':
        """Création depuis dictionnaire JSON"""
        # Conversion des strings en Enums
        if 'category' in data:
            data['category'] = ResourceCategory(data['category'])
        if 'urgency_level' in data:
            data['urgency_level'] = UrgencyLevel(data['urgency_level'])
        if 'contact_type' in data:
            data['contact_type'] = ContactType(data['contact_type'])
        if 'availability' in data:
            data['availability'] = Availability(data['availability'])
        if 'official_status' in data:
            data['official_status'] = OfficialStatus(data['official_status'])
        if 'test_status' in data:
            data['test_status'] = TestStatus(data['test_status'])
            
        return cls(**data)

class CategoryTargets:
    """Targets minimaux par pays selon la stratégie lean"""
    
    TARGETS_PER_COUNTRY = {
        "contacts_urgence": 3,        # 3018 + 2 backup
        "procedures_plateformes": 6,  # Top 6 plateformes
        "signalement_autorites": 2,   # Pharos + Cybermalveillance
        "associations_locales": 5     # 5 principales
    }
    
    # Total par pays: ~16 ressources (vs 100+ extensive)
    TOTAL_TARGET_PER_COUNTRY = sum(TARGETS_PER_COUNTRY.values())

# Mapping des catégories vers actions utilisateur (pour intégration chatbot future)
CATEGORY_TO_ACTION_MAPPING = {
    ResourceCategory.CONTACT_URGENCE: "besoin_aide_immediate",
    ResourceCategory.PROCEDURE_PLATEFORME: "signaler_contenu", 
    ResourceCategory.SIGNALEMENT_AUTORITE: "porter_plainte",
    ResourceCategory.ASSOCIATION_LOCALE: "accompagnement_local",
    ResourceCategory.SERVICES_SUPPORT: "conseils_generaux"  # Existant
}

# Validation spécialisée par catégorie
VALIDATION_CRITERIA_BY_CATEGORY = {
    ResourceCategory.CONTACT_URGENCE: {
        "test_appel": "Numéro fonctionnel testé",
        "statut_officiel": "Confirmé gouvernemental/agréé", 
        "specialisation": "Confirmé spécialisé cyberviolence",
        "accessibilite": "Horaires et langue vérifiés"
    },
    ResourceCategory.PROCEDURE_PLATEFORME: {
        "url_valide": "Help center accessible",
        "procedure_actuelle": "Steps testés manuellement",
        "mise_a_jour": "Contenu post-2024", 
        "completude": "Procédure end-to-end fonctionnelle"
    },
    ResourceCategory.SIGNALEMENT_AUTORITE: {
        "site_officiel": "Domaine gouvernemental vérifié",
        "formulaire_actif": "Formulaire testé et fonctionnel",
        "competence_juridiction": "Autorité compétente confirmée",
        "procedure_claire": "Steps de signalement explicites"
    },
    ResourceCategory.ASSOCIATION_LOCALE: {
        "agrement_verifie": "Agrément officiel confirmé",
        "specialisation_cyber": "Spécialisée cyberviolence",
        "zone_geographique": "Zone de couverture vérifiée",
        "accessibilite": "Contact et disponibilité testés"
    }
}