"""
Gestionnaire de workflow optimisé pour les ressources critiques
Séparation des responsabilités et optimisation pour le RAG

Intègre:
- WorkflowStatus: State machine (discovered → geo_pending → ... → rag_ready)
- DeduplicationService: Détection et nettoyage doublons
- PriorityDiscoveryService: Gestion priorités découverte
"""
from datetime import datetime
from typing import Dict, List, Optional
import json
import logging

logger = logging.getLogger(__name__)

# Import conditionnel pour éviter les erreurs de dépendance
try:
    from core.resource_models import ResourceMetadata, ResourceCategory, UrgencyLevel, ContactType, Availability, OfficialStatus, TestStatus
except ImportError:
    logger.warning("resource_models non disponible - fonctionnalités limitées")
    ResourceMetadata = None

# Import des services fusionnés
try:
    from core.deduplication_service import DeduplicationService
except ImportError:
    logger.warning("deduplication_service non disponible")
    DeduplicationService = None

try:
    from core.priority_discovery_service import PriorityDiscoveryService
except ImportError:
    logger.warning("priority_discovery_service non disponible")
    PriorityDiscoveryService = None

class WorkflowStatus:
    DISCOVERED = "discovered"
    GEO_PENDING = "geo_pending"
    GEO_VALIDATED = "geo_validated" 
    GEO_REJECTED = "geo_rejected"
    CRITICAL_PENDING = "critical_pending"
    CRITICAL_VALIDATED = "critical_validated"
    CRITICAL_REJECTED = "critical_rejected"
    RAG_READY = "rag_ready"
    
    VALID_TRANSITIONS = {
        DISCOVERED: [GEO_PENDING],
        GEO_PENDING: [GEO_VALIDATED, GEO_REJECTED],
        GEO_VALIDATED: [CRITICAL_PENDING],
        CRITICAL_PENDING: [CRITICAL_VALIDATED, CRITICAL_REJECTED],
        CRITICAL_VALIDATED: [RAG_READY],
        GEO_REJECTED: [],  # État terminal
        CRITICAL_REJECTED: [],  # État terminal
        RAG_READY: []      # État terminal
    }

class ResourceWorkflowManager:
    def __init__(self, 
                 unified_file="working_resources.json",  # ✅ working_resources.json par défaut
                 rag_file="rag_resources.json"):
        self.unified_file = unified_file
        self.rag_file = rag_file
        
        # Chargement des données
        # Toutes les ressources sont dans le fichier unifié, classées par statut
        self.unified_data = self._load_json(unified_file)
        # Seules les ressources finales RAG sont dans un fichier séparé
        self.rag_data = self._load_json(rag_file)
        
        # ==========================================
        # 🔧 INITIALISATION DES SERVICES FUSIONNÉS
        # ==========================================
        
        # Service de déduplication (détection + nettoyage doublons)
        self.deduplication_service = None
        if DeduplicationService:
            self.deduplication_service = DeduplicationService()
            logger.info("✅ DeduplicationService initialisé")
        
        # Service de priorités découverte (gestion stratégique)
        self.priority_discovery_service = None
        if PriorityDiscoveryService:
            self.priority_discovery_service = PriorityDiscoveryService()
            logger.info("✅ PriorityDiscoveryService initialisé")
        
        # PRÉVENTION : Synchronisation automatique au démarrage
        self.sync_rag_data()
    
    def _load_json(self, filename: str) -> dict:
        """Charge un fichier JSON de façon sécurisée"""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}
        except json.JSONDecodeError:
            logger.error(f"Erreur JSON dans {filename}")
            return {}
    
    def _save_json(self, data: dict, filename: str):
        """Sauvegarde sécurisée d'un fichier JSON"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Erreur sauvegarde {filename}: {e}")
    
    def clean_utf8_encoding(self, text: str) -> str:
        """
        Nettoie les problèmes d'encodage UTF-8 courants
        Exemple: 'Net Ã‰coute' → 'Net Écoute'
        """
        if not isinstance(text, str):
            return text
        
        # Corrections spécifiques UTF-8
        corrections = {
            'Ã‰': 'É',
            'Ã©': 'é', 
            'Ã€': 'À',
            'Ã ': 'à',
            'Ãª': 'ê',
            'Ã´': 'ô',
            'Ã§': 'ç',
            'Ã¹': 'ù',
            'Ã®': 'î',
            'Ã¢': 'â'
        }
        
        for bad, good in corrections.items():
            text = text.replace(bad, good)
        
        return text
    
    def add_discovered_resource(self, resource_id: str, llm_data: dict, metadata: Optional[Dict] = None) -> bool:
        """
        Ajoute une ressource découverte par LLM avec métadonnées enrichies
        
        Args:
            resource_id: Identifiant unique de la ressource
            llm_data: Données de base découvertes par LLM (nom, description, contact, etc.)
            metadata: Métadonnées enrichies selon ResourceMetadata (catégorie, urgence, etc.)
        """
        # Nettoyer l'encodage UTF-8 avant sauvegarde
        if 'name' in llm_data:
            llm_data['name'] = self.clean_utf8_encoding(llm_data['name'])
        if 'description' in llm_data:
            llm_data['description'] = self.clean_utf8_encoding(llm_data['description'])
        
        unified_entry = {
            **llm_data,
            "workflow_status": WorkflowStatus.DISCOVERED,
            "created_at": datetime.now().isoformat(),
            "validation_history": []
        }
        
        # Ajouter métadonnées enrichies si fournies
        if metadata:
            unified_entry["metadata"] = metadata
        else:
            # Métadonnées par défaut pour compatibilité rétrograde
            unified_entry["metadata"] = {
                "category": "services_support",  # Valeur par défaut (existant)
                "urgency_level": "normal",
                "contact_type": "phone",
                "availability": "business_hours", 
                "official_status": "approved",
                "test_status": "not_tested"
            }
        
        self.unified_data[resource_id] = unified_entry
        self._save_json(self.unified_data, self.unified_file)
        return True
    
    def add_discovered_resource_with_category(self, resource_id: str, llm_data: dict, 
                                            category: str, urgency_level: str = "normal",
                                            contact_type: str = "phone", availability: str = "business_hours",
                                            official_status: str = "approved") -> bool:
        """
        Méthode convenience pour ajouter une ressource avec catégorie spécifique
        Facilite l'intégration avec les nouvelles discovery ciblées
        """
        metadata = {
            "category": category,
            "urgency_level": urgency_level,
            "contact_type": contact_type,
            "availability": availability,
            "official_status": official_status,
            "test_status": "not_tested",
            "last_verified": None,
            "verification_notes": None
        }
        
        return self.add_discovered_resource(resource_id, llm_data, metadata)
    
    def transition_status(self, resource_id: str, new_status: str, admin_id: str, notes: str = "") -> bool:
        """Transition sécurisée de statut avec validation"""
        if resource_id not in self.unified_data:
            return False
        
        current_status = self.unified_data[resource_id].get("workflow_status")
        
        # Vérifier que la transition est valide
        if new_status not in WorkflowStatus.VALID_TRANSITIONS.get(current_status, []):
            logger.error(f"Transition invalide: {current_status} → {new_status}")
            return False
        
        # Effectuer la transition
        self.unified_data[resource_id]["workflow_status"] = new_status
        self.unified_data[resource_id]["validation_history"].append({
            "from_status": current_status,
            "to_status": new_status,
            "admin_id": admin_id,
            "timestamp": datetime.now().isoformat(),
            "notes": notes
        })
        
        # Si validation critique complète → copier vers rag_resources pour export final
        if new_status == WorkflowStatus.RAG_READY:
            self._update_rag_resources(resource_id)
        
        self._save_json(self.unified_data, self.unified_file)
        return True
    
    def _update_rag_resources(self, resource_id: str):
        """Copie une ressource finalisée vers rag_resources.json pour export"""
        
        # VALIDATION STRICTE : s'assurer que la source existe et est rag_ready
        if resource_id not in self.unified_data:
            logger.error(f"DÉSYNCHRONISATION ÉVITÉE: resource_id {resource_id} absent de unified_data")
            return False
        
        unified_resource = self.unified_data[resource_id]
        current_status = unified_resource.get("workflow_status")
        
        if current_status != "rag_ready":
            logger.error(f"DÉSYNCHRONISATION ÉVITÉE: resource_id {resource_id} pas en status rag_ready (statut: {current_status})")
            return False
        
        # Récupérer les données de contact de manière robuste
        phone = (unified_resource.get("core_data", {}).get("phone") or 
                unified_resource.get("phone") or 
                unified_resource.get("contact_info", {}).get("phone") or "")
        
        email = (unified_resource.get("core_data", {}).get("email") or 
                unified_resource.get("email") or 
                unified_resource.get("contact_info", {}).get("email") or "")
        
        website = (unified_resource.get("core_data", {}).get("website") or 
                  unified_resource.get("website") or "")
        
        organization_name = (unified_resource.get("core_data", {}).get("organization_name") or 
                           unified_resource.get("organization_name") or "")
        
        description = (unified_resource.get("core_data", {}).get("description") or 
                      unified_resource.get("description") or "")
        
        country_name = (unified_resource.get("core_data", {}).get("country_name") or 
                       unified_resource.get("country_name") or "")
        
        # Format optimisé pour RAG (avec toutes les données disponibles)
        rag_entry = {
            "organization_name": organization_name,
            "website": website,
            "description": description,
            "phone": phone,
            "email": email,
            "country_name": country_name,
            "contact_info": {
                "phone": phone,
                "email": email
            },
            "metadata": {
                "country": country_name,
                "language": unified_resource.get("language", "FR"),
                "type": unified_resource.get("resource_type", "association"),
                "finalized_at": datetime.now().isoformat(),
                "source": "llm_discovery"
            }
        }
        
        self.rag_data[resource_id] = rag_entry
        self._save_json(self.rag_data, self.rag_file)
        logger.info(f"Resource {resource_id} successfully added to RAG")
        return True
    
    def sync_rag_data(self):
        """Synchronise rag_data avec unified_data pour éviter les incohérences"""
        logger.info("Début de synchronisation RAG...")
        
        cleaned_count = 0
        orphaned_keys = []
        
        # Identifier les sources orphelines dans rag_data
        for rag_id in list(self.rag_data.keys()):
            if rag_id not in self.unified_data:
                orphaned_keys.append(rag_id)
            elif self.unified_data[rag_id].get("workflow_status") != "rag_ready":
                orphaned_keys.append(rag_id)
        
        # Supprimer les sources orphelines
        for orphaned_id in orphaned_keys:
            logger.warning(f"Suppression source orpheline RAG: {orphaned_id}")
            del self.rag_data[orphaned_id]
            cleaned_count += 1
        
        # Ajouter les sources rag_ready manquantes
        for unified_id, resource in self.unified_data.items():
            if (resource.get("workflow_status") == "rag_ready" and 
                unified_id not in self.rag_data):
                logger.info(f"Ajout source RAG manquante: {unified_id}")
                self._update_rag_resources(unified_id)
        
        # Sauvegarder si des changements ont été faits
        if cleaned_count > 0:
            self._save_json(self.rag_data, self.rag_file)
            logger.info(f"Synchronisation terminée: {cleaned_count} sources orphelines supprimées")
        else:
            logger.info("Synchronisation terminée: aucune incohérence trouvée")
        
        return cleaned_count
    
    def get_resources_by_category(self, category: str, status: Optional[str] = None) -> Dict[str, dict]:
        """
        Récupère les ressources par catégorie
        
        Args:
            category: Catégorie de ressource (contact_urgence, procedure_plateforme, etc.)
            status: Statut de workflow optionnel pour filtrer davantage
        """
        filtered_resources = {}
        
        for resource_id, resource_data in self.unified_data.items():
            # Vérifier la catégorie
            resource_category = resource_data.get("metadata", {}).get("category")
            if resource_category == category:
                # Vérifier le statut si spécifié
                if status is None or resource_data.get("workflow_status") == status:
                    filtered_resources[resource_id] = resource_data
        
        return filtered_resources
    
    def get_resources_by_country_and_category(self, country_code: str, category: str, 
                                            status: Optional[str] = None) -> Dict[str, dict]:
        """
        Récupère les ressources par pays ET catégorie 
        Utile pour la stratégie lean (16 ressources max par pays)
        """
        filtered_resources = {}
        
        for resource_id, resource_data in self.unified_data.items():
            # Vérifier pays ET catégorie
            if (resource_data.get("country_code") == country_code and 
                resource_data.get("metadata", {}).get("category") == category):
                # Vérifier le statut si spécifié
                if status is None or resource_data.get("workflow_status") == status:
                    filtered_resources[resource_id] = resource_data
        
        return filtered_resources
    
    def get_category_stats_by_country(self, country_code: str) -> Dict[str, int]:
        """
        Statistiques des catégories par pays pour monitoring des targets lean
        Retourne le nombre de ressources par catégorie pour un pays donné
        """
        stats = {
            "contact_urgence": 0,
            "procedure_plateforme": 0, 
            "signalement_autorite": 0,
            "association_locale": 0,
            "services_support": 0  # Existant
        }
        
        for resource_id, resource_data in self.unified_data.items():
            if resource_data.get("country_code") == country_code:
                category = resource_data.get("metadata", {}).get("category", "services_support")
                if category in stats:
                    stats[category] += 1
        
        stats["total"] = sum(stats.values())
        return stats
    
    def check_category_targets(self, country_code: str) -> Dict[str, Dict]:
        """
        Vérifie si les targets lean sont atteints pour un pays
        Retourne l'état vs objectifs selon CategoryTargets
        """
        current_stats = self.get_category_stats_by_country(country_code)
        
        # Targets selon logic_sourcing_ressources.md
        targets = {
            "contact_urgence": 3,
            "procedure_plateforme": 6,
            "signalement_autorite": 2,
            "association_locale": 5
        }
        
        result = {}
        for category, target in targets.items():
            current = current_stats.get(category, 0)
            result[category] = {
                "current": current,
                "target": target,
                "completion_rate": (current / target) * 100 if target > 0 else 100,
                "status": "complete" if current >= target else "incomplete",
                "needed": max(0, target - current)
            }
        
        # Total général
        total_current = sum(current_stats.get(cat, 0) for cat in targets.keys())
        total_target = sum(targets.values())  # 16 selon la stratégie
        
        result["overall"] = {
            "current": total_current,
            "target": total_target,
            "completion_rate": (total_current / total_target) * 100,
            "status": "complete" if total_current >= total_target else "incomplete"
        }
        
        return result

    def get_resources_by_status(self, status: str) -> Dict[str, dict]:
        """Récupère les ressources par statut"""
        return {
            resource_id: resource_data 
            for resource_id, resource_data in self.unified_data.items()
            if resource_data.get("workflow_status") == status
        }
    
    def get_rag_resources(self) -> dict:
        """Récupère les ressources optimisées pour RAG"""
        return self.rag_data
    
    def cleanup_old_working_data(self, days_old: int = 30):
        """Nettoie les anciennes données de travail"""
        cutoff_date = datetime.now().timestamp() - (days_old * 24 * 3600)
        
        to_remove = []
        for resource_id, resource_data in self.unified_data.items():
            created_at = resource_data.get("created_at")
            if created_at:
                try:
                    resource_timestamp = datetime.fromisoformat(created_at).timestamp()
                    if resource_timestamp < cutoff_date and resource_data.get("workflow_status") in [WorkflowStatus.GEO_REJECTED]:
                        to_remove.append(resource_id)
                except:
                    pass
        
        for resource_id in to_remove:
            del self.unified_data[resource_id]
        
        if to_remove:
            self._save_json(self.unified_data, self.unified_file)
            logger.info(f"Nettoyage: {len(to_remove)} ressources supprimées")
    
    def get_deduplication_analysis(self) -> dict:
        """Analyse complète des doublons (triple approche)"""
        if not self.deduplication_service:
            return {"status": "unavailable", "message": "DeduplicationService not initialized"}
        
        try:
            # Analyser tous les doublons
            analysis = self.deduplication_service.analyze_all(self.unified_data)
            
            return {
                "status": "success",
                "timestamp": datetime.now().isoformat(),
                "exact_duplicates": len(analysis.exact_duplicates),
                "similar_duplicates": len(analysis.similar_duplicates),
                "domain_duplicates": len(analysis.domain_duplicates),
                "total_issues": len(analysis.exact_duplicates) + len(analysis.similar_duplicates) + len(analysis.domain_duplicates),
                "recommendations": analysis.recommendations,
                "exact_groups": analysis.exact_duplicates,
                "similar_groups": analysis.similar_duplicates,
                "domain_groups": analysis.domain_duplicates
            }
        except Exception as e:
            logger.error(f"Error analyzing duplicates: {e}")
            return {"status": "error", "error": str(e)}
    
    def cleanup_duplicates(self, strategy: str = "keep_first") -> dict:
        """Nettoie automatiquement les doublons selon stratégie"""
        if not self.deduplication_service:
            return {"status": "unavailable", "message": "DeduplicationService not initialized"}
        
        try:
            # Nettoyer les doublons
            result = self.deduplication_service.clean_automatic(self.unified_data, strategy)
            
            # Mise à jour du fichier unifié
            self.unified_data = result['kept_resources']
            self._save_json(self.unified_data, self.unified_file)
            
            logger.info(f"Cleanup completed: {result['removed_count']} duplicates removed")
            
            return {
                "status": "success",
                "strategy": strategy,
                "timestamp": datetime.now().isoformat(),
                "removed_count": result['removed_count'],
                "removed_ids": result['removed_ids'],
                "kept_count": len(result['kept_resources']),
                "message": f"Cleaned {result['removed_count']} duplicates"
            }
        except Exception as e:
            logger.error(f"Error cleaning duplicates: {e}")
            return {"status": "error", "error": str(e)}
    
    def get_discovery_status_report(self, country: str) -> dict:
        """Rapport complet de statut des découvertes par pays"""
        if not self.priority_discovery_service:
            return {"status": "unavailable", "message": "PriorityDiscoveryService not initialized"}
        
        try:
            # Récupérer rapport de statut
            report = self.priority_discovery_service.get_discovery_status_report(country)
            
            return {
                "status": "success",
                "timestamp": datetime.now().isoformat(),
                "country": country.upper(),
                "by_priority": report,
                "message": f"Discovery status report for {country}"
            }
        except Exception as e:
            logger.error(f"Error getting discovery status: {e}")
            return {"status": "error", "error": str(e)}
    
    def get_next_discoveries_due(self, country: str) -> dict:
        """Prochaines découvertes à lancer (par priorité)"""
        if not self.priority_discovery_service:
            return {"status": "unavailable", "message": "PriorityDiscoveryService not initialized"}
        
        try:
            # Récupérer les découvertes dues
            due_categories = []
            
            # Utiliser config (pas discovery_configs)
            for config in self.priority_discovery_service.config.values():
                if self.priority_discovery_service.is_discovery_due(country, config.category):
                    due_categories.append({
                        "category": config.category,
                        "priority": config.priority.name,
                        "allocation": config.default_max_resources,
                        "retry_attempts": config.retry_attempts,
                        "rate_limit_delay": 2.0
                    })
            
            # Trier par priorité (CRITICAL d'abord)
            priority_order = {"CRITICAL": 0, "IMPORTANT": 1, "OPTIONAL": 2}
            due_categories.sort(key=lambda x: priority_order.get(x['priority'].split('_')[-1].upper(), 99))
            
            # Calcul allocation totale
            total_allocation = sum(cat['allocation'] for cat in due_categories)
            
            return {
                "status": "success",
                "timestamp": datetime.now().isoformat(),
                "country": country.upper(),
                "due_categories": [cat['category'] for cat in due_categories],
                "priority_order": due_categories,
                "resource_allocation": {
                    "total_capacity": total_allocation,
                    "allocated": total_allocation,
                    "remaining": 0
                },
                "estimated_time_hours": len(due_categories) * 2,
                "message": f"Found {len(due_categories)} categories due for discovery"
            }
        except Exception as e:
            logger.error(f"Error getting next discoveries due: {e}")
            return {"status": "error", "error": str(e)}

    def get_workflow_stats(self) -> dict:
        """Statistiques du workflow"""
        stats = {}
        for status in [WorkflowStatus.DISCOVERED, WorkflowStatus.GEO_VALIDATED, 
                      WorkflowStatus.CRITICAL_PENDING, WorkflowStatus.RAG_READY]:
            stats[status] = len(self.get_resources_by_status(status))
        
        stats["total_unified"] = len(self.unified_data)
        stats["total_rag_ready"] = len(self.rag_data)
        
        return stats

# Instance singleton
_workflow_manager = None

def get_workflow_manager() -> ResourceWorkflowManager:
    """Récupère l'instance singleton du gestionnaire de workflow"""
    global _workflow_manager
    if _workflow_manager is None:
        # Utiliser working_resources.json comme fichier unifié car c'est là que sont les données
        _workflow_manager = ResourceWorkflowManager(
            unified_file="working_resources.json",
            rag_file="rag_resources.json"
        )
    return _workflow_manager