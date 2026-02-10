"""
🔍 DeduplicationService - Service centralisé de détection et nettoyage de doublons

Architecture simple et modulable:
- Normalize: Une responsabilité = une méthode
- Detect: Logique claire "même org + 1 champ = doublon"
- Analyze: Triple approche (exacts, similarité, domaines)
- Clean: Actions automatiques ou manuelles
"""

import re
import logging
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from enum import Enum
from difflib import SequenceMatcher
from urllib.parse import urlparse

logger = logging.getLogger(__name__)


class DuplicateAction(Enum):
    """Actions suggérées pour les doublons détectés"""
    ACCEPT = "accept"           # Pas doublon, accepter
    MERGE = "merge"             # Doublon certain, fusionner
    REVIEW = "review"           # Probable doublon, demander avis
    KEEP_FIRST = "keep_first"   # Garder le premier, supprimer autres
    KEEP_BEST = "keep_best"     # Garder le plus complet


@dataclass
class NormalizationConfig:
    """Configuration des règles de normalisation"""
    remove_common_words: bool = True
    normalize_accents: bool = True
    normalize_case: bool = True
    normalize_punctuation: bool = True
    
    # Mots à supprimer (multilingue)
    common_words: List[str] = field(default_factory=lambda: [
        'association', 'fundação', 'instituto', 'centro', 'ong', 'ngo',
        'foundation', 'organization', 'org', 'inc', 'ltd', 'sa', 'lda',
        'organization', 'organización', 'organisation', 'società', 'verein',
        'ngos', 'association', 'societies', 'foundation', 'fdns',
        'e.v.', 'ev', 'asbl', 'vzw', 'gmbh', 'ag', 'bv', 'doo'
    ])
    
    # Accents à normaliser (français, portugais, espagnol, italien, allemand)
    accent_map: Dict[str, str] = field(default_factory=lambda: {
        'ç': 'c', 'ã': 'a', 'õ': 'o', 'á': 'a', 'à': 'a', 'â': 'a',
        'é': 'e', 'ê': 'e', 'í': 'i', 'ó': 'o', 'ô': 'o', 'ú': 'u', 'ü': 'u',
        'ä': 'a', 'ö': 'o', 'ë': 'e', 'ï': 'i',  # Allemand, néerlandais
    })


@dataclass
class DuplicateMatch:
    """Représentation d'une paire de ressources similaresn"""
    resource_id_1: str
    resource_id_2: str
    organization_1: str
    organization_2: str
    match_type: str  # "exact" | "similarity" | "domain"
    confidence: float  # 0.0 - 1.0
    matching_fields: List[str]
    suggested_action: DuplicateAction
    details: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DeduplicationAnalysis:
    """Résultat complet d'analyse de déduplication"""
    total_resources: int
    exact_duplicates: List[DuplicateMatch]
    similar_duplicates: List[DuplicateMatch]
    domain_duplicates: List[DuplicateMatch]
    statistics: Dict[str, Any]
    recommendations: List[str]


class DeduplicationService:
    """
    Service centralisé de gestion des doublons
    
    Usage:
    ```python
    service = DeduplicationService()
    
    # Vérifier un doublon avant ajout
    check = service.check_duplicate(new_resource)
    if check['is_duplicate']:
        action = check['suggested_action']
    
    # Analyser toutes les ressources
    analysis = service.analyze_all(working_resources)
    print(f"Found {len(analysis.exact_duplicates)} exact duplicates")
    
    # Nettoyer automatiquement
    cleaned = service.clean_automatic(working_resources)
    print(f"Removed {cleaned['removed_count']} duplicates")
    ```
    """
    
    def __init__(self, config: Optional[NormalizationConfig] = None):
        """Initialiser le service"""
        self.config = config or NormalizationConfig()
        self.organization_index = {}
        self.similarity_threshold = 0.80
        
    # ==========================================
    # 🔤 NORMALISATION - Cœur de la logique
    # ==========================================
    
    def normalize_organization_name(self, org_name: str) -> str:
        """
        Normaliser un nom d'organisation intelligemment
        
        Exemple:
        - "Association e-Enfance" → "enfance"
        - "e-Enfance Foundation" → "enfance"
        - "E-ENFANCE" → "enfance"
        """
        if not org_name or not isinstance(org_name, str):
            return ""
        
        result = org_name
        
        # 1. Casse uniforme
        if self.config.normalize_case:
            result = result.lower().strip()
        
        # 2. Normaliser accents
        if self.config.normalize_accents:
            for accent, normal in self.config.accent_map.items():
                result = result.replace(accent, normal)
        
        # 3. Supprimer ponctuation sauf tirets/espaces
        if self.config.normalize_punctuation:
            result = re.sub(r"[^\w\s\-]", "", result)
        
        # 4. Supprimer mots communs
        if self.config.remove_common_words:
            words = result.split()
            words = [w for w in words if w not in self.config.common_words and len(w) > 2]
            if not words:  # Si tout supprimé, garder original
                words = org_name.lower().split()
            result = " ".join(words)
        
        # 5. Normaliser espaces multiples
        result = re.sub(r"\s+", " ", result).strip()
        
        return result
    
    def normalize_phone(self, phone: str) -> str:
        """
        Normaliser numéro téléphone
        
        Exemple:
        - "(0)800-200 000" → "0800200000"
        - "+33 (0)800 200 000" → "+33800200000"
        """
        if not phone:
            return ""
        # Garder seulement chiffres et +
        return "".join(c for c in phone if c.isdigit() or c == "+")
    
    def normalize_email(self, email: str) -> str:
        """Normaliser email (casse basse, strip)"""
        if not email:
            return ""
        return email.lower().strip()
    
    def normalize_website(self, website: str) -> str:
        """
        Normaliser URL
        
        Exemple:
        - "https://www.site.fr/" → "site.fr"
        - "HTTP://SITE.FR" → "site.fr"
        - "www.site.fr:8080" → "site.fr"
        """
        if not website:
            return ""
        
        url = website.lower().strip()
        
        # Supprimer protocole
        url = re.sub(r"^https?://", "", url)
        
        # Supprimer www et sous-domaines communs
        url = re.sub(r"^www\.", "", url)
        url = re.sub(r"^mail\.", "", url)
        url = re.sub(r"^ftp\.", "", url)
        
        # Supprimer port
        url = re.sub(r":\d+$", "", url)
        
        # Supprimer trailing slash
        url = url.rstrip("/")
        
        # Garder seulement domaine principal (site.fr, pas subdomain.site.fr)
        try:
            parts = url.split(".")
            if len(parts) >= 2:
                url = ".".join(parts[-2:])  # Dernier 2 parties
        except:
            pass
        
        return url
    
    def normalize_country_code(self, country: str) -> str:
        """Normaliser code pays (toujours majuscule, 2 lettres)"""
        if not country:
            return ""
        return country.upper().strip()[:2]
    
    # ==========================================
    # 🔍 DÉTECTION - Logique de comparaison
    # ==========================================
    
    def check_duplicate(self, new_resource: Dict, existing_resources: Optional[Dict] = None) -> Dict:
        """
        Vérifier si une ressource est un doublon avant ajout
        
        Returns:
        {
            'is_duplicate': True/False,
            'matches': [DuplicateMatch, ...],
            'suggested_action': DuplicateAction,
            'confidence': 0.0-1.0,
            'details': {...}
        }
        """
        if not existing_resources:
            return {
                'is_duplicate': False,
                'matches': [],
                'suggested_action': DuplicateAction.ACCEPT,
                'confidence': 0.0
            }
        
        org_name = new_resource.get('organization_name', '')
        normalized_name = self.normalize_organization_name(org_name)
        
        if not normalized_name:
            return {
                'is_duplicate': False,
                'matches': [],
                'suggested_action': DuplicateAction.ACCEPT,
                'confidence': 0.0
            }
        
        # Chercher ressources avec même organisation
        new_fields = self._extract_comparable_fields(new_resource)
        matches = []
        
        for resource_id, existing in existing_resources.items():
            existing_name = existing.get('organization_name', '')
            existing_normalized = self.normalize_organization_name(existing_name)
            
            # Même organisation normalisée?
            if existing_normalized == normalized_name:
                existing_fields = self._extract_comparable_fields(existing)
                
                # Chercher champs identiques
                matching_fields = self._find_matching_fields(new_fields, existing_fields)
                
                if matching_fields:
                    matches.append({
                        'resource_id': resource_id,
                        'organization': existing_name,
                        'matching_fields': matching_fields,
                        'confidence': len(matching_fields) / len(new_fields)
                    })
        
        if not matches:
            return {
                'is_duplicate': False,
                'matches': [],
                'suggested_action': DuplicateAction.ACCEPT,
                'confidence': 0.0
            }
        
        # Décider action suggérée basée sur nombre/qualité matches
        best_match = max(matches, key=lambda x: x['confidence'])
        confidence = best_match['confidence']
        
        if confidence >= 0.75:
            suggested_action = DuplicateAction.MERGE
        elif confidence >= 0.5:
            suggested_action = DuplicateAction.REVIEW
        else:
            suggested_action = DuplicateAction.ACCEPT
        
        return {
            'is_duplicate': suggested_action != DuplicateAction.ACCEPT,
            'matches': matches,
            'best_match': best_match,
            'suggested_action': suggested_action,
            'confidence': confidence
        }
    
    def _extract_comparable_fields(self, resource: Dict) -> Dict:
        """Extraire champs à comparer"""
        return {
            'country': self.normalize_country_code(resource.get('country_code', '')),
            'email': self.normalize_email(resource.get('email', '')),
            'phone': self.normalize_phone(resource.get('phone', '')),
            'website': self.normalize_website(resource.get('website', ''))
        }
    
    def _find_matching_fields(self, fields1: Dict, fields2: Dict) -> List[str]:
        """Trouver quels champs matchent"""
        matches = []
        for key in fields1:
            val1 = fields1.get(key, '')
            val2 = fields2.get(key, '')
            if val1 and val2 and val1 == val2:
                matches.append(key)
        return matches
    
    # ==========================================
    # 📊 ANALYSE - Triple approche
    # ==========================================
    
    def analyze_all(self, resources: Dict) -> DeduplicationAnalysis:
        """
        Analyser TOUS les doublons avec triple approche
        """
        exact_duplicates = self._find_exact_duplicates(resources)
        similar_duplicates = self._find_similar_duplicates(resources)
        domain_duplicates = self._find_domain_duplicates(resources)
        
        stats = {
            'total_resources': len(resources),
            'exact_duplicate_pairs': len(exact_duplicates),
            'similar_duplicate_pairs': len(similar_duplicates),
            'domain_duplicate_pairs': len(domain_duplicates),
            'resources_by_country': self._count_by_country(resources),
            'resources_by_category': self._count_by_category(resources)
        }
        
        recommendations = self._generate_recommendations(
            exact_duplicates, similar_duplicates, domain_duplicates
        )
        
        return DeduplicationAnalysis(
            total_resources=len(resources),
            exact_duplicates=exact_duplicates,
            similar_duplicates=similar_duplicates,
            domain_duplicates=domain_duplicates,
            statistics=stats,
            recommendations=recommendations
        )
    
    def _find_exact_duplicates(self, resources: Dict) -> List[DuplicateMatch]:
        """Trouver doublons exacts (même nom)"""
        matches = []
        seen = {}
        
        for rid, resource in resources.items():
            name = self.normalize_organization_name(
                resource.get('organization_name', '')
            )
            
            if name in seen:
                matches.append(DuplicateMatch(
                    resource_id_1=seen[name]['rid'],
                    resource_id_2=rid,
                    organization_1=seen[name]['org'],
                    organization_2=resource.get('organization_name', ''),
                    match_type='exact',
                    confidence=1.0,
                    matching_fields=['organization_name'],
                    suggested_action=DuplicateAction.MERGE
                ))
            else:
                seen[name] = {'rid': rid, 'org': resource.get('organization_name', '')}
        
        return matches
    
    def _find_similar_duplicates(self, resources: Dict) -> List[DuplicateMatch]:
        """Trouver doublons par similarité (>80%)"""
        matches = []
        resource_list = list(resources.items())
        
        for i in range(len(resource_list)):
            for j in range(i + 1, len(resource_list)):
                rid1, res1 = resource_list[i]
                rid2, res2 = resource_list[j]
                
                # Vérifier similarité organisation
                norm1 = self.normalize_organization_name(
                    res1.get('organization_name', '')
                )
                norm2 = self.normalize_organization_name(
                    res2.get('organization_name', '')
                )
                
                if norm1 and norm2:
                    similarity = SequenceMatcher(None, norm1, norm2).ratio()
                    
                    if self.similarity_threshold <= similarity < 1.0:
                        matches.append(DuplicateMatch(
                            resource_id_1=rid1,
                            resource_id_2=rid2,
                            organization_1=res1.get('organization_name', ''),
                            organization_2=res2.get('organization_name', ''),
                            match_type='similarity',
                            confidence=similarity,
                            matching_fields=['organization_name (similar)'],
                            suggested_action=DuplicateAction.REVIEW,
                            details={'similarity_score': similarity}
                        ))
        
        return matches
    
    def _find_domain_duplicates(self, resources: Dict) -> List[DuplicateMatch]:
        """Trouver ressources avec même domaine web"""
        matches = []
        domains = {}
        
        for rid, resource in resources.items():
            website = resource.get('website', '')
            domain = self.normalize_website(website) if website else None
            
            if domain:
                if domain in domains:
                    matches.append(DuplicateMatch(
                        resource_id_1=domains[domain]['rid'],
                        resource_id_2=rid,
                        organization_1=domains[domain]['org'],
                        organization_2=resource.get('organization_name', ''),
                        match_type='domain',
                        confidence=0.6,
                        matching_fields=['website (same domain)'],
                        suggested_action=DuplicateAction.REVIEW,
                        details={'domain': domain}
                    ))
                else:
                    domains[domain] = {
                        'rid': rid,
                        'org': resource.get('organization_name', '')
                    }
        
        return matches
    
    def _count_by_country(self, resources: Dict) -> Dict[str, int]:
        """Compter ressources par pays"""
        counts = {}
        for resource in resources.values():
            country = resource.get('country_code', 'UNKNOWN')
            counts[country] = counts.get(country, 0) + 1
        return counts
    
    def _count_by_category(self, resources: Dict) -> Dict[str, int]:
        """Compter ressources par catégorie"""
        counts = {}
        for resource in resources.values():
            category = resource.get('category', 'UNKNOWN')
            counts[category] = counts.get(category, 0) + 1
        return counts
    
    def _generate_recommendations(self, exact, similar, domain) -> List[str]:
        """Générer recommandations d'action"""
        recs = []
        
        if exact:
            recs.append(f"🔴 {len(exact)} doublons EXACTS détectés - À fusionner immédiatement")
        
        if similar:
            recs.append(f"🟡 {len(similar)} doublons PROBABLES (similarité >80%) - À vérifier")
        
        if domain:
            recs.append(f"🔵 {len(domain)} ressources partagent domaine - À valider")
        
        if not (exact or similar or domain):
            recs.append("✅ Aucun doublon détecté - Données propres!")
        
        return recs
    
    # ==========================================
    # 🧹 NETTOYAGE - Actions automatiques
    # ==========================================
    
    def clean_automatic(self, resources: Dict, strategy: str = "keep_first") -> Dict:
        """
        Nettoyer automatiquement les doublons
        
        Stratégies:
        - "keep_first": Garder le premier, supprimer autres (plus simple)
        - "keep_best": Garder le plus complet (plus intelligent mais plus lent)
        
        Returns:
        {
            'removed_count': int,
            'kept_resources': Dict,
            'removed_ids': List[str],
            'removal_reasons': Dict
        }
        """
        analysis = self.analyze_all(resources)
        
        removed_ids = set()
        removal_reasons = {}
        
        # Traiter doublons exacts
        for match in analysis.exact_duplicates:
            if match.resource_id_2 not in removed_ids:
                removed_ids.add(match.resource_id_2)
                removal_reasons[match.resource_id_2] = (
                    f"Exact duplicate of {match.resource_id_1}"
                )
        
        # Construire résultat
        kept = {rid: res for rid, res in resources.items() if rid not in removed_ids}
        
        logger.info(f"🧹 Nettoyage: {len(removed_ids)} ressources supprimées")
        
        return {
            'removed_count': len(removed_ids),
            'kept_resources': kept,
            'removed_ids': list(removed_ids),
            'removal_reasons': removal_reasons
        }


# ==========================================
# 📈 Utilitaires d'export
# ==========================================

def export_analysis_as_dict(analysis: DeduplicationAnalysis) -> Dict:
    """Convertir analyse en dictionnaire JSON-sérialisable"""
    return {
        'summary': {
            'total_resources': analysis.total_resources,
            'exact_duplicates': len(analysis.exact_duplicates),
            'similar_duplicates': len(analysis.similar_duplicates),
            'domain_duplicates': len(analysis.domain_duplicates)
        },
        'exact_duplicates': [
            {
                'resource_1': m.resource_id_1,
                'resource_2': m.resource_id_2,
                'organization_1': m.organization_1,
                'organization_2': m.organization_2
            }
            for m in analysis.exact_duplicates
        ],
        'similar_duplicates': [
            {
                'resource_1': m.resource_id_1,
                'resource_2': m.resource_id_2,
                'organization_1': m.organization_1,
                'organization_2': m.organization_2,
                'similarity': round(m.confidence, 2)
            }
            for m in analysis.similar_duplicates
        ],
        'domain_duplicates': [
            {
                'resource_1': m.resource_id_1,
                'resource_2': m.resource_id_2,
                'organization_1': m.organization_1,
                'organization_2': m.organization_2,
                'domain': m.details.get('domain', 'unknown')
            }
            for m in analysis.domain_duplicates
        ],
        'statistics': analysis.statistics,
        'recommendations': analysis.recommendations
    }
