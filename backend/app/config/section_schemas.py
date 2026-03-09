"""Section JSON schemas and structural rules for AI text generation.

Defines the expected JSON structure for each section type,
array validation rules, and key synonym mappings for
normalizing AI-generated field names.
"""

from typing import Dict, List


# =========================================================
# SECTION SCHEMAS: JSON template for each section type.
# _generate_texts() assembles only the schemas for the
# sections the user actually requested, cutting prompt size
# by 40-60% and reducing noise for the LLM.
# =========================================================
SECTION_SCHEMAS: Dict[str, str] = {
    "hero": '''"hero": {{
    "HERO_TITLE": "Headline impattante (max 8 parole, MIN 3 parole)",
    "HERO_SUBTITLE": "Sottotitolo evocativo (MIN 15 parole, 2-3 frasi che creano desiderio)",
    "HERO_CTA_TEXT": "Testo bottone CTA (3-5 parole, verbo d'azione)",
    "HERO_CTA_URL": "#contact",
    "HERO_IMAGE_URL": "",
    "HERO_IMAGE_ALT": "Descrizione immagine specifica per il business",
    "HERO_ROTATING_TEXTS": "3-4 frasi alternative per il titolo hero, separate da | (es: Frase Uno|Frase Due|Frase Tre)"
  }}''',
    "about": '''"about": {{
    "ABOUT_TITLE": "Titolo sezione (evocativo, NO 'Chi Siamo')",
    "ABOUT_SUBTITLE": "Sottotitolo (MIN 10 parole)",
    "ABOUT_TEXT": "MIN 40 parole: racconta la storia/missione con dettagli specifici, emozioni, visione futura",
    "ABOUT_HIGHLIGHT_1": "Fatto chiave 1",
    "ABOUT_HIGHLIGHT_2": "Fatto chiave 2",
    "ABOUT_HIGHLIGHT_3": "Fatto chiave 3",
    "ABOUT_HIGHLIGHT_NUM_1": "25",
    "ABOUT_HIGHLIGHT_NUM_2": "500",
    "ABOUT_HIGHLIGHT_NUM_3": "98"
  }}''',
    "services": '''"services": {{
    "SERVICES_TITLE": "Titolo sezione",
    "SERVICES_SUBTITLE": "Sottotitolo",
    "SERVICES": [
      {{"SERVICE_ICON": "emoji unico", "SERVICE_TITLE": "Nome servizio (2-4 parole)", "SERVICE_DESCRIPTION": "MIN 15 parole: beneficio concreto per il cliente"}},
      {{"SERVICE_ICON": "emoji unico", "SERVICE_TITLE": "Nome servizio (2-4 parole)", "SERVICE_DESCRIPTION": "MIN 15 parole: beneficio concreto per il cliente"}},
      {{"SERVICE_ICON": "emoji unico", "SERVICE_TITLE": "Nome servizio (2-4 parole)", "SERVICE_DESCRIPTION": "MIN 15 parole: beneficio concreto per il cliente"}}
    ]
  }}''',
    "features": '''"features": {{
    "FEATURES_TITLE": "Titolo sezione",
    "FEATURES_SUBTITLE": "Sottotitolo",
    "FEATURES": [
      {{"FEATURE_ICON": "emoji unico", "FEATURE_TITLE": "Feature (2-4 parole)", "FEATURE_DESCRIPTION": "MIN 12 parole: cosa ottiene l'utente"}},
      {{"FEATURE_ICON": "emoji unico", "FEATURE_TITLE": "Feature (2-4 parole)", "FEATURE_DESCRIPTION": "MIN 12 parole: cosa ottiene l'utente"}},
      {{"FEATURE_ICON": "emoji unico", "FEATURE_TITLE": "Feature (2-4 parole)", "FEATURE_DESCRIPTION": "MIN 12 parole: cosa ottiene l'utente"}},
      {{"FEATURE_ICON": "emoji unico", "FEATURE_TITLE": "Feature (2-4 parole)", "FEATURE_DESCRIPTION": "MIN 12 parole: cosa ottiene l'utente"}},
      {{"FEATURE_ICON": "emoji unico", "FEATURE_TITLE": "Feature (2-4 parole)", "FEATURE_DESCRIPTION": "MIN 12 parole: cosa ottiene l'utente"}},
      {{"FEATURE_ICON": "emoji unico", "FEATURE_TITLE": "Feature (2-4 parole)", "FEATURE_DESCRIPTION": "MIN 12 parole: cosa ottiene l'utente"}}
    ]
  }}''',
    "testimonials": '''"testimonials": {{
    "TESTIMONIALS_TITLE": "Titolo sezione",
    "TESTIMONIALS": [
      {{"TESTIMONIAL_TEXT": "MIN 20 parole: storia specifica con dettagli, emozioni, risultati concreti", "TESTIMONIAL_AUTHOR": "Nome e Cognome realistico italiano", "TESTIMONIAL_ROLE": "Ruolo specifico (es: CEO di NomeDitta)", "TESTIMONIAL_INITIAL": "N"}},
      {{"TESTIMONIAL_TEXT": "MIN 20 parole: esperienza unica, diversa dalla precedente", "TESTIMONIAL_AUTHOR": "Nome e Cognome", "TESTIMONIAL_ROLE": "Ruolo specifico", "TESTIMONIAL_INITIAL": "N"}},
      {{"TESTIMONIAL_TEXT": "MIN 20 parole: racconto con before/after, numeri o dettagli specifici", "TESTIMONIAL_AUTHOR": "Nome e Cognome", "TESTIMONIAL_ROLE": "Ruolo specifico", "TESTIMONIAL_INITIAL": "N"}}
    ]
  }}''',
    "cta": '''"cta": {{
    "CTA_TITLE": "Headline CTA urgente e persuasiva (4-8 parole)",
    "CTA_SUBTITLE": "MIN 12 parole: motiva all'azione con beneficio chiaro",
    "CTA_BUTTON_TEXT": "Verbo d'azione + risultato (3-5 parole)",
    "CTA_BUTTON_URL": "#contact"
  }}''',
    "contact": '''"contact": {{
    "CONTACT_TITLE": "Titolo sezione (invitante, NO 'Contattaci')",
    "CONTACT_SUBTITLE": "MIN 10 parole: sottotitolo che invoglia a scrivere",
    "CONTACT_ADDRESS": "indirizzo o vuoto",
    "CONTACT_PHONE": "telefono o vuoto",
    "CONTACT_EMAIL": "email o vuoto"
  }}''',
    "gallery": '''"gallery": {{
    "GALLERY_TITLE": "Titolo galleria",
    "GALLERY_SUBTITLE": "Sottotitolo",
    "GALLERY_ITEMS": [
      {{"GALLERY_IMAGE_URL": "", "GALLERY_IMAGE_ALT": "descrizione specifica", "GALLERY_CAPTION": "Didascalia evocativa"}},
      {{"GALLERY_IMAGE_URL": "", "GALLERY_IMAGE_ALT": "descrizione specifica", "GALLERY_CAPTION": "Didascalia evocativa"}},
      {{"GALLERY_IMAGE_URL": "", "GALLERY_IMAGE_ALT": "descrizione specifica", "GALLERY_CAPTION": "Didascalia evocativa"}},
      {{"GALLERY_IMAGE_URL": "", "GALLERY_IMAGE_ALT": "descrizione specifica", "GALLERY_CAPTION": "Didascalia evocativa"}},
      {{"GALLERY_IMAGE_URL": "", "GALLERY_IMAGE_ALT": "descrizione specifica", "GALLERY_CAPTION": "Didascalia evocativa"}},
      {{"GALLERY_IMAGE_URL": "", "GALLERY_IMAGE_ALT": "descrizione specifica", "GALLERY_CAPTION": "Didascalia evocativa"}}
    ]
  }}''',
    "team": '''"team": {{
    "TEAM_TITLE": "Titolo sezione team",
    "TEAM_SUBTITLE": "Sottotitolo",
    "TEAM_MEMBERS": [
      {{"MEMBER_NAME": "Nome Cognome realistico", "MEMBER_ROLE": "Ruolo specifico (es: Direttore Creativo)", "MEMBER_IMAGE_URL": "", "MEMBER_BIO": "MIN 15 parole: personalita, passioni, competenze uniche"}},
      {{"MEMBER_NAME": "Nome Cognome", "MEMBER_ROLE": "Ruolo specifico", "MEMBER_IMAGE_URL": "", "MEMBER_BIO": "MIN 15 parole: storia personale e approccio al lavoro"}},
      {{"MEMBER_NAME": "Nome Cognome", "MEMBER_ROLE": "Ruolo specifico", "MEMBER_IMAGE_URL": "", "MEMBER_BIO": "MIN 15 parole: background e contributo al team"}}
    ]
  }}''',
    "pricing": '''"pricing": {{
    "PRICING_TITLE": "Titolo sezione prezzi",
    "PRICING_SUBTITLE": "Sottotitolo",
    "PRICING_PLANS": [
      {{"PLAN_NAME": "Base", "PLAN_PRICE": "29", "PLAN_PERIOD": "/mese", "PLAN_DESCRIPTION": "Ideale per iniziare", "PLAN_FEATURES": "Feature 1, Feature 2, Feature 3", "PLAN_CTA_TEXT": "Inizia Ora", "PLAN_CTA_URL": "#contact", "PLAN_FEATURED": "false"}},
      {{"PLAN_NAME": "Pro", "PLAN_PRICE": "59", "PLAN_PERIOD": "/mese", "PLAN_DESCRIPTION": "Il piu popolare", "PLAN_FEATURES": "Tutto Base + Feature 4, Feature 5, Feature 6", "PLAN_CTA_TEXT": "Scegli Pro", "PLAN_CTA_URL": "#contact", "PLAN_FEATURED": "true"}},
      {{"PLAN_NAME": "Enterprise", "PLAN_PRICE": "99", "PLAN_PERIOD": "/mese", "PLAN_DESCRIPTION": "Per grandi aziende", "PLAN_FEATURES": "Tutto Pro + Feature 7, Feature 8, Supporto dedicato", "PLAN_CTA_TEXT": "Contattaci", "PLAN_CTA_URL": "#contact", "PLAN_FEATURED": "false"}}
    ]
  }}''',
    "faq": '''"faq": {{
    "FAQ_TITLE": "Domande Frequenti",
    "FAQ_SUBTITLE": "Sottotitolo",
    "FAQ_ITEMS": [
      {{"FAQ_QUESTION": "Domanda 1?", "FAQ_ANSWER": "Risposta dettagliata (2-3 frasi)"}},
      {{"FAQ_QUESTION": "Domanda 2?", "FAQ_ANSWER": "Risposta dettagliata"}},
      {{"FAQ_QUESTION": "Domanda 3?", "FAQ_ANSWER": "Risposta dettagliata"}},
      {{"FAQ_QUESTION": "Domanda 4?", "FAQ_ANSWER": "Risposta dettagliata"}},
      {{"FAQ_QUESTION": "Domanda 5?", "FAQ_ANSWER": "Risposta dettagliata"}}
    ]
  }}''',
    "stats": '''"stats": {{
    "STATS_TITLE": "I Nostri Numeri",
    "STATS_SUBTITLE": "Sottotitolo",
    "STATS_ITEMS": [
      {{"STAT_NUMBER": "150", "STAT_SUFFIX": "+", "STAT_LABEL": "Etichetta", "STAT_ICON": "emoji"}},
      {{"STAT_NUMBER": "98", "STAT_SUFFIX": "%", "STAT_LABEL": "Etichetta", "STAT_ICON": "emoji"}},
      {{"STAT_NUMBER": "10", "STAT_SUFFIX": "K", "STAT_LABEL": "Etichetta", "STAT_ICON": "emoji"}},
      {{"STAT_NUMBER": "24", "STAT_SUFFIX": "/7", "STAT_LABEL": "Etichetta", "STAT_ICON": "emoji"}}
    ]
  }}''',
    "logos": '''"logos": {{
    "LOGOS_TITLE": "I Nostri Partner",
    "LOGOS_ITEMS": [
      {{"LOGO_IMAGE_URL": "", "LOGO_ALT": "Partner 1", "LOGO_NAME": "Partner 1"}},
      {{"LOGO_IMAGE_URL": "", "LOGO_ALT": "Partner 2", "LOGO_NAME": "Partner 2"}},
      {{"LOGO_IMAGE_URL": "", "LOGO_ALT": "Partner 3", "LOGO_NAME": "Partner 3"}},
      {{"LOGO_IMAGE_URL": "", "LOGO_ALT": "Partner 4", "LOGO_NAME": "Partner 4"}}
    ]
  }}''',
    "process": '''"process": {{
    "PROCESS_TITLE": "Come Funziona",
    "PROCESS_SUBTITLE": "Sottotitolo",
    "PROCESS_STEPS": [
      {{"STEP_NUMBER": "1", "STEP_TITLE": "Titolo step", "STEP_DESCRIPTION": "Descrizione breve", "STEP_ICON": "emoji"}},
      {{"STEP_NUMBER": "2", "STEP_TITLE": "Titolo step", "STEP_DESCRIPTION": "Descrizione breve", "STEP_ICON": "emoji"}},
      {{"STEP_NUMBER": "3", "STEP_TITLE": "Titolo step", "STEP_DESCRIPTION": "Descrizione breve", "STEP_ICON": "emoji"}}
    ]
  }}''',
    "timeline": '''"timeline": {{
    "TIMELINE_TITLE": "La Nostra Storia",
    "TIMELINE_SUBTITLE": "Sottotitolo",
    "TIMELINE_ITEMS": [
      {{"TIMELINE_YEAR": "2020", "TIMELINE_HEADING": "Titolo", "TIMELINE_DESCRIPTION": "Descrizione evento", "TIMELINE_ICON": "emoji"}},
      {{"TIMELINE_YEAR": "2022", "TIMELINE_HEADING": "Titolo", "TIMELINE_DESCRIPTION": "Descrizione evento", "TIMELINE_ICON": "emoji"}},
      {{"TIMELINE_YEAR": "2024", "TIMELINE_HEADING": "Titolo", "TIMELINE_DESCRIPTION": "Descrizione evento", "TIMELINE_ICON": "emoji"}}
    ]
  }}''',
    "footer": '''"footer": {{
    "FOOTER_DESCRIPTION": "Breve descrizione per footer (1 frase)"
  }}''',
    "blog": '''"blog": {{
    "BLOG_TITLE": "Titolo sezione blog",
    "BLOG_SUBTITLE": "Sottotitolo",
    "BLOG_POSTS": [
      {{"POST_TITLE": "Titolo articolo (5-10 parole)", "POST_EXCERPT": "MIN 15 parole: anteprima accattivante dell'articolo", "POST_CATEGORY": "Categoria (1-2 parole)", "POST_DATE": "15 Gen 2025", "POST_AUTHOR": "Nome Cognome", "POST_IMAGE_URL": "", "POST_IMAGE_ALT": "descrizione immagine"}},
      {{"POST_TITLE": "Titolo articolo diverso", "POST_EXCERPT": "MIN 15 parole: anteprima diversa dal precedente", "POST_CATEGORY": "Categoria", "POST_DATE": "8 Gen 2025", "POST_AUTHOR": "Nome Cognome", "POST_IMAGE_URL": "", "POST_IMAGE_ALT": "descrizione immagine"}},
      {{"POST_TITLE": "Terzo titolo articolo", "POST_EXCERPT": "MIN 15 parole: anteprima unica", "POST_CATEGORY": "Categoria", "POST_DATE": "2 Gen 2025", "POST_AUTHOR": "Nome Cognome", "POST_IMAGE_URL": "", "POST_IMAGE_ALT": "descrizione immagine"}}
    ]
  }}''',
    "awards": '''"awards": {{
    "AWARDS_TITLE": "Titolo sezione premi/riconoscimenti",
    "AWARDS_SUBTITLE": "Sottotitolo",
    "AWARDS_IMAGE_1": "",
    "AWARDS_IMAGE_2": "",
    "AWARDS_IMAGE_3": "",
    "AWARDS": [
      {{"AWARD_YEAR": "2024", "AWARD_TITLE": "Nome premio", "AWARD_DESCRIPTION": "Breve descrizione del riconoscimento"}},
      {{"AWARD_YEAR": "2023", "AWARD_TITLE": "Nome premio", "AWARD_DESCRIPTION": "Breve descrizione"}},
      {{"AWARD_YEAR": "2022", "AWARD_TITLE": "Nome premio", "AWARD_DESCRIPTION": "Breve descrizione"}}
    ]
  }}''',
    "listings": '''"listings": {{
    "LISTINGS_TITLE": "Titolo sezione catalogo",
    "LISTINGS_SUBTITLE": "Sottotitolo",
    "LISTING_ITEMS": [
      {{"LISTING_TITLE": "Titolo elemento", "LISTING_DESCRIPTION": "MIN 10 parole: descrizione", "LISTING_PRICE": "\u20ac99", "LISTING_IMAGE_URL": "", "LISTING_IMAGE_ALT": "descrizione", "LISTING_SPEC_1": "Specifica 1", "LISTING_SPEC_2": "Specifica 2", "LISTING_SPEC_3": "Specifica 3"}},
      {{"LISTING_TITLE": "Titolo elemento", "LISTING_DESCRIPTION": "MIN 10 parole: descrizione", "LISTING_PRICE": "\u20ac149", "LISTING_IMAGE_URL": "", "LISTING_IMAGE_ALT": "descrizione", "LISTING_SPEC_1": "Specifica 1", "LISTING_SPEC_2": "Specifica 2", "LISTING_SPEC_3": "Specifica 3"}},
      {{"LISTING_TITLE": "Titolo elemento", "LISTING_DESCRIPTION": "MIN 10 parole: descrizione", "LISTING_PRICE": "\u20ac199", "LISTING_IMAGE_URL": "", "LISTING_IMAGE_ALT": "descrizione", "LISTING_SPEC_1": "Specifica 1", "LISTING_SPEC_2": "Specifica 2", "LISTING_SPEC_3": "Specifica 3"}}
    ]
  }}''',
    "donations": '''"donations": {{
    "DONATIONS_TITLE": "Titolo sezione donazioni",
    "DONATIONS_SUBTITLE": "Sottotitolo",
    "DONATION_ITEMS": [
      {{"DONATION_TITLE": "Nome campagna", "DONATION_DESCRIPTION": "MIN 10 parole: descrizione causa", "DONATION_RAISED": "\u20ac12.500", "DONATION_GOAL": "\u20ac25.000", "DONATION_PROGRESS": "50", "DONATION_IMAGE_URL": "", "DONATION_IMAGE_ALT": "descrizione"}},
      {{"DONATION_TITLE": "Nome campagna", "DONATION_DESCRIPTION": "MIN 10 parole: descrizione", "DONATION_RAISED": "\u20ac8.200", "DONATION_GOAL": "\u20ac15.000", "DONATION_PROGRESS": "55", "DONATION_IMAGE_URL": "", "DONATION_IMAGE_ALT": "descrizione"}}
    ]
  }}''',
    "comparison": '''"comparison": {{
    "COMPARISON_TITLE": "Perche Scegliere Noi",
    "COMPARISON_SUBTITLE": "Sottotitolo confronto",
    "COMPARISON_BRAND_NAME": "Il Nostro Brand",
    "COMPARISON_ITEMS": [
      {{"COMPARISON_FEATURE": "Feature 1", "COMPARISON_US": "true", "COMPARISON_OTHERS": "false"}},
      {{"COMPARISON_FEATURE": "Feature 2", "COMPARISON_US": "true", "COMPARISON_OTHERS": "false"}},
      {{"COMPARISON_FEATURE": "Feature 3", "COMPARISON_US": "true", "COMPARISON_OTHERS": "true"}},
      {{"COMPARISON_FEATURE": "Feature 4", "COMPARISON_US": "true", "COMPARISON_OTHERS": "false"}},
      {{"COMPARISON_FEATURE": "Feature 5", "COMPARISON_US": "true", "COMPARISON_OTHERS": "false"}}
    ],
    "COMPARISON_CTA_TEXT": "Inizia Ora",
    "COMPARISON_CTA_URL": "#contact"
  }}''',
    "booking": '''"booking": {{
    "BOOKING_TITLE": "Prenota un Appuntamento",
    "BOOKING_SUBTITLE": "Sottotitolo",
    "BOOKING_DESCRIPTION": "MIN 15 parole: descrizione del servizio di prenotazione",
    "BOOKING_PHONE": "telefono o vuoto",
    "BOOKING_EMAIL": "email o vuoto",
    "BOOKING_HOURS": "Lun-Ven: 9:00-18:00",
    "BOOKING_SERVICE_LABEL": "Seleziona Servizio",
    "BOOKING_NOTES_LABEL": "Note Aggiuntive",
    "BOOKING_BUTTON_TEXT": "Prenota Ora"
  }}''',
    "app-download": '''"app-download": {{
    "APP_TITLE": "Scarica la Nostra App",
    "APP_SUBTITLE": "MIN 10 parole: sottotitolo che invoglia al download",
    "APP_FEATURES": [
      {{"APP_FEATURE_TEXT": "Feature 1 dell'app"}},
      {{"APP_FEATURE_TEXT": "Feature 2 dell'app"}},
      {{"APP_FEATURE_TEXT": "Feature 3 dell'app"}}
    ],
    "APP_IMAGE_URL": "",
    "APP_STORE_URL": "#",
    "APP_PLAY_URL": "#"
  }}''',
    "social-proof": '''"social-proof": {{
    "SOCIAL_TITLE": "I Nostri Numeri Parlano",
    "SOCIAL_ITEMS": [
      {{"SOCIAL_ICON": "emoji", "SOCIAL_COUNT": "10K", "SOCIAL_LABEL": "Followers"}},
      {{"SOCIAL_ICON": "emoji", "SOCIAL_COUNT": "500", "SOCIAL_LABEL": "Progetti"}},
      {{"SOCIAL_ICON": "emoji", "SOCIAL_COUNT": "98%", "SOCIAL_LABEL": "Soddisfazione"}},
      {{"SOCIAL_ICON": "emoji", "SOCIAL_COUNT": "24/7", "SOCIAL_LABEL": "Supporto"}}
    ]
  }}''',
    "schedule": '''"schedule": {{
    "SCHEDULE_TITLE": "Programma",
    "SCHEDULE_SUBTITLE": "Sottotitolo",
    "SCHEDULE_ITEMS": [
      {{"SCHEDULE_TIME": "09:00", "SCHEDULE_TITLE": "Titolo sessione", "SCHEDULE_SPEAKER": "Nome Speaker", "SCHEDULE_DESCRIPTION": "Breve descrizione"}},
      {{"SCHEDULE_TIME": "10:30", "SCHEDULE_TITLE": "Titolo sessione", "SCHEDULE_SPEAKER": "Nome Speaker", "SCHEDULE_DESCRIPTION": "Breve descrizione"}},
      {{"SCHEDULE_TIME": "14:00", "SCHEDULE_TITLE": "Titolo sessione", "SCHEDULE_SPEAKER": "Nome Speaker", "SCHEDULE_DESCRIPTION": "Breve descrizione"}}
    ]
  }}''',
}

# Map array keys for dynamic structure-rule generation
SECTION_ARRAY_RULES: Dict[str, str] = {
    "services": 'The "SERVICES" key MUST be an array of objects with EXACTLY: "SERVICE_ICON", "SERVICE_TITLE", "SERVICE_DESCRIPTION". At LEAST 3 items.',
    "features": 'The "FEATURES" key MUST be an array of objects with EXACTLY: "FEATURE_ICON", "FEATURE_TITLE", "FEATURE_DESCRIPTION". At LEAST 4 items.',
    "testimonials": 'The "TESTIMONIALS" key MUST be an array of objects with EXACTLY: "TESTIMONIAL_TEXT", "TESTIMONIAL_AUTHOR", "TESTIMONIAL_ROLE", "TESTIMONIAL_INITIAL". At LEAST 3 items.',
    "gallery": 'The "GALLERY_ITEMS" key MUST be an array of objects with EXACTLY: "GALLERY_IMAGE_URL", "GALLERY_IMAGE_ALT", "GALLERY_CAPTION". At LEAST 4 items.',
    "team": 'The "TEAM_MEMBERS" key MUST be an array of objects with EXACTLY: "MEMBER_NAME", "MEMBER_ROLE", "MEMBER_IMAGE_URL", "MEMBER_BIO". At LEAST 3 items.',
    "blog": 'The "BLOG_POSTS" key MUST be an array of objects with EXACTLY: "POST_TITLE", "POST_EXCERPT", "POST_CATEGORY", "POST_DATE", "POST_AUTHOR", "POST_IMAGE_URL", "POST_IMAGE_ALT". At LEAST 3 items.',
    "awards": 'The "AWARDS" key MUST be an array of objects with EXACTLY: "AWARD_YEAR", "AWARD_TITLE", "AWARD_DESCRIPTION". At LEAST 3 items.',
    "listings": 'The "LISTING_ITEMS" key MUST be an array of objects with EXACTLY: "LISTING_TITLE", "LISTING_DESCRIPTION", "LISTING_PRICE", "LISTING_IMAGE_URL", "LISTING_IMAGE_ALT", "LISTING_SPEC_1", "LISTING_SPEC_2", "LISTING_SPEC_3". At LEAST 3 items.',
    "donations": 'The "DONATION_ITEMS" key MUST be an array of objects with EXACTLY: "DONATION_TITLE", "DONATION_DESCRIPTION", "DONATION_RAISED", "DONATION_GOAL", "DONATION_PROGRESS", "DONATION_IMAGE_URL", "DONATION_IMAGE_ALT". At LEAST 2 items.',
    "comparison": 'The "COMPARISON_ITEMS" key MUST be an array of objects with EXACTLY: "COMPARISON_FEATURE", "COMPARISON_US", "COMPARISON_OTHERS". At LEAST 4 items.',
    "social-proof": 'The "SOCIAL_ITEMS" key MUST be an array of objects with EXACTLY: "SOCIAL_ICON", "SOCIAL_COUNT", "SOCIAL_LABEL". At LEAST 3 items.',
    "schedule": 'The "SCHEDULE_ITEMS" key MUST be an array of objects with EXACTLY: "SCHEDULE_TIME", "SCHEDULE_TITLE", "SCHEDULE_SPEAKER", "SCHEDULE_DESCRIPTION". At LEAST 3 items.',
    "app-download": 'The "APP_FEATURES" key MUST be an array of objects with EXACTLY: "APP_FEATURE_TEXT". At LEAST 3 items.',
}

# Synonym map: maps common AI key variations to canonical suffixes.
# Used by _normalize_item_keys to catch any creative key naming the AI uses.
KEY_SYNONYMS: Dict[str, str] = {
    # ICON synonyms
    "ICON": "ICON",
    "EMOJI": "ICON",
    "ICONA": "ICON",
    "SYMBOL": "ICON",
    "SIMBOLO": "ICON",
    "IMAGE": "ICON",  # fallback: if no IMAGE_URL field, treat as icon
    # TITLE synonyms
    "TITLE": "TITLE",
    "TITOLO": "TITLE",
    "NAME": "TITLE",
    "NOME": "TITLE",
    "HEADING": "TITLE",
    "LABEL": "TITLE",
    "TITL": "TITLE",
    # DESCRIPTION synonyms
    "DESCRIPTION": "DESCRIPTION",
    "DESCRIZIONE": "DESCRIPTION",
    "DESC": "DESCRIPTION",
    "TEXT": "DESCRIPTION",
    "TESTO": "DESCRIPTION",
    "BODY": "DESCRIPTION",
    "CONTENT": "DESCRIPTION",
    "DETAIL": "DESCRIPTION",
    "DETAILS": "DESCRIPTION",
    "SUMMARY": "DESCRIPTION",
    # CTA synonyms
    "CTA": "CTA",
    "CTA_TEXT": "CTA",
    "LINK": "CTA",
    "LINK_TEXT": "CTA",
    "BUTTON": "CTA",
    "BUTTON_TEXT": "CTA",
    # AUTHOR synonyms (for testimonials)
    "AUTHOR": "AUTHOR",
    "AUTORE": "AUTHOR",
    "WRITER": "AUTHOR",
    # ROLE synonyms (for testimonials)
    "ROLE": "ROLE",
    "RUOLO": "ROLE",
    "JOB": "ROLE",
    "POSITION": "ROLE",
    "JOB_TITLE": "ROLE",
    # INITIAL synonyms (for testimonials)
    "INITIAL": "INITIAL",
    "INIZIALE": "INITIAL",
    "AVATAR": "INITIAL",
    # IMAGE_URL synonyms
    "IMAGE_URL": "IMAGE_URL",
    "IMG_URL": "IMAGE_URL",
    "PHOTO": "IMAGE_URL",
    "FOTO": "IMAGE_URL",
    "PHOTO_URL": "IMAGE_URL",
    "IMAGE_SRC": "IMAGE_URL",
    # IMAGE_ALT synonyms
    "IMAGE_ALT": "IMAGE_ALT",
    "IMG_ALT": "IMAGE_ALT",
    "ALT": "IMAGE_ALT",
    "ALT_TEXT": "IMAGE_ALT",
    # CAPTION synonyms
    "CAPTION": "CAPTION",
    "DIDASCALIA": "CAPTION",
    # BIO synonyms
    "BIO": "BIO",
    "BIOGRAFIA": "BIO",
    "ABOUT": "BIO",
    # NUMBER/NUM synonyms (for stats)
    "NUMBER": "NUMBER",
    "NUM": "NUMBER",
    "NUMERO": "NUMBER",
    "VALUE": "NUMBER",
    "VALORE": "NUMBER",
    # SUFFIX synonyms (for stats)
    "SUFFIX": "SUFFIX",
    "SUFFISSO": "SUFFIX",
    "UNIT": "SUFFIX",
    # QUESTION/ANSWER synonyms (for FAQ)
    "QUESTION": "QUESTION",
    "DOMANDA": "QUESTION",
    "Q": "QUESTION",
    "ANSWER": "ANSWER",
    "RISPOSTA": "ANSWER",
    "A": "ANSWER",
    # YEAR synonyms (for timeline)
    "YEAR": "YEAR",
    "ANNO": "YEAR",
    "DATE": "YEAR",
    "DATA": "YEAR",
    "PERIOD": "YEAR",
    # HEADING synonym (for timeline)
    "HEADING": "HEADING",
    # STEP fields
    "STEP_NUMBER": "NUMBER",
    "STEP_TITLE": "TITLE",
    "STEP_DESCRIPTION": "DESCRIPTION",
}
