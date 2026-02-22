/**
 * ai.js — Integrazione OpenRouter + gestione sessioni
 *
 * Usa OpenRouter (API OpenAI-compatibile) per accedere a Claude.
 * Gestisce sessioni in memoria con TTL, limite turni e rilevamento lingua.
 */

import { getKnowledgeContext } from './knowledge.js';

const OPENROUTER_API_KEY = process.env.OPENROUTER_API_KEY;
const MODEL = process.env.AI_MODEL || 'anthropic/claude-3.5-sonnet';
const OPENROUTER_URL = 'https://openrouter.ai/api/v1/chat/completions';

// ─── Sessioni in memoria ──────────────────────────────────────────────────────
const SESSION_TTL_MS = (parseInt(process.env.SESSION_TTL_MINUTES) || 30) * 60 * 1000;
const MAX_TURNS = 10;
const sessions = new Map();

setInterval(() => {
  const ora = Date.now();
  let n = 0;
  for (const [id, s] of sessions.entries()) {
    if (ora - s.lastActivity > SESSION_TTL_MS) { sessions.delete(id); n++; }
  }
  if (n > 0) console.log(`[${new Date().toISOString()}] Sessioni eliminate: ${n}`);
}, 5 * 60 * 1000);

export function getSessionCount() { return sessions.size; }

// ─── Rilevamento lingua ───────────────────────────────────────────────────────
const PAROLE_EN = ['what','when','where','how','who','why','the','is','are','was',
  'have','has','can','will','would','could','should','ticket','schedule','event',
  'rally','program','information','price','map','location','free','stage'];

export function detectLanguage(text) {
  const parole = text.toLowerCase().split(/\s+/);
  return parole.filter(p => PAROLE_EN.includes(p)).length >= 2 ? 'en' : 'it';
}

// ─── System prompt ────────────────────────────────────────────────────────────
function buildSystemPrompt(language) {
  if (language === 'en') {
    return `You are Cesare, the official assistant of the Rally di Roma Capitale 2026 (FIA ERC + CIAR Sparco).

Key confirmed facts:
- Dates: July 4-6, 2026 (CONFIRMED)
- Free admission for all public areas
- HQ and Service Park in Rome for the first time (previously Fiuggi)
- Friday evening: Colosseum Special Stage at 20:05
- Saturday: stages in Frusinate area (Vico nel Lazio, Torre di Cicerone, Santopadre)
- Sunday: Guarcino, Canterano, Jenne Power Stage + Podium in Fiuggi at 18:30
- 2026 is being observed by FIA/WRC Promoter for potential WRC 2027 inclusion

Rules:
- NEVER invent unconfirmed details
- If unsure, redirect to: rallydiromacapitale.it or info@rallydiromacapitale.it
- Be concise (max 3-4 paragraphs), enthusiastic, with Roman flair
- Use HTML formatting when helpful (<b>, <a href>)`;
  }

  return `Sei Cesare, l'assistente ufficiale del Rally di Roma Capitale 2026 (FIA ERC + CIAR Sparco).

Fatti confermati:
- Date: 4-6 luglio 2026 (CONFERMATE)
- Ingresso gratuito in tutte le zone pubbliche
- HQ e Parco Assistenza a Roma per la prima volta (prima era a Fiuggi)
- Venerdì sera: PS Colosseo ore 20:05
- Sabato: prove zona Frusinate (Vico nel Lazio, Torre di Cicerone, Santopadre)
- Domenica: Guarcino, Canterano, Jenne Power Stage + Podio Fiuggi ore 18:30
- 2026 candidata all'osservazione FIA/WRC Promoter per WRC 2027

Regole:
- NON inventare mai dettagli non confermati
- Se non sai, rimanda a: rallydiromacapitale.it o info@rallydiromacapitale.it
- Conciso (max 3-4 paragrafi), appassionato, con carattere romano
- Usa HTML quando utile (<b>, <a href>)`;
}

// ─── Chiamata OpenRouter ──────────────────────────────────────────────────────
async function callOpenRouter(messages, systemPrompt, maxTokens = 500) {
  const resp = await fetch(OPENROUTER_URL, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${OPENROUTER_API_KEY}`,
      'Content-Type': 'application/json',
      'HTTP-Referer': 'https://cesare.e-quipe.app',
      'X-Title': 'Cesare - Rally di Roma Capitale',
    },
    body: JSON.stringify({
      model: MODEL,
      max_tokens: maxTokens,
      messages: [{ role: 'system', content: systemPrompt }, ...messages],
    }),
  });

  if (!resp.ok) {
    const err = await resp.text();
    throw new Error(`OpenRouter error ${resp.status}: ${err}`);
  }
  const data = await resp.json();
  return data.choices[0].message.content;
}

// ─── Chat con sessione ────────────────────────────────────────────────────────
export async function chat(sessionId, message) {
  if (!sessions.has(sessionId)) {
    sessions.set(sessionId, { history: [], lastActivity: Date.now(), language: detectLanguage(message) });
  }
  const s = sessions.get(sessionId);
  s.lastActivity = Date.now();
  if (s.history.length === 0) s.language = detectLanguage(message);
  const language = s.language;

  if (s.history.length >= MAX_TURNS * 2) {
    return {
      response: language === 'en'
        ? 'Conversation limit reached. Please start a new chat.'
        : 'Limite conversazione raggiunto. Inizia una nuova chat.',
      language, sessionId,
    };
  }

  const systemPrompt = buildSystemPrompt(language) + '\n\n--- KNOWLEDGE BASE ---\n' + getKnowledgeContext(message);
  s.history.push({ role: 'user', content: message });

  try {
    const risposta = await callOpenRouter(s.history, systemPrompt);
    s.history.push({ role: 'assistant', content: risposta });
    console.log(`[${new Date().toISOString()}] Chat sessione=${sessionId} lingua=${language} turni=${s.history.length / 2}`);
    return { response: risposta, language, sessionId };
  } catch (e) {
    s.history.pop();
    console.error(`[${new Date().toISOString()}] Errore OpenRouter:`, e.message);
    throw e;
  }
}

// ─── Vision: analisi foto auto da rally ──────────────────────────────────────
export async function analyzeRallyCarPhoto(imageBuffer, mimeType = 'image/jpeg', language = 'it') {
  const base64Image = imageBuffer.toString('base64');
  const prompt = language === 'en'
    ? `You are Cesare, a rally expert. Analyze this rally car photo and provide:
1. 🚗 Car model (e.g. Škoda Fabia RS Rally2, Ford Puma Rally1, etc.)
2. 🔢 Race number (if visible)
3. 🏷️ Main sponsors/livery colors
4. 👤 Driver and team (if recognizable)
5. 🏆 Category (Rally1, Rally2, Rally3, etc.)
6. 💡 Fun facts about this car/driver if you know them
Be honest if you cannot identify something. Answer in English, concise and passionate.`
    : `Sei Cesare, esperto di rally. Analizza questa foto di un'auto da rally e fornisci:
1. 🚗 Modello auto (es. Škoda Fabia RS Rally2, Ford Puma Rally1, ecc.)
2. 🔢 Numero di gara (se visibile)
3. 🏷️ Sponsor principali e colori livrea
4. 👤 Pilota e team (se riconoscibili)
5. 🏆 Categoria (Rally1, Rally2, Rally3, ecc.)
6. 💡 Curiosità su quest'auto/pilota se le conosci
Sii onesto se non riesci a identificare qualcosa. Risposta in italiano, concisa e appassionata.`;

  const resp = await fetch(OPENROUTER_URL, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${OPENROUTER_API_KEY}`,
      'Content-Type': 'application/json',
      'HTTP-Referer': 'https://cesare.e-quipe.app',
      'X-Title': 'Cesare - Rally di Roma Capitale',
    },
    body: JSON.stringify({
      model: MODEL,
      max_tokens: 600,
      messages: [{
        role: 'user',
        content: [
          { type: 'image_url', image_url: { url: `data:${mimeType};base64,${base64Image}` } },
          { type: 'text', text: prompt },
        ],
      }],
    }),
  });

  if (!resp.ok) {
    const err = await resp.text();
    throw new Error(`OpenRouter Vision error ${resp.status}: ${err}`);
  }
  const data = await resp.json();
  console.log(`[${new Date().toISOString()}] Vision: analisi foto completata`);
  return data.choices[0].message.content;
}
