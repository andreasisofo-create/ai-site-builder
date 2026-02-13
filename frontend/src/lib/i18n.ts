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
        { name: "Ristorante Amore", category: "Ristorante", image: "/images/demos/ristorante.png" },
        { name: "Modern Hair Studio", category: "Parrucchiere", image: "/images/demos/parrucchiere.png" },
        { name: "Smile & Co. Dental", category: "Studio Dentistico", image: "/images/demos/dentista.png" },
        { name: "FitZone Gym", category: "Palestra", image: "/images/demos/palestra.png" },
        { name: "Studio Legale Rossi", category: "Studio Professionale", image: "/images/demos/avvocato.png" },
        { name: "Noir & Blanc", category: "E-commerce", image: "/images/demos/ecommerce.png" },
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
      copyright: "\u00A9 2026 E-quipe S.r.l.s. Tutti i diritti riservati. P.IVA: 12345678901",
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
