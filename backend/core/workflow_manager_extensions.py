"""
Extension du workflow_manager avec intégration DeduplicationService
À ajouter à ResourceWorkflowManager via la méthode:

    def add_discovered_resource_with_deduplication(...)
"""

# Ajouter cette méthode à la classe ResourceWorkflowManager


def add_discovered_resource_with_deduplication(self, resource_id: str, llm_data: dict, 
                                              category: str, country: str,
                                              urgency_level: str = "normal",
                                              contact_type: str = "phone") -> Dict:
    """
    Ajouter une ressource découverte avec check automatique de doublons
    
    Returns:
    {
        'success': True/False,
        'resource_id': str,
        'duplicate_check': {...},  # Résultat du check doublons
        'action_taken': str         # "added" | "skipped_duplicate" | "flagged_for_review"
    }
    """
    
    # 🔍 ÉTAPE 1: Vérifier les doublons si service disponible
    if self.deduplication_service:
        dup_check = self.deduplication_service.check_duplicate(llm_data, self.unified_data)
        
        if dup_check['is_duplicate']:
            action = dup_check['suggested_action']
            logger.warning(
                f"⚠️ Doublon détecté pour '{llm_data.get('organization_name')}' "
                f"({country}) - Action suggérée: {action.value}"
            )
            
            # Si MERGE suggéré → Ne pas ajouter, logger seulement
            if action.value == 'merge':
                logger.info(f"❌ Ressource skippée (doublon certain): {resource_id}")
                return {
                    'success': False,
                    'resource_id': resource_id,
                    'duplicate_check': dup_check,
                    'action_taken': 'skipped_duplicate'
                }
            
            # Si REVIEW suggéré → Ajouter mais marquer pour attention admin
            elif action.value == 'review':
                llm_data['needs_admin_review'] = True
                llm_data['duplicate_check'] = dup_check
                logger.info(f"⚠️ Ressource ajoutée avec flag review (doublon probable): {resource_id}")
                action_taken = 'flagged_for_review'
    else:
        dup_check = None
        action_taken = 'added'
    
    # ✅ ÉTAPE 2: Ajouter la ressource au workflow
    success = self.add_discovered_resource_with_category(
        resource_id=resource_id,
        llm_data=llm_data,
        category=category,
        urgency_level=urgency_level,
        contact_type=contact_type
    )
    
    if success:
        logger.info(f"✅ Ressource ajoutée: {resource_id} ({country}/{category})")
        
        # 📊 Marquer découverte comme complète si service disponible
        if self.priority_discovery_service:
            self.priority_discovery_service.mark_discovered(country, category, resources_found=1)
    
    return {
        'success': success,
        'resource_id': resource_id,
        'duplicate_check': dup_check,
        'action_taken': action_taken
    }


def get_deduplication_analysis(self) -> Dict:
    """
    Générer rapport complet d'analyse de doublons
    
    Returns:
    {
        'summary': {...},
        'exact_duplicates': [...],
        'similar_duplicates': [...],
        'recommendations': [...]
    }
    """
    if not self.deduplication_service:
        return {
            'error': 'DeduplicationService not available'
        }
    
    analysis = self.deduplication_service.analyze_all(self.unified_data)
    
    # Convertir en dictionnaire sérialisable
    from core.deduplication_service import export_analysis_as_dict
    return export_analysis_as_dict(analysis)


def cleanup_duplicates(self, strategy: str = "keep_first") -> Dict:
    """
    Nettoyer automatiquement les doublons
    
    Args:
        strategy: "keep_first" (simple) ou "keep_best" (intelligent)
    
    Returns:
    {
        'removed_count': int,
        'removed_ids': List[str],
        'status': 'success' | 'error'
    }
    """
    if not self.deduplication_service:
        return {
            'status': 'error',
            'message': 'DeduplicationService not available'
        }
    
    result = self.deduplication_service.clean_automatic(
        self.unified_data,
        strategy=strategy
    )
    
    # Mettre à jour les données après nettoyage
    self.unified_data = result['kept_resources']
    self._save_json(self.unified_data, self.unified_file)
    
    logger.info(f"🧹 Nettoyage complété: {result['removed_count']} doublons supprimés")
    
    return {
        'removed_count': result['removed_count'],
        'removed_ids': result['removed_ids'],
        'status': 'success'
    }


def get_discovery_status_report(self, country: str) -> Dict:
    """
    Obtenir rapport de statut des découvertes pour un pays
    
    Returns:
    {
        'country': str,
        'by_priority': {...},
        'statistics': {...}
    }
    """
    if not self.priority_discovery_service:
        return {
            'error': 'PriorityDiscoveryService not available'
        }
    
    return self.priority_discovery_service.get_discovery_status_report(country)


def get_next_discoveries_due(self, country: str) -> List[Dict]:
    """
    Obtenir liste des découvertes à lancer prochainement (par priorité)
    
    Returns:
    [
        {
            'category': 'contact_urgence',
            'priority': 'priority_1_critical',
            'allocation': {'max_resources': 5, 'retry_attempts': 5, ...}
        },
        ...
    ]
    """
    if not self.priority_discovery_service:
        return []
    
    return self.priority_discovery_service.get_next_discoveries_to_run(country)
