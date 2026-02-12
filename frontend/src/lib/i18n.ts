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
      features: "Funzionalita'",
      howItWorks: "Come Funziona",
      adsService: "Servizio Ads",
      pricing: "Prezzi",
      dashboard: "Dashboard",
      login: "Accedi",
      cta: "Crea il Tuo Sito",
    },
    hero: {
      badge: "AI-Powered Website Builder + Ads Management",
      titleLine1: "Crea il tuo sito.",
      titleLine2: "Porta clienti.",
      titleLine3: "Cresci online.",
      description:
        "L'unica piattaforma che crea il tuo sito in 60 secondi E ti porta clienti con campagne Meta e Google Ads gestite da esperti.",
      ctaPrimary: "Crea il Tuo Sito",
      ctaSecondary: "Scopri il Servizio Ads",
      trustNoCode: "Nessun codice",
      trustSetup: "Setup in 60 secondi",
      trustAds: "Ads gestiti da esperti",
      floatingPublished: "Sito Pubblicato!",
      floatingPublishedSub: "Online in 45 secondi",
      floatingAI: "Generato con AI",
    },
    quickStats: {
      creationTime: "60s",
      creationTimeLabel: "Tempo medio creazione",
      templates: "19",
      templatesLabel: "Template professionali",
      animations: "29",
      animationsLabel: "Effetti animazione",
      monitoring: "24/7",
      monitoringLabel: "Monitoraggio Ads",
    },
    howItWorks: {
      title: "Da zero al tuo sito",
      titleHighlight: " in 4 passaggi",
      subtitle: "Nessuna competenza tecnica richiesta. Descrivi, genera, personalizza e pubblica.",
      steps: [
        {
          title: "Descrivi",
          description: "Raccontaci del tuo business, i tuoi servizi e il tuo stile.",
        },
        {
          title: "Genera",
          description: "L'AI crea il tuo sito completo in meno di 60 secondi.",
        },
        {
          title: "Personalizza",
          description: "Modifica colori, testi e immagini con l'editor chat AI.",
        },
        {
          title: "Pubblica",
          description: "Vai online con un click. Dominio e SSL inclusi.",
        },
      ],
    },
    features: {
      title: "Tutto cio' che serve per",
      titleHighlight: " andare online",
      subtitle:
        "Non serve essere designer o sviluppatori. La nostra AI crea siti professionali che sembrano fatti a mano da un esperto.",
      items: [
        {
          title: "AI Generativa",
          description:
            "Descrivi il tuo business e ottieni un sito professionale in 60 secondi. L'AI crea layout, testi e design su misura.",
        },
        {
          title: "19 Template Professionali",
          description:
            "8 categorie, 19 stili unici: ristoranti, SaaS, portfolio, e-commerce, business, blog, eventi.",
        },
        {
          title: "Editor Chat AI",
          description:
            "Modifica il tuo sito parlando con l'AI. Cambia colori, testi e layout in linguaggio naturale.",
        },
        {
          title: "Animazioni GSAP",
          description:
            "29 effetti professionali: scroll, parallax, text-split, magnetic e molto altro.",
        },
        {
          title: "Mobile First",
          description:
            "Ogni sito e' ottimizzato per mobile, tablet e desktop fin dal primo pixel.",
        },
        {
          title: "Pubblica con 1 Click",
          description:
            "Hosting, SSL e sottodominio inclusi. Collega il tuo dominio personalizzato.",
        },
        {
          title: "HTML5 Semantico",
          description:
            "Codice pulito, SEO ottimizzato, accessibile. Pensato per piacere a Google.",
        },
        {
          title: "Design Completo",
          description:
            "Hero, about, servizi, contatti, footer. Tutto incluso, tutto personalizzabile.",
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
            "A/B testing creativo automatico",
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
          title: "Contenuti AI",
          subtitle: "Video + Grafiche",
          items: [
            "Video con Higgsfield AI",
            "Grafiche per ads e social",
            "Avatar parlanti AI",
            "Contenuti ottimizzati per conversione",
          ],
        },
      ],
      flowTitle: "Come funziona il servizio Ads",
      flowStep1Title: "L'IA prepara tutto",
      flowStep1Sub: "Creativita', copy, targeting",
      flowStep2Title: "Gli esperti rivedono e approvano",
      flowStep2Sub: "Supervisione umana esperta",
      flowStep3Title: "Lancio + monitoraggio 24/7",
      flowStep3Sub: "Ottimizzazione continua",
      complianceBadge: "100% conforme alle policy Google — supervisione umana garantita",
    },
    timeline: {
      title: "Il tuo percorso verso la",
      titleHighlight: " crescita",
      subtitle: "Da zero a una crescita stabile in poche settimane.",
      milestones: [
        { time: "Settimana 1", title: "L'AI crea il tuo sito" },
        { time: "Settimana 2", title: "Lancio campagne Ads" },
        { time: "Settimana 4", title: "Primi risultati" },
        { time: "Mese 3", title: "Crescita stabile" },
      ],
    },
    earnings: {
      badge: "Calcolatore ROI",
      title: "Quanto puoi",
      titleHighlight: " guadagnare?",
      subtitle: "Scopri il ritorno stimato sul tuo investimento Ads.",
      budgetLabel: "Budget mensile Ads",
      businessTypeLabel: "Tipo di business",
      businessTypes: {
        ristorante: "Ristorante",
        studio: "Studio Professionale",
        ecommerce: "E-commerce",
        servizi: "Servizi",
      },
      estimatedClientsLabel: "Nuovi clienti stimati/mese",
      estimatedRevenueLabel: "Fatturato stimato/mese",
      estimatedProfitLabel: "Guadagno netto stimato/mese",
      disclaimer: "* Stime basate su dati medi di settore. I risultati possono variare.",
    },
    comparison: {
      title: "Fai da Te",
      titleVs: " vs ",
      titleBrand: "Con E-quipe",
      diy: {
        title: "Fai da Te",
        items: [
          "Web designer: \u20AC2.000-5.000",
          "Agenzia Ads: \u20AC500-1.500/mese",
          "Tempo setup: 2-4 settimane",
          "Gestione continua a carico tuo",
        ],
        totalLabel: "Totale primo anno",
        totalValue: "\u20AC8.000 - 23.000",
      },
      equipe: {
        saveBadge: "RISPARMIA FINO AL 96%",
        title: "Con E-quipe",
        items: [
          "Sito AI: da \u20AC199 una tantum",
          "Ads gestiti: da \u20AC49/mese",
          "Online in 60 secondi",
          "AI + supervisione umana inclusa",
        ],
        totalLabel: "Totale primo anno",
        totalValue: "da \u20AC787",
      },
    },
    stats: {
      sitesGenerated: "Siti generati",
      activeCampaigns: "Campagne ads attive",
      revenueGenerated: "Fatturato generato ai clienti",
      clientRating: "Rating medio clienti",
    },
    pricing: {
      title: "Prezzi semplici,",
      titleHighlight: " senza sorprese",
      subtitle: "Inizia col sito, aggiungi le Ads quando sei pronto a crescere.",
      toggleSite: "Solo Sito",
      toggleSiteAds: "Sito + Ads",
      mostPopular: "Piu' Popolare",
      plans: [
        {
          name: "STARTER",
          price: "199",
          period: "una tantum",
          description: "Il tuo sito AI, subito online",
          features: [
            "Sito AI (1 pagina)",
            "Hosting su sottodominio",
            "Certificato SSL incluso",
            "3 modifiche via chat",
          ],
          adsFeatures: [],
          cta: "Inizia Ora",
        },
        {
          name: "BUSINESS",
          price: "49",
          period: "/mese",
          description: "Sito completo + primi clienti",
          features: [
            "Sito completo multi-pagina",
            "Dominio personalizzato",
            "Modifiche illimitate via chat",
            "SSL e hosting inclusi",
          ],
          adsFeatures: [
            "2 campagne Meta/mese",
            "Report mensile performance",
          ],
          cta: "Scegli Business",
        },
        {
          name: "GROWTH",
          price: "99",
          period: "/mese",
          description: "Crescita accelerata con AI",
          features: [
            "Tutto di Business +",
            "Dominio personalizzato",
            "Modifiche illimitate",
            "Supporto prioritario",
          ],
          adsFeatures: [
            "Google Ads + Meta Ads",
            "DM automatici ai lead",
            "5 contenuti IA/mese",
            "Report settimanale",
          ],
          cta: "Scegli Growth",
        },
        {
          name: "PREMIUM",
          price: "199",
          period: "/mese",
          description: "Tutto illimitato, strategia dedicata",
          features: [
            "Tutto di Growth +",
            "Pagine illimitate",
            "Priorita' massima generazione",
            "Account manager dedicato",
          ],
          adsFeatures: [
            "Campagne illimitate",
            "Contenuti IA illimitati",
            "Strategia dedicata mensile",
            "Supporto prioritario 24/7",
          ],
          cta: "Scegli Premium",
        },
      ],
    },
    testimonials: {
      title: "Amato dai clienti",
      subtitle: "Business di tutta Italia hanno gia' scelto E-quipe per crescere online.",
      items: [
        {
          quote:
            "Ho creato il sito in 10 minuti. Con le campagne Ads ho raddoppiato le prenotazioni in 3 mesi.",
          author: "Marco Rossi",
          role: "Ristorante Da Mario",
        },
        {
          quote:
            "Sito pronto in un'ora, campagne partite il giorno dopo. 15 nuovi clienti al mese.",
          author: "Laura Bianchi",
          role: "Studio Legale",
        },
        {
          quote:
            "L'AI ha capito esattamente il mio stile. Google Ads mi porta 15 contatti a settimana.",
          author: "Giuseppe Verdi",
          role: "Fotografo",
        },
      ],
    },
    faq: {
      title: "Domande frequenti",
      subtitle: "Tutto quello che devi sapere su E-quipe.",
      items: [
        {
          q: "Come funziona la creazione del sito?",
          a: "Scegli un template dalla nostra galleria di 19 stili professionali, descrivi il tuo business in 3 semplici step e l'AI genera il tuo sito completo in meno di 60 secondi. Puoi poi personalizzarlo con l'editor chat AI.",
        },
        {
          q: "Quanto costa il servizio?",
          a: "Il piano Starter parte da \u20AC199 una tantum per il solo sito. Se vuoi anche la gestione Ads, i piani partono da \u20AC49/mese (Business) con campagne Meta incluse. Puoi sempre iniziare col sito e aggiungere Ads dopo.",
        },
        {
          q: "Chi gestisce le mie campagne Ads?",
          a: "Le campagne vengono preparate dalla nostra AI e poi riviste e approvate dagli esperti di E-quipe. Ogni campagna ha supervisione umana garantita e monitoraggio continuo.",
        },
        {
          q: "Posso usare il mio dominio?",
          a: "Certo! Dal piano Business in su puoi collegare il tuo dominio personalizzato. Il piano Starter include un sottodominio gratuito (tuonome.e-quipe.app).",
        },
        {
          q: "Cosa include il monitoraggio 24/7?",
          a: "Il nostro sistema monitora le performance delle tue campagne in tempo reale. Se un annuncio non performa, viene ottimizzato o sostituito automaticamente. Ricevi report periodici con metriche chiare.",
        },
        {
          q: "Posso iniziare solo col sito e aggiungere Ads dopo?",
          a: "Assolutamente si! Puoi partire col piano Starter (solo sito) e fare upgrade a Business o Growth in qualsiasi momento per attivare la gestione Ads.",
        },
        {
          q: "Come sono i siti generati?",
          a: "HTML5 semantico, Tailwind CSS, animazioni GSAP professionali, completamente responsive e SEO-friendly. Codice pulito che piace a Google.",
        },
        {
          q: "Quanto tempo ci vuole per vedere risultati Ads?",
          a: "Primi risultati in 2-4 settimane, crescita stabile in 2-3 mesi. Ogni campagna viene ottimizzata continuamente dall'AI con supervisione umana.",
        },
      ],
    },
    cta: {
      title: "Pronto a crescere online?",
      description: "Sito + Ads: tutto quello che serve per il tuo business.",
      descriptionLine2: "Inizia oggi, risultati domani.",
      ctaPrimary: "Crea il Tuo Sito",
      ctaSecondary: "Contattaci",
    },
    footer: {
      brandDescription:
        "E-quipe S.r.l.s \u2014 La piattaforma AI che crea il tuo sito web e gestisce le tue campagne Ads per farti crescere online.",
      productTitle: "Prodotto",
      productFeatures: "Funzionalita'",
      productHowItWorks: "Come Funziona",
      productPricing: "Prezzi",
      productDashboard: "Dashboard",
      adsTitle: "Servizi Ads",
      adsMetaAds: "Meta Ads",
      adsGoogleAds: "Google Ads",
      adsAIContent: "Contenuti AI",
      supportTitle: "Supporto",
      supportContact: "Contatti",
      supportFAQ: "FAQ",
      supportPrivacy: "Privacy Policy",
      supportTerms: "Termini di Servizio",
      copyright: "\u00A9 2026 E-quipe S.r.l.s. Tutti i diritti riservati.",
      footerPrivacy: "Privacy",
      footerTerms: "Termini",
      footerCookies: "Cookie",
    },
  },

  en: {
    nav: {
      features: "Features",
      howItWorks: "How It Works",
      adsService: "Ads Service",
      pricing: "Pricing",
      dashboard: "Dashboard",
      login: "Sign In",
      cta: "Build Your Site",
    },
    hero: {
      badge: "AI-Powered Website Builder + Ads Management",
      titleLine1: "Build your site.",
      titleLine2: "Attract clients.",
      titleLine3: "Grow online.",
      description:
        "The only platform that builds your website in 60 seconds AND brings you clients with expert-managed Meta and Google Ads campaigns.",
      ctaPrimary: "Build Your Site",
      ctaSecondary: "Discover Ads Service",
      trustNoCode: "No coding needed",
      trustSetup: "Setup in 60 seconds",
      trustAds: "Expert-managed Ads",
      floatingPublished: "Site Published!",
      floatingPublishedSub: "Online in 45 seconds",
      floatingAI: "AI-Generated",
    },
    quickStats: {
      creationTime: "60s",
      creationTimeLabel: "Avg. creation time",
      templates: "19",
      templatesLabel: "Professional templates",
      animations: "29",
      animationsLabel: "Animation effects",
      monitoring: "24/7",
      monitoringLabel: "Ads monitoring",
    },
    howItWorks: {
      title: "From zero to your site",
      titleHighlight: " in 4 steps",
      subtitle: "No technical skills required. Describe, generate, customize, and publish.",
      steps: [
        {
          title: "Describe",
          description: "Tell us about your business, services, and style.",
        },
        {
          title: "Generate",
          description: "AI creates your complete website in under 60 seconds.",
        },
        {
          title: "Customize",
          description: "Edit colors, text, and images with the AI chat editor.",
        },
        {
          title: "Publish",
          description: "Go live with one click. Domain and SSL included.",
        },
      ],
    },
    features: {
      title: "Everything you need to",
      titleHighlight: " go online",
      subtitle:
        "No need to be a designer or developer. Our AI creates professional websites that look handcrafted by an expert.",
      items: [
        {
          title: "Generative AI",
          description:
            "Describe your business and get a professional website in 60 seconds. AI creates layout, copy, and design tailored to you.",
        },
        {
          title: "19 Professional Templates",
          description:
            "8 categories, 19 unique styles: restaurants, SaaS, portfolio, e-commerce, business, blog, events.",
        },
        {
          title: "AI Chat Editor",
          description:
            "Edit your website by chatting with AI. Change colors, text, and layout using natural language.",
        },
        {
          title: "GSAP Animations",
          description:
            "29 professional effects: scroll, parallax, text-split, magnetic, and much more.",
        },
        {
          title: "Mobile First",
          description:
            "Every site is optimized for mobile, tablet, and desktop from the first pixel.",
        },
        {
          title: "1-Click Publish",
          description:
            "Hosting, SSL, and subdomain included. Connect your custom domain.",
        },
        {
          title: "Semantic HTML5",
          description:
            "Clean code, SEO optimized, accessible. Built to rank on Google.",
        },
        {
          title: "Complete Design",
          description:
            "Hero, about, services, contact, footer. All included, all customizable.",
        },
      ],
    },
    ads: {
      badge: "Ads Management Service",
      title: "A website isn't enough.",
      titleHighlight: "You need clients.",
      subtitle:
        "Our team manages your Meta and Google Ads campaigns powered by artificial intelligence.",
      columns: [
        {
          title: "Meta Ads",
          subtitle: "Instagram + Facebook",
          items: [
            "Instagram & Facebook campaigns",
            "Automatic creative A/B testing",
            "Automated DMs to leads",
            "AI-powered advanced targeting",
          ],
        },
        {
          title: "Google Ads",
          subtitle: "Search + Display",
          items: [
            "Search & Display campaigns",
            "AI keyword optimization",
            "Guaranteed policy compliance",
            "Smart automatic bidding",
          ],
        },
        {
          title: "AI Content",
          subtitle: "Video + Graphics",
          items: [
            "Videos with Higgsfield AI",
            "Ad and social graphics",
            "AI talking avatars",
            "Conversion-optimized content",
          ],
        },
      ],
      flowTitle: "How the Ads service works",
      flowStep1Title: "AI prepares everything",
      flowStep1Sub: "Creatives, copy, targeting",
      flowStep2Title: "Experts review and approve",
      flowStep2Sub: "Expert human oversight",
      flowStep3Title: "Launch + 24/7 monitoring",
      flowStep3Sub: "Continuous optimization",
      complianceBadge: "100% Google policy compliant \u2014 guaranteed human oversight",
    },
    timeline: {
      title: "Your path to",
      titleHighlight: " growth",
      subtitle: "From zero to stable growth in just a few weeks.",
      milestones: [
        { time: "Week 1", title: "AI builds your site" },
        { time: "Week 2", title: "Ads campaigns launch" },
        { time: "Week 4", title: "First results" },
        { time: "Month 3", title: "Stable growth" },
      ],
    },
    earnings: {
      badge: "ROI Calculator",
      title: "How much can you",
      titleHighlight: " earn?",
      subtitle: "Discover the estimated return on your Ads investment.",
      budgetLabel: "Monthly Ads budget",
      businessTypeLabel: "Business type",
      businessTypes: {
        ristorante: "Restaurant",
        studio: "Professional Office",
        ecommerce: "E-commerce",
        servizi: "Services",
      },
      estimatedClientsLabel: "Estimated new clients/month",
      estimatedRevenueLabel: "Estimated revenue/month",
      estimatedProfitLabel: "Estimated net profit/month",
      disclaimer: "* Estimates based on industry averages. Results may vary.",
    },
    comparison: {
      title: "DIY",
      titleVs: " vs ",
      titleBrand: "With E-quipe",
      diy: {
        title: "DIY",
        items: [
          "Web designer: \u20AC2,000\u20135,000",
          "Ads agency: \u20AC500\u20131,500/month",
          "Setup time: 2\u20134 weeks",
          "Ongoing management on you",
        ],
        totalLabel: "Total first year",
        totalValue: "\u20AC8,000 \u2013 23,000",
      },
      equipe: {
        saveBadge: "SAVE UP TO 96%",
        title: "With E-quipe",
        items: [
          "AI website: from \u20AC199 one-time",
          "Managed Ads: from \u20AC49/month",
          "Online in 60 seconds",
          "AI + human oversight included",
        ],
        totalLabel: "Total first year",
        totalValue: "from \u20AC787",
      },
    },
    stats: {
      sitesGenerated: "Sites generated",
      activeCampaigns: "Active ad campaigns",
      revenueGenerated: "Revenue generated for clients",
      clientRating: "Average client rating",
    },
    pricing: {
      title: "Simple pricing,",
      titleHighlight: " no surprises",
      subtitle: "Start with your site, add Ads when you're ready to grow.",
      toggleSite: "Site Only",
      toggleSiteAds: "Site + Ads",
      mostPopular: "Most Popular",
      plans: [
        {
          name: "STARTER",
          price: "199",
          period: "one-time",
          description: "Your AI website, instantly online",
          features: [
            "AI website (1 page)",
            "Subdomain hosting",
            "SSL certificate included",
            "3 chat edits",
          ],
          adsFeatures: [],
          cta: "Get Started",
        },
        {
          name: "BUSINESS",
          price: "49",
          period: "/month",
          description: "Full website + first clients",
          features: [
            "Full multi-page website",
            "Custom domain",
            "Unlimited chat edits",
            "SSL and hosting included",
          ],
          adsFeatures: [
            "2 Meta campaigns/month",
            "Monthly performance report",
          ],
          cta: "Choose Business",
        },
        {
          name: "GROWTH",
          price: "99",
          period: "/month",
          description: "Accelerated growth with AI",
          features: [
            "Everything in Business +",
            "Custom domain",
            "Unlimited edits",
            "Priority support",
          ],
          adsFeatures: [
            "Google Ads + Meta Ads",
            "Automated DMs to leads",
            "5 AI contents/month",
            "Weekly report",
          ],
          cta: "Choose Growth",
        },
        {
          name: "PREMIUM",
          price: "199",
          period: "/month",
          description: "Everything unlimited, dedicated strategy",
          features: [
            "Everything in Growth +",
            "Unlimited pages",
            "Top priority generation",
            "Dedicated account manager",
          ],
          adsFeatures: [
            "Unlimited campaigns",
            "Unlimited AI content",
            "Dedicated monthly strategy",
            "24/7 priority support",
          ],
          cta: "Choose Premium",
        },
      ],
    },
    testimonials: {
      title: "Loved by clients",
      subtitle: "Businesses across Italy have already chosen E-quipe to grow online.",
      items: [
        {
          quote:
            "I built my site in 10 minutes. With Ads campaigns, I doubled my bookings in 3 months.",
          author: "Marco Rossi",
          role: "Ristorante Da Mario",
        },
        {
          quote:
            "Site ready in an hour, campaigns live the next day. 15 new clients per month.",
          author: "Laura Bianchi",
          role: "Law Firm",
        },
        {
          quote:
            "The AI understood my style perfectly. Google Ads brings me 15 leads per week.",
          author: "Giuseppe Verdi",
          role: "Photographer",
        },
      ],
    },
    faq: {
      title: "Frequently asked questions",
      subtitle: "Everything you need to know about E-quipe.",
      items: [
        {
          q: "How does website creation work?",
          a: "Choose a template from our gallery of 19 professional styles, describe your business in 3 simple steps, and AI generates your complete website in under 60 seconds. You can then customize it with the AI chat editor.",
        },
        {
          q: "How much does it cost?",
          a: "The Starter plan starts at \u20AC199 one-time for the website only. If you also want Ads management, plans start at \u20AC49/month (Business) with Meta campaigns included. You can always start with the site and add Ads later.",
        },
        {
          q: "Who manages my Ads campaigns?",
          a: "Campaigns are prepared by our AI and then reviewed and approved by E-quipe experts. Every campaign has guaranteed human oversight and continuous monitoring.",
        },
        {
          q: "Can I use my own domain?",
          a: "Absolutely! From the Business plan and up, you can connect your custom domain. The Starter plan includes a free subdomain (yourname.e-quipe.app).",
        },
        {
          q: "What does 24/7 monitoring include?",
          a: "Our system monitors your campaign performance in real time. If an ad underperforms, it's automatically optimized or replaced. You receive periodic reports with clear metrics.",
        },
        {
          q: "Can I start with just the site and add Ads later?",
          a: "Of course! You can start with the Starter plan (site only) and upgrade to Business or Growth at any time to activate Ads management.",
        },
        {
          q: "What are the generated sites like?",
          a: "Semantic HTML5, Tailwind CSS, professional GSAP animations, fully responsive and SEO-friendly. Clean code that Google loves.",
        },
        {
          q: "How long until I see Ads results?",
          a: "First results in 2\u20134 weeks, stable growth in 2\u20133 months. Every campaign is continuously optimized by AI with human oversight.",
        },
      ],
    },
    cta: {
      title: "Ready to grow online?",
      description: "Site + Ads: everything your business needs.",
      descriptionLine2: "Start today, see results tomorrow.",
      ctaPrimary: "Build Your Site",
      ctaSecondary: "Contact Us",
    },
    footer: {
      brandDescription:
        "E-quipe S.r.l.s \u2014 The AI platform that builds your website and manages your Ads campaigns to help you grow online.",
      productTitle: "Product",
      productFeatures: "Features",
      productHowItWorks: "How It Works",
      productPricing: "Pricing",
      productDashboard: "Dashboard",
      adsTitle: "Ads Services",
      adsMetaAds: "Meta Ads",
      adsGoogleAds: "Google Ads",
      adsAIContent: "AI Content",
      supportTitle: "Support",
      supportContact: "Contact",
      supportFAQ: "FAQ",
      supportPrivacy: "Privacy Policy",
      supportTerms: "Terms of Service",
      copyright: "\u00A9 2026 E-quipe S.r.l.s. All rights reserved.",
      footerPrivacy: "Privacy",
      footerTerms: "Terms",
      footerCookies: "Cookies",
    },
  },
} as const;

// ==================== HELPER: dot-path accessor ====================

function getNestedValue(obj: Record<string, unknown>, path: string): string {
  const keys = path.split(".");
  let current: unknown = obj;
  for (const key of keys) {
    if (current === null || current === undefined || typeof current !== "object") {
      return path; // fallback: return the key itself
    }
    current = (current as Record<string, unknown>)[key];
  }
  if (typeof current === "string") return current;
  if (typeof current === "number") return String(current);
  return path; // fallback
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

// ==================== PROVIDER (exported as value, wrapped by component file) ====================

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
