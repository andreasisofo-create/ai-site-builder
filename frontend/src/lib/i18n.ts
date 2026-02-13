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
