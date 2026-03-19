"""
Prompts LLM spécialisés par catégorie de ressource.

Stratégie multi-langue : les prompts sont en anglais (langue pivot).
La langue de réponse est contrôlée via `get_system_prompt()` transmis
en system_prompt au LLM — compatible avec tous les providers.
"""

import langcodes
from typing import Dict, Callable


class CategoryPrompts:
    """Générateur de prompts spécialisés par catégorie — EN pivot + system_prompt langue."""

    @staticmethod
    def get_system_prompt(language_code: str) -> str:
        """Retourne un system_prompt demandant au LLM de répondre dans la langue cible.

        Les labels de champs (Name:, URL:, etc.) restent en anglais pour
        que le parser soit robuste quelle que soit la langue de contenu.
        """
        try:
            lang_name = langcodes.get(language_code.lower()).language_name("en")
        except Exception:
            lang_name = language_code

        return (
            f"You are a research assistant specialized in online safety resources. "
            f"Always respond entirely in {lang_name}. "
            f"Keep the field label names exactly as written in the prompt (do not translate them). "
            f"Only translate the field values and free-text content."
        )

    @staticmethod
    def generate_prompt(category: str, country: str, language: str, **kwargs) -> str:
        """
        Génère un prompt spécialisé selon la catégorie

        Args:
            category: Type de ressource (service_support, procedure_plateforme, etc.)
            country: Pays cible
            language: Code langue ISO (conservé pour compatibilité — le prompt est en anglais)
            **kwargs: Paramètres spécialisés (platform_name pour procedure_plateforme, etc.)
        """
        
        prompt_generators = {
            "service_support":      CategoryPrompts._prompt_service_support,
            "procedure_plateforme": CategoryPrompts._prompt_procedure_plateforme,
            "signalement_autorite": CategoryPrompts._prompt_signalement_autorite,
        }

        if category not in prompt_generators:
            raise ValueError(
                f"Catégorie non supportée: '{category}'. "
                f"Catégories valides: {list(prompt_generators.keys())}"
            )
        
        prompt = prompt_generators[category](country, language, **kwargs)

        # Ajout du bloc d'exclusion si des ressources ont déjà été trouvées
        exclude_orgs = kwargs.get("exclude_orgs", [])
        if exclude_orgs:
            org_list = ", ".join(exclude_orgs)
            prompt += f"\n\n⛔ ABSOLUTELY AVOID these already found resources: {org_list}"

        return prompt

    # =================================================================
    # ENRICHISSEMENT — prompts pour ressource connue (ajout manuel)
    # Différence clé : le nom est fourni, le LLM cherche les détails.
    # Le format de sortie est identique aux prompts de découverte pour
    # que _parse_llm_response puisse parser sans modification.
    # =================================================================

    @staticmethod
    def generate_enrich_prompt(category: str, name: str, country: str, language: str) -> str:
        """Génère un prompt d'enrichissement pour une ressource connue par son nom."""
        enrich_generators = {
            "service_support":      CategoryPrompts._enrich_service_support,
            "procedure_plateforme": CategoryPrompts._enrich_procedure_plateforme,
            "signalement_autorite": CategoryPrompts._enrich_signalement_autorite,
        }
        fn = enrich_generators.get(category)
        if not fn:
            raise ValueError(f"Catégorie non supportée: '{category}'")
        return fn(name, country, language)

    @staticmethod
    def _enrich_service_support(name: str, country: str, language: str) -> str:
        return f"""The following assistance service is known to exist in {country}: "{name}".
Find its exact official details. Leave a field empty if you are not certain.

Answer ONLY in this exact format:
Name: {name}
URL: [official website with https://]
DirectLink: [direct URL to help page or contact form]
Description: [what this service offers in 1-2 sentences]
Phone: [exact phone number or empty]
Audience: [minors | all]
ViolenceType: [cyberviolence | all]
Anonymous: [yes | no]
Governmental: [yes | no]"""

    @staticmethod
    def _enrich_procedure_plateforme(name: str, country: str, language: str) -> str:
        return f"""The following platform is known to exist: "{name}".
Find its exact official cyberbullying reporting procedure.

Answer ONLY in this exact format:
Platform: {name}
URL: [official help center with https://]
DirectLink: [direct URL to the cyberbullying-specific page]
Description: [what this procedure allows in 1-2 sentences]
ActionType: [report | block | content_removal | profile_management]
Anonymous: [yes | no]"""

    @staticmethod
    def _enrich_signalement_autorite(name: str, country: str, language: str) -> str:
        return f"""The following official reporting authority is known to exist in {country}: "{name}".
Find its exact official details for cyberbullying reporting.

Answer ONLY in this exact format:
Name: {name}
URL: [official .gov or equivalent site with https://]
DirectLink: [direct URL to cyberbullying form with https://]
Description: [what this platform allows in 1-2 sentences]
Authority: [Police/Justice/Regulator responsible]
ReportingMethod: [form | phone | whatsapp | email | app | mail]
Anonymous: [yes | no]
Audience: [minors | all]
Governmental: [yes | no]"""

    # =================================================================
    # �️ SERVICE SUPPORT - Services d'assistance nationaux (V2)

    # =================================================================

    @staticmethod
    def _prompt_service_support(country: str, language: str, **kwargs) -> str:
        """EN-only prompt. Language via system_prompt (see get_system_prompt)."""
        return f"""Find OFFICIAL assistance services against cyberviolence in {country}.

STRICT CRITERIA:
- Absolute priority to government or officially recognized services
- Specialized in cyberviolence, cyberbullying, or violence (including offline)
- Accessible to minors AND/OR general public
- Direct contact: phone number, form, chat — not a generic institutional website
- Include 24h services, office hours, and online platforms

PRIORITY SOURCES:
- National short numbers (3018, 116 111, 116 000…)
- Specialized government services (e.g. e-Enfance, Net Écoute)
- Government online help platforms
- Youth cyberviolence hotlines

Answer ONLY in this exact format:
Name: [Exact official service]
URL: [Official website]
DirectLink: [Direct URL to help page or contact form]
Description: [Service offered in 1-2 sentences]
Phone: [Number if available, otherwise empty]
Hours: [Precise availability]
Audience: [minors | all]
ViolenceType: [cyberviolence | all]
Anonymous: [yes | no]
Governmental: [yes | no]"""
        # ===== LEGACY multi-language dict (unreachable — kept for reference) =====
        prompts = {
            "FR": f"""Trouve des services d'assistance OFFICIELS contre la cyberviolence en {country}.

CRITÈRES STRICTS :
- Priorité absolue aux services gouvernementaux ou officiellement reconnus
- Spécialisés cyberviolence, cyberharcèlement, ou violence (y compris hors internet)
- Accessibles aux mineurs ET/OU au grand public
- Contact direct : numéro, formulaire, chat — pas un site institutionnel générique
- Inclure services 24h, horaires bureau, et plateformes en ligne

SOURCES PRIORITAIRES :
- Numéros nationaux courts (3018, 116 111, 116 000...)
- Services gouvernementaux spécialisés (ex: e-Enfance, Net Écoute)
- Plateformes d'aide en ligne gouvernementales
- Hotlines spécialisées cyberviolence jeunesse

Réponds UNIQUEMENT sous ce format exact :
Nom: [Service officiel exact]
URL: [Site officiel]
LienDirect: [URL directe vers la page d'aide ou formulaire de contact]
Description: [Service proposé en 1-2 phrases]
Telephone: [Numéro si disponible, sinon vide]
Horaires: [Disponibilité précise]
PublicVise: [mineurs | tous]
TypeViolence: [cyberviolence | tous]
SignalementAnonyme: [oui | non]
SourceGouvernementale: [oui | non]""",

            "EN": f"""Find OFFICIAL assistance services against cyberviolence in {country}.

STRICT CRITERIA:
- Absolute priority to government or officially recognized services
- Specialized in cyberviolence, cyberbullying, or violence (including offline)
- Accessible to minors AND/OR general public
- Direct contact: phone number, form, chat — not a generic institutional website
- Include 24h services, office hours, and online platforms

PRIORITY SOURCES:
- National short numbers (3018, 116 111, 116 000...)
- Specialized government services
- Government online help platforms
- Youth cyberviolence hotlines

Answer ONLY in this exact format:
Name: [Exact official service]
URL: [Official website]
DirectLink: [Direct URL to help page or contact form]
Description: [Service offered in 1-2 sentences]
Phone: [Number if available, otherwise empty]
Hours: [Precise availability]
Audience: [minors | all]
ViolenceType: [cyberviolence | all]
Anonymous: [yes | no]
Governmental: [yes | no]""",

            "ES": f"""Encuentra servicios de asistencia OFICIALES contra la ciberviolencia en {country}.

CRITERIOS ESTRICTOS:
- Prioridad absoluta a servicios gubernamentales o reconocidos oficialmente
- Especializados en ciberviolencia, ciberacoso o violencia (incluso fuera de internet)
- Accesibles a menores Y/O público general
- Contacto directo: número, formulario, chat — no sitio institucional genérico
- Incluir servicios 24h, horario de oficina y plataformas en línea

FUENTES PRIORITARIAS:
- Números nacionales cortos (tipo 3018, 116 111...)
- Servicios gubernamentales especializados
- Plataformas de ayuda en línea gubernamentales
- Líneas de atención ciberviolencia juvenil

Responde ÚNICAMENTE en este formato exacto:
Nombre: [Servicio oficial exacto]
URL: [Sitio oficial]
EnlaceDirecto: [URL directa a la página de ayuda o formulario]
Descripción: [Servicio ofrecido en 1-2 frases]
Teléfono: [Número si disponible, si no vacío]
Horarios: [Disponibilidad precisa]
Público: [menores | todos]
TipoViolencia: [ciberviolencia | todos]
Anónimo: [sí | no]
Gubernamental: [sí | no]""",

            "IT": f"""Trova servizi di assistenza UFFICIALI contro la cyberviolenza in {country}.

CRITERI RIGOROSI:
- Priorità assoluta ai servizi governativi o riconosciuti ufficialmente
- Specializzati in cyberviolenza, cyberbullismo o violenza (anche offline)
- Accessibili a minori E/O al pubblico generale
- Contatto diretto: telefono, modulo, chat — non sito istituzionale generico
- Includere servizi 24h, orari di ufficio e piattaforme online

FONTI PRIORITARIE:
- Numeri nazionali brevi (tipo 116 111, 116 000)
- Servizi governativi specializzati
- Piattaforme di aiuto online governative
- Linee di assistenza cyberviolenza giovani

Rispondi UNICAMENTE in questo formato esatto:
Nome: [Servizio ufficiale esatto]
URL: [Sito ufficiale]
LinkDiretto: [URL diretta alla pagina di aiuto o modulo contatto]
Descrizione: [Servizio offerto in 1-2 frasi]
Telefono: [Numero se disponibile, altrimenti vuoto]
Orari: [Disponibilità precisa]
Pubblico: [minori | tutti]
TipoViolenza: [cyberviolenza | tutti]
Anonimo: [sì | no]
Governativo: [sì | no]""",

            "DE": f"""Finde OFFIZIELLE Hilfsdienste gegen Cybergewalt in {country}.

STRENGE KRITERIEN:
- Absolute Priorität für staatliche oder offiziell anerkannte Dienste
- Spezialisiert auf Cybergewalt, Cybermobbing oder Gewalt (auch offline)
- Zugänglich für Minderjährige UND/ODER die Allgemeinheit
- Direkter Kontakt: Telefon, Formular, Chat — keine generische Behördenwebsite
- 24h-Dienste, Bürozeiten und Online-Plattformen einbeziehen

PRIORITÄRE QUELLEN:
- Nationale Kurznummern (wie 116 111, 116 000)
- Spezialisierte Regierungsdienste
- Staatliche Online-Hilfsplattformen
- Jugend-Cybergewalt-Hotlines

Antworte NUR in diesem exakten Format:
Name: [Exakter offizieller Service]
URL: [Offizielle Website]
DirektLink: [Direkter URL zur Hilfeseite oder Kontaktformular]
Beschreibung: [Angebotener Service in 1-2 Sätzen]
Telefon: [Nummer falls verfügbar, sonst leer]
Zeiten: [Genaue Verfügbarkeit]
Zielgruppe: [Minderjährige | alle]
Gewaltart: [Cybergewalt | alle]
Anonym: [ja | nein]
Behördlich: [ja | nein]""",

            "PT": f"""Encontre serviços de assistência OFICIAIS contra a ciberviolência em {country}.

CRITÉRIOS RIGOROSOS:
- Prioridade absoluta a serviços governamentais ou oficialmente reconhecidos
- Especializados em ciberviolência, cyberbullying ou violência (incluindo offline)
- Acessíveis a menores E/OU ao público geral
- Contacto direto: telefone, formulário, chat — não site institucional genérico
- Incluir serviços 24h, horário de atendimento e plataformas online

FONTES PRIORITÁRIAS:
- Números nacionais curtos (tipo 116 111, 116 000)
- Serviços governamentais especializados
- Plataformas de ajuda online governamentais
- Linhas de apoio ciberviolência jovens

Responda APENAS neste formato exacto:
Nome: [Serviço oficial exacto]
URL: [Site oficial]
LinkDirecto: [URL directo para página de ajuda ou formulário]
Descrição: [Serviço oferecido em 1-2 frases]
Telefone: [Número se disponível, caso contrário vazio]
Horários: [Disponibilidade precisa]
Público: [menores | todos]
TipoViolência: [ciberviolência | todos]
Anónimo: [sim | não]
Governamental: [sim | não]"""
        }
        
        return prompts.get(language, prompts["EN"])
    
    # ================================================================
    # 🛠️ PROCEDURE PLATEFORME - Steps exacts de signalement/blocage
    # ================================================================
    
    @staticmethod
    def _prompt_procedure_plateforme(country: str, language: str, **kwargs) -> str:
        """EN-only prompt. Language via system_prompt (see get_system_prompt)."""
        platform_name = kwargs.get("platform_name", "all platforms")
        return f"""Find EXACT reporting procedures on {platform_name} updated in 2024/2025.

TARGET PLATFORMS (include social networks AND youth messaging apps):
Instagram, TikTok, Snapchat, YouTube, Facebook, X/Twitter,
Discord, WhatsApp, Telegram, BeReal, Twitch

STRICT CRITERIA:
- Official help center URLs ONLY
- Recent step-by-step procedures (post-2024)
- Specific to cyberbullying/cyberviolence
- Indicate exact action type: report, block, content removal, profile management

OFFICIAL SOURCES only:
- Official platform help centers
- Official security documentation
- Updated reporting guides

Answer ONLY in this exact format:
Platform: [Exact platform name]
URL: [Official help center link]
DirectLink: [Direct URL to cyberbullying-specific page]
Description: [1-2 sentences: what this page allows you to do (report, block, safety settings, etc.)]
ActionType: [report | block | content_removal | profile_management]
Anonymous: [yes | no]"""
        # ===== LEGACY multi-language dict (unreachable — kept for reference) =====
        prompts = {
            "FR": f"""Trouve les procédures EXACTES de signalement sur {platform_name} mises à jour en 2024/2025.

PLATEFORMES CIBLES (inclure réseaux sociaux ET apps de messagerie jeunesse) :
Instagram, TikTok, Snapchat, YouTube, Facebook, X/Twitter,
Discord, WhatsApp, Telegram, BeReal, Twitch

CRITÈRES STRICTS :
- URLs help center officiels UNIQUEMENT
- Procédures step-by-step récentes (post-2024)
- Spécifique au cyberharcèlement/cyberviolence
- Indiquer le type d'action exact : signalement, blocage, suppression de contenu, gestion de profil

SOURCES OFFICIELLES uniquement :
- Help centers / centres d'aide officiels des plateformes
- Documentation de sécurité officielle
- Guides de signalement mis à jour

Réponds UNIQUEMENT sous ce format exact :
Plateforme: [Nom exact de la plateforme]
URL: [Lien help center officiel]
LienDirect: [URL directe vers la page spécifique cyberharcèlement]
Description: [1-2 phrases : ce que cette page permet de faire (signaler, bloquer, paramètres de sécurité, etc.)]
TypeAction: [signalement | blocage | suppression_contenu | gestion_profil]
SignalementAnonyme: [oui | non]""",

            "EN": f"""Find EXACT reporting procedures on {platform_name} updated in 2024/2025.

TARGET PLATFORMS (include social networks AND youth messaging apps):
Instagram, TikTok, Snapchat, YouTube, Facebook, X/Twitter,
Discord, WhatsApp, Telegram, BeReal, Twitch

STRICT CRITERIA:
- Official help center URLs ONLY
- Recent step-by-step procedures (post-2024)
- Specific to cyberbullying/cyberviolence
- Indicate exact action type: report, block, content removal, profile management

OFFICIAL SOURCES only:
- Official platform help centers
- Official security documentation
- Updated reporting guides

Answer ONLY in this exact format:
Platform: [Exact platform name]
URL: [Official help center link]
DirectLink: [Direct URL to cyberbullying-specific page]
Description: [1-2 sentences: what this page allows you to do (report, block, safety settings, etc.)]
ActionType: [report | block | content_removal | profile_management]
Anonymous: [yes | no]""",

            "ES": f"""Encuentra procedimientos EXACTOS de denuncia en {platform_name} actualizados en 2024/2025.

PLATAFORMAS OBJETIVO (incluir redes sociales Y apps de mensajería juvenil):
Instagram, TikTok, Snapchat, YouTube, Facebook, X/Twitter,
Discord, WhatsApp, Telegram, BeReal, Twitch

CRITERIOS ESTRICTOS:
- URLs de centros de ayuda oficiales ÚNICAMENTE
- Procedimientos paso a paso recientes (post-2024)
- Específico para ciberacoso/ciberviolencia
- Indicar el tipo exacto de acción: denuncia, bloqueo, eliminación de contenido, gestión de perfil

FUENTES OFICIALES únicamente:
- Centros de ayuda oficiales de las plataformas
- Documentación de seguridad oficial
- Guías de denuncia actualizadas

Responde ÚNICAMENTE en este formato exacto:
Plataforma: [Nombre exacto de la plataforma]
URL: [Enlace centro de ayuda oficial]
EnlaceDirecto: [URL directa a la página específica de ciberacoso]
Descripción: [1-2 frases: qué permite hacer esta página (denunciar, bloquear, configuración de seguridad, etc.)]
TipoAcción: [denuncia | bloqueo | eliminación_contenido | gestión_perfil]
Anónimo: [sí | no]""",

            "IT": f"""Trova le procedure ESATTE di segnalazione su {platform_name} aggiornate nel 2024/2025.

PIATTAFORME TARGET (includere social network E app di messaggistica per giovani):
Instagram, TikTok, Snapchat, YouTube, Facebook, X/Twitter,
Discord, WhatsApp, Telegram, BeReal, Twitch

CRITERI RIGOROSI:
- URL dei centri di aiuto ufficiali UNICAMENTE
- Procedure step-by-step recenti (post-2024)
- Specifico per cyberbullismo/cyberviolenza
- Indicare il tipo esatto di azione: segnalazione, blocco, rimozione contenuto, gestione profilo

FONTI UFFICIALI unicamente:
- Centri di aiuto/help center ufficiali delle piattaforme
- Documentazione di sicurezza ufficiale
- Guide di segnalazione aggiornate

Rispondi UNICAMENTE in questo formato esatto:
Piattaforma: [Nome esatto della piattaforma]
URL: [Link help center ufficiale]
LinkDiretto: [URL diretta alla pagina specifica cyberbullismo]
Descrizione: [1-2 frasi: cosa permette di fare questa pagina (segnalare, bloccare, impostazioni di sicurezza, ecc.)]
TipoAzione: [segnalazione | blocco | rimozione_contenuto | gestione_profilo]
Anonimo: [sì | no]""",

            "DE": f"""Finde GENAUE Meldeverfahren auf {platform_name} aktualisiert in 2024/2025.

ZIEL-PLATTFORMEN (soziale Netzwerke UND Jugend-Messaging-Apps einschließen):
Instagram, TikTok, Snapchat, YouTube, Facebook, X/Twitter,
Discord, WhatsApp, Telegram, BeReal, Twitch

STRENGE KRITERIEN:
- Nur offizielle Hilfecenter-URLs
- Aktuelle schrittweise Anleitungen (nach 2024)
- Spezifisch für Cybermobbing/Cybergewalt
- Genauen Aktionstyp angeben: Meldung, Blockierung, Inhaltsentfernung, Profilverwaltung

NUR OFFIZIELLE QUELLEN:
- Offizielle Hilfecenter der Plattformen
- Offizielle Sicherheitsdokumentation
- Aktualisierte Meldeanleitungen

Antworte NUR in diesem exakten Format:
Plattform: [Exakter Plattformname]
URL: [Offizieller Hilfecenter-Link]
DirekterLink: [Direkter URL zur Cybermobbing-spezifischen Seite]
Beschreibung: [1-2 Sätze: was diese Seite erlaubt (melden, blockieren, Sicherheitseinstellungen, usw.)]
Aktionstyp: [meldung | blockierung | inhaltsentfernung | profilverwaltung]
Anonym: [ja | nein]""",

            "PT": f"""Encontra procedimentos EXATOS de denúncia em {platform_name} atualizados em 2024/2025.

PLATAFORMAS ALVO (incluir redes sociais E apps de mensagens juvenis):
Instagram, TikTok, Snapchat, YouTube, Facebook, X/Twitter,
Discord, WhatsApp, Telegram, BeReal, Twitch

CRITÉRIOS RIGOROSOS:
- URLs de centros de ajuda oficiais UNICAMENTE
- Procedimentos passo-a-passo recentes (pós-2024)
- Específico para ciberassédio/ciberviolência
- Indicar o tipo exato de ação: denúncia, bloqueio, remoção de conteúdo, gestão de perfil

FONTES OFICIAIS unicamente:
- Centros de ajuda/help centers oficiais das plataformas
- Documentação de segurança oficial
- Guias de denúncia atualizados

Responde UNICAMENTE neste formato exato:
Plataforma: [Nome exato da plataforma]
URL: [Link do help center oficial]
LinkDireto: [URL direta para a página específica de ciberassédio]
Descrição: [1-2 frases: o que esta página permite fazer (denunciar, bloquear, definições de segurança, etc.)]
TipoAção: [denúncia | bloqueio | remoção_conteúdo | gestão_perfil]
Anônimo: [sim | não]"""
        }
        
        return prompts.get(language, prompts["EN"])
    
    # ========================================================================
    # ⚖️ SIGNALEMENT AUTORITE - Procédures officielles, pas d'interprétation
    # ========================================================================
    
    @staticmethod
    def _prompt_signalement_autorite(country: str, language: str, **kwargs) -> str:
        """EN-only prompt. Language via system_prompt (see get_system_prompt)."""
        return f"""Find OFFICIAL government reporting platforms for cyberbullying in {country}.

KNOWN EXAMPLES (verify and complete):
- France: PHAROS (internet-signalement.gouv.fr), cybermalveillance.gouv.fr
- UK: report.cybercrime.gov.uk, CEOP
- Germany: BKA online reporting

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
URL: [.gov or official equivalent site — WITH https://]
DirectLink: [Direct URL to cyberbullying form — WITH https://]
Description: [1-2 sentences: what this platform allows you to do]
Authority: [Police/Justice/Regulator responsible]
Jurisdiction: [Territorial competence]
ReportingMethod: [form | phone | whatsapp | email | app | mail]
Anonymous: [yes | no]
Audience: [minors | all]
ViolenceType: [cyberviolence | all]
Governmental: [yes | no]"""
        # ===== LEGACY multi-language dict (unreachable — kept for reference) =====
        prompts = {
            "FR": f"""Trouve les plateformes OFFICIELLES de signalement aux autorités pour cyberharcèlement en {country}.

EXEMPLES CONNUS (à vérifier et compléter) :
- France : PHAROS (internet-signalement.gouv.fr), cybermalveillance.gouv.fr, Thémis
- Belgique : eCops (police.be/fr/internet)
- Suisse : fedpol.admin.ch

CRITÈRES STRICTS :
- Sites .gouv ou équivalent officiel UNIQUEMENT
- Formulaires en ligne fonctionnels et récents
- Procédures cyberharcèlement spécifiques (pas criminalité générale)
- Pas d'associations privées ou ONG
- Autorité gouvernementale ou police/justice

SOURCES GOUVERNEMENTALES prioritaires :
- Plateformes police/gendarmerie nationales
- Ministères Justice/Intérieur
- Autorités de régulation numérique
- Services cybercriminalité officiels

Réponds UNIQUEMENT sous ce format exact :
Nom: [Plateforme gouvernementale officielle]
URL: [Site .gouv ou équivalent officiel — AVEC https://]
LienDirect: [URL directe vers le formulaire cyberharcèlement — AVEC https://]
Description: [1-2 phrases : ce que permet de faire cette plateforme]
Autorité: [Police/Justice/Régulateur responsable]
Juridiction: [Compétence territoriale]
ModeSignalement: [formulaire | téléphone | whatsapp | email | application | courrier]
SignalementAnonyme: [oui | non]
PublicVise: [mineurs | tous]
TypeViolence: [cyberviolence | tous]
SourceGouvernementale: [oui | non]""",

            "EN": f"""Find OFFICIAL government reporting platforms for cyberbullying in {country}.

KNOWN EXAMPLES (verify and complete):
- France: PHAROS (internet-signalement.gouv.fr), cybermalveillance.gouv.fr
- UK: report.cybercrime.gov.uk, CEOP
- Germany: BKA online reporting

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
URL: [.gov or official equivalent site — WITH https://]
DirectLink: [Direct URL to cyberbullying form — WITH https://]
Description: [1-2 sentences: what this platform allows you to do]
Authority: [Police/Justice/Regulator responsible]
Jurisdiction: [Territorial competence]
ReportingMethod: [form | phone | whatsapp | email | app | mail]
Anonymous: [yes | no]
Audience: [minors | all]
ViolenceType: [cyberviolence | all]
Governmental: [yes | no]""",

            "ES": f"""Encuentra plataformas OFICIALES gubernamentales de denuncia para ciberacoso en {country}.

EJEMPLOS CONOCIDOS (verificar y completar):
- España: Policía Nacional (policia.es), Guardia Civil (guardiacivil.es)
- INCIBE-CERT para incidentes digitales

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
URL: [Sitio .gob o equivalente oficial — CON https://]
EnlaceDirecto: [URL directa al formulario de ciberacoso — CON https://]
Descripción: [1-2 frases: qué permite hacer esta plataforma]
Autoridad: [Policía/Justicia/Regulador responsable]
Jurisdicción: [Competencia territorial]
MétodoDenuncia: [formulario | teléfono | whatsapp | email | aplicación | correo]
Anónimo: [sí | no]
Público: [menores | todos]
TipoViolencia: [ciberviolencia | todos]
Gubernamental: [sí | no]""",

            "IT": f"""Trova piattaforme UFFICIALI governative di segnalazione per cyberbullismo in {country}.

ESEMPI NOTI (verificare e completare):
- Italia: Polizia Postale (commissariatodips.it), AGCOM
- Svizzera: fedpol.admin.ch

CRITERI RIGOROSI:
- Siti .gov.it o equivalente ufficiale UNICAMENTE
- Moduli online funzionali e recenti
- Procedure specifiche per cyberbullismo (non criminalità generale)
- Nessuna associazione privata o ONG
- Autorità governativa o polizia/giustizia

FONTI GOVERNATIVE prioritarie:
- Piattaforme polizia/forze dell'ordine nazionali
- Ministeri Giustizia/Interno
- Autorità di regolamentazione digitale
- Servizi cybercriminalità ufficiali

Rispondi UNICAMENTE in questo formato esatto:
Nome: [Piattaforma governativa ufficiale]
URL: [Sito .gov o equivalente ufficiale — CON https://]
LinkDiretto: [URL diretto al modulo cyberbullismo — CON https://]
Descrizione: [1-2 frasi: cosa permette di fare questa piattaforma]
Autorità: [Polizia/Giustizia/Regolatore responsabile]
Giurisdizione: [Competenza territoriale]
MetodoSegnalazione: [modulo | telefono | whatsapp | email | app | posta]
Anonimo: [sì | no]
Pubblico: [minori | tutti]
TipoViolenza: [cyberviolenza | tutti]
Governativo: [sì | no]""",

            "DE": f"""Finde OFFIZIELLE Behördenplattformen zur Meldung von Cybermobbing in {country}.

BEKANNTE BEISPIELE (überprüfen und ergänzen):
- Deutschland: BKA (bka.de), Bundesnetzagentur
- Österreich: bundeskriminalamt.at
- Schweiz: fedpol.admin.ch

STRENGE KRITERIEN:
- Nur .bund.de oder offizielle Äquivalent-Seiten
- Funktionierende und aktuelle Online-Formulare
- Spezifische Cybermobbing-Verfahren (keine allgemeine Kriminalität)
- Keine privaten Vereine oder NGOs
- Regierungsbehörde oder Polizei/Justiz

PRIORITÄRE BEHÖRDENQUELLEN:
- Nationale Polizei/Strafverfolgungsplattformen
- Justiz-/Innenministerien
- Digitale Regulierungsbehörden
- Offizielle Cyberkriminalitätsdienste

Antworte NUR in diesem exakten Format:
Name: [Offizielle Behördenplattform]
URL: [.bund.de oder offizielle Äquivalent-Seite — MIT https://]
DirekterLink: [Direkter URL zum Cybermobbing-Formular — MIT https://]
Beschreibung: [1-2 Sätze: was diese Plattform erlaubt]
Behörde: [Polizei/Justiz/Regulierer zuständig]
Zuständigkeit: [Gebietliche Zuständigkeit]
Meldeweg: [formular | telefon | whatsapp | email | app | post]
Anonym: [ja | nein]
Zielgruppe: [Minderjährige | alle]
Gewaltart: [Cybergewalt | alle]
Behördlich: [ja | nein]""",

            "PT": f"""Encontra plataformas OFICIAIS governamentais de denúncia para ciberassédio em {country}.

EXEMPLOS CONHECIDOS (verificar e completar):
- Portugal: PSP (psp.pt), GNR (gnr.pt), CNCS
- Brasil: SaferNet (safernet.org.br), Polícia Federal

CRITÉRIOS RIGOROSOS:
- Sites .gov.pt ou equivalente oficial UNICAMENTE
- Formulários online funcionais e recentes
- Procedimentos específicos de ciberassédio (não criminalidade geral)
- Sem associações privadas ou ONGs
- Autoridade governamental ou polícia/justiça

FONTES GOVERNAMENTAIS prioritárias:
- Plataformas polícia/forças de segurança nacionais
- Ministérios da Justiça/Interior
- Autoridades de regulação digital
- Serviços oficiais de cibercriminalidade

Responde UNICAMENTE neste formato exato:
Nome: [Plataforma governamental oficial]
URL: [Site .gov ou equivalente oficial — COM https://]
LinkDireto: [URL direto para o formulário de ciberassédio — COM https://]
Descrição: [1-2 frases: o que esta plataforma permite fazer]
Autoridade: [Polícia/Justiça/Regulador responsável]
Jurisdição: [Competência territorial]
MétodoDenúncia: [formulário | telefone | whatsapp | email | aplicação | correio]
Anônimo: [sim | não]
Público-alvo: [menores | todos]
TipoViolência: [ciberviolência | todos]
Governamental: [sim | não]"""
        }
        
        return prompts.get(language, prompts["EN"])
    
    # ========================================================================
    # 🏢 ASSOCIATION LOCALE — supprimée en V2
    #    Les ressources locales sont absorbées par service_support.
    #    Méthode conservée uniquement si des données V1 doivent être relues.
    # ========================================================================

    @staticmethod
    def _prompt_association_locale(country: str, language: str, **kwargs) -> str:
        """Deprecated V2 — redirige vers _prompt_service_support."""
        return CategoryPrompts._prompt_service_support(country, language, **kwargs)
        
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

# Fonction utilitaire pour l'intégration facile
def get_category_prompt(category: str, country: str, language: str, **kwargs) -> str:
    """
    Interface simple pour obtenir un prompt spécialisé
    
    Usage:
        prompt = get_category_prompt("service_support", "France", "FR")
        prompt = get_category_prompt("procedure_plateforme", "Germany", "DE", platform_name="Instagram")
    """
    return CategoryPrompts.generate_prompt(category, country, language, **kwargs)


# Plateformes prioritaires V2 pour procedure_plateforme
# Séparées en deux groupes pour faciliter le ciblage des prompts.
PRIORITY_PLATFORMS_SOCIAL = [
    "Instagram", "TikTok", "Snapchat", "YouTube",
    "Facebook", "X/Twitter", "BeReal", "Twitch",
]
PRIORITY_PLATFORMS_MESSAGING = [
    "Discord", "WhatsApp", "Telegram",
]
PRIORITY_PLATFORMS = PRIORITY_PLATFORMS_SOCIAL + PRIORITY_PLATFORMS_MESSAGING

# Configuration des pays avec sources gouvernementales connues
GOVERNMENT_SOURCES = {
    "France": ["pharos.gouv.fr", "cybermalveillance.gouv.fr"],
    "Germany": ["bka.de", "bsi.bund.de"],
    "Spain": ["policia.es", "guardia-civil.es"],
    "Italy": ["poliziadistato.it", "carabinieri.it"],
    "Portugal": ["psp.pt", "gnr.pt"],
    "Belgium": ["police.be", "cybersecurity.be"]
}