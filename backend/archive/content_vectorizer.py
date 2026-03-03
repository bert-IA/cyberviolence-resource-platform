"""
Module de vectorisation du contenu scrapé pour intégration dans le RAG.

🎯 Objectifs :
1. Prendre le contenu scrapé (JSON) 
2. Le chunker de façon optimale pour RAG
3. Générer les embeddings avec métadonnées (pays, langue)
4. Stocker dans la collection "rag_content" de PostgreSQL
5. Permettre la recherche vectorielle filtrée par pays/langue

Architecture RAG with Metadata:
- Content chunking: Par sections sémantiques (préservation contexte)
- Embeddings: GoogleGenerativeAIEmbeddings (cohérence avec RAG existant)
- Metadata filtering: Pays, langue, organisation, type_content
- Vector storage: PGVector (même infrastructure que docs_youth/docs_adult)
"""

import sys
import os
from pathlib import Path
from typing import List, Dict, Optional, Tuple
import json
import logging
from datetime import datetime

# Ajouter le chemin vers l'API pour accéder aux services RAG
sys.path.append(str(Path(__file__).parent.parent.parent / "api"))

from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_postgres import PGVector
from langchain_core.documents import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter

# Import des modules locaux
from .content_scraper import ScrapedContent
from .bulk_scraper import BulkScraper

logger = logging.getLogger(__name__)

class ScrapedContentVectorizer:
    """
    🎓 CLASSE PÉDAGOGIQUE : Vectorisation du contenu scrapé pour RAG
    
    Cette classe montre comment :
    1. Transformer le contenu scrapé en chunks optimaux pour RAG
    2. Enrichir chaque chunk avec des métadonnées pour le filtrage
    3. Générer des embeddings avec le même modèle que le RAG existant
    4. Stocker dans PostgreSQL avec possibilité de recherche filtrée
    """
    
    def __init__(self, db_url: str, collection_name: str = "rag_content"):
        """
        🔧 Configuration du vectorizer
        
        Args:
            db_url: URL de connexion PostgreSQL
            collection_name: Nom de la collection pour le contenu scrapé
        """
        self.db_url = db_url
        self.collection_name = collection_name
        
        # Utiliser le même modèle d'embeddings que le RAG existant
        self.embeddings = GoogleGenerativeAIEmbeddings(model="gemini-embedding-001")
        
        # Configuration du chunking (adaptée au contenu web)
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=800,        # Plus petit que les PDFs (contenu web plus dense)
            chunk_overlap=150,     # Overlap important pour préserver le contexte
            separators=["\n\n", "\n", ". ", " "],  # Séparateurs naturels
            keep_separator=False
        )
        
        # Initialiser la base vectorielle
        self.vector_store = PGVector(
            embeddings=self.embeddings,
            collection_name=self.collection_name,
            connection=self.db_url,
            use_jsonb=True
        )
        
        logger.info(f"🧠 Vectorizer initialisé: collection '{self.collection_name}'")
    
    def _create_chunks_from_scraped_content(self, scraped_content: ScrapedContent) -> List[Document]:
        """
        ✂️ CHUNKING INTELLIGENT : Transformer le contenu scrapé en chunks RAG
        
        Stratégie hybride :
        1. Utiliser les sections sémantiques quand disponibles
        2. Chunker RecursiveCharacterTextSplitter pour les sections trop longues
        3. Enrichir chaque chunk avec métadonnées complètes
        
        Args:
            scraped_content: Contenu scrapé à vectoriser
            
        Returns:
            Liste de Documents LangChain avec métadonnées
        """
        documents = []
        
        # Métadonnées de base pour tous les chunks
        base_metadata = {
            "source": scraped_content.url,
            "organization": scraped_content.metadata.get("organization", "Unknown"),
            "country": scraped_content.metadata.get("country", ""),
            "language": scraped_content.metadata.get("language", ""),
            "content_type": "scraped_content",
            "scraped_date": scraped_content.metadata.get("scraped_date", ""),
            "title": scraped_content.title
        }
        
        logger.info(f"📄 Chunking: {scraped_content.url} ({len(scraped_content.sections)} sections)")
        
        # Stratégie 1: Utiliser les sections sémantiques
        for i, section in enumerate(scraped_content.sections):
            section_content = section["content"].strip()
            section_title = section["title"].strip()
            
            if not section_content or len(section_content) < 50:
                continue  # Ignorer les sections trop courtes
            
            # Si la section est courte, l'utiliser directement
            if len(section_content) <= 800:
                # Enrichir le contenu avec le titre de section
                full_content = f"{section_title}\n\n{section_content}" if section_title != f"Paragraphe {i+1}" else section_content
                
                section_metadata = base_metadata.copy()
                section_metadata.update({
                    "section_title": section_title,
                    "section_index": i,
                    "chunk_type": "semantic_section"
                })
                
                documents.append(Document(
                    page_content=full_content,
                    metadata=section_metadata
                ))
                
            else:
                # Si la section est longue, la chunker davantage
                section_text = f"{section_title}\n\n{section_content}"
                sub_chunks = self.text_splitter.split_text(section_text)
                
                for j, chunk in enumerate(sub_chunks):
                    if len(chunk.strip()) < 50:
                        continue
                    
                    chunk_metadata = base_metadata.copy()
                    chunk_metadata.update({
                        "section_title": section_title,
                        "section_index": i,
                        "sub_chunk_index": j,
                        "chunk_type": "semantic_section_split"
                    })
                    
                    documents.append(Document(
                        page_content=chunk,
                        metadata=chunk_metadata
                    ))
        
        # Stratégie 2: Fallback sur le contenu complet si pas de sections
        if not documents and scraped_content.content:
            logger.info("📝 Pas de sections valides, chunking du contenu complet")
            
            full_chunks = self.text_splitter.split_text(scraped_content.content)
            
            for i, chunk in enumerate(full_chunks):
                if len(chunk.strip()) < 50:
                    continue
                
                chunk_metadata = base_metadata.copy()
                chunk_metadata.update({
                    "section_title": "Full content",
                    "section_index": i,
                    "chunk_type": "full_content_split"
                })
                
                documents.append(Document(
                    page_content=chunk,
                    metadata=chunk_metadata
                ))
        
        logger.info(f"✅ {len(documents)} chunks créés pour {scraped_content.url}")
        return documents
    
    def vectorize_scraped_content(self, scraped_content: ScrapedContent) -> bool:
        """
        🧠 VECTORISATION : Transformer le contenu scrapé en vecteurs recherchables
        
        Pipeline complet :
        1. Chunking intelligent du contenu
        2. Génération des embeddings 
        3. Stockage dans PostgreSQL avec métadonnées
        
        Args:
            scraped_content: Contenu à vectoriser
            
        Returns:
            True si succès, False sinon
        """
        try:
            logger.info(f"🚀 Début vectorisation: {scraped_content.url}")
            
            # 1. Créer les chunks avec métadonnées
            documents = self._create_chunks_from_scraped_content(scraped_content)
            
            if not documents:
                logger.warning(f"⚠️ Aucun chunk créé pour {scraped_content.url}")
                return False
            
            # 2. Vérifier si déjà vectorisé (éviter les doublons)
            if self._is_already_vectorized(scraped_content.url):
                logger.info(f"🔄 Déjà vectorisé, suppression des anciens chunks...")
                self._remove_existing_chunks(scraped_content.url)
            
            # 3. Ajouter à la base vectorielle
            logger.info(f"🧠 Génération embeddings pour {len(documents)} chunks...")
            self.vector_store.add_documents(documents)
            
            logger.info(f"✅ Vectorisation réussie: {scraped_content.url} ({len(documents)} chunks)")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erreur vectorisation {scraped_content.url}: {e}")
            return False
    
    def _is_already_vectorized(self, url: str) -> bool:
        """🔍 Vérifier si une URL est déjà vectorisée"""
        try:
            # Rechercher par métadonnée source
            results = self.vector_store.similarity_search(
                query="test",  # Query dummy
                k=1,
                filter={"source": url}
            )
            return len(results) > 0
        except Exception as e:
            logger.warning(f"⚠️ Erreur vérification vectorisation {url}: {e}")
            return False
    
    def _remove_existing_chunks(self, url: str):
        """🗑️ Supprimer les chunks existants pour une URL (avant re-vectorisation)"""
        try:
            # Note: PGVector ne supporte pas delete par filter directement
            # On devrait implémenter une méthode custom ou utiliser SQL direct
            logger.warning("⚠️ Suppression des chunks existants non implémentée")
            logger.warning("   → Les nouveaux chunks s'ajouteront aux anciens")
        except Exception as e:
            logger.error(f"❌ Erreur suppression chunks {url}: {e}")
    
    def search_vectorized_content(self, query: str, country: str = "", 
                                language: str = "", k: int = 5) -> List[Document]:
        """
        🔍 RECHERCHE VECTORIELLE FILTRÉE : Rechercher dans le contenu vectorisé
        
        Args:
            query: Requête de recherche
            country: Filtrer par pays (optionnel)
            language: Filtrer par langue (optionnel)  
            k: Nombre de résultats
            
        Returns:
            Documents trouvés avec métadonnées
        """
        try:
            # Construire le filtre
            filter_dict = {}
            if country:
                filter_dict["country"] = country
            if language:
                filter_dict["language"] = language
            
            logger.info(f"🔍 Recherche vectorielle: '{query}' (filtre: {filter_dict})")
            
            # Recherche avec filtre
            if filter_dict:
                results = self.vector_store.similarity_search(
                    query=query,
                    k=k,
                    filter=filter_dict
                )
            else:
                results = self.vector_store.similarity_search(query=query, k=k)
            
            logger.info(f"📚 {len(results)} résultats trouvés")
            return results
            
        except Exception as e:
            logger.error(f"❌ Erreur recherche vectorielle: {e}")
            return []
    
    def get_collection_stats(self) -> Dict[str, any]:
        """📊 Statistiques de la collection vectorisée"""
        try:
            # Recherche dummy pour obtenir des stats
            all_results = self.vector_store.similarity_search("test", k=100)
            
            # Analyser les métadonnées
            countries = set()
            languages = set()
            organizations = set()
            
            for doc in all_results:
                meta = doc.metadata
                if meta.get("country"):
                    countries.add(meta["country"])
                if meta.get("language"):
                    languages.add(meta["language"])
                if meta.get("organization"):
                    organizations.add(meta["organization"])
            
            return {
                "total_chunks": len(all_results),
                "countries": sorted(list(countries)),
                "languages": sorted(list(languages)),
                "organizations": sorted(list(organizations)),
                "collection_name": self.collection_name
            }
            
        except Exception as e:
            logger.error(f"❌ Erreur stats collection: {e}")
            return {"error": str(e)}


def vectorize_all_scraped_content(db_url: str, scraped_data_dir: str = "scraped_data") -> Dict[str, int]:
    """
    🚀 FONCTION UTILITAIRE : Vectoriser tout le contenu scrapé
    
    Args:
        db_url: URL de connexion PostgreSQL
        scraped_data_dir: Dossier contenant les données scrapées
        
    Returns:
        Statistiques de vectorisation
    """
    vectorizer = ScrapedContentVectorizer(db_url)
    bulk_scraper = BulkScraper(storage_dir=scraped_data_dir)
    
    # Charger tous les contenus scrapés
    scraped_index = bulk_scraper.scraper.list_scraped_data()
    
    stats = {"success": 0, "failed": 0, "total": len(scraped_index)}
    
    logger.info(f"🚀 Début vectorisation: {stats['total']} contenus")
    
    for url, info in scraped_index.items():
        logger.info(f"🧠 Vectorisation: {info['organization']}")
        
        try:
            # Charger le contenu scrapé
            scraped_content = bulk_scraper.scraper.load_scraped_content(url)
            
            if scraped_content:
                success = vectorizer.vectorize_scraped_content(scraped_content)
                if success:
                    stats["success"] += 1
                else:
                    stats["failed"] += 1
            else:
                stats["failed"] += 1
                logger.error(f"❌ Impossible de charger: {url}")
                
        except Exception as e:
            stats["failed"] += 1
            logger.error(f"❌ Erreur vectorisation {url}: {e}")
    
    logger.info(f"🏁 Vectorisation terminée: {stats}")
    return stats


def test_vectorization():
    """🧪 Test de la vectorisation avec les données existantes"""
    print("🧪 Test de la vectorisation du contenu scrapé")
    
    # Configuration (à adapter selon ton environnement)
    db_url = "postgresql://user:password@localhost:5432/dbname"  # À remplacer
    
    try:
        # Tester avec les données existantes
        vectorizer = ScrapedContentVectorizer(db_url)
        
        # Charger un contenu scrapé existant
        bulk_scraper = BulkScraper()
        scraped_data = bulk_scraper.scraper.list_scraped_data()
        
        if scraped_data:
            url = list(scraped_data.keys())[0]
            content = bulk_scraper.scraper.load_scraped_content(url)
            
            if content:
                print(f"📄 Test avec: {content.title}")
                print(f"🌍 Pays: {content.metadata.get('country', 'N/A')}")
                print(f"🗣️ Langue: {content.metadata.get('language', 'N/A')}")
                
                # Test du chunking
                chunks = vectorizer._create_chunks_from_scraped_content(content)
                print(f"✂️ {len(chunks)} chunks créés")
                
                # Afficher le premier chunk
                if chunks:
                    print(f"\n📋 Premier chunk:")
                    print(f"Contenu: {chunks[0].page_content[:200]}...")
                    print(f"Métadonnées: {chunks[0].metadata}")
                
            else:
                print("❌ Impossible de charger le contenu")
        else:
            print("❌ Aucune donnée scrapée trouvée")
            
    except Exception as e:
        print(f"❌ Erreur test: {e}")


if __name__ == "__main__":
    test_vectorization()