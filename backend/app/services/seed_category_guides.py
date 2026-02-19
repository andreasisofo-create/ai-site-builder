"""
Seed script for Category Design Guides.
Populates the SQLite database with expert-level design knowledge for all website categories.
The AI consults this before building any site to know HOW each category should look.

Run: python -m app.services.seed_category_guides
"""

from app.services.design_knowledge import upsert_category_guide, get_category_guide

GUIDES = {
    # ====================================================
    # RESTAURANT / RISTORANTE
    # ====================================================
    "restaurant": {
        "structure": """Flusso ideale delle sezioni:
1. Hero (immagine full-screen del piatto signature o sala, overlay scuro 40-60%)
2. Concept / About (storia del ristorante, filosofia culinaria, max 3 paragrafi)
3. Menu / Specialità (griglia 2-3 colonne con foto, prezzi, descrizioni evocative)
4. Gallery (masonry grid o slider full-width, minimo 6 foto di qualità)
5. Testimonials / Recensioni (citazioni con stelle, fonte Google/TripAdvisor)
6. Location & Orari (mappa integrata + indirizzo + orari formattati in tabella)
7. Prenotazione / CTA (form semplice o link a TheFork/Google)
8. Footer (contatti, social, partita IVA)""",

        "visual_style": """Palette colori per ristoranti:
- Elegante: nero/oro (#1A1A2E + #D4AF37), crema caldo (#FAF7F2), bordeaux (#722F37)
- Casual/Trattoria: verde oliva (#556B2F), arancione caldo (#E8751A), avorio (#FFFDF7)
- Moderno: navy profondo (#0A1628), bianco puro (#FAFAFA), accento corallo (#FF6B6B)
- Sushi/Giapponese: nero (#0D0D0D), rosso (#C41E3A), bianco riso (#F5F5DC)
- Pizzeria: rosso pomodoro (#D32F2F), verde basilico (#388E3C), giallo (#FBC02D)
Sfondo SEMPRE ricco, mai #ffffff puro. Usare toni caldi per creare atmosfera accogliente.""",

        "ux_patterns": """- Navbar: trasparente su hero, diventa solida on scroll. Logo a sinistra, menu hamburger su mobile
- CTA principale: "Prenota un Tavolo" sempre visibile, bottone con colore accent
- Menu: tabs per categorie (Antipasti, Primi, Secondi, Dolci) con smooth scroll
- Mobile: hero ridotto a 70vh, menu collassabile per categoria, telefono cliccabile
- Prenotazione: form con data, ora, numero persone. Max 4 campi visibili
- Velocità: immagini ottimizzate, lazy loading su gallery, hero image preloaded""",

        "hero_section": """Hero ristorante DEVE essere:
- Immagine full-screen (100vh) del piatto migliore o della sala illuminata
- Overlay gradient dal basso (rgba(0,0,0,0.3) a rgba(0,0,0,0.7))
- Titolo grande con font serif elegante (Playfair Display, DM Serif)
- Sottotitolo: tagline emozionale ("Dal 1985, l'arte della cucina italiana")
- CTA: "Prenota" + "Scopri il Menu" (due bottoni affiancati)
- Animazione: testo text-split con fade-in, bottoni fade-up con delay
- NO video autoplay (rallenta il sito). Sì a immagine statica di altissima qualità""",

        "content_strategy": """Contenuto above the fold: nome ristorante + tagline + CTA prenotazione
Tono: evocativo, sensoriale, specifico. MAI generico.
- BUONO: "Ravioli al tartufo nero di Norcia, sfoglia tirata a mano ogni mattina"
- CATTIVO: "Offriamo piatti di alta qualità con ingredienti freschi"
Storytelling: la storia del fondatore, il legame col territorio, la filosofia culinaria.
Menu: descrivere ogni piatto con 1-2 righe evocative, specificare allergeni se possibile.
Usare parole sensoriali: croccante, vellutato, profumato, fragrante, avvolgente.""",

        "animations": """- Hero: parallax lento su immagine di sfondo (data-speed="0.3")
- Titoli sezione: text-split con chars animation
- Cards menu: stagger fade-up (0.1s delay tra ogni card)
- Gallery: scale-in on scroll, hover zoom (image-zoom)
- Numeri (anni, coperti): data-counter con animazione incremento
- Sezione about: reveal-left per immagine, fade-right per testo
- CTA prenotazione: magnetic button effect
- Background parallax su sezione concept""",

        "cta_design": """CTA primario: "Prenota un Tavolo" / "Riserva il tuo tavolo"
- Colore: accent color (oro, corallo, o contrasto forte con bg)
- Stile: pill (border-radius: 99px) per elegante, sharp per moderno
- Hover: translateY(-2px) + shadow intensificato
- Mobile: full-width, posizione sticky in basso
CTA secondario: "Vedi il Menu" / "Scopri i nostri piatti" - outline button o text link
Telefono: sempre cliccabile (tel:), icona telefono accanto""",

        "photo_treatment": """Le foto fanno il 70% della differenza per un ristorante:
- HERO: foto piatto dall'alto (flat-lay) o prospettiva 45° con sfondo sfocato
- MENU: ogni piatto su sfondo neutro, illuminazione calda laterale, 4:3 ratio
- GALLERY: mix di piatti (60%), sala (20%), dettagli (10%), chef (10%)
- Trattamento: leggera vignettatura, contrasto +10%, saturazione +5% per calore
- MAI: foto stock generiche, piatti su piatto bianco senza contesto, luci fredde
- Formato: WebP, max 400KB per immagine, 1200px lato lungo""",

        "typography": """Font heading: serif con carattere - Playfair Display (wght 700), DM Serif Display, Cormorant Garamond
Font body: sans-serif pulito - Inter, Plus Jakarta Sans, DM Sans a 16-18px
Font menu prezzi: monospace leggero o tabular numbers
Gerarchia: h1 (48-64px), h2 (36-42px), h3 (24-28px), body (16-18px), prezzi (14-16px)
Line-height: 1.6 per body, 1.2 per heading. Letter-spacing: -0.02em per heading serif.
Accento calligrafico per "specials" o nomi piatti: font corsivo (Pinyon Script, Dancing Script) SOLO per 1-2 parole decorative.""",

        "common_mistakes": """EVITARE assolutamente:
- Menu come PDF scaricabile (deve essere HTML navigabile)
- Foto piatti di bassa qualità o scure
- Muro di testo nella sezione about
- Mancanza del bottone prenotazione above the fold
- Orari non aggiornati o assenti
- Mappa non cliccabile
- Font troppo piccoli per il menu
- Colori freddi (blu, grigio) per un ristorante
- Slider automatici troppo veloci sulle foto
- Mancanza di prezzo sui piatti (il cliente vuole sapere prima)""",

        "trends_2025": """Trend 2025-2026 per siti ristorante:
- Dark mode elegante con accenti oro/rame
- Micro-animazioni su hover delle foto (zoom + overlay info)
- Sezione "Chef's Story" con parallax scrolling
- Integrazione prenotazione inline (senza redirect)
- Video brevi (5-10s) di preparazione piatti come sfondo
- Typography bold: titoli enormi (80-120px) che fanno statement
- Bento grid per il menu al posto della lista tradizionale
- Glassmorphism cards per le recensioni
- Scroll-triggered number counters (anni, piatti serviti, stelleMichelin)"""
    },

    # ====================================================
    # SAAS / TECH
    # ====================================================
    "saas": {
        "structure": """Flusso ideale delle sezioni:
1. Hero (headline boldissima + sottotitolo + CTA + product screenshot/mockup)
2. Social Proof (loghi clienti, "Usato da 10.000+ aziende")
3. Features / Come Funziona (3-6 feature cards con icone)
4. Bento Grid (showcase features con screenshot UI)
5. Pricing (3 piani: Free/Pro/Enterprise in cards affiancate)
6. Testimonials (quote con foto, nome, ruolo, azienda)
7. FAQ (accordion espandibile)
8. Final CTA (headline + singolo bottone prominente)
9. Footer (prodotto, risorse, azienda, legal)""",

        "visual_style": """Palette colori SaaS:
- Dark premium: navy (#0F172A), viola (#7C3AED), ciano (#22D3EE), bg alt (#1E293B)
- Clean light: bianco (#FAFAFA), blu (#3B82F6), grigio pallido (#F1F5F9)
- Gradient bold: viola-to-blu gradient hero, sfondo bianco sezioni
- Neon dark: nero (#09090B), verde neon (#22C55E), grigio (#27272A)
Glassmorphism: backdrop-blur-xl + bg-white/5 + border-white/10 per cards su dark bg
Gradient text per hero headline: bg-clip-text text-transparent bg-gradient-to-r""",

        "ux_patterns": """- Navbar: sticky, trasparente→opaca on scroll, CTA "Get Started" a destra
- Pricing: evidenziare il piano "Pro" (più venduto) con bordo colorato e badge "Popolare"
- Feature comparison: toggle mensile/annuale con sconto evidenziato
- Social proof: logo carousel automatico, contatore utenti animato
- Mobile: hero senza screenshot (solo testo+CTA), features in stack verticale
- Scroll: sezioni con padding generoso (py-24 a py-32), alternare bg colori""",

        "hero_section": """Hero SaaS DEVE essere:
- Headline ENORME (56-80px) con 1-2 righe max, font bold (800-900 weight)
- Gradient text o highlight colorato sulla parola chiave
- Sottotitolo in grigio (18-20px), max 2 righe
- CTA prominente: "Inizia Gratis" (bg colore primario) + "Vedi Demo" (outline)
- Sotto i CTA: social proof ("Gratis per sempre • 10.000+ utenti • Nessuna carta richiesta")
- Product screenshot o mockup flottante con shadow-2xl e angolo leggero
- Background: gradient radiale sottile o mesh-gradient, o pattern dots""",

        "content_strategy": """Above the fold: value proposition chiara (cosa fa + per chi + risultato)
- BUONO: "Automatizza le tue fatture in 30 secondi. Zero errori, zero stress."
- CATTIVO: "La soluzione innovativa per la gestione aziendale"
Features: verbo d'azione + beneficio concreto, non feature tecnica
- BUONO: "Risparmia 10 ore/settimana con report automatici"
- CATTIVO: "Dashboard con grafici personalizzabili"
Pricing: prezzi chiari, feature list per piano, CTA per ogni piano""",

        "animations": """- Hero: headline text-split per parole, screenshot fade-up con delay
- Logo carousel: marquee infinito (data-animate="marquee")
- Feature cards: stagger fade-up con 0.15s delay
- Pricing cards: scale-in simultaneo
- Numeri/stats: data-counter per metriche ("10,000+ utenti")
- Bento grid: stagger-scale per celle
- CTA buttons: magnetic effect
- Section transitions: blur-in per titoli sezione
- Scroll progress bar in navbar""",

        "cta_design": """CTA primario: "Inizia Gratis" / "Prova Gratis" / "Crea Account"
- Colore: primario vivace, gradient per premium feel
- Size: px-8 py-4, text-lg font-bold, rounded-xl
- Hover: translateY(-2px) + shadow-lg colorata (shadow-primary/25)
CTA secondario: "Vedi Demo" / "Scopri di Più" - outline o ghost button
Nella pricing: ogni piano ha il suo CTA, il piano Pro ha CTA più grande e colorato
Badge sotto CTA: "Nessuna carta di credito" / "Setup in 2 minuti" """,

        "photo_treatment": """SaaS NON usa foto tradizionali, usa:
- Product screenshots con rounded corners (16px) e shadow-2xl
- UI mockups su sfondi gradient o su device (laptop/phone frame)
- Illustrazioni custom o 3D renders per features
- Icone Lucide/Heroicons per feature cards (24-32px, stroke-width 1.5)
- Avatar cerchio per testimonials (48-64px)
- Logo clienti: grayscale, opacity 0.5, hover → full color
- MAI: foto stock persone in ufficio, stock photography generica""",

        "typography": """Font heading: geometric bold - Space Grotesk (700-800), Sora, Unbounded, Outfit
Font body: sans-serif leggibile - Inter, DM Sans, Plus Jakarta Sans a 16px
Heading h1: 48-72px, font-weight 800, letter-spacing -0.03em, line-height 1.1
Heading h2: 36-48px, font-weight 700
Body: 16-18px, text-gray-600 (light) o text-gray-300 (dark), line-height 1.7
Stats/numbers: font-mono o tabular-nums, dimensione oversize (48-72px)
MAI: font serif per SaaS (tranne casi luxury SaaS)""",

        "common_mistakes": """EVITARE:
- Hero senza screenshot del prodotto (l'utente vuole VEDERE cosa compra)
- Pricing nascosto o assente (trasparenza = fiducia)
- Troppo testo, troppo poco visual
- Feature list senza icone (muro di testo)
- CTA vaghi ("Scopri di più" al posto di "Inizia Gratis")
- Mancanza di social proof (loghi, numeri, testimonials)
- Layout noioso: tutto uguale, nessuna sezione che spicca
- Font generici (Roboto, Open Sans) senza personalità""",

        "trends_2025": """Trend 2025-2026 per SaaS:
- Bento grid layout per feature showcase (à la Apple)
- Glassmorphism cards con backdrop-blur
- Gradient mesh backgrounds (Stripe-style)
- Micro-interactions hover su ogni card/bottone
- Dark mode di default per tech products
- 3D elements leggeri (CSS transforms, non WebGL)
- Animated gradients su CTA hero
- Scroll-triggered product demos inline
- AI-powered feature highlights con sparkle icons"""
    },

    # ====================================================
    # PORTFOLIO / CREATIVE
    # ====================================================
    "portfolio": {
        "structure": """Flusso ideale:
1. Hero (nome + ruolo + statement artistico, minimal)
2. Selected Works (griglia progetti 2-3 colonne, full-width su hover)
3. About / Bio (foto + testo breve + skills/competenze)
4. Process / Come Lavoro (3-4 step visuali)
5. Testimonials (citazioni clienti)
6. Contact (form minimale o solo email/social)
7. Footer (social links prominenti)""",

        "visual_style": """Portfolio palette:
- Minimal B&W: nero (#0D0D0D), bianco (#FAFAFA), accento unico vivace (#FF3366 o #00FF88)
- Creative bold: viola scuro (#1A1A2E), magenta (#E94560), giallo (#FDCB6E)
- Warm neutral: off-white (#F5F0EB), charcoal (#2D3436), terracotta (#CC5A47)
- Dark moody: quasi-nero (#0A0A0A), grigio (#636E72), accent neon (#7DF9FF)
Spazio bianco generoso è OBBLIGATORIO. Meno è più. Il lavoro deve parlare, non il design.""",

        "ux_patterns": """- Navbar: minimalissima - solo nome a sinistra, "Work" "About" "Contact" a destra
- Gallery: hover su progetto = titolo + categoria overlay, click = case study
- Case study: full-page con mockup, brief, soluzione, risultati
- Cursor: custom cursor è un forte differenziatore (cerchio che segue il mouse)
- Mobile: gallery a colonna singola, immagini full-width
- Scroll: smooth, ogni progetto è un "momento" separato
- Filtri: tabs per categoria (Branding, Web, UI/UX, Motion)""",

        "hero_section": """Hero portfolio:
- OPZIONE A: Nome gigante (80-120px) + ruolo sotto + nessuna immagine
- OPZIONE B: Video reel autoplay muted in background + nome overlay
- OPZIONE C: Progetto hero full-screen con testo overlay minimale
- Font: bold sans-serif (Space Grotesk 900) o serif elegante (Playfair Display)
- Animazione: typewriter per il ruolo, o text-split lettera per lettera
- Colore: bianco su nero, o nero su bianco. Minimal.
- CTA: freccia scroll-down animata, o "Vedi i miei lavori" discreto""",

        "content_strategy": """Portfolio = MOSTRA, non raccontare
- Max 8-12 progetti selezionati (qualità > quantità)
- Ogni progetto: 1 hero image + titolo + categoria + 1 riga descrizione
- Case study: Brief → Approccio → Soluzione → Risultati (con numeri)
- Bio: max 150 parole. Chi sei, cosa fai, perché sei diverso.
- Skills: visualizza con barre o tag, non liste lunghe
- Tono: sicuro ma non arrogante. "Creo esperienze digitali che convertono" """,

        "animations": """- Hero: text-split lettera per lettera con delay
- Gallery: stagger fade-up, hover → scale(1.03) + overlay
- Progetto hover: clip-reveal o blur-in per titolo
- Scroll: parallax leggero su immagini progetti
- Cursore custom: cerchio che scala su hover elementi
- Page transitions: fade tra case studies
- About photo: reveal-left con clip-path
- Skills bars: width animata on scroll (da 0 a valore)
- Contact: magnetic button per CTA""",

        "cta_design": """CTA portfolio: sottili ma efficaci
- "Lavoriamo insieme" / "Parliamone" / "Inizia un progetto"
- Stile: outline minimalista o text-link con freccia animata
- Posizione: fine pagina + navbar (discrete)
- Email: grande, cliccabile, centrata nella sezione contact
- Social: icone grandi (32px), riga orizzontale, hover colorato
- NO bottoni appariscenti colorati (stonano con l'estetica minimal)""",

        "photo_treatment": """I progetti SONO le foto:
- Mockup realistici: laptop, phone, tablet per progetti web/app
- Immagini full-bleed per progetti di branding (packaging, poster)
- Aspect ratio: 16:9 per hero, 4:3 o 1:1 per griglia
- Hover: leggero zoom (1.03) + overlay semitrasparente con titolo
- Filtro: nessuno o leggera desaturazione per coerenza visiva
- Lightbox: click apre visualizzazione grande con navigazione
- Lazy loading obbligatorio per gallerie con molte immagini""",

        "typography": """Font heading: personalità forte - Space Grotesk (800-900), Sora, Unbounded, o serif caratteristico come Playfair Display
Font body: minimal leggibile - Inter, DM Sans a 16px, colore grigio medio
Nome hero: 72-120px, lettera singola per animazione
Progetto titoli: 24-32px, font-weight 600
Body testo: 16px, max-width 65ch, line-height 1.8
Accento: un font display SOLO per il nome/hero (es. Instrument Serif italic)""",

        "common_mistakes": """EVITARE:
- Troppi progetti (massimo 12, seleziona i migliori)
- Mancanza di case study dettagliati (solo screenshots non bastano)
- Design che sovrasta il lavoro (il portfolio deve essere cornice, non soggetto)
- Nessuna informazione di contatto chiara
- Navigazione complessa (un portfolio deve essere lineare)
- Auto-descrizioni generiche ("Sono un designer appassionato...")
- Immagini non ottimizzate (portfolio pesanti = bounce rate alto)
- Font troppo decorativi per il body text""",

        "trends_2025": """Trend 2025-2026 per portfolio:
- Layout asimmetrico con grid CSS irregolari
- Custom cursor effects (cerchio, blend-mode)
- Horizontal scroll per progetti selezionati
- Animazioni GSAP pesanti ma fluide (clip-path, text-split)
- Dark mode con un singolo accent color neon
- Tipografia oversize per il hero (100px+)
- Case study interattivi con scroll-triggered animations
- Micro-interactions su ogni hover
- Video previews on hover (3-5 secondi, muted)"""
    },

    # ====================================================
    # ECOMMERCE / SHOP
    # ====================================================
    "ecommerce": {
        "structure": """Flusso ideale:
1. Hero (prodotto hero o offerta principale, full-width)
2. Categorie Prodotti (griglia 3-4 colonne con immagini)
3. Prodotti in Evidenza / Bestseller (carousel o griglia)
4. USP / Vantaggi (spedizione gratuita, garanzia, pagamento sicuro)
5. Testimonials / Recensioni (con stelle e foto)
6. Newsletter signup (sconto benvenuto)
7. Footer (spedizioni, resi, contatti, pagamenti accettati)""",

        "visual_style": """Palette e-commerce:
- Luxury: nero (#0A0A0A), oro (#C9A96E), bianco (#FFFFFF), grigio (#8A8A8A)
- Modern clean: bianco (#FFFFFF), nero (#111111), accent verde (#22C55E) per CTA
- Fashion: beige (#F5F0EB), nero (#1A1A1A), accent terracotta (#C67D5B)
- Tech: dark (#0F172A), blu (#3B82F6), bianco (#F8FAFC)
CTA "Aggiungi al carrello" DEVE usare il colore più vivace della palette.
Badge sconto: rosso (#EF4444) o arancione (#F97316) per urgenza.""",

        "ux_patterns": """- Navbar: logo | ricerca | account | carrello (con badge quantità)
- Filtri: sidebar su desktop, bottom-sheet su mobile
- Prodotto: immagini grandi, zoom on hover, galleria scorrevole
- CTA: "Aggiungi al Carrello" grande e colorato, sempre visibile
- Prezzi: grande, grassetto, prezzo scontato in rosso con barrato originale
- Trust signals: icone sicurezza sotto CTA (lucchetto, spedizione, reso)
- Mobile: bottom bar fissa con carrello e menu
- Quick view: modal al click su prodotto dalla griglia""",

        "hero_section": """Hero e-commerce:
- Prodotto principale fotografato professionalmente su sfondo pulito
- Headline: nome prodotto o collezione + tagline corta
- Prezzo ben visibile se c'è un'offerta
- CTA: "Scopri la Collezione" o "Acquista Ora" in colore primario
- Badge: "NUOVO" / "-30%" / "BEST SELLER" per urgenza
- Slider: se multiple promozioni, max 3 slide con autoplay lento (5s)
- Mobile: immagine 1:1, testo sotto, CTA full-width""",

        "content_strategy": """E-commerce: vendere con le parole
- Titoli prodotto: specifici, includere materiale/taglia/colore chiave
- Descrizioni: benefici prima, specifiche tecniche dopo
- Prezzo: prominente, mai nascosto. Se c'è sconto, mostrare risparmio in €
- Recensioni: stelle + numero recensioni + 1-2 citazioni selezionate
- Urgenza: "Solo 3 rimasti" / "Offerta valida fino a..."
- Trust: "Spedizione gratuita sopra 49€" / "Reso entro 30 giorni"
- Cross-sell: "Potresti anche amare..." sotto il prodotto""",

        "animations": """- Hero: fade-in prodotto + slide-up testo
- Product cards: hover → scale(1.05) + shadow-lg + mostra quick-view
- Carrello: badge bounce animation quando si aggiunge item
- Prezzo: data-counter per countdown offerta
- Categorie: stagger fade-up
- Gallery prodotto: slide orizzontale con snap
- Add to cart button: magnetic + feedback visivo (checkmark animation)
- Filtri: smooth transition altezza container
- Recensioni: stagger fade-in""",

        "cta_design": """CTA e-commerce:
- "Aggiungi al Carrello": GRANDE (px-8 py-4), colore pieno, icon carrello
- "Acquista Ora": variante diretta, skip cart
- "Scopri": outline/ghost per categorie
- Hover: scurimento + translateY(-2px) + shadow
- Stato loading: spinner inline durante add-to-cart
- Badge sconto: position absolute, top-right, rosso con testo bianco
- Colore CTA: il più contrastante della palette (mai grigio)""",

        "photo_treatment": """Foto prodotto = conversione:
- Sfondo bianco puro (#FFFFFF) o neutro per prodotto singolo
- Lifestyle shots: prodotto in contesto d'uso
- Multiple angolazioni: fronte, retro, dettaglio, indossato
- Zoom: hover su desktop, pinch su mobile
- Aspect ratio: 1:1 per griglia, 4:5 per prodotto singolo
- Consistency: stessa illuminazione e sfondo per tutti i prodotti
- Peso: max 200KB per thumbnail, max 500KB per full
- Lazy loading obbligatorio per griglie prodotto""",

        "typography": """Font heading: moderno pulito - Plus Jakarta Sans (700), Sora, Space Grotesk
Font body: massima leggibilità - Inter, DM Sans a 16px
Prezzi: font-weight 700, font-size 24-32px per prezzo principale
Prezzo scontato: text-decoration line-through + colore grigio per originale, rosso per nuovo
Nome prodotto griglia: 14-16px, font-weight 500, 2 righe max (overflow ellipsis)
CTA: 16-18px, font-weight 700, letter-spacing 0.02em
Badge/tag: 10-12px, uppercase, font-weight 600""",

        "common_mistakes": """EVITARE:
- Foto prodotto di bassa qualità o inconsistenti
- Prezzo nascosto o difficile da trovare
- CTA poco visibile o troppo piccolo
- Mancanza di trust signals (spedizioni, resi, sicurezza)
- Nessuna recensione o social proof
- Navigazione complessa (troppe categorie annidate)
- Checkout complicato (troppi step)
- Mancanza di ricerca prodotti
- Filtri che ricaricano la pagina invece di aggiornare inline""",

        "trends_2025": """Trend 2025-2026 per e-commerce:
- Product cards con 3D tilt on hover
- Quick-view modale senza cambio pagina
- AR preview (prova virtuale) per fashion/arredamento
- Video prodotto inline (5-15s loop)
- Personalized recommendations sezione
- Checkout single-page con progress bar
- Social commerce: integrazione UGC (User Generated Content)
- Glassmorphism per carrello/checkout overlay
- Badge animati per sconti/nuovo arrivo"""
    },

    # ====================================================
    # BUSINESS / CORPORATE / STUDIO PROFESSIONALE
    # ====================================================
    "business": {
        "structure": """Flusso ideale:
1. Hero (headline chiara + sottotitolo + CTA + immagine/illustrazione)
2. Servizi (3-6 cards con icona + titolo + descrizione)
3. Chi Siamo / About (team, storia, valori - con foto)
4. Numeri / Stats (contatori animati: anni esperienza, clienti, progetti)
5. Casi Studio / Portfolio (2-4 progetti con risultati)
6. Testimonials (citazioni con nome, ruolo, azienda)
7. FAQ (accordion)
8. Contatto (form + mappa + telefono)
9. Footer (servizi, azienda, contatti, legal)""",

        "visual_style": """Palette business/corporate:
- Trust classico: blu navy (#1E3A5F), bianco (#FAFAFA), grigio (#64748B), accent arancione (#F97316)
- Moderno fresco: teal (#0F766E), crema (#FAF7F2), nero (#1A1A2E), accent lime (#84CC16)
- Premium: nero (#0A0A0A), grigio (#4B5563), oro (#D4AF37), bianco (#F8FAFC)
- Studio legale: blu scuro (#1B2A4A), bordeaux (#8B1A1A), avorio (#FFFFF0)
Toni sobri ma NON noiosi. Accent color vivace per CTA e highlight.""",

        "ux_patterns": """- Navbar: logo + servizi + chi siamo + contatti + CTA "Richiedi Consulenza"
- Servizi: griglia 3 colonne desktop, stack mobile, icone Lucide/Heroicons
- Stats: sezione con sfondo diverso, numeri grandi animati
- Form contatto: max 5 campi, validazione inline, submit con feedback
- Mobile: CTA sticky in basso, menu hamburger, telefono cliccabile
- Trust: loghi clienti, certificazioni, anni esperienza
- Pagine secondarie: link a pagine servizio dettagliate (se multi-page)""",

        "hero_section": """Hero business:
- Headline diretta: cosa fai + per chi ("Soluzioni digitali per PMI che vogliono crescere")
- Sottotitolo: beneficio concreto in 1-2 righe
- CTA: "Richiedi Consulenza Gratuita" + "Scopri i Servizi"
- Immagine: foto team professionale, illustrazione custom, o pattern astratto
- Stile: split layout (testo sinistra, immagine destra) o centrato con bg
- Animazione: fade-up per testo, scale-in per immagine
- NO: slogan vaghi, foto stock evidenti, troppo testo""",

        "content_strategy": """Business = credibilità
- Headline: promessa specifica con risultato misurabile
- Servizi: beneficio + come lo facciamo + per chi, non feature list
- About: storia umana, non corporate-speak. Mostrare le persone.
- Stats: numeri reali (anni esperienza, clienti serviti, risultati ottenuti)
- Testimonials: con nome completo, ruolo, azienda, possibilmente foto
- Case study: problema → soluzione → risultato (con numeri)
- Tono: professionale ma umano, mai burocratico""",

        "animations": """- Hero: text-split per headline, fade-up per sottotitolo e CTA
- Servizi cards: stagger fade-up
- Stats: data-counter (partono da 0, arrivano al valore on scroll)
- About: reveal parallax per foto team
- Testimonials: slider automatico o stagger fade-in
- FAQ: accordion con smooth height transition
- Form: focus animation su input fields
- CTA sezioni: magnetic button
- Section dividers: wave SVG o curve CSS""",

        "cta_design": """CTA business:
- "Richiedi Consulenza" / "Contattaci" / "Parla con un Esperto"
- Colore: accent color pieno, prominente
- Stile: rounded-xl, px-8 py-4, shadow-lg
- Posizione: hero + fine ogni sezione servizi + footer
- Telefono: bottone "Chiama Ora" su mobile, cliccabile
- Form CTA: "Invia Richiesta" con feedback success/error
- Urgenza soft: "Consulenza gratuita" / "Rispondiamo in 24h" """,

        "photo_treatment": """Foto business: professionali ma umane
- Team: foto professionali ma naturali, no stock, sfondo coerente
- Ufficio: ambiente di lavoro reale, illuminazione naturale
- Clienti: loghi in griglia, grayscale con hover colore
- Case study: screenshot risultati, grafici, before/after
- Icone: Lucide/Heroicons monocromatiche, consistenti
- NO: strette di mano stock, uffici generici vuoti, foto con watermark""",

        "typography": """Font heading: autorevole moderno - Plus Jakarta Sans (700-800), Space Grotesk, Outfit
Font body: leggibile professionale - Inter, DM Sans, Source Sans 3 a 16px
Heading h1: 42-56px, font-weight 700-800
Heading h2: 32-40px, font-weight 700
Stats: font-weight 800, 48-64px, colore accent
Body: 16px, grigio scuro (non nero pieno), line-height 1.7
Citazioni testimonial: font serif italic (DM Serif) 18-20px""",

        "common_mistakes": """EVITARE:
- Linguaggio corporate vuoto ("soluzioni innovative a 360 gradi")
- Mancanza di differenziazione (sembrare come tutti gli altri)
- Nessun numero o prova concreta
- Foto stock generiche ovunque
- Form contatto con troppi campi (nome, email, messaggio bastano)
- FAQ assente (le domande frequenti riducono il carico di supporto)
- Servizi descritti in modo troppo vago
- CTA poco visibile o assente nelle sezioni intermedie""",

        "trends_2025": """Trend 2025-2026 per business:
- Hero con illustrazioni custom o 3D leggero
- Stats sezione con background gradient
- Bento grid per servizi (invece di grid uniforme)
- Testimonials video brevi (30s) invece di solo testo
- FAQ con ricerca inline
- Dark mode opzionale (toggle)
- Micro-animazioni su icone servizio
- Chatbot/AI assistant widget nell'angolo
- Scroll-triggered case study reveals"""
    },

    # ====================================================
    # BLOG / EDITORIAL
    # ====================================================
    "blog": {
        "structure": """Flusso ideale homepage blog:
1. Hero / Featured Post (articolo in evidenza, grande immagine)
2. Grid Articoli Recenti (2-3 colonne)
3. Categorie (pills o sidebar navigabile)
4. Newsletter Signup (form prominente)
5. About / Chi Scrive (bio autore con foto)
6. Footer (categorie, social, about, legal)""",

        "visual_style": """Palette blog:
- Editorial classico: bianco (#FFFFFF), nero (#111111), accent rosso (#E63946), grigio (#6B7280)
- Dark reader: nero (#0D1117), grigio (#21262D), bianco (#F0F6FC), accent blu (#58A6FF)
- Minimal warm: crema (#FAF7F2), charcoal (#374151), accent teal (#0D9488)
- Magazine bold: bianco (#FAFAFA), nero (#000), accent arancione (#F97316)
Sfondo pulitissimo, zero distrazioni. Il contenuto è il re.""",

        "ux_patterns": """- Navbar: logo + categorie + ricerca + newsletter CTA
- Articolo: max-width 680px centrato, typography ottimizzata per lettura
- Sidebar: solo su desktop, sticky con indice articolo (TOC)
- Mobile: articolo full-width, font-size 18px per leggibilità
- Scroll: progress bar in alto che mostra % articolo letto
- Related posts: griglia 3 articoli correlati in fondo
- Commenti: sezione semplice o integrazione Disqus/Giscus
- Reading time: "5 min di lettura" sotto il titolo""",

        "hero_section": """Hero blog homepage:
- Featured post gigante: immagine + categoria badge + titolo + excerpt + autore + data
- Layout: immagine a sinistra, testo a destra (split) o immagine sopra, testo sotto
- Titolo: 36-48px, font serif per eleganza editoriale
- CTA: "Leggi" discreto, o click su tutta la card
- Sotto: griglia 3 colonne con articoli recenti
- Animazione: fade-up per card, nessuna animazione invasiva""",

        "content_strategy": """Blog = leggibilità e valore
- Titoli: specifici, concreti, con numero o promessa chiara
- BUONO: "7 Errori di UX che Ti Costano il 30% dei Clienti"
- CATTIVO: "Pensieri sul Design"
- Excerpt: 2-3 righe che AGGANCIANO il lettore
- Categorie: max 6-8, nomi chiari e brevi
- Autore: nome + foto + bio 1 riga sotto ogni articolo
- Data: formato leggibile ("15 Febbraio 2026")
- CTA newsletter: valore chiaro ("Ricevi 1 articolo a settimana")""",

        "animations": """- MINIME: il blog deve essere veloce e leggibile
- Card articoli: fade-up on scroll, stagger leggero
- Hero: fade-in, nessun effetto pesante
- Progress bar: scroll-progress in cima alla pagina
- Newsletter form: subtle scale on focus
- Immagini articolo: lazy loading con blur-up placeholder
- NO parallax, NO text-split pesanti, NO animazioni che rallentano la lettura""",

        "cta_design": """CTA blog:
- Newsletter: "Iscriviti" semplice, form email + bottone
- Colore: accent color, non troppo appariscente
- "Leggi l'articolo": text link con freccia, non bottone
- Social share: icone piccole in fondo all'articolo
- Related posts: click su card, non bottone separato
- Author link: "Tutti gli articoli di [Nome]" """,

        "photo_treatment": """Immagini blog:
- Cover articolo: 16:9, alta qualità, rilevante al contenuto
- Inline images: max-width del testo (680px), con caption
- Autore avatar: 48px cerchio
- Categorie: icone o colori, non immagini
- Ottimizzazione: WebP, srcset per responsive, lazy loading
- ALT text descrittivo per ogni immagine (accessibilità + SEO)
- NO: immagini decorative che non aggiungono valore""",

        "typography": """Font heading: serif editoriale - Playfair Display, DM Serif Display, Instrument Serif
Font body: alta leggibilità - Source Serif 4 o Georgia (serif) per contenuto lungo, Inter per UI
Articolo body: 18-20px, line-height 1.8, max-width 680px, color #374151
Heading articolo: 36-48px, font-weight 700, line-height 1.2
Categoria: 12px uppercase, font-weight 600, colore accent, letter-spacing 0.1em
Data: 14px, grigio chiaro
Code blocks: font mono (JetBrains Mono, Fira Code), bg grigio chiaro""",

        "common_mistakes": """EVITARE:
- Font body troppo piccolo (< 16px) o line-height stretto
- Articoli senza immagine cover
- Layout troppo largo (oltre 800px per il testo)
- Mancanza di data pubblicazione
- Categorie troppe e confuse
- Newsletter popup aggressivo (appare dopo 2 secondi)
- Nessun related posts in fondo all'articolo
- Sidebar sovraffollata di widget inutili
- Mancanza di ricerca""",

        "trends_2025": """Trend 2025-2026 per blog:
- Reader mode / minimal UI durante lettura
- Scroll progress indicator
- Table of Contents sticky sidebar
- Dark mode automatico basato su preferenze sistema
- Typography-first design (contenuto > decorazione)
- Newsletter con preview dell'ultimo articolo
- AI-generated reading time e summary
- Substack-style minimalism"""
    },

    # ====================================================
    # EVENT / EVENTO
    # ====================================================
    "event": {
        "structure": """Flusso ideale:
1. Hero (nome evento + data + location + countdown + CTA biglietti)
2. About / Cos'è (descrizione evento, value proposition)
3. Programma / Schedule (timeline oraria)
4. Speaker / Artisti (griglia con foto + bio)
5. Location / Venue (mappa + info logistiche)
6. Biglietti / Pricing (tipologie biglietto con prezzi)
7. Sponsor / Partner (loghi)
8. FAQ (domande pratiche: parcheggio, dress code, ecc.)
9. Footer (contatti, social, note legali)""",

        "visual_style": """Palette eventi:
- Conferenza tech: dark (#0A0A1A), viola (#7C3AED), ciano (#06B6D4), bianco (#F0F0F0)
- Festival musicale: nero (#000000), rosa neon (#FF2D87), giallo (#FFD700), bianco (#FFFFFF)
- Matrimonio: crema (#FFF8F0), oro rosa (#B76E79), verde salvia (#9CAF88)
- Corporate event: navy (#1E3A5F), bianco (#FFFFFF), accent arancione (#FB923C)
- Workshop: bianco (#FAFAFA), nero (#111), accent colorato per categoria
Colori vivaci e energetici. L'evento deve EMOZIONARE visivamente.""",

        "ux_patterns": """- Navbar: nome evento + countdown mini + CTA "Biglietti" (sempre visibile)
- Countdown: prominente in hero, aggiorna in tempo reale
- Schedule: timeline verticale, filtri per giornata/track
- Speaker cards: foto + nome + ruolo, click → bio completa
- Biglietti: comparison table, evidenziare il piano consigliato
- Mobile: CTA sticky in basso "Acquista Biglietto", schedule scrollabile
- Social: integrazione hashtag, share buttons prominenti""",

        "hero_section": """Hero evento:
- IMPATTO MASSIMO: gradient bold o immagine evento precedente
- Nome evento: 60-80px, font bold o display
- Data + Luogo: prominenti sotto il titolo (icone calendario + pin)
- Countdown: grande, animato, giorni:ore:minuti:secondi
- CTA: "Acquista Biglietti" grande e luminoso + "Scopri il Programma"
- Background: gradient radiale, particelle animate, o foto con overlay
- Animazione: text-split per nome, counter animato, CTA magnetic""",

        "content_strategy": """Evento = urgenza + esclusività
- Headline: nome evento + edizione (se ricorrente)
- Data e luogo DEVONO essere visibili in 1 secondo
- Value proposition: "Perché partecipare?" in 3 bullet points
- Speaker: nome, foto, titolo breve, link LinkedIn/bio
- Schedule: orario preciso, track se multi-sala
- Early bird: sconto evidenziato con deadline chiara
- Testimonials: citazioni edizioni precedenti + foto/video
- Numeri: partecipanti precedenti, speaker, sessioni""",

        "animations": """- Hero: text-split per nome evento, scale-in per countdown
- Countdown: numeri che flippano (flip-clock animation)
- Speaker cards: stagger fade-up, hover → scale + glow
- Schedule: timeline reveal on scroll (reveal-up per ogni slot)
- Stats: data-counter per numeri partecipanti/speaker
- CTA: magnetic button + gradient-flow su hover
- Background: gradient-flow lento o particelle
- Section transitions: clip-reveal per sezioni impattanti""",

        "cta_design": """CTA evento:
- "Acquista Biglietti" / "Registrati Ora" / "Prenota il tuo Posto"
- Colore: il più vivace della palette, gradient per premium
- Stile: grande (px-10 py-5), bold, con icona ticket/arrow
- Hover: glow effect + translateY(-3px)
- Early bird badge: "Risparmia 30%" accanto al prezzo
- Urgenza: "Ultimi 50 posti" / "Prezzo sale tra 5 giorni"
- Mobile: sticky bottom bar con prezzo + CTA
- Posizione: hero + fine programma + fine speaker + footer""",

        "photo_treatment": """Foto evento:
- Hero: foto edizione precedente (folla, palco, energia) o gradient
- Speaker: foto professionali quadrate, bordo arrotondato
- Gallery edizioni passate: masonry grid o slider
- Venue: foto location + mappa interattiva
- Sponsor: loghi su riga, grayscale opzionale
- Video: trailer evento 30-60s in sezione dedicata
- User-generated: foto social con hashtag evento""",

        "typography": """Font heading: display impattante - Unbounded (800-900), Space Grotesk (800), Sora (800)
Font body: leggibile - Inter, DM Sans, Plus Jakarta Sans a 16px
Nome evento: 56-80px, font-weight 900, letter-spacing -0.03em
Countdown numbers: 48-72px, font-mono o tabular-nums
Schedule: 14-16px, orari in bold, titoli sessione 18px
Speaker nome: 18-20px, font-weight 700
Prezzo: 32-48px, font-weight 800""",

        "common_mistakes": """EVITARE:
- Data e luogo non immediatamente visibili
- Mancanza di countdown (crea urgenza)
- Speaker senza foto
- Schedule confuso o non navigabile
- Prezzi nascosti ("Contattaci per info" = bounce)
- Nessun link a mappa/indicazioni per il venue
- FAQ assente (parcheggio? dress code? badge?)
- Nessun contenuto da edizioni precedenti (prova sociale)
- CTA acquisto non prominente""",

        "trends_2025": """Trend 2025-2026 per siti evento:
- Countdown animato con flip-clock
- Speaker cards con video bio on hover
- Schedule interattivo con filtri e bookmark
- Biglietto digitale con QR code
- Live streaming integration per eventi ibridi
- Animated gradient backgrounds
- 3D venue map interattiva
- Social wall con feed live hashtag
- Gamification: early bird rewards, referral codes"""
    },

    # ====================================================
    # CUSTOM / GENERICO (fallback)
    # ====================================================
    "custom": {
        "structure": """Struttura adattabile al business:
1. Hero (messaggio principale, identità brand)
2. Chi Siamo / About (storia, valori)
3. Servizi/Prodotti (offerta principale)
4. Gallery / Portfolio (lavori o ambientazioni)
5. Testimonials / Social Proof
6. Contatto (form o CTA diretto)
7. Footer""",

        "visual_style": """Scegli i colori in base alla PERSONALITÀ del brand:
- Caldo/accogliente: toni ambra, terracotta, crema
- Freddo/professionale: blu navy, grigio, bianco
- Energico/giovane: viola, rosa, gradient neon
- Elegante/lusso: nero, oro, champagne
- Naturale/eco: verde, beige, legno
SEMPRE: contrasto alto per leggibilità, accent vivace per CTA.""",

        "ux_patterns": """- Adattare la navigazione al tipo di business
- CTA principale sempre above the fold
- Form contatto semplice (max 5 campi)
- Mobile-first: tutto deve funzionare perfettamente su telefono
- Velocità: immagini ottimizzate, lazy loading
- Accessibilità: contrasto WCAG AA, focus visible, alt text""",

        "hero_section": """Il hero deve comunicare 3 cose in 3 secondi:
1. CHI sei (nome/brand)
2. COSA fai (servizio/prodotto principale)
3. PERCHÉ sceglierti (differenziatore unico)
+ Un CTA chiaro che dice cosa fare dopo.""",

        "content_strategy": """Regole universali per contenuto efficace:
- Specifico > generico
- Benefici > caratteristiche
- Numeri > aggettivi vaghi
- Storie > corporate-speak
- Breve > lungo (per il web)""",

        "animations": """Animazioni sicure per ogni tipo di sito:
- text-split su titoli principali
- fade-up su cards e sezioni
- stagger su griglie
- magnetic su bottoni CTA
- parallax leggero su hero
- counter su numeri/stats
- scale-in su loghi/icone""",

        "cta_design": """CTA efficace:
- Verbo d'azione + beneficio: "Richiedi Preventivo Gratuito"
- Colore: il più contrastante della palette
- Visibile: non serve scrollare per trovarlo
- Ripetuto: minimo 3 volte nella pagina (hero, metà, fine)""",

        "photo_treatment": """Regole foto universali:
- Qualità alta, peso basso (WebP, max 400KB)
- Coerenza: stesso stile/filtro su tutte le foto
- Relevanti: foto reali del business > stock generiche
- Lazy loading per performance""",

        "typography": """Regole tipografiche universali:
- Heading: font con personalità, weight 700+
- Body: font leggibile, 16-18px, line-height 1.6-1.8
- MAI stessi font per heading e body
- Gerarchia chiara: h1 > h2 > h3 > body con sizing coerente""",

        "common_mistakes": """Errori universali:
- Testo troppo piccolo su mobile
- CTA nascosto o poco evidente
- Troppe animazioni pesanti
- Foto di bassa qualità
- Colori con poco contrasto
- Muro di testo senza break visivi
- Mancanza di social proof""",

        "trends_2025": """Trend design 2025-2026:
- Bento grid layouts
- Glassmorphism subtle
- Typography oversize per hero
- Dark mode come opzione
- Micro-interactions su hover
- Scroll-triggered reveals
- Gradient mesh backgrounds"""
    },
}

# Map Italian category names to their guide keys
CATEGORY_ALIASES = {
    "ristorante": "restaurant",
    "tech": "saas",
    "corporate": "business",
    "studio_professionale": "business",
    "shop": "ecommerce",
    "creative": "portfolio",
    "bellezza": "portfolio",  # beauty → portfolio visual style
    "fitness": "business",    # fitness → business energy
    "salute": "business",     # health → business trust
    "artigiani": "business",  # artisan → business warmth
    "agenzia": "saas",        # agency → saas modern
    "evento": "event",
}


def seed_category_guides():
    """Seed all category design guides into the database."""
    count = 0
    for category, guide in GUIDES.items():
        upsert_category_guide(category, guide)
        count += 1
        print(f"  Seeded guide: {category}")

    # Also seed aliases pointing to the same guides
    for alias, target in CATEGORY_ALIASES.items():
        if target in GUIDES and alias not in GUIDES:
            upsert_category_guide(alias, GUIDES[target])
            count += 1
            print(f"  Seeded alias: {alias} → {target}")

    print(f"\nTotal category guides seeded: {count}")
    return count


if __name__ == "__main__":
    seed_category_guides()
