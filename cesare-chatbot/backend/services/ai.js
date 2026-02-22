/**
 * ai.js — Integrazione OpenRouter + gestione sessioni
 *
 * Usa OpenRouter (API OpenAI-compatibile) per accedere a Claude.
 * Gestisce sessioni in memoria con TTL, limite turni e rilevamento lingua.
 */

import { getKnowledgeContext } from './knowledge.js';
import { getPartecipantiContext } from './rallyCarDatabase.js';

const OPENROUTER_API_KEY = process.env.OPENROUTER_API_KEY;
const MODEL = process.env.AI_MODEL || 'google/gemini-2.0-flash-001';
const OPENROUTER_URL = 'https://openrouter.ai/api/v1/chat/completions';

// ─── Sessioni in memoria ──────────────────────────────────────────────────────
const SESSION_TTL_MS = (parseInt(process.env.SESSION_TTL_MINUTES) || 30) * 60 * 1000;
const MAX_TURNS = 0; // 0 = nessun limite
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

export function injectExchange(sessionId, userMessage, assistantMessage) {
  if (!sessions.has(sessionId)) {
    sessions.set(sessionId, { history: [], lastActivity: Date.now(), language: 'it' });
  }
  const s = sessions.get(sessionId);
  s.lastActivity = Date.now();
  s.history.push({ role: 'user', content: userMessage });
  s.history.push({ role: 'assistant', content: assistantMessage });
}

// ─── Rilevamento lingua ───────────────────────────────────────────────────────
const PAROLE_EN = ['what','when','where','how','who','why','the','is','are','was',
  'have','has','can','will','would','could','should','ticket','schedule','event',
  'rally','program','information','price','map','location','free','stage'];

export function detectLanguage(text) {
  const parole = text.toLowerCase().split(/\s+/);
  return parole.filter(p => PAROLE_EN.includes(p)).length >= 2 ? 'en' : 'it';
}

// ─── System prompt ────────────────────────────────────────────────────────────
function buildSystemPrompt() {
  return `Sei Cesare, il leone mascotte e assistente virtuale ufficiale del Rally di Roma Capitale 2026 (FIA ERC + CIAR Sparco)!

REGOLA LINGUA — FONDAMENTALE:
Rileva automaticamente la lingua dell'utente e rispondi SEMPRE nella stessa lingua.
Parli fluentemente TUTTE le lingue del mondo: italiano, inglese, spagnolo, francese, tedesco, portoghese, arabo, cinese, giapponese, russo, olandese, polacco, e molte altre.
Se l'utente scrive in spagnolo → rispondi in spagnolo. In francese → francese. In inglese → inglese. Ecc.

PERSONALITÀ:
- Dai SEMPRE del TU (mai "Lei" o "Vous" formale o "Sie" formale — usa sempre il registro informale)
- Sei amichevole, caloroso, un po' scherzoso ma sempre professionale
- Ami il rally con passione genuina — sei il "friend expert" dell'evento
- Saluti con "Ciao!" / "Hey!" / "¡Hola!" / "Salut!" ecc. a seconda della lingua
- Puoi fare battute leggere sul rally e sulla velocità
- NON sei mai freddo, distaccato o robotico — sei come un amico appassionato
- Usi emoji con moderazione per rendere le risposte vivaci 🏎️

FATTI CONFERMATI:
- Date: 4-6 luglio 2026 / July 4-6, 2026 (CONFERMATE)
- Ingresso GRATUITO in tutte le zone pubbliche
- HQ e Parco Assistenza a Roma per la prima volta (prima era a Fiuggi)
- Venerdì: PS Colosseo ore 20:05 | Parata ore 18:00 Bocca della Verità
- Sabato: zona Frusinate (Vico nel Lazio, Torre di Cicerone, Santopadre)
- Domenica: Guarcino, Canterano, Jenne Power Stage + Podio Fiuggi ore 18:30
- 2026 sotto osservazione FIA/WRC Promoter per possibile WRC 2027

REGOLE:
- NON inventare mai dettagli non confermati
- Se non sai, rimanda a: rallydiromacapitale.it o info@rallydiromacapitale.it
- Risposte concise (max 3-4 paragrafi brevi)
- Usa HTML quando utile (<b>, <a href>)
- VIETATO dialetto romanesco o slang eccessivo`;
}

// ─── Chiamata OpenRouter (con retry automatico) ───────────────────────────────
async function callOpenRouter(messages, systemPrompt, maxTokens = 300, retry = 1) {
  const doRequest = async () => {
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
        provider: { sort: 'latency' },
        messages: [{ role: 'system', content: systemPrompt }, ...messages],
      }),
    });

    if (!resp.ok) {
      const err = await resp.text();
      throw new Error(`OpenRouter error ${resp.status}: ${err}`);
    }
    const data = await resp.json();
    return data.choices[0].message.content;
  };

  try {
    return await doRequest();
  } catch (e) {
    // Retry una volta su errori transitori (timeout, 500, 503)
    if (retry > 0 && (e.message.includes('500') || e.message.includes('503') || e.message.includes('fetch'))) {
      console.warn(`[${new Date().toISOString()}] OpenRouter retry dopo errore: ${e.message.substring(0, 80)}`);
      await new Promise(r => setTimeout(r, 1000));
      return callOpenRouter(messages, systemPrompt, maxTokens, 0);
    }
    throw e;
  }
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

  // Limite turni disabilitato per test (MAX_TURNS = 0)
  // if (s.history.length >= MAX_TURNS * 2) { ... }

  const systemPrompt = buildSystemPrompt() + '\n\n--- KNOWLEDGE BASE ---\n' + getKnowledgeContext(message);
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
export async function analyzeRallyCarPhoto(imageBuffer, mimeType = 'image/jpeg', language = 'it', sessionId = null) {
  const base64Image = imageBuffer.toString('base64');

  // Recupera il contesto partecipanti dal database (se disponibile)
  let partecipantiContext = '';
  try {
    partecipantiContext = getPartecipantiContext();
  } catch (e) {
    partecipantiContext = '(database partecipanti non disponibile)';
  }

  const prompt = language === 'en'
    ? `You are the Photo Agent of Cesare, official assistant of Rally di Roma Capitale 2026.

A user has sent this photo. Follow EXACTLY these steps:

STEP 1 — VALIDATION:
Determine if the photo shows A RALLY CAR in competition or in paddock.
Criteria: competition bodywork, visible roll cage, race number, racing livery, sponsor decals.
If it is NOT a rally car, respond ONLY: "RIFIUTO"

STEP 2 — RALLY DI ROMA CONTEXT:
Look for elements in the photo indicating Rally di Roma Capitale:
- "Rally di Roma Capitale" or "Rally Roma Capitale" logos on the car
- Roman monuments in the background (Colosseum, etc.)
- ERC/CIAR logos with "Fiuggi" or "Roma"
If the photo seems to be from another rally (WRC in Finland, etc.), note it but proceed with the analysis if it is still a rally car.

STEP 3 — IDENTIFICATION (only if STEP 1 = rally car):
Read carefully the REAR WINDOW (usually has the race number and names in small print):
1. 🔢 Race number (large number on the side or rear window)
2. 👤 Driver and Co-driver (names on rear window or tailgate)
3. 🚗 Car model (Škoda Fabia RS Rally2, Hyundai i20 N Rally2, Citroën C3 Rally2, Ford Puma Rally1, Toyota GR Yaris Rally2, etc.)
4. 🏷️ Team and main sponsors visible on the livery
5. 🏆 Category (Rally1, Rally2, Rally3, ERC, CIAR, etc.)
6. 🌍 Crew nationality if visible (flag)

STEP 4 — CROSS-CHECK WITH DATABASE:
${partecipantiContext}

If you find the race number in the database, confirm the data and add extra info about the crew.

Answer in English, concise and passionate. Use HTML (<b>, emoji). MAX 300 words.`
    : `Sei il Photo Agent di Cesare, assistente ufficiale del Rally di Roma Capitale 2026.

Un utente ha inviato questa foto. Segui ESATTAMENTE questi passi:

PASSO 1 — VALIDAZIONE:
Determina se la foto mostra UN'AUTO DA RALLY in gara o in paddock.
Criteri: carrozzeria da competizione, roll cage visibile, numero gara, livrea racing, decals sponsor.
Se NON è un'auto da rally, rispondi SOLO: "RIFIUTO"

PASSO 2 — CONTESTO RALLY DI ROMA:
Cerca nella foto elementi che indicano Rally di Roma Capitale:
- Loghi "Rally di Roma Capitale" o "Rally Roma Capitale" sull'auto
- Monumenti romani sullo sfondo (Colosseo, ecc.)
- Loghi ERC/CIAR con "Fiuggi" o "Roma"
Se la foto sembra di un altro rally (WRC in Finlandia, ecc.), segnalalo ma procedi ugualmente con l'analisi se è comunque un'auto da rally.

PASSO 3 — IDENTIFICAZIONE (solo se PASSO 1 = auto da rally):
Leggi attentamente il VETRO POSTERIORE (di solito ha scritti in piccolo il numero gara e i nomi):
1. 🔢 Numero di gara (numero grande sul fianco o lunotto)
2. 👤 Pilota e Copilota (nomi scritti sul vetro posteriore o lunotto)
3. 🚗 Modello auto (Škoda Fabia RS Rally2, Hyundai i20 N Rally2, Citroën C3 Rally2, Ford Puma Rally1, Toyota GR Yaris Rally2, ecc.)
4. 🏷️ Team e sponsor principali visibili sulla livrea
5. 🏆 Categoria (Rally1, Rally2, Rally3, ERC, CIAR, ecc.)
6. 🌍 Nazionalità dell'equipaggio se visibile (bandiera)

PASSO 4 — INCROCIA CON DATABASE:
${partecipantiContext}

Se trovi il numero di gara nel database, conferma i dati e aggiungi info extra sull'equipaggio.

Rispondi in italiano, conciso e appassionato. Usa HTML (<b>, emoji). MAX 300 parole.`;

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
  const risposta = data.choices[0].message.content;

  // Se il modello ha rilevato che NON è un'auto da rally, restituisci messaggio di rifiuto
  if (risposta.trim().startsWith('RIFIUTO')) {
    console.log(`[${new Date().toISOString()}] Vision: foto rifiutata (non è auto da rally)`);
    return language === 'en'
      ? '⚠️ This doesn\'t look like a rally car photo! Send me a Rally di Roma Capitale car photo and I\'ll tell you everything about the driver, team and car. 🏎️'
      : '⚠️ Questa non sembra essere una foto di un\'auto da rally! Inviami una foto di un\'auto da rally del Rally di Roma Capitale e ti dirò tutto su pilota, team e vettura. 🏎️';
  }

  console.log(`[${new Date().toISOString()}] Vision: analisi foto completata`);
  return risposta;
}
