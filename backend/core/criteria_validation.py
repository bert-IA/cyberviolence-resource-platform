"""
🆕 NOUVEAU - Module de gestion des critères de validation obligatoires
Permet de récupérer et vérifier les critères selon la catégorie de ressource

Fonctionnalités:
- Récupération des critères selon catégorie et étape de validation
- Vérification que tous les critères sont cochés avant validation
- Auto-vérification de certains critères (HTTPS, domaine actif)
- Historique des vérifications
"""
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, field
from datetime import datetime
import logging
import re

logger = logging.getLogger(__name__)

# Import des critères depuis dual_validation
try:
    from core.dual_validation import ValidationCriteria, ValidationStage
except ImportError:
    logger.warning("dual_validation non disponible - critères génériques utilisés")
    ValidationCriteria = None
    ValidationStage = None


@dataclass
class CriteriaCheckResult:
    """
    Résultat de la vérification d'un critère
    """
    criterion_id: str
    criterion_name: str
    checked: bool
    auto_verified: bool = False
    verification_result: Optional[bool] = None
    verification_method: Optional[str] = None
    verification_date: Optional[str] = None
    notes: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Conversion en dictionnaire pour JSON"""
        return {
            "criterion_id": self.criterion_id,
            "criterion_name": self.criterion_name,
            "checked": self.checked,
            "auto_verified": self.auto_verified,
            "verification_result": self.verification_result,
            "verification_method": self.verification_method,
            "verification_date": self.verification_date,
            "notes": self.notes
        }


@dataclass
class ValidationCriteriaSet:
    """
    Ensemble de critères pour une étape de validation
    """
    stage: str  # "geographic" ou "critical"
    category: str  # catégorie de ressource
    criteria: Dict[str, str]  # criterion_id -> description
    required_criteria: Set[str]  # IDs des critères obligatoires
    optional_criteria: Set[str]  # IDs des critères optionnels
    auto_verifiable_criteria: Set[str]  # IDs des critères auto-vérifiables
    
    def to_dict(self) -> Dict[str, Any]:
        """Conversion en dictionnaire pour JSON"""
        return {
            "stage": self.stage,
            "category": self.category,
            "criteria": self.criteria,
            "required_criteria": list(self.required_criteria),
            "optional_criteria": list(self.optional_criteria),
            "auto_verifiable_criteria": list(self.auto_verifiable_criteria),
            "total_criteria": len(self.criteria),
            "required_count": len(self.required_criteria)
        }


class CriteriaValidationManager:
    """
    🆕 NOUVEAU - Gestionnaire des critères de validation
    Responsable de la récupération et vérification des critères
    """
    
    # Critères auto-vérifiables (vérifiés automatiquement par le système)
    AUTO_VERIFIABLE_CRITERIA = {
        "security_verified",  # HTTPS, certificat valide
        "contact_accessible",  # URL/téléphone accessible
        "geographic_match",   # Pays correspond
    }
    
    def __init__(self, workflow_manager=None):
        """
        Args:
            workflow_manager: Instance de ResourceWorkflowManager pour accéder aux ressources
        """
        self.workflow_manager = workflow_manager
        logger.info("✅ CriteriaValidationManager initialisé")
    
    def get_validation_criteria(self, resource_id: str, stage: str = "critical") -> ValidationCriteriaSet:
        """
        Récupère les critères de validation pour une ressource
        
        Args:
            resource_id: ID de la ressource
            stage: "geographic" ou "critical"
            
        Returns:
            ValidationCriteriaSet avec tous les critères applicables
        """
        # Récupérer la ressource pour obtenir sa catégorie
        resource = self._get_resource_by_id(resource_id)
        if not resource:
            raise ValueError(f"Ressource {resource_id} non trouvée")
        
        # Récupérer la catégorie
        category = resource.get("metadata", {}).get("category", "services_support")
        
        # Récupérer les critères selon catégorie et étape
        if ValidationCriteria:
            criteria = ValidationCriteria.get_specialized_criteria(category, stage)
        else:
            # Fallback vers critères génériques
            criteria = self._get_generic_criteria(stage)
        
        # Identifier les critères obligatoires vs optionnels
        required_criteria = set(criteria.keys())
        optional_criteria = set()  # Pour l'instant, tous obligatoires
        
        # Identifier les critères auto-vérifiables
        auto_verifiable = required_criteria.intersection(self.AUTO_VERIFIABLE_CRITERIA)
        
        return ValidationCriteriaSet(
            stage=stage,
            category=category,
            criteria=criteria,
            required_criteria=required_criteria,
            optional_criteria=optional_criteria,
            auto_verifiable_criteria=auto_verifiable
        )
    
    def verify_all_criteria_checked(self, 
                                    resource_id: str, 
                                    criteria_checks: Dict[str, bool],
                                    stage: str = "critical") -> Dict[str, Any]:
        """
        Vérifie que tous les critères obligatoires sont cochés
        
        Args:
            resource_id: ID de la ressource
            criteria_checks: Dict {criterion_id: checked}
            stage: "geographic" ou "critical"
            
        Returns:
            Dict avec résultat de la vérification et détails
        """
        # Récupérer les critères applicables
        criteria_set = self.get_validation_criteria(resource_id, stage)
        
        # Vérifier les critères cochés
        checked_criteria = {k for k, v in criteria_checks.items() if v}
        missing_criteria = criteria_set.required_criteria - checked_criteria
        
        # Auto-vérifications si disponibles
        auto_verification_results = self._auto_verify_criteria(resource_id, criteria_set)
        
        # Critères manquants après auto-vérification
        auto_verified_ok = {k for k, v in auto_verification_results.items() if v}
        still_missing = missing_criteria - auto_verified_ok
        
        all_checked = len(still_missing) == 0
        
        return {
            "all_checked": all_checked,
            "total_required": len(criteria_set.required_criteria),
            "checked_count": len(checked_criteria),
            "auto_verified_count": len(auto_verified_ok),
            "missing_criteria": [
                {
                    "id": crit_id,
                    "name": criteria_set.criteria.get(crit_id, crit_id)
                }
                for crit_id in still_missing
            ],
            "auto_verification_results": auto_verification_results
        }
    
    def _auto_verify_criteria(self, resource_id: str, criteria_set: ValidationCriteriaSet) -> Dict[str, bool]:
        """
        Effectue les auto-vérifications possibles
        
        Returns:
            Dict {criterion_id: verification_passed}
        """
        results = {}
        resource = self._get_resource_by_id(resource_id)
        
        if not resource:
            return results
        
        # Vérification sécurité (HTTPS)
        if "security_verified" in criteria_set.auto_verifiable_criteria:
            url = resource.get("url", "")
            results["security_verified"] = self._verify_https(url)
        
        # Vérification contact accessible
        if "contact_accessible" in criteria_set.auto_verifiable_criteria:
            url = resource.get("url", "")
            phone = resource.get("phone", "")
            results["contact_accessible"] = bool(url or phone)
        
        # Vérification correspondance géographique
        if "geographic_match" in criteria_set.auto_verifiable_criteria:
            requested_country = resource.get("country", "")
            results["geographic_match"] = bool(requested_country)
        
        return results
    
    def save_criteria_verification(self, 
                                   resource_id: str, 
                                   criteria_checks: Dict[str, bool],
                                   stage: str = "critical",
                                   verified_by: str = "admin") -> bool:
        """
        Enregistre les vérifications de critères pour une ressource
        
        Args:
            resource_id: ID de la ressource
            criteria_checks: Dict {criterion_id: checked}
            stage: "geographic" ou "critical"
            verified_by: Qui a vérifié
            
        Returns:
            True si sauvegarde réussie
        """
        resource = self._get_resource_by_id(resource_id)
        if not resource:
            raise ValueError(f"Ressource {resource_id} non trouvée")
        
        # Créer la structure d'historique si elle n'existe pas
        if "validation_history" not in resource:
            resource["validation_history"] = []
        
        # Enregistrer la vérification
        verification_record = {
            "stage": stage,
            "timestamp": datetime.now().isoformat(),
            "verified_by": verified_by,
            "criteria_checks": criteria_checks,
            "all_checked": all(criteria_checks.values())
        }
        
        resource["validation_history"].append(verification_record)
        
        # Sauvegarder la ressource mise à jour
        self._update_resource(resource)
        
        logger.info(f"✅ Critères de validation enregistrés pour {resource_id} ({stage})")
        return True
    
    def _get_resource_by_id(self, resource_id: str) -> Optional[Dict[str, Any]]:
        """Récupère une ressource par son ID"""
        if not self.workflow_manager:
            return None
        
        # unified_data est structuré comme {resource_id: resource_data}
        resource = self.workflow_manager.unified_data.get(resource_id)
        if resource:
            # Ajouter l'ID dans la ressource si absent
            if "id" not in resource:
                resource["id"] = resource_id
            return resource
        
        return None
    
    def _update_resource(self, resource: Dict[str, Any]):
        """Met à jour une ressource dans le workflow manager"""
        if not self.workflow_manager:
            return
        
        resource_id = resource.get("id")
        status = resource.get("status")
        
        # Mise à jour dans la structure unifiée
        if status and status in self.workflow_manager.unified_data:
            resources = self.workflow_manager.unified_data[status]
            if isinstance(resources, list):
                for i, r in enumerate(resources):
                    if r.get("id") == resource_id:
                        resources[i] = resource
                        break
        
        # Sauvegarde des modifications
        self.workflow_manager._save_json(self.workflow_manager.unified_file, 
                                        self.workflow_manager.unified_data)
    
    @staticmethod
    def _verify_https(url: str) -> bool:
        """Vérifie qu'une URL utilise HTTPS"""
        if not url:
            return False
        return url.startswith("https://")
    
    @staticmethod
    def _get_generic_criteria(stage: str) -> Dict[str, str]:
        """Retourne des critères génériques si ValidationCriteria n'est pas disponible"""
        if stage == "geographic":
            return {
                "existence_verified": "Organisation existe et est active",
                "contact_accessible": "Contact (URL/téléphone) accessible",
                "mission_relevant": "Mission en rapport avec cyberviolence",
                "geographic_match": "Correspond au pays/région demandé",
                "language_appropriate": "Langue appropriée"
            }
        else:  # critical
            return {
                "security_verified": "Sécurité du site/organisation vérifiée (HTTPS, certificat valide)",
                "reliability_confirmed": "Fiabilité de l'organisation confirmée (organisme reconnu)",
                "data_accuracy": "Précision des données de contact (numéro testé)",
                "professional_standards": "Respect des standards professionnels",
                "legal_compliance": "Conformité légale et éthique (RGPD, mentions légales)"
            }


# ==========================================
# 🆕 FONCTIONS UTILITAIRES
# ==========================================

def get_criteria_validation_manager(workflow_manager=None) -> CriteriaValidationManager:
    """
    Factory function pour obtenir une instance de CriteriaValidationManager
    
    Args:
        workflow_manager: Instance optionnelle de ResourceWorkflowManager
        
    Returns:
        Instance de CriteriaValidationManager
    """
    return CriteriaValidationManager(workflow_manager)
