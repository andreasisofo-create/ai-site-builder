"""Variety Engine pools for creative direction diversity.

Each generation randomly picks from these pools to ensure
every site feels unique even for the same template style.
Pools include personality archetypes, color mood presets,
font pairings, and fallback theme palettes.
"""

from typing import Dict, List, Any


# Creative personality archetypes that shape ALL copy tone
PERSONALITY_POOL: List[Dict[str, str]] = [
    {
        "name": "provocative",
        "directive": "You are PROVOCATIVE. Challenge assumptions. Use contrasts, paradoxes, and unexpected juxtapositions. 'Il Caos che Crea Ordine'. Make the reader stop and think.",
        "headline_style": "contrasting, paradoxical, thought-provoking",
    },
    {
        "name": "poetic",
        "directive": "You are POETIC. Write like a modern poet. Use metaphors drawn from nature, art, and human emotion. 'Dove il Vento Incontra la Pietra'. Rhythm matters — alternate short and flowing.",
        "headline_style": "lyrical, metaphorical, evocative",
    },
    {
        "name": "minimal",
        "directive": "You are MINIMALIST. Less is everything. Each word is surgical. No adjective without purpose. 'Meno. Meglio.' White space is your friend. Think Dieter Rams meets copywriting.",
        "headline_style": "ultra-short, punchy, stark",
    },
    {
        "name": "bold",
        "directive": "You are BOLD and LOUD. Capital energy. Confidence that borders on audacity. 'Noi Non Seguiamo Tendenze. Le Creiamo.' Every sentence should feel like a manifesto.",
        "headline_style": "declarative, confident, manifesto-like",
    },
    {
        "name": "storytelling",
        "directive": "You are a STORYTELLER. Every section is a chapter. Create narrative tension — hint at a journey, a transformation, a before/after. 'C era un Vuoto. Poi Siamo Arrivati Noi.' Hook the reader emotionally.",
        "headline_style": "narrative, hook-driven, emotional arc",
    },
    {
        "name": "data-driven",
        "directive": "You are DATA-DRIVEN. Lead with proof, numbers, evidence. '847 Progetti. Zero Compromessi.' Use specific numbers, percentages, timeframes. Credibility through precision.",
        "headline_style": "numbers-first, evidence-based, precise",
    },
    {
        "name": "emotional",
        "directive": "You are DEEPLY EMOTIONAL. Write from the heart. What does the customer FEEL? Fear of missing out? Joy of discovery? Relief? 'Finalmente, Qualcuno Che Capisce.' Touch nerves.",
        "headline_style": "empathetic, feelings-first, intimate",
    },
    {
        "name": "visionary",
        "directive": "You are a VISIONARY. Write from the future. Paint a picture of what could be. 'Il Futuro Non Aspetta. Noi Nemmeno.' Aspirational, forward-looking, transformative.",
        "headline_style": "future-oriented, aspirational, transformative",
    },
    {
        "name": "irreverent",
        "directive": "You are IRREVERENT. Break the mold. Use unexpected humor, informal tone, and anti-corporate language. 'Basta Siti Noiosi.' Be the brand that winks at the reader.",
        "headline_style": "witty, informal, rule-breaking",
    },
    {
        "name": "luxurious",
        "directive": "You are LUXURIOUS. Every word drips exclusivity. Understated elegance. 'Per Chi Non Si Accontenta.' Use words like esclusivo, raffinato, senza tempo, artigianale. Appeal to taste, not price.",
        "headline_style": "refined, exclusive, understated elegance",
    },
    {
        "name": "scientific",
        "directive": "You are SCIENTIFIC. Precision meets clarity. Explain complex things simply. 'La Scienza Dietro Ogni Dettaglio.' Use structured arguments, cause-effect chains, and evidence.",
        "headline_style": "analytical, precise, clarity-first",
    },
    {
        "name": "warm",
        "directive": "You are WARM and HUMAN. Write like a trusted friend giving honest advice. 'Ti Meriti di Meglio.' Conversational, genuine, zero corporate veneer. Use 'tu' form naturally.",
        "headline_style": "conversational, genuine, friendly",
    },
]

# Color mood presets — injected into theme prompt to push the AI toward diverse palettes
COLOR_MOOD_POOL: List[Dict[str, str]] = [
    {"mood": "Sunset Warmth", "hint": "Think golden hour: amber #F59E0B, terracotta #C2410C, warm cream #FFFBEB, deep mahogany #7C2D12. Warm, inviting, organic."},
    {"mood": "Ocean Depth", "hint": "Think deep sea: teal #0D9488, navy #0C4A6E, seafoam #CCFBF1, coral accent #FB7185. Cool, professional, trustworthy."},
    {"mood": "Forest Calm", "hint": "Think ancient forest: emerald #059669, sage #D1FAE5, bark brown #78350F, golden light #FDE68A. Natural, grounded, sustainable."},
    {"mood": "Electric Night", "hint": "Think neon city: electric purple #A855F7, hot pink #EC4899, dark navy #0F172A, cyan spark #22D3EE. Bold, modern, energetic."},
    {"mood": "Desert Minimal", "hint": "Think desert sand: sand #D4A574, terracotta #9A3412, bone white #FEF3C7, indigo sky #4338CA. Earthy, warm, Mediterranean."},
    {"mood": "Nordic Clean", "hint": "Think Scandinavian: slate blue #475569, ice white #F8FAFC, pine green #166534, blush #FECDD3. Clean, crisp, functional."},
    {"mood": "Art Deco Luxe", "hint": "Think 1920s glamour: gold #D4AF37, black #1C1917, cream #FFFDD0, emerald #047857. Opulent, dramatic, sophisticated."},
    {"mood": "Candy Pop", "hint": "Think playful: bubblegum #F472B6, lavender #C4B5FD, mint #A7F3D0, sunny yellow #FDE047. Fun, youthful, creative."},
    {"mood": "Monochrome Power", "hint": "Think high contrast: charcoal #1E293B, silver #CBD5E1, white #FFFFFF, one vivid accent (red #EF4444 OR orange #F97316). Powerful, dramatic, sophisticated."},
    {"mood": "Terracotta Earth", "hint": "Think Italian countryside: burnt sienna #A0522D, olive #808000, cream #FAF0E6, dusty rose #BC8F8F. Warm, artisanal, authentic."},
    {"mood": "Cyber Fresh", "hint": "Think tech startup: lime #84CC16, dark slate #1E1B4B, electric blue #3B82F6, white #F5F5F5. Fresh, innovative, dynamic."},
    {"mood": "Royal Velvet", "hint": "Think regal: deep burgundy #831843, royal purple #581C87, gold #B8860B, ivory #FFFFF0. Rich, prestigious, commanding."},
]

# Extended font pairings pool — more options to reduce repetition
FONT_PAIRING_POOL: List[Dict[str, str]] = [
    {"heading": "Playfair Display", "body": "Inter", "personality": "ELEGANT/LUXURY", "url_h": "Playfair+Display:wght@400;600;700;800", "url_b": "Inter:wght@400;500;600"},
    {"heading": "Space Grotesk", "body": "DM Sans", "personality": "MODERN TECH/SAAS", "url_h": "Space+Grotesk:wght@400;600;700", "url_b": "DM+Sans:wght@400;500;600"},
    {"heading": "Sora", "body": "Inter", "personality": "CLEAN STARTUP", "url_h": "Sora:wght@400;600;700;800", "url_b": "Inter:wght@400;500;600"},
    {"heading": "DM Serif Display", "body": "Plus Jakarta Sans", "personality": "EDITORIAL/BLOG", "url_h": "DM+Serif+Display:wght@400", "url_b": "Plus+Jakarta+Sans:wght@400;500;600;700"},
    {"heading": "Outfit", "body": "DM Sans", "personality": "GEOMETRIC MODERN", "url_h": "Outfit:wght@400;600;700;800", "url_b": "DM+Sans:wght@400;500;600"},
    {"heading": "Fraunces", "body": "Nunito Sans", "personality": "WARM ARTISAN", "url_h": "Fraunces:wght@400;600;700;800", "url_b": "Nunito+Sans:wght@400;500;600;700"},
    {"heading": "Epilogue", "body": "Source Sans 3", "personality": "PROFESSIONAL", "url_h": "Epilogue:wght@400;600;700;800", "url_b": "Source+Sans+3:wght@400;500;600"},
    {"heading": "Bricolage Grotesque", "body": "Inter", "personality": "PLAYFUL MODERN", "url_h": "Bricolage+Grotesque:wght@400;600;700;800", "url_b": "Inter:wght@400;500;600"},
    {"heading": "Instrument Serif", "body": "Instrument Sans", "personality": "REFINED EDITORIAL", "url_h": "Instrument+Serif:wght@400", "url_b": "Instrument+Sans:wght@400;500;600;700"},
    {"heading": "Libre Baskerville", "body": "Karla", "personality": "CLASSIC LITERARY", "url_h": "Libre+Baskerville:wght@400;700", "url_b": "Karla:wght@400;500;600;700"},
    {"heading": "Unbounded", "body": "Figtree", "personality": "FUTURISTIC BOLD", "url_h": "Unbounded:wght@400;600;700;800;900", "url_b": "Figtree:wght@400;500;600;700"},
    {"heading": "Cormorant Garamond", "body": "Lato", "personality": "TIMELESS LUXURY", "url_h": "Cormorant+Garamond:wght@400;600;700", "url_b": "Lato:wght@400;700"},
    {"heading": "Archivo Black", "body": "Work Sans", "personality": "IMPACT INDUSTRIAL", "url_h": "Archivo+Black", "url_b": "Work+Sans:wght@400;500;600"},
    {"heading": "Josefin Sans", "body": "Mulish", "personality": "SLEEK GEOMETRIC", "url_h": "Josefin+Sans:wght@400;600;700", "url_b": "Mulish:wght@400;500;600;700"},
    {"heading": "Bitter", "body": "Poppins", "personality": "WARM PROFESSIONAL", "url_h": "Bitter:wght@400;600;700;800", "url_b": "Poppins:wght@400;500;600"},
    {"heading": "Albert Sans", "body": "IBM Plex Sans", "personality": "SWISS CLEAN", "url_h": "Albert+Sans:wght@400;600;700;800", "url_b": "IBM+Plex+Sans:wght@400;500;600"},
]

# Fallback theme palettes — used when AI fails, each is distinct
FALLBACK_THEME_POOL: List[Dict[str, str]] = [
    {
        "primary_color": "#7C3AED", "secondary_color": "#1E3A5F", "accent_color": "#F59E0B",
        "bg_color": "#FAF7F2", "bg_alt_color": "#F0EDE6", "text_color": "#1A1A2E", "text_muted_color": "#6B7280",
        "font_heading": "Space Grotesk", "font_heading_url": "Space+Grotesk:wght@400;600;700;800",
        "font_body": "DM Sans", "font_body_url": "DM+Sans:wght@400;500;600",
        "border_radius_style": "soft", "shadow_style": "soft", "spacing_density": "normal",
    },
    {
        "primary_color": "#0D9488", "secondary_color": "#0C4A6E", "accent_color": "#FB7185",
        "bg_color": "#F0FDFA", "bg_alt_color": "#CCFBF1", "text_color": "#0F172A", "text_muted_color": "#64748B",
        "font_heading": "Sora", "font_heading_url": "Sora:wght@400;600;700;800",
        "font_body": "Inter", "font_body_url": "Inter:wght@400;500;600",
        "border_radius_style": "pill", "shadow_style": "soft", "spacing_density": "normal",
    },
    {
        "primary_color": "#DC2626", "secondary_color": "#1E293B", "accent_color": "#FBBF24",
        "bg_color": "#FFFBEB", "bg_alt_color": "#FEF3C7", "text_color": "#1C1917", "text_muted_color": "#78716C",
        "font_heading": "DM Serif Display", "font_heading_url": "DM+Serif+Display:wght@400",
        "font_body": "Plus Jakarta Sans", "font_body_url": "Plus+Jakarta+Sans:wght@400;500;600;700",
        "border_radius_style": "sharp", "shadow_style": "none", "spacing_density": "compact",
    },
    {
        "primary_color": "#059669", "secondary_color": "#78350F", "accent_color": "#F472B6",
        "bg_color": "#ECFDF5", "bg_alt_color": "#D1FAE5", "text_color": "#064E3B", "text_muted_color": "#6B7280",
        "font_heading": "Fraunces", "font_heading_url": "Fraunces:wght@400;600;700;800",
        "font_body": "Nunito Sans", "font_body_url": "Nunito+Sans:wght@400;500;600;700",
        "border_radius_style": "round", "shadow_style": "soft", "spacing_density": "generous",
    },
    {
        "primary_color": "#7C2D12", "secondary_color": "#4338CA", "accent_color": "#22D3EE",
        "bg_color": "#FEF3C7", "bg_alt_color": "#FDE68A", "text_color": "#1C1917", "text_muted_color": "#92400E",
        "font_heading": "Playfair Display", "font_heading_url": "Playfair+Display:wght@400;600;700;800",
        "font_body": "Lato", "font_body_url": "Lato:wght@400;700",
        "border_radius_style": "soft", "shadow_style": "dramatic", "spacing_density": "generous",
    },
    {
        "primary_color": "#A855F7", "secondary_color": "#EC4899", "accent_color": "#22D3EE",
        "bg_color": "#0F172A", "bg_alt_color": "#1E293B", "text_color": "#F1F5F9", "text_muted_color": "#CBD5E1",
        "font_heading": "Outfit", "font_heading_url": "Outfit:wght@400;600;700;800",
        "font_body": "DM Sans", "font_body_url": "DM+Sans:wght@400;500;600",
        "border_radius_style": "pill", "shadow_style": "dramatic", "spacing_density": "normal",
    },
    {
        "primary_color": "#B8860B", "secondary_color": "#1C1917", "accent_color": "#047857",
        "bg_color": "#FFFDD0", "bg_alt_color": "#FEF9C3", "text_color": "#1C1917", "text_muted_color": "#78716C",
        "font_heading": "Cormorant Garamond", "font_heading_url": "Cormorant+Garamond:wght@400;600;700",
        "font_body": "Lato", "font_body_url": "Lato:wght@400;700",
        "border_radius_style": "soft", "shadow_style": "soft", "spacing_density": "generous",
    },
    {
        "primary_color": "#831843", "secondary_color": "#581C87", "accent_color": "#FBBF24",
        "bg_color": "#FFFFF0", "bg_alt_color": "#FEF3C7", "text_color": "#1E1B4B", "text_muted_color": "#6B7280",
        "font_heading": "Libre Baskerville", "font_heading_url": "Libre+Baskerville:wght@400;700",
        "font_body": "Karla", "font_body_url": "Karla:wght@400;500;600;700",
        "border_radius_style": "round", "shadow_style": "none", "spacing_density": "normal",
    },
]

# Few-shot examples: Award-winning Italian copy per category.
# Injected into _generate_texts() so the AI sees CONCRETE
# examples of the quality level expected. 2 examples each.
FEW_SHOT_EXAMPLES: Dict[str, List[Dict[str, Any]]] = {
    "restaurant": [
        {
            "hero_title": "Dove il Tempo si Ferma a Tavola",
            "hero_subtitle": (
                "Ogni piatto nasce da un dialogo silenzioso tra la terra e le mani "
                "dello chef. Non serviamo cena — creiamo il ricordo che racconterai domani. "
                "Stagionalita' radicale, zero compromessi."
            ),
            "service_title": "Il Rituale del Fuoco",
            "service_description": (
                "Cotture lente su brace di quercia centenaria. 14 ore di pazienza per "
                "trasformare un taglio umile in qualcosa che non dimenticherai. La fiamma "
                "non ha fretta, e nemmeno noi."
            ),
            "testimonial": (
                "Ho chiuso gli occhi al primo boccone e ho rivisto la cucina di mia nonna "
                "a Matera. Non succedeva da vent'anni. Mia moglie dice che ho pianto — "
                "io dico che era il pepe. Ci torniamo ogni anniversario, ormai e' tradizione."
            ),
        },
        {
            "hero_title": "Sapori Che Raccontano Storie",
            "hero_subtitle": (
                "Trentadue ingredienti locali, sette fornitori che conosciamo per nome, "
                "un menu che cambia quando cambia il vento. Cucina d'autore che sa di casa, "
                "non di pretesa."
            ),
            "service_title": "L'Orto Segreto",
            "service_description": (
                "A 400 metri dal ristorante, il nostro orto biodinamico detta il menu. "
                "Quello che raccogliamo la mattina, lo serviamo la sera. Nessun intermediario "
                "tra la radice e il tuo piatto."
            ),
            "testimonial": (
                "Siamo arrivati per caso, sotto la pioggia, senza prenotazione. Tre ore dopo "
                "stavamo brindando col sommelier come vecchi amici. Il risotto allo zafferano "
                "dell'orto? Ancora ci penso, a distanza di sei mesi."
            ),
        },
    ],
    "saas": [
        {
            "hero_title": "Meno Caos. Piu' Risultati.",
            "hero_subtitle": (
                "Il tuo team perde 23 ore a settimana in task ripetitivi. "
                "Noi le restituiamo. Automazione intelligente che si adatta al tuo flusso, "
                "non il contrario. Setup in 4 minuti, ROI dal primo giorno."
            ),
            "service_title": "Automazione Predittiva",
            "service_description": (
                "L'AI analizza 10.000 pattern nel tuo workflow e anticipa i colli di bottiglia "
                "prima che esistano. Non reagire ai problemi — previenili. "
                "I nostri clienti riducono i ritardi del 67% nel primo trimestre."
            ),
            "testimonial": (
                "Prima gestivamo 200 ticket al giorno con 8 persone. Ora ne gestiamo 340 "
                "con 5. Non e' magia — e' che finalmente il software lavora PER noi, "
                "non CONTRO di noi. Il team e' tornato a fare il lavoro che conta."
            ),
        },
        {
            "hero_title": "847 Progetti. Zero Compromessi.",
            "hero_subtitle": (
                "Ogni feature nasce da un problema reale, non da una slide. "
                "Dashboard che parla la tua lingua, integrazioni che funzionano al primo click, "
                "supporto che risponde in 90 secondi. Provalo gratis, poi decidi."
            ),
            "service_title": "Dashboard Viva",
            "service_description": (
                "Dimentica i report statici di fine mese. La nostra dashboard si aggiorna "
                "in tempo reale, evidenzia anomalie con alert intelligenti e suggerisce "
                "azioni correttive. I tuoi dati, finalmente, parlano chiaro."
            ),
            "testimonial": (
                "Ho convinto il CEO con un solo screenshot della dashboard. In 30 secondi "
                "ha visto quello che prima richiedeva 3 riunioni e un foglio Excel da incubo. "
                "Budget approvato in giornata — mai successo prima."
            ),
        },
    ],
    "portfolio": [
        {
            "hero_title": "Ogni Pixel Ha un Perche'",
            "hero_subtitle": (
                "Non creo siti web. Creo sistemi visivi che trasformano visitatori distratti "
                "in clienti convinti. 12 anni di ossessione per il dettaglio, "
                "47 brand reinventati, zero template riciclati."
            ),
            "service_title": "Brand Identity Radicale",
            "service_description": (
                "Parto da chi sei veramente, non da chi vorresti sembrare. Interviste, "
                "analisi competitiva, moodboard che sfidano — e poi il logo arriva come "
                "una conseguenza naturale, non come una decorazione."
            ),
            "testimonial": (
                "Gli ho detto 'voglio qualcosa di diverso' aspettandomi il solito moodboard "
                "su Pinterest. Mi ha presentato un manifesto di 12 pagine sulla mia azienda "
                "che nemmeno io avrei saputo scrivere. Il rebranding ha aumentato "
                "le conversioni del 180%."
            ),
        },
        {
            "hero_title": "Design Senza Compromessi",
            "hero_subtitle": (
                "Tre regole: funziona, emoziona, dura. Il bello senza sostanza e' decorazione. "
                "La sostanza senza bellezza e' un foglio Excel. "
                "Io cerco il punto esatto dove si incontrano."
            ),
            "service_title": "UX Che Respira",
            "service_description": (
                "Ogni interfaccia che disegno viene testata con utenti reali prima di "
                "vedere la luce. Prototipi interattivi, A/B test, heatmap. "
                "Il design bello che nessuno usa e' solo arte — io faccio strumenti."
            ),
            "testimonial": (
                "Il nostro e-commerce aveva un tasso di abbandono carrello del 78%. "
                "Dopo il redesign, e' sceso al 31%. Non ha cambiato i colori — ha ripensato "
                "l'intero percorso dell'utente. Numeri che parlano."
            ),
        },
    ],
    "ecommerce": [
        {
            "hero_title": "Non Compri un Oggetto. Scegli Chi Vuoi Essere.",
            "hero_subtitle": (
                "Ogni pezzo della collezione nasce da 200 ore di artigianato e una domanda: "
                "'Lo terrai per sempre?'. Materiali che invecchiano con grazia, "
                "design che non segue le stagioni ma le anticipa."
            ),
            "service_title": "Pelle Che Racconta",
            "service_description": (
                "Conceria toscana, concia vegetale, 18 mesi di stagionatura. "
                "Ogni borsa porta i segni del suo viaggio — graffi, patina, carattere. "
                "Non la sostituirai. La erediterai."
            ),
            "testimonial": (
                "Ho aperto la scatola e ho sentito l'odore del cuoio prima ancora di vederla. "
                "La uso ogni giorno da 14 mesi e la pelle ha preso un colore ambrato "
                "che non esisteva all'inizio. E' diventata piu' bella con il tempo, come "
                "dovrebbero essere tutte le cose."
            ),
        },
        {
            "hero_title": "Il Lusso e' nella Scelta Consapevole",
            "hero_subtitle": (
                "Zero fast fashion, zero sovrapproduzione. Edizioni limitate da 50 pezzi, "
                "tessuti certificati, filiera trasparente dal filo al bottone. "
                "Quando scegli qualita', il pianeta ringrazia."
            ),
            "service_title": "Spedizione Rituale",
            "service_description": (
                "Packaging in carta riciclata con sigillo in ceralacca, biglietto scritto "
                "a mano, sacchetto in cotone organico. L'esperienza inizia "
                "dall'apertura della scatola, non dall'indossare il capo."
            ),
            "testimonial": (
                "Mia figlia mi ha chiesto perche' quella maglietta costava 'cosi' tanto'. "
                "Le ho fatto toccare il tessuto, leggere l'etichetta, sentire la differenza. "
                "Ora e' lei che non vuole piu' comprare fast fashion. "
                "Investimento migliore della mia vita."
            ),
        },
    ],
    "business": [
        {
            "hero_title": "Costruiamo il Domani. Oggi.",
            "hero_subtitle": (
                "In 15 anni abbiamo accompagnato 340 aziende dalla visione all'esecuzione. "
                "Non vendiamo consulenza — costruiamo ponti tra dove sei "
                "e dove il mercato ti aspetta. Risultati misurabili, non presentazioni."
            ),
            "service_title": "Strategia Operativa",
            "service_description": (
                "Basta piani strategici che finiscono in un cassetto. Il nostro metodo "
                "traduce la visione in sprint da 90 giorni con KPI chiari, owner definiti "
                "e review settimanali. La strategia funziona solo se cammina."
            ),
            "testimonial": (
                "Avevamo provato 3 societa' di consulenza in 5 anni. Slide bellissime, "
                "risultati zero. Questi sono entrati in azienda il lunedi' e il venerdi' "
                "avevamo gia' il primo processo ottimizzato. Il fatturato e' cresciuto "
                "del 34% in 8 mesi. Niente magia — metodo."
            ),
        },
        {
            "hero_title": "Dove Nasce il Cambiamento",
            "hero_subtitle": (
                "Il mercato non aspetta chi esita. Analisi predittiva, "
                "trasformazione digitale e un team che ha detto 'no' a 200 clienti "
                "per dire 'si' a quelli giusti. La tua crescita e' la nostra reputazione."
            ),
            "service_title": "Digital Acceleration",
            "service_description": (
                "Audit completo in 72 ore, roadmap personalizzata in 2 settimane, "
                "primi risultati in 30 giorni. Non digitalizziamo processi rotti — "
                "li ripensiamo da zero e poi li automatizziamo."
            ),
            "testimonial": (
                "Il nostro settore era fermo agli anni '90. Processi cartacei, Excel ovunque, "
                "decisioni a intuito. In 6 mesi ci hanno portato nel 2024. "
                "I dipendenti che resistevano al cambiamento ora sono i piu' entusiasti. "
                "Questo vale piu' di qualsiasi ROI."
            ),
        },
    ],
    "blog": [
        {
            "hero_title": "Le Idee Che Cambiano le Regole",
            "hero_subtitle": (
                "Non un altro blog di settore. Un laboratorio di pensiero dove "
                "le certezze vengono smontate, le tendenze anticipate e le domande "
                "scomode trovano risposte scomode. Leggi solo se vuoi cambiare idea."
            ),
            "service_title": "Deep Dive Settimanale",
            "service_description": (
                "Ogni giovedi', un'analisi di 2.000 parole che spacca un tema in due. "
                "Dati originali, interviste esclusive, zero riciclo di comunicati stampa. "
                "Il tipo di articolo che salvi nei preferiti e condividi con il team."
            ),
            "testimonial": (
                "Ho smesso di leggere newsletter due anni fa. Questa e' l'unica che apro "
                "il giovedi' mattina prima del caffe'. L'articolo sulla disruption del retail "
                "l'ho fatto leggere a tutto il board. Ha cambiato la nostra strategia Q3."
            ),
        },
        {
            "hero_title": "Pensiero Critico, Zero Filtri",
            "hero_subtitle": (
                "47.000 lettori che preferiscono la verita' scomoda alla rassicurazione facile. "
                "Analisi controcorrente, dati che contraddicono i titoli, "
                "prospettive che nessun altro osa pubblicare."
            ),
            "service_title": "Il Contrarian Report",
            "service_description": (
                "Una volta al mese prendiamo la narrativa dominante del settore "
                "e la mettiamo alla prova dei fatti. Con dati, fonti, e il coraggio "
                "di dire quello che tutti pensano ma nessuno scrive."
            ),
            "testimonial": (
                "L'analisi sul fallimento delle startup 'purpose-driven' mi ha fatto "
                "ripensare l'intero pitch deck. Scomodo? Si'. Necessario? Assolutamente. "
                "E' il blog che leggo per non restare nella bolla."
            ),
        },
    ],
    "event": [
        {
            "hero_title": "Non Partecipare. Vivi.",
            "hero_subtitle": (
                "12 ore che comprimeranno 12 mesi di ispirazione. "
                "Speaker che hanno cambiato industrie, workshop dove le idee diventano "
                "prototipi e 800 persone che condividono la stessa urgenza di fare."
            ),
            "service_title": "Masterclass Immersiva",
            "service_description": (
                "Niente slide da 50 pagine. 90 minuti di pratica pura con chi ha costruito "
                "aziende da zero. Gruppi da massimo 15 persone, "
                "un progetto reale da portare a casa. Impari facendo, non ascoltando."
            ),
            "testimonial": (
                "Sono andata per networking e sono tornata con un co-founder, "
                "tre clienti e un'idea che ha raccolto 200k in seed round. "
                "L'anno prima ho saltato l'evento. Non faro' mai piu' quell'errore."
            ),
        },
        {
            "hero_title": "Il Momento e' Adesso",
            "hero_subtitle": (
                "350 posti. 2.400 richieste. Una sola edizione all'anno. "
                "Non e' esclusivita' — e' la promessa che ogni persona in sala "
                "ha qualcosa da insegnarti. La lista d'attesa apre tra 48 ore."
            ),
            "service_title": "After Dark Sessions",
            "service_description": (
                "Quando le luci del palco si spengono, il vero evento inizia. "
                "Conversazioni informali con gli speaker, musica live, cena condivisa. "
                "Le connessioni migliori nascono dopo le 22."
            ),
            "testimonial": (
                "Al terzo cocktail ho trovato il coraggio di parlare con lo speaker "
                "che seguivo da anni. Mi ha dato un feedback sul mio progetto che valeva "
                "piu' di qualsiasi corso. Quell'incontro ha cambiato la traiettoria "
                "della mia carriera."
            ),
        },
    ],
    "custom": [
        {
            "hero_title": "Dove Tutto Prende Forma",
            "hero_subtitle": (
                "Non siamo per tutti — e va bene cosi'. Per chi cerca l'eccezionale "
                "nel quotidiano, per chi rifiuta il 'buono abbastanza', "
                "per chi sa che la differenza sta nei dettagli che nessuno nota. Tranne te."
            ),
            "service_title": "L'Approccio Sartoriale",
            "service_description": (
                "Niente soluzioni preconfezionate, niente template mentali. "
                "Ascoltiamo per tre volte il tempo che parliamo. Poi costruiamo "
                "qualcosa che non esisteva prima — su misura, come un abito "
                "che calza solo a te."
            ),
            "testimonial": (
                "Ho cercato per mesi qualcuno che capisse la mia visione senza che dovessi "
                "spiegarla tre volte. Alla prima call hanno completato le mie frasi. "
                "Il risultato? Esattamente quello che avevo in testa, "
                "ma meglio di come lo immaginavo."
            ),
        },
        {
            "hero_title": "L'Eccellenza Non e' un Caso",
            "hero_subtitle": (
                "Ogni dettaglio e' una decisione. Ogni decisione e' una dichiarazione. "
                "Lavoriamo con chi capisce che il valore si costruisce, "
                "non si dichiara. I risultati parlano — noi li facciamo gridare."
            ),
            "service_title": "Consulenza Strategica",
            "service_description": (
                "Due ore che valgono sei mesi di tentativi. Analizziamo il tuo mercato, "
                "smontiamo le assunzioni sbagliate, ricostruiamo la strategia "
                "su fondamenta solide. Niente teoria — solo azioni concrete con deadline."
            ),
            "testimonial": (
                "Ero scettico — l'ennesimo consulente, pensavo. Poi hanno trovato in 48 ore "
                "un problema che il mio team ignorava da 2 anni. Il fix ha aumentato "
                "la retention del 40%. A volte serve uno sguardo esterno per vedere "
                "l'ovvio."
            ),
        },
    ],
}

# Category-specific fallback texts — used when AI text generation fails
_CATEGORY_FALLBACK_TEXTS: Dict[str, Dict[str, dict]] = {
    "restaurant": {
        "hero": {
            "HERO_TITLE": "Dove il Gusto Incontra l'Arte",
            "HERO_SUBTITLE": "Ogni piatto racconta una storia di passione, tradizione e ingredienti scelti con cura maniacale. Un viaggio sensoriale che inizia dal primo sguardo al menu.",
            "HERO_CTA_TEXT": "Prenota il Tuo Tavolo",
            "HERO_CTA_URL": "#contact",
            "HERO_IMAGE_URL": "",
            "HERO_IMAGE_ALT": "L'esperienza culinaria nel nostro ristorante",
        },
        "about": {
            "ABOUT_TITLE": "La Nostra Filosofia in Cucina",
            "ABOUT_SUBTITLE": "Ogni ingrediente ha una provenienza, ogni ricetta una storia che merita di essere raccontata",
            "ABOUT_TEXT": "Nasciamo dalla convinzione che mangiare non sia solo nutrirsi, ma vivere un'esperienza. La nostra cucina parte dalla terra: collaboriamo con produttori locali selezionati, seguiamo la stagionalita e trasformiamo materie prime eccezionali in piatti che emozionano. Ogni ricetta e il risultato di ricerca, sperimentazione e amore per il dettaglio.",
            "ABOUT_HIGHLIGHT_1": "Fornitori locali selezionati",
            "ABOUT_HIGHLIGHT_2": "Coperti serviti ogni anno",
            "ABOUT_HIGHLIGHT_3": "Valutazione media clienti",
            "ABOUT_HIGHLIGHT_NUM_1": "18",
            "ABOUT_HIGHLIGHT_NUM_2": "12400",
            "ABOUT_HIGHLIGHT_NUM_3": "4.9",
        },
        "services": {
            "SERVICES_TITLE": "I Nostri Piatti Signature",
            "SERVICES_SUBTITLE": "Tre esperienze culinarie che definiscono la nostra identita gastronomica",
            "SERVICES": [
                {"SERVICE_ICON": "\U0001f372", "SERVICE_TITLE": "Menu Degustazione", "SERVICE_DESCRIPTION": "Un percorso di 7 portate che attraversa sapori e territori. Ogni piatto dialoga con il successivo in un crescendo di gusto che sorprende il palato."},
                {"SERVICE_ICON": "\U0001f37e", "SERVICE_TITLE": "Cantina Curata", "SERVICE_DESCRIPTION": "Oltre 180 etichette selezionate personalmente dal nostro sommelier. Abbinamenti pensati per esaltare ogni singola portata del vostro menu."},
                {"SERVICE_ICON": "\U0001f382", "SERVICE_TITLE": "Eventi Privati", "SERVICE_DESCRIPTION": "La nostra sala riservata accoglie fino a 40 ospiti per cene aziendali, celebrazioni e serate esclusive con menu personalizzati dallo chef."},
            ],
        },
        "contact": {
            "CONTACT_TITLE": "Riserva il Tuo Momento Speciale",
            "CONTACT_SUBTITLE": "Che sia una cena romantica, un pranzo di lavoro o una serata tra amici, siamo pronti ad accoglierti con il calore che meriti.",
            "CONTACT_ADDRESS": "", "CONTACT_PHONE": "", "CONTACT_EMAIL": "",
        },
        "cta": {
            "CTA_TITLE": "La Tavola Ti Aspetta",
            "CTA_SUBTITLE": "I posti migliori vanno via in fretta, soprattutto il venerdi e sabato sera. Prenota ora e assicurati un'esperienza indimenticabile.",
            "CTA_BUTTON_TEXT": "Prenota Ora", "CTA_BUTTON_URL": "#contact",
        },
        "footer": {"FOOTER_DESCRIPTION": "Dove ogni pasto diventa un ricordo che vale la pena conservare."},
    },
    "saas": {
        "hero": {
            "HERO_TITLE": "Il Futuro e Adesso",
            "HERO_SUBTITLE": "La piattaforma che trasforma il caos operativo in flussi intelligenti. Automatizza, analizza, scala - mentre tu ti concentri su cio che conta davvero.",
            "HERO_CTA_TEXT": "Prova Gratis 14 Giorni",
            "HERO_CTA_URL": "#contact", "HERO_IMAGE_URL": "", "HERO_IMAGE_ALT": "Dashboard della piattaforma",
        },
        "about": {
            "ABOUT_TITLE": "Costruito per Chi Vuole di Piu",
            "ABOUT_SUBTITLE": "Non un altro tool. Una rivoluzione nel modo in cui lavori ogni giorno",
            "ABOUT_TEXT": "Siamo nati dalla frustrazione di chi usa 15 strumenti diversi per fare il lavoro di uno. La nostra piattaforma unifica, semplifica e potenzia ogni flusso operativo. Dietro ogni funzionalita c'e un team ossessionato dall'esperienza utente e dalla performance. Zero compromessi sulla velocita, zero compromessi sulla sicurezza.",
            "ABOUT_HIGHLIGHT_1": "Aziende attive sulla piattaforma",
            "ABOUT_HIGHLIGHT_2": "Uptime garantito",
            "ABOUT_HIGHLIGHT_3": "Ore risparmiate al mese per utente",
            "ABOUT_HIGHLIGHT_NUM_1": "2400", "ABOUT_HIGHLIGHT_NUM_2": "99.97", "ABOUT_HIGHLIGHT_NUM_3": "23",
        },
        "services": {
            "SERVICES_TITLE": "Funzionalita che Cambiano le Regole",
            "SERVICES_SUBTITLE": "Ogni feature e progettata per eliminare un problema reale, non per riempire una checklist",
            "SERVICES": [
                {"SERVICE_ICON": "\u26a1", "SERVICE_TITLE": "Automazione Intelligente", "SERVICE_DESCRIPTION": "Crea flussi di lavoro complessi in pochi click. Il nostro motore AI impara dai tuoi pattern e suggerisce ottimizzazioni che ti fanno risparmiare ore ogni settimana."},
                {"SERVICE_ICON": "\U0001f4ca", "SERVICE_TITLE": "Analytics in Tempo Reale", "SERVICE_DESCRIPTION": "Dashboard personalizzabili con metriche che contano. Visualizza trend, anomalie e opportunita prima che diventino problemi o che la concorrenza le colga."},
                {"SERVICE_ICON": "\U0001f6e1\ufe0f", "SERVICE_TITLE": "Sicurezza Enterprise", "SERVICE_DESCRIPTION": "Crittografia end-to-end, SSO, audit log completo e conformita GDPR integrata. La tua sicurezza non e un'opzione, e la nostra ossessione."},
            ],
        },
        "contact": {
            "CONTACT_TITLE": "Parliamo del Tuo Prossimo Livello",
            "CONTACT_SUBTITLE": "Demo personalizzata in 15 minuti. Ti mostriamo esattamente come la piattaforma risolve i tuoi problemi specifici.",
            "CONTACT_ADDRESS": "", "CONTACT_PHONE": "", "CONTACT_EMAIL": "",
        },
        "cta": {
            "CTA_TITLE": "Smetti di Perdere Tempo",
            "CTA_SUBTITLE": "Ogni giorno senza automazione e un giorno di produttivita sprecata. Inizia ora, i risultati arrivano dalla prima settimana.",
            "CTA_BUTTON_TEXT": "Inizia la Prova Gratuita", "CTA_BUTTON_URL": "#contact",
        },
        "footer": {"FOOTER_DESCRIPTION": "La piattaforma che fa lavorare la tecnologia per te, non il contrario."},
    },
    "portfolio": {
        "hero": {
            "HERO_TITLE": "Creo Mondi Visivi",
            "HERO_SUBTITLE": "Designer, pensatore, risolutore di problemi. Trasformo idee astratte in esperienze digitali che le persone ricordano e con cui vogliono interagire.",
            "HERO_CTA_TEXT": "Esplora i Progetti",
            "HERO_CTA_URL": "#gallery", "HERO_IMAGE_URL": "", "HERO_IMAGE_ALT": "Portfolio dei migliori progetti creativi",
        },
        "about": {
            "ABOUT_TITLE": "Il Metodo Dietro la Creativita",
            "ABOUT_SUBTITLE": "Ogni progetto inizia con una domanda: come posso superare le aspettative?",
            "ABOUT_TEXT": "Con oltre un decennio di esperienza nel design digitale, ho sviluppato un approccio che unisce ricerca, intuizione e ossessione per il dettaglio. Non creo semplicemente interfacce - costruisco esperienze che risolvono problemi reali e generano risultati misurabili. Ogni pixel ha uno scopo, ogni interazione racconta una storia.",
            "ABOUT_HIGHLIGHT_1": "Progetti completati", "ABOUT_HIGHLIGHT_2": "Premi e riconoscimenti",
            "ABOUT_HIGHLIGHT_3": "Clienti in tutto il mondo",
            "ABOUT_HIGHLIGHT_NUM_1": "127", "ABOUT_HIGHLIGHT_NUM_2": "14", "ABOUT_HIGHLIGHT_NUM_3": "38",
        },
        "services": {
            "SERVICES_TITLE": "Competenze al Tuo Servizio",
            "SERVICES_SUBTITLE": "Dalla strategia al pixel finale, ogni fase del progetto riceve la stessa cura maniacale",
            "SERVICES": [
                {"SERVICE_ICON": "\U0001f3a8", "SERVICE_TITLE": "Brand Identity", "SERVICE_DESCRIPTION": "Logo, palette, tipografia e sistema visivo completo. Costruisco identita che si distinguono nel rumore e restano impresse nella memoria."},
                {"SERVICE_ICON": "\U0001f4f1", "SERVICE_TITLE": "UI/UX Design", "SERVICE_DESCRIPTION": "Interfacce intuitive che guidano l'utente verso l'obiettivo. Ricerca, wireframe, prototipazione e test - ogni decisione e supportata dai dati."},
                {"SERVICE_ICON": "\U0001f680", "SERVICE_TITLE": "Design Strategico", "SERVICE_DESCRIPTION": "Non solo estetica: analizzo il mercato, studio i competitor e progetto soluzioni che generano conversioni reali e crescita misurabile."},
            ],
        },
        "contact": {
            "CONTACT_TITLE": "Costruiamo Qualcosa di Grande",
            "CONTACT_SUBTITLE": "Hai un progetto ambizioso? Parliamone davanti a un caffe virtuale. Le migliori collaborazioni iniziano con una conversazione sincera.",
            "CONTACT_ADDRESS": "", "CONTACT_PHONE": "", "CONTACT_EMAIL": "",
        },
        "cta": {
            "CTA_TITLE": "Il Tuo Progetto Merita il Meglio",
            "CTA_SUBTITLE": "Accetto solo 3 nuovi progetti al mese per garantire a ciascuno l'attenzione che merita. Verifica la mia disponibilita.",
            "CTA_BUTTON_TEXT": "Richiedi una Consulenza", "CTA_BUTTON_URL": "#contact",
        },
        "footer": {"FOOTER_DESCRIPTION": "Design che risolve problemi e crea connessioni autentiche."},
    },
    "ecommerce": {
        "hero": {
            "HERO_TITLE": "Stile Che Parla di Te",
            "HERO_SUBTITLE": "Prodotti selezionati con cura per chi non si accontenta del banale. Qualita artigianale, design contemporaneo, spedizione fulminante.",
            "HERO_CTA_TEXT": "Scopri la Collezione",
            "HERO_CTA_URL": "#services", "HERO_IMAGE_URL": "", "HERO_IMAGE_ALT": "La nostra collezione esclusiva",
        },
        "services": {
            "SERVICES_TITLE": "Perche Scegliere Noi",
            "SERVICES_SUBTITLE": "Tre promesse che manteniamo ogni singolo giorno",
            "SERVICES": [
                {"SERVICE_ICON": "\U0001f48e", "SERVICE_TITLE": "Qualita Certificata", "SERVICE_DESCRIPTION": "Ogni prodotto passa 3 controlli qualita prima di raggiungere le tue mani. Materiali premium, lavorazione impeccabile, durabilita garantita nel tempo."},
                {"SERVICE_ICON": "\U0001f69a", "SERVICE_TITLE": "Spedizione Express", "SERVICE_DESCRIPTION": "Ordini prima delle 14? Spedito lo stesso giorno. Tracciamento in tempo reale e consegna in 24-48 ore in tutta Italia, gratis sopra i 59 euro."},
                {"SERVICE_ICON": "\U0001f504", "SERVICE_TITLE": "Reso Senza Pensieri", "SERVICE_DESCRIPTION": "30 giorni per cambiare idea. Reso gratuito, rimborso immediato, zero domande. La tua soddisfazione e la nostra unica priorita."},
            ],
        },
        "contact": {
            "CONTACT_TITLE": "Siamo Qui Per Te",
            "CONTACT_SUBTITLE": "Dubbi sulla taglia, domande sui materiali o bisogno di un consiglio personalizzato? Il nostro team risponde in meno di 2 ore.",
            "CONTACT_ADDRESS": "", "CONTACT_PHONE": "", "CONTACT_EMAIL": "",
        },
        "cta": {
            "CTA_TITLE": "Non Lasciarti Sfuggire Questo",
            "CTA_SUBTITLE": "Nuovi arrivi ogni settimana. Iscriviti alla newsletter e ricevi il 15% di sconto sul primo ordine.",
            "CTA_BUTTON_TEXT": "Ottieni il 15% di Sconto", "CTA_BUTTON_URL": "#contact",
        },
        "footer": {"FOOTER_DESCRIPTION": "Prodotti che raccontano chi sei, consegnati a casa tua con cura."},
    },
    "business": {
        "hero": {
            "HERO_TITLE": "Costruiamo il Domani",
            "HERO_SUBTITLE": "Partner strategici per aziende che non si accontentano dello status quo. Trasformiamo sfide complesse in opportunita concrete di crescita misurabile.",
            "HERO_CTA_TEXT": "Richiedi una Consulenza",
            "HERO_CTA_URL": "#contact", "HERO_IMAGE_URL": "", "HERO_IMAGE_ALT": "Il nostro approccio strategico al business",
        },
        "about": {
            "ABOUT_TITLE": "Il Nostro Approccio Strategico",
            "ABOUT_SUBTITLE": "Non vendiamo servizi. Costruiamo partnership che generano risultati duraturi",
            "ABOUT_TEXT": "Nasciamo dalla convinzione che il mercato merita di meglio. Non ci accontentiamo della mediocrita e non inseguiamo le scorciatoie. Ogni progetto diventa una sfida personale, un'opportunita per dimostrare che si puo fare di piu, meglio e con piu cura. La nostra storia e fatta di intuizioni brillanti e la testardaggine di chi crede davvero in quello che fa.",
            "ABOUT_HIGHLIGHT_1": "Anni di esperienza sul campo",
            "ABOUT_HIGHLIGHT_2": "Progetti completati con successo",
            "ABOUT_HIGHLIGHT_3": "Tasso di soddisfazione clienti",
            "ABOUT_HIGHLIGHT_NUM_1": "15", "ABOUT_HIGHLIGHT_NUM_2": "847", "ABOUT_HIGHLIGHT_NUM_3": "99.2",
        },
        "services": {
            "SERVICES_TITLE": "Il Metodo Dietro i Risultati",
            "SERVICES_SUBTITLE": "Tre pilastri che trasformano la complessita in vantaggio competitivo",
            "SERVICES": [
                {"SERVICE_ICON": "\U0001f3af", "SERVICE_TITLE": "Strategia su Misura", "SERVICE_DESCRIPTION": "Analizziamo a fondo il tuo contesto per costruire un percorso che rifletta la vera identita del tuo business e porti risultati misurabili nel tempo."},
                {"SERVICE_ICON": "\U0001f680", "SERVICE_TITLE": "Esecuzione Fulminante", "SERVICE_DESCRIPTION": "Dalla visione al lancio in tempi record. Ogni fase del progetto segue un metodo collaudato che elimina gli sprechi e accelera i risultati concreti."},
                {"SERVICE_ICON": "\U0001f4a1", "SERVICE_TITLE": "Evoluzione Continua", "SERVICE_DESCRIPTION": "Non ci fermiamo al primo traguardo. Monitoriamo, ottimizziamo e iteriamo per garantire che ogni aspetto cresca insieme al tuo business."},
            ],
        },
        "contact": {
            "CONTACT_TITLE": "Parliamo del Tuo Prossimo Passo",
            "CONTACT_SUBTITLE": "Ogni grande progetto inizia con una conversazione. Raccontaci la tua idea e trasformiamola insieme in qualcosa di straordinario.",
            "CONTACT_ADDRESS": "", "CONTACT_PHONE": "", "CONTACT_EMAIL": "",
        },
        "cta": {
            "CTA_TITLE": "Il Momento e Adesso",
            "CTA_SUBTITLE": "Ogni giorno che passa e un'opportunita persa. Fai il primo passo verso risultati che superano le aspettative.",
            "CTA_BUTTON_TEXT": "Prenota una Consulenza Gratuita", "CTA_BUTTON_URL": "#contact",
        },
        "footer": {"FOOTER_DESCRIPTION": "Dove nascono le idee che cambiano le regole del gioco."},
    },
    "blog": {
        "hero": {
            "HERO_TITLE": "Parole Che Lasciano il Segno",
            "HERO_SUBTITLE": "Storie, riflessioni e approfondimenti per chi vuole andare oltre la superficie. Contenuti che informano, ispirano e provocano il pensiero critico.",
            "HERO_CTA_TEXT": "Leggi l'Ultimo Articolo",
            "HERO_CTA_URL": "#services", "HERO_IMAGE_URL": "", "HERO_IMAGE_ALT": "Il nostro blog editoriale",
        },
        "services": {
            "SERVICES_TITLE": "Le Nostre Rubriche",
            "SERVICES_SUBTITLE": "Contenuti curati per menti curiose che cercano sostanza, non rumore",
            "SERVICES": [
                {"SERVICE_ICON": "\U0001f4dd", "SERVICE_TITLE": "Analisi di Fondo", "SERVICE_DESCRIPTION": "Approfondimenti che vanno oltre il titolo. Ricerche originali, dati verificati e prospettive che non trovi altrove. Ogni articolo e un viaggio."},
                {"SERVICE_ICON": "\U0001f4a1", "SERVICE_TITLE": "Idee e Tendenze", "SERVICE_DESCRIPTION": "Cosa sta cambiando nel nostro settore e perche dovrebbe importarti. Anticipiamo i trend con analisi lucide e consigli pratici immediati."},
                {"SERVICE_ICON": "\U0001f399\ufe0f", "SERVICE_TITLE": "Interviste Esclusive", "SERVICE_DESCRIPTION": "Conversazioni con chi sta plasmando il futuro. Storie vere, lezioni apprese e visioni che ampliano gli orizzonti di ogni lettore."},
            ],
        },
        "contact": {
            "CONTACT_TITLE": "Unisciti alla Conversazione",
            "CONTACT_SUBTITLE": "Hai un'idea per un articolo, una storia da raccontare o semplicemente vuoi dire la tua? La nostra community cresce grazie a voci come la tua.",
            "CONTACT_ADDRESS": "", "CONTACT_PHONE": "", "CONTACT_EMAIL": "",
        },
        "footer": {"FOOTER_DESCRIPTION": "Storie che contano, scritte per chi vuole capire davvero."},
    },
    "event": {
        "hero": {
            "HERO_TITLE": "Vivi l'Esperienza dal Vivo",
            "HERO_SUBTITLE": "Gli eventi che creano connessioni autentiche, ispirano nuove idee e lasciano ricordi che durano. Non semplici incontri, ma momenti che cambiano prospettive.",
            "HERO_CTA_TEXT": "Riserva il Tuo Posto",
            "HERO_CTA_URL": "#contact", "HERO_IMAGE_URL": "", "HERO_IMAGE_ALT": "L'atmosfera dei nostri eventi esclusivi",
        },
        "services": {
            "SERVICES_TITLE": "Cosa Ti Aspetta",
            "SERVICES_SUBTITLE": "Un programma progettato per massimizzare ogni minuto della tua esperienza",
            "SERVICES": [
                {"SERVICE_ICON": "\U0001f3a4", "SERVICE_TITLE": "Speaker d'Eccezione", "SERVICE_DESCRIPTION": "Relatori selezionati tra i migliori del settore. Non le solite presentazioni, ma conversazioni che provocano idee e cambiano il modo di pensare."},
                {"SERVICE_ICON": "\U0001f91d", "SERVICE_TITLE": "Networking Mirato", "SERVICE_DESCRIPTION": "Sessioni strutturate per connettere le persone giuste. Il nostro sistema di matching ti mette in contatto con chi puo davvero fare la differenza."},
                {"SERVICE_ICON": "\U0001f3c6", "SERVICE_TITLE": "Esperienza Premium", "SERVICE_DESCRIPTION": "Dall'accoglienza al follow-up, ogni dettaglio e curato per offrirti un'esperienza che supera qualsiasi aspettativa. Location esclusiva, catering d'autore."},
            ],
        },
        "contact": {
            "CONTACT_TITLE": "Non Perdere Questa Occasione",
            "CONTACT_SUBTITLE": "I posti sono limitati e ogni edizione registra il tutto esaurito. Assicurati il tuo ingresso prima che sia troppo tardi.",
            "CONTACT_ADDRESS": "", "CONTACT_PHONE": "", "CONTACT_EMAIL": "",
        },
        "cta": {
            "CTA_TITLE": "I Posti Stanno Finendo",
            "CTA_SUBTITLE": "Le ultime tre edizioni hanno registrato il sold out in meno di una settimana. Non aspettare l'ultimo momento.",
            "CTA_BUTTON_TEXT": "Acquista il Tuo Biglietto", "CTA_BUTTON_URL": "#contact",
        },
        "footer": {"FOOTER_DESCRIPTION": "Eventi che creano connessioni e ispirano il cambiamento."},
    },
}

# Animation randomizer pools — replace hardcoded data-animate values
# with randomly-chosen alternatives from equivalent pools.
ANIMATION_POOLS: Dict[str, List[str]] = {
    # Heading animations (replacements for text-split)
    "heading": ["text-split", "text-reveal", "typewriter", "blur-in", "clip-reveal"],
    # Subtitle/paragraph entrance
    "subtitle": ["blur-slide", "fade-up", "fade-left", "slide-up", "fade-right", "reveal-up"],
    # CTA button entrance
    "cta": ["bounce-in", "scale-in", "magnetic", "blur-in", "fade-up"],
    # Card/item entrance
    "card": ["fade-up", "scale-in", "blur-in", "fade-left", "fade-right", "zoom-out"],
    # Section entrance (generic)
    "section": ["fade-up", "fade-left", "fade-right", "reveal-up", "reveal-left", "blur-in", "scale-in"],
    # Image entrance
    "image": ["scale-in", "blur-in", "fade-up", "clip-reveal", "zoom-out"],
}

# Stagger animation variants
STAGGER_VARIANTS: List[str] = ["stagger", "stagger-scale"]

# Ease function variants
EASE_VARIANTS: List[str] = [
    "power2.out", "power3.out", "power4.out",
    "back.out(1.2)", "expo.out", "circ.out",
    "elastic.out(0.5,0.3)",
]
