"""
🎯 PriorityDiscoveryService - Service de découverte alignée aux besoins du chatbot

Architecture simple:
- Définir priorités par impact chatbot réel
- Adapter allocation ressources selon priorité
- Tracker fréquence découverte par catégorie
- Décider quoi découvrir ET QUAND
"""

import logging
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum

logger = logging.getLogger(__name__)


class DiscoveryPriority(Enum):
    """Niveaux de priorité de découverte"""
    CRITICAL = "priority_1_critical"      # Impact direct parcours utilisateur
    IMPORTANT = "priority_2_important"    # Support parcours fréquents
    OPTIONAL = "priority_3_optional"      # Enrichissement selon contexte


@dataclass
class PriorityConfig:
    """Configuration d'une catégorie de découverte"""
    category: str
    priority: DiscoveryPriority
    description: str
    chatbot_usage: str           # Comment le chatbot l'utilise
    user_impact: str             # "DIRECT" | "SEMI-DIRECT" | "CONTEXTUEL"
    discovery_frequency: str     # "Hebdomadaire" | "Mensuelle" | etc.
    default_max_resources: int   # Nombre max de ressources à découvrir
    retry_attempts: int          # Nombre de tentatives LLM
    related_platforms: List[str] = field(default_factory=list)  # Pour procedure_plateforme


# Configuration par défaut des priorités (align avec archive_legacy)
DEFAULT_PRIORITY_CONFIG = {
    # =================================================================
    # NIVEAU 1 - CRITIQUE (Impact direct, découverte hebdomadaire)
    # =================================================================
    'services_urgence_cyber': PriorityConfig(
        category='contact_urgence',
        priority=DiscoveryPriority.CRITICAL,
        description='Services urgence cyberharcèlement jeunes',
        chatbot_usage='Sentiment négatif → Service support → Contact urgence',
        user_impact='DIRECT - Ressource fournie immédiatement',
        discovery_frequency='Hebdomadaire',
        default_max_resources=5,
        retry_attempts=5
    ),
    
    'autorites_cyber_jeunes': PriorityConfig(
        category='signalement_autorite',
        priority=DiscoveryPriority.CRITICAL,
        description='Autorités signalement cyberharcèlement mineurs',
        chatbot_usage='Service support → Signalement officiel',
        user_impact='DIRECT - Action légale proposée',
        discovery_frequency='Bi-hebdomadaire',
        default_max_resources=4,
        retry_attempts=4
    ),
    
    # =================================================================
    # NIVEAU 2 - IMPORTANT (Support parcours fréquents, mensuelle)
    # =================================================================
    'guide_signalement_plateforme': PriorityConfig(
        category='procedure_plateforme',
        priority=DiscoveryPriority.IMPORTANT,
        description='Guides signalement par plateforme',
        chatbot_usage='Suppression contenu → Procédures plateformes',
        user_impact='SEMI-DIRECT - Guide fourni selon plateforme mentionnée',
        discovery_frequency='Mensuelle',
        default_max_resources=5,
        retry_attempts=3,
        related_platforms=['Instagram', 'TikTok', 'Snapchat', 'Discord', 'YouTube']
    ),
    
    'guides_communication_parents': PriorityConfig(
        category='association_locale',
        priority=DiscoveryPriority.IMPORTANT,
        description='Guides dialogue parents-enfants',
        chatbot_usage='Parler aux parents → Ressources communication',
        user_impact='SEMI-DIRECT - Support selon âge utilisateur',
        discovery_frequency='Mensuelle',
        default_max_resources=4,
        retry_attempts=3
    ),
    
    # =================================================================
    # NIVEAU 3 - OPTIONNEL (Enrichissement selon contexte, trimestrielle)
    # =================================================================
    'associations_cyber_locales': PriorityConfig(
        category='association_locale',
        priority=DiscoveryPriority.OPTIONAL,
        description='Associations locales cyberharcèlement',
        chatbot_usage='Service support → Accompagnement local',
        user_impact='CONTEXTUEL - Selon localisation utilisateur',
        discovery_frequency='Trimestrielle',
        default_max_resources=3,
        retry_attempts=2
    ),
    
    'procedures_scolaires_cyber': PriorityConfig(
        category='association_locale',
        priority=DiscoveryPriority.OPTIONAL,
        description='Procédures scolaires cyberharcèlement',
        chatbot_usage='Parler enseignant → Protocoles école',
        user_impact='CONTEXTUEL - Si contexte scolaire identifié',
        discovery_frequency='Trimestrielle',
        default_max_resources=3,
        retry_attempts=2
    ),
}


@dataclass
class DiscoverySchedule:
    """Tracking de quand découvrir une catégorie"""
    config_key: str
    category: str
    priority: DiscoveryPriority
    last_discovery: Optional[datetime] = None
    next_scheduled: Optional[datetime] = None
    discovery_count: int = 0
    resources_discovered: int = 0


class PriorityDiscoveryService:
    """
    Service de gestion des priorités de découverte
    
    Usage:
    ```python
    service = PriorityDiscoveryService()
    
    # Obtenir config pour une catégorie
    config = service.get_config('contact_urgence')
    print(f"Max ressources: {config.default_max_resources}")
    print(f"Retry attempts: {config.retry_attempts}")
    
    # Obtenir toutes les catégories critiques
    critical = service.get_by_priority(DiscoveryPriority.CRITICAL)
    for config in critical:
        print(f"{config.category} - {config.user_impact}")
    
    # Vérifier quand re-découvrir
    due = service.is_discovery_due(country, 'contact_urgence')
    if due:
        start_discovery(country, 'contact_urgence')
    
    # Marquer découverte comme complète
    service.mark_discovered(country, 'contact_urgence', resources_found=5)
    
    # Rapport pour admin
    report = service.get_discovery_status_report(country)
    ```
    """
    
    def __init__(self, config: Optional[Dict[str, PriorityConfig]] = None):
        """Initialiser le service"""
        self.config = config or DEFAULT_PRIORITY_CONFIG
        self.schedules: Dict[str, Dict[str, DiscoverySchedule]] = {}  # {country: {key: schedule}}
    
    # ==========================================
    # 📋 Configuration
    # ==========================================
    
    def get_config(self, category: str) -> Optional[PriorityConfig]:
        """Obtenir config pour une catégorie"""
        for config in self.config.values():
            if config.category == category:
                return config
        return None
    
    def get_by_priority(self, priority: DiscoveryPriority) -> List[PriorityConfig]:
        """Obtenir toutes les configs d'une priorité"""
        return [c for c in self.config.values() if c.priority == priority]
    
    def get_all_configs(self) -> List[PriorityConfig]:
        """Obtenir toutes les configs"""
        return list(self.config.values())
    
    # ==========================================
    # 🎯 Allocation ressources
    # ==========================================
    
    def get_resource_allocation(self, category: str) -> Dict:
        """
        Obtenir allocation optimale pour une catégorie
        
        Returns:
        {
            'max_resources': int,           # Nombre max à chercher
            'retry_attempts': int,         # Tentatives LLM
            'priority': str,               # CRITICAL | IMPORTANT | OPTIONAL
            'batch_size': int,             # Taille batch recommandée
            'rate_limit_delay': float      # Délai entre requêtes (secondes)
        }
        """
        config = self.get_config(category)
        if not config:
            return {
                'max_resources': 3,
                'retry_attempts': 1,
                'priority': 'UNKNOWN',
                'batch_size': 1,
                'rate_limit_delay': 5.0
            }
        
        # Adapter selon priorité
        if config.priority == DiscoveryPriority.CRITICAL:
            return {
                'max_resources': config.default_max_resources,
                'retry_attempts': config.retry_attempts,  # Agressif
                'priority': 'CRITICAL',
                'batch_size': 2,           # Paralleliser un peu
                'rate_limit_delay': 3.0   # Pas trop d'attente
            }
        
        elif config.priority == DiscoveryPriority.IMPORTANT:
            return {
                'max_resources': config.default_max_resources - 1,
                'retry_attempts': config.retry_attempts,
                'priority': 'IMPORTANT',
                'batch_size': 1,
                'rate_limit_delay': 5.0
            }
        
        else:  # OPTIONAL
            return {
                'max_resources': config.default_max_resources - 2,
                'retry_attempts': config.retry_attempts,
                'priority': 'OPTIONAL',
                'batch_size': 1,
                'rate_limit_delay': 10.0  # Plus prudent
            }
    
    # ==========================================
    # ⏰ Planification
    # ==========================================
    
    def is_discovery_due(self, country: str, category: str) -> bool:
        """
        Vérifier si on doit re-découvrir pour cette catégorie/pays
        
        Basé sur discovery_frequency
        """
        schedule = self._get_or_create_schedule(country, category)
        
        if schedule.last_discovery is None:
            return True  # Jamais découvert
        
        config = self.get_config(category)
        if not config:
            return False
        
        # Mapper fréquence → timedelta
        freq_map = {
            'Hebdomadaire': timedelta(days=7),
            'Bi-hebdomadaire': timedelta(days=14),
            'Mensuelle': timedelta(days=30),
            'Trimestrielle': timedelta(days=90)
        }
        
        interval = freq_map.get(config.discovery_frequency, timedelta(days=30))
        next_allowed = schedule.last_discovery + interval
        
        return datetime.now() >= next_allowed
    
    def mark_discovered(self, country: str, category: str, resources_found: int = 0):
        """Marquer une découverte comme complète"""
        schedule = self._get_or_create_schedule(country, category)
        schedule.last_discovery = datetime.now()
        schedule.discovery_count += 1
        schedule.resources_discovered += resources_found
        
        logger.info(
            f"✅ Découverte marquée: {country}/{category} "
            f"(+{resources_found} ressources, total: {schedule.resources_discovered})"
        )
    
    def _get_or_create_schedule(self, country: str, category: str) -> DiscoverySchedule:
        """Obtenir ou créer planning de découverte"""
        if country not in self.schedules:
            self.schedules[country] = {}
        
        if category not in self.schedules[country]:
            config = self.get_config(category)
            key = self._find_config_key(category)
            
            self.schedules[country][category] = DiscoverySchedule(
                config_key=key or category,
                category=category,
                priority=config.priority if config else DiscoveryPriority.OPTIONAL
            )
        
        return self.schedules[country][category]
    
    def _find_config_key(self, category: str) -> Optional[str]:
        """Trouver clé de config pour une catégorie"""
        for key, config in self.config.items():
            if config.category == category:
                return key
        return None
    
    # ==========================================
    # 📊 Rapports
    # ==========================================
    
    def get_discovery_status_report(self, country: str) -> Dict:
        """Générer rapport de statut découvertes par pays"""
        if country not in self.schedules:
            self.schedules[country] = {}
        
        report = {
            'country': country,
            'timestamp': datetime.now().isoformat(),
            'by_priority': {},
            'statistics': {
                'total_discovered': 0,
                'total_attempts': 0
            }
        }
        
        for priority in DiscoveryPriority:
            configs = self.get_by_priority(priority)
            priority_status = []
            
            for config in configs:
                schedule = self._get_or_create_schedule(country, config.category)
                
                due = self.is_discovery_due(country, config.category)
                days_since = None
                if schedule.last_discovery:
                    days_since = (datetime.now() - schedule.last_discovery).days
                
                priority_status.append({
                    'category': config.category,
                    'description': config.description,
                    'last_discovered': schedule.last_discovery.isoformat() if schedule.last_discovery else None,
                    'days_since': days_since,
                    'is_due': due,
                    'discovery_count': schedule.discovery_count,
                    'resources_found': schedule.resources_discovered
                })
                
                report['statistics']['total_discovered'] += schedule.resources_discovered
                report['statistics']['total_attempts'] += schedule.discovery_count
            
            report['by_priority'][priority.value] = priority_status
        
        return report
    
    def get_next_discoveries_to_run(self, country: str) -> List[Dict]:
        """Obtenir liste des découvertes à lancer en priorité"""
        due = []
        
        # Regrouper par priorité (CRITICAL d'abord)
        for priority in [DiscoveryPriority.CRITICAL, DiscoveryPriority.IMPORTANT, DiscoveryPriority.OPTIONAL]:
            for config in self.get_by_priority(priority):
                if self.is_discovery_due(country, config.category):
                    due.append({
                        'category': config.category,
                        'priority': priority.value,
                        'description': config.description,
                        'allocation': self.get_resource_allocation(config.category)
                    })
        
        return due
    
    def get_summary(self) -> Dict:
        """Résumé global du service"""
        critical = self.get_by_priority(DiscoveryPriority.CRITICAL)
        important = self.get_by_priority(DiscoveryPriority.IMPORTANT)
        optional = self.get_by_priority(DiscoveryPriority.OPTIONAL)
        
        return {
            'total_categories': len(self.config),
            'by_priority': {
                'critical': len(critical),
                'important': len(important),
                'optional': len(optional)
            },
            'categories': {
                'critical': [c.category for c in critical],
                'important': [c.category for c in important],
                'optional': [c.category for c in optional]
            },
            'countries_tracked': list(self.schedules.keys())
        }


# ==========================================
# Utilitaires d'export
# ==========================================

def export_discovery_config_as_markdown() -> str:
    """Exporter config de découverte en Markdown (pour docs)"""
    service = PriorityDiscoveryService()
    
    md = "# Configuration de Découverte - Priorités\n\n"
    
    for priority in DiscoveryPriority:
        configs = service.get_by_priority(priority)
        md += f"## {priority.value.upper()}\n\n"
        
        for config in configs:
            md += f"### {config.category}\n"
            md += f"- **Description**: {config.description}\n"
            md += f"- **Impact**: {config.user_impact}\n"
            md += f"- **Fréquence**: {config.discovery_frequency}\n"
            md += f"- **Ressources max**: {config.default_max_resources}\n"
            md += f"- **Tentatives**: {config.retry_attempts}\n\n"
    
    return md
