"use client";

import { useState, useRef, useEffect, FormEvent, useCallback } from "react";
import { chatMessage } from "@/lib/api";

// ============ TYPES ============

interface Message {
  id: number;
  text: string;
  sender: "bot" | "user";
  timestamp: Date;
  type?: "text" | "contact-form" | "contact-success" | "quick-actions";
}

interface ContactFormData {
  nome: string;
  contatto: string;
  messaggio: string;
}

// ============ KNOWLEDGE BASE ============

interface KnowledgeTopic {
  id: string;
  keywords: string[][];
  answer: string;
  followUp?: string[];
}

const KNOWLEDGE_BASE: KnowledgeTopic[] = [
  {
    id: "creare-sito",
    keywords: [
      ["creare", "sito"],
      ["crea", "sito"],
      ["creo", "sito"],
      ["nuovo", "sito"],
      ["costruire", "sito"],
      ["fare", "sito"],
      ["come", "creare"],
      ["come", "faccio"],
      ["voglio", "creare"],
      ["iniziare"],
      ["primo", "sito"],
      ["generare"],
      ["genera"],
    ],
    answer:
      "Per creare un sito con E-quipe:\n\n" +
      "1. Dalla dashboard, scegli un template tra le 8 categorie (19 stili disponibili)\n" +
      "2. Inserisci i dati della tua attivita: nome, descrizione, colori, logo\n" +
      "3. L'AI genera il tuo sito in circa 60 secondi con animazioni GSAP professionali\n" +
      "4. Puoi poi modificarlo con la chat AI nell'editor",
    followUp: ["modificare-sito", "template", "pubblicare"],
  },
  {
    id: "modificare-sito",
    keywords: [
      ["modificare", "sito"],
      ["modifica", "sito"],
      ["modifico"],
      ["cambiare"],
      ["cambio"],
      ["editare"],
      ["editor"],
      ["personalizzare"],
      ["aggiungere", "sezione"],
      ["cambiare", "colori"],
      ["cambiare", "testi"],
      ["aggiungere", "foto"],
      ["aggiungere", "immagini"],
      ["aggiungere", "video"],
      ["inserire", "video"],
      ["youtube"],
      ["embed"],
      ["codice", "embed"],
    ],
    answer:
      "Per modificare il tuo sito:\n\n" +
      "1. Apri l'editor cliccando \"Modifica\" sul tuo sito nella dashboard\n" +
      "2. Usa la chat AI a destra per descrivere le modifiche\n" +
      "3. Puoi chiedere di cambiare colori, testi, layout, sezioni\n" +
      "4. Puoi aggiungere foto (incolla URL o carica dal dispositivo)\n" +
      "5. Puoi aggiungere video YouTube (incolla il link)\n" +
      "6. Puoi inserire codice embed da qualsiasi provider\n\n" +
      "Le modifiche vengono applicate in tempo reale nell'anteprima.",
    followUp: ["pubblicare", "piani-prezzi"],
  },
  {
    id: "pubblicare",
    keywords: [
      ["pubblicare"],
      ["pubblica"],
      ["pubblico"],
      ["online"],
      ["deploy"],
      ["mettere", "online"],
      ["andare", "online"],
      ["live"],
      ["dominio"],
      ["url"],
      ["link"],
      ["indirizzo"],
      ["visibile"],
      ["vercel"],
    ],
    answer:
      "Per pubblicare il tuo sito:\n\n" +
      "1. Apri l'editor del tuo sito\n" +
      "2. Clicca il pulsante \"Pubblica\" in alto a destra\n" +
      "3. Il sito viene pubblicato su tuosito.e-quipe.app\n\n" +
      "NOTA: La pubblicazione richiede il piano Sito Web (EUR 200) o superiore. Il piano Starter gratuito permette solo l'anteprima.",
    followUp: ["piani-prezzi", "dominio"],
  },
  {
    id: "piani-prezzi",
    keywords: [
      ["piano", "piani"],
      ["prezzo", "prezzi"],
      ["costo", "costi"],
      ["quanto", "costa"],
      ["abbonamento"],
      ["pagamento"],
      ["gratuito", "gratis"],
      ["free"],
      ["starter"],
      ["base"],
      ["premium"],
      ["upgrade"],
      ["pagare"],
      ["comprare"],
      ["acquistare"],
    ],
    answer:
      "I piani E-quipe (pagamento unico, NO abbonamento):\n\n" +
      "STARTER (Gratuito)\n" +
      "- 1 generazione AI, 3 modifiche chat, solo anteprima\n\n" +
      "SITO WEB (EUR 200)\n" +
      "- 3 generazioni AI, 20 modifiche chat\n" +
      "- Pubblicazione su sottodominio e-quipe.app\n\n" +
      "PREMIUM (EUR 500)\n" +
      "- 5 generazioni AI, modifiche illimitate\n" +
      "- Dominio personalizzato incluso\n\n" +
      "SITO + ADS (EUR 700)\n" +
      "- Tutto Premium + gestione campagne Meta Ads e Google Ads\n" +
      "- Gestite dagli esperti di E-quipe",
    followUp: ["creare-sito", "upgrade"],
  },
  {
    id: "template",
    keywords: [
      ["template"],
      ["modello", "modelli"],
      ["temi", "tema"],
      ["categorie"],
      ["ristorante"],
      ["agenzia"],
      ["portfolio"],
      ["business"],
      ["stile", "stili"],
    ],
    answer:
      "Template disponibili in Site Builder:\n\n" +
      "Il piano gratuito usa solo la modalita \"Personalizzato\" (AI crea da zero).\n" +
      "I template richiedono piano Creazione Sito o Premium.\n\n" +
      "4 categorie disponibili:\n" +
      "- Ristorante & Food: 3 stili (Elegante, Accogliente, Moderno)\n" +
      "- Agenzia & Startup: 3 stili (Bold, Pulito, Dark)\n" +
      "- Portfolio & Creativo: 3 stili (Galleria, Minimal, Colorato)\n" +
      "- Business & Professionale: 3 stili (Corporate, Trust, Fresco)\n\n" +
      "Ogni template include 84 varianti di componenti HTML (hero, about, services, gallery, testimonials, contact, pricing, FAQ, footer, ecc.)",
    followUp: ["creare-sito", "piani-prezzi"],
  },
  {
    id: "problema-generazione",
    keywords: [
      ["non", "genera"],
      ["non", "funziona"],
      ["errore", "generazione"],
      ["bloccato"],
      ["non", "carica"],
      ["problema", "generazione"],
      ["sito", "non", "genera"],
    ],
    answer:
      "Se il sito non si genera:\n\n" +
      "1. Verifica la connessione internet e riprova\n" +
      "2. Se il problema persiste, potrebbe essere un sovraccarico temporaneo dei server\n" +
      "3. Attendi qualche minuto e riprova\n" +
      "4. Assicurati di aver inserito il nome del business e la descrizione\n\n" +
      "Se il problema continua, contatta il supporto tramite il pulsante qui sotto.",
    followUp: ["contatto"],
  },
  {
    id: "problema-pubblicazione",
    keywords: [
      ["non", "riesco", "pubblicare"],
      ["non", "pubblica"],
      ["errore", "pubblicazione"],
      ["pubblicazione", "fallita"],
    ],
    answer:
      "Se non riesci a pubblicare il sito:\n\n" +
      "- Verifica di avere un piano Creazione Sito (EUR 200) o Premium (EUR 500)\n" +
      "- Il piano Starter gratuito NON include la pubblicazione\n" +
      "- Per fare l'upgrade, dalla dashboard clicca su uno dei pulsanti di upgrade\n\n" +
      "Se hai gia un piano a pagamento e il problema persiste, contatta il supporto.",
    followUp: ["piani-prezzi", "contatto"],
  },
  {
    id: "problema-modifiche",
    keywords: [
      ["modifiche", "non", "vedono"],
      ["non", "vedo", "modifiche"],
      ["non", "salva"],
      ["non", "aggiorna"],
      ["modifiche", "perse"],
    ],
    answer:
      "Se le modifiche non si vedono:\n\n" +
      "1. Ricarica la pagina dell'editor (F5 o Ctrl+R)\n" +
      "2. Le modifiche vengono salvate automaticamente\n" +
      "3. Verifica di non aver esaurito le modifiche AI del tuo piano\n" +
      "4. Controlla la connessione internet\n\n" +
      "Se il problema persiste, contatta il supporto.",
    followUp: ["contatto", "piani-prezzi"],
  },
  {
    id: "problema-template",
    keywords: [
      ["non", "vedo", "template"],
      ["template", "bloccati"],
      ["template", "non", "disponibili"],
      ["sbloccare", "template"],
    ],
    answer:
      "I template sono disponibili solo con piano Creazione Sito (EUR 200) o Premium (EUR 500).\n\n" +
      "Con il piano Starter gratuito puoi usare solo la modalita \"Personalizzato\", dove l'AI crea il sito da zero basandosi sulla tua descrizione.\n\n" +
      "Per sbloccare i template, fai l'upgrade dalla dashboard.",
    followUp: ["piani-prezzi", "template"],
  },
  {
    id: "problema-login",
    keywords: [
      ["errore", "login"],
      ["non", "riesco", "accedere"],
      ["non", "entra"],
      ["password", "sbagliata"],
      ["accesso", "negato"],
      ["login", "fallito"],
      ["registrazione"],
      ["registrare"],
    ],
    answer:
      "Se hai problemi di accesso:\n\n" +
      "1. Verifica che email e password siano corretti\n" +
      "2. Se hai usato Google per registrarti, usa il pulsante \"Accedi con Google\"\n" +
      "3. Controlla di aver verificato l'email (link nella mail di registrazione)\n" +
      "4. Se hai dimenticato la password, prova il recupero password\n\n" +
      "Se il problema persiste, contatta il supporto.",
    followUp: ["contatto"],
  },
  {
    id: "upgrade",
    keywords: [
      ["cambio", "piano"],
      ["cambiare", "piano"],
      ["upgrade"],
      ["passare", "premium"],
      ["passare", "base"],
      ["migliorare", "piano"],
    ],
    answer:
      "Per cambiare piano:\n\n" +
      "1. Vai alla dashboard\n" +
      "2. Nella sezione upgrade, clicca su \"Creazione Sito - EUR 200\" o \"Premium - EUR 500\"\n" +
      "3. Verrai reindirizzato al pagamento sicuro\n" +
      "4. Dopo il pagamento, il piano si attiva immediatamente\n\n" +
      "Il pagamento e una tantum, non e un abbonamento mensile.",
    followUp: ["piani-prezzi"],
  },
  {
    id: "rimborso",
    keywords: [
      ["rimborso"],
      ["rimborsare"],
      ["soldi", "indietro"],
      ["annullare", "pagamento"],
      ["disdetta"],
    ],
    answer:
      "Per richiedere un rimborso o informazioni sui pagamenti, contatta il supporto direttamente.\n\n" +
      "Usa il pulsante \"Contatta il supporto\" qui sotto per inviarci i tuoi dati e ti risponderemo il prima possibile.",
    followUp: ["contatto"],
  },
  {
    id: "dominio",
    keywords: [
      ["dominio", "personalizzato"],
      ["dominio", "custom"],
      ["mio", "dominio"],
      ["collegare", "dominio"],
      ["dns"],
      ["sottodominio"],
    ],
    answer:
      "Informazioni sul dominio:\n\n" +
      "- Piano Creazione Sito: il sito viene pubblicato su un sottodominio (tuosito.e-quipe.app)\n" +
      "- Piano Premium: dominio personalizzato incluso (es. tuosito.it)\n" +
      "- Il certificato SSL e incluso in tutti i piani a pagamento\n" +
      "- L'hosting e illimitato\n\n" +
      "Per collegare un dominio personalizzato, serve il piano Premium (EUR 500).",
    followUp: ["piani-prezzi", "pubblicare"],
  },
  {
    id: "servizi-professionali",
    keywords: [
      ["servizi", "professionali"],
      ["e-quipe", "studio"],
      ["sito", "complesso"],
      ["e-commerce"],
      ["funzionalita", "avanzate"],
      ["design", "su", "misura"],
      ["integrazioni"],
      ["professionale"],
      ["agenzia"],
    ],
    answer:
      "Per siti piu complessi e personalizzati, e-quipe Studio offre servizi professionali:\n\n" +
      "- Design su misura\n" +
      "- Funzionalita avanzate\n" +
      "- E-commerce\n" +
      "- Integrazioni custom\n" +
      "- Sviluppo web completo\n\n" +
      "Contatta il supporto tramite il pulsante qui sotto per maggiori informazioni.",
    followUp: ["contatto"],
  },
  {
    id: "contatto",
    keywords: [
      ["contatto", "contatti"],
      ["supporto"],
      ["aiuto"],
      ["help"],
      ["assistenza"],
      ["email"],
      ["parlare", "persona"],
      ["operatore"],
      ["umano"],
      ["contattare"],
      ["scrivere"],
      ["chiamare"],
    ],
    answer: "__SHOW_CONTACT_FORM__",
    followUp: [],
  },
];

// ============ QUICK ACTIONS ============

const QUICK_ACTIONS = [
  { label: "Come creare un sito", topicId: "creare-sito" },
  { label: "Piani e prezzi", topicId: "piani-prezzi" },
  { label: "Problemi tecnici", topicId: "problemi-tecnici" },
  { label: "Contatta il supporto", topicId: "contatto" },
];

const PROBLEMS_QUICK_ACTIONS = [
  { label: "Il sito non si genera", topicId: "problema-generazione" },
  { label: "Non riesco a pubblicare", topicId: "problema-pubblicazione" },
  { label: "Le modifiche non si vedono", topicId: "problema-modifiche" },
  { label: "Non vedo i template", topicId: "problema-template" },
  { label: "Errore di login", topicId: "problema-login" },
  { label: "Indietro", topicId: "__back__" },
];

// ============ SMART MATCHING ============

function normalizeText(text: string): string {
  return text
    .toLowerCase()
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .replace(/[^a-z0-9\s]/g, " ")
    .replace(/\s+/g, " ")
    .trim();
}

function findBestMatch(input: string, lastTopicId: string | null): KnowledgeTopic | null {
  const normalized = normalizeText(input);
  const words = normalized.split(" ");

  let bestMatch: KnowledgeTopic | null = null;
  let bestScore = 0;

  for (const topic of KNOWLEDGE_BASE) {
    let topicScore = 0;

    for (const keywordSet of topic.keywords) {
      let allMatch = true;
      let matchCount = 0;

      for (const keyword of keywordSet) {
        const normalizedKeyword = normalizeText(keyword);
        const found = words.some(
          (word) =>
            word === normalizedKeyword ||
            word.startsWith(normalizedKeyword) ||
            normalizedKeyword.startsWith(word)
        );
        if (found) {
          matchCount++;
        } else {
          allMatch = false;
        }
      }

      if (allMatch && keywordSet.length > 0) {
        // Full match bonus: longer keyword sets score higher
        const setScore = keywordSet.length * 3 + matchCount;
        topicScore = Math.max(topicScore, setScore);
      } else if (matchCount > 0) {
        // Partial match
        const partialScore = matchCount;
        topicScore = Math.max(topicScore, partialScore);
      }
    }

    // Context bonus: if this topic is a follow-up of the last topic
    if (lastTopicId) {
      const lastTopic = KNOWLEDGE_BASE.find((t) => t.id === lastTopicId);
      if (lastTopic?.followUp?.includes(topic.id)) {
        topicScore += 1;
      }
    }

    if (topicScore > bestScore) {
      bestScore = topicScore;
      bestMatch = topic;
    }
  }

  // Minimum threshold to avoid false positives
  if (bestScore < 1) return null;

  return bestMatch;
}

// ============ HELPERS ============

function formatTime(date: Date): string {
  return date.toLocaleTimeString("it-IT", { hour: "2-digit", minute: "2-digit" });
}

function sendContactEmail(data: ContactFormData) {
  const subject = encodeURIComponent("Richiesta assistenza - Site Builder");
  const body = encodeURIComponent(
    `Nome: ${data.nome}\nContatto: ${data.contatto}\nMessaggio: ${data.messaggio || "Nessun messaggio aggiuntivo"}`
  );
  window.open(
    `mailto:andrea.sisofo@e-quipe.it?subject=${subject}&body=${body}`,
    "_blank"
  );
}

// ============ COMPONENT ============

export default function HelpChatbot() {
  const [open, setOpen] = useState(false);
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [isTyping, setIsTyping] = useState(false);
  const [lastTopicId, setLastTopicId] = useState<string | null>(null);
  const [showProblems, setShowProblems] = useState(false);
  const [contactForm, setContactForm] = useState<ContactFormData>({
    nome: "",
    contatto: "",
    messaggio: "",
  });
  const [contactFormVisible, setContactFormVisible] = useState(false);

  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  const nextId = useRef(1);
  const initialized = useRef(false);

  const WELCOME_MESSAGE =
    "Ciao! Sono l'assistente AI di E-quipe. Posso aiutarti con qualsiasi domanda sui nostri servizi di creazione siti web e gestione campagne Ads. Come posso aiutarti?";

  const DEFAULT_ANSWER =
    "Non sono sicuro di aver capito la tua domanda. Prova a usare i pulsanti qui sotto oppure riformula la domanda.\n\nPosso aiutarti con: creazione siti, modifiche, pubblicazione, piani e prezzi, gestione Ads e contatto supporto.";

  // Welcome message on first open
  useEffect(() => {
    if (open && !initialized.current) {
      initialized.current = true;
      setMessages([
        {
          id: nextId.current++,
          text: WELCOME_MESSAGE,
          sender: "bot",
          timestamp: new Date(),
        },
      ]);
    }
    if (open) {
      setTimeout(() => inputRef.current?.focus(), 200);
    }
  }, [open]);

  // Scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isTyping, contactFormVisible]);

  const addBotMessage = useCallback(
    (text: string, type?: Message["type"]) => {
      setMessages((prev) => [
        ...prev,
        {
          id: nextId.current++,
          text,
          sender: "bot",
          timestamp: new Date(),
          type: type || "text",
        },
      ]);
    },
    []
  );

  const handleTopicResponse = useCallback(
    (topicId: string) => {
      if (topicId === "__back__") {
        setShowProblems(false);
        return;
      }
      if (topicId === "problemi-tecnici") {
        setShowProblems(true);
        return;
      }

      const topic = KNOWLEDGE_BASE.find((t) => t.id === topicId);
      if (!topic) return;

      setShowProblems(false);
      setLastTopicId(topicId);

      if (topic.answer === "__SHOW_CONTACT_FORM__") {
        setIsTyping(true);
        setTimeout(() => {
          setIsTyping(false);
          addBotMessage(
            "Certo! Per metterti in contatto con il nostro team, compila i campi qui sotto e invieremo la tua richiesta.",
          );
          setContactFormVisible(true);
        }, 300);
      } else {
        setIsTyping(true);
        setTimeout(() => {
          setIsTyping(false);
          addBotMessage(topic.answer);
        }, 300);
      }
    },
    [addBotMessage]
  );

  const handleSubmit = useCallback(
    async (e: FormEvent) => {
      e.preventDefault();
      const text = input.trim();
      if (!text || isTyping) return;

      // Add user message
      setMessages((prev) => [
        ...prev,
        {
          id: nextId.current++,
          text,
          sender: "user",
          timestamp: new Date(),
        },
      ]);
      setInput("");
      setContactFormVisible(false);
      setShowProblems(false);

      // Check for contact keywords locally first (instant)
      const contactMatch = findBestMatch(text, lastTopicId);
      if (contactMatch?.answer === "__SHOW_CONTACT_FORM__") {
        setLastTopicId(contactMatch.id);
        setIsTyping(true);
        setTimeout(() => {
          setIsTyping(false);
          addBotMessage(
            "Certo! Per metterti in contatto con il nostro team, compila i campi qui sotto.",
          );
          setContactFormVisible(true);
        }, 300);
        return;
      }

      setIsTyping(true);

      // Try AI first, fallback to local matching
      try {
        const history = messages
          .filter((m) => m.sender === "user" || m.sender === "bot")
          .slice(-10)
          .map((m) => ({
            role: m.sender === "user" ? "user" : "assistant",
            content: m.text,
          }));

        const result = await chatMessage(text, history);

        setIsTyping(false);

        if (result.reply && !result.error) {
          addBotMessage(result.reply);
        } else {
          // Fallback to local matching
          const match = findBestMatch(text, lastTopicId);
          if (match) {
            setLastTopicId(match.id);
            addBotMessage(match.answer);
          } else {
            addBotMessage(DEFAULT_ANSWER);
          }
        }
      } catch {
        // API failed - fallback to local matching
        setIsTyping(false);
        const match = findBestMatch(text, lastTopicId);
        if (match) {
          setLastTopicId(match.id);
          addBotMessage(match.answer);
        } else {
          addBotMessage(DEFAULT_ANSWER);
        }
      }
    },
    [input, isTyping, lastTopicId, messages, addBotMessage]
  );

  const handleContactSubmit = useCallback(
    (e: FormEvent) => {
      e.preventDefault();
      if (!contactForm.contatto.trim()) return;

      sendContactEmail(contactForm);

      setContactFormVisible(false);
      addBotMessage(
        "Grazie! La tua richiesta e stata inviata a e-quipe Studio.\n\n" +
          "Nome: " + (contactForm.nome || "Non specificato") + "\n" +
          "Contatto: " + contactForm.contatto + "\n" +
          (contactForm.messaggio ? "Messaggio: " + contactForm.messaggio + "\n" : "") +
          "\nTi risponderemo il prima possibile!",
        "contact-success"
      );

      setContactForm({ nome: "", contatto: "", messaggio: "" });
    },
    [contactForm, addBotMessage]
  );

  const handleQuickAction = useCallback(
    (topicId: string) => {
      // Add user message for the quick action
      const action = [...QUICK_ACTIONS, ...PROBLEMS_QUICK_ACTIONS].find(
        (a) => a.topicId === topicId
      );
      if (action && topicId !== "__back__" && topicId !== "problemi-tecnici") {
        setMessages((prev) => [
          ...prev,
          {
            id: nextId.current++,
            text: action.label,
            sender: "user",
            timestamp: new Date(),
          },
        ]);
      }
      setContactFormVisible(false);
      handleTopicResponse(topicId);
    },
    [handleTopicResponse]
  );

  return (
    <>
      {/* Floating toggle button */}
      <button
        onClick={() => setOpen((v) => !v)}
        aria-label="Apri assistenza"
        className="fixed bottom-6 right-6 z-[9999] flex h-14 w-14 items-center justify-center rounded-full bg-blue-600 text-white shadow-lg shadow-blue-600/30 transition-transform hover:scale-105 hover:bg-blue-500 active:scale-95"
      >
        {open ? (
          <svg
            xmlns="http://www.w3.org/2000/svg"
            className="h-6 w-6"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
            strokeWidth={2}
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              d="M6 18L18 6M6 6l12 12"
            />
          </svg>
        ) : (
          <svg
            xmlns="http://www.w3.org/2000/svg"
            className="h-6 w-6"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
            strokeWidth={2}
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"
            />
          </svg>
        )}
      </button>

      {/* Chat window */}
      <div
        className={`fixed bottom-24 right-6 z-[9999] flex flex-col overflow-hidden rounded-2xl border border-white/10 bg-[#111] shadow-2xl transition-all duration-300 ${
          open
            ? "pointer-events-auto translate-y-0 opacity-100"
            : "pointer-events-none translate-y-4 opacity-0"
        }`}
        style={{ width: 380, height: 520 }}
      >
        {/* Header */}
        <div className="flex items-center justify-between border-b border-white/10 bg-gradient-to-r from-blue-600/20 to-violet-600/20 px-4 py-3">
          <div className="flex items-center gap-2.5">
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-gradient-to-br from-blue-500 to-violet-600">
              <svg
                xmlns="http://www.w3.org/2000/svg"
                className="h-4 w-4 text-white"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
                strokeWidth={2}
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  d="M9.813 15.904L9 18.75l-.813-2.846a4.5 4.5 0 00-3.09-3.09L2.25 12l2.846-.813a4.5 4.5 0 003.09-3.09L9 5.25l.813 2.846a4.5 4.5 0 003.09 3.09L15.75 12l-2.846.813a4.5 4.5 0 00-3.09 3.09zM18.259 8.715L18 9.75l-.259-1.035a3.375 3.375 0 00-2.455-2.456L14.25 6l1.036-.259a3.375 3.375 0 002.455-2.456L18 2.25l.259 1.035a3.375 3.375 0 002.455 2.456L21.75 6l-1.036.259a3.375 3.375 0 00-2.455 2.456z"
                />
              </svg>
            </div>
            <div>
              <h3 className="text-sm font-semibold text-white">
                Assistente E-quipe
              </h3>
              <p className="text-[10px] text-slate-400">Sempre disponibile</p>
            </div>
          </div>
          <button
            onClick={() => setOpen(false)}
            aria-label="Chiudi"
            className="rounded p-1 text-slate-400 transition-colors hover:bg-white/10 hover:text-white"
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              className="h-4 w-4"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
              strokeWidth={2}
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                d="M6 18L18 6M6 6l12 12"
              />
            </svg>
          </button>
        </div>

        {/* Messages */}
        <div className="flex-1 space-y-3 overflow-y-auto px-4 py-3 scrollbar-thin scrollbar-thumb-white/10 scrollbar-track-transparent">
          {messages.map((msg) => (
            <div key={msg.id}>
              <div
                className={`flex ${
                  msg.sender === "user" ? "justify-end" : "justify-start"
                }`}
              >
                <div
                  className={`max-w-[85%] whitespace-pre-line rounded-xl px-3 py-2 text-sm leading-relaxed ${
                    msg.sender === "bot"
                      ? msg.type === "contact-success"
                        ? "border border-emerald-500/20 bg-emerald-500/10 text-slate-200"
                        : "border border-blue-500/20 bg-blue-500/10 text-slate-200"
                      : "bg-white/10 text-white"
                  }`}
                >
                  {msg.text}
                </div>
              </div>
              <p
                className={`mt-0.5 text-[10px] text-slate-600 ${
                  msg.sender === "user" ? "text-right" : "text-left"
                }`}
              >
                {formatTime(msg.timestamp)}
              </p>
            </div>
          ))}

          {/* Typing indicator */}
          {isTyping && (
            <div className="flex justify-start">
              <div className="flex items-center gap-1.5 rounded-xl border border-blue-500/20 bg-blue-500/10 px-4 py-2.5">
                <span
                  className="inline-block h-1.5 w-1.5 animate-bounce rounded-full bg-blue-400"
                  style={{ animationDelay: "0ms" }}
                />
                <span
                  className="inline-block h-1.5 w-1.5 animate-bounce rounded-full bg-blue-400"
                  style={{ animationDelay: "150ms" }}
                />
                <span
                  className="inline-block h-1.5 w-1.5 animate-bounce rounded-full bg-blue-400"
                  style={{ animationDelay: "300ms" }}
                />
              </div>
            </div>
          )}

          {/* Contact form inline */}
          {contactFormVisible && !isTyping && (
            <div className="rounded-xl border border-blue-500/20 bg-blue-500/5 p-3">
              <form onSubmit={handleContactSubmit} className="space-y-2.5">
                <div>
                  <label className="mb-1 block text-xs text-slate-400">
                    Nome
                  </label>
                  <input
                    type="text"
                    value={contactForm.nome}
                    onChange={(e) =>
                      setContactForm((prev) => ({
                        ...prev,
                        nome: e.target.value,
                      }))
                    }
                    placeholder="Il tuo nome"
                    className="w-full rounded-lg border border-white/10 bg-white/5 px-3 py-1.5 text-xs text-white placeholder-slate-500 outline-none transition-colors focus:border-blue-500/50"
                  />
                </div>
                <div>
                  <label className="mb-1 block text-xs text-slate-400">
                    Email o Cellulare <span className="text-red-400">*</span>
                  </label>
                  <input
                    type="text"
                    value={contactForm.contatto}
                    onChange={(e) =>
                      setContactForm((prev) => ({
                        ...prev,
                        contatto: e.target.value,
                      }))
                    }
                    placeholder="email@esempio.it o +39..."
                    required
                    className="w-full rounded-lg border border-white/10 bg-white/5 px-3 py-1.5 text-xs text-white placeholder-slate-500 outline-none transition-colors focus:border-blue-500/50"
                  />
                </div>
                <div>
                  <label className="mb-1 block text-xs text-slate-400">
                    Messaggio (opzionale)
                  </label>
                  <textarea
                    value={contactForm.messaggio}
                    onChange={(e) =>
                      setContactForm((prev) => ({
                        ...prev,
                        messaggio: e.target.value,
                      }))
                    }
                    placeholder="Descrivi la tua richiesta..."
                    rows={2}
                    className="w-full resize-none rounded-lg border border-white/10 bg-white/5 px-3 py-1.5 text-xs text-white placeholder-slate-500 outline-none transition-colors focus:border-blue-500/50"
                  />
                </div>
                <button
                  type="submit"
                  disabled={!contactForm.contatto.trim()}
                  className="w-full rounded-lg bg-blue-600 py-2 text-xs font-semibold text-white transition-colors hover:bg-blue-500 disabled:opacity-40 disabled:hover:bg-blue-600"
                >
                  Invia richiesta
                </button>
              </form>
            </div>
          )}

          {/* Quick action buttons */}
          {!isTyping && !contactFormVisible && messages.length > 0 && (
            <div className="flex flex-wrap gap-1.5 pt-1">
              {(showProblems ? PROBLEMS_QUICK_ACTIONS : QUICK_ACTIONS).map(
                (action) => (
                  <button
                    key={action.topicId}
                    onClick={() => handleQuickAction(action.topicId)}
                    className="rounded-full border border-white/10 bg-white/5 px-3 py-1 text-[11px] text-slate-300 transition-colors hover:border-blue-500/30 hover:bg-blue-500/10 hover:text-white"
                  >
                    {action.label}
                  </button>
                )
              )}
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Input */}
        <form
          onSubmit={handleSubmit}
          className="flex items-center gap-2 border-t border-white/10 px-3 py-3"
        >
          <input
            ref={inputRef}
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Scrivi un messaggio..."
            disabled={isTyping}
            className="flex-1 rounded-lg border border-white/10 bg-white/5 px-3 py-2 text-sm text-white placeholder-slate-500 outline-none transition-colors focus:border-blue-500/50 focus:bg-white/10 disabled:opacity-50"
          />
          <button
            type="submit"
            disabled={!input.trim() || isTyping}
            className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-blue-600 text-white transition-colors hover:bg-blue-500 disabled:opacity-40 disabled:hover:bg-blue-600"
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              className="h-4 w-4"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
              strokeWidth={2}
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                d="M5 12h14M12 5l7 7-7 7"
              />
            </svg>
          </button>
        </form>
      </div>
    </>
  );
}
