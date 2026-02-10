"""
Module de scraping en masse des ressources critiques avec gestion intelligente des doublons.

🎯 Objectifs :
1. Lire rag_resources.json
2. Normaliser les URLs pour éviter les doublons
3. Vérifier l'historique de scraping
4. Décider intelligemment quoi scraper
5. Gérer les erreurs et reprises

Architecture anti-doublons :
- Normalisation d'URL (www, https, trailing slash)
- Index de scraping avec timestamps
- Politique de re-scraping (jamais/après X jours/si erreur)
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Set
from urllib.parse import urlparse, urlunparse
import time
from datetime import datetime, timedelta
from dataclasses import dataclass

from .content_scraper import ContentScraper, ScrapedContent

logger = logging.getLogger(__name__)

@dataclass
class ScrapingDecision:
    """Décision de scraping pour une ressource"""
    should_scrape: bool
    reason: str
    url_normalized: str
    organization: str
    
class BulkScraper:
    """
    🎓 CLASSE PÉDAGOGIQUE : Scraping en masse avec gestion des doublons
    
    Cette classe montre comment :
    1. Normaliser les URLs pour éviter les doublons techniques
    2. Gérer un index de scraping avec historique
    3. Décider intelligemment quoi re-scraper
    4. Traiter des ressources en batch avec gestion d'erreurs
    """
    
    def __init__(self, rag_resources_file: str = "rag_resources.json", 
                 storage_dir: str = "scraped_data",
                 re_scrape_after_days: int = 30):
        """
        🔧 Configuration du scraper en masse
        
        Args:
            rag_resources_file: Fichier des ressources critiques
            storage_dir: Dossier de stockage 
            re_scrape_after_days: Re-scraper après X jours (0 = jamais)
        """
        self.rag_resources_file = Path(rag_resources_file)
        self.storage_dir = Path(storage_dir)
        self.re_scrape_after_days = re_scrape_after_days
        
        # Initialiser le scraper de base
        self.scraper = ContentScraper(
            delay_between_requests=3.0,  # Plus prudent pour le bulk
            storage_dir=str(self.storage_dir)
        )
        
        # Charger les ressources critiques
        self.critical_resources = self._load_critical_resources()
        
        logger.info(f"📋 {len(self.critical_resources)} ressources critiques chargées")
    
    def _load_critical_resources(self) -> Dict:
        """📂 Charger les ressources critiques depuis JSON"""
        if not self.rag_resources_file.exists():
            logger.error(f"❌ Fichier manquant: {self.rag_resources_file}")
            return {}
        
        try:
            with open(self.rag_resources_file, 'r', encoding='utf-8') as f:
                resources = json.load(f)
            
            logger.info(f"✅ {len(resources)} ressources chargées depuis {self.rag_resources_file}")
            return resources
            
        except Exception as e:
            logger.error(f"❌ Erreur lecture {self.rag_resources_file}: {e}")
            return {}
    
    def _normalize_url(self, url: str) -> str:
        """
        🧹 Normalisation d'URL pour éviter les doublons techniques
        
        Transformations :
        - http → https (si possible)
        - Suppression www. 
        - Suppression trailing slash
        - Minuscules pour le domaine
        
        Exemple:
        HTTP://WWW.E-ENFANCE.ORG/ → https://e-enfance.org
        """
        if not url or not url.strip():
            return ""
        
        try:
            # Parser l'URL
            parsed = urlparse(url.strip())
            
            # Normaliser le scheme (préférer https)
            scheme = parsed.scheme.lower()
            if scheme not in ['http', 'https']:
                scheme = 'https'  # Default sécurisé
            
            # Normaliser le netloc (domaine)
            netloc = parsed.netloc.lower()
            # Supprimer www. (optionnel selon la stratégie)
            if netloc.startswith('www.'):
                netloc = netloc[4:]
            
            # Normaliser le path (supprimer trailing slash sauf pour racine)
            path = parsed.path
            if path.endswith('/') and len(path) > 1:
                path = path[:-1]
            
            # Reconstruire l'URL normalisée
            normalized = urlunparse((
                scheme, netloc, path, 
                parsed.params, parsed.query, parsed.fragment
            ))
            
            if normalized != url:
                logger.debug(f"🔄 URL normalisée: {url} → {normalized}")
            
            return normalized
            
        except Exception as e:
            logger.warning(f"⚠️ Erreur normalisation URL {url}: {e}")
            return url  # Retourner l'original si erreur
    
    def _is_already_scraped(self, normalized_url: str) -> Tuple[bool, Optional[Dict]]:
        """
        🔍 Vérifier si une URL a déjà été scrapée
        
        Returns:
            (is_scraped, scraping_info)
        """
        scraped_index = self.scraper.list_scraped_data()
        
        # Vérifier URL exacte
        if normalized_url in scraped_index:
            return True, scraped_index[normalized_url]
        
        # Vérifier variations possibles (avec/sans www, http/https)
        parsed = urlparse(normalized_url)
        
        # Variations à tester
        variations = [
            # Avec www
            f"{parsed.scheme}://www.{parsed.netloc}{parsed.path}",
            # HTTP au lieu de HTTPS  
            f"http://{parsed.netloc}{parsed.path}",
            # Avec trailing slash
            f"{normalized_url}/",
        ]
        
        for variation in variations:
            if variation in scraped_index:
                logger.info(f"🔍 URL trouvée via variation: {variation}")
                return True, scraped_index[variation]
        
        return False, None
    
    def _should_re_scrape(self, scraping_info: Dict) -> bool:
        """
        🤔 Décider si on doit re-scraper une ressource existante
        
        Politique de re-scraping :
        1. Si re_scrape_after_days = 0 → Jamais re-scraper
        2. Si age > re_scrape_after_days → Re-scraper
        3. Si scraping précédent en erreur → Re-scraper
        """
        if self.re_scrape_after_days <= 0:
            return False  # Jamais re-scraper
        
        try:
            scraped_date = datetime.strptime(scraping_info['scraped_date'], '%Y-%m-%d')
            age_days = (datetime.now() - scraped_date).days
            
            should_rescrape = age_days > self.re_scrape_after_days
            
            if should_rescrape:
                logger.info(f"📅 Re-scraping nécessaire: {age_days} jours > {self.re_scrape_after_days}")
            
            return should_rescrape
            
        except Exception as e:
            logger.warning(f"⚠️ Erreur analyse date scraping: {e}")
            return True  # En cas d'erreur, re-scraper par sécurité
    
    def analyze_scraping_needs(self) -> List[ScrapingDecision]:
        """
        📊 MÉTHODE PÉDAGOGIQUE : Analyser toutes les ressources et décider quoi scraper
        
        Cette méthode montre la logique de décision complète :
        1. Extraire URLs des ressources critiques
        2. Normaliser les URLs
        3. Vérifier l'historique
        4. Décider selon la politique
        """
        decisions = []
        processed_urls = set()  # Éviter les doublons dans la même analyse
        
        logger.info("🔍 Analyse des besoins de scraping...")
        
        for resource_id, resource_data in self.critical_resources.items():
            # Extraire l'URL et les métadonnées
            url = resource_data.get('website', '').strip()
            organization = resource_data.get('organization_name', 'Unknown')
            
            if not url:
                logger.warning(f"⚠️ Pas d'URL pour {resource_id} ({organization})")
                continue
            
            # Normaliser l'URL
            normalized_url = self._normalize_url(url)
            
            # Éviter les doublons dans cette analyse
            if normalized_url in processed_urls:
                logger.info(f"🔄 URL déjà analysée dans ce batch: {normalized_url}")
                decisions.append(ScrapingDecision(
                    should_scrape=False,
                    reason="Doublon dans cette analyse",
                    url_normalized=normalized_url,
                    organization=organization
                ))
                continue
            
            processed_urls.add(normalized_url)
            
            # Vérifier si déjà scrapé
            is_scraped, scraping_info = self._is_already_scraped(normalized_url)
            
            if not is_scraped:
                # Nouveau scraping nécessaire
                decisions.append(ScrapingDecision(
                    should_scrape=True,
                    reason="Jamais scrapé",
                    url_normalized=normalized_url,
                    organization=organization
                ))
            elif self._should_re_scrape(scraping_info):
                # Re-scraping nécessaire
                decisions.append(ScrapingDecision(
                    should_scrape=True,
                    reason=f"Re-scraping après {self.re_scrape_after_days} jours",
                    url_normalized=normalized_url,
                    organization=organization
                ))
            else:
                # Pas besoin de scraper
                decisions.append(ScrapingDecision(
                    should_scrape=False,
                    reason=f"Déjà scrapé le {scraping_info['scraped_date']}",
                    url_normalized=normalized_url,
                    organization=organization
                ))
        
        # Statistiques
        to_scrape = [d for d in decisions if d.should_scrape]
        already_done = [d for d in decisions if not d.should_scrape]
        
        logger.info(f"📊 Analyse terminée:")
        logger.info(f"   🆕 À scraper: {len(to_scrape)}")
        logger.info(f"   ✅ Déjà fait: {len(already_done)}")
        
        return decisions
    
    def print_scraping_plan(self, decisions: List[ScrapingDecision]):
        """📋 Afficher le plan de scraping de manière lisible"""
        print("\n" + "="*60)
        print("📋 PLAN DE SCRAPING - RESSOURCES CRITIQUES")
        print("="*60)
        
        to_scrape = [d for d in decisions if d.should_scrape]
        already_done = [d for d in decisions if not d.should_scrape]
        
        if to_scrape:
            print(f"\n🆕 SITES À SCRAPER ({len(to_scrape)}):")
            for i, decision in enumerate(to_scrape, 1):
                print(f"  {i:2d}. {decision.organization}")
                print(f"      URL: {decision.url_normalized}")
                print(f"      Raison: {decision.reason}")
                print()
        
        if already_done:
            print(f"\n✅ SITES DÉJÀ TRAITÉS ({len(already_done)}):")
            for decision in already_done[:5]:  # Limiter l'affichage
                print(f"  • {decision.organization} - {decision.reason}")
            if len(already_done) > 5:
                print(f"  ... et {len(already_done) - 5} autres")
        
        print("="*60)
    
    def execute_scraping(self, decisions: List[ScrapingDecision], 
                        dry_run: bool = False) -> Dict[str, int]:
        """
        🚀 Exécuter le scraping selon les décisions
        
        Args:
            decisions: Liste des décisions de scraping
            dry_run: Si True, simule sans scraper réellement
        
        Returns:
            Statistiques de l'exécution
        """
        to_scrape = [d for d in decisions if d.should_scrape]
        
        if dry_run:
            print(f"🧪 DRY RUN: Scraperait {len(to_scrape)} sites")
            return {"would_scrape": len(to_scrape), "skipped": len(decisions) - len(to_scrape)}
        
        stats = {"success": 0, "failed": 0, "skipped": 0}
        
        logger.info(f"🚀 Début du scraping en masse: {len(to_scrape)} sites")
        
        for i, decision in enumerate(to_scrape, 1):
            logger.info(f"📄 [{i}/{len(to_scrape)}] Scraping: {decision.organization}")
            logger.info(f"    URL: {decision.url_normalized}")
            
            try:
                # Extraire les métadonnées depuis les ressources critiques
                resource_data = None
                for res_data in self.critical_resources.values():
                    if self._normalize_url(res_data.get('website', '')) == decision.url_normalized:
                        resource_data = res_data
                        break
                
                country = resource_data.get('country_name', '') if resource_data else ''
                language = resource_data.get('metadata', {}).get('language', '') if resource_data else ''
                
                # Scraper
                result = self.scraper.scrape_url(
                    decision.url_normalized,
                    decision.organization,
                    country,
                    language
                )
                
                if result:
                    stats["success"] += 1
                    logger.info(f"✅ Scraping réussi: {decision.organization}")
                else:
                    stats["failed"] += 1
                    logger.error(f"❌ Scraping échoué: {decision.organization}")
                
            except Exception as e:
                stats["failed"] += 1
                logger.error(f"❌ Erreur scraping {decision.organization}: {e}")
            
            # Petit délai entre les sites pour être courtois
            if i < len(to_scrape):
                time.sleep(1)
        
        logger.info(f"🏁 Scraping terminé: {stats['success']} réussis, {stats['failed']} échecs")
        return stats


def main():
    """🎯 Fonction principale pour tester le bulk scraper"""
    print("🚀 Test du Bulk Scraper avec gestion des doublons")
    
    # Initialiser
    bulk_scraper = BulkScraper(
        rag_resources_file="rag_resources.json",
        re_scrape_after_days=30
    )
    
    # Analyser
    decisions = bulk_scraper.analyze_scraping_needs()
    
    # Afficher le plan
    bulk_scraper.print_scraping_plan(decisions)
    
    # Demander confirmation
    to_scrape_count = len([d for d in decisions if d.should_scrape])
    if to_scrape_count > 0:
        print(f"\n❓ Voulez-vous procéder au scraping de {to_scrape_count} sites ? (y/N)")
        response = input().strip().lower()
        
        if response == 'y':
            stats = bulk_scraper.execute_scraping(decisions)
            print(f"\n📊 Résultats: {stats}")
        else:
            print("⏸️ Scraping annulé")
    else:
        print("\n✅ Aucun scraping nécessaire!")

if __name__ == "__main__":
    main()