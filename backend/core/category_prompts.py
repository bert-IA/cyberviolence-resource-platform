"""
Prompts LLM spécialisés par catégorie de ressource
Implémentation de la stratégie lean selon logic_sourcing_ressources.md
"""

from typing import Dict, Callable


class CategoryPrompts:
    """Générateur de prompts spécialisés par catégorie et langue"""
    
    @staticmethod
    def generate_prompt(category: str, country: str, language: str, **kwargs) -> str:
        """
        Génère un prompt spécialisé selon la catégorie
        
        Args:
            category: Type de ressource (contact_urgence, procedure_plateforme, etc.)
            country: Pays cible
            language: Langue du prompt (FR, EN, ES, IT, DE, PT)
            **kwargs: Paramètres spécialisés (platform_name pour procedure_plateforme, etc.)
        """
        
        prompt_generators = {
            "contact_urgence": CategoryPrompts._prompt_contact_urgence,
            "procedure_plateforme": CategoryPrompts._prompt_procedure_plateforme,
            "signalement_autorite": CategoryPrompts._prompt_signalement_autorite,
            "association_locale": CategoryPrompts._prompt_association_locale,
            "services_support": CategoryPrompts._prompt_services_support  # Existant/fallback
        }
        
        if category not in prompt_generators:
            raise ValueError(f"Catégorie non supportée: {category}")
        
        return prompt_generators[category](country, language, **kwargs)
    
    # =================================================================
    # 📞 CONTACT URGENCE - Numéros directs, pas de conseils généraux
    # =================================================================
    
    @staticmethod
    def _prompt_contact_urgence(country: str, language: str, **kwargs) -> str:
        """Prompt pour découverte de contacts d'urgence spécialisés"""
        
        prompts = {
            "FR": f"""Trouve UNIQUEMENT les numéros d'urgence OFFICIELS pour cyberharcèlement en {country}.

CRITÈRES STRICTS:
- Numéros gratuits gouvernementaux ou associations agréées
- Services 24h/7j si possible  
- Spécialisés cyberviolence/cyberharcèlement (PAS généralistes)
- Contact direct, pas site web général
- Évite les associations d'aide générale

SOURCES PRIORITAIRES à vérifier:
- Numéros nationaux courts (3018, 116 xxx)
- Services gouvernementaux spécialisés
- Hotlines cybercriminalité/cyberviolence
- Services jeunesse spécialisés

Réponds UNIQUEMENT sous ce format exact:
Nom: [Service officiel exact]
Numéro: [Numéro gratuit exact] 
Description: [Spécialisation cyberharcèlement en 1-2 phrases]
Horaires: [Disponibilité précise]
Autorité: [Ministère/organisme de tutelle]
URL: [Site officiel si disponible]""",

            "EN": f"""Find ONLY OFFICIAL emergency numbers for cyberbullying in {country}.

STRICT CRITERIA:
- Free government numbers or certified associations
- 24/7 services if possible
- Specialized in cyberviolence/cyberbullying (NOT general help)
- Direct contact, not general website
- Avoid general support associations

PRIORITY SOURCES to check:
- National short numbers (similar to 3018, 116 xxx)
- Specialized government services
- Cybercrime/cyberviolence hotlines
- Specialized youth services

Answer ONLY in this exact format:
Name: [Exact official service]
Number: [Exact free number]
Description: [Cyberbullying specialization in 1-2 sentences]  
Hours: [Precise availability]
Authority: [Ministry/supervising organization]
URL: [Official website if available]""",

            "ES": f"""Encuentra ÚNICAMENTE números de urgencia OFICIALES para ciberacoso en {country}.

CRITERIOS ESTRICTOS:
- Números gratuitos gubernamentales o asociaciones certificadas
- Servicios 24h/7días si es posible
- Especializados en ciberviolencia/ciberacoso (NO generalistas)
- Contacto directo, no sitio web general
- Evita asociaciones de ayuda general

FUENTES PRIORITARIAS a verificar:
- Números nacionales cortos (tipo 3018, 116 xxx)
- Servicios gubernamentales especializados
- Líneas directas cibercrimen/ciberviolencia
- Servicios juveniles especializados

Responde ÚNICAMENTE en este formato exacto:
Nombre: [Servicio oficial exacto]
Número: [Número gratuito exacto]
Descripción: [Especialización ciberacoso en 1-2 frases]
Horarios: [Disponibilidad precisa]
Autoridad: [Ministerio/organismo supervisor]
URL: [Sitio oficial si disponible]""",

            "IT": f"""Trova UNICAMENTE numeri di emergenza UFFICIALI per cyberbullismo in {country}.

CRITERI RIGOROSI:
- Numeri gratuiti governativi o associazioni certificate
- Servizi 24h/7giorni se possibile
- Specializzati in cyberviolenza/cyberbullismo (NON generici)
- Contatto diretto, non sito web generale
- Evita associazioni di aiuto generale

FONTI PRIORITARIE da verificare:
- Numeri nazionali brevi (tipo 3018, 116 xxx)  
- Servizi governativi specializzati
- Hotline cybercrimine/cyberviolenza
- Servizi giovanili specializzati

Rispondi UNICAMENTE in questo formato esatto:
Nome: [Servizio ufficiale esatto]
Numero: [Numero gratuito esatto]
Descrizione: [Specializzazione cyberbullismo in 1-2 frasi]
Orari: [Disponibilità precisa]
Autorità: [Ministero/organismo supervisore]
URL: [Sito ufficiale se disponibile]""",

            "DE": f"""Finde NUR OFFIZIELLE Notfallnummern für Cybermobbing in {country}.

STRENGE KRITERIEN:
- Kostenlose Regierungsnummern oder zertifizierte Vereine
- 24h/7Tage Service wenn möglich
- Spezialisiert auf Cybergewalt/Cybermobbing (NICHT allgemein)
- Direkter Kontakt, nicht allgemeine Website
- Vermeide allgemeine Hilfsvereine

PRIORITÄRE QUELLEN zu prüfen:
- Nationale Kurznummern (wie 3018, 116 xxx)
- Spezialisierte Regierungsdienste
- Cyberkriminalität/Cybergewalt Hotlines
- Spezialisierte Jugenddienste

Antworte NUR in diesem exakten Format:
Name: [Exakter offizieller Service]
Nummer: [Exakte kostenlose Nummer]
Beschreibung: [Cybermobbing-Spezialisierung in 1-2 Sätzen]
Zeiten: [Genaue Verfügbarkeit]
Behörde: [Ministerium/Aufsichtsorgan]
URL: [Offizielle Website falls verfügbar]""",

            "PT": f"""Encontre APENAS números de emergência OFICIAIS para cyberbullying em {country}.

CRITÉRIOS RIGOROSOS:
- Números gratuitos governamentais ou associações certificadas
- Serviços 24h/7dias se possível
- Especializados em cyberviolência/cyberbullying (NÃO generalistas)
- Contacto direto, não site geral
- Evite associações de ajuda geral

FONTES PRIORITÁRIAS a verificar:
- Números nacionais curtos (tipo 3018, 116 xxx)
- Serviços governamentais especializados
- Linhas directas cybercrime/cyberviolência
- Serviços juvenis especializados

Responda APENAS neste formato exacto:
Nome: [Serviço oficial exacto]
Número: [Número gratuito exacto]
Descrição: [Especialização cyberbullying em 1-2 frases]
Horários: [Disponibilidade precisa]
Autoridade: [Ministério/organismo supervisor]
URL: [Site oficial se disponível]"""
        }
        
        return prompts.get(language, prompts["EN"])
    
    # ================================================================
    # 🛠️ PROCEDURE PLATEFORME - Steps exacts de signalement/blocage
    # ================================================================
    
    @staticmethod
    def _prompt_procedure_plateforme(country: str, language: str, **kwargs) -> str:
        """Prompt pour découverte de procédures techniques plateformes"""
        
        platform_name = kwargs.get("platform_name", "toutes plateformes")
        
        prompts = {
            "FR": f"""Trouve les procédures EXACTES de signalement sur {platform_name} mises à jour en 2024/2025.

CRITÈRES STRICTS:
- URLs help center officiels UNIQUEMENT
- Procédures step-by-step récentes (post-2024)
- Pas de conseils généraux ou théoriques
- Screenshots/captures officielles si disponibles
- Spécifique au cyberharcèlement/cyberviolence

SOURCES OFFICIELLES uniquement:
- Help centers/centres d'aide officiels
- Documentation de sécurité des plateformes
- Guides de signalement mis à jour
- Procédures de modération officielles

Réponds UNIQUEMENT sous ce format exact:
Plateforme: [Nom exact de la plateforme]
URL: [Lien help center officiel direct]
Procédure: [Steps 1,2,3... exacts pour signaler cyberharcèlement]
Délai: [Temps de traitement annoncé par la plateforme]
Preuves: [Types de preuves demandées]
Suivi: [Comment suivre le signalement]""",

            "EN": f"""Find EXACT reporting procedures on {platform_name} updated in 2024/2025.

STRICT CRITERIA:
- Official help center URLs ONLY
- Recent step-by-step procedures (post-2024)
- No general advice or theory
- Official screenshots/captures if available
- Specific to cyberbullying/cyberviolence

OFFICIAL SOURCES only:
- Official help centers/support centers
- Platform security documentation
- Updated reporting guides
- Official moderation procedures

Answer ONLY in this exact format:
Platform: [Exact platform name]
URL: [Direct official help center link]
Procedure: [Exact steps 1,2,3... to report cyberbullying]
Timeframe: [Processing time announced by platform]
Evidence: [Types of evidence required]
Follow-up: [How to track the report]""",

            "ES": f"""Encuentra procedimientos EXACTOS de denuncia en {platform_name} actualizados en 2024/2025.

CRITERIOS ESTRICTOS:
- URLs de centros de ayuda oficiales ÚNICAMENTE
- Procedimientos paso a paso recientes (post-2024)
- Sin consejos generales o teóricos
- Capturas/screenshots oficiales si están disponibles
- Específico para ciberacoso/ciberviolencia

FUENTES OFICIALES únicamente:
- Centros de ayuda/soporte oficiales
- Documentación de seguridad de plataformas
- Guías de denuncia actualizadas
- Procedimientos de moderación oficiales

Responde ÚNICAMENTE en este formato exacto:
Plataforma: [Nombre exacto de la plataforma]
URL: [Enlace directo del centro de ayuda oficial]
Procedimiento: [Pasos exactos 1,2,3... para denunciar ciberacoso]
Plazo: [Tiempo de procesamiento anunciado por la plataforma]
Evidencias: [Tipos de evidencia requerida]
Seguimiento: [Cómo hacer seguimiento de la denuncia]"""
        }
        
        return prompts.get(language, prompts["EN"])
    
    # ========================================================================
    # ⚖️ SIGNALEMENT AUTORITE - Procédures officielles, pas d'interprétation
    # ========================================================================
    
    @staticmethod
    def _prompt_signalement_autorite(country: str, language: str, **kwargs) -> str:
        """Prompt pour découverte de signalement aux autorités officielles"""
        
        prompts = {
            "FR": f"""Trouve les plateformes OFFICIELLES de signalement gouvernemental pour cyberharcèlement en {country}.

CRITÈRES STRICTS:
- Sites .gouv ou équivalent officiel UNIQUEMENT
- Formulaires en ligne fonctionnels et récents
- Procédures cyberharcèlement spécifiques (pas criminalité générale)
- Pas d'associations privées ou ONG
- Authority gouvernementale ou police/justice

SOURCES GOUVERNEMENTALES prioritaires:
- Plateformes police/gendarmerie nationales
- Ministères Justice/Intérieur
- Autorités de régulation numérique
- Services cybercriminalité officiels

Réponds UNIQUEMENT sous ce format exact:
Nom: [Plateforme gouvernementale officielle]
URL: [Site .gouv ou équivalent officiel]
Formulaire: [Lien direct vers formulaire cyberharcèlement]
Autorité: [Police/Justice/Régulateur responsable]
Juridiction: [Compétence territoriale]
Prérequis: [Conditions pour déposer signalement]""",

            "EN": f"""Find OFFICIAL government reporting platforms for cyberbullying in {country}.

STRICT CRITERIA:
- .gov or official equivalent sites ONLY
- Functional and recent online forms
- Specific cyberbullying procedures (not general crime)
- No private associations or NGOs
- Government authority or police/justice

PRIORITY GOVERNMENT SOURCES:
- National police/law enforcement platforms
- Justice/Interior Ministries
- Digital regulation authorities
- Official cybercrime services

Answer ONLY in this exact format:
Name: [Official government platform]
URL: [.gov or official equivalent site]
Form: [Direct link to cyberbullying form]
Authority: [Police/Justice/Regulator responsible]
Jurisdiction: [Territorial competence]
Requirements: [Conditions to file report]""",

            "ES": f"""Encuentra plataformas OFICIALES gubernamentales de denuncia para ciberacoso en {country}.

CRITERIOS ESTRICTOS:
- Sitios .gob o equivalente oficial ÚNICAMENTE
- Formularios en línea funcionales y recientes
- Procedimientos específicos de ciberacoso (no criminalidad general)
- Sin asociaciones privadas u ONGs
- Autoridad gubernamental o policía/justicia

FUENTES GUBERNAMENTALES prioritarias:
- Plataformas policía/fuerzas del orden nacionales
- Ministerios Justicia/Interior
- Autoridades de regulación digital
- Servicios oficiales de cibercrimen

Responde ÚNICAMENTE en este formato exacto:
Nombre: [Plataforma gubernamental oficial]
URL: [Sitio .gob o equivalente oficial]
Formulario: [Enlace directo a formulario ciberacoso]
Autoridad: [Policía/Justicia/Regulador responsable]
Jurisdicción: [Competencia territorial]
Requisitos: [Condiciones para presentar denuncia]"""
        }
        
        return prompts.get(language, prompts["EN"])
    
    # ========================================================================
    # 🏢 ASSOCIATION LOCALE - Aide professionnelle, pas conseils généraux
    # ========================================================================
    
    @staticmethod
    def _prompt_association_locale(country: str, language: str, **kwargs) -> str:
        """Prompt pour découverte d'associations spécialisées locales"""
        
        prompts = {
            "FR": f"""Trouve des associations SPÉCIALISÉES en cyberharcèlement/cyberviolence locales en {country}.

CRITÈRES STRICTS:
- Associations agréées officiellement ou reconnues
- Spécialisées cyberviolence (pas aide générale)
- Services d'accompagnement professionnel
- Structures locales/régionales (pas internationales)
- Avec accompagnement juridique ou psychologique spécialisé

TYPES D'ASSOCIATIONS recherchées:
- Associations anti-cyberharcèlement agréées
- Services sociaux spécialisés cyberviolence
- Structures d'accompagnement juridique numérique
- Centres d'aide victimes numériques
- Associations jeunesse spécialisées

Réponds UNIQUEMENT sous ce format exact:
Nom: [Association/structure exacte]
URL: [Site officiel]
Description: [Spécialisation cyberviolence et services proposés]
Zone: [Zone géographique couverte]
Contact: [Téléphone ou email principal]
Agrément: [Type d'agrément ou reconnaissance officielle]""",

            "EN": f"""Find SPECIALIZED associations for cyberbullying/cyberviolence local to {country}.

STRICT CRITERIA:
- Officially accredited or recognized associations
- Specialized in cyberviolence (not general help)
- Professional support services
- Local/regional structures (not international)
- With specialized legal or psychological support

TYPES OF ASSOCIATIONS sought:
- Accredited anti-cyberbullying associations
- Specialized cyberviolence social services
- Digital legal support structures
- Digital victim support centers
- Specialized youth associations

Answer ONLY in this exact format:
Name: [Exact association/structure]
URL: [Official website]
Description: [Cyberviolence specialization and services offered]
Area: [Geographic area covered]
Contact: [Main phone or email]
Accreditation: [Type of accreditation or official recognition]""",

            "ES": f"""Encuentra asociaciones ESPECIALIZADAS en ciberacoso/ciberviolencia locales en {country}.

CRITERIOS ESTRICTOS:
- Asociaciones acreditadas oficialmente o reconocidas
- Especializadas en ciberviolencia (no ayuda general)
- Servicios de acompañamiento profesional
- Estructuras locales/regionales (no internacionales)
- Con acompañamiento jurídico o psicológico especializado

TIPOS DE ASOCIACIONES buscadas:
- Asociaciones anti-ciberacoso acreditadas
- Servicios sociales especializados en ciberviolencia
- Estructuras de acompañamiento jurídico digital
- Centros de ayuda a víctimas digitales
- Asociaciones juveniles especializadas

Responde ÚNICAMENTE en este formato exacto:
Nombre: [Asociación/estructura exacta]
URL: [Sitio oficial]
Descripción: [Especialización ciberviolencia y servicios ofrecidos]
Zona: [Zona geográfica cubierta]
Contacto: [Teléfono o email principal]
Acreditación: [Tipo de acreditación o reconocimiento oficial]"""
        }
        
        return prompts.get(language, prompts["EN"])
    
    # ================================================================
    # 🤝 SERVICES SUPPORT - Existant/fallback (généraliste)
    # ================================================================
    
    @staticmethod
    def _prompt_services_support(country: str, language: str, **kwargs) -> str:
        """Prompt existant pour services d'aide générale (fallback)"""
        
        prompts = {
            "FR": f"""Trouve-moi une association ou organisation LOCALE RÉELLE et EXISTANTE qui lutte contre la cyberviolence spécifiquement en {country}.
            
IMPORTANT: 
- Donne-moi une organisation DIFFÉRENTE à chaque fois
- Vérifie que l'organisation existe vraiment  
- Cherche UNIQUEMENT des associations LOCALES basées en {country}
- Évite les organisations internationales ou d'autres pays
- Évite de répéter les mêmes organisations

Réponds uniquement en français et sous ce format exact :
Nom : [nom exact de l'association/organisation]
URL : [site web officiel]
Description : [description en 1-2 phrases de leur action contre la cyberviolence]
Téléphone : [numéro si disponible, sinon laisser vide]
Email : [email si disponible, sinon laisser vide]""",

            "EN": f"""Find me a LOCAL REAL and EXISTING association or organization that fights cyberviolence specifically in {country}.
            
IMPORTANT:
- Give me a DIFFERENT organization each time
- Verify that the organization really exists
- Look ONLY for LOCAL associations based in {country}
- Avoid international organizations or from other countries
- Avoid repeating the same organizations

Answer only in English and use this exact format:
Name: [exact name of association/organization]
URL: [official website]
Description: [1-2 sentence description of their action against cyberviolence]
Phone: [number if available, otherwise leave empty]
Email: [email if available, otherwise leave empty]"""
        }
        
        return prompts.get(language, prompts["EN"])


# Fonction utilitaire pour l'intégration facile
def get_category_prompt(category: str, country: str, language: str, **kwargs) -> str:
    """
    Interface simple pour obtenir un prompt spécialisé
    
    Usage:
        prompt = get_category_prompt("contact_urgence", "France", "FR")
        prompt = get_category_prompt("procedure_plateforme", "Germany", "DE", platform_name="Instagram")
    """
    return CategoryPrompts.generate_prompt(category, country, language, **kwargs)


# Configuration des plateformes prioritaires pour procedure_plateforme
PRIORITY_PLATFORMS = [
    "Instagram", "TikTok", "Snapchat", 
    "Discord", "WhatsApp", "YouTube",
    "Facebook", "Twitter/X", "Telegram"
]

# Configuration des pays avec sources gouvernementales connues
GOVERNMENT_SOURCES = {
    "France": ["pharos.gouv.fr", "cybermalveillance.gouv.fr"],
    "Germany": ["bka.de", "bsi.bund.de"],
    "Spain": ["policia.es", "guardia-civil.es"],
    "Italy": ["poliziadistato.it", "carabinieri.it"],
    "Portugal": ["psp.pt", "gnr.pt"],
    "Belgium": ["police.be", "cybersecurity.be"]
}