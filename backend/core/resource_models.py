"""
Modèles de données étendus pour les catégories de ressources spécialisées
Selon la logique de sourcing définie dans logic_sourcing_ressources.md
"""

from enum import Enum
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict

class ResourceCategory(Enum):
    """3 catégories cibles V2 selon la stratégie lean

    V2 — SERVICE_SUPPORT remplace contact_urgence + association_locale.
    CONTACT_URGENCE conservé comme alias de rétrocompatibilité.
    """
    # ── Catégories V2 actives ─────────────────────────────────────────────────
    SERVICE_SUPPORT      = "service_support"       # 🛡️ Services d'assistance nationaux
    PROCEDURE_PLATEFORME = "procedure_plateforme"  # 🛠️ Procédures des plateformes numériques
    SIGNALEMENT_AUTORITE = "signalement_autorite"  # ⚖️ Autorités légales officielles

    # ── Alias V1 conservés pour rétrocompatibilité (ne pas utiliser en V2) ───
    CONTACT_URGENCE = "contact_urgence"            # → fusionné dans SERVICE_SUPPORT
    SERVICES_SUPPORT = "services_support"          # → fusionné dans SERVICE_SUPPORT

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
    platform_name: Optional[str] = None           # Pour PROCEDURE_PLATEFORME
    authority_name: Optional[str] = None           # Pour SIGNALEMENT_AUTORITE
    service_scope: Optional[str] = None            # Portée géographique

    # ── Champs V2 ─────────────────────────────────────────────────────────────
    direct_link: str = ""                          # Lien direct formulaire/aide
    is_governmental: bool = False                  # Source gouvernementale officielle
    action_type: str = ""                          # Pour PROCEDURE_PLATEFORME
                                                   #   ex: signalement, blocage, suppression
    scope_audience: str = ""                       # Public visé : "mineurs" | "tous"
    scope_violence: str = ""                       # Type : "cyberviolence" | "tous"
    scope_anonymous: bool = False                  # Signalement anonyme possible

    # Métadonnées de validation
    last_verified: Optional[str] = None            # Date dernière vérification
    verification_notes: Optional[str] = None       # Notes de vérification
    update_frequency: Optional[str] = None         # Fréquence de mise à jour
    
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
    """Targets minimaux par pays selon la stratégie lean V2"""

    TARGETS_PER_COUNTRY = {
        "service_support":       3,   # Services d'assistance nationaux (gov. prioritaires)
        "procedure_plateforme":  5,   # Top 5 plateformes (incl. Discord/WhatsApp/Telegram)
        "signalement_autorite":  4,   # Autorités nationales (PHAROS, Cybermalveillance...)
    }

    # Total par pays : ~12 ressources ciblées (lean vs 100+ extensive)
    TOTAL_TARGET_PER_COUNTRY = sum(TARGETS_PER_COUNTRY.values())

# Mapping des catégories vers actions utilisateur (pour intégration chatbot future)
CATEGORY_TO_ACTION_MAPPING = {
    # V2
    ResourceCategory.SERVICE_SUPPORT:      "besoin_aide",
    ResourceCategory.PROCEDURE_PLATEFORME: "signaler_contenu",
    ResourceCategory.SIGNALEMENT_AUTORITE: "porter_plainte",
    # V1 — alias rétrocompatibilité
    ResourceCategory.CONTACT_URGENCE:      "besoin_aide",
    ResourceCategory.SERVICES_SUPPORT:     "besoin_aide",
}

# Critères de validation par catégorie V2
# Chaque critère est affiché sous forme de checklist dans l'interface admin.
VALIDATION_CRITERIA_BY_CATEGORY = {
    ResourceCategory.SERVICE_SUPPORT: {
        "statut_officiel":   "Source gouvernementale ou officiellement reconnue",
        "public_cible":      "Public visé identifié (mineurs / tous)",
        "direct_link":       "Lien direct vers la page d'aide ou formulaire vérifié",
        "accessibilite":     "Horaires, langue et modalités de contact vérifiés",
    },
    ResourceCategory.PROCEDURE_PLATEFORME: {
        "url_valide":        "Page d'aide officielle de la plateforme accessible",
        "procedure_actuelle": "Procédure testée manuellement (post-2024)",
        "action_type":       "Type d'action identifié (signalement/blocage/suppression)",
        "completude":        "Procédure end-to-end fonctionnelle",
    },
    ResourceCategory.SIGNALEMENT_AUTORITE: {
        "site_officiel":         "Domaine gouvernemental vérifié",
        "formulaire_actif":      "Formulaire ou contact testé et fonctionnel",
        "competence_juridiction": "Autorité compétente pour la cyberviolence confirmée",
        "anonymat":              "Possibilité de signalement anonyme documentée",
    },
    # Alias V1 — redirige vers les critères SERVICE_SUPPORT
    ResourceCategory.CONTACT_URGENCE: {
        "statut_officiel":   "Source gouvernementale ou officiellement reconnue",
        "public_cible":      "Public visé identifié (mineurs / tous)",
        "direct_link":       "Lien direct vers la page d'aide ou formulaire vérifié",
        "accessibilite":     "Horaires, langue et modalités de contact vérifiés",
    },
}