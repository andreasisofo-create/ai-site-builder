"use client";

import { useState, useRef, useEffect, FormEvent } from "react";

interface Message {
  id: number;
  text: string;
  sender: "bot" | "user";
}

const FAQ: { keywords: RegExp; answer: string }[] = [
  {
    keywords: /\b(creo|creare|crea|nuovo sito|nuova|costruire)\b/i,
    answer:
      "Per creare un sito:\n1) Clicca 'Crea nuovo sito'\n2) Scegli template o personalizzato\n3) Inserisci i dati della tua attivita\n4) L'AI generera il sito in ~60 secondi",
  },
  {
    keywords: /\b(modifico|modifica|modificare|cambio|cambiare|editare|editor)\b/i,
    answer:
      "Puoi modificare il sito usando la chat AI nell'editor. Scrivi cosa vuoi cambiare e l'AI aggiornera il sito.",
  },
  {
    keywords: /\b(pubblico|pubblicare|pubblica|online|deploy|dominio)\b/i,
    answer:
      "Per pubblicare: apri l'editor del sito e clicca 'Pubblica'. Il sito sara online su un sottodominio.",
  },
  {
    keywords: /\b(costo|prezzo|quanto|piano|piani|pagamento|abbonamento)\b/i,
    answer:
      "Piano Starter: Gratuito (1 generazione, preview).\nPiano Creazione Sito: \u20AC200 (3 generazioni, pubblicazione).\nPiano Premium: \u20AC500 (5 generazioni, dominio incluso).",
  },
  {
    keywords: /\b(contatto|contatti|supporto|aiuto|help|assistenza|email)\b/i,
    answer:
      "Per assistenza personalizzata: andrea.sisofo@e-quipe.it oppure visita e-quipe.it",
  },
  {
    keywords: /\b(template|modello|modelli|temi|tema)\b/i,
    answer:
      "I template sono disponibili con i piani a pagamento. Con il piano gratuito puoi creare un sito personalizzato con l'AI.",
  },
];

const DEFAULT_ANSWER =
  "Non ho capito la domanda. Prova a chiedere: come creo un sito, come lo modifico, come lo pubblico, quanto costa.\nPer assistenza: andrea.sisofo@e-quipe.it";

const WELCOME_MESSAGE =
  "Ciao! Come posso aiutarti? Puoi chiedermi come creare, modificare o pubblicare il tuo sito.";

function getAnswer(input: string): string {
  const trimmed = input.trim().toLowerCase();
  for (const faq of FAQ) {
    if (faq.keywords.test(trimmed)) {
      return faq.answer;
    }
  }
  return DEFAULT_ANSWER;
}

export default function HelpChatbot() {
  const [open, setOpen] = useState(false);
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  const nextId = useRef(1);
  const initialized = useRef(false);

  // Add the welcome message the first time the panel opens
  useEffect(() => {
    if (open && !initialized.current) {
      initialized.current = true;
      setMessages([
        { id: nextId.current++, text: WELCOME_MESSAGE, sender: "bot" },
      ]);
    }
    if (open) {
      // Focus the input when panel opens
      setTimeout(() => inputRef.current?.focus(), 150);
    }
  }, [open]);

  // Scroll to bottom when messages change
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  function handleSubmit(e: FormEvent) {
    e.preventDefault();
    const text = input.trim();
    if (!text) return;

    const userMsg: Message = {
      id: nextId.current++,
      text,
      sender: "user",
    };
    const botMsg: Message = {
      id: nextId.current++,
      text: getAnswer(text),
      sender: "bot",
    };

    setMessages((prev) => [...prev, userMsg, botMsg]);
    setInput("");
  }

  return (
    <>
      {/* Floating toggle button */}
      <button
        onClick={() => setOpen((v) => !v)}
        aria-label="Apri assistenza"
        className="fixed bottom-6 right-6 z-[9999] flex h-14 w-14 items-center justify-center rounded-full bg-blue-600 text-white shadow-lg shadow-blue-600/30 transition-transform hover:scale-105 hover:bg-blue-500 active:scale-95"
      >
        {open ? (
          /* X icon when open */
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
          /* Chat bubble icon when closed */
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
        className={`fixed bottom-24 right-6 z-[9999] flex w-[350px] flex-col overflow-hidden rounded-2xl border border-white/10 bg-[#111] shadow-2xl transition-all duration-300 ${
          open
            ? "pointer-events-auto translate-y-0 opacity-100"
            : "pointer-events-none translate-y-4 opacity-0"
        }`}
        style={{ height: 450 }}
      >
        {/* Header */}
        <div className="flex items-center justify-between border-b border-white/10 px-4 py-3">
          <h3 className="text-sm font-semibold text-white">
            Assistenza Site Builder
          </h3>
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
        <div className="flex-1 space-y-3 overflow-y-auto px-4 py-3">
          {messages.map((msg) => (
            <div
              key={msg.id}
              className={`flex ${
                msg.sender === "user" ? "justify-end" : "justify-start"
              }`}
            >
              <div
                className={`max-w-[85%] whitespace-pre-line rounded-xl px-3 py-2 text-sm leading-relaxed ${
                  msg.sender === "bot"
                    ? "border border-blue-500/20 bg-blue-500/10 text-slate-200"
                    : "bg-white/10 text-white"
                }`}
              >
                {msg.text}
              </div>
            </div>
          ))}
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
            className="flex-1 rounded-lg border border-white/10 bg-white/5 px-3 py-2 text-sm text-white placeholder-slate-500 outline-none transition-colors focus:border-blue-500/50 focus:bg-white/10"
          />
          <button
            type="submit"
            disabled={!input.trim()}
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
