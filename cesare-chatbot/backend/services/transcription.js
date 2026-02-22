/**
 * transcription.js — Trascrizione Vocale
 *
 * Strategia a cascata:
 *   1. Groq Whisper (whisper-large-v3-turbo) — se GROQ_API_KEY presente
 *   2. OpenRouter multimodal (google/gemini-2.0-flash-001) — transcribe via LLM con audio base64
 *   3. Errore esplicito
 */

const GROQ_API_KEY = process.env.GROQ_API_KEY;
const OPENROUTER_API_KEY = process.env.OPENROUTER_API_KEY;
const GROQ_URL = 'https://api.groq.com/openai/v1/audio/transcriptions';
const OPENROUTER_URL = 'https://openrouter.ai/api/v1/chat/completions';

/**
 * Trascrive un buffer audio in testo.
 * @param {Buffer} audioBuffer
 * @param {string} mimeType - es. 'audio/ogg'
 * @param {string} language - 'it' o 'en'
 * @returns {Promise<string>}
 */
export async function transcribeAudio(audioBuffer, mimeType = 'audio/ogg', language = 'it') {
  // ── Strategia 1: Groq Whisper (preferito — velocissimo) ────────────────────
  if (GROQ_API_KEY) {
    return transcribeGroq(audioBuffer, mimeType, language);
  }

  // ── Strategia 2: OpenRouter multimodal LLM con audio base64 ────────────────
  if (OPENROUTER_API_KEY) {
    return transcribeOpenRouterMultimodal(audioBuffer, mimeType, language);
  }

  throw new Error('Nessuna API key configurata per trascrizione vocale');
}

// ── Groq Whisper ──────────────────────────────────────────────────────────────
async function transcribeGroq(audioBuffer, mimeType, language) {
  const ext = getExt(mimeType);
  const formData = new FormData();
  formData.append('file', new Blob([audioBuffer], { type: mimeType }), `voice.${ext}`);
  formData.append('model', 'whisper-large-v3-turbo');
  formData.append('language', language === 'en' ? 'en' : 'it');
  formData.append('response_format', 'text');

  const resp = await fetch(GROQ_URL, {
    method: 'POST',
    headers: { 'Authorization': `Bearer ${GROQ_API_KEY}` },
    body: formData,
  });

  if (!resp.ok) {
    const err = await resp.text();
    throw new Error(`Groq Whisper error ${resp.status}: ${err}`);
  }

  const testo = await resp.text();
  console.log(`[${new Date().toISOString()}] Trascrizione Groq: "${testo.trim().substring(0, 80)}"`);
  return testo.trim();
}

// ── OpenRouter multimodal (Gemini 2.0 Flash — supporta audio base64) ──────────
async function transcribeOpenRouterMultimodal(audioBuffer, mimeType, language) {
  const base64Audio = audioBuffer.toString('base64');
  const langHint = language === 'en' ? 'English' : 'Italian';

  const prompt = `You are a transcription service. Transcribe EXACTLY what is said in this audio.
Output ONLY the transcribed text, nothing else. No explanations, no quotes, just the words spoken.
The speaker is likely speaking in ${langHint}. If you cannot understand the audio or it's not speech, reply with: [incomprensibile]`;

  const resp = await fetch(OPENROUTER_URL, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${OPENROUTER_API_KEY}`,
      'Content-Type': 'application/json',
      'HTTP-Referer': 'https://cesare.e-quipe.app',
      'X-Title': 'Cesare - Rally di Roma Capitale',
    },
    body: JSON.stringify({
      model: 'google/gemini-2.0-flash-001',
      max_tokens: 300,
      messages: [{
        role: 'user',
        content: [
          {
            type: 'input_audio',
            input_audio: {
              data: base64Audio,
              format: mimeType.includes('ogg') ? 'ogg' : mimeType.includes('mp4') ? 'mp4' : 'mp3',
            },
          },
          { type: 'text', text: prompt },
        ],
      }],
    }),
  });

  if (!resp.ok) {
    const err = await resp.text();
    throw new Error(`OpenRouter multimodal error ${resp.status}: ${err.substring(0, 200)}`);
  }

  const data = await resp.json();
  const testo = data.choices?.[0]?.message?.content?.trim();
  if (!testo) throw new Error('Risposta vuota da OpenRouter multimodal');

  console.log(`[${new Date().toISOString()}] Trascrizione OpenRouter Gemini: "${testo.substring(0, 80)}"`);
  return testo;
}

// ── Utility ───────────────────────────────────────────────────────────────────
function getExt(mimeType) {
  if (mimeType.includes('ogg')) return 'ogg';
  if (mimeType.includes('mpeg') || mimeType.includes('mp3')) return 'mp3';
  if (mimeType.includes('wav')) return 'wav';
  if (mimeType.includes('mp4') || mimeType.includes('m4a')) return 'm4a';
  return 'ogg';
}
