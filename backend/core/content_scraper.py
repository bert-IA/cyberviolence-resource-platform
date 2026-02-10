"""
Module de scraping de contenu web pour enrichir le RAG avec le contenu des organisations.

Architecture:
1. 🌐 Scraper: URL → HTML brut (requests + BeautifulSoup)
2. 🧹 Cleaner: HTML → Texte propre (suppression navigation, footer, etc.)
3. ✂️ Chunker: Texte → Chunks sémantiques (par section/paragraphe)
4. 📋 Metadata: Enrichissement avec informations source
5. 💾 Storage: Sauvegarde JSON + préparation pour RAG

Objectif pédagogique: Comprendre chaque étape du pipeline RAG avec du contenu web
"""

import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Optional, Tuple
import time
import logging
import json
import os
from pathlib import Path
from urllib.parse import urljoin, urlparse
from urllib.robotparser import RobotFileParser
import re
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)

@dataclass
class ScrapedContent:
    """Structure pour le contenu scrapé"""
    url: str
    title: str
    content: str
    sections: List[Dict[str, str]]  # [{"title": "...", "content": "..."}]
    metadata: Dict[str, str]
    
    def __post_init__(self):
        """Validation après création"""
        if not self.content.strip():
            raise ValueError(f"Contenu vide pour {self.url}")

class ContentScraper:
    """
    🎓 CLASSE PÉDAGOGIQUE: Scraper de contenu web pour RAG
    
    Cette classe montre chaque étape du pipeline de scraping:
    1. Respect des robots.txt ✅
    2. Rate limiting ✅  
    3. Extraction intelligente du contenu ✅
    4. Chunking sémantique ✅
    """
    
    def __init__(self, delay_between_requests: float = 2.0, timeout: int = 30, 
                 storage_dir: str = "scraped_data"):
        """
        🔧 Configuration du scraper avec stockage
        
        Args:
            delay_between_requests: Délai entre requêtes (respect des serveurs)
            timeout: Timeout des requêtes HTTP
            storage_dir: Dossier de sauvegarde des données scrapées
        """
        self.delay = delay_between_requests
        self.timeout = timeout
        self.session = requests.Session()
        # User-Agent respectueux pour identifier notre bot
        self.session.headers.update({
            'User-Agent': 'StopCyberViolences-RAG-Bot/1.0 (Educational Content Indexing)'
        })
        self.last_request_time = 0
        
        # 💾 Configuration du stockage
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(exist_ok=True)
        
        # Fichier index des données scrapées
        self.index_file = self.storage_dir / "scraped_index.json"
        self._load_index()
        
    def _load_index(self):
        """📋 Charger l'index des données scrapées"""
        if self.index_file.exists():
            with open(self.index_file, 'r', encoding='utf-8') as f:
                self.scraped_index = json.load(f)
        else:
            self.scraped_index = {}
    
    def _save_index(self):
        """💾 Sauvegarder l'index des données scrapées"""
        with open(self.index_file, 'w', encoding='utf-8') as f:
            json.dump(self.scraped_index, f, indent=2, ensure_ascii=False)
    
    def _save_scraped_data(self, content: ScrapedContent) -> str:
        """
        💾 Sauvegarder les données scrapées en JSON
        
        Returns:
            Chemin du fichier sauvegardé
        """
        # Nom de fichier basé sur l'URL (sécurisé)
        parsed = urlparse(content.url)
        domain = parsed.netloc.replace('www.', '')
        filename = f"{domain}_{content.metadata['scraped_date']}.json"
        
        filepath = self.storage_dir / filename
        
        # Sauvegarder les données complètes
        data_to_save = asdict(content)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data_to_save, f, indent=2, ensure_ascii=False)
        
        # Mettre à jour l'index
        self.scraped_index[content.url] = {
            'filename': filename,
            'organization': content.metadata['organization'],
            'scraped_date': content.metadata['scraped_date'],
            'sections_count': int(content.metadata['sections_count']),
            'content_length': int(content.metadata['content_length']),
            'filepath': str(filepath)
        }
        self._save_index()
        
        logger.info(f"💾 Données sauvegardées: {filepath}")
        return str(filepath)
    
    def list_scraped_data(self) -> Dict[str, Dict]:
        """📋 Lister toutes les données scrapées"""
        return self.scraped_index.copy()
    
    def load_scraped_content(self, url: str) -> Optional[ScrapedContent]:
        """📂 Charger le contenu scrapé depuis le stockage"""
        if url not in self.scraped_index:
            return None
        
        filepath = Path(self.scraped_index[url]['filepath'])
        if not filepath.exists():
            logger.warning(f"⚠️ Fichier manquant: {filepath}")
            return None
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            return ScrapedContent(**data)
        except Exception as e:
            logger.error(f"❌ Erreur chargement {filepath}: {e}")
            return None
        
    def _respect_rate_limit(self):
        """🕐 Rate limiting: Éviter de surcharger les serveurs"""
        elapsed = time.time() - self.last_request_time
        if elapsed < self.delay:
            sleep_time = self.delay - elapsed
            logger.info(f"⏳ Rate limiting: sleeping {sleep_time:.1f}s")
            time.sleep(sleep_time)
        self.last_request_time = time.time()
    
    def _check_robots_txt(self, url: str) -> bool:
        """
        🤖 Vérification robots.txt (Bonne pratique web scraping)
        
        Returns:
            True si le scraping est autorisé
        """
        try:
            parsed = urlparse(url)
            robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"
            
            rp = RobotFileParser()
            rp.set_url(robots_url)
            rp.read()
            
            user_agent = self.session.headers.get('User-Agent', '*')
            can_fetch = rp.can_fetch(user_agent, url)
            
            if not can_fetch:
                logger.warning(f"🚫 robots.txt interdit le scraping de: {url}")
            
            return can_fetch
            
        except Exception as e:
            logger.warning(f"⚠️ Erreur robots.txt pour {url}: {e}")
            # En cas d'erreur, on autorise (principe de courtoisie)
            return True
    
    def _fetch_page(self, url: str) -> Optional[str]:
        """
        🌐 Récupération de la page HTML
        
        Returns:
            HTML content ou None si erreur
        """
        # Vérification robots.txt
        if not self._check_robots_txt(url):
            return None
            
        # Rate limiting
        self._respect_rate_limit()
        
        try:
            logger.info(f"🔍 Fetching: {url}")
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            
            # Vérification du content-type
            content_type = response.headers.get('content-type', '').lower()
            if 'text/html' not in content_type:
                logger.warning(f"⚠️ Content-Type non-HTML: {content_type}")
                return None
                
            return response.text
            
        except requests.RequestException as e:
            logger.error(f"❌ Erreur HTTP pour {url}: {e}")
            return None
        except Exception as e:
            logger.error(f"❌ Erreur inattendue pour {url}: {e}")
            return None

    def _extract_main_content(self, html: str, url: str) -> Tuple[str, List[Dict[str, str]]]:
        """
        🧹 Extraction intelligente du contenu principal
        
        Stratégie:
        1. Identifier le contenu principal (éviter nav, footer, sidebar)
        2. Extraire par sections sémantiques 
        3. Nettoyer le texte
        
        Returns:
            (contenu_complet, sections_structurées)
        """
        soup = BeautifulSoup(html, 'html.parser')
        
        # 🗑️ Suppression des éléments non-utiles
        for element in soup(['script', 'style', 'nav', 'footer', 'aside', 'header']):
            element.decompose()
            
        # 🎯 Tentative d'identifier le contenu principal
        main_content = None
        
        # Sélecteurs courants pour le contenu principal
        main_selectors = [
            'main', '[role="main"]', '#main', '.main',
            '#content', '.content', '.main-content',
            'article', '.article'
        ]
        
        for selector in main_selectors:
            main_content = soup.select_one(selector)
            if main_content:
                logger.info(f"✅ Contenu principal trouvé avec: {selector}")
                break
        
        # Fallback: prendre le body
        if not main_content:
            main_content = soup.find('body') or soup
            logger.info("📄 Utilisation du body complet")
        
        # 📝 Extraction des sections structurées
        sections = self._extract_sections(main_content)
        
        # 🧹 Contenu complet nettoyé
        full_text = self._clean_text(main_content.get_text())
        
        return full_text, sections
    
    def _extract_sections(self, element) -> List[Dict[str, str]]:
        """
        ✂️ CHUNKING SÉMANTIQUE: Extraction par sections logiques
        
        Cette méthode montre comment découper le contenu de façon intelligente
        plutôt qu'avec des tailles fixes
        """
        sections = []
        
        # 🏷️ Recherche des titres de section (H1, H2, H3...)
        headings = element.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
        
        for i, heading in enumerate(headings):
            title = self._clean_text(heading.get_text())
            
            # 📄 Collecte du contenu jusqu'au prochain titre
            content_parts = []
            current = heading.next_sibling
            
            while current:
                # Arrêter si on trouve un autre titre de même niveau ou supérieur
                if (hasattr(current, 'name') and 
                    current.name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
                    heading_level = int(heading.name[1])
                    current_level = int(current.name[1])
                    if current_level <= heading_level:
                        break
                
                # Ajouter le contenu textuel
                if hasattr(current, 'get_text'):
                    text = self._clean_text(current.get_text())
                    if text.strip():
                        content_parts.append(text)
                
                current = current.next_sibling
            
            content = ' '.join(content_parts).strip()
            
            if content and len(content) > 50:  # Filtrer les sections trop courtes
                sections.append({
                    'title': title,
                    'content': content,
                    'heading_level': heading.name
                })
        
        # 📋 Si pas de sections trouvées, découper par paragraphes
        if not sections:
            paragraphs = element.find_all('p')
            for i, p in enumerate(paragraphs):
                text = self._clean_text(p.get_text())
                if len(text) > 100:  # Paragraphes significatifs
                    sections.append({
                        'title': f"Paragraphe {i+1}",
                        'content': text,
                        'heading_level': 'p'
                    })
        
        logger.info(f"📚 {len(sections)} sections extraites")
        return sections
    
    def _clean_text(self, text: str) -> str:
        """🧽 Nettoyage du texte"""
        if not text:
            return ""
        
        # Normalisation des espaces
        text = re.sub(r'\s+', ' ', text)
        # Suppression des espaces en début/fin
        text = text.strip()
        # Suppression des caractères de contrôle
        text = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', text)
        
        return text

    def scrape_url(self, url: str, organization_name: str = "", 
                   country: str = "", language: str = "") -> Optional[ScrapedContent]:
        """
        🎯 MÉTHODE PRINCIPALE: Scraper une URL complète
        
        Cette méthode orchestre tout le pipeline de scraping
        """
        logger.info(f"🚀 Début scraping: {url}")
        
        # 1. Récupération HTML
        html = self._fetch_page(url)
        if not html:
            return None
        
        # 2. Extraction du contenu
        try:
            full_content, sections = self._extract_main_content(html, url)
            
            if not full_content.strip():
                logger.warning(f"⚠️ Contenu vide après extraction: {url}")
                return None
            
            # 3. Extraction du titre de la page
            soup = BeautifulSoup(html, 'html.parser')
            title_tag = soup.find('title')
            title = self._clean_text(title_tag.get_text()) if title_tag else "Sans titre"
            
            # 4. Métadonnées enrichies
            metadata = {
                'organization': organization_name,
                'country': country,
                'language': language,
                'content_type': 'scraped_content',
                'scraped_date': time.strftime('%Y-%m-%d'),
                'sections_count': str(len(sections)),
                'content_length': str(len(full_content))
            }
            
            result = ScrapedContent(
                url=url,
                title=title,
                content=full_content,
                sections=sections,
                metadata=metadata
            )
            
            # 💾 Sauvegarder automatiquement
            saved_path = self._save_scraped_data(result)
            
            logger.info(f"✅ Scraping réussi: {url} ({len(sections)} sections, {len(full_content)} chars)")
            logger.info(f"💾 Sauvegardé dans: {saved_path}")
            return result
            
        except Exception as e:
            logger.error(f"❌ Erreur extraction contenu {url}: {e}")
            return None

    def scrape_organization_urls(self, urls: List[str], organization_name: str,
                               country: str = "", language: str = "") -> List[ScrapedContent]:
        """
        📋 Scraper plusieurs URLs d'une même organisation
        
        Utile pour scraper page d'accueil + pages ressources d'une association
        """
        results = []
        
        logger.info(f"🏢 Scraping organisation: {organization_name} ({len(urls)} URLs)")
        
        for i, url in enumerate(urls):
            logger.info(f"📄 [{i+1}/{len(urls)}] Processing: {url}")
            
            content = self.scrape_url(url, organization_name, country, language)
            if content:
                results.append(content)
            else:
                logger.warning(f"⚠️ Échec scraping: {url}")
        
        logger.info(f"✅ Scraping organisation terminé: {len(results)}/{len(urls)} réussis")
        return results


# 🎓 Fonction utilitaire pour tests et exploration
def test_scraper_with_storage():
    """Test du scraper avec sauvegarde pour voir où sont stockés les résultats"""
    scraper = ContentScraper(delay_between_requests=1.0, storage_dir="scraped_data")
    
    print("🚀 Test du scraper avec stockage...")
    
    # Test avec e-enfance (depuis tes ressources critiques)
    url = "https://e-enfance.org"
    result = scraper.scrape_url(url, "e-Enfance", "France", "FR")
    
    if result:
        print(f"✅ Scraping réussi!")
        print(f"📄 Titre: {result.title}")
        print(f"📚 Sections: {len(result.sections)}")
        print(f"📝 Contenu: {len(result.content)} caractères")
        
        print("\n" + "="*50)
        print("💾 STOCKAGE DES RÉSULTATS:")
        print("="*50)
        
        # Afficher l'index des données
        index = scraper.list_scraped_data()
        for url, info in index.items():
            print(f"🌐 URL: {url}")
            print(f"📁 Fichier: {info['filename']}")
            print(f"� Organisation: {info['organization']}")
            print(f"📅 Date: {info['scraped_date']}")
            print(f"� {info['sections_count']} sections, {info['content_length']} caractères")
            print(f"📂 Chemin complet: {info['filepath']}")
            print()
        
        # Test de rechargement
        print("🔄 Test de rechargement depuis le stockage...")
        reloaded = scraper.load_scraped_content(url)
        if reloaded:
            print(f"✅ Rechargement réussi! {len(reloaded.sections)} sections")
        else:
            print("❌ Échec du rechargement")
            
    else:
        print("❌ Test échoué")

if __name__ == "__main__":
    test_scraper_with_storage()