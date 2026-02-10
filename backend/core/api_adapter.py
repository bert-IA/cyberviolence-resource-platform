"""
Adaptateur pour intégrer les nouveaux modules avec les interfaces existantes
Maintient la compatibilité avec geographic_discovery.html et sources_validation_fixed.html
"""
from typing import Dict, List, Any, Optional
import logging
import asyncio
from datetime import datetime

from core.llm_manager import get_llm_manager, LLMProvider
from core.workflow_manager import get_workflow_manager
from core.dual_validation import get_validation_system, ValidationAction, ValidationStage
from core.geo_discovery import get_countries_for_language
from core.category_prompts import get_category_prompt, PRIORITY_PLATFORMS

logger = logging.getLogger(__name__)

class LegacyAPIAdapter:
    """Adaptateur pour maintenir la compatibilité avec les APIs existantes"""
    
    def __init__(self):
        # Détecter le provider depuis les variables d'environnement
        import os
        provider_name = os.environ.get("LLM_PROVIDER", "openrouter").lower()
        
        try:
            if provider_name == "gemini":
                provider = LLMProvider.GEMINI
            elif provider_name == "openrouter":
                provider = LLMProvider.OPENROUTER
            else:
                raise ValueError(f"Provider non supporté: {provider_name}")
                
            self.llm_manager = get_llm_manager(provider)
        except Exception as e:
            # Ne plus utiliser LOCAL en fallback - lever l'erreur
            logger.error(f"Erreur initialisation LLM {provider_name}: {e}")
            raise Exception(f"Impossible d'initialiser le provider LLM {provider_name}: {e}")
            
        self.workflow_manager = get_workflow_manager()
        self.validation_system = get_validation_system(self.workflow_manager)
    
    # === GEOGRAPHIC DISCOVERY ENDPOINTS ===
    
    async def start_geographic_discovery(self, language: str, category: str, countries: List[str], 
                                        max_per_category: int, admin_id: str) -> Dict[str, Any]:
        """
        Endpoint compatible: POST /geographic/discover
        Lance la découverte avec le nouveau système (PHASE 1.5 + PHASE 2)
        
        🔧 PHASE 1.5: Capture ressources AVANT validation (évite le bug du status vide)
        🔧 PHASE 2: Filtre par category dans les prompts LLM
        🔧 FUSION: Intègre check doublons et allocation ressources par priorité
        """
        try:
            # Sinon, continuer avec une seule catégorie
            return await self._discover_single_category(language, category, countries, max_per_category, admin_id)
        
        except Exception as e:
            logger.error(f"Erreur start_geographic_discovery: {e}", exc_info=True)
            return {
                "success": False,
                "message": f"Erreur système: {str(e)}",
                "data": {"estimated_duration": "N/A"}
            }
    
    async def start_geographic_discovery_multi_categories(self, language: str, categories: List[str], 
                                                          countries: List[str], max_per_category: int, 
                                                          admin_id: str) -> Dict[str, Any]:
        """
        ✅ NOUVEAU: Lance la découverte pour PLUSIEURS catégories en séquence avec tempo
        
        Exemple d'utilisation:
        POST /geographic/discover
        {
            "language": "EN",
            "categories": ["emergency", "procedure", "authority", "local"],
            "countries": ["GB", "FR"],
            "max_per_category": 3
        }
        """
        try:
            logger.info(f"� Découverte MULTI-CATÉGORIES: {categories}")
            
            combined_resources = []
            total_discovered = 0
            
            # Lancer les découvertes EN SÉQUENCE avec tempo
            for idx, category in enumerate(categories):
                # Ajouter tempo entre chaque catégorie pour éviter rate limiting
                if idx > 0:
                    delay = 12.0  # 12 secondes entre catégories
                    logger.info(f"⏳ Tempo {delay}s avant catégorie suivante...")
                    await asyncio.sleep(delay)
                
                logger.info(f"⏳ Découverte catégorie {idx+1}/{len(categories)}: {category}")
                result = await self._discover_single_category(language, category, countries, max_per_category, admin_id)
                
                if isinstance(result, dict) and result.get("success"):
                    resources = result.get("data", {}).get("resources", [])
                    combined_resources.extend(resources)
                    count = result.get("data", {}).get("discovered_count", 0)
                    total_discovered += count
                    logger.info(f"✅ {category}: {len(resources)} ressources ajoutées (total: {total_discovered})")
                else:
                    logger.warning(f"⚠️ {category}: Erreur ou aucune ressource")
            
            # Retourner les résultats combinés
            duration = len(categories) * 10 + (len(categories) - 1) * 12  # Estimation
            return {
                "success": True,
                "message": f"{total_discovered} ressources découvertes ({len(categories)} catégories)",
                "data": {
                    "language": language,
                    "categories": categories,
                    "estimated_duration": f"{duration} secondes",
                    "discovered_count": total_discovered,
                    "resources": combined_resources
                }
            }
        
        except Exception as e:
            logger.error(f"Erreur start_geographic_discovery_multi_categories: {e}", exc_info=True)
            return {
                "success": False,
                "message": f"Erreur système: {str(e)}",
                "data": {"estimated_duration": "N/A"}
            }
    
    async def _discover_single_category(self, language: str, category: str, countries: List[str],
                                        max_per_category: int, admin_id: str) -> Dict[str, Any]:
        """Lance la découverte pour UNE catégorie spécifique"""
        try:
            # Tester la connexion LLM
            if not self.llm_manager.test_connection():
                return {
                    "success": False,
                    "message": "Connexion LLM échouée",
                    "data": {"estimated_duration": "N/A"}
                }
            
            # 🎯 FUSION: Obtenir allocation ressources selon priorité de la catégorie
            allocation = self.workflow_manager.priority_discovery_service.get_resource_allocation(category) if self.workflow_manager.priority_discovery_service else {"max_resources": max_per_category, "retry_attempts": 1, "rate_limit_delay": 5.0}
            
            logger.info(f"🎯 Découverte {category} (Priority: {allocation.get('priority', 'N/A')})")
            logger.info(f"   Max ressources: {allocation['max_resources']}, Retry: {allocation['retry_attempts']}")
            
            # ✅ PHASE 1.5: En mémoire list pour capturer les ressources AVANT status change
            newly_discovered = []  # ✅ Garder trace des découvertes dans cette requête
            discovered_count = 0
            
            # Configuration pays (utiliser la liste de pays reçue du frontend, ou tous les pays si empty)
            if countries and len(countries) > 0:
                max_countries = len(countries)
                try:
                    logger.info(f"Recherche dans {len(countries)} pays spécifiques: {countries}")
                except UnicodeEncodeError:
                    logger.info(f"Recherche dans {len(countries)} pays spécifiques (encoding UTF-8)")
            else:
                max_countries = 5  # Fallback
                logger.info(f"Pas de pays spécifiés, utiliser {max_countries} par défaut")
            
            countries_config = await self._get_countries_config_dynamic(language, max_countries)
            
            # ✅ FIX BUG: Filtrer countries_config selon les pays sélectionnés du frontend
            if countries and len(countries) > 0:
                # Mapper les noms du frontend (UK, USA) vers les noms du backend (United Kingdom, United States)
                country_mapping = self._get_country_name_mapping(language)
                mapped_countries = [country_mapping.get(c, c) for c in countries]
                
                # ✅ ALSO accept country codes directly (ES, FR, IT, etc. from frontend)
                # Si le pays est un code (2 lettres), le garder comme code
                country_codes = [c if len(c) == 2 and c.isupper() else None for c in countries]
                country_codes = [c for c in country_codes if c]  # Remove None values
                
                # Filtrer countries_config pour ne garder que les pays demandés
                countries_config = [
                    c for c in countries_config 
                    if c["name"] in mapped_countries or c["code"] in countries or c["code"] in mapped_countries or c["code"] in country_codes
                ]
                
                try:
                    filtered_names = [c['name'] for c in countries_config]
                    logger.info(f"✅ Pays filtrés: {filtered_names} (demandés: {countries})")
                except UnicodeEncodeError:
                    logger.info(f"✅ Pays filtrés: {len(countries_config)} pays (encoding UTF-8)")
            
            for country_idx, country in enumerate(countries_config):
                for term_idx, search_term in enumerate(country.get("search_terms", [])[:1]):  # 1 seul terme par pays pour éviter rate limiting
                    try:
                        # ✅ DEBUG: Log pour chaque pays traité
                        logger.info(f"🌍 Traitement pays {country_idx + 1}/{len(countries_config)}: {country['name']} ({country['code']}) - Terme: {search_term}")
                        
                        # Délai pour éviter rate limiting (surtout après la première requête)
                        if country_idx > 0 or term_idx > 0:
                            await asyncio.sleep(5.0)  # Réduit de 10s à 5s - parser amélioré
                        
                        # ✅ PHASE 2: Générer avec LLM en passant la category pour filtrer mieux
                        prompt = self._generate_discovery_prompt(country["name"], language, search_term, category)
                        response = self.llm_manager.generate(prompt)
                        
                        # ✅ DEBUG: Log la réponse du LLM
                        if response.success:
                            logger.info(f"📝 LLM Response ({country['code']}): {response.content[:200]}...")
                        else:
                            logger.warning(f"❌ LLM Error ({country['code']}): {response.error if hasattr(response, 'error') else 'Unknown'}")
                        
                        if response.success:
                            # Parser la réponse
                            resource_data = self._parse_llm_response(response.content, country, language)
                            
                            if resource_data:
                                resource_id = f"DISCOVERED_{country['code']}_{discovered_count + 1}"
                                
                                # 🎯 FUSION: Vérifier si c'est un doublon AVANT d'ajouter
                                is_duplicate = False
                                duplicate_action = None
                                
                                if self.workflow_manager.deduplication_service:
                                    check = self.workflow_manager.deduplication_service.check_duplicate(resource_data, self.workflow_manager.unified_data)
                                    is_duplicate = check['is_duplicate']
                                    duplicate_action = check.get('suggested_action', 'skip')
                                    
                                    if is_duplicate:
                                        logger.info(f"⚠️ Doublon détecté: {duplicate_action}")
                                
                                if not is_duplicate:
                                    # Ajouter au workflow
                                    self.workflow_manager.add_discovered_resource(resource_id, resource_data)
                                    
                                    # ✅ PHASE 1.5: Capturer AVANT que la validation ne change le status
                                    newly_discovered.append({
                                        "id": resource_id,
                                        "name": resource_data.get("name", ""),
                                        "country": resource_data.get("country", ""),
                                        "phone": resource_data.get("phone", ""),
                                        "email": resource_data.get("email", ""),
                                        "confidence": resource_data.get("confidence_score", 0.0),
                                        "category": resource_data.get("category", category),  # ✅ Utiliser category du param
                                        "description": resource_data.get("description", ""),
                                        "is_new": True
                                    })
                                    
                                    # Démarrer validation géographique
                                    self.validation_system.start_geographic_validation(resource_id)
                                    
                                    discovered_count += 1
                                    
                                    # 🎯 FUSION: Marquer découverte complète pour cette catégorie
                                    if self.workflow_manager.priority_discovery_service:
                                        self.workflow_manager.priority_discovery_service.mark_discovered(
                                            country['code'], category, resources_found=1
                                        )
                                else:
                                    # Ressource est un doublon - l'ajouter à la liste mais marquée comme doublon
                                    newly_discovered.append({
                                        "id": resource_id,
                                        "name": resource_data.get("name", ""),
                                        "country": resource_data.get("country", ""),
                                        "phone": resource_data.get("phone", ""),
                                        "email": resource_data.get("email", ""),
                                        "confidence": resource_data.get("confidence_score", 0.0),
                                        "category": resource_data.get("category", category),
                                        "description": resource_data.get("description", ""),
                                        "is_new": False,
                                        "duplicate_reason": str(duplicate_action) if duplicate_action else "unknown"
                                    })
                    
                    except Exception as e:
                        logger.error(f"Erreur découverte {country['name']}: {e}")
            
            # ✅ PHASE 1.5: Retourner les ressources capturées (liste en mémoire, pas de lookup par status)
            return {
                "success": True,
                "message": f"{discovered_count} ressources découvertes",
                "data": {
                    "language": language,
                    "estimated_duration": "10 secondes",
                    "discovered_count": discovered_count,
                    "resources": newly_discovered  # ✅ Utiliser la copie locale au lieu du status lookup
                }
            }
            
        except Exception as e:
            logger.error(f"Erreur geographic discovery: {e}")
            return {
                "success": False,
                "message": f"Erreur: {str(e)}",
                "data": {"estimated_duration": "N/A"}
            }
    
    # === CATEGORY DISCOVERY ENDPOINTS (NOUVEAU) ===
    
    async def start_category_discovery(self, category: str, country_code: str, language: str, 
                                     max_resources: int, admin_id: str, **kwargs) -> Dict[str, Any]:
        """
        NOUVEAU: Endpoint pour découverte ciblée par catégorie
        Implémente la stratégie lean selon logic_sourcing_ressources.md
        
        Args:
            category: Type de ressource (contact_urgence, procedure_plateforme, etc.)
            country_code: Code pays (FR, DE, ES, etc.)
            language: Langue pour le prompt
            max_resources: Nombre max de ressources à découvrir (lean = 3-6 selon catégorie)
            admin_id: ID admin pour audit
            **kwargs: Paramètres spécialisés (platform_name pour plateformes, etc.)
        """
        try:
            # Délai initial pour éviter rate limiting
            await asyncio.sleep(2.0)  # Petite pause avant chaque découverte
            
            # Vérifier la connexion LLM
            if not self.llm_manager.test_connection():
                return {
                    "success": False,
                    "message": "LLM non disponible",
                    "data": {"category": category, "discovered_count": 0}
                }
            
            # Vérifier les targets actuels
            current_stats = self.workflow_manager.get_category_stats_by_country(country_code)
            current_count = current_stats.get(category, 0)
            
            logger.info(f"Discovery {category} pour {country_code}: {current_count} existants, target {max_resources}")
            
            # Obtenir le nom du pays depuis le code
            countries = await get_countries_for_language(language)
            country_name = next((c["name"] for c in countries if c["code"] == country_code), country_code)
            
            discovered_count = 0
            
            # Générer plusieurs tentatives pour diversité
            for attempt in range(max_resources):
                try:
                    # Générer prompt spécialisé
                    prompt = get_category_prompt(category, country_name, language, **kwargs)
                    
                    logger.info(f"Tentative {attempt + 1}/{max_resources} pour {category} en {country_name}")
                    
                    # Générer avec LLM
                    response = self.llm_manager.generate(prompt)
                    
                    if response.success:
                        # DEBUG: Log de la réponse brute
                        logger.info(f"🔍 Réponse LLM brute pour {category}:\n{response.content[:500]}...")
                        
                        # Parser la réponse
                        resource_data = self._parse_llm_response(response.content, 
                                                               {"name": country_name, "code": country_code}, 
                                                               language)
                        
                        if resource_data:
                            # ⭐ VÉRIFICATION ANTI-DOUBLONS
                            if self._is_duplicate_resource(resource_data, country_code, category):
                                logger.info(f"⚠️  Doublon détecté pour {resource_data.get('organization_name', 'N/A')} - ignoré")
                                continue
                            
                            # Ajouter au workflow avec métadonnées de catégorie
                            resource_id = f"DISCOVERED_{country_code}_{category.upper()}_{discovered_count + 1}"
                            
                            # Déterminer métadonnées selon catégorie
                            metadata = self._determine_category_metadata(category, resource_data, **kwargs)
                            
                            # Ajouter avec métadonnées enrichies
                            self.workflow_manager.add_discovered_resource_with_category(
                                resource_id, resource_data, 
                                category=category,
                                urgency_level=metadata.get("urgency_level", "normal"),
                                contact_type=metadata.get("contact_type", "phone"),
                                availability=metadata.get("availability", "business_hours"),
                                official_status=metadata.get("official_status", "approved")
                            )
                            
                            # Démarrer validation géographique
                            self.validation_system.start_geographic_validation(resource_id)
                            
                            discovered_count += 1
                            
                            logger.info(f"✅ Ressource {category} découverte: {resource_data.get('organization_name', 'N/A')}")
                
                except Exception as e:
                    logger.error(f"Erreur tentative {attempt + 1} pour {category}: {e}")
                    continue
            
            return {
                "success": True,
                "message": f"{discovered_count} ressources {category} découvertes pour {country_name}",
                "data": {
                    "category": category,
                    "country_code": country_code,
                    "language": language,
                    "discovered_count": discovered_count,
                    "previous_count": current_count,
                    "new_total": current_count + discovered_count,
                    "target_reached": (current_count + discovered_count) >= max_resources
                }
            }
            
        except Exception as e:
            logger.error(f"Erreur category discovery {category}: {e}")
            return {
                "success": False,
                "message": f"Erreur: {str(e)}",
                "data": {"category": category, "discovered_count": 0}
            }
    
    # === BATCH DISCOVERY METHODS (NOUVEAU) ===
    
    async def start_batch_discovery_multi_countries(self, category: str, language: str, 
                                                   country_codes: List[str], max_resources_per_country: int,
                                                   admin_id: str) -> Dict[str, Any]:
        """
        Découverte d'une catégorie sur plusieurs pays simultanément
        Optimisé pour éviter la répétition de contexte
        """
        try:
            if not self.llm_manager.test_connection():
                return {"error": "LLM non disponible", "results": {}}
            
            # Obtenir noms des pays
            countries = await get_countries_for_language(language)
            country_mapping = {c["code"]: c["name"] for c in countries}
            
            total_discovered = 0
            results = {}
            
            # Découverte parallèle avec délai optimisé
            for i, country_code in enumerate(country_codes):
                country_name = country_mapping.get(country_code, country_code)
                
                logger.info(f"Découverte {category} pour {country_name} ({i+1}/{len(country_codes)})")
                
                # Délai intelligent : très conservateur pour éviter 429
                if i > 0:
                    await asyncio.sleep(8.0)  # Augmenté de 3.0 à 8.0s
                
                country_result = await self.start_category_discovery(
                    category=category,
                    country_code=country_code,
                    language=language,
                    max_resources=max_resources_per_country,
                    admin_id=admin_id
                )
                
                if country_result["success"]:
                    discovered = country_result["data"]["discovered_count"]
                    total_discovered += discovered
                    results[country_code] = {
                        "country_name": country_name,
                        "discovered": discovered,
                        "status": "success"
                    }
                else:
                    results[country_code] = {
                        "country_name": country_name,
                        "discovered": 0,
                        "status": "error",
                        "error": country_result["message"]
                    }
            
            return {
                "total_discovered": total_discovered,
                "countries_processed": len(country_codes),
                "results": results,
                "category": category,
                "language": language
            }
            
        except Exception as e:
            logger.error(f"Erreur batch multi-pays: {e}")
            return {"error": str(e), "results": {}}
    
    async def start_batch_discovery_all_platforms(self, country_code: str, language: str,
                                                 platforms: List[str], max_resources_per_platform: int,
                                                 admin_id: str) -> Dict[str, Any]:
        """
        Découverte de toutes les procédures plateformes pour un pays
        Optimisé pour mutualiser le contexte pays
        """
        try:
            if not self.llm_manager.test_connection():
                return {"error": "LLM non disponible", "results": {}}
            
            # Obtenir nom du pays
            countries = await get_countries_for_language(language)
            country_name = next((c["name"] for c in countries if c["code"] == country_code), country_code)
            
            total_discovered = 0
            results = {}
            
            logger.info(f"Découverte toutes plateformes pour {country_name}")
            
            # Découverte séquentielle optimisée pour plateformes
            for i, platform in enumerate(platforms):
                logger.info(f"Plateforme {platform} ({i+1}/{len(platforms)})")
                
                # Délai très conservateur entre plateformes pour éviter 429
                if i > 0:
                    await asyncio.sleep(6.0)  # Augmenté de 2.5 à 6.0s
                
                platform_result = await self.start_category_discovery(
                    category="procedure_plateforme",
                    country_code=country_code,
                    language=language,
                    max_resources=max_resources_per_platform,
                    admin_id=admin_id,
                    platform_name=platform
                )
                
                if platform_result["success"]:
                    discovered = platform_result["data"]["discovered_count"]
                    total_discovered += discovered
                    results[platform] = {
                        "discovered": discovered,
                        "status": "success"
                    }
                else:
                    results[platform] = {
                        "discovered": 0,
                        "status": "error",
                        "error": platform_result["message"]
                    }
            
            return {
                "total_discovered": total_discovered,
                "platforms_processed": len(platforms),
                "results": results,
                "country_code": country_code,
                "country_name": country_name
            }
            
        except Exception as e:
            logger.error(f"Erreur batch plateformes: {e}")
            return {"error": str(e), "results": {}}
    
    async def start_complete_lean_discovery(self, language: str, country_codes: List[str],
                                          categories: List[str], admin_id: str) -> Dict[str, Any]:
        """
        Découverte complète lean strategy : toutes catégories pour plusieurs pays
        Implémente l'approche 16 ressources/pays de façon optimisée
        """
        try:
            if not self.llm_manager.test_connection():
                return {"error": "LLM non disponible", "results": {}}
            
            # Mapping lean strategy
            lean_targets = {
                "contact_urgence": 3,
                "procedure_plateforme": 5,
                "signalement_autorite": 4,
                "association_locale": 4
            }
            
            total_discovered = 0
            results = {}
            
            logger.info(f"Découverte lean complète: {len(categories)} catégories × {len(country_codes)} pays")
            
            # Découverte par pays puis par catégorie (optimise contexte pays)
            for country_idx, country_code in enumerate(country_codes):
                country_results = {}
                country_total = 0
                
                logger.info(f"Pays {country_code} ({country_idx+1}/{len(country_codes)})")
                
                for cat_idx, category in enumerate(categories):
                    max_resources = lean_targets.get(category, 3)
                    
                    # Délai adaptatif très conservateur
                    if country_idx > 0 or cat_idx > 0:
                        await asyncio.sleep(7.0)  # Augmenté de 3.5 à 7.0s
                    
                    cat_result = await self.start_category_discovery(
                        category=category,
                        country_code=country_code,
                        language=language,
                        max_resources=max_resources,
                        admin_id=admin_id
                    )
                    
                    if cat_result["success"]:
                        discovered = cat_result["data"]["discovered_count"]
                        country_total += discovered
                        country_results[category] = {
                            "discovered": discovered,
                            "target": max_resources,
                            "status": "success"
                        }
                    else:
                        country_results[category] = {
                            "discovered": 0,
                            "target": max_resources,
                            "status": "error",
                            "error": cat_result["message"]
                        }
                
                results[country_code] = {
                    "categories": country_results,
                    "total_discovered": country_total,
                    "lean_target": sum(lean_targets.values()),
                    "completion_rate": (country_total / sum(lean_targets.values())) * 100
                }
                
                total_discovered += country_total
            
            return {
                "total_discovered": total_discovered,
                "countries_processed": len(country_codes),
                "categories_processed": len(categories),
                "results": results,
                "language": language,
                "lean_strategy_applied": True
            }
            
        except Exception as e:
            logger.error(f"Erreur découverte lean complète: {e}")
            return {"error": str(e), "results": {}}
    
    def _determine_category_metadata(self, category: str, resource_data: dict, **kwargs) -> dict:
        """Détermine les métadonnées selon la catégorie de ressource"""
        
        metadata_by_category = {
            "contact_urgence": {
                "urgency_level": "immediate" if "24h" in resource_data.get("description", "") else "normal",
                "contact_type": "phone",
                "availability": "24h" if "24h" in resource_data.get("description", "") else "business_hours",
                "official_status": "government" if any(word in resource_data.get("organization_name", "").lower() 
                                                     for word in ["ministère", "gouvernement", "service public"]) else "certified"
            },
            "procedure_plateforme": {
                "urgency_level": "normal",
                "contact_type": "online",
                "availability": "24h",  # Plateformes dispo 24h
                "official_status": "approved",
                "platform_name": kwargs.get("platform_name", "multiple")
            },
            "signalement_autorite": {
                "urgency_level": "normal",
                "contact_type": "form",
                "availability": "business_hours",
                "official_status": "government"
            },
            "association_locale": {
                "urgency_level": "normal",
                "contact_type": "phone" if resource_data.get("phone") else "email",
                "availability": "business_hours",
                "official_status": "certified" if "agré" in resource_data.get("description", "") else "approved"
            }
        }
        
        return metadata_by_category.get(category, {
            "urgency_level": "normal",
            "contact_type": "phone",
            "availability": "business_hours",
            "official_status": "approved"
        })

    def get_geographic_results(self, language: str = None) -> Dict[str, Any]:
        """
        Endpoint compatible: GET /geographic/results  
        Retourne les ressources en attente de validation géographique
        Filtre par langue si spécifiée
        """
        try:
            # Récupérer ressources en attente de validation géographique
            pending_resources = self.validation_system.get_resources_for_geographic_validation()
            
            # Filtrer par langue si spécifiée
            if language:
                pending_resources = {
                    k: v for k, v in pending_resources.items() 
                    if v.get("language", "").upper() == language.upper()
                }
            
            # Formater pour l'interface existante
            discovered_resources = []
            for resource_id, resource_data in pending_resources.items():
                discovered_resources.append({
                    "discovery_id": resource_id,
                    "organization_name": resource_data.get("organization_name", ""),
                    "website": resource_data.get("website", ""),
                    "description": resource_data.get("description", ""),
                    "phone": resource_data.get("phone", ""),
                    "email": resource_data.get("email", ""),
                    "country_name": resource_data.get("country_name", ""),
                    "country_code": resource_data.get("country_code", ""),
                    "language": resource_data.get("language", ""),
                    "confidence_score": 0.7,  # Score par défaut
                    "validation_status": "geo_pending"
                })
            
            return {
                "success": True,
                "data": {
                    "discovered_resources": discovered_resources,
                    "total_discovered": len(discovered_resources),
                    "language": language or "ALL",
                    "filter_applied": language is not None
                }
            }
            
        except Exception as e:
            logger.error(f"Erreur get_geographic_results: {e}")
            return {
                "success": False,
                "message": f"Erreur: {str(e)}",
                "data": {"discovered_resources": []}
            }
    
    def validate_geographic_batch(self, action: str, resource_ids: List[str], admin_id: str) -> Dict[str, Any]:
        """
        ✅ AMÉLIORÉ - Endpoint compatible: POST /geographic/validate-batch
        Validation géographique en lot avec transition automatique vers validation critique
        
        Améliorations Phase 1.5:
        - Transition automatique geo_validated → critical_pending
        - Meilleure traçabilité des transitions
        - Compteurs de transitions réussies
        """
        try:
            processed_resources = []
            auto_transitioned = 0  # 🆕 Compteur de transitions automatiques
            validation_action = ValidationAction.APPROVE if action == "approve" else ValidationAction.REJECT
            
            logger.info(f"✅ Starting batch validation: {action} for {len(resource_ids)} resources: {resource_ids}")
            
            for resource_id in resource_ids:
                logger.info(f"📋 Processing resource: {resource_id}")
                try:
                    # Critères par défaut (à adapter selon interface)
                    criteria_scores = {
                        "existence_verified": action == "approve",
                        "contact_accessible": action == "approve", 
                        "mission_relevant": action == "approve",
                        "geographic_match": action == "approve",
                        "language_appropriate": action == "approve"
                    }
                    
                    # Effectuer validation
                    result = self.validation_system.perform_geographic_validation(
                        resource_id, admin_id, validation_action, criteria_scores,
                        f"Validation en lot: {action}"
                    )
                    
                    transition_status = None
                    
                    # ✅ AMÉLIORÉ - Si approuvé → transition automatique vers critical_pending
                    if result.success and action == "approve" and resource_id:
                        try:
                            transition_success = self.validation_system.start_critical_validation(resource_id)
                            if transition_success:
                                auto_transitioned += 1
                                transition_status = "critical_pending"
                                logger.info(f"🔄 AUTO-TRANSITION: {resource_id} → critical_pending (succès)")
                            else:
                                transition_status = "transition_failed"
                                logger.warning(f"⚠️ AUTO-TRANSITION échouée pour {resource_id}")
                        except Exception as e:
                            logger.error(f"❌ Erreur start_critical_validation pour {resource_id}: {e}")
                            transition_status = "transition_error"
                            # Continuer le traitement même si la transition échoue
                    
                    processed_resources.append({
                        "resource_id": resource_id,
                        "action": action,
                        "success": result.success,
                        "new_status": result.next_stage.value if result.next_stage else "unknown",
                        "auto_transition": transition_status  # 🆕 NOUVEAU - Status de la transition
                    })
                
                except Exception as e:
                    logger.error(f"❌ Erreur validation {resource_id}: {e}")
                    processed_resources.append({
                        "resource_id": resource_id,
                        "action": action,
                        "success": False,
                        "error": str(e)
                    })
            
            logger.info(f"✅ Batch validation completed: {len(processed_resources)} resources processed")
            logger.info(f"🔄 Auto-transitions: {auto_transitioned}/{len(resource_ids)} ressources transitioned → critical_pending")
            
            return {
                "success": True,
                "message": f"{len(processed_resources)} ressources traitées, {auto_transitioned} transitions automatiques",
                "data": {
                    "processed_resources": processed_resources,
                    "action": action,
                    "auto_transitions": auto_transitioned,  # 🆕 NOUVEAU - Compteur
                    "total_validated": len([r for r in processed_resources if r.get("success")])
                }
            }
            
        except Exception as e:
            logger.error(f"Erreur validate_geographic_batch: {e}")
            return {
                "success": False,
                "message": f"Erreur: {str(e)}",
                "data": {"processed_resources": []}
            }
    
    # === CRITICAL VALIDATION ENDPOINTS ===
    
    def get_sources_for_validation(self) -> Dict[str, Any]:
        """
        Endpoint compatible pour sources_validation_fixed.html
        Retourne les ressources validées géographiquement en attente de validation critique
        """
        try:
            # Ressources en attente de validation critique
            critical_pending = self.validation_system.get_resources_for_critical_validation()
            
            # Format compatible avec l'interface existante
            sources = []
            for resource_id, resource_data in critical_pending.items():
                sources.append({
                    "id": resource_id,
                    "organization_name": resource_data.get("organization_name", ""),
                    "website": resource_data.get("website", ""),
                    "description": resource_data.get("description", ""),
                    "country_name": resource_data.get("country_name", ""),
                    "country_code": resource_data.get("country_code", ""),
                    "language": resource_data.get("language", ""),
                    # Format direct pour l'interface
                    "phone": resource_data.get("phone", ""),
                    "email": resource_data.get("email", ""),
                    # Format imbriqué pour compatibilité
                    "contact_info": {
                        "phone": resource_data.get("phone", ""),
                        "email": resource_data.get("email", "")
                    },
                    "workflow_status": "critical_pending",
                    "validation_metadata": resource_data.get("validation_metadata", {}),
                    # Champs supplémentaires pour validation
                    "discovered_at": resource_data.get("discovered_at", ""),
                    "source": resource_data.get("source", "llm_discovery")
                })
            
            return {
                "success": True,
                "sources": sources,
                "total_sources": len(sources)
            }
            
        except Exception as e:
            logger.error(f"Erreur get_sources_for_validation: {e}")
            return {
                "success": False,
                "sources": [],
                "error": str(e)
            }
    
    def validate_critical_source(self, source_id: str, action: str, admin_id: str, 
                                modifications: Optional[Dict] = None,
                                auto_transition_rag: bool = False) -> Dict[str, Any]:
        """
        ✅ AMÉLIORÉ - Endpoint compatible pour validation critique individuelle
        
        Args:
            source_id: ID de la ressource
            action: "validate_critical" ou "reject"
            admin_id: ID de l'administrateur
            modifications: Modifications optionnelles
            auto_transition_rag: Si True, transition automatique vers rag_ready après validation
                                 (Par défaut False pour garder contrôle manuel)
        
        Améliorations Phase 1.5:
        - Option de transition automatique vers RAG (désactivée par défaut)
        - Meilleure traçabilité des étapes suivantes
        """
        try:
            validation_action = ValidationAction.APPROVE if action == "validate_critical" else ValidationAction.REJECT
            
            # Critères critiques par défaut
            criteria_scores = {
                "security_verified": action == "validate_critical",
                "reliability_confirmed": action == "validate_critical",
                "data_accuracy": action == "validate_critical", 
                "professional_standards": action == "validate_critical",
                "legal_compliance": action == "validate_critical"
            }
            
            # Effectuer validation critique
            result = self.validation_system.perform_critical_validation(
                source_id, admin_id, validation_action, criteria_scores,
                f"Validation critique: {action}"
            )
            
            next_step_message = None
            transition_status = None
            
            # 🆕 NOUVEAU - Transition automatique optionnelle vers RAG
            if result.success and action == "validate_critical" and auto_transition_rag:
                try:
                    # Transition vers RAG_READY
                    rag_transition = self.workflow_manager.transition_status(
                        source_id,
                        "rag_ready",
                        admin_id,
                        "Transition automatique vers RAG après validation critique"
                    )
                    if rag_transition:
                        transition_status = "rag_ready"
                        next_step_message = "Auto-transitioned to RAG-ready"
                        logger.info(f"🔄 AUTO-TRANSITION: {source_id} → rag_ready (succès)")
                    else:
                        transition_status = "transition_failed"
                        next_step_message = "Failed to auto-transition to RAG"
                        logger.warning(f"⚠️ AUTO-TRANSITION vers RAG échouée pour {source_id}")
                except Exception as e:
                    logger.error(f"❌ Erreur transition RAG pour {source_id}: {e}")
                    transition_status = "transition_error"
                    next_step_message = f"Error during RAG transition: {str(e)}"
            elif result.success and action == "validate_critical":
                next_step_message = "Manual RAG formatting required"
            
            return {
                "success": result.success,
                "message": f"Ressource {action}" + (f" → {transition_status}" if transition_status else ""),
                "data": {
                    "source_id": source_id,
                    "new_status": result.next_stage.value if result.next_stage else "unknown",
                    "action": action,
                    "next_step": next_step_message,
                    "auto_transition": transition_status  # 🆕 NOUVEAU - Status de la transition
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Erreur validate_critical_source: {e}")
            return {
                "success": False,
                "message": f"Erreur: {str(e)}",
                "data": {"source_id": source_id}
            }
    
    # === UTILITY METHODS ===
    
    async def _get_countries_config_dynamic(self, language: str, max_countries: int) -> List[Dict]:
        """
        Configuration dynamique des pays via API REST Countries
        """
        try:
            # Utiliser le système dynamique
            countries = await get_countries_for_language(language, max_countries)
            logger.info(f"Pays dynamiques pour {language}: {len(countries)} trouvés")
            return countries
        except Exception as e:
            logger.error(f"Erreur geo dynamique {language}: {e}")
            # Fallback vers static
            return self._get_countries_config(language, max_countries)
    
    def _get_countries_config(self, language: str, max_countries: int) -> List[Dict]:
        """Configuration des pays pour la découverte - Version étendue pour vraies découvertes"""
        configs = {
            "FR": [
                {"name": "France", "code": "FR", "search_terms": ["cyberviolence", "cyberharcèlement", "harcèlement numérique"]},
                {"name": "Belgique", "code": "BE", "search_terms": ["cyberviolence", "harcèlement en ligne"]},
                {"name": "Suisse", "code": "CH", "search_terms": ["cyberharcèlement", "violence numérique"]},
                {"name": "Canada", "code": "CA", "search_terms": ["cyberintimidation", "harcèlement en ligne"]},
                {"name": "Luxembourg", "code": "LU", "search_terms": ["cyberviolence", "sécurité numérique"]}
            ],
            "EN": [
                {"name": "United Kingdom", "code": "GB", "search_terms": ["cyberbullying", "online harassment", "digital safety"]},
                {"name": "United States", "code": "US", "search_terms": ["cyberbullying", "online abuse", "digital citizenship"]},
                {"name": "Canada", "code": "CA", "search_terms": ["cyberbullying", "online safety"]},
                {"name": "Australia", "code": "AU", "search_terms": ["cyberbullying", "e-safety"]},
                {"name": "Ireland", "code": "IE", "search_terms": ["cyberbullying", "online protection"]}
            ],
            "ES": [
                {"name": "España", "code": "ES", "search_terms": ["ciberacoso", "violencia digital", "acoso online"]},
                {"name": "México", "code": "MX", "search_terms": ["ciberacoso", "violencia en línea", "seguridad en internet"]},
                {"name": "Argentina", "code": "AR", "search_terms": ["ciberacoso Argentina", "violencia digital Argentina", "acoso cibernético"]},
                {"name": "Colombia", "code": "CO", "search_terms": ["ciberacoso", "violencia digital", "seguridad digital"]}
            ],
            "IT": [
                {"name": "Italia", "code": "IT", "search_terms": ["cyberbullismo", "violenza digitale", "molestie online"]},
                {"name": "Svizzera", "code": "CH", "search_terms": ["cyberbullismo", "sicurezza digitale"]},
                {"name": "San Marino", "code": "SM", "search_terms": ["cyberbullismo", "protezione online"]}
            ],
            "DE": [
                {"name": "Deutschland", "code": "DE", "search_terms": ["Cybermobbing", "digitale Gewalt", "Online-Belästigung"]},
                {"name": "Österreich", "code": "AT", "search_terms": ["Cybermobbing", "digitale Sicherheit"]},
                {"name": "Schweiz", "code": "CH", "search_terms": ["Cybermobbing", "Online-Schutz"]}
            ],
            "PT": [
                {"name": "Portugal", "code": "PT", "search_terms": ["ciberbullying", "violência digital", "assédio online"]},
                {"name": "Brasil", "code": "BR", "search_terms": ["cyberbullying", "violência digital"]}
            ]
        }
        return configs.get(language, [])[:max_countries]
    
    def _get_country_name_mapping(self, language: str) -> Dict[str, str]:
        """
        ✅ FIX BUG: Mappe les noms courts du frontend vers les noms complets du backend
        
        Exemple:
        - Frontend: "UK" → Backend: "United Kingdom"
        - Frontend: "USA" → Backend: "United States"
        - Frontend: "Australia" → Backend: "Australia" (déjà correct)
        """
        mappings = {
            "FR": {
                "France": "France",
                "Belgique": "Belgique",
                "Suisse": "Suisse",
                "Canada": "Canada",
                "Luxembourg": "Luxembourg"
            },
            "EN": {
                "UK": "United Kingdom",
                "GB": "United Kingdom",
                "United Kingdom": "United Kingdom",
                "USA": "United States",
                "US": "United States",
                "United States": "United States",
                "Canada": "Canada",
                "Australia": "Australia",
                "AU": "Australia",
                "Ireland": "Ireland",
                "IE": "Ireland",
                "New Zealand": "New Zealand",
                "NZ": "New Zealand"
            },
            "ES": {
                "España": "España",
                "ES": "España",
                "México": "México",
                "MX": "México",
                "Argentina": "Argentina",
                "AR": "Argentina",
                "Colombia": "Colombia",
                "CO": "Colombia",
                "Perú": "Perú",
                "PE": "Perú"
            },
            "IT": {
                "Italia": "Italia",
                "IT": "Italia",
                "Svizzera": "Svizzera",
                "CH": "Svizzera",
                "San Marino": "San Marino",
                "SM": "San Marino",
                "Malta": "Malta",
                "MT": "Malta",
                "Vaticano": "Vaticano",
                "VA": "Vaticano"
            },
            "DE": {
                "Deutschland": "Deutschland",
                "DE": "Deutschland",
                "Österreich": "Österreich",
                "AT": "Österreich",
                "Schweiz": "Schweiz",
                "CH": "Schweiz",
                "Luxemburg": "Luxemburg",
                "LU": "Luxemburg",
                "Liechtenstein": "Liechtenstein",
                "LI": "Liechtenstein"
            },
            "PT": {
                "Portugal": "Portugal",
                "PT": "Portugal",
                "Brasil": "Brasil",
                "BR": "Brasil",
                "Angola": "Angola",
                "AO": "Angola",
                "Moçambique": "Moçambique",
                "MZ": "Moçambique",
                "Cabo Verde": "Cabo Verde",
                "CV": "Cabo Verde"
            }
        }
        return mappings.get(language, {})
    
    def _generate_discovery_prompt(self, country: str, language: str, search_term: str, category: str = "") -> str:
        """Génère le prompt pour la découverte LLM - Version améliorée avec support de catégorie (PHASE 2)"""
        # Mapping catégorie -> description pour le prompt
        category_descriptions = {
            "emergency": "services d'urgence contre le cyberharcèlement",
            "emergency_contact": "numéros d'urgence pour aide immédiate contre le cyberharcèlement",
            "procedure": "procédures de signalement du cyberharcèlement sur les réseaux sociaux",
            "procedure_plateforme": "comment signaler le cyberharcèlement sur les plateformes digitales",
            "authority": "autorités officielles de signalement du cyberharcèlement",
            "signalement_autorite": "autorités gouvernementales pour signaler le cyberharcèlement",
            "local": "associations locales de lutte contre le cyberharcèlement et la cyberviolence",
            "association_locale": "associations locales contre le cyberharcèlement et la cyberviolence"
        }
        
        category_desc = category_descriptions.get(category, search_term) if category else search_term
        
        if language == "FR":
            category_prompt = f" qui propose des {category_desc}" if category else ""
            return f"""Trouve-moi une association ou organisation LOCALE RÉELLE et EXISTANTE{category_prompt} spécifiquement en {country}.
            
IMPORTANT: 
- Donne-moi une organisation DIFFÉRENTE à chaque fois
- Vérifie que l'organisation existe vraiment  
- Cherche UNIQUEMENT des associations LOCALES basées en {country}
- Évite les organisations internationales ou d'autres pays
- Évite de répéter les mêmes organisations
- La catégorie cible est: {category_desc}

Réponds uniquement en français et sous ce format exact :
Nom : [nom exact de l'association/organisation]
URL : [site web officiel]
Description : [description en 1-2 phrases de leur action]
Téléphone : [numéro si disponible, sinon laisser vide]
Email : [email si disponible, sinon laisser vide]"""
        elif language == "ES":
            return f"""Encuéntrame una asociación u organización LOCAL REAL y EXISTENTE que luche contra {search_term} específicamente en {country}.
            
IMPORTANTE:
- Dame una organización DIFERENTE cada vez
- Verifica que la organización realmente existe
- Busca ÚNICAMENTE asociaciones LOCALES basadas en {country}
- Evita organizaciones internacionales o de otros países
- Evita repetir las mismas organizaciones

Responde solo en español y usa este formato exacto:
Nombre: [nombre exacto de la asociación/organización]
URL: [sitio web oficial]
Descripción: [descripción en 1-2 frases de su acción contra {search_term}]
Teléfono: [número si está disponible, sino dejar vacío]
Email: [email si está disponible, sino dejar vacío]"""
        elif language == "IT":
            return f"""Trovami un'associazione o organizzazione LOCALE REALE ed ESISTENTE che combatte {search_term} specificamente in {country}.
            
IMPORTANTE:
- Dammi un'organizzazione DIVERSA ogni volta
- Verifica che l'organizzazione esista davvero
- Cerca SOLO associazioni LOCALI basate in {country}
- Evita organizzazioni internazionali o di altri paesi
- Evita di ripetere le stesse organizzazioni

Rispondi solo in italiano usando questo formato esatto:
Nome: [nome esatto dell'associazione/organizzazione]
URL: [sito web ufficiale]
Descrizione: [descrizione in 1-2 frasi della loro azione contro {search_term}]
Telefono: [numero se disponibile, altrimenti lasciare vuoto]
Email: [email se disponibile, altrimenti lasciare vuoto]"""
        elif language == "DE":
            return f"""Finde mir eine LOKALE ECHTE und EXISTIERENDE Vereinigung oder Organisation, die gegen {search_term} speziell in {country} kämpft.
            
WICHTIG:
- Gib mir jedes Mal eine ANDERE Organisation
- Überprüfe, dass die Organisation wirklich existiert
- Suche NUR nach LOKALEN Vereinigungen mit Sitz in {country}
- Vermeide internationale Organisationen oder aus anderen Ländern
- Vermeide die Wiederholung derselben Organisationen

Antworte nur auf Deutsch in diesem exakten Format:
Namen: [exakter Name der Vereinigung/Organisation]
URL: [offizielle Website]
Beschreibung: [Beschreibung in 1-2 Sätzen ihrer Aktion gegen {search_term}]
Telefon: [Telefonnummer falls verfügbar, sonst leer lassen]
Email: [E-Mail falls verfügbar, sonst leer lassen]"""
        elif language == "PT":
            return f"""Encontre-me uma associação ou organização LOCAL REAL e EXISTENTE que lute contra {search_term} especificamente em {country}.
            
IMPORTANTE:
- Dê-me uma organização DIFERENTE a cada vez
- Verifique se a organização realmente existe
- Procure APENAS associações LOCAIS baseadas em {country}
- Evite organizações internacionais ou de outros países
- Evite repetir as mesmas organizações

Responda apenas em português usando este formato exato:
Nome: [nome exato da associação/organização]
URL: [site oficial]
Descrição: [descrição em 1-2 frases de sua ação contra {search_term}]
Telefone: [número se disponível, senão deixar vazio]
Email: [email se disponível, senão deixar vazio]"""
        else:
            return f"""Find me a LOCAL REAL and EXISTING association or organization fighting {search_term} specifically in {country}.
            
IMPORTANT:
- Give me a DIFFERENT organization each time
- Verify the organization actually exists
- Look for LOCAL associations ONLY based in {country}
- Avoid international organizations or from other countries
- Avoid repeating the same organizations

Respond only in English using this exact format:
Name: [exact name of the association/organization]
URL: [official website]
Description: [1-2 sentence description of their action against {search_term}]
Phone: [phone number if available, otherwise leave blank]
Email: [email if available, otherwise leave blank]"""
    
    def _parse_llm_response(self, response_text: str, country: Dict, language: str) -> Optional[Dict]:
        """Parse la réponse LLM en données structurées - Version TRÈS tolérante avec fallbacks"""
        import re
        
        logger.info(f"🔍 Parsing réponse LLM (longueur: {len(response_text)} chars)")
        logger.info(f"🔍 Réponse brute (première 300 chars): {response_text[:300]}")
        
        lines = response_text.strip().split('\n')
        data = {}
        lines_with_content = [l.strip() for l in lines if l.strip()]  # Garder les lignes non-vides
        
        # Parser TRÈS tolérant avec fallbacks multiples
        for line in lines_with_content:
            if not line:
                continue
                
            # Nom/Name/Nombre/Nome/Namen - Support toutes langues + patterns plus flexibles
            # ✅ AMÉLIORÉ: Chercher aussi sans restriction au début
            match = re.search(r"(Nom|Name|Nombre|Nome|Namen|Service|Organisation|Organization|Organisación|Organización)\s*[:\-]\s*(.+)", line, re.IGNORECASE)
            if match and not data.get("organization_name"):
                org_name = match.group(2).strip()
                # Nettoyer les caractères superflus
                org_name = re.sub(r'^[\*\-\•\s]+', '', org_name)
                org_name = re.sub(r'[\*\-\•\s]+$', '', org_name)
                if org_name and org_name.lower() not in ['n/a', 'none', 'na', '']:
                    data["organization_name"] = org_name
                    logger.info(f"✓ Nom trouvé: {data['organization_name']}")
            
            # ✅ FALLBACK NOM: Si pas de nom trouvé, chercher la première ligne substantive (qui n'est pas un label)
            if not data.get("organization_name") and len(line) > 5 and ':' not in line and '@' not in line and 'http' not in line.lower():
                # Cette ligne pourrait être un nom si elle n'a pas de séparateur structuré
                if len(line.split()) > 1 or len(line) > 10:  # Au moins 2 mots ou 10 caractères
                    potential_name = line
                    if potential_name.lower() not in ['n/a', 'none', 'na', 'not available']:
                        data["organization_name"] = potential_name
                        logger.info(f"✓ Nom extrait (fallback ligne): {data['organization_name']}")
            
            # Description/Descripción/Descrizione/Beschreibung - TRÈS flexible (PAS DE ^ pour permettre indentation)
            # ✅ AMÉLIORÉ: Sans restriction de début de ligne
            match = re.search(r"(Description|Desc|Descripción|Descrizione|Beschreibung|Mission|Spécialisation|Specialization|Missión|Action|Acciones|Azioni|Maßnahmen|Ação|About|Sobre|À propos)\s*[:\-]\s*(.+)", line, re.IGNORECASE)
            if match and not data.get("description"):
                desc_candidate = match.group(2).strip()
                # Nettoyer et valider
                desc_candidate = re.sub(r'^[\*\-\•\s]+', '', desc_candidate)
                desc_candidate = re.sub(r'[\*\-\•\s]+$', '', desc_candidate)
                if desc_candidate and desc_candidate.lower() not in ['n/a', 'none', 'na', 'not available', ''] and len(desc_candidate) > 5:
                    data["description"] = desc_candidate
                    logger.info(f"✓ Description trouvée (pattern): {data['description'][:100]}...")
            
            # URL/Site/Sitio/Sito/Website - Plus flexible, sans ^ restriction
            match = re.search(r"(URL|Site|Sitio|Sito|Website|Web|Sitio web|Website oficial|Lien|Link)\s*[:\-]\s*(https?://[\w\.-/]+)", line, re.IGNORECASE)
            if match and not data.get("website"):
                data["website"] = match.group(2).strip()
                logger.info(f"✓ URL trouvée: {data['website']}")
            
            # Chercher des URLs même sans préfixe
            url_match = re.search(r"(https?://[\w\.-/]+)", line)
            if url_match and not data.get("website"):
                data["website"] = url_match.group(1).strip()
                logger.info(f"✓ URL extraite: {data['website']}")
            
            # Téléphone/Phone - Plus flexible avec détection automatique (sans ^ restriction)
            match = re.search(r"(Téléphone|Phone|Tel|Teléfono|Telefono|Telefon|Numéro|Number|Teléfono:|Tel:)\s*[:\-]\s*(.+)", line, re.IGNORECASE)
            if match and not data.get("phone"):
                phone_candidate = match.group(2).strip()
                if phone_candidate.lower() not in ['n/a', 'none', 'na', 'not available', '']:
                    data["phone"] = phone_candidate
                    logger.info(f"✓ Téléphone trouvé: {data['phone']}")
            
            # Détection de nuéros même sans préfixe (formats européens/internationaux)
            phone_match = re.search(r"(\+?\d{1,4}[\s\-\.]?\d{1,4}[\s\-\.]?\d{1,4}[\s\-\.]?\d{1,4}[\s\-\.]?\d{0,4})", line)
            if phone_match and not data.get("phone") and len(phone_match.group(1).replace(" ", "").replace("-", "").replace(".", "")) >= 8:
                data["phone"] = phone_match.group(1).strip()
                logger.info(f"✓ Numéro extrait: {data['phone']}")
            
            # Email - Plus flexible (sans ^ restriction)
            match = re.search(r"(Email|Mail|Correo|E-mail|Contact|E-Mail)\s*[:\-]\s*(.+)", line, re.IGNORECASE)
            if match and not data.get("email"):
                email_candidate = match.group(2).strip()
                if email_candidate.lower() not in ['n/a', 'none', 'na', 'not available', '']:
                    data["email"] = email_candidate
                    logger.info(f"✓ Email trouvé: {data['email']}")
            
            # Détection d'emails même sans préfixe
            email_match = re.search(r"([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})", line)
            if email_match and not data.get("email"):
                data["email"] = email_match.group(1).strip()
                logger.info(f"✓ Email extrait: {data['email']}")
        
        # ✅ SUPER FALLBACK DESCRIPTION: Si aucune description trouvée, reconstruire à partir des lignes
        if not data.get("description") and len(lines_with_content) > 1:
            # Chercher une ligne qui pourrait être une description (longue, sans : ni @)
            for i, line in enumerate(lines_with_content):
                # Ignorer le nom si on l'a déjà trouvé, ignorer les URLs et emails
                if (line != data.get("organization_name") and 
                    len(line) > 10 and 
                    ':' not in line and 
                    '@' not in line and 
                    'http' not in line.lower() and
                    not any(x in line.lower() for x in ['+', 'phone', 'tel', 'email', 'contact'])):
                    # Cette ligne pourrait être une description
                    data["description"] = line
                    logger.info(f"✓ Description extraite (super fallback): {data['description'][:100]}...")
                    break
        
        # Validation stricte - Nom + Description + Au moins 1 contact (phone, email ou website)
        # ✅ PHASE 2 FIX: Description est obligatoire pour évaluer la ressource
        has_name = bool(data.get("organization_name"))
        has_description = bool(data.get("description"))
        has_contact = bool(data.get("website") or data.get("phone") or data.get("email"))
        
        logger.info(f"🔍 Validation stricte: nom={has_name}, description={has_description}, contact={has_contact}")
        logger.info(f"🔍 Données extraites: {data}")
        
        if has_name and has_description and has_contact:
            # Normaliser les noms pour la compatibilité
            # ✅ Ajouter tous les champs critiques pour la capture
            
            # ✅ NOUVEAU: Calculer le confiance en fonction de la complétude
            fields_count = sum([
                bool(data.get("organization_name")),
                bool(data.get("description")),
                bool(data.get("website")),
                bool(data.get("phone")),
                bool(data.get("email"))
            ])
            # Confiance: 0.6 (3 champs min) → 1.0 (tous les champs)
            confidence_score = min(1.0, 0.6 + (fields_count * 0.1))
            
            data.update({
                "name": data.get("organization_name", ""),  # ✅ Champ "name" pour compatibilité
                "organization_name": data.get("organization_name", ""),
                "description": data.get("description", ""),  # ✅ Description obligatoire
                "country": country["name"],  # ✅ Champ "country" pour la capture
                "country_name": country["name"],
                "country_code": country["code"],
                "language": language,
                "discovered_at": datetime.now().isoformat(),
                "source": "llm_discovery",
                "confidence_score": confidence_score  # ✅ Nouveau champ
            })
            logger.info(f"✅ Ressource valide ajoutée: {data['name']} ({country['code']}) - Confiance: {confidence_score:.2f}")
            return data
        else:
            # Log détaillé pour diagnostic
            reasons = []
            if not has_name:
                reasons.append("nom manquant")
            if not has_description:
                reasons.append("description manquante")
            if not has_contact:
                reasons.append("contact manquant")
            logger.warning(f"❌ Ressource rejetée - {', '.join(reasons)}")
        
        return None
    
    def _is_duplicate_resource(self, new_resource: Dict, country_code: str, category: str) -> bool:
        """
        Vérifie si une ressource est un doublon d'une ressource existante
        
        Args:
            new_resource: Nouvelle ressource à vérifier
            country_code: Code pays 
            category: Catégorie de la ressource
            
        Returns:
            True si c'est un doublon, False sinon
        """
        import re
        from difflib import SequenceMatcher
        
        new_name = new_resource.get('organization_name', '').strip()
        new_website = new_resource.get('website', '').strip()
        new_phone = new_resource.get('phone', '').strip()
        
        if not new_name:
            return False
        
        # Normaliser le nom pour comparaison
        def normalize_name(name):
            if not name:
                return ""
            # Supprimer caractères spéciaux, minuscules
            normalized = re.sub(r'[^\w\s]', '', name.lower())
            # Supprimer mots communs
            stop_words = ['association', 'organisation', 'foundation', 'e.v.', 'ev', 'asbl']
            words = [w for w in normalized.split() if w not in stop_words]
            return ' '.join(words)
        
        new_name_normalized = normalize_name(new_name)
        
        # Vérifier contre toutes les ressources existantes
        existing_resources = self.workflow_manager.unified_data
        
        for resource_id, existing_resource in existing_resources.items():
            existing_name = existing_resource.get('organization_name', '').strip()
            existing_website = existing_resource.get('website', '').strip()
            existing_phone = existing_resource.get('phone', '').strip()
            existing_country = existing_resource.get('country_code', '')
            
            # Même pays uniquement
            if existing_country != country_code:
                continue
            
            # 1. Doublon exact par nom
            if new_name == existing_name:
                logger.info(f"🔍 Doublon exact détecté: '{new_name}'")
                return True
            
            # 2. Doublon par similarité de nom (>85%)
            existing_name_normalized = normalize_name(existing_name)
            if existing_name_normalized and new_name_normalized:
                similarity = SequenceMatcher(None, new_name_normalized, existing_name_normalized).ratio()
                if similarity > 0.85:
                    logger.info(f"🔍 Doublon par similarité détecté: '{new_name}' vs '{existing_name}' ({similarity:.1%})")
                    return True
            
            # 3. Doublon par website identique
            if new_website and existing_website:
                # Extraire domaine pour comparaison
                def extract_domain(url):
                    match = re.search(r'https?://(?:www\.)?([^/]+)', url)
                    return match.group(1).lower() if match else url.lower()
                
                new_domain = extract_domain(new_website)
                existing_domain = extract_domain(existing_website)
                
                if new_domain == existing_domain:
                    logger.info(f"🔍 Doublon par domaine détecté: '{new_name}' ({new_domain})")
                    return True
            
            # 4. Doublon par téléphone identique
            if new_phone and existing_phone:
                # Normaliser les numéros (supprimer espaces, tirets, etc.)
                def normalize_phone(phone):
                    return re.sub(r'[\s\-\.\(\)]', '', phone)
                
                new_phone_normalized = normalize_phone(new_phone)
                existing_phone_normalized = normalize_phone(existing_phone)
                
                if new_phone_normalized == existing_phone_normalized:
                    logger.info(f"🔍 Doublon par téléphone détecté: '{new_name}' ({new_phone})")
                    return True
        
        return False
    
    def get_system_stats(self) -> Dict[str, Any]:
        """Statistiques complètes du système"""
        return {
            "llm_stats": self.llm_manager.get_stats(),
            "workflow_stats": self.workflow_manager.get_workflow_stats(),
            "validation_stats": self.validation_system.get_validation_stats(),
            "timestamp": datetime.now().isoformat()
        }

# Instance singleton
_api_adapter = None

def get_api_adapter() -> LegacyAPIAdapter:
    """Récupère l'instance singleton de l'adaptateur API"""
    global _api_adapter
    if _api_adapter is None:
        _api_adapter = LegacyAPIAdapter()
    return _api_adapter