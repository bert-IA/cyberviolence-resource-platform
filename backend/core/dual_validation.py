"""
Système de double validation stricte pour les ressources critiques
ÉTAPE 1: Validation Géographique (Pertinence, Existence, Contact)
ÉTAPE 2: Validation Critique (Sécurité, Fiabilité, RAG-Ready)
NOUVELLE: Critères spécialisés par catégorie de ressource
"""
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any
from enum import Enum
import logging
from dataclasses import dataclass

# Import conditionnel pour éviter les erreurs de dépendance
try:
    from core.resource_models import ResourceCategory, VALIDATION_CRITERIA_BY_CATEGORY
except ImportError:
    logger = logging.getLogger(__name__)
    logger.warning("resource_models non disponible - critères génériques utilisés")
    ResourceCategory = None
    VALIDATION_CRITERIA_BY_CATEGORY = {}

logger = logging.getLogger(__name__)

class ValidationStage(Enum):
    """Étapes de validation strictement ordonnées"""
    DISCOVERED = "discovered"           # Ressource découverte par LLM
    GEO_PENDING = "geo_pending"         # En attente validation géographique
    GEO_VALIDATED = "geo_validated"     # Validée géographiquement
    GEO_REJECTED = "geo_rejected"       # Rejetée géographiquement
    CRITICAL_PENDING = "critical_pending"  # En attente validation critique
    CRITICAL_VALIDATED = "critical_validated"  # Validée pour production
    CRITICAL_REJECTED = "critical_rejected"    # Rejetée définitivement
    RAG_READY = "rag_ready"            # Prête pour intégration RAG

class ValidationAction(Enum):
    """Actions de validation disponibles"""
    APPROVE = "approve"
    REJECT = "reject"  
    REQUEST_MODIFICATION = "request_modification"
    ESCALATE = "escalate"

@dataclass
class ValidationCriteria:
    """Critères de validation par étape ET par catégorie"""
    
    # Validation Géographique (communes à toutes catégories)
    geo_criteria = {
        "existence_verified": "Organisation existe et est active",
        "contact_accessible": "Contact (URL/téléphone) accessible", 
        "mission_relevant": "Mission en rapport avec cyberviolence",
        "geographic_match": "Correspond au pays/région demandé",
        "language_appropriate": "Langue appropriée"
    }
    
    # Validation Critique (communes à toutes catégories)
    critical_criteria = {
        "security_verified": "Sécurité du site/organisation vérifiée",
        "reliability_confirmed": "Fiabilité de l'organisation confirmée",
        "data_accuracy": "Précision des données de contact",
        "professional_standards": "Respect des standards professionnels",
        "legal_compliance": "Conformité légale et éthique"
    }
    
    @staticmethod
    def get_specialized_criteria(category: str, validation_stage: str) -> Dict[str, str]:
        """
        Récupère les critères spécialisés selon la catégorie et l'étape
        
        Args:
            category: Catégorie de ressource (contact_urgence, procedure_plateforme, etc.)
            validation_stage: "geographic" ou "critical"
        
        Returns:
            Dict des critères spécialisés pour cette catégorie
        """
        
        if not VALIDATION_CRITERIA_BY_CATEGORY or not ResourceCategory:
            # Fallback vers critères génériques si models non disponibles
            return ValidationCriteria.critical_criteria if validation_stage == "critical" else ValidationCriteria.geo_criteria
        
        # Mapping string vers enum (V2 : association_locale supprimée)
        category_enum_mapping = {
            "service_support": ResourceCategory.SERVICE_SUPPORT,
            "procedure_plateforme": ResourceCategory.PROCEDURE_PLATEFORME,
            "signalement_autorite": ResourceCategory.SIGNALEMENT_AUTORITE,
            "contact_urgence": ResourceCategory.CONTACT_URGENCE,     # alias V1
            "services_support": ResourceCategory.SERVICES_SUPPORT    # alias V1
        }
        
        category_enum = category_enum_mapping.get(category)
        if not category_enum:
            # Catégorie inconnue → critères génériques
            return ValidationCriteria.critical_criteria if validation_stage == "critical" else ValidationCriteria.geo_criteria
        
        specialized_criteria = VALIDATION_CRITERIA_BY_CATEGORY.get(category_enum, {})
        
        if validation_stage == "geographic":
            # Pour validation géographique : critères génériques + quelques spécialisés
            geo_specialized = {
                **ValidationCriteria.geo_criteria,
                # Ajouter critères spécialisés pertinents pour validation géographique
            }
            
            # Ajouter critères spécialisés selon catégorie
            if category in ("contact_urgence", "service_support", "services_support"):
                geo_specialized["specialisation"] = specialized_criteria.get("specialisation", "Spécialisation cyberviolence vérifiée")
            elif category == "signalement_autorite":
                geo_specialized["site_officiel"] = specialized_criteria.get("site_officiel", "Domaine gouvernemental vérifié")
                
            return geo_specialized
            
        elif validation_stage == "critical":
            # Pour validation critique : tous les critères spécialisés + génériques
            return {
                **ValidationCriteria.critical_criteria,
                **specialized_criteria
            }
        
        return ValidationCriteria.geo_criteria

@dataclass
class ValidationResult:
    """Résultat d'une validation"""
    success: bool
    action: ValidationAction
    validator_id: str
    timestamp: str
    criteria_scores: Dict[str, bool]  # Critère → réussi/échoué
    comments: str
    next_stage: Optional[ValidationStage] = None
    required_modifications: Optional[List[str]] = None

class DualValidationSystem:
    """Système de double validation avec workflow strict"""
    
    # Transitions autorisées entre étapes
    VALID_TRANSITIONS = {
        ValidationStage.DISCOVERED: [ValidationStage.GEO_PENDING],
        ValidationStage.GEO_PENDING: [ValidationStage.GEO_VALIDATED, ValidationStage.GEO_REJECTED],
        ValidationStage.GEO_VALIDATED: [ValidationStage.CRITICAL_PENDING],
        ValidationStage.GEO_REJECTED: [],  # Terminal
        ValidationStage.CRITICAL_PENDING: [ValidationStage.CRITICAL_VALIDATED, ValidationStage.CRITICAL_REJECTED],
        ValidationStage.CRITICAL_VALIDATED: [ValidationStage.RAG_READY],
        ValidationStage.CRITICAL_REJECTED: [],  # Terminal
        ValidationStage.RAG_READY: []  # Terminal
    }
    
    # Actions autorisées par étape
    ALLOWED_ACTIONS = {
        ValidationStage.GEO_PENDING: [ValidationAction.APPROVE, ValidationAction.REJECT, ValidationAction.REQUEST_MODIFICATION],
        ValidationStage.CRITICAL_PENDING: [ValidationAction.APPROVE, ValidationAction.REJECT, ValidationAction.ESCALATE]
    }
    
    def __init__(self, workflow_manager):
        """
        Initialise le système de validation
        workflow_manager: Instance du ResourceWorkflowManager
        """
        self.workflow_manager = workflow_manager
        self.validation_history = {}
    
    def _get_resource_category(self, resource_id: str) -> str:
        """Récupère la catégorie d'une ressource depuis ses métadonnées"""
        try:
            resource_data = self.workflow_manager.unified_data.get(resource_id, {})
            metadata = resource_data.get("metadata", {})
            return metadata.get("category", "services_support")  # Fallback vers existant
        except Exception as e:
            logger.warning(f"Impossible de récupérer la catégorie pour {resource_id}: {e}")
            return "services_support"
    
    def start_geographic_validation(self, resource_id: str) -> bool:
        """Démarre la validation géographique d'une ressource découverte"""
        current_stage = self._get_resource_stage(resource_id)
        
        if current_stage != ValidationStage.DISCOVERED:
            logger.error(f"Ressource {resource_id} pas en statut 'discovered': {current_stage}")
            return False
        
        return self._transition_stage(resource_id, ValidationStage.GEO_PENDING, "system", "Début validation géographique")
    
    def perform_geographic_validation(self, 
                                    resource_id: str, 
                                    validator_id: str,
                                    action: ValidationAction,
                                    criteria_scores: Dict[str, bool],
                                    comments: str = "") -> ValidationResult:
        """Effectue la validation géographique avec critères spécialisés par catégorie"""
        
        current_stage = self._get_resource_stage(resource_id)
        
        if current_stage != ValidationStage.GEO_PENDING:
            raise ValueError(f"Validation géographique impossible: ressource en statut {current_stage}")
        
        if action not in self.ALLOWED_ACTIONS[ValidationStage.GEO_PENDING]:
            raise ValueError(f"Action {action} non autorisée pour validation géographique")
        
        # Récupérer catégorie pour critères spécialisés
        category = self._get_resource_category(resource_id)
        
        # Validation des critères géographiques spécialisés
        required_criteria = ValidationCriteria.get_specialized_criteria(category, "geographic").keys()
        missing_criteria = [criterion for criterion in required_criteria if criterion not in criteria_scores]
        
        if missing_criteria:
            logger.warning(f"Critères manquants pour {category}: {missing_criteria}")
            # En mode dégradé, utiliser seulement les critères fournis
            # raise ValueError(f"Critères manquants pour catégorie {category}: {missing_criteria}")
        
        # Déterminer l'étape suivante
        if action == ValidationAction.APPROVE:
            next_stage = ValidationStage.GEO_VALIDATED
            success = True
        elif action == ValidationAction.REJECT:
            next_stage = ValidationStage.GEO_REJECTED  
            success = False
        else:  # REQUEST_MODIFICATION
            next_stage = ValidationStage.GEO_PENDING  # Reste en pending
            success = False
        
        # Enregistrer le résultat avec métadonnées de catégorie
        result = ValidationResult(
            success=success,
            action=action,
            validator_id=validator_id,
            timestamp=datetime.now().isoformat(),
            criteria_scores=criteria_scores,
            comments=f"[{category}] {comments}",  # Préfixe catégorie
            next_stage=next_stage
        )
        
        # Effectuer la transition
        if next_stage != current_stage:
            self._transition_stage(resource_id, next_stage, validator_id, f"Validation {category}: {comments}")
        
        # Enregistrer dans l'historique avec contexte catégorie
        self._record_validation(resource_id, f"geographic_{category}", result)
        
        return result
    
    def start_critical_validation(self, resource_id: str) -> bool:
        """Démarre la validation critique (automatique après validation géographique)"""
        if not resource_id:
            logger.error("Resource ID vide fourni à start_critical_validation")
            return False
            
        try:
            current_stage = self._get_resource_stage(resource_id)
        except ValueError as e:
            logger.error(f"Ressource {resource_id} non trouvée: {e}")
            return False
        
        if current_stage != ValidationStage.GEO_VALIDATED:
            logger.error(f"Ressource {resource_id} pas validée géographiquement: {current_stage}")
            return False
        
        return self._transition_stage(resource_id, ValidationStage.CRITICAL_PENDING, "system", "Début validation critique")
    
    def perform_critical_validation(self,
                                  resource_id: str,
                                  validator_id: str, 
                                  action: ValidationAction,
                                  criteria_scores: Dict[str, bool],
                                  comments: str = "") -> ValidationResult:
        """Effectue la validation critique avec critères spécialisés par catégorie"""
        
        current_stage = self._get_resource_stage(resource_id)
        
        if current_stage != ValidationStage.CRITICAL_PENDING:
            raise ValueError(f"Validation critique impossible: ressource en statut {current_stage}")
        
        if action not in self.ALLOWED_ACTIONS[ValidationStage.CRITICAL_PENDING]:
            raise ValueError(f"Action {action} non autorisée pour validation critique")
        
        # Récupérer catégorie pour critères spécialisés
        category = self._get_resource_category(resource_id)
        
        # Validation des critères critiques spécialisés
        required_criteria = ValidationCriteria.get_specialized_criteria(category, "critical").keys()
        missing_criteria = [criterion for criterion in required_criteria if criterion not in criteria_scores]
        
        if missing_criteria:
            logger.warning(f"Critères critiques manquants pour {category}: {missing_criteria}")
            # En mode dégradé, utiliser seulement les critères fournis
            # raise ValueError(f"Critères critiques manquants pour catégorie {category}: {missing_criteria}")
        
        # Déterminer l'étape suivante
        if action == ValidationAction.APPROVE:
            next_stage = ValidationStage.CRITICAL_VALIDATED
            success = True
        elif action == ValidationAction.REJECT:
            next_stage = ValidationStage.CRITICAL_REJECTED
            success = False
        else:  # ESCALATE
            next_stage = ValidationStage.CRITICAL_PENDING  # Reste en pending
            success = False
        
        # Enregistrer le résultat avec métadonnées de catégorie
        result = ValidationResult(
            success=success,
            action=action,
            validator_id=validator_id,
            timestamp=datetime.now().isoformat(), 
            criteria_scores=criteria_scores,
            comments=f"[{category}] {comments}",  # Préfixe catégorie
            next_stage=next_stage
        )
        
        # Effectuer la transition
        if next_stage != current_stage:
            self._transition_stage(resource_id, next_stage, validator_id, f"Validation critique {category}: {comments}")
        
        # Enregistrer dans l'historique avec contexte catégorie
        self._record_validation(resource_id, f"critical_{category}", result)
        
        # Déterminer l'étape suivante
        if action == ValidationAction.APPROVE:
            next_stage = ValidationStage.CRITICAL_VALIDATED
            success = True
        elif action == ValidationAction.REJECT:
            next_stage = ValidationStage.CRITICAL_REJECTED
            success = False
        else:  # ESCALATE
            next_stage = ValidationStage.CRITICAL_PENDING  # Reste en pending
            success = False
        
        # Enregistrer le résultat
        result = ValidationResult(
            success=success,
            action=action,
            validator_id=validator_id,
            timestamp=datetime.now().isoformat(), 
            criteria_scores=criteria_scores,
            comments=comments,
            next_stage=next_stage
        )
        
        # Effectuer la transition
        if next_stage != current_stage:
            self._transition_stage(resource_id, next_stage, validator_id, comments)
        
        # Si validée critique → prête pour RAG
        if next_stage == ValidationStage.CRITICAL_VALIDATED:
            self._transition_stage(resource_id, ValidationStage.RAG_READY, validator_id, "Ressource prête pour RAG")
        
        # Enregistrer dans l'historique
        self._record_validation(resource_id, "critical", result)
        
        return result
    
    def get_resources_for_geographic_validation(self) -> Dict[str, dict]:
        """Récupère les ressources en attente de validation géographique"""
        return self.workflow_manager.get_resources_by_status(ValidationStage.GEO_PENDING.value)
    
    def get_resources_for_critical_validation(self) -> Dict[str, dict]:
        """Récupère les ressources en attente de validation critique"""  
        # Récupérer les ressources en critical_pending ET geo_validated (transition automatique)
        critical_pending = self.workflow_manager.get_resources_by_status(ValidationStage.CRITICAL_PENDING.value)
        geo_validated = self.workflow_manager.get_resources_by_status(ValidationStage.GEO_VALIDATED.value)
        
        logger.info(f"Found {len(critical_pending)} critical_pending resources")
        logger.info(f"Found {len(geo_validated)} geo_validated resources")
        
        # Faire la transition automatique de geo_validated vers critical_pending
        for resource_id, resource_data in geo_validated.items():
            try:
                logger.info(f"Auto-transitioning {resource_id} from geo_validated to critical_pending")
                # Déclencher automatiquement la validation critique
                self.start_critical_validation(resource_id)
                # Ajouter à la liste des ressources à valider
                critical_pending[resource_id] = resource_data
            except Exception as e:
                logger.warning(f"Transition automatique échouée pour {resource_id}: {e}")
                # Ajouter quand même à la liste pour affichage
                critical_pending[resource_id] = resource_data
        
        logger.info(f"Returning {len(critical_pending)} resources for critical validation")
        return critical_pending
    
    # === NOUVELLES MÉTHODES POUR CRITÈRES SPÉCIALISÉS ===
    
    def get_required_criteria_for_resource(self, resource_id: str, validation_stage: str) -> Dict[str, str]:
        """
        Récupère les critères requis pour valider une ressource spécifique
        
        Args:
            resource_id: ID de la ressource
            validation_stage: "geographic" ou "critical"
            
        Returns:
            Dict {critère: description} des critères requis pour cette ressource
        """
        category = self._get_resource_category(resource_id)
        return ValidationCriteria.get_specialized_criteria(category, validation_stage)
    
    def validate_criteria_completeness(self, resource_id: str, validation_stage: str, 
                                     provided_criteria: Dict[str, bool]) -> Tuple[bool, List[str]]:
        """
        Valide que tous les critères requis sont fournis
        
        Returns:
            (is_complete, missing_criteria)
        """
        required_criteria = self.get_required_criteria_for_resource(resource_id, validation_stage)
        missing_criteria = [criterion for criterion in required_criteria.keys() 
                          if criterion not in provided_criteria]
        
        return len(missing_criteria) == 0, missing_criteria
    
    def get_validation_template_for_resource(self, resource_id: str, validation_stage: str) -> Dict[str, Any]:
        """
        Génère un template de validation pré-rempli pour une ressource
        Utile pour les interfaces de validation
        
        Returns:
            Template avec critères requis et métadonnées de ressource
        """
        try:
            category = self._get_resource_category(resource_id)
            required_criteria = self.get_required_criteria_for_resource(resource_id, validation_stage)
            
            # Récupérer métadonnées de ressource pour contexte
            resource_data = self.workflow_manager.unified_data.get(resource_id, {})
            metadata = resource_data.get("metadata", {})
            
            template = {
                "resource_id": resource_id,
                "category": category,
                "validation_stage": validation_stage,
                "resource_info": {
                    "name": resource_data.get("organization_name", "N/A"),
                    "country": resource_data.get("country_name", "N/A"),
                    "contact_type": metadata.get("contact_type", "unknown"),
                    "urgency_level": metadata.get("urgency_level", "normal"),
                    "official_status": metadata.get("official_status", "unknown")
                },
                "required_criteria": [
                    {
                        "criterion": criterion,
                        "description": description,
                        "value": None,  # À remplir par le validateur
                        "notes": ""     # Commentaires optionnels
                    }
                    for criterion, description in required_criteria.items()
                ],
                "category_specific_notes": self._get_category_validation_notes(category, validation_stage)
            }
            
            return template
            
        except Exception as e:
            logger.error(f"Erreur génération template pour {resource_id}: {e}")
            return {"error": str(e)}
    
    def _get_category_validation_notes(self, category: str, validation_stage: str) -> List[str]:
        """Notes spécifiques par catégorie pour guider la validation"""
        
        notes_by_category = {
            "contact_urgence": {
                "geographic": [
                    "Vérifier que le numéro est gratuit et accessible",
                    "Confirmer les horaires de disponibilité",
                    "Valider la spécialisation cyberviolence"
                ],
                "critical": [
                    "Tester l'appel téléphonique",
                    "Vérifier l'agrément officiel",
                    "Confirmer la compétence linguistique"
                ]
            },
            "procedure_plateforme": {
                "geographic": [
                    "Vérifier l'URL du help center officiel",
                    "Contrôler que la procédure est récente (2024+)"
                ],
                "critical": [
                    "Tester manuellement les steps de signalement",
                    "Vérifier que la procédure est end-to-end",
                    "Confirmer les délais de traitement annoncés"
                ]
            },
            "signalement_autorite": {
                "geographic": [
                    "Vérifier le domaine gouvernemental (.gouv, etc.)",
                    "Confirmer la compétence juridictionnelle"
                ],
                "critical": [
                    "Tester le formulaire de signalement",
                    "Vérifier l'autorité responsable",
                    "Confirmer les procédures de suivi"
                ]
            },
            "association_locale": {
                "geographic": [
                    "Vérifier la zone géographique de couverture",
                    "Confirmer la spécialisation cyberviolence"
                ],
                "critical": [
                    "Vérifier l'agrément officiel",
                    "Tester l'accessibilité du contact",
                    "Valider les services d'accompagnement"
                ]
            }
        }
        
        return notes_by_category.get(category, {}).get(validation_stage, [
            "Appliquer les critères de validation standard"
        ])

    def get_validation_history(self, resource_id: str) -> List[Dict]:
        """Récupère l'historique de validation d'une ressource"""
        return self.validation_history.get(resource_id, [])
    
    def get_validation_stats(self) -> Dict[str, Any]:
        """Statistiques de validation"""
        stats = {}
        
        # Comptages par étape
        for stage in ValidationStage:
            count = len(self.workflow_manager.get_resources_by_status(stage.value))
            stats[stage.value] = count
        
        # Taux de réussite
        total_geo_validations = stats.get(ValidationStage.GEO_VALIDATED.value, 0) + stats.get(ValidationStage.GEO_REJECTED.value, 0)
        total_critical_validations = stats.get(ValidationStage.CRITICAL_VALIDATED.value, 0) + stats.get(ValidationStage.CRITICAL_REJECTED.value, 0)
        
        if total_geo_validations > 0:
            stats["geo_success_rate"] = round((stats.get(ValidationStage.GEO_VALIDATED.value, 0) / total_geo_validations) * 100, 2)
        
        if total_critical_validations > 0:
            stats["critical_success_rate"] = round((stats.get(ValidationStage.CRITICAL_VALIDATED.value, 0) / total_critical_validations) * 100, 2)
        
        # Ressources prêtes pour RAG
        stats["rag_ready_count"] = stats.get(ValidationStage.RAG_READY.value, 0)
        
        return stats
    
    def _get_resource_stage(self, resource_id: str) -> ValidationStage:
        """Récupère l'étape actuelle d'une ressource"""
        resource_data = self.workflow_manager.unified_data.get(resource_id)
        if not resource_data:
            raise ValueError(f"Ressource {resource_id} non trouvée")
        
        status = resource_data.get("workflow_status", "discovered")
        return ValidationStage(status)
    
    def _transition_stage(self, resource_id: str, new_stage: ValidationStage, actor_id: str, notes: str) -> bool:
        """Effectue une transition d'étape avec validation"""
        current_stage = self._get_resource_stage(resource_id)
        
        # Vérifier que la transition est autorisée
        if new_stage not in self.VALID_TRANSITIONS.get(current_stage, []):
            logger.error(f"Transition interdite: {current_stage} → {new_stage}")
            return False
        
        # Effectuer la transition via le workflow manager
        return self.workflow_manager.transition_status(resource_id, new_stage.value, actor_id, notes)
    
    def _record_validation(self, resource_id: str, validation_type: str, result: ValidationResult):
        """Enregistre une validation dans l'historique"""
        if resource_id not in self.validation_history:
            self.validation_history[resource_id] = []
        
        self.validation_history[resource_id].append({
            "type": validation_type,
            "result": result.__dict__,
            "recorded_at": datetime.now().isoformat()
        })

# Instance singleton
_validation_system = None

def get_validation_system(workflow_manager) -> DualValidationSystem:
    """Récupère l'instance singleton du système de validation"""
    global _validation_system
    if _validation_system is None:
        _validation_system = DualValidationSystem(workflow_manager)
    return _validation_system