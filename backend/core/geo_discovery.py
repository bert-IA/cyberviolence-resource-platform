"""
Système de découverte géographique dynamique
Récupère les pays par langue via des APIs externes
"""
import requests
import logging
from typing import List, Dict, Optional
from dataclasses import dataclass
import asyncio
import aiohttp

logger = logging.getLogger(__name__)

@dataclass
class CountryInfo:
    name: str
    code: str
    flag: str
    languages: List[str]
    search_terms: List[str]

class DynamicGeoDiscovery:
    """
    Découverte géographique dynamique basée sur des APIs externes
    """
    
    def __init__(self):
        self.countries_cache = {}
        self.language_terms = {
            "FR": ["cyberviolence", "cyberharcèlement", "harcèlement numérique"],
            "EN": ["cyberbullying", "online harassment", "digital safety"],
            "ES": ["ciberacoso", "violencia digital", "acoso online"],
            "IT": ["cyberbullismo", "violenza digitale", "molestie online"],
            "DE": ["Cybermobbing", "digitale Gewalt", "Online-Belästigung"],
            "PT": ["ciberbullying", "violência digital", "assédio online"]
        }
        
        # Configuration des pays GARANTIS par langue (toujours inclus)
        self.guaranteed_countries = {
            "FR": [
                ("France", "FR"),
                ("Belgique", "BE"), 
                ("Suisse", "CH"),
                ("Canada", "CA"),
                ("Luxembourg", "LU")
            ],
            "EN": [
                ("United Kingdom", "GB"),
                ("United States", "US"),
                ("Canada", "CA"),
                ("Australia", "AU"),
                ("Ireland", "IE"),
                ("New Zealand", "NZ")
            ],
            "ES": [
                ("Spain", "ES"),
                ("Mexico", "MX"),
                ("Argentina", "AR"),
                ("Colombia", "CO"),
                ("Chile", "CL"),
                ("Peru", "PE")
            ],
            "IT": [
                ("Italy", "IT"),
                ("Switzerland", "CH"),
                ("San Marino", "SM"),
                ("Vatican City", "VA")
            ],
            "DE": [
                ("Germany", "DE"),
                ("Austria", "AT"),
                ("Switzerland", "CH"),
                ("Luxembourg", "LU"),
                ("Liechtenstein", "LI")
            ],
            "PT": [
                ("Portugal", "PT"),
                ("Brazil", "BR"),
                ("Angola", "AO"),
                ("Mozambique", "MZ"),
                ("Cape Verde", "CV")
            ]
        }
    
    async def get_countries_by_language(self, language: str, max_countries: int = 10) -> List[CountryInfo]:
        """
        Récupère dynamiquement les pays qui parlent une langue donnée
        """
        try:
            # Vérifier le cache
            cache_key = f"{language}_{max_countries}"
            if cache_key in self.countries_cache:
                logger.info(f"Cache hit pour {language}")
                return self.countries_cache[cache_key]
            
            # Récupérer via API
            countries = await self._fetch_countries_from_api(language, max_countries)
            
            # Mettre en cache
            self.countries_cache[cache_key] = countries
            
            return countries
            
        except Exception as e:
            logger.error(f"Erreur get_countries_by_language {language}: {e}")
            # Fallback vers configuration statique
            return self._get_static_fallback(language, max_countries)
    
    async def _fetch_countries_from_api(self, language: str, max_countries: int) -> List[CountryInfo]:
        """
        APPROCHE HYBRIDE : Pays garantis + découverte API
        """
        countries = []
        search_terms = self.language_terms.get(language, [])
        used_codes = set()
        
        # ÉTAPE 1 : Ajouter les pays GARANTIS pour cette langue
        guaranteed = self.guaranteed_countries.get(language, [])
        for name, code in guaranteed:
            countries.append(CountryInfo(
                name=name,
                code=code, 
                flag="🌍",
                languages=[language.lower()],
                search_terms=search_terms
            ))
            used_codes.add(code)
        
        logger.info(f"Pays garantis pour {language}: {len(guaranteed)}")
        
        # ÉTAPE 2 : Compléter avec l'API REST Countries (si on a de la place)
        remaining_slots = max_countries - len(countries)
        if remaining_slots > 0:
            try:
                api_countries = await self._fetch_from_rest_countries_api(language, remaining_slots * 2)  # On en récupère plus pour filtrer
                
                # Ajouter les pays de l'API qui ne sont pas déjà dans les garantis
                for country in api_countries:
                    if country.code not in used_codes and len(countries) < max_countries:
                        countries.append(country)
                        used_codes.add(country.code)
                
                logger.info(f"Ajouté {len(countries) - len(guaranteed)} pays depuis l'API")
                
            except Exception as e:
                logger.warning(f"API REST Countries échouée pour {language}: {e}")
                # Ce n'est pas grave, on a déjà les pays garantis
        
        return countries[:max_countries]
    
    async def _fetch_from_rest_countries_api(self, language: str, max_countries: int) -> List[CountryInfo]:
        """
        Récupère les pays via l'API REST Countries
        """
        # Mapping des codes de langue
        lang_mapping = {
            "FR": "french",
            "EN": "english", 
            "ES": "spanish",
            "IT": "italian",
            "DE": "german",
            "PT": "portuguese"
        }
        
        lang_name = lang_mapping.get(language)
        if not lang_name:
            raise ValueError(f"Langue non supportée: {language}")
        
        url = f"https://restcountries.com/v3.1/lang/{lang_name}"
        search_terms = self.language_terms.get(language, [])
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status != 200:
                    raise Exception(f"API Error: {response.status}")
                
                data = await response.json()
                
                countries = []
                for country_data in data[:max_countries]:
                    name = country_data.get("name", {}).get("common", "Unknown")
                    code = country_data.get("cca2", "XX")
                    flag = country_data.get("flag", "🌍")
                    
                    countries.append(CountryInfo(
                        name=name,
                        code=code,
                        flag=flag,
                        languages=[lang_name],
                        search_terms=search_terms
                    ))
                
                return countries
                
                # Filtrer et convertir
                for country_data in data[:max_countries]:
                    try:
                        country = CountryInfo(
                            name=country_data.get("name", {}).get("common", "Unknown"),
                            code=country_data.get("cca2", "XX"),
                            flag=country_data.get("flag", "🏳️"),
                            languages=list(country_data.get("languages", {}).values()),
                            search_terms=search_terms
                        )
                        countries.append(country)
                    except Exception as e:
                        logger.warning(f"Erreur parsing pays: {e}")
                        continue
                
                return countries
    
    def _get_static_fallback(self, language: str, max_countries: int) -> List[CountryInfo]:
        """
        Configuration statique en cas d'échec de l'API
        """
        static_config = {
            "FR": [
                CountryInfo("France", "FR", "🇫🇷", ["french"], self.language_terms["FR"]),
                CountryInfo("Belgique", "BE", "🇧🇪", ["french"], self.language_terms["FR"]),
                CountryInfo("Suisse", "CH", "🇨🇭", ["french"], self.language_terms["FR"]),
                CountryInfo("Canada", "CA", "🇨🇦", ["french", "english"], self.language_terms["FR"]),
                CountryInfo("Luxembourg", "LU", "🇱🇺", ["french"], self.language_terms["FR"])
            ],
            "EN": [
                CountryInfo("United Kingdom", "GB", "🇬🇧", ["english"], self.language_terms["EN"]),
                CountryInfo("United States", "US", "🇺🇸", ["english"], self.language_terms["EN"]),
                CountryInfo("Canada", "CA", "🇨🇦", ["english", "french"], self.language_terms["EN"]),
                CountryInfo("Australia", "AU", "🇦🇺", ["english"], self.language_terms["EN"]),
                CountryInfo("Ireland", "IE", "🇮🇪", ["english"], self.language_terms["EN"])
            ],
            "IT": [
                CountryInfo("Italia", "IT", "🇮🇹", ["italian"], self.language_terms["IT"]),
                CountryInfo("Svizzera", "CH", "🇨🇭", ["italian"], self.language_terms["IT"]),
                CountryInfo("San Marino", "SM", "🇸🇲", ["italian"], self.language_terms["IT"]),
                CountryInfo("Vaticano", "VA", "🇻🇦", ["italian"], self.language_terms["IT"])
            ],
            "ES": [
                CountryInfo("España", "ES", "🇪🇸", ["spanish"], self.language_terms["ES"]),
                CountryInfo("México", "MX", "🇲🇽", ["spanish"], self.language_terms["ES"]),
                CountryInfo("Argentina", "AR", "🇦🇷", ["spanish"], self.language_terms["ES"]),
                CountryInfo("Colombia", "CO", "🇨🇴", ["spanish"], self.language_terms["ES"]),
                CountryInfo("Chile", "CL", "🇨🇱", ["spanish"], self.language_terms["ES"])
            ],
            "DE": [
                CountryInfo("Deutschland", "DE", "🇩🇪", ["german"], self.language_terms["DE"]),
                CountryInfo("Österreich", "AT", "🇦🇹", ["german"], self.language_terms["DE"]),
                CountryInfo("Schweiz", "CH", "🇨🇭", ["german"], self.language_terms["DE"])
            ],
            "PT": [
                CountryInfo("Portugal", "PT", "🇵🇹", ["portuguese"], self.language_terms["PT"]),
                CountryInfo("Brasil", "BR", "🇧🇷", ["portuguese"], self.language_terms["PT"])
            ]
        }
        
        return static_config.get(language, [])[:max_countries]
    
    async def refresh_cache(self):
        """Vide le cache pour forcer une mise à jour"""
        self.countries_cache.clear()
        logger.info("Cache géographique vidé")

# Instance globale
geo_discovery = DynamicGeoDiscovery()

async def get_countries_for_language(language: str, max_countries: int = 10) -> List[Dict]:
    """
    Interface compatible avec l'existant
    """
    countries = await geo_discovery.get_countries_by_language(language, max_countries)
    
    # Convertir en format compatible
    return [
        {
            "name": country.name,
            "code": country.code,
            "search_terms": country.search_terms
        }
        for country in countries
    ]