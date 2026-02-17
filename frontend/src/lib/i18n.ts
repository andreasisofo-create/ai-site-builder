"use client";

import { createContext, useContext, useState, useEffect, useCallback, ReactNode } from "react";

// ==================== TYPES ====================

type Language = "it" | "en";

interface LanguageContextType {
  language: Language;
  setLanguage: (lang: Language) => void;
  t: (key: string) => string;
}

// ==================== TRANSLATIONS ====================

export const translations = {
  it: {
    nav: {
      howItWorks: "Come Funziona",
      features: "Funzionalita'",
      pricing: "Prezzi",
      faq: "FAQ",
      cta: "Prova Gratis",
      ads: "Servizio Ads",
      customSite: "Sito su misura",
      createWithAi: "Crea con AI",
      contact: "Contattaci",
      createFree: "Crea il tuo sito gratis",
      portfolio: "Portfolio",
    },
    hero: {
      title: "Il tuo sito professionale in 60 secondi.",
      subtitle: "I tuoi clienti, dal giorno dopo.",
      description:
        "Descrivi la tua attivita', scegli uno stile e l'intelligenza artificiale crea il tuo sito. Poi attiviamo campagne pubblicitarie per portarti clienti reali.",
      cta: "Crea il tuo sito gratis",
      ctaSecondary: "Guarda come funziona",
    },
    howItWorks: {
      label: "Online in 3 passaggi",
      title: "Da zero al tuo sito, in meno di un caffe'.",
      steps: [
        {
          title: "Descrivi la tua attivita'",
          description:
            "Rispondi a 3 domande: cosa fai, dove sei, che stile preferisci. Non serve nient'altro.",
        },
        {
          title: "L'AI genera il tuo sito",
          description:
            "In 60 secondi ottieni un sito completo: testi, immagini, colori e animazioni professionali.",
        },
        {
          title: "Pubblica e ricevi clienti",
          description:
            "Il tuo sito va online con un click. Se vuoi, attiviamo subito le campagne per portarti clienti.",
        },
      ],
    },
    features: {
      title: "Tutto quello che ti serve per essere online",
      tabs: {
        site: "Crea il Sito",
        clients: "Porta Clienti",
      },
      site: [
        {
          title: "Sito pronto in 60 secondi",
          description: "Rispondi a 3 domande e l'AI crea il tuo sito completo. Testi, foto, colori: tutto fatto.",
        },
        {
          title: "19 stili professionali",
          description: "Ristorante, studio, negozio, portfolio: scegli il design perfetto per la tua attivita'.",
        },
        {
          title: "Modifiche con la chat",
          description: "Scrivi 'cambia il colore in blu' o 'aggiungi gli orari'. L'AI modifica il sito per te.",
        },
        {
          title: "Perfetto su cellulare",
          description: "Il tuo sito si adatta automaticamente a telefono, tablet e computer.",
        },
        {
          title: "Online con un click",
          description: "Hosting, certificato di sicurezza e indirizzo web inclusi. Nessun costo nascosto.",
        },
        {
          title: "Pensato per Google",
          description: "Codice ottimizzato per i motori di ricerca. I tuoi clienti ti trovano piu' facilmente.",
        },
      ],
      clients: [
        {
          title: "Campagne Meta Ads",
          description: "Pubblichiamo su Instagram e Facebook per far conoscere la tua attivita' a chi e' vicino a te.",
        },
        {
          title: "Campagne Google Ads",
          description: "Chi cerca i tuoi servizi su Google trova te. Campagne mirate sulla tua zona.",
        },
        {
          title: "Contenuti creati dall'AI",
          description: "Video, grafiche e testi per le tue pubblicita'. Tutto creato automaticamente dall'intelligenza artificiale.",
        },
        {
          title: "Gestione completa",
          description: "Non devi fare niente. Il nostro team imposta, monitora e ottimizza le campagne per te.",
        },
        {
          title: "Report chiari ogni mese",
          description: "Sai esattamente quante persone hanno visto il tuo annuncio e quante ti hanno contattato.",
        },
        {
          title: "Budget sotto controllo",
          description: "Decidi tu quanto spendere. Nessun costo a sorpresa, solo risultati misurabili.",
        },
      ],
    },
    ads: {
      badge: "Servizio Ads Management",
      title: "Non basta avere un sito.",
      titleHighlight: "Servono clienti.",
      subtitle:
        "Il nostro team gestisce le tue campagne Meta e Google Ads con il supporto dell'intelligenza artificiale.",
      columns: [
        {
          title: "Meta Ads",
          subtitle: "Instagram + Facebook",
          items: [
            "Campagne Instagram & Facebook",
            "A/B testing automatico",
            "DM automatici ai lead",
            "Targeting avanzato con AI",
          ],
        },
        {
          title: "Google Ads",
          subtitle: "Search + Display",
          items: [
            "Campagne Search & Display",
            "Keyword optimization con AI",
            "Policy compliance garantita",
            "Bidding automatico intelligente",
          ],
        },
        {
          title: "Report Mensile",
          subtitle: "Dati chiari, risultati misurabili",
          items: [
            "Dashboard con metriche chiave",
            "Analisi costo per lead",
            "Confronto performance mensile",
            "Suggerimenti AI per ottimizzare",
          ],
        },
      ],
      flowTitle: "Come funziona il servizio Ads",
      flowSteps: [
        { title: "L'AI prepara tutto", subtitle: "Creativita', copy, targeting" },
        { title: "Un esperto revisiona", subtitle: "Supervisione umana garantita" },
        { title: "Monitoraggio 24/7", subtitle: "Ottimizzazione continua" },
      ],
      complianceBadge: "100% conforme alle policy Google e Meta — supervisione umana garantita",
    },
    socialProof: {
      title: "Loro l'hanno gia' fatto",
      subtitle: "Attivita' reali che sono andate online con E-quipe.",
      demos: [
        { name: "Ristorante Amore", category: "Ristorante", image: "/images/demos/ristorante.webp" },
        { name: "Modern Hair Studio", category: "Parrucchiere", image: "/images/demos/parrucchiere.webp" },
        { name: "Smile & Co. Dental", category: "Studio Dentistico", image: "/images/demos/dentista.webp" },
        { name: "FitZone Gym", category: "Palestra", image: "/images/demos/palestra.webp" },
        { name: "Studio Legale Rossi", category: "Studio Professionale", image: "/images/demos/avvocato.webp" },
        { name: "Noir & Blanc", category: "E-commerce", image: "/images/demos/ecommerce.webp" },
      ],
      testimonials: [
        {
          quote: "Ho creato il sito in pausa pranzo. Il giorno dopo avevo gia' ricevuto due richieste di prenotazione.",
          author: "Marco R.",
          role: "Ristorante Da Mario, Roma",
        },
        {
          quote: "Non avevo mai avuto un sito. In 10 minuti ero online con un risultato che sembra fatto da un'agenzia.",
          author: "Laura B.",
          role: "Studio Legale, Milano",
        },
        {
          quote: "Le campagne Google mi portano 10 contatti a settimana. Ho dovuto assumere un'altra persona.",
          author: "Giuseppe V.",
          role: "Idraulico, Torino",
        },
      ],
    },
    pricing: {
      title: "Prezzi chiari. Nessuna sorpresa.",
      subtitle: "Parti col sito, aggiungi le campagne quando vuoi crescere.",
      adBudgetNote: "* Il budget pubblicitario (da dare a Meta/Google) e' separato e lo decidi tu.",
      recommended: "Consigliato",
      plans: [
        {
          name: "Starter",
          price: "199",
          period: "una tantum",
          description: "Per chi vuole solo il sito",
          features: [
            "Sito AI (1 pagina)",
            "Sottodominio gratuito",
            "Certificato SSL",
            "3 modifiche via chat",
          ],
          cta: "Crea il tuo sito",
          popular: false,
        },
        {
          name: "Business",
          price: "49",
          period: "/mese",
          description: "Sito + primi clienti",
          features: [
            "Sito multi-pagina",
            "Dominio personalizzato",
            "Modifiche illimitate",
            "2 campagne Meta/mese",
            "Report mensile",
          ],
          cta: "Scegli Business",
          popular: false,
        },
        {
          name: "Growth",
          price: "99",
          period: "/mese",
          description: "Crescita accelerata",
          features: [
            "Tutto di Business +",
            "Google Ads + Meta Ads",
            "5 contenuti AI/mese",
            "DM automatici ai lead",
            "Report settimanale",
            "Supporto prioritario",
          ],
          cta: "Scegli Growth",
          popular: true,
        },
        {
          name: "Premium",
          price: "199",
          period: "/mese",
          description: "Tutto illimitato",
          features: [
            "Tutto di Growth +",
            "Pagine illimitate",
            "Campagne illimitate",
            "Contenuti AI illimitati",
            "Account manager dedicato",
            "Supporto 24/7",
          ],
          cta: "Scegli Premium",
          popular: false,
        },
      ],
    },
    cta: {
      title: "Pronto a portare la tua attivita' online?",
      subtitle: "Crea il tuo sito in 60 secondi. Gratis, senza carta di credito.",
      button: "Crea il tuo sito gratis",
    },
    faq: {
      title: "Domande frequenti",
      items: [
        {
          q: "Devo saper programmare?",
          a: "No. Rispondi a 3 domande sulla tua attivita' e l'AI crea tutto: testi, immagini, colori. Se vuoi cambiare qualcosa, scrivi nella chat quello che vuoi (es. 'metti gli orari di apertura') e l'AI lo fa per te.",
        },
        {
          q: "Quanto ci mette a creare il sito?",
          a: "Meno di 60 secondi. Scegli un template, descrivi la tua attivita' e il sito e' pronto. Poi puoi personalizzarlo quanto vuoi.",
        },
        {
          q: "Posso usare il mio dominio (es. mionome.it)?",
          a: "Si, dal piano Business in su puoi collegare il tuo dominio. Col piano Starter hai un indirizzo gratuito tipo tuonome.e-quipe.app.",
        },
        {
          q: "Come funzionano le campagne pubblicitarie?",
          a: "Il nostro team imposta le campagne su Meta (Instagram e Facebook) e Google per te. Tu scegli il budget, noi facciamo il resto: creativita', targeting, monitoraggio e ottimizzazione.",
        },
        {
          q: "Quanto devo spendere di pubblicita'?",
          a: "Il budget pubblicitario lo decidi tu ed e' separato dal costo del piano. Con 200-300 euro al mese si ottengono gia' buoni risultati per un'attivita' locale.",
        },
        {
          q: "Posso iniziare solo col sito e aggiungere le campagne dopo?",
          a: "Certo. Il piano Starter e' solo il sito. Quando sei pronto a ricevere piu' clienti, fai upgrade a Business o Growth e attiviamo le campagne.",
        },
        {
          q: "In quanto tempo vedo i risultati delle campagne?",
          a: "I primi contatti arrivano in genere entro 2-4 settimane. La crescita diventa stabile dopo 2-3 mesi di campagne attive.",
        },
        {
          q: "Posso disdire quando voglio?",
          a: "Si, nessun vincolo. Puoi disdire il piano mensile in qualsiasi momento. Il sito Starter (una tantum) resta tuo per sempre.",
        },
      ],
    },
    footer: {
      description:
        "E-quipe crea il tuo sito web con l'intelligenza artificiale e gestisce le campagne pubblicitarie per portarti clienti reali.",
      product: "Prodotto",
      productLinks: {
        howItWorks: "Come Funziona",
        features: "Funzionalita'",
        pricing: "Prezzi",
        dashboard: "Dashboard",
      },
      company: "Azienda",
      companyLinks: {
        about: "Chi Siamo",
        contact: "Contatti",
        blog: "Blog",
      },
      legal: "Legale",
      legalLinks: {
        privacy: "Privacy Policy",
        terms: "Termini di Servizio",
        cookies: "Cookie Policy",
      },
      bottomLinks: {
        privacy: "Privacy",
        terms: "Termini",
        cookies: "Cookie",
      },
      copyright: "\u00A9 2026 E-quipe S.r.l.s. Tutti i diritti riservati. P.IVA: 12345678901",
      chooseYourPath: "Scegli la tua strada",
      chooseYourPathDesc: "Offriamo due soluzioni distinte: {customSite} (sviluppato dai nostri esperti) oppure {aiTech} (fai-da-te in autonomia). I prezzi e i servizi sono specifici per ogni soluzione.",
      customSite: "Sito su misura",
      aiTechnology: "Tecnologia AI",
      aiBuilder: "App AI Builder",
      agencyPortfolio: "Portfolio Agenzia",
      agencyPricing: "Prezzi Agenzia",
      internalDoc: "Documento interno — Uso riservato",
    },
    heroAgency: {
      badge: "Creazione sito gratuita",
      title: "Ti creiamo il sito.",
      titleHighlight: "Gratis.",
      subtitle: "Paghi solo se ti piace. Zero rischi, zero obblighi.",
      description: "Raccontaci la tua attivita' e il nostro team crea il tuo sito professionale su misura.",
      descriptionLine2: "Se non ti convince, non spendi un centesimo.",
      cta: "Contattaci — e' gratis",
      ctaSecondary: "Oppure crealo da solo in 60 secondi",
      trustBadges: [
        "200+ attivita' gia' online",
        "Senza carta di credito",
        "Risposta entro 24h",
      ],
    },
    reviews: [
      {
        name: "Marco Rossi",
        role: "Titolare Ristorante Da Marco",
        text: "Incredibile. Hanno rifatto il sito del mio ristorante gratis. Ho pagato solo quando l'ho visto online. Ora ricevo prenotazioni ogni giorno.",
      },
      {
        name: "Giulia Bianchi",
        role: "Architetto",
        text: "Ero scettica sul 'gratis', ma e' tutto vero. Il sito e' bellissimo e molto professionale. Il team e' super disponibile.",
      },
      {
        name: "Luca Verdi",
        role: "Personal Trainer",
        text: "Un servizio che mancava. Niente preventivi complicati o anticipi al buio. Vedi il risultato e decidi. Consigliatissimo.",
      },
    ],
    howItWorksAgency: {
      title: "Come funziona? Semplice.",
      subtitle: "Dal primo contatto al tuo sito online in 3 passaggi.",
      steps: [
        {
          title: "1. Contattaci",
          description: "Raccontaci cosa fai e che stile ti piace. Bastano 2 minuti. Compila il form o scrivici su WhatsApp.",
        },
        {
          title: "2. Noi creiamo il sito",
          description: "Il nostro team + intelligenza artificiale costruisce il tuo sito su misura. Design, testi, immagini: tutto incluso.",
        },
        {
          title: "3. Vedi e decidi",
          description: "Ti mostriamo il risultato. Ti piace? Scegli un piano e vai online. Non ti piace? Nessun costo, nessun obbligo.",
        },
      ],
      cta: "Contattaci ora — e' gratis",
    },
    portfolio: {
      title: "Esempi di siti realizzati",
      subtitle: "Guarda la qualita' che possiamo offrire alla tua attivita'.",
      visitSite: "Visita il sito",
      items: [
        { name: "Professional Force", sector: "Sicurezza & Investigazioni" },
        { name: "Restinone", sector: "Ristorazione & Eventi" },
        { name: "Fondazione Italiana Sport", sector: "No-Profit & Sport" },
        { name: "Now Now", sector: "Servizi Digitali" },
        { name: "Rally di Roma Capitale", sector: "Eventi Sportivi" },
        { name: "Max Rendina", sector: "Personal Branding" },
      ],
    },
    contact: {
      title: "Raccontaci la tua attivita'",
      subtitle: "Ti creiamo il sito gratis. Senza impegno.",
      nameLabel: "Nome",
      namePlaceholder: "Il tuo nome",
      activityLabel: "Attivita'",
      activityPlaceholder: "Che attivita' hai? (es: ristorante, studio legale...)",
      contactLabel: "Contatto",
      contactPlaceholder: "Email o numero di telefono",
      hasSiteLabel: "Hai gia' un sito?",
      hasSiteNo: "No, e' il primo sito",
      hasSiteYes: "Si', voglio rifarlo",
      submit: "Voglio il mio sito gratis",
      loading: "Invio in corso...",
      successTitle: "Richiesta Ricevuta!",
      successMessage: "Grazie per averci contattato. Il nostro team analizzera' la tua richiesta e ti rispondera' entro 24 ore.",
      privacy: "I tuoi dati sono al sicuro. Nessun impegno.",
      whatsapp: "Preferisci WhatsApp?",
      whatsappLink: "Scrivici qui \u2192",
    },
    featuresAgency: {
      title: "Cosa ottieni, senza spendere un centesimo",
      items: [
        { title: "Sito professionale su misura", description: "Design personalizzato per la tua attivita'. Non un template generico." },
        { title: "Perfetto su ogni dispositivo", description: "Il sito si adatta a telefono, tablet e computer automaticamente." },
        { title: "Testi scritti dall'AI", description: "Copy persuasivi generati dall'intelligenza artificiale per la tua attivita'." },
        { title: "Hosting e SSL inclusi", description: "Il tuo sito e' online e protetto. Nessun costo aggiuntivo." },
        { title: "Ottimizzato per Google", description: "Codice SEO-friendly. I tuoi clienti ti trovano piu' facilmente." },
        { title: "Modifiche via chat", description: "Vuoi cambiare qualcosa? Scrivici e aggiorniamo il sito per te." },
      ],
      cta: "Contattaci — e' gratis",
    },
    aiBuilder: {
      badge: "Fai da Te",
      title: "Preferisci fare da solo?",
      titleLine2: "Prova la nostra AI.",
      description: "Abbiamo costruito una piattaforma dove l'intelligenza artificiale crea il sito per te in 60 secondi. Rispondi a 3 domande e il sito e' pronto. Modificalo con un click.",
      cta: "Prova l'App AI",
      floatingBadge1: "\u2713 SEO Optimized",
      floatingBadge2: "\u26A1 Super Veloce",
    },
    adsUpsell: {
      title: "Non solo siti web. Portiamo clienti.",
      description: "Un bel sito senza traffico e' inutile. Gestiamo noi le tue campagne su Google e Facebook per portarti contatti reali ogni giorno.",
      feature1Title: "Target Preciso",
      feature1Desc: "Mostriamo il tuo sito solo a chi cerca i tuoi servizi.",
      feature2Title: "Risultati Misurabili",
      feature2Desc: "Report chiari. Sai esattamente quanto ti costa un cliente.",
      feature3Title: "Creativita' Incluse",
      feature3Desc: "Scriviamo noi gli annunci e creiamo le grafiche.",
      cta: "Scopri i pacchetti ads \u2192",
    },
    faqAgency: {
      title: "Domande Frequenti",
      items: [
        { q: "E' davvero gratis?", a: "Si', la creazione del sito e' gratuita. Non ci sono costi nascosti di sviluppo. Se ti piace il risultato, paghi solo il piano che scegli (es. Pack Presenza a 499\u20AC o Pack Clienti). Se non ti piace, amici come prima." },
        { q: "Quanto tempo ci vuole?", a: "Il nostro team, aiutato dall'AI, puo' presentarti una bozza completa in 24-48 ore dalla tua richiesta." },
        { q: "Il sito sara' mio o in affitto?", a: "Con il Pack Presenza e Crescita, dopo il pagamento una tantum, il sito e' tuo. Paghi solo il canone mensile ridotto per hosting e manutenzione." },
        { q: "Posso modificare il sito da solo?", a: "Certamente. Ti diamo accesso a un pannello di controllo semplicissimo. Oppure, se hai il pacchetto incluso, chiedi a noi via chat e facciamo tutto noi." },
        { q: "Cosa succede se smetto di pagare il rinnovo?", a: "Il sito andra' offline alla scadenza. Puoi pero' richiedere l'export dei contenuti se vuoi spostarti altrove (previo saldo di eventuali canoni)." },
      ],
    },
    finalCta: {
      title: "Pronto a portare la tua attivita' online?",
      subtitle: "Contattaci oggi. Ti creiamo il sito gratis, senza impegno.",
      cta: "Contattaci — e' gratis",
      ctaSecondary: "Oppure crealo da solo",
    },
    page: {
      mobileCta: "Contattaci — e' gratis",
    },
    aiPage: {
      hero: {
        title: "Il tuo sito professionale in",
        titleBreak: "60 secondi.",
        subtitle: "I tuoi clienti, dal giorno dopo.",
        description: "Scegli la tua attivita', carica il logo e l'intelligenza artificiale crea il tuo sito. Poi attiviamo campagne pubblicitarie per portarti clienti reali ogni giorno.",
        cta: "Crea il tuo sito gratis",
        ctaSecondary: "Guarda come funziona",
        browserUrl: "iltuosito.e-quipe.app",
        aiCreating: "La tua AI sta creando il sito...",
      },
      steps: {
        badge: "3 Passaggi",
        title: "Da zero al tuo sito, in meno di",
        titleBreak: "un caffe'.",
        items: [
          { title: "Descrivi la tua attivita'", desc: "Rispondi a 3 semplici domande. Nome, tipo di attivita', i tuoi servizi principali. Non serve altro." },
          { title: "L'AI genera il tuo sito", desc: "In 60 secondi hai un sito completo. Testi, immagini, colori e animazioni. Tutto ottimizzato." },
          { title: "Pubblica e trova clienti", desc: "Il sito va online subito. Attiva le campagne pubblicitarie per portarti contatti reali ogni giorno." },
        ],
      },
      features: {
        title: "Tutto quello che ti serve per",
        titleBreak: "essere online",
        tabSite: "Crea Siti",
        tabAds: "Trova Clienti",
        site: [
          { title: "Sito pronto in 60 secondi", desc: "Rispondi a 3 domande. Testi, foto, colori: tutto generato dall'AI." },
          { title: "7+ stili professionali", desc: "L'AI sceglie design portfolio per la tua attivita'. Oppure scegli tu." },
          { title: "Modifiche con la chat", desc: "Di' all'AI cosa cambiare. \"Cambia il colore\", \"aggiungi un testo\". Fatto." },
          { title: "Perfetto su qualsiasi dispositivo", desc: "Il sito si adatta automaticamente a smartphone, tablet e desktop." },
          { title: "Online con un click", desc: "Hosting, certificato SSL e dominio: e' tutto incluso. Pubblica subito." },
          { title: "Pensato per Google", desc: "L'AI ottimizza titoli, descrizioni per i motori di ricerca automaticamente." },
        ],
        ads: [
          { title: "Meta Ads incluse", desc: "Campagne Instagram e Facebook gestite dal nostro team con AI." },
          { title: "Google Ads ottimizzate", desc: "Annunci su Google per chi cerca i tuoi servizi nella tua zona." },
          { title: "Report mensile", desc: "Dashboard chiara con clic, lead e costo per contatto." },
          { title: "Contenuti AI", desc: "Post social, testi annunci e grafiche generate dall'intelligenza artificiale." },
          { title: "Landing page dedicate", desc: "Pagine ottimizzate per ogni campagna pubblicitaria." },
          { title: "DM automatici", desc: "Rispondi automaticamente ai lead che arrivano da Instagram e Facebook." },
        ],
      },
      adsSection: {
        badge: "Servizio Ads Management",
        title: "Non basta avere un sito.",
        titleHighlight: "Servono clienti.",
        subtitle: "Il nostro team gestisce le tue campagne Meta e Google Ads con il supporto dell'intelligenza artificiale.",
        cards: [
          { title: "Meta Ads", items: ["Instagram + Facebook Ads", "Audience personalizzate", "A/B testing automatico", "Creativita' generate con AI"] },
          { title: "Google Ads", items: ["Annunci su Ricerca Google", "Keyword della tua zona", "Budget ottimizzato con AI", "Monitoraggio conversioni intelligente"] },
          { title: "Report Mensile", items: ["Dashboard risultati", "Clic, lead e conversioni", "Costo per contatto", "Suggerimenti di auto-ottimizzazione"] },
        ],
        flowTitle: "Come funziona il servizio Ads",
        flowDesc: "Analizziamo la tua attivita' \u2192 Creiamo le campagne \u2192 Ottimizziamo ogni settimana \u2192 Ti mandiamo il report",
      },
      portfolio: {
        title: "Loro l'hanno gia' fatto",
        subtitle: "Attivita' reali che sono andate online con E-quipe.",
      },
      testimonials: [
        { name: "Marco R.", role: "Ristoratore", text: "Ho creato il sito in pausa pranzo. Il mio vecchio webmaster ci ha messo 3 mesi. Incredibile davvero." },
        { name: "Laura M.", role: "Estetista", text: "Non ci capisco nulla di tecnologia. Ma in 60 secondi avevo il sito online. E le campagne Google mi portano 15 clienti nuovi al mese." },
        { name: "Giuseppe V.", role: "Avvocato", text: "Le campagne Google ci portano 15 contatti al mese. Con il report mensile so esattamente quanto mi costa ogni nuovo cliente." },
      ],
      pricing: {
        title: "Prezzi chiari. Nessuna",
        titleBreak: "sorpresa.",
        subtitle: "Parti col sito, aggiungi le campagne quando vuoi crescere.",
        baseBadge: "Solo Sito Web",
        baseName: "Sito Base",
        baseDesc: "Il tuo sito AI, pronto per andare online. Paghi una volta, nessun abbonamento.",
        baseFeatures: ["Sito AI completo (5 pagine)", "Dominio e-quipe.app", "Hosting + SSL incluso", "Modifiche via chat (5/mese)"],
        basePrice: "\u20AC199",
        basePeriod: "una tantum",
        baseNoCost: "Nessun costo mensile",
        baseCta: "Crea il tuo sito",
        divider: "Sito + Ads \u2014 Porta clienti ogni mese",
        plans: [
          { name: "Business", price: "\u20AC49", period: "/mese", desc: "Per chi vuole un sito completo e autonomo.", features: ["Sito AI multi-pagina (5 pag)", "Dominio personalizzato", "Hosting + SSL + Backup", "Supporto prioritario"], cta: "Scegli Business" },
          { name: "Crescita", price: "\u20AC99", period: "/mese", desc: "Sito + campagne per portarti clienti.", features: ["Tutto di Business", "Meta Ads (Instagram + Facebook)", "Contenuti AI (4 post/mese)", "Report mensile performance", "Landing page dedicate"], cta: "Scegli Crescita", tag: "CONSIGLIATO" },
          { name: "Premium", price: "\u20AC199", period: "/mese", desc: "Sito + Full Ads + contenuti Pro.", features: ["Tutto di Crescita", "Google Ads incluso", "1 video + 1 foto a settimana", "Report settimanale"], cta: "Scegli Premium" },
        ],
        budgetNote: "* Budget pubblicitario escluso dai piani Crescita e Premium",
      },
      faq: {
        title: "Domande frequenti",
        items: [
          { q: "Devo saper programmare?", a: "Assolutamente no. Rispondi a 3 domande e l'AI crea tutto: testi, immagini, colori, animazioni. Puoi modificare qualsiasi cosa con la chat, senza toccare codice." },
          { q: "Quanto ci metto a creare il sito?", a: "60 secondi. Letteralmente. Rispondi alle domande, l'AI genera il sito completo. Poi puoi modificarlo quanto vuoi." },
          { q: "Posso usare il mio dominio (es. mionome.it)?", a: "Si', dal piano Business in su puoi collegare il tuo dominio personalizzato. Con il piano base usi un sottodominio gratuito e-quipe.app." },
          { q: "Come funzionano le campagne pubblicitarie?", a: "Il nostro team crea e gestisce le campagne su Meta (Instagram + Facebook) e Google. L'AI ottimizza budget e targeting. Tu ricevi i contatti." },
          { q: "Quanto devo spendere di pubblicita'?", a: "Il budget pubblicitario e' separato dal costo del piano. Consigliamo un minimo di \u20AC300/mese per Meta e \u20AC500/mese per Google. Il nostro team ti aiuta a decidere." },
          { q: "Posso iniziare con il sito e aggiungere le campagne dopo?", a: "Certo! Puoi partire col piano Sito Base o Business e passare a Crescita o Premium quando vuoi. L'upgrade e' immediato." },
          { q: "In quanto tempo vedo i risultati delle campagne?", a: "Le prime richieste arrivano in genere entro 7-14 giorni dall'attivazione. I risultati migliorano mese dopo mese grazie all'ottimizzazione continua dell'AI." },
          { q: "Posso disdire quando voglio?", a: "Si', nessun vincolo. Puoi disdire il piano mensile in qualsiasi momento. Il sito base una tantum resta tuo." },
        ],
      },
      finalCta: {
        title: "Pronto a portare la tua attivita'",
        titleBreak: "online?",
        subtitle: "Crea il tuo sito in 60 secondi. Gratis, senza carta di credito.",
        cta: "Crea il tuo sito gratis",
      },
    },
    adsPage: {
      hero: {
        badge: "Servizio Ads Management",
        title: "Ogni euro investito.",
        titleHighlight: "Diventa un cliente.",
        subtitle: "Il nostro team gestisce le tue campagne su Google e Meta con il supporto dell'intelligenza artificiale. Tu ricevi i contatti. Noi facciamo tutto il resto.",
        cta: "Richiedi consulenza gratuita",
        ctaSecondary: "Come funziona",
        stats: [
          { value: "4", label: "Moduli AI dedicati" },
          { value: "24/7", label: "Ottimizzazione continua" },
          { value: "-30%", label: "Costo per lead medio" },
          { value: "7gg", label: "Primi risultati" },
        ],
      },
      whatWeDo: {
        title: "Cosa facciamo per te",
        subtitle: "Un ecosistema completo per portarti clienti ogni giorno. Tutto gestito dal nostro team con AI.",
        services: [
          { title: "Google Ads", desc: "Annunci su Ricerca Google, Shopping e Display. Intercettiamo chi cerca i tuoi servizi nella tua zona.", features: ["Ricerca keyword", "Annunci RSA", "Google Shopping", "Remarketing"] },
          { title: "Meta Ads", desc: "Campagne Instagram e Facebook per raggiungere il tuo pubblico ideale con creativita' generate dall'AI.", features: ["Instagram Feed & Stories", "Facebook Ads", "Audience personalizzate", "A/B Testing"] },
          { title: "Contenuti AI", desc: "Immagini generate con Gemini AI, video prompt per Seedance 2.0 e copy ottimizzati per ogni piattaforma.", features: ["Immagini con Gemini AI", "Video prompt AI", "Copy annunci RSA", "Post social"] },
          { title: "Analytics & Report", desc: "Dashboard chiara con tutti i numeri che contano: clic, lead, costo per contatto e ROI.", features: ["Report settimanale/mensile", "Costo per lead", "Conversion tracking", "Benchmark settore"] },
          { title: "Landing Page", desc: "Pagine di atterraggio ottimizzate per ogni campagna. L'AI analizza e migliora continuamente.", features: ["Design ottimizzato", "A/B testing", "Score qualita'", "Ottimizzazione CRO"] },
          { title: "DM Automatici", desc: "Rispondi automaticamente ai lead che arrivano da Instagram e Facebook. Nessun contatto perso.", features: ["Risposta automatica", "Qualificazione lead", "CRM integrato", "Follow-up AI"] },
        ],
      },
      howItWorks: {
        badge: "Come funziona",
        title: "Dalla consulenza ai clienti",
        titleBreak: "in 4 step",
        steps: [
          { title: "Consulenza gratuita", desc: "Analizziamo la tua attivita', i tuoi obiettivi e il tuo mercato di riferimento. Nessun impegno." },
          { title: "L'AI analizza il mercato", desc: "4 moduli AI studiano il tuo settore: keyword, competitor, benchmark e opportunita' pubblicitarie." },
          { title: "Lanciamo le campagne", desc: "Creiamo annunci, landing page e contenuti ottimizzati. Le campagne vanno live in 48 ore." },
          { title: "Ottimizziamo ogni settimana", desc: "L'AI monitora e ottimizza budget, targeting e creativita'. Tu ricevi i lead e il report." },
        ],
      },
      aiPipeline: {
        badge: "AI-Powered",
        title: "4 moduli AI lavorano",
        titleBreak: "per te, 24/7",
        subtitle: "Dall'analisi del mercato all'ottimizzazione delle campagne: ogni fase e' automatizzata con guardrail di sicurezza e supervisione umana.",
        modules: [
          { name: "L'Investigatore", subtitle: "Analisi Cliente & Asset", desc: "Analizza il sito web del cliente, struttura, contenuti e proposta di valore. Genera un profilo completo del business.", outputs: ["Categoria business", "Proposta di valore", "Punteggio landing page", "Catalogo servizi"] },
          { name: "L'Analista", subtitle: "Trend & Competizione", desc: "Studia keyword, competitor, benchmark di settore e trend stagionali. Mappa completa del panorama competitivo.", outputs: ["Mappa keyword (volumi, CPC)", "Indice stagionalita'", "Stima budget competitivo", "SWOT vs competitor"] },
          { name: "L'Architetto", subtitle: "Piano Marketing", desc: "Incrocia i dati dei moduli precedenti per generare campagne, keyword, copy annunci e KPI target.", outputs: ["Piano campagne completo", "Copy annunci RSA", "Allocazione budget", "KPI target"] },
          { name: "Il Broker", subtitle: "Gestione & Ottimizzazione", desc: "Gestisce il budget come un investitore algoritmico. Ottimizza bid, gestisce A/B test e monitora in tempo reale.", outputs: ["Campagne live", "A/B testing automatico", "Bid adjustments real-time", "Alert e report"] },
        ],
        safetyTitle: "Guardrail di sicurezza integrati",
        safetyDesc: "Budget cap assoluto, circuit breaker automatico, approvazione umana per decisioni critiche, benchmark validation e anomaly detection. L'AI non puo' superare i limiti impostati.",
      },
      contentCreation: {
        title: "Creativita' generate",
        titleBreak: "dall'intelligenza artificiale",
        subtitle: "Non devi pensare a grafiche, testi o video. L'AI crea tutto per te, ottimizzato per ogni piattaforma.",
        tools: [
          { title: "Generatore Immagini AI", desc: "Crea immagini per i tuoi annunci con Gemini 2.5 Flash. 6 formati disponibili (Feed, Stories, YouTube, Display).", badge: "Gemini AI" },
          { title: "Video Creator AI", desc: "Genera prompt video ottimizzati per Seedance 2.0. Stili cinematografici, social e product demo.", badge: "Seedance 2.0" },
          { title: "Copy AI per Annunci", desc: "15 titoli + 4 descrizioni RSA generati automaticamente. Copy ottimizzato per conversioni.", badge: "Multi-Agent AI" },
        ],
      },
      pricing: {
        title: "Pack completi. Prezzi chiari.",
        subtitle: "Soluzioni tutto-incluso con risparmio garantito.",
        packs: [
          { name: "Pack Presenza", price: "\u20AC499", setup: "una tantum", subscription: "+ \u20AC39/mese", desc: "Per chi vuole essere online con un sito professionale.", features: ["Homepage AI completa", "3 pagine extra incluse (4 totali)", "Dominio personalizzato (1 anno)", "Hosting + SSL + Backup", "Modifiche illimitate via chat"], cta: "Scegli Pack Presenza" },
          { name: "Pack Clienti", price: "\u20AC499", setup: "una tantum", subscription: "+ \u20AC199/mese", desc: "Per iniziare subito a ricevere clienti da Instagram e Facebook.", features: ["Tutto del Pack Presenza", "Meta Ads (Instagram & Facebook)", "Contenuti Base (8 post AI/mese)", "Report mensile performance", "Supporto via chat"], cta: "Scegli Pack Clienti" },
          { name: "Pack Crescita", price: "\u20AC499", setup: "SETUP GRATUITO", subscription: "+ \u20AC399/mese", desc: "Per crescere seriamente con Google e Meta insieme.", features: ["Sito Web Custom completo (8 pagine)", "Dominio personalizzato incluso", "Full Ads: Meta Pro + Google Ads", "DM automatici ai lead", "Contenuti Pro (illimitati)", "Report settimanale dettagliato", "Manutenzione inclusa", "Supporto prioritario"], cta: "Scegli Pack Crescita", tag: "CONSIGLIATO" },
          { name: "Pack Premium", price: "\u20AC1.499", setup: "SETUP GRATUITO", subscription: "+ \u20AC999/mese", desc: "Per attivita' ambiziose. Un'agenzia digitale dedicata.", features: ["Tutto del Pack Crescita", "Pagine sito illimitate", "Campagne illimitate su tutti i canali", "Account manager dedicato", "Strategia marketing mensile", "Report personalizzato e call mensile", "Supporto 24/7 dedicato"], cta: "Scegli Pack Premium" },
        ],
        notes: ["* Budget pubblicitario escluso", "** Sconto 15% pagamento annuale"],
      },
      testimonials: {
        title: "Risultati reali, clienti reali",
        reviews: [
          { name: "Marco R.", role: "Ristoratore", text: "Le campagne Meta ci portano 25 coperti in piu' a settimana. Il report mensile e' chiarissimo, so esattamente quanto mi costa ogni cliente." },
          { name: "Laura M.", role: "Estetista", text: "Prima spendevo in volantini senza sapere se funzionassero. Ora con Google Ads ricevo 15 nuovi contatti al mese e so il costo di ognuno." },
          { name: "Giuseppe V.", role: "Avvocato", text: "Il team gestisce tutto, io ricevo solo i contatti qualificati. In 3 mesi ho recuperato l'investimento e ora il flusso e' costante." },
        ],
      },
      faq: {
        title: "Domande frequenti",
        items: [
          { q: "Quanto devo spendere di budget pubblicitario?", a: "Il budget pubblicitario e' separato dal costo del servizio. Consigliamo un minimo di \u20AC300/mese per Meta e \u20AC500/mese per Google. Il nostro team ti aiuta a decidere in base ai tuoi obiettivi." },
          { q: "In quanto tempo vedo i risultati?", a: "Le prime richieste arrivano in genere entro 7-14 giorni dall'attivazione delle campagne. I risultati migliorano mese dopo mese grazie all'ottimizzazione continua dell'AI." },
          { q: "Devo creare io i contenuti degli annunci?", a: "No, creiamo noi tutto: testi, immagini, video e grafiche. L'AI genera contenuti ottimizzati per ogni piattaforma e li testa automaticamente." },
          { q: "Come funziona il report?", a: "Ricevi un report dettagliato (settimanale o mensile in base al piano) con clic, impression, lead, costo per contatto e suggerimenti di ottimizzazione. Dashboard sempre accessibile." },
          { q: "Posso scegliere solo il servizio Ads senza il sito?", a: "Si', puoi acquistare i servizi a la carte. Ads Management parte da \u20AC149/mese per Meta Ads. Pero' un sito ottimizzato migliora drasticamente le conversioni." },
          { q: "Cosa succede se le campagne non performano?", a: "Il sistema ha guardrail automatici: circuit breaker che pausa le campagne se il costo per lead supera la soglia, anomaly detection e revisione settimanale. Non sprechiamo budget." },
          { q: "Posso disdire quando voglio?", a: "Si', nessun vincolo. I piani mensili si possono disdire in qualsiasi momento. I servizi una tantum (sito) restano tuoi." },
          { q: "Gestite anche i miei account social?", a: "I piani con Contenuti AI includono la creazione di post per i social. Il piano Crescita include 8 post AI/mese, il Premium contenuti illimitati. La pubblicazione sui social e' gestita dal nostro team." },
        ],
      },
      finalCta: {
        title: "Pronto a ricevere",
        titleBreak: "clienti ogni giorno?",
        subtitle: "Consulenza gratuita. Analizziamo la tua attivita' e ti mostriamo il potenziale delle campagne AI.",
        cta: "Richiedi consulenza gratuita",
      },
    },
  },
  en: {
    nav: {
      howItWorks: "How It Works",
      features: "Features",
      pricing: "Pricing",
      faq: "FAQ",
      cta: "Try Free",
      ads: "Ads Service",
      customSite: "Custom Site",
      createWithAi: "Create with AI",
      contact: "Contact Us",
      createFree: "Create your site for free",
      portfolio: "Portfolio",
    },
    hero: {
      title: "Your professional website in 60 seconds.",
      subtitle: "Your customers, starting tomorrow.",
      description:
        "Describe your business, choose a style, and AI creates your site. Then we launch ad campaigns to bring you real customers.",
      cta: "Create your site for free",
      ctaSecondary: "See how it works",
    },
    howItWorks: {
      label: "Online in 3 steps",
      title: "From zero to your website, in less than a coffee break.",
      steps: [
        {
          title: "Describe your business",
          description:
            "Answer 3 questions: what you do, where you are, what style you prefer. That's all you need.",
        },
        {
          title: "AI generates your site",
          description:
            "In 60 seconds you get a complete website: copy, images, colors and professional animations.",
        },
        {
          title: "Publish and get customers",
          description:
            "Your site goes live with one click. If you want, we launch campaigns right away to bring you customers.",
        },
      ],
    },
    features: {
      title: "Everything you need to be online",
      tabs: {
        site: "Create Site",
        clients: "Get Customers",
      },
      site: [
        {
          title: "Site ready in 60 seconds",
          description: "Answer 3 questions and AI creates your complete site. Copy, photos, colors: all done.",
        },
        {
          title: "19 professional styles",
          description: "Restaurant, studio, shop, portfolio: choose the perfect design for your business.",
        },
        {
          title: "Edits via chat",
          description: "Type 'change color to blue' or 'add opening hours'. AI modifies the site for you.",
        },
        {
          title: "Perfect on mobile",
          description: "Your site automatically adapts to phone, tablet and computer.",
        },
        {
          title: "Online with one click",
          description: "Hosting, SSL certificate and web address included. No hidden costs.",
        },
        {
          title: "Built for Google",
          description: "Code optimized for search engines. Your customers find you more easily.",
        },
      ],
      clients: [
        {
          title: "Meta Ads campaigns",
          description: "We advertise on Instagram and Facebook to introduce your business to people near you.",
        },
        {
          title: "Google Ads campaigns",
          description: "When people search for your services on Google, they find you. Targeted campaigns in your area.",
        },
        {
          title: "AI-created content",
          description: "Videos, graphics and copy for your ads. All created automatically by AI.",
        },
        {
          title: "Full management",
          description: "You don't do anything. Our team sets up, monitors and optimizes campaigns for you.",
        },
        {
          title: "Clear monthly reports",
          description: "You know exactly how many people saw your ad and how many contacted you.",
        },
        {
          title: "Budget under control",
          description: "You decide how much to spend. No surprise costs, only measurable results.",
        },
      ],
    },
    ads: {
      badge: "Ads Management Service",
      title: "Having a website is not enough.",
      titleHighlight: "You need customers.",
      subtitle:
        "Our team manages your Meta and Google Ads campaigns with AI support.",
      columns: [
        {
          title: "Meta Ads",
          subtitle: "Instagram + Facebook",
          items: [
            "Instagram & Facebook campaigns",
            "Automatic A/B testing",
            "Automated DMs to leads",
            "Advanced AI targeting",
          ],
        },
        {
          title: "Google Ads",
          subtitle: "Search + Display",
          items: [
            "Search & Display campaigns",
            "AI keyword optimization",
            "Guaranteed policy compliance",
            "Smart automated bidding",
          ],
        },
        {
          title: "Monthly Report",
          subtitle: "Clear data, measurable results",
          items: [
            "Dashboard with key metrics",
            "Cost per lead analysis",
            "Monthly performance comparison",
            "AI suggestions to optimize",
          ],
        },
      ],
      flowTitle: "How the Ads service works",
      flowSteps: [
        { title: "AI prepares everything", subtitle: "Creatives, copy, targeting" },
        { title: "An expert reviews", subtitle: "Human oversight guaranteed" },
        { title: "24/7 monitoring", subtitle: "Continuous optimization" },
      ],
      complianceBadge: "100% compliant with Google and Meta policies — guaranteed human oversight",
    },
    socialProof: {
      title: "They've already done it",
      subtitle: "Real businesses that went online with E-quipe.",
      demos: [
        { name: "Ristorante Amore", category: "Restaurant", image: "/images/demos/ristorante.webp" },
        { name: "Modern Hair Studio", category: "Hair Salon", image: "/images/demos/parrucchiere.webp" },
        { name: "Smile & Co. Dental", category: "Dental Office", image: "/images/demos/dentista.webp" },
        { name: "FitZone Gym", category: "Gym", image: "/images/demos/palestra.webp" },
        { name: "Studio Legale Rossi", category: "Law Firm", image: "/images/demos/avvocato.webp" },
        { name: "Noir & Blanc", category: "E-commerce", image: "/images/demos/ecommerce.webp" },
      ],
      testimonials: [
        {
          quote: "I created the site during my lunch break. The next day I had already received two booking requests.",
          author: "Marco R.",
          role: "Ristorante Da Mario, Rome",
        },
        {
          quote: "I never had a website. In 10 minutes I was online with a result that looks agency-made.",
          author: "Laura B.",
          role: "Law Firm, Milan",
        },
        {
          quote: "Google campaigns bring me 10 contacts a week. I had to hire another person.",
          author: "Giuseppe V.",
          role: "Plumber, Turin",
        },
      ],
    },
    pricing: {
      title: "Clear pricing. No surprises.",
      subtitle: "Start with the site, add campaigns when you want to grow.",
      adBudgetNote: "* Ad budget (to pay Meta/Google) is separate and you decide the amount.",
      recommended: "Recommended",
      plans: [
        {
          name: "Starter",
          price: "199",
          period: "one-time",
          description: "For those who just want the site",
          features: [
            "AI site (1 page)",
            "Free subdomain",
            "SSL certificate",
            "3 chat edits",
          ],
          cta: "Create your site",
          popular: false,
        },
        {
          name: "Business",
          price: "49",
          period: "/month",
          description: "Site + first customers",
          features: [
            "Multi-page site",
            "Custom domain",
            "Unlimited edits",
            "2 Meta campaigns/month",
            "Monthly report",
          ],
          cta: "Choose Business",
          popular: false,
        },
        {
          name: "Growth",
          price: "99",
          period: "/month",
          description: "Accelerated growth",
          features: [
            "Everything in Business +",
            "Google Ads + Meta Ads",
            "5 AI content/month",
            "Automated DMs to leads",
            "Weekly report",
            "Priority support",
          ],
          cta: "Choose Growth",
          popular: true,
        },
        {
          name: "Premium",
          price: "199",
          period: "/month",
          description: "Everything unlimited",
          features: [
            "Everything in Growth +",
            "Unlimited pages",
            "Unlimited campaigns",
            "Unlimited AI content",
            "Dedicated account manager",
            "24/7 support",
          ],
          cta: "Choose Premium",
          popular: false,
        },
      ],
    },
    cta: {
      title: "Ready to take your business online?",
      subtitle: "Create your site in 60 seconds. Free, no credit card required.",
      button: "Create your site for free",
    },
    faq: {
      title: "Frequently asked questions",
      items: [
        {
          q: "Do I need to know how to code?",
          a: "No. Answer 3 questions about your business and AI creates everything: copy, images, colors. If you want to change something, type in the chat what you want (e.g. 'add opening hours') and AI does it for you.",
        },
        {
          q: "How long does it take to create the site?",
          a: "Less than 60 seconds. Choose a template, describe your business and the site is ready. Then you can customize it as much as you want.",
        },
        {
          q: "Can I use my own domain (e.g. myname.com)?",
          a: "Yes, from the Business plan onwards you can connect your domain. With the Starter plan you get a free address like yourname.e-quipe.app.",
        },
        {
          q: "How do ad campaigns work?",
          a: "Our team sets up campaigns on Meta (Instagram and Facebook) and Google for you. You choose the budget, we do the rest: creatives, targeting, monitoring and optimization.",
        },
        {
          q: "How much should I spend on advertising?",
          a: "You decide the ad budget and it's separate from the plan cost. With 200-300 euros per month you already get good results for a local business.",
        },
        {
          q: "Can I start with just the site and add campaigns later?",
          a: "Of course. The Starter plan is just the site. When you're ready to get more customers, upgrade to Business or Growth and we activate the campaigns.",
        },
        {
          q: "How long before I see campaign results?",
          a: "First contacts usually arrive within 2-4 weeks. Growth becomes stable after 2-3 months of active campaigns.",
        },
        {
          q: "Can I cancel anytime?",
          a: "Yes, no commitment. You can cancel the monthly plan anytime. The Starter site (one-time) is yours forever.",
        },
      ],
    },
    footer: {
      description:
        "E-quipe creates your website with artificial intelligence and manages ad campaigns to bring you real customers.",
      product: "Product",
      productLinks: {
        howItWorks: "How It Works",
        features: "Features",
        pricing: "Pricing",
        dashboard: "Dashboard",
      },
      company: "Company",
      companyLinks: {
        about: "About Us",
        contact: "Contact",
        blog: "Blog",
      },
      legal: "Legal",
      legalLinks: {
        privacy: "Privacy Policy",
        terms: "Terms of Service",
        cookies: "Cookie Policy",
      },
      bottomLinks: {
        privacy: "Privacy",
        terms: "Terms",
        cookies: "Cookies",
      },
      copyright: "\u00A9 2026 E-quipe S.r.l.s. All rights reserved. VAT: 12345678901",
      chooseYourPath: "Choose your path",
      chooseYourPathDesc: "We offer two distinct solutions: {customSite} (built by our experts) or {aiTech} (do-it-yourself). Pricing and services are specific to each solution.",
      customSite: "Custom Site",
      aiTechnology: "AI Technology",
      aiBuilder: "AI Builder App",
      agencyPortfolio: "Agency Portfolio",
      agencyPricing: "Agency Pricing",
      internalDoc: "Internal document — Reserved use",
    },
    heroAgency: {
      badge: "Free website creation",
      title: "We create your site.",
      titleHighlight: "Free.",
      subtitle: "Pay only if you like it. Zero risks, zero obligations.",
      description: "Tell us about your business and our team creates your professional custom website.",
      descriptionLine2: "If you're not satisfied, you don't spend a penny.",
      cta: "Contact us — it's free",
      ctaSecondary: "Or create it yourself in 60 seconds",
      trustBadges: [
        "200+ businesses already online",
        "No credit card needed",
        "Response within 24h",
      ],
    },
    reviews: [
      {
        name: "Marco Rossi",
        role: "Restaurant Owner, Da Marco",
        text: "Incredible. They redid my restaurant website for free. I only paid when I saw it online. Now I receive reservations every day.",
      },
      {
        name: "Giulia Bianchi",
        role: "Architect",
        text: "I was skeptical about the 'free' part, but it's all true. The site is beautiful and very professional. The team is super helpful.",
      },
      {
        name: "Luca Verdi",
        role: "Personal Trainer",
        text: "A service that was missing. No complicated quotes or blind advances. You see the result and decide. Highly recommended.",
      },
    ],
    howItWorksAgency: {
      title: "How does it work? Simple.",
      subtitle: "From first contact to your site online in 3 steps.",
      steps: [
        {
          title: "1. Contact us",
          description: "Tell us what you do and what style you like. It takes 2 minutes. Fill out the form or message us on WhatsApp.",
        },
        {
          title: "2. We create your site",
          description: "Our team + artificial intelligence builds your custom site. Design, copy, images: all included.",
        },
        {
          title: "3. See and decide",
          description: "We show you the result. Like it? Choose a plan and go live. Don't like it? No cost, no obligation.",
        },
      ],
      cta: "Contact us now — it's free",
    },
    portfolio: {
      title: "Examples of sites we built",
      subtitle: "See the quality we can offer your business.",
      visitSite: "Visit site",
      items: [
        { name: "Professional Force", sector: "Security & Investigations" },
        { name: "Restinone", sector: "Catering & Events" },
        { name: "Fondazione Italiana Sport", sector: "Non-Profit & Sports" },
        { name: "Now Now", sector: "Digital Services" },
        { name: "Rally di Roma Capitale", sector: "Sporting Events" },
        { name: "Max Rendina", sector: "Personal Branding" },
      ],
    },
    contact: {
      title: "Tell us about your business",
      subtitle: "We create your site for free. No commitment.",
      nameLabel: "Name",
      namePlaceholder: "Your name",
      activityLabel: "Business",
      activityPlaceholder: "What's your business? (e.g. restaurant, law firm...)",
      contactLabel: "Contact",
      contactPlaceholder: "Email or phone number",
      hasSiteLabel: "Do you already have a website?",
      hasSiteNo: "No, it's my first site",
      hasSiteYes: "Yes, I want to redo it",
      submit: "I want my free site",
      loading: "Sending...",
      successTitle: "Request Received!",
      successMessage: "Thank you for contacting us. Our team will review your request and respond within 24 hours.",
      privacy: "Your data is safe. No commitment.",
      whatsapp: "Prefer WhatsApp?",
      whatsappLink: "Write us here \u2192",
    },
    featuresAgency: {
      title: "What you get, without spending a penny",
      items: [
        { title: "Custom professional site", description: "Personalized design for your business. Not a generic template." },
        { title: "Perfect on every device", description: "The site adapts to phone, tablet and computer automatically." },
        { title: "AI-written copy", description: "Persuasive copy generated by artificial intelligence for your business." },
        { title: "Hosting and SSL included", description: "Your site is online and secured. No extra costs." },
        { title: "Optimized for Google", description: "SEO-friendly code. Your customers find you more easily." },
        { title: "Edits via chat", description: "Want to change something? Write us and we update the site for you." },
      ],
      cta: "Contact us — it's free",
    },
    aiBuilder: {
      badge: "DIY",
      title: "Prefer to do it yourself?",
      titleLine2: "Try our AI.",
      description: "We built a platform where artificial intelligence creates your site in 60 seconds. Answer 3 questions and the site is ready. Edit it with a click.",
      cta: "Try the AI App",
      floatingBadge1: "\u2713 SEO Optimized",
      floatingBadge2: "\u26A1 Super Fast",
    },
    adsUpsell: {
      title: "Not just websites. We bring customers.",
      description: "A beautiful site without traffic is useless. We manage your Google and Facebook campaigns to bring you real contacts every day.",
      feature1Title: "Precise Targeting",
      feature1Desc: "We show your site only to those searching for your services.",
      feature2Title: "Measurable Results",
      feature2Desc: "Clear reports. You know exactly how much a customer costs.",
      feature3Title: "Creatives Included",
      feature3Desc: "We write the ads and create the graphics.",
      cta: "Discover ads packages \u2192",
    },
    faqAgency: {
      title: "Frequently Asked Questions",
      items: [
        { q: "Is it really free?", a: "Yes, website creation is free. There are no hidden development costs. If you like the result, you only pay the plan you choose (e.g. Presence Pack at \u20AC499 or Client Pack). If you don't like it, no hard feelings." },
        { q: "How long does it take?", a: "Our team, aided by AI, can present you with a complete draft within 24-48 hours of your request." },
        { q: "Will the site be mine or rented?", a: "With the Presence and Growth Pack, after the one-time payment, the site is yours. You only pay a reduced monthly fee for hosting and maintenance." },
        { q: "Can I edit the site myself?", a: "Absolutely. We give you access to a very simple control panel. Or, if you have the included package, just ask us via chat and we do everything for you." },
        { q: "What happens if I stop paying the renewal?", a: "The site will go offline at expiration. You can however request a content export if you want to move elsewhere (subject to payment of any outstanding fees)." },
      ],
    },
    finalCta: {
      title: "Ready to take your business online?",
      subtitle: "Contact us today. We create your site for free, no commitment.",
      cta: "Contact us — it's free",
      ctaSecondary: "Or create it yourself",
    },
    page: {
      mobileCta: "Contact us — it's free",
    },
    aiPage: {
      hero: {
        title: "Your professional website in",
        titleBreak: "60 seconds.",
        subtitle: "Your customers, starting tomorrow.",
        description: "Choose your business, upload your logo and artificial intelligence creates your site. Then we launch ad campaigns to bring you real customers every day.",
        cta: "Create your site for free",
        ctaSecondary: "See how it works",
        browserUrl: "yoursite.e-quipe.app",
        aiCreating: "Your AI is creating the site...",
      },
      steps: {
        badge: "3 Steps",
        title: "From zero to your website, in less than",
        titleBreak: "a coffee break.",
        items: [
          { title: "Describe your business", desc: "Answer 3 simple questions. Name, business type, your main services. That's all." },
          { title: "AI generates your site", desc: "In 60 seconds you have a complete site. Copy, images, colors and animations. All optimized." },
          { title: "Publish and find customers", desc: "The site goes live immediately. Activate ad campaigns to bring you real contacts every day." },
        ],
      },
      features: {
        title: "Everything you need to",
        titleBreak: "be online",
        tabSite: "Create Sites",
        tabAds: "Find Customers",
        site: [
          { title: "Site ready in 60 seconds", desc: "Answer 3 questions. Copy, photos, colors: all generated by AI." },
          { title: "7+ professional styles", desc: "AI picks portfolio designs for your business. Or choose yourself." },
          { title: "Edits via chat", desc: "Tell AI what to change. \"Change the color\", \"add text\". Done." },
          { title: "Perfect on any device", desc: "The site adapts automatically to smartphone, tablet and desktop." },
          { title: "Online with one click", desc: "Hosting, SSL certificate and domain: all included. Publish now." },
          { title: "Built for Google", desc: "AI optimizes titles, descriptions for search engines automatically." },
        ],
        ads: [
          { title: "Meta Ads included", desc: "Instagram and Facebook campaigns managed by our team with AI." },
          { title: "Optimized Google Ads", desc: "Ads on Google for people searching your services in your area." },
          { title: "Monthly report", desc: "Clear dashboard with clicks, leads and cost per contact." },
          { title: "AI Content", desc: "Social posts, ad copy and graphics generated by artificial intelligence." },
          { title: "Dedicated landing pages", desc: "Pages optimized for every ad campaign." },
          { title: "Automated DMs", desc: "Automatically respond to leads from Instagram and Facebook." },
        ],
      },
      adsSection: {
        badge: "Ads Management Service",
        title: "Having a website is not enough.",
        titleHighlight: "You need customers.",
        subtitle: "Our team manages your Meta and Google Ads campaigns with AI support.",
        cards: [
          { title: "Meta Ads", items: ["Instagram + Facebook Ads", "Custom audiences", "Automatic A/B testing", "AI-generated creatives"] },
          { title: "Google Ads", items: ["Google Search Ads", "Keywords for your area", "AI-optimized budget", "Smart conversion tracking"] },
          { title: "Monthly Report", items: ["Results dashboard", "Clicks, leads & conversions", "Cost per contact", "Auto-optimization suggestions"] },
        ],
        flowTitle: "How the Ads service works",
        flowDesc: "We analyze your business \u2192 Create campaigns \u2192 Optimize every week \u2192 Send you the report",
      },
      portfolio: {
        title: "They've already done it",
        subtitle: "Real businesses that went online with E-quipe.",
      },
      testimonials: [
        { name: "Marco R.", role: "Restaurant Owner", text: "I created the site during my lunch break. My old webmaster took 3 months. Truly incredible." },
        { name: "Laura M.", role: "Beautician", text: "I know nothing about technology. But in 60 seconds I had my site online. And Google campaigns bring me 15 new customers per month." },
        { name: "Giuseppe V.", role: "Lawyer", text: "Google campaigns bring us 15 contacts per month. With the monthly report I know exactly how much each new customer costs me." },
      ],
      pricing: {
        title: "Clear pricing. No",
        titleBreak: "surprises.",
        subtitle: "Start with the site, add campaigns when you want to grow.",
        baseBadge: "Website Only",
        baseName: "Basic Site",
        baseDesc: "Your AI site, ready to go live. Pay once, no subscription.",
        baseFeatures: ["Complete AI site (5 pages)", "e-quipe.app domain", "Hosting + SSL included", "Chat edits (5/month)"],
        basePrice: "\u20AC199",
        basePeriod: "one-time",
        baseNoCost: "No monthly cost",
        baseCta: "Create your site",
        divider: "Site + Ads \u2014 Get customers every month",
        plans: [
          { name: "Business", price: "\u20AC49", period: "/month", desc: "For those who want a complete, autonomous site.", features: ["AI multi-page site (5 pg)", "Custom domain", "Hosting + SSL + Backup", "Priority support"], cta: "Choose Business" },
          { name: "Growth", price: "\u20AC99", period: "/month", desc: "Site + campaigns to bring you customers.", features: ["Everything in Business", "Meta Ads (Instagram + Facebook)", "AI Content (4 posts/month)", "Monthly performance report", "Dedicated landing pages"], cta: "Choose Growth", tag: "RECOMMENDED" },
          { name: "Premium", price: "\u20AC199", period: "/month", desc: "Site + Full Ads + Pro content.", features: ["Everything in Growth", "Google Ads included", "1 video + 1 photo per week", "Weekly report"], cta: "Choose Premium" },
        ],
        budgetNote: "* Ad budget excluded from Growth and Premium plans",
      },
      faq: {
        title: "Frequently asked questions",
        items: [
          { q: "Do I need to know how to code?", a: "Absolutely not. Answer 3 questions and AI creates everything: copy, images, colors, animations. You can modify anything via chat, without touching code." },
          { q: "How long does it take to create the site?", a: "60 seconds. Literally. Answer the questions, AI generates the complete site. Then you can modify it as much as you want." },
          { q: "Can I use my own domain (e.g. myname.com)?", a: "Yes, from the Business plan onwards you can connect your custom domain. With the basic plan you use a free e-quipe.app subdomain." },
          { q: "How do ad campaigns work?", a: "Our team creates and manages campaigns on Meta (Instagram + Facebook) and Google. AI optimizes budget and targeting. You receive the contacts." },
          { q: "How much should I spend on advertising?", a: "The ad budget is separate from the plan cost. We recommend a minimum of \u20AC300/month for Meta and \u20AC500/month for Google. Our team helps you decide." },
          { q: "Can I start with just the site and add campaigns later?", a: "Of course! You can start with the Basic Site or Business plan and switch to Growth or Premium anytime. Upgrade is immediate." },
          { q: "How long before I see campaign results?", a: "First requests typically arrive within 7-14 days of activation. Results improve month after month thanks to continuous AI optimization." },
          { q: "Can I cancel anytime?", a: "Yes, no commitment. You can cancel the monthly plan at any time. The one-time basic site is yours to keep." },
        ],
      },
      finalCta: {
        title: "Ready to take your business",
        titleBreak: "online?",
        subtitle: "Create your site in 60 seconds. Free, no credit card required.",
        cta: "Create your site for free",
      },
    },
    adsPage: {
      hero: {
        badge: "Ads Management Service",
        title: "Every euro invested.",
        titleHighlight: "Becomes a customer.",
        subtitle: "Our team manages your campaigns on Google and Meta with AI support. You receive the contacts. We do everything else.",
        cta: "Request free consultation",
        ctaSecondary: "How it works",
        stats: [
          { value: "4", label: "Dedicated AI modules" },
          { value: "24/7", label: "Continuous optimization" },
          { value: "-30%", label: "Average cost per lead" },
          { value: "7d", label: "First results" },
        ],
      },
      whatWeDo: {
        title: "What we do for you",
        subtitle: "A complete ecosystem to bring you customers every day. All managed by our team with AI.",
        services: [
          { title: "Google Ads", desc: "Ads on Google Search, Shopping and Display. We intercept people searching for your services in your area.", features: ["Keyword research", "RSA Ads", "Google Shopping", "Remarketing"] },
          { title: "Meta Ads", desc: "Instagram and Facebook campaigns to reach your ideal audience with AI-generated creatives.", features: ["Instagram Feed & Stories", "Facebook Ads", "Custom audiences", "A/B Testing"] },
          { title: "AI Content", desc: "Images generated with Gemini AI, video prompts for Seedance 2.0 and copy optimized for every platform.", features: ["Gemini AI images", "AI video prompts", "RSA ad copy", "Social posts"] },
          { title: "Analytics & Reports", desc: "Clear dashboard with all the numbers that matter: clicks, leads, cost per contact and ROI.", features: ["Weekly/monthly report", "Cost per lead", "Conversion tracking", "Industry benchmark"] },
          { title: "Landing Pages", desc: "Landing pages optimized for every campaign. AI analyzes and continuously improves.", features: ["Optimized design", "A/B testing", "Quality score", "CRO optimization"] },
          { title: "Automated DMs", desc: "Automatically respond to leads from Instagram and Facebook. No contact lost.", features: ["Auto response", "Lead qualification", "Integrated CRM", "AI follow-up"] },
        ],
      },
      howItWorks: {
        badge: "How it works",
        title: "From consultation to customers",
        titleBreak: "in 4 steps",
        steps: [
          { title: "Free consultation", desc: "We analyze your business, your goals and your target market. No commitment." },
          { title: "AI analyzes the market", desc: "4 AI modules study your industry: keywords, competitors, benchmarks and advertising opportunities." },
          { title: "We launch campaigns", desc: "We create ads, landing pages and optimized content. Campaigns go live in 48 hours." },
          { title: "We optimize every week", desc: "AI monitors and optimizes budget, targeting and creatives. You receive leads and the report." },
        ],
      },
      aiPipeline: {
        badge: "AI-Powered",
        title: "4 AI modules working",
        titleBreak: "for you, 24/7",
        subtitle: "From market analysis to campaign optimization: every phase is automated with safety guardrails and human oversight.",
        modules: [
          { name: "The Investigator", subtitle: "Client & Asset Analysis", desc: "Analyzes the client's website, structure, content and value proposition. Generates a complete business profile.", outputs: ["Business category", "Value proposition", "Landing page score", "Service catalog"] },
          { name: "The Analyst", subtitle: "Trends & Competition", desc: "Studies keywords, competitors, industry benchmarks and seasonal trends. Complete competitive landscape map.", outputs: ["Keyword map (volumes, CPC)", "Seasonality index", "Competitive budget estimate", "SWOT vs competitors"] },
          { name: "The Architect", subtitle: "Marketing Plan", desc: "Cross-references data from previous modules to generate campaigns, keywords, ad copy and target KPIs.", outputs: ["Complete campaign plan", "RSA ad copy", "Budget allocation", "Target KPIs"] },
          { name: "The Broker", subtitle: "Management & Optimization", desc: "Manages budget like an algorithmic investor. Optimizes bids, runs A/B tests and monitors in real-time.", outputs: ["Live campaigns", "Automatic A/B testing", "Real-time bid adjustments", "Alerts and reports"] },
        ],
        safetyTitle: "Built-in safety guardrails",
        safetyDesc: "Absolute budget cap, automatic circuit breaker, human approval for critical decisions, benchmark validation and anomaly detection. AI cannot exceed set limits.",
      },
      contentCreation: {
        title: "Creatives generated by",
        titleBreak: "artificial intelligence",
        subtitle: "You don't need to think about graphics, copy or video. AI creates everything for you, optimized for every platform.",
        tools: [
          { title: "AI Image Generator", desc: "Create images for your ads with Gemini 2.5 Flash. 6 formats available (Feed, Stories, YouTube, Display).", badge: "Gemini AI" },
          { title: "AI Video Creator", desc: "Generate optimized video prompts for Seedance 2.0. Cinematic, social and product demo styles.", badge: "Seedance 2.0" },
          { title: "AI Ad Copy", desc: "15 headlines + 4 RSA descriptions generated automatically. Copy optimized for conversions.", badge: "Multi-Agent AI" },
        ],
      },
      pricing: {
        title: "Complete packs. Clear pricing.",
        subtitle: "All-inclusive solutions with guaranteed savings.",
        packs: [
          { name: "Presence Pack", price: "\u20AC499", setup: "one-time", subscription: "+ \u20AC39/month", desc: "For those who want to be online with a professional site.", features: ["Complete AI homepage", "3 extra pages included (4 total)", "Custom domain (1 year)", "Hosting + SSL + Backup", "Unlimited chat edits"], cta: "Choose Presence Pack" },
          { name: "Clients Pack", price: "\u20AC499", setup: "one-time", subscription: "+ \u20AC199/month", desc: "To start receiving customers from Instagram and Facebook right away.", features: ["Everything in Presence Pack", "Meta Ads (Instagram & Facebook)", "Basic Content (8 AI posts/month)", "Monthly performance report", "Chat support"], cta: "Choose Clients Pack" },
          { name: "Growth Pack", price: "\u20AC499", setup: "FREE SETUP", subscription: "+ \u20AC399/month", desc: "To grow seriously with Google and Meta together.", features: ["Complete Custom Website (8 pages)", "Custom domain included", "Full Ads: Meta Pro + Google Ads", "Automated DMs to leads", "Pro Content (unlimited)", "Detailed weekly report", "Maintenance included", "Priority support"], cta: "Choose Growth Pack", tag: "RECOMMENDED" },
          { name: "Premium Pack", price: "\u20AC1,499", setup: "FREE SETUP", subscription: "+ \u20AC999/month", desc: "For ambitious businesses. A dedicated digital agency.", features: ["Everything in Growth Pack", "Unlimited site pages", "Unlimited campaigns on all channels", "Dedicated account manager", "Monthly marketing strategy", "Custom report and monthly call", "Dedicated 24/7 support"], cta: "Choose Premium Pack" },
        ],
        notes: ["* Ad budget excluded", "** 15% discount for annual payment"],
      },
      testimonials: {
        title: "Real results, real customers",
        reviews: [
          { name: "Marco R.", role: "Restaurant Owner", text: "Meta campaigns bring us 25 extra covers per week. The monthly report is crystal clear, I know exactly how much each customer costs me." },
          { name: "Laura M.", role: "Beautician", text: "Before I was spending on flyers without knowing if they worked. Now with Google Ads I get 15 new contacts per month and I know the cost of each one." },
          { name: "Giuseppe V.", role: "Lawyer", text: "The team manages everything, I only receive qualified contacts. In 3 months I recovered the investment and now the flow is constant." },
        ],
      },
      faq: {
        title: "Frequently asked questions",
        items: [
          { q: "How much ad budget should I spend?", a: "The ad budget is separate from the service cost. We recommend a minimum of \u20AC300/month for Meta and \u20AC500/month for Google. Our team helps you decide based on your goals." },
          { q: "How soon will I see results?", a: "First requests typically arrive within 7-14 days of campaign activation. Results improve month after month thanks to continuous AI optimization." },
          { q: "Do I have to create the ad content?", a: "No, we create everything: copy, images, videos and graphics. AI generates content optimized for every platform and tests them automatically." },
          { q: "How does the report work?", a: "You receive a detailed report (weekly or monthly depending on plan) with clicks, impressions, leads, cost per contact and optimization suggestions. Dashboard always accessible." },
          { q: "Can I choose only the Ads service without a site?", a: "Yes, you can purchase services a la carte. Ads Management starts at \u20AC149/month for Meta Ads. However, an optimized site drastically improves conversions." },
          { q: "What happens if campaigns don't perform?", a: "The system has automatic guardrails: circuit breaker that pauses campaigns if cost per lead exceeds threshold, anomaly detection and weekly review. We don't waste budget." },
          { q: "Can I cancel anytime?", a: "Yes, no commitment. Monthly plans can be canceled at any time. One-time services (site) are yours to keep." },
          { q: "Do you manage my social media accounts too?", a: "Plans with AI Content include creating social media posts. The Growth plan includes 8 AI posts/month, Premium unlimited content. Social media publishing is managed by our team." },
        ],
      },
      finalCta: {
        title: "Ready to receive",
        titleBreak: "customers every day?",
        subtitle: "Free consultation. We analyze your business and show you the potential of AI campaigns.",
        cta: "Request free consultation",
      },
    },
  },
} as const;

// ==================== HELPER: dot-path accessor ====================

function getNestedValue(obj: Record<string, unknown>, path: string): string {
  const keys = path.split(".");
  let current: unknown = obj;
  for (const key of keys) {
    if (current === null || current === undefined || typeof current !== "object") {
      return path;
    }
    current = (current as Record<string, unknown>)[key];
  }
  if (typeof current === "string") return current;
  if (typeof current === "number") return String(current);
  return path;
}

// ==================== CONTEXT ====================

const LanguageContext = createContext<LanguageContextType | null>(null);

export { LanguageContext };

// ==================== HOOK ====================

export function useLanguage(): LanguageContextType {
  const context = useContext(LanguageContext);
  if (!context) {
    throw new Error("useLanguage must be used within a LanguageProvider");
  }
  return context;
}

// ==================== t() HELPER (standalone, for use outside React) ====================

export function t(lang: Language, key: string): string {
  return getNestedValue(translations[lang] as unknown as Record<string, unknown>, key);
}

// ==================== PROVIDER PROPS ====================

export interface LanguageProviderProps {
  children: ReactNode;
  defaultLanguage?: Language;
}

// ==================== PROVIDER ====================

export function useLanguageState(defaultLanguage: Language = "it") {
  const [language, setLanguageState] = useState<Language>(defaultLanguage);

  useEffect(() => {
    const stored = localStorage.getItem("e-quipe-lang") as Language | null;
    if (stored === "it" || stored === "en") {
      setLanguageState(stored);
    }
  }, []);

  const setLanguage = useCallback((lang: Language) => {
    setLanguageState(lang);
    localStorage.setItem("e-quipe-lang", lang);
  }, []);

  const translate = useCallback(
    (key: string): string => {
      return getNestedValue(translations[language] as unknown as Record<string, unknown>, key);
    },
    [language]
  );

  return { language, setLanguage, t: translate };
}

// Re-export type
export type { Language };
