"""
Configuration Manager - Gestion dynamique de la configuration pays/langues
Remplace la configuration hardcodée dans constants.py par un système persistant JSON
"""
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
from pydantic import BaseModel, Field, validator

logger = logging.getLogger(__name__)

# === MODELS PYDANTIC ===

class CountryConfig(BaseModel):
    """Configuration d'un pays"""
    country_name: str = Field(..., description="Nom du pays")
    country_code: str = Field(..., min_length=2, max_length=3, description="Code ISO du pays (FR, GB, US, etc.)")
    flag: str = Field(..., description="Emoji drapeau du pays")
    organizations_count: int = Field(0, ge=0, description="Nombre d'organisations ciblées")

    class Config:
        json_schema_extra = {
            "example": {
                "country_name": "France",
                "country_code": "FR",
                "flag": "🇫🇷",
                "organizations_count": 15
            }
        }


class LanguageConfig(BaseModel):
    """Configuration d'une langue"""
    name: str = Field(..., description="Nom de la langue")
    code: str = Field(..., min_length=2, max_length=2, description="Code ISO de la langue (FR, EN, etc.)")
    search_terms: List[str] = Field(default=[], description="Termes de recherche dans cette langue")
    countries: List[CountryConfig] = Field(..., min_items=0, max_items=10, description="Pays supportés (max 10)")

    @validator('countries')
    def validate_max_countries(cls, v):
        """Valide qu'il y a maximum 10 pays par langue"""
        if len(v) > 10:
            raise ValueError("Maximum 10 pays autorisés par langue")
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Français",
                "code": "FR",
                "countries": [
                    {
                        "country_name": "France",
                        "country_code": "FR",
                        "flag": "🇫🇷",
                        "search_terms": ["cyberviolence", "cyberharcèlement"],
                        "search_terms_count": 2,
                        "organizations_count": 15
                    }
                ]
            }
        }


class ConfigData(BaseModel):
    """Structure complète de la configuration"""
    version: str = Field("1.0.0", description="Version de la configuration")
    last_updated: str = Field(default_factory=lambda: datetime.utcnow().isoformat() + "Z", description="Date de dernière mise à jour (ISO 8601)")
    languages: Dict[str, LanguageConfig] = Field(..., description="Configuration des langues et pays")

    class Config:
        json_schema_extra = {
            "example": {
                "version": "1.0.0",
                "last_updated": "2026-02-13T12:00:00Z",
                "languages": {
                    "FR": {
                        "name": "Français",
                        "code": "FR",
                        "countries": []
                    }
                }
            }
        }


# === CONFIG MANAGER ===

class ConfigManager:
    """
    Gestionnaire de configuration pays/langues avec persistance JSON
    Pattern Singleton pour accès global
    """
    
    _instance = None
    _config_path = Path("config.json")
    
    def __new__(cls):
        """Singleton pattern"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """Initialisation - chargement config depuis JSON"""
        if self._initialized:
            return
            
        self._config: Optional[ConfigData] = None
        self._load_config()
        self._initialized = True
        logger.info(f"ConfigManager initialisé avec {len(self._config.languages)} langues")
    
    def _load_config(self):
        """Charge la configuration depuis config.json"""
        try:
            if not self._config_path.exists():
                logger.warning("config.json non trouvé - création config par défaut")
                self._create_default_config()
                return
            
            with open(self._config_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self._config = ConfigData(**data)
            logger.info(f"Configuration chargée: {len(self._config.languages)} langues")
            
        except Exception as e:
            logger.error(f"Erreur chargement config: {e}")
            self._create_default_config()
    
    def _create_default_config(self):
        """Crée une configuration par défaut si config.json n'existe pas"""
        self._config = ConfigData(
            version="1.0.0",
            last_updated=datetime.utcnow().isoformat() + "Z",
            languages={}
        )
        self._save_config()
        logger.info("Configuration par défaut créée")
    
    def _save_config(self):
        """Sauvegarde la configuration dans config.json"""
        try:
            self._config.last_updated = datetime.utcnow().isoformat() + "Z"
            
            with open(self._config_path, 'w', encoding='utf-8') as f:
                json.dump(
                    self._config.model_dump(),
                    f,
                    indent=2,
                    ensure_ascii=False
                )
            
            logger.info("Configuration sauvegardée dans config.json")
            
        except Exception as e:
            logger.error(f"Erreur sauvegarde config: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"Impossible de sauvegarder la configuration: {str(e)}"
            )
    
    # === MÉTHODES CRUD ===
    
    def get_all_languages(self) -> Dict[str, LanguageConfig]:
        """Récupère toutes les langues configurées"""
        return self._config.languages
    
    def get_language(self, language_code: str) -> Optional[LanguageConfig]:
        """Récupère la configuration d'une langue spécifique"""
        return self._config.languages.get(language_code.upper())
    
    def get_countries_for_language(self, language_code: str) -> List[CountryConfig]:
        """Récupère la liste des pays pour une langue"""
        lang = self.get_language(language_code)
        return lang.countries if lang else []
    
    def update_language(self, language_code: str, language_config: LanguageConfig):
        """Met à jour ou crée la configuration d'une langue"""
        try:
            # Validation max 10 pays
            if len(language_config.countries) > 10:
                raise ValueError("Maximum 10 pays autorisés par langue")
            
            # Mise à jour
            self._config.languages[language_code.upper()] = language_config
            self._save_config()
            
            logger.info(f"Langue {language_code} mise à jour avec {len(language_config.countries)} pays")
            return True
            
        except Exception as e:
            logger.error(f"Erreur mise à jour langue {language_code}: {e}")
            raise
    
    def add_country_to_language(self, language_code: str, country: CountryConfig) -> bool:
        """Ajoute un pays à une langue"""
        try:
            lang = self.get_language(language_code)
            
            if not lang:
                # Crée nouvelle langue si n'existe pas
                lang = LanguageConfig(
                    name=language_code,
                    code=language_code.upper(),
                    countries=[]
                )
            
            # Vérifie max 10 pays
            if len(lang.countries) >= 10:
                raise ValueError(f"Maximum 10 pays atteints pour la langue {language_code}")
            
            # Vérifie doublon country_code
            if any(c.country_code == country.country_code for c in lang.countries):
                raise ValueError(f"Pays {country.country_code} déjà présent pour {language_code}")
            
            # Ajoute pays
            lang.countries.append(country)
            self.update_language(language_code, lang)
            
            logger.info(f"Pays {country.country_code} ajouté à {language_code}")
            return True
            
        except Exception as e:
            logger.error(f"Erreur ajout pays: {e}")
            raise
    
    def remove_country_from_language(self, language_code: str, country_code: str) -> bool:
        """Supprime un pays d'une langue"""
        try:
            lang = self.get_language(language_code)
            
            if not lang:
                raise ValueError(f"Langue {language_code} non trouvée")
            
            # Filtre pays à supprimer
            initial_count = len(lang.countries)
            lang.countries = [c for c in lang.countries if c.country_code != country_code.upper()]
            
            if len(lang.countries) == initial_count:
                raise ValueError(f"Pays {country_code} non trouvé pour {language_code}")
            
            self.update_language(language_code, lang)
            
            logger.info(f"Pays {country_code} supprimé de {language_code}")
            return True
            
        except Exception as e:
            logger.error(f"Erreur suppression pays: {e}")
            raise
    
    def delete_language(self, language_code: str) -> bool:
        """Supprime une langue complète"""
        try:
            if language_code.upper() not in self._config.languages:
                raise ValueError(f"Langue {language_code} non trouvée")
            
            del self._config.languages[language_code.upper()]
            self._save_config()
            
            logger.info(f"Langue {language_code} supprimée")
            return True
            
        except Exception as e:
            logger.error(f"Erreur suppression langue: {e}")
            raise
    
    def get_stats(self) -> Dict:
        """Statistiques configuration"""
        total_countries = sum(len(lang.countries) for lang in self._config.languages.values())
        
        return {
            "version": self._config.version,
            "last_updated": self._config.last_updated,
            "total_languages": len(self._config.languages),
            "total_countries": total_countries,
            "languages": {
                code: {
                    "name": lang.name,
                    "countries_count": len(lang.countries),
                    "countries": [c.country_code for c in lang.countries]
                }
                for code, lang in self._config.languages.items()
            }
        }


# === SINGLETON GETTER ===

def get_config_manager() -> ConfigManager:
    """Récupère l'instance singleton du ConfigManager"""
    return ConfigManager()


# === EXCEPTION HANDLING ===

from fastapi import HTTPException

def handle_config_error(e: Exception, operation: str) -> HTTPException:
    """Gère les erreurs de configuration et retourne une HTTPException"""
    if isinstance(e, ValueError):
        return HTTPException(status_code=400, detail=str(e))
    else:
        logger.error(f"Erreur {operation}: {e}")
        return HTTPException(status_code=500, detail=f"Erreur serveur: {str(e)}")
