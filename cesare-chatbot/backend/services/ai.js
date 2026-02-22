/**
 * ai.js — Integrazione Anthropic Claude e gestione sessioni
 *
 * Gestisce:
 * - Sessioni conversazionali in memoria con TTL e pulizia automatica
 * - Limite turni per sessione (contenimento costi)
 * - System prompt per persona chatbot
 * - Rilevamento lingua automatico
 * - Chiamate all'API Anthropic
 */

import Anthropic from '@anthropic-ai/sdk';
import { getKnowledgeContext } from './knowledge.js';

const client = new Anthropic({ apiKey: process.env.ANTHROPIC_API_KEY });

// Configurazione sessioni
const SESSION_TTL_MS = (parseInt(process.env.SESSION_TTL_MINUTES) || 30) * 60 * 1000;
const MAX_TURNS_PER_SESSION = 10; // limite turni per contenere i costi

// Mappa sessioni in memoria: sessionId → { history, lastActivity, language }
const sessions = new Map();

// Pulizia automatica sessioni scadute ogni 5 minuti
setInterval(() => {
  const ora = Date.now();
  let eliminate = 0;
  for (const [id, sessione] of sessions.entries()) {
    if (ora - sessione.lastActivity > SESSION_TTL_MS) {
      sessions.delete(id);
      eliminate++;
    }
  }
  if (eliminate > 0) {
    console.log(`[${new Date().toISOString()}] Sessioni eliminate per scadenza: ${eliminate}`);
  }
}, 5 * 60 * 1000);

/**
 * Restituisce il numero di sessioni attive. Usato dall'health check.
 * @returns {number}
 */
export function getSessionCount() {
  return sessions.size;
}

/**
 * Parole inglesi comuni per il rilevamento lingua.
 */
const PAROLE_INGLESI = [
  'what', 'when', 'where', 'how', 'who', 'why', 'the', 'is', 'are', 'was',
  'have', 'has', 'can', 'will', 'would', 'could', 'should', 'ticket', 'schedule',
  'event', 'rally', 'program', 'information', 'price', 'map', 'location',
];

/**
 * Rileva la lingua del testo.
 * Default italiano; cambia a inglese se ≥2 parole inglesi riconosciute.
 *
 * @param {string} text
 * @returns {'it'|'en'}
 */
export function detectLanguage(text) {
  const parole = text.toLowerCase().split(/\s+/);
  const trovate = parole.filter((p) => PAROLE_INGLESI.includes(p));
  return trovate.length >= 2 ? 'en' : 'it';
}

/**
 * Costruisce il system prompt per l'assistente.
 *
 * @param {'it'|'en'} language
 * @returns {string}
 */
function buildSystemPrompt(language) {
  if (language === 'en') {
    return `You are Cesare, the official assistant of the Rally di Roma Capitale 2026, a prestigious FIA European Rally Championship event held in the Rome area, Italy.

Your role:
- Provide accurate information about the event, program, tickets, and logistics
- Be friendly, concise, and professional — with a touch of Roman charm
- NEVER invent dates, prices, or details that are not confirmed
- If you don't know something, redirect to the official website: rallydiromacapitale.it or email: info@rallydiromacapitale.it
- Keep responses short and clear (max 3-4 paragraphs)
- When relevant, use HTML formatting for Telegram (bold, links) but keep responses readable as plain text too

Key confirmed facts:
- Dates: July 3-5, 2026 (CONFIRMED)
- Free admission for all public areas
- HQ and Service Park in Rome for the first time (previously in Fiuggi)
- Evening Special Stage at the Colosseum on Friday July 3

Personality: enthusiastic about motorsport, helpful, concise, with Roman flair. Never apologetic or verbose.`;
  }

  return `Sei Cesare, l'assistente ufficiale del Rally di Roma Capitale 2026, prestigiosa gara del FIA European Rally Championship che si svolge nella zona di Roma.

Il tuo ruolo:
- Fornire informazioni accurate su evento, programma, biglietti e logistica
- Essere amichevole, conciso e professionale — con un tocco di carattere romano
- NON inventare mai date, prezzi o dettagli non confermati
- Se non sai qualcosa, indirizza al sito ufficiale: rallydiromacapitale.it oppure email: info@rallydiromacapitale.it
- Risposte brevi e chiare (max 3-4 paragrafi)
- Quando rilevante, usa formattazione HTML per Telegram (grassetto, link) ma mantieni le risposte leggibili anche come testo normale

Fatti confermati da usare nelle risposte:
- Date: 3-5 luglio 2026 (CONFERMATE)
- Ingresso gratuito in tutte le zone pubbliche
- HQ e Parco Assistenza a Roma per la prima volta (prima era a Fiuggi)
- PS serale al Colosseo venerdì 3 luglio alle 20:05
- Candidatura per il WRC 2027

Personalità: appassionata di motorsport, disponibile, concisa, con carattere romano. Mai apologetica o prolissa.`;
}

/**
 * Gestisce un turno di conversazione.
 *
 * @param {string} sessionId - ID univoco della sessione
 * @param {string} message - Messaggio dell'utente
 * @param {'text'|'html'} format - Formato risposta (html per Telegram)
 * @returns {Promise<{response: string, language: string, sessionId: string}>}
 */
export async function chat(sessionId, message, format = 'text') {
  // Crea o recupera sessione
  if (!sessions.has(sessionId)) {
    const lingua = detectLanguage(message);
    sessions.set(sessionId, {
      history: [],
      lastActivity: Date.now(),
      language: lingua,
    });
  }

  const sessione = sessions.get(sessionId);
  sessione.lastActivity = Date.now();

  // Rileva lingua dal primo messaggio se non ancora impostata
  if (sessione.history.length === 0) {
    sessione.language = detectLanguage(message);
  }

  const language = sessione.language;

  // Verifica limite turni
  if (sessione.history.length >= MAX_TURNS_PER_SESSION * 2) {
    const msg =
      language === 'en'
        ? 'This conversation has reached its maximum length. Please start a new chat to continue.'
        : 'Questa conversazione ha raggiunto il limite massimo. Inizia una nuova chat per continuare.';
    return { response: msg, language, sessionId };
  }

  // Arricchisce con contesto dalla knowledge base
  const contestoKnowledge = getKnowledgeContext(message);
  const systemPrompt =
    buildSystemPrompt(language) +
    '\n\n--- KNOWLEDGE BASE ---\n' +
    contestoKnowledge;

  // Aggiunge il messaggio utente alla storia
  sessione.history.push({ role: 'user', content: message });

  try {
    const risposta = await client.messages.create({
      model: 'claude-sonnet-4-6',
      max_tokens: 500,
      system: systemPrompt,
      messages: sessione.history,
    });

    const testoRisposta = risposta.content[0].text;

    // Aggiunge la risposta dell'assistente alla storia
    sessione.history.push({ role: 'assistant', content: testoRisposta });

    console.log(
      `[${new Date().toISOString()}] Chat sessione=${sessionId} lingua=${language} turni=${sessione.history.length / 2}`
    );

    return { response: testoRisposta, language, sessionId };
  } catch (errore) {
    // Rimuovi l'ultimo messaggio utente se la chiamata fallisce
    sessione.history.pop();

    console.error(`[${new Date().toISOString()}] Errore API Anthropic:`, errore.message);
    throw errore;
  }
}

/**
 * Analizza una foto di un'auto da rally con Claude Vision.
 * Identifica modello, livrea, numero di gara, pilota e team se riconoscibili.
 *
 * @param {Buffer} imageBuffer - Buffer dell'immagine
 * @param {string} mimeType - MIME type (es. 'image/jpeg')
 * @param {'it'|'en'} language - Lingua della risposta
 * @returns {Promise<string>} - Risposta testuale con info sull'auto
 */
export async function analyzeRallyCarPhoto(imageBuffer, mimeType = 'image/jpeg', language = 'it') {
  const base64Image = imageBuffer.toString('base64');

  const promptIt =
    'Stai guardando una foto di un\'auto da rally. Sei Cesare, esperto di rally e assistente del Rally di Roma Capitale.\n\n' +
    'Analizza l\'immagine e fornisci:\n' +
    '1. 🚗 Modello dell\'auto (es. Škoda Fabia RS Rally2, Citroën C3 Rally2, Ford Puma Rally1, ecc.)\n' +
    '2. 🔢 Numero di gara (se visibile)\n' +
    '3. 🏷️ Sponsor/livrea principali (colori e marchi visibili)\n' +
    '4. 👤 Pilota e team (se riconoscibili da numeri, livree o decals)\n' +
    '5. 🏆 Categoria (Rally1 WRC, Rally2, Rally3, ecc.)\n' +
    '6. 💡 Curiosità o fatti interessanti su quest\'auto o pilota se li conosci\n\n' +
    'Se non riesci a identificare con certezza qualcosa, dillo chiaramente senza inventare.\n' +
    'Se l\'immagine non mostra un\'auto da rally, spiegalo gentilmente.\n' +
    'Risposta in italiano, concisa e appassionata.';

  const promptEn =
    'You\'re looking at a rally car photo. You are Cesare, rally expert and Rally di Roma Capitale assistant.\n\n' +
    'Analyze the image and provide:\n' +
    '1. 🚗 Car model (e.g. Škoda Fabia RS Rally2, Citroën C3 Rally2, Ford Puma Rally1, etc.)\n' +
    '2. 🔢 Race number (if visible)\n' +
    '3. 🏷️ Main sponsors/livery (visible colors and brands)\n' +
    '4. 👤 Driver and team (if recognizable from numbers, livery or decals)\n' +
    '5. 🏆 Category (Rally1 WRC, Rally2, Rally3, etc.)\n' +
    '6. 💡 Fun facts about this car or driver if you know them\n\n' +
    'If you can\'t identify something with certainty, say so clearly without making things up.\n' +
    'If the image doesn\'t show a rally car, explain it politely.\n' +
    'Answer in English, concise and passionate.';

  try {
    const risposta = await client.messages.create({
      model: 'claude-sonnet-4-6',
      max_tokens: 600,
      messages: [
        {
          role: 'user',
          content: [
            {
              type: 'image',
              source: {
                type: 'base64',
                media_type: mimeType,
                data: base64Image,
              },
            },
            {
              type: 'text',
              text: language === 'en' ? promptEn : promptIt,
            },
          ],
        },
      ],
    });

    console.log(`[${new Date().toISOString()}] Vision: analisi foto rally completata`);
    return risposta.content[0].text;
  } catch (errore) {
    console.error(`[${new Date().toISOString()}] Errore Vision API:`, errore.message);
    throw errore;
  }
}
