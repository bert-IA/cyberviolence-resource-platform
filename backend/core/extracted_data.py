"""
🆕 NOUVEAU - Module de gestion des données extraites
Permet l'extraction et la modification des données de contact depuis les ressources

Fonctionnalités:
- Extraction des données de contact (téléphone, URL, email, horaires)  
- Modification inline des données extraites
- Validation des formats de contact
- Historique des modifications
"""
from dataclasses import dataclass, asdict, field
from typing import Optional, Dict, Any, List
from datetime import datetime
import re
import logging

logger = logging.getLogger(__name__)


@dataclass
class ExtractedContactData:
    """
    Données de contact extraites d'une ressource
    Utilisé pour l'édition inline (Interface 4 - Section 1)
    """
    # Données de contact principales
    phone: Optional[str] = None
    url: Optional[str] = None
    email: Optional[str] = None
    
    # Type de contact principal
    contact_type: str = "phone"  # phone, online, email, form, app
    
    # Disponibilité
    availability: Dict[str, Any] = field(default_factory=lambda: {
        "type": "24h",  # 24h, business_hours, specific_schedule
        "details": "",  # Ex: "7j/7, 9h-23h"
        "schedule": {}  # Horaires détaillés si specific_schedule
    })
    
    # Métadonnées d'extraction
    extraction_date: Optional[str] = None
    extraction_method: str = "llm"  # llm, manual, auto
    confidence: float = 0.0  # Confiance de l'extraction (0-1)
    
    # Informations de vérification
    phone_verified: bool = False
    url_verified: bool = False
    email_verified: bool = False
    
    # Historique des modifications
    modification_history: List[Dict[str, Any]] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Conversion en dictionnaire pour JSON"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ExtractedContactData':
        """Création depuis dictionnaire JSON"""
        # Enlever les champs qui ne sont pas dans le dataclass
        valid_fields = {f for f in cls.__dataclass_fields__}
        filtered_data = {k: v for k, v in data.items() if k in valid_fields}
        return cls(**filtered_data)
    
    def add_modification(self, field_name: str, old_value: Any, new_value: Any, 
                        modified_by: str = "admin"):
        """Ajoute une entrée dans l'historique des modifications"""
        modification = {
            "timestamp": datetime.now().isoformat(),
            "field": field_name,
            "old_value": old_value,
            "new_value": new_value,
            "modified_by": modified_by
        }
        self.modification_history.append(modification)
        logger.info(f"Modification enregistrée: {field_name} modifié par {modified_by}")


class ExtractedDataManager:
    """
    🆕 NOUVEAU - Gestionnaire des données extraites
    Responsable de l'extraction et de la mise à jour des données de contact
    """
    
    def __init__(self, workflow_manager=None):
        """
        Args:
            workflow_manager: Instance de ResourceWorkflowManager pour accéder aux ressources
        """
        self.workflow_manager = workflow_manager
        logger.info("✅ ExtractedDataManager initialisé")
    
    def extract_contact_data(self, resource: Dict[str, Any]) -> ExtractedContactData:
        """
        Extrait les données de contact depuis une ressource
        
        Args:
            resource: Dictionnaire contenant les données de la ressource
            
        Returns:
            ExtractedContactData avec les informations extraites
        """
        # Extraction des données depuis la ressource
        extracted = ExtractedContactData()
        
        # Extraction du téléphone
        if "phone" in resource:
            extracted.phone = resource["phone"]
            extracted.phone_verified = resource.get("phone_verified", False)
        
        # Extraction de l'URL (website dans la structure LLM)
        if "website" in resource:
            extracted.url = resource["website"]
            extracted.url_verified = self._verify_url(resource["website"])
        elif "url" in resource:  # Compatibilité ancienne structure
            extracted.url = resource["url"]
            extracted.url_verified = self._verify_url(resource["url"])
        
        # Extraction de l'email
        if "email" in resource:
            extracted.email = resource["email"]
            extracted.email_verified = self._verify_email(resource["email"])
        
        # Extraction du type de contact
        if "metadata" in resource and "contact_type" in resource["metadata"]:
            extracted.contact_type = resource["metadata"]["contact_type"]
        elif extracted.phone:
            extracted.contact_type = "phone"
        elif extracted.url:
            extracted.contact_type = "online"
        elif extracted.email:
            extracted.contact_type = "email"
        
        # Extraction de la disponibilité
        if "metadata" in resource:
            metadata = resource["metadata"]
            if "availability" in metadata:
                extracted.availability["type"] = metadata["availability"]
            if "availability_details" in metadata:
                extracted.availability["details"] = metadata["availability_details"]
        
        # Métadonnées d'extraction
        extracted.extraction_date = datetime.now().isoformat()
        extracted.extraction_method = resource.get("extraction_method", "llm")
        extracted.confidence = resource.get("confidence", 0.8)
        
        logger.info(f"Données extraites pour ressource ID: {resource.get('id', 'unknown')}")
        return extracted
    
    def update_contact_data(self, resource_id: str, updated_data: Dict[str, Any], 
                           modified_by: str = "admin") -> Dict[str, Any]:
        """
        Met à jour les données de contact d'une ressource
        
        Args:
            resource_id: ID de la ressource à modifier
            updated_data: Nouvelles données de contact
            modified_by: Qui a effectué la modification
            
        Returns:
            Ressource mise à jour avec les nouvelles données
        """
        if not self.workflow_manager:
            raise ValueError("Workflow manager non initialisé")
        
        # Récupération de la ressource
        resource = self._get_resource_by_id(resource_id)
        if not resource:
            raise ValueError(f"Ressource {resource_id} non trouvée")
        
        # Extraction des données actuelles
        current_data = self.extract_contact_data(resource)
        
        # Mise à jour des champs modifiés
        modifications = []
        
        # Mise à jour du téléphone
        if "phone" in updated_data and updated_data["phone"] != current_data.phone:
            current_data.add_modification("phone", current_data.phone, 
                                         updated_data["phone"], modified_by)
            resource["phone"] = updated_data["phone"]
            modifications.append("phone")
        
        # Mise à jour de l'URL (website dans la structure LLM)
        if "url" in updated_data and updated_data["url"] != current_data.url:
            current_data.add_modification("url", current_data.url, 
                                         updated_data["url"], modified_by)
            resource["website"] = updated_data["url"]  # Structure LLM utilise "website"
            resource["url_verified"] = self._verify_url(updated_data["url"])
            modifications.append("url")
        
        # Mise à jour de l'email
        if "email" in updated_data and updated_data["email"] != current_data.email:
            current_data.add_modification("email", current_data.email, 
                                         updated_data["email"], modified_by)
            resource["email"] = updated_data["email"]
            resource["email_verified"] = self._verify_email(updated_data["email"])
            modifications.append("email")
        
        # Mise à jour du type de contact
        if "contact_type" in updated_data:
            if "metadata" not in resource:
                resource["metadata"] = {}
            old_type = resource["metadata"].get("contact_type")
            if updated_data["contact_type"] != old_type:
                current_data.add_modification("contact_type", old_type, 
                                             updated_data["contact_type"], modified_by)
                resource["metadata"]["contact_type"] = updated_data["contact_type"]
                modifications.append("contact_type")
        
        # Mise à jour de la disponibilité
        if "availability" in updated_data:
            if "metadata" not in resource:
                resource["metadata"] = {}
            
            avail_data = updated_data["availability"]
            if "type" in avail_data:
                old_avail = resource["metadata"].get("availability")
                if avail_data["type"] != old_avail:
                    current_data.add_modification("availability", old_avail, 
                                                 avail_data["type"], modified_by)
                    resource["metadata"]["availability"] = avail_data["type"]
                    modifications.append("availability")
            
            if "details" in avail_data:
                resource["metadata"]["availability_details"] = avail_data["details"]
        
        # Enregistrement de l'historique des modifications
        if "extraction_data" not in resource:
            resource["extraction_data"] = {}
        resource["extraction_data"]["modification_history"] = current_data.modification_history
        resource["extraction_data"]["last_modified"] = datetime.now().isoformat()
        resource["extraction_data"]["last_modified_by"] = modified_by
        
        # Sauvegarde de la ressource mise à jour
        self._update_resource(resource)
        
        logger.info(f"✅ Ressource {resource_id} mise à jour. Champs modifiés: {', '.join(modifications)}")
        return resource
    
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
    def _verify_url(url: str) -> bool:
        """
        Vérifie basiquement le format d'une URL
        Note: Pour une vérification complète (HTTPS, certificat), 
        voir auto_verification dans dual_validation.py
        """
        if not url:
            return False
        
        # Vérification basique du format
        url_pattern = re.compile(
            r'^https?://'  # http:// ou https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domaine
            r'localhost|'  # localhost
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ou IP
            r'(?::\d+)?'  # port optionnel
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        
        return bool(url_pattern.match(url))
    
    @staticmethod
    def _verify_email(email: str) -> bool:
        """Vérifie basiquement le format d'un email"""
        if not email:
            return False
        
        # Vérification basique du format email
        email_pattern = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
        return bool(email_pattern.match(email))


# ==========================================
# 🆕 FONCTIONS UTILITAIRES
# ==========================================

def get_extracted_data_manager(workflow_manager=None) -> ExtractedDataManager:
    """
    Factory function pour obtenir une instance d'ExtractedDataManager
    
    Args:
        workflow_manager: Instance optionnelle de ResourceWorkflowManager
        
    Returns:
        Instance d'ExtractedDataManager
    """
    return ExtractedDataManager(workflow_manager)
