"""Style-to-component mapping and tone configuration.

Maps frontend template style IDs to backend component variants,
copywriting voice directives, and visual CSS profiles.
"""

from typing import Dict, List


# =========================================================
# CATEGORY TONE PROFILES
# Injected into _generate_texts() prompt so the AI adapts
# its voice to the business sector, not just the personality.
# =========================================================
CATEGORY_TONES: Dict[str, str] = {
    "restaurant": (
        "TONO: Sensoriale, intimo, poetico. Evoca profumi, consistenze, luci soffuse. "
        "Scrivi come se il lettore potesse assaggiare le parole. Usa sinestesie "
        "(\"un sapore che suona come jazz\"). Il cibo e' memoria, identita', rituale."
    ),
    "saas": (
        "TONO: Affilato, sicuro, orientato ai risultati. Numeri specifici, "
        "contrasti prima/dopo, promesse misurabili. Niente buzzword vuote: "
        "ogni frase deve rispondere a 'perche' dovrei scegliere voi?'. "
        "Pensa a Stripe, Linear, Vercel — copy che taglia."
    ),
    "portfolio": (
        "TONO: Autoriale, visionario, leggermente enigmatico. "
        "Ogni progetto e' una storia, non una voce di catalogo. "
        "Parla del PERCHE', non del cosa. Il designer/artista ha una filosofia, "
        "non solo competenze. Ispira curiosita'."
    ),
    "ecommerce": (
        "TONO: Desiderio, identita', trasformazione. Non vendi prodotti, "
        "vendi chi il cliente DIVENTA. Linguaggio aspirazionale ma autentico. "
        "Dettagli sensoriali sui materiali, la fattura, l'esperienza di unboxing. "
        "Urgenza sottile, mai aggressiva."
    ),
    "business": (
        "TONO: Autorevole, visionario, concreto. Bilancia fiducia e ambizione. "
        "Numeri che dimostrano, non che vantano. Parla del futuro del cliente, "
        "non del passato dell'azienda. Ogni frase costruisce credibilita' "
        "attraverso specificita', non attraverso aggettivi."
    ),
    "blog": (
        "TONO: Intellettuale, curioso, provocatorio. Ogni titolo e' una domanda "
        "che il lettore non sapeva di avere. Crea tensione tra il conosciuto e "
        "l'inaspettato. Il blog non informa — sfida, reinterpreta, illumina."
    ),
    "event": (
        "TONO: Elettrico, urgente, esperienziale. Il lettore deve sentire "
        "l'energia PRIMA di arrivare. FOMO strategico: non 'partecipa', "
        "ma 'non puoi permetterti di perdere questo'. Date, numeri, "
        "countdown. Ogni parola accelera il battito."
    ),
    "custom": (
        "TONO: Adatta il tono al tipo di attivita' descritto. "
        "Se non e' chiaro, usa un mix di autorevolezza e calore. "
        "Copy che potrebbe vincere un Awwwards: specifico, ritmato, memorabile."
    ),
}

# =========================================================
# STYLE_TONE_MAP: Per-style copywriting directives.
# While CATEGORY_TONES sets the broad sector voice (restaurant,
# saas, etc.), this map overrides/refines the tone for each
# specific template sub-style. "restaurant-elegant" should read
# COMPLETELY different from "restaurant-cozy".
# Injected into BOTH _generate_texts() and _generate_theme()
# so that fonts, colors, AND copy all speak the same language.
# =========================================================
STYLE_TONE_MAP: Dict[str, Dict[str, str]] = {
    "restaurant-elegant": {
        "voice": (
            "VOCE: Formale, raffinata, sussurrata. Come un maitre d'hotel che ti accoglie per nome. "
            "Frasi lunghe ed eleganti, vocabolario ricercato (degustazione, mise en place, terroir). "
            "Mai esclamazioni, mai punti esclamativi. Il lusso non grida."
        ),
        "headlines": "Titoli evocativi e poetici. Metafore sensoriali. MAX 5 parole. Es: 'Dove il Gusto Diventa Arte'.",
        "theme_hint": (
            "Palette calda e profonda: bordeaux, oro antico, crema avorio. Font serif classico (Playfair, Cormorant). "
            "shadow_style: soft. spacing_density: generous. border_radius_style: soft."
        ),
    },
    "restaurant-cozy": {
        "voice": (
            "VOCE: Calda, familiare, come una nonna che ti invita a sederti. Tono colloquiale ma mai sciatto. "
            "Frasi brevi e affettuose. Parole che sanno di casa: 'fatto a mano', 'ricetta della nonna', "
            "'come una volta'. Accogliente, mai formale."
        ),
        "headlines": "Titoli che sorridono. Tono amichevole, quasi intimo. Es: 'A Casa Nostra, Si Mangia Col Cuore'.",
        "theme_hint": (
            "Colori caldi e terrosi: terracotta, arancio tenue, verde salvia, beige. Font morbido e arrotondato "
            "(Nunito, Quicksand heading). shadow_style: soft. spacing_density: normal. border_radius_style: round."
        ),
    },
    "restaurant-modern": {
        "voice": (
            "VOCE: Tagliente, contemporanea, magazine-style. Come Bon Appetit o Eater. "
            "Frasi corte e d'impatto. Giustapposizioni: 'Tradizione. Rivista.' — 'Fuoco. Tecnica. Ossessione.' "
            "Zero nostalgia, tutta innovazione. Food come design."
        ),
        "headlines": "Titoli brutali e minimali. Una parola. Un concetto. Es: 'Fuoco Vivo' o 'Crudo. Puro. Nostro.'.",
        "theme_hint": (
            "Palette ad alto contrasto: nero/bianco con un accento vivace (rosso fuoco, lime). Font sans-serif "
            "geometrico bold (Space Grotesk, Archivo). shadow_style: none. spacing_density: compact. "
            "border_radius_style: sharp."
        ),
    },
    "saas-gradient": {
        "voice": (
            "VOCE: Energica, futuristica, tech-ottimista. Come la landing page di Vercel o Linear. "
            "Promesse audaci con numeri specifici. Linguaggio da startup che sta cambiando il mondo. "
            "Verbi d'azione forti: 'accelera', 'scala', 'automatizza', 'domina'."
        ),
        "headlines": "Titoli brevi e potenti con numeri o verbi d'azione. Es: '10x Piu' Veloce' o 'Il Futuro e' Adesso'.",
        "theme_hint": (
            "Palette scura con gradienti vibranti: deep purple→electric blue, dark bg con glow neon. "
            "Font geometrico moderno (Sora, Inter heading bold). shadow_style: dramatic. "
            "spacing_density: normal. border_radius_style: soft."
        ),
    },
    "saas-clean": {
        "voice": (
            "VOCE: Chiara, diretta, senza fronzoli. Come Notion o Stripe. Ogni parola ha uno scopo. "
            "Niente metafore eccessive — chiarezza sopra tutto. Il prodotto parla da solo. "
            "Benefici misurabili, frasi che un CEO condividerebbe su LinkedIn."
        ),
        "headlines": "Titoli funzionali ma eleganti. Chiarezza > creativita'. Es: 'Tutto in Un Solo Strumento'.",
        "theme_hint": (
            "Palette luminosa e pulita: bianco/grigio chiaro con un primary vibrante (blue, indigo). "
            "Font sans-serif pulito (Inter, Plus Jakarta Sans). shadow_style: soft. "
            "spacing_density: normal. border_radius_style: soft."
        ),
    },
    "saas-dark": {
        "voice": (
            "VOCE: Tecnica, affilata, da developer-tool. Come GitHub, Raycast, o Warp terminal. "
            "Gergo tech accettato. Poche parole, massima densita' informativa. "
            "Copy che sembra codice: preciso, senza sprechi. Mai 'soluzione innovativa' — "
            "piuttosto 'build, ship, iterate'."
        ),
        "headlines": "Titoli ultra-minimali, quasi comandi. Es: 'Ship Faster.' o 'Zero Config. Full Power.'.",
        "theme_hint": (
            "Palette dark-mode: charcoal/navy profondo, accento neon (cyan, green, amber). "
            "Font monospace o geometric (JetBrains Mono heading, Space Grotesk). shadow_style: none. "
            "spacing_density: compact. border_radius_style: sharp."
        ),
    },
    "portfolio-gallery": {
        "voice": (
            "VOCE: Visiva, minimale, ogni parola e' didascalia. Come un catalogo d'arte o Behance. "
            "I progetti parlano — il testo accompagna, non domina. Frasi poetiche e frammentarie. "
            "Il designer non spiega, mostra. 'Esplora il progetto' non 'Guarda i nostri lavori'."
        ),
        "headlines": "Titoli evocativi e astratti. Es: 'Forme che Parlano' o 'Spazio. Luce. Intenzione.'.",
        "theme_hint": (
            "Palette neutra con un accento deciso: bianco/nero + un colore signature (rosso, electric blue). "
            "Font display con carattere (Instrument Serif, Space Grotesk). shadow_style: none. "
            "spacing_density: generous. border_radius_style: sharp."
        ),
    },
    "portfolio-minimal": {
        "voice": (
            "VOCE: Ultra-ridotta, zen-like. Come il portfolio di un designer svizzero. "
            "Ogni parola e' pesata come in un haiku. Nessun aggettivo superfluo. "
            "Il vuoto parla piu' del pieno. Bio in terza persona, distaccata e autorevole."
        ),
        "headlines": "Titoli di una o due parole. Es: 'Design.' o 'Meno, Meglio.'.",
        "theme_hint": (
            "Palette monocromatica: bianco purissimo o nero profondo, quasi nessun colore. "
            "Font sans-serif raffinato con molto tracking (Epilogue, Albert Sans). shadow_style: none. "
            "spacing_density: generous. border_radius_style: sharp."
        ),
    },
    "portfolio-creative": {
        "voice": (
            "VOCE: Esplosiva, giocosa, anti-convenzionale. Come un manifesto artistico. "
            "Rompi le regole della punteggiatura. Mix di lingue accettato. Emotivo e viscerale. "
            "Il creativo non e' un fornitore — e' un visionario che trasforma brand."
        ),
        "headlines": "Titoli provocatori, anche irriverenti. Es: 'Facciamo Cose Belle (Sul Serio)' o 'Caos Calcolato'.",
        "theme_hint": (
            "Palette audace e inaspettata: accostamenti non convenzionali (lime+magenta, coral+indigo). "
            "Font display grassissimo (Unbounded, Archivo Black). shadow_style: dramatic. "
            "spacing_density: normal. border_radius_style: round."
        ),
    },
    "ecommerce-modern": {
        "voice": (
            "VOCE: Aspirazionale ma accessibile. Come Glossier o Everlane. "
            "Il prodotto diventa lifestyle. Linguaggio sensoriale sui materiali e l'esperienza. "
            "Urgenza morbida: 'Edizione limitata' non 'COMPRA ORA'. "
            "Ogni descrizione e' una micro-storia."
        ),
        "headlines": "Titoli che creano desiderio. Es: 'Progettato per Chi Non si Accontenta'.",
        "theme_hint": (
            "Palette lifestyle: toni neutri caldi (blush, sand, sage) con primary deciso. "
            "Font moderno elegante (DM Sans, Plus Jakarta Sans). shadow_style: soft. "
            "spacing_density: normal. border_radius_style: soft."
        ),
    },
    "ecommerce-luxury": {
        "voice": (
            "VOCE: Esclusiva, sussurrata, da maison. Come Hermes o Bottega Veneta. "
            "Mai vendere — invitare. Mai 'economico' — 'accessibile'. Mai 'prodotto' — 'creazione'. "
            "Frasi brevi, peso specifico altissimo. L'understatement e' il vero lusso."
        ),
        "headlines": "Titoli che non spiegano, evocano. Es: 'L'Arte del Dettaglio' o 'Senza Tempo'.",
        "theme_hint": (
            "Palette lusso: nero/champagne/oro, fondi scuri con tipografia chiara. "
            "Font serif sofisticato (Playfair Display, DM Serif Display). shadow_style: dramatic. "
            "spacing_density: generous. border_radius_style: soft."
        ),
    },
    "business-corporate": {
        "voice": (
            "VOCE: Autorevole, strutturata, da report annuale di alto livello. Come McKinsey o Deloitte. "
            "Dati concreti, case study impliciti, linguaggio che ispira fiducia istituzionale. "
            "Mai informale. Il 'noi' aziendale e' forte e coeso."
        ),
        "headlines": "Titoli che comunicano solidita' e visione. Es: 'Costruiamo il Futuro delle Imprese'.",
        "theme_hint": (
            "Palette professionale: navy, grigio-blu, bianco. Accento corporate (teal o gold). "
            "Font serif autorevole per heading (DM Serif Display), sans-serif per body. "
            "shadow_style: soft. spacing_density: normal. border_radius_style: soft."
        ),
    },
    "business-trust": {
        "voice": (
            "VOCE: Empatica, rassicurante, concreta. Come un consulente che ti prende per mano. "
            "Meno 'noi siamo bravi' e piu' 'tu otterrai questo'. Focus su risultati tangibili. "
            "Testimonial e numeri costruiscono credibilita' naturale."
        ),
        "headlines": "Titoli orientati al risultato del cliente. Es: 'Il Tuo Successo e' la Nostra Misura'.",
        "theme_hint": (
            "Palette calda e affidabile: blu medio, verde, terra di Siena. Sfondo caldo (cream/ivory). "
            "Font amichevole ma professionale (Source Serif, Lora heading). shadow_style: soft. "
            "spacing_density: normal. border_radius_style: round."
        ),
    },
    "business-fresh": {
        "voice": (
            "VOCE: Giovane, energica, startup-vibes. Come Mailchimp o Slack. "
            "Tono conversazionale, quasi amichevole. Emoji strategici OK. "
            "Humor sottile accettato. Parole corte, frasi che rimbalzano. "
            "Il business e' serio, il tono no."
        ),
        "headlines": "Titoli giocosi e diretti. Es: 'Basta Fogli Excel. Davvero.' o 'Lavora Meglio, Non di Piu''.",
        "theme_hint": (
            "Palette vivace e pop: primary brillante (viola, coral, teal), sfondo chiaro e fresco. "
            "Font sans-serif rotondo e friendly (Nunito, Outfit). shadow_style: soft. "
            "spacing_density: normal. border_radius_style: round."
        ),
    },
    "blog-editorial": {
        "voice": (
            "VOCE: Intellettuale, narrativa, da rivista letteraria. Come The Atlantic o Il Post. "
            "Frasi lunghe e ben costruite. Citazioni, domande retoriche, aperture in medias res. "
            "Il blog non informa — crea pensiero. Ogni articolo e' un mini-saggio."
        ),
        "headlines": "Titoli che pongono domande o provocano. Es: 'Perche' Nessuno Parla di Questo?' o 'La Fine di un'Era'.",
        "theme_hint": (
            "Palette editoriale: fondi carta (ivory, linen), testo scuro ricco, accento minimo. "
            "Font serif da rivista (Instrument Serif, Lora heading). shadow_style: none. "
            "spacing_density: generous. border_radius_style: sharp."
        ),
    },
    "blog-dark": {
        "voice": (
            "VOCE: Intima, notturna, da blog tech/culture. Come The Verge o Wired dark mode. "
            "Tono informato e opinionated. Mix di analisi tecnica e storytelling. "
            "Linguaggio contemporaneo, riferimenti culturali, frasi nette e taglienti."
        ),
        "headlines": "Titoli d'impatto, stile news/tech. Es: 'L'Algoritmo Che Cambia Tutto' o 'Deep Dive: Oltre il Codice'.",
        "theme_hint": (
            "Palette dark: background scuro (charcoal, navy), testo chiaro, accento neon vivace. "
            "Font moderno e leggibile (Space Grotesk, Sora). shadow_style: soft. "
            "spacing_density: normal. border_radius_style: soft."
        ),
    },
    "event-vibrant": {
        "voice": (
            "VOCE: Elettrica, urgente, da festival poster. Come Primavera Sound o Web Summit. "
            "FOMO puro. Countdown implicito. Numeri ovunque (speaker, ore, partecipanti). "
            "Frasi brevissime. Imperativi. 'Non Mancare.' 'Ci Vediamo Li'.' "
            "L'energia deve uscire dallo schermo."
        ),
        "headlines": "Titoli da poster: grandi, audaci, 3 parole max. Es: 'L'Evento dell'Anno' o 'Preparati.'.",
        "theme_hint": (
            "Palette esplosiva: gradienti neon, accostamenti elettrici (magenta+cyan, arancio+viola). "
            "Font display gigantesco (Unbounded, Space Grotesk 900). shadow_style: dramatic. "
            "spacing_density: compact. border_radius_style: round."
        ),
    },
    "event-minimal": {
        "voice": (
            "VOCE: Elegante, curata, da invito esclusivo. Come un vernissage o un TED Talk. "
            "Poche parole, massima eleganza. L'evento parla di qualita', non di quantita'. "
            "Dettagli pratici (data, luogo, orario) presentati con grazia tipografica."
        ),
        "headlines": "Titoli raffinati e puliti. Es: 'Un Incontro di Menti' o '12 Aprile. Milano. Sii Presente.'.",
        "theme_hint": (
            "Palette sofisticata: bianco/nero con un accento metallico (oro, argento). "
            "Font serif elegante (Cormorant, Instrument Serif). shadow_style: none. "
            "spacing_density: generous. border_radius_style: sharp."
        ),
    },
}

# =========================================================
# Deterministic style -> component variant mapping.
# Each frontend template style maps to curated component variants
# ensuring visually distinct sites for every template choice.
# =========================================================
STYLE_VARIANT_MAP: Dict[str, Dict[str, str]] = {
    # --- Restaurant ---
    "restaurant-elegant": {
        "nav": "nav-classic-01",
        "hero": "hero-classic-01",
        "about": "about-magazine-01",
        "services": "services-alternating-rows-01",
        "gallery": "gallery-spotlight-01",
        "testimonials": "testimonials-spotlight-01",
        "contact": "contact-minimal-01",
        "footer": "footer-centered-01",
    },
    "restaurant-cozy": {
        "nav": "nav-classic-01",
        "hero": "hero-organic-01",
        "about": "about-split-scroll-01",
        "services": "services-icon-list-01",
        "gallery": "gallery-masonry-01",
        "testimonials": "testimonials-card-stack-01",
        "contact": "contact-card-01",
        "footer": "footer-multi-col-01",
    },
    "restaurant-modern": {
        "nav": "nav-minimal-01",
        "hero": "hero-zen-01",
        "about": "about-bento-01",
        "services": "services-tabs-01",
        "gallery": "gallery-filmstrip-01",
        "testimonials": "testimonials-marquee-01",
        "contact": "contact-modern-form-01",
        "footer": "footer-minimal-02",
    },
    # --- SaaS / Landing Page ---
    "saas-gradient": {
        "nav": "nav-minimal-01",
        "hero": "hero-gradient-03",
        "about": "about-timeline-02",
        "services": "services-hover-reveal-01",
        "features": "features-bento-grid-01",
        "testimonials": "testimonials-marquee-01",
        "cta": "cta-gradient-animated-01",
        "contact": "contact-modern-form-01",
        "footer": "footer-gradient-01",
    },
    "saas-clean": {
        "nav": "nav-classic-01",
        "hero": "hero-centered-02",
        "about": "about-alternating-01",
        "services": "services-cards-grid-01",
        "features": "features-icons-grid-01",
        "testimonials": "testimonials-grid-01",
        "cta": "cta-banner-01",
        "contact": "contact-form-01",
        "footer": "footer-sitemap-01",
    },
    "saas-dark": {
        "nav": "nav-minimal-01",
        "hero": "hero-dark-bold-01",
        "about": "about-split-cards-01",
        "services": "services-bento-02",
        "features": "features-hover-cards-01",
        "testimonials": "testimonials-masonry-01",
        "contact": "contact-minimal-02",
        "footer": "footer-mega-01",
    },
    # --- Portfolio ---
    "portfolio-gallery": {
        "nav": "nav-centered-01",
        "hero": "hero-editorial-01",
        "about": "about-image-showcase-01",
        "gallery": "gallery-masonry-01",
        "services": "services-minimal-list-01",
        "testimonials": "testimonials-grid-01",
        "contact": "contact-minimal-01",
        "footer": "footer-minimal-02",
    },
    "portfolio-minimal": {
        "nav": "nav-minimal-01",
        "hero": "hero-zen-01",
        "about": "about-alternating-01",
        "gallery": "gallery-lightbox-01",
        "contact": "contact-minimal-02",
        "footer": "footer-centered-01",
    },
    "portfolio-creative": {
        "nav": "nav-minimal-01",
        "hero": "hero-brutalist-01",
        "about": "about-bento-01",
        "gallery": "gallery-spotlight-01",
        "services": "services-hover-expand-01",
        "contact": "contact-card-01",
        "footer": "footer-gradient-01",
    },
    # --- E-commerce / Shop ---
    "ecommerce-modern": {
        "nav": "nav-classic-01",
        "hero": "hero-split-01",
        "about": "about-image-showcase-01",
        "services": "services-cards-grid-01",
        "gallery": "gallery-masonry-01",
        "testimonials": "testimonials-carousel-01",
        "contact": "contact-modern-form-01",
        "footer": "footer-multi-col-01",
    },
    "ecommerce-luxury": {
        "nav": "nav-centered-01",
        "hero": "hero-classic-01",
        "about": "about-magazine-01",
        "services": "services-alternating-rows-01",
        "gallery": "gallery-spotlight-01",
        "testimonials": "testimonials-spotlight-01",
        "contact": "contact-minimal-01",
        "footer": "footer-centered-01",
    },
    # --- Business ---
    "business-corporate": {
        "nav": "nav-classic-01",
        "hero": "hero-split-01",
        "about": "about-alternating-01",
        "services": "services-cards-grid-01",
        "features": "features-comparison-01",
        "testimonials": "testimonials-carousel-01",
        "contact": "contact-form-01",
        "footer": "footer-mega-01",
    },
    "business-trust": {
        "nav": "nav-classic-01",
        "hero": "hero-classic-01",
        "about": "about-timeline-01",
        "services": "services-process-steps-01",
        "team": "team-grid-01",
        "testimonials": "testimonials-spotlight-01",
        "contact": "contact-split-map-01",
        "footer": "footer-sitemap-01",
    },
    "business-fresh": {
        "nav": "nav-centered-01",
        "hero": "hero-gradient-03",
        "about": "about-split-cards-01",
        "services": "services-hover-expand-01",
        "features": "features-alternating-01",
        "testimonials": "testimonials-carousel-01",
        "cta": "cta-split-image-01",
        "contact": "contact-modern-form-01",
        "footer": "footer-multi-col-01",
    },
    # --- Blog / Magazine ---
    "blog-editorial": {
        "nav": "nav-centered-01",
        "hero": "hero-editorial-01",
        "about": "about-alternating-01",
        "services": "services-minimal-list-01",
        "gallery": "gallery-lightbox-01",
        "blog": "blog-editorial-grid-01",
        "contact": "contact-card-01",
        "footer": "footer-content-grid-01",
    },
    "blog-dark": {
        "nav": "nav-minimal-01",
        "hero": "hero-neon-01",
        "about": "about-split-cards-01",
        "services": "services-hover-reveal-01",
        "gallery": "gallery-filmstrip-01",
        "blog": "blog-cards-grid-01",
        "contact": "contact-minimal-02",
        "footer": "footer-gradient-01",
    },
    # --- Evento / Community ---
    "event-vibrant": {
        "nav": "nav-minimal-01",
        "hero": "hero-animated-shapes-01",
        "about": "about-bento-01",
        "services": "services-tabs-01",
        "team": "team-carousel-01",
        "schedule": "schedule-tabbed-multi-01",
        "cta": "cta-gradient-animated-01",
        "contact": "contact-modern-form-01",
        "footer": "footer-gradient-01",
    },
    "event-minimal": {
        "nav": "nav-centered-01",
        "hero": "hero-centered-02",
        "about": "about-timeline-01",
        "services": "services-process-steps-01",
        "team": "team-grid-01",
        "schedule": "schedule-tabbed-multi-01",
        "contact": "contact-form-01",
        "footer": "footer-minimal-02",
    },
}

# =========================================================
# Randomized variant pools for variety.
# Each style maps to a POOL of 2-3 compatible variants per section.
# At generation time, one variant is randomly chosen from the pool.
# STYLE_VARIANT_MAP above is kept as deterministic fallback.
# =========================================================
STYLE_VARIANT_POOL: Dict[str, Dict[str, List[str]]] = {
    # --- Restaurant ---
    "restaurant-elegant": {
        "nav": ["nav-classic-01", "nav-centered-01", "nav-topbar-01", "nav-transparent-01"],
        "hero": ["hero-classic-01", "hero-editorial-01", "hero-typewriter-01", "hero-parallax-01", "hero-video-bg-01", "hero-zen-01", "hero-counter-01", "hero-avatar-stack-01"],
        "about": ["about-magazine-01", "about-image-showcase-01", "about-split-scroll-01", "about-alternating-01", "about-timeline-01", "about-progress-bars-01"],
        "services": ["services-alternating-rows-01", "services-minimal-list-01", "services-icon-list-01", "services-cards-grid-01", "services-process-steps-01", "services-timeline-01", "services-numbered-zigzag-01"],
        "gallery": ["gallery-spotlight-01", "gallery-lightbox-01", "gallery-masonry-01", "gallery-filmstrip-01"],
        "testimonials": ["testimonials-spotlight-01", "testimonials-carousel-01", "testimonials-grid-01", "testimonials-card-stack-01", "testimonials-masonry-01", "testimonials-minimal-01", "testimonials-video-01"],
        "contact": ["contact-minimal-01", "contact-form-01", "contact-minimal-02", "contact-card-01", "contact-split-map-01", "contact-two-col-01"],
        "cta": ["cta-banner-01", "cta-split-image-01", "cta-floating-card-01", "cta-newsletter-01", "cta-bold-text-01"],
        "footer": ["footer-centered-01", "footer-minimal-02", "footer-stacked-01", "footer-sitemap-01", "footer-multi-col-01"],
        "booking": ["booking-form-01"],
        "social-proof": ["social-bar-01"],
    },
    "restaurant-cozy": {
        "nav": ["nav-classic-01", "nav-centered-01", "nav-split-cta-01", "nav-topbar-01"],
        "hero": ["hero-organic-01", "hero-typewriter-01", "hero-classic-01", "hero-parallax-01", "hero-split-01", "hero-centered-02", "hero-avatar-stack-01"],
        "about": ["about-split-scroll-01", "about-image-showcase-01", "about-magazine-01", "about-alternating-01", "about-timeline-01", "about-progress-bars-01"],
        "services": ["services-icon-list-01", "services-minimal-list-01", "services-alternating-rows-01", "services-cards-grid-01", "services-process-steps-01", "services-timeline-01", "services-numbered-zigzag-01"],
        "gallery": ["gallery-masonry-01", "gallery-spotlight-01", "gallery-lightbox-01", "gallery-filmstrip-01"],
        "testimonials": ["testimonials-card-stack-01", "testimonials-spotlight-01", "testimonials-carousel-01", "testimonials-grid-01", "testimonials-masonry-01", "testimonials-minimal-01", "testimonials-video-01"],
        "contact": ["contact-card-01", "contact-minimal-01", "contact-form-01", "contact-split-map-01", "contact-modern-form-01", "contact-two-col-01"],
        "cta": ["cta-banner-01", "cta-split-image-01", "cta-floating-card-02", "cta-newsletter-01"],
        "footer": ["footer-multi-col-01", "footer-centered-01", "footer-stacked-01", "footer-sitemap-01", "footer-minimal-02"],
        "booking": ["booking-form-01"],
        "social-proof": ["social-bar-01"],
    },
    "restaurant-modern": {
        "nav": ["nav-minimal-01", "nav-centered-01", "nav-transparent-01", "nav-pill-01"],
        "hero": ["hero-zen-01", "hero-parallax-01", "hero-glassmorphism-01", "hero-split-01", "hero-linear-01", "hero-video-bg-01", "hero-marquee-01"],
        "about": ["about-bento-01", "about-timeline-02", "about-split-cards-01", "about-image-showcase-01", "about-magazine-01", "about-split-scroll-01"],
        "services": ["services-tabs-01", "services-hover-reveal-01", "services-bento-02", "services-hover-expand-01", "services-minimal-list-01", "services-pricing-cards-01", "services-image-reveal-01"],
        "gallery": ["gallery-filmstrip-01", "gallery-masonry-01", "gallery-spotlight-01", "gallery-lightbox-01"],
        "testimonials": ["testimonials-marquee-01", "testimonials-masonry-01", "testimonials-card-stack-01", "testimonials-carousel-01", "testimonials-spotlight-01", "testimonials-quote-wall-01", "testimonials-video-01"],
        "contact": ["contact-modern-form-01", "contact-split-map-01", "contact-card-01", "contact-minimal-02", "contact-form-01", "contact-cards-grid-01"],
        "cta": ["cta-gradient-banner-01", "cta-floating-card-01", "cta-split-image-01", "cta-countdown-01", "cta-bold-text-01"],
        "footer": ["footer-minimal-02", "footer-gradient-01", "footer-cta-band-01", "footer-asymmetric-01", "footer-social-01"],
        "booking": ["booking-form-01"],
        "social-proof": ["social-bar-01"],
    },
    # --- SaaS / Landing Page ---
    "saas-gradient": {
        "nav": ["nav-minimal-01", "nav-classic-01", "nav-pill-01", "nav-split-cta-01", "nav-transparent-01"],
        "hero": ["hero-linear-01", "hero-gradient-03", "hero-animated-shapes-01", "hero-parallax-01", "hero-rotating-01", "hero-glassmorphism-01", "hero-floating-cards-01", "hero-aurora-01", "hero-calculator-01"],
        "about": ["about-timeline-02", "about-bento-01", "about-split-cards-01", "about-image-showcase-01", "about-alternating-01", "about-progress-bars-01"],
        "services": ["services-hover-reveal-01", "services-bento-02", "services-hover-expand-01", "services-tabs-01", "services-cards-grid-01", "services-pricing-cards-01", "services-interactive-tabs-01", "services-numbered-zigzag-01"],
        "features": ["features-bento-01", "features-bento-grid-01", "features-hover-cards-01", "features-tabs-01", "features-icon-showcase-01", "features-showcase-01", "features-elevated-01"],
        "testimonials": ["testimonials-marquee-01", "testimonials-masonry-01", "testimonials-carousel-01", "testimonials-card-stack-01", "testimonials-grid-01", "testimonials-quote-wall-01", "testimonials-video-01"],
        "cta": ["cta-gradient-animated-01", "cta-gradient-banner-01", "cta-floating-card-01", "cta-floating-card-02", "cta-split-image-01", "cta-countdown-01", "cta-bold-text-01"],
        "contact": ["contact-modern-form-01", "contact-split-map-01", "contact-card-01", "contact-form-01", "contact-minimal-02", "contact-cards-grid-01"],
        "footer": ["footer-gradient-01", "footer-mega-01", "footer-cta-band-01", "footer-multi-col-01", "footer-sitemap-01"],
        "comparison": ["comparison-table-01"],
        "social-proof": ["social-bar-01"],
        "app-download": ["app-download-01"],
    },
    "saas-clean": {
        "nav": ["nav-classic-01", "nav-centered-01", "nav-split-cta-01", "nav-pill-01", "nav-topbar-01"],
        "hero": ["hero-centered-02", "hero-split-01", "hero-linear-01", "hero-classic-01", "hero-gradient-03", "hero-counter-01", "hero-aurora-01", "hero-calculator-01", "hero-avatar-stack-01"],
        "about": ["about-alternating-01", "about-image-showcase-01", "about-timeline-02", "about-split-cards-01", "about-bento-01", "about-progress-bars-01"],
        "services": ["services-cards-grid-01", "services-process-steps-01", "services-tabs-01", "services-icon-list-01", "services-alternating-rows-01", "services-pricing-cards-01", "services-interactive-tabs-01", "services-numbered-zigzag-01"],
        "features": ["features-icons-grid-01", "features-bento-01", "features-alternating-01", "features-icon-showcase-01", "features-comparison-01", "features-showcase-01", "features-elevated-01"],
        "testimonials": ["testimonials-grid-01", "testimonials-carousel-01", "testimonials-spotlight-01", "testimonials-card-stack-01", "testimonials-masonry-01", "testimonials-rating-01", "testimonials-video-01"],
        "cta": ["cta-banner-01", "cta-split-image-01", "cta-floating-card-01", "cta-floating-card-02", "cta-gradient-banner-01", "cta-newsletter-01"],
        "contact": ["contact-form-01", "contact-modern-form-01", "contact-minimal-01", "contact-split-map-01", "contact-card-01", "contact-two-col-01"],
        "footer": ["footer-sitemap-01", "footer-multi-col-01", "footer-cta-band-01", "footer-centered-01", "footer-mega-01"],
        "comparison": ["comparison-table-01"],
        "social-proof": ["social-bar-01"],
    },
    "saas-dark": {
        "nav": ["nav-minimal-01", "nav-classic-01", "nav-pill-01", "nav-transparent-01", "nav-split-cta-01"],
        "hero": ["hero-linear-01", "hero-dark-bold-01", "hero-neon-01", "hero-animated-shapes-01", "hero-rotating-01", "hero-gradient-03", "hero-floating-cards-01", "hero-spotlight-01"],
        "about": ["about-split-cards-01", "about-bento-01", "about-timeline-01", "about-timeline-02", "about-magazine-01"],
        "services": ["services-bento-02", "services-hover-expand-01", "services-hover-reveal-01", "services-tabs-01", "services-minimal-list-01", "services-pricing-cards-01", "services-hover-cards-01", "services-image-reveal-01"],
        "features": ["features-bento-01", "features-hover-cards-01", "features-bento-grid-01", "features-tabs-01", "features-comparison-01", "features-elevated-01"],
        "testimonials": ["testimonials-masonry-01", "testimonials-marquee-01", "testimonials-card-stack-01", "testimonials-carousel-01", "testimonials-grid-01", "testimonials-quote-wall-01", "testimonials-video-01"],
        "cta": ["cta-gradient-animated-01", "cta-gradient-banner-01", "cta-floating-card-01", "cta-countdown-01", "cta-bold-text-01"],
        "contact": ["contact-minimal-02", "contact-modern-form-01", "contact-card-01", "contact-form-01", "contact-split-map-01", "contact-cards-grid-01"],
        "footer": ["footer-mega-01", "footer-gradient-01", "footer-cta-band-01", "footer-asymmetric-01", "footer-social-01"],
        "comparison": ["comparison-table-01"],
        "social-proof": ["social-bar-01"],
        "app-download": ["app-download-01"],
    },
    # --- Portfolio ---
    "portfolio-gallery": {
        "nav": ["nav-centered-01", "nav-minimal-01", "nav-sidebar-01", "nav-transparent-01"],
        "hero": ["hero-editorial-01", "hero-zen-01", "hero-typewriter-01", "hero-parallax-01", "hero-video-bg-01", "hero-marquee-01"],
        "about": ["about-image-showcase-01", "about-magazine-01", "about-split-scroll-01", "about-alternating-01", "about-timeline-02"],
        "gallery": ["gallery-masonry-01", "gallery-spotlight-01", "gallery-lightbox-01", "gallery-filmstrip-01"],
        "services": ["services-minimal-list-01", "services-alternating-rows-01", "services-icon-list-01", "services-cards-grid-01", "services-hover-reveal-01"],
        "testimonials": ["testimonials-grid-01", "testimonials-spotlight-01", "testimonials-carousel-01", "testimonials-masonry-01", "testimonials-card-stack-01", "testimonials-minimal-01", "testimonials-video-01"],
        "contact": ["contact-minimal-01", "contact-minimal-02", "contact-form-01", "contact-card-01", "contact-modern-form-01", "contact-two-col-01"],
        "footer": ["footer-minimal-02", "footer-social-01", "footer-asymmetric-01", "footer-centered-01", "footer-stacked-01"],
        "awards": ["awards-timeline-01"],
    },
    "portfolio-minimal": {
        "nav": ["nav-minimal-01", "nav-centered-01", "nav-transparent-01", "nav-sidebar-01"],
        "hero": ["hero-zen-01", "hero-typewriter-01", "hero-editorial-01", "hero-centered-02", "hero-classic-01", "hero-spotlight-01"],
        "about": ["about-alternating-01", "about-split-scroll-01", "about-image-showcase-01", "about-magazine-01", "about-timeline-01"],
        "gallery": ["gallery-lightbox-01", "gallery-spotlight-01", "gallery-masonry-01", "gallery-filmstrip-01"],
        "services": ["services-minimal-list-01", "services-icon-list-01", "services-alternating-rows-01", "services-timeline-01"],
        "testimonials": ["testimonials-spotlight-01", "testimonials-grid-01", "testimonials-carousel-01", "testimonials-minimal-01", "testimonials-video-01"],
        "contact": ["contact-minimal-02", "contact-minimal-01", "contact-form-01", "contact-card-01", "contact-modern-form-01"],
        "footer": ["footer-centered-01", "footer-social-01", "footer-minimal-02", "footer-stacked-01", "footer-asymmetric-01"],
        "awards": ["awards-timeline-01"],
    },
    "portfolio-creative": {
        "nav": ["nav-minimal-01", "nav-centered-01", "nav-sidebar-01", "nav-transparent-01", "nav-pill-01"],
        "hero": ["hero-linear-01", "hero-brutalist-01", "hero-animated-shapes-01", "hero-neon-01", "hero-physics-01", "hero-rotating-01", "hero-marquee-01", "hero-aurora-01"],
        "about": ["about-bento-01", "about-split-cards-01", "about-timeline-02", "about-image-showcase-01", "about-magazine-01"],
        "gallery": ["gallery-spotlight-01", "gallery-filmstrip-01", "gallery-masonry-01", "gallery-lightbox-01"],
        "services": ["services-hover-expand-01", "services-hover-reveal-01", "services-bento-02", "services-tabs-01", "services-cards-grid-01", "services-hover-cards-01", "services-image-reveal-01"],
        "features": ["features-showcase-01", "features-bento-01", "features-hover-cards-01", "features-bento-grid-01", "features-elevated-01"],
        "testimonials": ["testimonials-masonry-01", "testimonials-marquee-01", "testimonials-card-stack-01", "testimonials-carousel-01", "testimonials-grid-01", "testimonials-quote-wall-01", "testimonials-video-01"],
        "contact": ["contact-card-01", "contact-modern-form-01", "contact-split-map-01", "contact-minimal-02", "contact-form-01"],
        "cta": ["cta-gradient-animated-01", "cta-floating-card-01", "cta-split-image-01", "cta-countdown-01", "cta-bold-text-01"],
        "footer": ["footer-gradient-01", "footer-asymmetric-01", "footer-social-01", "footer-cta-band-01", "footer-mega-01"],
        "awards": ["awards-timeline-01"],
    },
    # --- E-commerce / Shop ---
    "ecommerce-modern": {
        "nav": ["nav-classic-01", "nav-centered-01", "nav-split-cta-01", "nav-topbar-01", "nav-pill-01"],
        "hero": ["hero-split-01", "hero-parallax-01", "hero-glassmorphism-01", "hero-classic-01", "hero-gradient-03", "hero-centered-02", "hero-counter-01", "hero-search-01"],
        "about": ["about-image-showcase-01", "about-bento-01", "about-alternating-01", "about-split-cards-01", "about-magazine-01"],
        "services": ["services-cards-grid-01", "services-hover-reveal-01", "services-tabs-01", "services-hover-expand-01", "services-icon-list-01", "services-pricing-cards-01", "services-interactive-tabs-01"],
        "features": ["features-icons-grid-01", "features-bento-01", "features-comparison-01", "features-hover-cards-01", "features-alternating-01", "features-showcase-01", "features-elevated-01"],
        "gallery": ["gallery-masonry-01", "gallery-filmstrip-01", "gallery-lightbox-01", "gallery-spotlight-01"],
        "testimonials": ["testimonials-carousel-01", "testimonials-grid-01", "testimonials-marquee-01", "testimonials-masonry-01", "testimonials-spotlight-01", "testimonials-rating-01", "testimonials-video-01"],
        "cta": ["cta-banner-01", "cta-split-image-01", "cta-floating-card-01", "cta-gradient-banner-01", "cta-countdown-01"],
        "contact": ["contact-modern-form-01", "contact-card-01", "contact-split-map-01", "contact-form-01", "contact-minimal-01", "contact-cards-grid-01"],
        "footer": ["footer-multi-col-01", "footer-mega-01", "footer-cta-band-01", "footer-sitemap-01", "footer-stacked-01"],
        "comparison": ["comparison-table-01"],
        "social-proof": ["social-bar-01"],
        "listings": ["listings-cards-01", "listings-filterable-01"],
    },
    "ecommerce-luxury": {
        "nav": ["nav-centered-01", "nav-classic-01", "nav-topbar-01", "nav-transparent-01"],
        "hero": ["hero-classic-01", "hero-editorial-01", "hero-video-bg-01", "hero-parallax-01", "hero-zen-01", "hero-typewriter-01", "hero-counter-01", "hero-spotlight-01"],
        "about": ["about-magazine-01", "about-image-showcase-01", "about-split-scroll-01", "about-alternating-01", "about-timeline-01", "about-progress-bars-01"],
        "services": ["services-alternating-rows-01", "services-minimal-list-01", "services-icon-list-01", "services-cards-grid-01", "services-process-steps-01", "services-timeline-01", "services-numbered-zigzag-01"],
        "features": ["features-icon-showcase-01", "features-alternating-01", "features-comparison-01", "features-icons-grid-01", "features-showcase-01"],
        "gallery": ["gallery-spotlight-01", "gallery-lightbox-01", "gallery-masonry-01", "gallery-filmstrip-01"],
        "testimonials": ["testimonials-spotlight-01", "testimonials-carousel-01", "testimonials-grid-01", "testimonials-card-stack-01", "testimonials-masonry-01", "testimonials-minimal-01", "testimonials-video-01"],
        "cta": ["cta-banner-01", "cta-split-image-01", "cta-floating-card-01", "cta-newsletter-01", "cta-bold-text-01"],
        "contact": ["contact-minimal-01", "contact-form-01", "contact-minimal-02", "contact-card-01", "contact-split-map-01", "contact-two-col-01"],
        "footer": ["footer-centered-01", "footer-stacked-01", "footer-sitemap-01", "footer-multi-col-01", "footer-minimal-02"],
        "awards": ["awards-timeline-01"],
        "social-proof": ["social-bar-01"],
    },
    # --- Business ---
    "business-corporate": {
        "nav": ["nav-classic-01", "nav-centered-01", "nav-topbar-01", "nav-split-cta-01"],
        "hero": ["hero-split-01", "hero-classic-01", "hero-video-bg-01", "hero-centered-02", "hero-parallax-01", "hero-counter-01", "hero-calculator-01", "hero-avatar-stack-01"],
        "about": ["about-alternating-01", "about-image-showcase-01", "about-timeline-02", "about-timeline-01", "about-magazine-01", "about-progress-bars-01"],
        "services": ["services-cards-grid-01", "services-process-steps-01", "services-tabs-01", "services-alternating-rows-01", "services-icon-list-01", "services-timeline-01", "services-hover-cards-01", "services-numbered-zigzag-01"],
        "features": ["features-comparison-01", "features-icons-grid-01", "features-alternating-01", "features-icon-showcase-01", "features-bento-01", "features-showcase-01", "features-elevated-01"],
        "testimonials": ["testimonials-carousel-01", "testimonials-grid-01", "testimonials-spotlight-01", "testimonials-card-stack-01", "testimonials-masonry-01", "testimonials-rating-01", "testimonials-video-01"],
        "team": ["team-grid-01", "team-carousel-01"],
        "cta": ["cta-banner-01", "cta-split-image-01", "cta-floating-card-01", "cta-gradient-banner-01", "cta-newsletter-01"],
        "contact": ["contact-form-01", "contact-split-map-01", "contact-modern-form-01", "contact-card-01", "contact-minimal-01", "contact-cards-grid-01"],
        "footer": ["footer-mega-01", "footer-sitemap-01", "footer-cta-band-01", "footer-multi-col-01", "footer-stacked-01"],
        "comparison": ["comparison-table-01"],
        "social-proof": ["social-bar-01"],
        "awards": ["awards-timeline-01"],
        "booking": ["booking-form-01"],
    },
    "business-trust": {
        "nav": ["nav-classic-01", "nav-centered-01", "nav-topbar-01", "nav-split-cta-01"],
        "hero": ["hero-classic-01", "hero-editorial-01", "hero-split-01", "hero-centered-02", "hero-video-bg-01", "hero-counter-01", "hero-avatar-stack-01"],
        "about": ["about-timeline-01", "about-magazine-01", "about-image-showcase-01", "about-alternating-01", "about-split-scroll-01", "about-progress-bars-01"],
        "services": ["services-process-steps-01", "services-alternating-rows-01", "services-cards-grid-01", "services-icon-list-01", "services-tabs-01", "services-timeline-01", "services-numbered-zigzag-01"],
        "features": ["features-icons-grid-01", "features-comparison-01", "features-alternating-01", "features-icon-showcase-01", "features-showcase-01", "features-elevated-01"],
        "team": ["team-grid-01", "team-carousel-01"],
        "testimonials": ["testimonials-spotlight-01", "testimonials-carousel-01", "testimonials-grid-01", "testimonials-card-stack-01", "testimonials-masonry-01", "testimonials-rating-01", "testimonials-video-01"],
        "cta": ["cta-banner-01", "cta-split-image-01", "cta-floating-card-02", "cta-newsletter-01"],
        "contact": ["contact-split-map-01", "contact-form-01", "contact-modern-form-01", "contact-card-01", "contact-minimal-01", "contact-two-col-01"],
        "footer": ["footer-sitemap-01", "footer-mega-01", "footer-stacked-01", "footer-multi-col-01", "footer-centered-01"],
        "social-proof": ["social-bar-01"],
        "awards": ["awards-timeline-01"],
        "booking": ["booking-form-01"],
    },
    "business-fresh": {
        "nav": ["nav-centered-01", "nav-minimal-01", "nav-pill-01", "nav-split-cta-01", "nav-transparent-01"],
        "hero": ["hero-linear-01", "hero-gradient-03", "hero-animated-shapes-01", "hero-rotating-01", "hero-glassmorphism-01", "hero-floating-cards-01", "hero-calculator-01"],
        "about": ["about-split-cards-01", "about-bento-01", "about-timeline-02", "about-image-showcase-01", "about-alternating-01", "about-progress-bars-01"],
        "services": ["services-hover-expand-01", "services-hover-reveal-01", "services-bento-02", "services-tabs-01", "services-cards-grid-01", "services-pricing-cards-01", "services-interactive-tabs-01", "services-image-reveal-01"],
        "features": ["features-bento-01", "features-alternating-01", "features-bento-grid-01", "features-hover-cards-01", "features-icon-showcase-01", "features-elevated-01"],
        "testimonials": ["testimonials-carousel-01", "testimonials-marquee-01", "testimonials-masonry-01", "testimonials-card-stack-01", "testimonials-grid-01", "testimonials-quote-wall-01", "testimonials-video-01"],
        "cta": ["cta-split-image-01", "cta-gradient-animated-01", "cta-floating-card-01", "cta-gradient-banner-01", "cta-floating-card-02", "cta-countdown-01", "cta-bold-text-01"],
        "contact": ["contact-modern-form-01", "contact-card-01", "contact-split-map-01", "contact-form-01", "contact-minimal-02", "contact-cards-grid-01"],
        "footer": ["footer-multi-col-01", "footer-gradient-01", "footer-cta-band-01", "footer-social-01", "footer-mega-01"],
        "comparison": ["comparison-table-01"],
        "social-proof": ["social-bar-01"],
        "app-download": ["app-download-01"],
    },
    # --- Blog / Magazine ---
    "blog-editorial": {
        "nav": ["nav-centered-01", "nav-classic-01", "nav-transparent-01", "nav-topbar-01"],
        "hero": ["hero-editorial-01", "hero-typewriter-01", "hero-zen-01", "hero-classic-01", "hero-split-01", "hero-marquee-01"],
        "about": ["about-alternating-01", "about-magazine-01", "about-split-scroll-01", "about-image-showcase-01", "about-timeline-01"],
        "services": ["services-minimal-list-01", "services-icon-list-01", "services-alternating-rows-01", "services-cards-grid-01", "services-process-steps-01", "services-timeline-01"],
        "features": ["features-showcase-01", "features-alternating-01", "features-icon-showcase-01"],
        "testimonials": ["testimonials-spotlight-01", "testimonials-grid-01", "testimonials-carousel-01", "testimonials-card-stack-01", "testimonials-masonry-01", "testimonials-minimal-01", "testimonials-video-01"],
        "gallery": ["gallery-lightbox-01", "gallery-spotlight-01", "gallery-masonry-01", "gallery-filmstrip-01"],
        "cta": ["cta-newsletter-01", "cta-banner-01", "cta-split-image-01"],
        "contact": ["contact-card-01", "contact-minimal-01", "contact-form-01", "contact-minimal-02", "contact-modern-form-01", "contact-two-col-01"],
        "footer": ["footer-sitemap-01", "footer-centered-01", "footer-asymmetric-01", "footer-stacked-01", "footer-multi-col-01", "footer-content-grid-01"],
        "blog": ["blog-editorial-grid-01", "blog-minimal-01"],
    },
    "blog-dark": {
        "nav": ["nav-minimal-01", "nav-centered-01", "nav-pill-01", "nav-transparent-01"],
        "hero": ["hero-neon-01", "hero-dark-bold-01", "hero-brutalist-01", "hero-linear-01", "hero-animated-shapes-01", "hero-floating-cards-01", "hero-spotlight-01"],
        "about": ["about-split-cards-01", "about-bento-01", "about-timeline-01", "about-timeline-02", "about-magazine-01"],
        "services": ["services-hover-reveal-01", "services-bento-02", "services-hover-expand-01", "services-tabs-01", "services-minimal-list-01", "services-image-reveal-01"],
        "testimonials": ["testimonials-masonry-01", "testimonials-marquee-01", "testimonials-card-stack-01", "testimonials-carousel-01", "testimonials-grid-01", "testimonials-quote-wall-01", "testimonials-video-01"],
        "gallery": ["gallery-filmstrip-01", "gallery-masonry-01", "gallery-spotlight-01", "gallery-lightbox-01"],
        "contact": ["contact-minimal-02", "contact-card-01", "contact-modern-form-01", "contact-form-01", "contact-split-map-01", "contact-cards-grid-01"],
        "cta": ["cta-gradient-animated-01", "cta-floating-card-01", "cta-gradient-banner-01", "cta-countdown-01", "cta-bold-text-01"],
        "footer": ["footer-gradient-01", "footer-mega-01", "footer-social-01", "footer-asymmetric-01", "footer-cta-band-01", "footer-content-grid-01"],
        "blog": ["blog-cards-grid-01", "blog-editorial-grid-01", "blog-minimal-01"],
    },
    # --- Evento / Community ---
    "event-vibrant": {
        "nav": ["nav-minimal-01", "nav-centered-01", "nav-pill-01", "nav-transparent-01", "nav-split-cta-01"],
        "hero": ["hero-animated-shapes-01", "hero-gradient-03", "hero-parallax-01", "hero-physics-01", "hero-rotating-01", "hero-neon-01", "hero-marquee-01", "hero-aurora-01", "hero-countdown-01"],
        "about": ["about-bento-01", "about-timeline-02", "about-split-cards-01", "about-image-showcase-01", "about-alternating-01"],
        "services": ["services-tabs-01", "services-hover-expand-01", "services-bento-02", "services-hover-reveal-01", "services-cards-grid-01", "services-hover-cards-01"],
        "features": ["features-bento-grid-01", "features-hover-cards-01", "features-tabs-01", "features-bento-01", "features-elevated-01"],
        "team": ["team-carousel-01", "team-grid-01"],
        "testimonials": ["testimonials-marquee-01", "testimonials-masonry-01", "testimonials-card-stack-01", "testimonials-carousel-01", "testimonials-grid-01", "testimonials-quote-wall-01", "testimonials-video-01"],
        "cta": ["cta-gradient-animated-01", "cta-gradient-banner-01", "cta-floating-card-01", "cta-floating-card-02", "cta-split-image-01", "cta-countdown-01", "cta-bold-text-01"],
        "contact": ["contact-modern-form-01", "contact-card-01", "contact-split-map-01", "contact-form-01", "contact-minimal-02", "contact-cards-grid-01"],
        "footer": ["footer-gradient-01", "footer-cta-band-01", "footer-social-01", "footer-mega-01", "footer-asymmetric-01"],
        "schedule": ["schedule-tabbed-multi-01"],
        "social-proof": ["social-bar-01"],
        "booking": ["booking-form-01"],
    },
    "event-minimal": {
        "nav": ["nav-centered-01", "nav-classic-01", "nav-transparent-01", "nav-minimal-01"],
        "hero": ["hero-centered-02", "hero-typewriter-01", "hero-zen-01", "hero-editorial-01", "hero-classic-01", "hero-counter-01", "hero-aurora-01", "hero-countdown-01"],
        "about": ["about-timeline-01", "about-alternating-01", "about-split-scroll-01", "about-image-showcase-01", "about-magazine-01"],
        "services": ["services-process-steps-01", "services-cards-grid-01", "services-icon-list-01", "services-minimal-list-01", "services-alternating-rows-01", "services-timeline-01"],
        "team": ["team-grid-01", "team-carousel-01"],
        "testimonials": ["testimonials-spotlight-01", "testimonials-carousel-01", "testimonials-grid-01", "testimonials-card-stack-01", "testimonials-minimal-01", "testimonials-video-01"],
        "cta": ["cta-banner-01", "cta-split-image-01", "cta-floating-card-01", "cta-newsletter-01"],
        "contact": ["contact-form-01", "contact-minimal-01", "contact-minimal-02", "contact-card-01", "contact-split-map-01", "contact-two-col-01"],
        "footer": ["footer-minimal-02", "footer-stacked-01", "footer-centered-01", "footer-sitemap-01", "footer-social-01"],
        "schedule": ["schedule-tabbed-multi-01"],
        "booking": ["booking-form-01"],
    },
}

# Randomized pools for default section types (faq, pricing, stats, etc.)
DEFAULT_SECTION_VARIANT_POOLS: Dict[str, List[str]] = {
    "faq": ["faq-accordion-01", "faq-accordion-02", "faq-two-column-01", "faq-search-01"],
    "pricing": ["pricing-cards-01", "pricing-toggle-01", "pricing-toggle-02", "pricing-comparison-01", "pricing-minimal-01", "pricing-dark-parallax-01"],
    "stats": ["stats-counters-01", "stats-wave-01"],
    "logos": ["logos-marquee-01"],
    "process": ["process-steps-01", "process-horizontal-01", "process-cards-01"],
    "timeline": ["timeline-vertical-01"],
    "blog": ["blog-editorial-grid-01", "blog-cards-grid-01", "blog-minimal-01"],
    "awards": ["awards-timeline-01"],
    "listings": ["listings-cards-01", "listings-filterable-01"],
    "donations": ["donations-progress-01", "donations-form-01"],
    "comparison": ["comparison-table-01"],
    "booking": ["booking-form-01"],
    "app-download": ["app-download-01"],
    "social-proof": ["social-bar-01"],
    "schedule": ["schedule-tabbed-multi-01"],
}

# =========================================================
# STYLE CSS PROFILES: Per-style visual overrides
# Each profile creates a distinct spatial/visual rhythm so
# sites don't all share the same Tailwind defaults.
# =========================================================
STYLE_CSS_PROFILES: Dict[str, Dict[str, str]] = {
    "restaurant-elegant": {
        "space_section": "7rem",
        "max_width": "75rem",
        "radius": "1rem",
        "shadow": "0 25px 60px -12px rgba(0,0,0,0.12)",
        "h1_scale": "clamp(3rem, 6vw + 1rem, 6rem)",
        "h2_scale": "clamp(2.2rem, 4vw + 0.5rem, 4rem)",
        "animation_speed": "1.2",
        "letter_spacing": "-0.03em",
    },
    "restaurant-cozy": {
        "space_section": "6rem",
        "max_width": "72rem",
        "radius": "1.25rem",
        "shadow": "0 10px 30px -5px rgba(0,0,0,0.1)",
        "h1_scale": "clamp(2.5rem, 5vw + 0.5rem, 4.5rem)",
        "h2_scale": "clamp(2rem, 3vw + 0.5rem, 3.2rem)",
        "animation_speed": "1.0",
        "letter_spacing": "-0.02em",
    },
    "restaurant-modern": {
        "space_section": "5rem",
        "max_width": "76rem",
        "radius": "0.5rem",
        "shadow": "0 4px 20px rgba(0,0,0,0.08)",
        "h1_scale": "clamp(2.8rem, 6vw + 0.5rem, 5.5rem)",
        "h2_scale": "clamp(1.8rem, 3vw + 0.5rem, 3rem)",
        "animation_speed": "0.8",
        "letter_spacing": "-0.04em",
    },
    "saas-gradient": {
        "space_section": "5.5rem",
        "max_width": "76rem",
        "radius": "0.75rem",
        "shadow": "0 8px 32px rgba(0,0,0,0.12)",
        "h1_scale": "clamp(2.8rem, 5.5vw + 1rem, 5.5rem)",
        "h2_scale": "clamp(2rem, 3vw + 0.5rem, 3.5rem)",
        "animation_speed": "0.7",
        "letter_spacing": "-0.03em",
    },
    "saas-clean": {
        "space_section": "5rem",
        "max_width": "72rem",
        "radius": "0.5rem",
        "shadow": "0 2px 12px rgba(0,0,0,0.06)",
        "h1_scale": "clamp(2.5rem, 5vw + 0.5rem, 4.5rem)",
        "h2_scale": "clamp(1.8rem, 2.5vw + 0.5rem, 3rem)",
        "animation_speed": "0.6",
        "letter_spacing": "-0.02em",
    },
    "saas-dark": {
        "space_section": "5rem",
        "max_width": "74rem",
        "radius": "0.75rem",
        "shadow": "0 4px 24px rgba(0,0,0,0.3)",
        "h1_scale": "clamp(2.5rem, 5vw + 1rem, 5.5rem)",
        "h2_scale": "clamp(1.8rem, 3vw + 0.5rem, 3rem)",
        "animation_speed": "0.7",
        "letter_spacing": "0em",
    },
    "portfolio-gallery": {
        "space_section": "7rem",
        "max_width": "80rem",
        "radius": "0.25rem",
        "shadow": "none",
        "h1_scale": "clamp(3.5rem, 7vw + 1rem, 7rem)",
        "h2_scale": "clamp(2.2rem, 4vw + 0.5rem, 4rem)",
        "animation_speed": "1.3",
        "letter_spacing": "-0.04em",
    },
    "portfolio-minimal": {
        "space_section": "8rem",
        "max_width": "68rem",
        "radius": "0",
        "shadow": "none",
        "h1_scale": "clamp(2.5rem, 4vw + 1rem, 4.5rem)",
        "h2_scale": "clamp(1.8rem, 3vw + 0.5rem, 3rem)",
        "animation_speed": "1.5",
        "letter_spacing": "-0.02em",
    },
    "portfolio-creative": {
        "space_section": "6rem",
        "max_width": "80rem",
        "radius": "1.5rem",
        "shadow": "0 12px 40px rgba(0,0,0,0.15)",
        "h1_scale": "clamp(3.5rem, 8vw + 1rem, 8rem)",
        "h2_scale": "clamp(2.2rem, 4vw + 1rem, 4.5rem)",
        "animation_speed": "0.9",
        "letter_spacing": "-0.05em",
    },
    "ecommerce-modern": {
        "space_section": "5.5rem",
        "max_width": "76rem",
        "radius": "0.75rem",
        "shadow": "0 8px 24px rgba(0,0,0,0.08)",
        "h1_scale": "clamp(2.5rem, 5vw + 0.5rem, 5rem)",
        "h2_scale": "clamp(1.8rem, 3vw + 0.5rem, 3rem)",
        "animation_speed": "0.8",
        "letter_spacing": "-0.02em",
    },
    "ecommerce-luxury": {
        "space_section": "7rem",
        "max_width": "74rem",
        "radius": "1rem",
        "shadow": "0 20px 50px -10px rgba(0,0,0,0.15)",
        "h1_scale": "clamp(3rem, 6vw + 1rem, 6rem)",
        "h2_scale": "clamp(2.2rem, 4vw + 0.5rem, 4rem)",
        "animation_speed": "1.2",
        "letter_spacing": "-0.03em",
    },
    "business-corporate": {
        "space_section": "6rem",
        "max_width": "76rem",
        "radius": "0.5rem",
        "shadow": "0 4px 16px rgba(0,0,0,0.08)",
        "h1_scale": "clamp(2.5rem, 5vw + 0.5rem, 5rem)",
        "h2_scale": "clamp(2rem, 3vw + 0.5rem, 3.2rem)",
        "animation_speed": "1.0",
        "letter_spacing": "-0.02em",
    },
    "business-trust": {
        "space_section": "6rem",
        "max_width": "74rem",
        "radius": "0.75rem",
        "shadow": "0 6px 20px rgba(0,0,0,0.08)",
        "h1_scale": "clamp(2.5rem, 5vw + 0.5rem, 4.5rem)",
        "h2_scale": "clamp(2rem, 3vw + 0.5rem, 3.2rem)",
        "animation_speed": "1.0",
        "letter_spacing": "-0.02em",
    },
    "business-fresh": {
        "space_section": "5.5rem",
        "max_width": "76rem",
        "radius": "1rem",
        "shadow": "0 8px 28px rgba(0,0,0,0.1)",
        "h1_scale": "clamp(2.8rem, 5.5vw + 1rem, 5.5rem)",
        "h2_scale": "clamp(2rem, 3vw + 0.5rem, 3.5rem)",
        "animation_speed": "0.8",
        "letter_spacing": "-0.03em",
    },
    "blog-editorial": {
        "space_section": "7.5rem",
        "max_width": "70rem",
        "radius": "0",
        "shadow": "none",
        "h1_scale": "clamp(3rem, 6vw + 1rem, 6.5rem)",
        "h2_scale": "clamp(2.2rem, 4vw + 0.5rem, 4rem)",
        "animation_speed": "1.3",
        "letter_spacing": "-0.04em",
    },
    "blog-dark": {
        "space_section": "6rem",
        "max_width": "72rem",
        "radius": "0.5rem",
        "shadow": "0 4px 20px rgba(0,0,0,0.25)",
        "h1_scale": "clamp(2.5rem, 5vw + 0.5rem, 5rem)",
        "h2_scale": "clamp(2rem, 3vw + 0.5rem, 3.2rem)",
        "animation_speed": "1.0",
        "letter_spacing": "-0.02em",
    },
    "event-vibrant": {
        "space_section": "4.5rem",
        "max_width": "80rem",
        "radius": "1.5rem",
        "shadow": "0 12px 36px rgba(0,0,0,0.15)",
        "h1_scale": "clamp(3.5rem, 8vw + 1rem, 9rem)",
        "h2_scale": "clamp(2.2rem, 4vw + 1rem, 4.5rem)",
        "animation_speed": "0.5",
        "letter_spacing": "-0.05em",
    },
    "event-minimal": {
        "space_section": "7rem",
        "max_width": "72rem",
        "radius": "0.25rem",
        "shadow": "none",
        "h1_scale": "clamp(3rem, 6vw + 1rem, 6rem)",
        "h2_scale": "clamp(2rem, 3.5vw + 0.5rem, 3.5rem)",
        "animation_speed": "1.2",
        "letter_spacing": "-0.03em",
    },
}

# =========================================================
# SECTION BACKGROUND ACCENTS: Break monotonous bg/bg-alt alternation
# by injecting special backgrounds on specific sections per style.
# =========================================================
SECTION_BG_ACCENTS: Dict[str, str] = {
    "restaurant-elegant": """
    /* Testimonials: warm gradient overlay */
    #testimonials { background: linear-gradient(135deg, var(--color-bg-alt), rgba(var(--color-primary-rgb), 0.06)) !important; }
    /* CTA: inverted dark section */
    #cta { background: var(--color-text) !important; color: var(--color-bg) !important; }
    #cta h2, #cta p, #cta span { color: var(--color-bg) !important; }
    #cta [style*="color: var(--color-text)"] { color: var(--color-bg) !important; }
    """,
    "restaurant-cozy": """
    /* About: subtle warm pattern */
    #about { background: radial-gradient(circle at 20% 80%, rgba(var(--color-primary-rgb), 0.04), transparent 50%), var(--color-bg-alt) !important; }
    /* Testimonials: warm tint */
    #testimonials { background: linear-gradient(180deg, var(--color-bg), rgba(var(--color-secondary-rgb), 0.05)) !important; }
    """,
    "restaurant-modern": """
    /* Testimonials: full dark inversion */
    #testimonials { background: var(--color-text) !important; color: var(--color-bg) !important; }
    #testimonials h2, #testimonials p, #testimonials span, #testimonials blockquote { color: var(--color-bg) !important; }
    #testimonials [style*="color: var(--color-text)"] { color: var(--color-bg) !important; }
    #testimonials [style*="color: var(--color-text-muted)"] { color: rgba(var(--color-bg-rgb), 0.6) !important; }
    """,
    "saas-gradient": """
    /* Features: gradient mesh */
    #features { background: linear-gradient(135deg, var(--color-bg), rgba(var(--color-primary-rgb), 0.08) 40%, rgba(var(--color-secondary-rgb), 0.06)) !important; }
    /* CTA: vibrant gradient */
    #cta { background: linear-gradient(135deg, var(--color-primary), var(--color-secondary)) !important; color: #fff !important; }
    #cta h2, #cta p, #cta span { color: #fff !important; }
    """,
    "saas-clean": """
    /* Testimonials: subtle dot pattern */
    #testimonials { background: radial-gradient(circle, rgba(var(--color-primary-rgb), 0.08) 1px, transparent 1px), var(--color-bg-alt) !important; background-size: 24px 24px !important; }
    """,
    "saas-dark": """
    /* Features: glow gradient */
    #features { background: radial-gradient(ellipse at 50% 0%, rgba(var(--color-primary-rgb), 0.12), transparent 70%), var(--color-bg) !important; }
    /* CTA: accent glow */
    #cta { background: radial-gradient(ellipse at 50% 100%, rgba(var(--color-accent-rgb), 0.15), transparent 60%), var(--color-bg-alt) !important; }
    """,
    "portfolio-gallery": """
    /* About: clean white break */
    #about { background: #fff !important; }
    """,
    "portfolio-minimal": """
    /* Testimonials: single thin top border as accent */
    #testimonials { border-top: 1px solid rgba(var(--color-primary-rgb), 0.15); }
    """,
    "portfolio-creative": """
    /* Services: diagonal gradient */
    #services { background: linear-gradient(160deg, var(--color-bg), rgba(var(--color-primary-rgb), 0.1) 30%, rgba(var(--color-accent-rgb), 0.08) 70%, var(--color-bg-alt)) !important; }
    /* Testimonials: inverted */
    #testimonials { background: var(--color-text) !important; color: var(--color-bg) !important; }
    #testimonials h2, #testimonials p, #testimonials span, #testimonials blockquote { color: var(--color-bg) !important; }
    #testimonials [style*="color: var(--color-text)"] { color: var(--color-bg) !important; }
    """,
    "ecommerce-modern": """
    /* Testimonials: soft radial spotlight */
    #testimonials { background: radial-gradient(ellipse at 50% 50%, rgba(var(--color-primary-rgb), 0.06), transparent 70%), var(--color-bg) !important; }
    /* CTA: accent band */
    #cta { background: linear-gradient(90deg, var(--color-primary), var(--color-secondary)) !important; color: #fff !important; }
    #cta h2, #cta p, #cta span { color: #fff !important; }
    """,
    "ecommerce-luxury": """
    /* Testimonials: dark luxurious section */
    #testimonials { background: var(--color-text) !important; color: var(--color-bg) !important; }
    #testimonials h2, #testimonials p, #testimonials span, #testimonials blockquote { color: var(--color-bg) !important; }
    #testimonials [style*="color: var(--color-text)"] { color: var(--color-bg) !important; }
    #testimonials [style*="color: var(--color-text-muted)"] { color: rgba(var(--color-bg-rgb), 0.5) !important; }
    /* CTA: gold-tinted */
    #cta { background: linear-gradient(135deg, var(--color-bg-alt), rgba(var(--color-primary-rgb), 0.08)) !important; }
    """,
    "business-corporate": """
    /* Stats/features: corporate dark band */
    #stats, #features { background: var(--color-text) !important; color: var(--color-bg) !important; }
    #stats h2, #stats p, #stats span, #features h2, #features p, #features span { color: var(--color-bg) !important; }
    #stats [style*="color: var(--color-text)"], #features [style*="color: var(--color-text)"] { color: var(--color-bg) !important; }
    """,
    "business-trust": """
    /* Testimonials: warm trust gradient */
    #testimonials { background: linear-gradient(180deg, rgba(var(--color-primary-rgb), 0.04), var(--color-bg-alt)) !important; }
    """,
    "business-fresh": """
    /* Features: playful gradient mesh */
    #features { background: linear-gradient(135deg, rgba(var(--color-primary-rgb), 0.06), transparent 40%, rgba(var(--color-secondary-rgb), 0.06)) !important; }
    /* CTA: vibrant gradient */
    #cta { background: linear-gradient(135deg, var(--color-primary), var(--color-accent)) !important; color: #fff !important; }
    #cta h2, #cta p, #cta span { color: #fff !important; }
    """,
    "blog-editorial": """
    /* Pull-quote accent on testimonials */
    #testimonials { border-top: 3px solid var(--color-primary); border-bottom: 3px solid var(--color-primary); }
    """,
    "blog-dark": """
    /* About: glow from below */
    #about { background: radial-gradient(ellipse at 50% 100%, rgba(var(--color-primary-rgb), 0.1), transparent 60%), var(--color-bg) !important; }
    """,
    "event-vibrant": """
    /* CTA: explosive gradient */
    #cta { background: linear-gradient(135deg, var(--color-primary), var(--color-secondary), var(--color-accent)) !important; color: #fff !important; }
    #cta h2, #cta p, #cta span { color: #fff !important; }
    /* Testimonials: dark with glow */
    #testimonials { background: radial-gradient(ellipse at 30% 50%, rgba(var(--color-primary-rgb), 0.15), transparent 50%), var(--color-text) !important; color: var(--color-bg) !important; }
    #testimonials h2, #testimonials p, #testimonials span, #testimonials blockquote { color: var(--color-bg) !important; }
    """,
    "event-minimal": """
    /* Subtle section dividers */
    #about, #services, #contact { border-top: 1px solid rgba(var(--color-text-rgb), 0.08); }
    """,
}

# =========================================================
# BLUEPRINTS: Optimal section ordering per business category.
# Each blueprint defines the narrative flow that converts best
# for that business type.
# =========================================================
BLUEPRINTS: Dict[str, List[str]] = {
    "restaurant": [
        "hero", "about", "gallery", "services", "testimonials",
        "team", "faq", "contact",
    ],
    "saas": [
        "hero", "features", "about", "services", "testimonials",
        "pricing", "cta", "faq", "contact",
    ],
    "portfolio": [
        "hero", "gallery", "about", "services", "testimonials",
        "contact",
    ],
    "ecommerce": [
        "hero", "services", "gallery", "about", "testimonials",
        "pricing", "cta", "faq", "contact",
    ],
    "business": [
        "hero", "about", "services", "features", "team",
        "testimonials", "cta", "contact",
    ],
    "blog": [
        "hero", "about", "services", "gallery", "contact",
    ],
    "event": [
        "hero", "about", "services", "team", "gallery",
        "cta", "faq", "contact",
    ],
    "custom": [
        "hero", "about", "services", "gallery", "testimonials",
        "contact",
    ],
}

# =========================================================
# HARMONY GROUPS: Visual families for cross-section cohesion.
# When generating a site, one harmony group is selected and
# component variants are preferentially chosen from it.
# =========================================================
HARMONY_GROUPS: Dict[str, List[str]] = {
    "bento": [
        "bento", "masonry", "hover-expand", "grid", "split-cards",
    ],
    "editorial": [
        "alternating", "magazine", "spotlight", "editorial", "image-showcase",
        "split-scroll",
    ],
    "interactive": [
        "hover-expand", "hover-reveal", "tabs", "hover-cards", "card-stack",
    ],
    "classic": [
        "classic", "centered", "grid", "cards", "carousel", "form",
        "process-steps", "icon-list", "icons-grid",
    ],
    "dark-bold": [
        "dark-bold", "neon", "brutalist", "gradient", "animated-shapes",
    ],
    "organic": [
        "organic", "zen", "scroll", "minimal", "typewriter", "parallax",
    ],
}
