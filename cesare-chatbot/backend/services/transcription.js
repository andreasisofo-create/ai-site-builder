/**
 * transcription.js — Agente Trascrizione Vocale
 *
 * Usa Whisper per trascrivere note vocali OGG/Opus inviate su Telegram.
 * Approccio a cascata:
 *   1. Groq Whisper (whisper-large-v3-turbo) — se GROQ_API_KEY è presente
 *   2. OpenRouter Whisper (openai/whisper-large-v3) — se OPENROUTER_API_KEY è presente
 *   3. Errore esplicito — se nessuna chiave è configurata
 */

const GROQ_API_KEY = process.env.GROQ_API_KEY;
const OPENROUTER_API_KEY = process.env.OPENROUTER_API_KEY;
const GROQ_URL = 'https://api.groq.com/openai/v1/audio/transcriptions';
const OPENROUTER_AUDIO_URL = 'https://openrouter.ai/api/v1/audio/transcriptions';

/**
 * Trascrive un buffer audio (OGG/Opus da Telegram) in testo.
 * @param {Buffer} audioBuffer - Buffer del file audio
 * @param {string} mimeType - es. 'audio/ogg' o 'audio/mpeg'
 * @param {string} language - 'it' o 'en' (hint per Whisper)
 * @returns {Promise<string>} - Testo trascritto
 */
export async function transcribeAudio(audioBuffer, mimeType = 'audio/ogg', language = 'it') {
  // Determina quale servizio usare
  const apiKey = GROQ_API_KEY || OPENROUTER_API_KEY;
  const apiUrl = GROQ_API_KEY ? GROQ_URL : OPENROUTER_AUDIO_URL;
  const model = GROQ_API_KEY ? 'whisper-large-v3-turbo' : 'openai/whisper-large-v3';

  if (!apiKey) {
    throw new Error('Nessuna API key configurata per trascrizione vocale (GROQ_API_KEY o OPENROUTER_API_KEY)');
  }

  // Determina estensione dal mime type
  const ext = mimeType.includes('ogg') ? 'ogg'
    : mimeType.includes('mpeg') || mimeType.includes('mp3') ? 'mp3'
    : mimeType.includes('wav') ? 'wav'
    : mimeType.includes('mp4') || mimeType.includes('m4a') ? 'm4a'
    : 'ogg';

  // Crea FormData con il file audio
  const formData = new FormData();
  const blob = new Blob([audioBuffer], { type: mimeType });
  formData.append('file', blob, `voice.${ext}`);
  formData.append('model', model);
  formData.append('language', language === 'en' ? 'en' : 'it');
  formData.append('response_format', 'text');

  const resp = await fetch(apiUrl, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${apiKey}`,
      ...(OPENROUTER_API_KEY && !GROQ_API_KEY ? {
        'HTTP-Referer': 'https://cesare.e-quipe.app',
        'X-Title': 'Cesare - Rally di Roma Capitale',
      } : {}),
    },
    body: formData,
  });

  if (!resp.ok) {
    const err = await resp.text();
    throw new Error(`Whisper error ${resp.status}: ${err}`);
  }

  const testo = await resp.text();
  const servizio = GROQ_API_KEY ? 'Groq' : 'OpenRouter';
  console.log(`[${new Date().toISOString()}] Trascrizione ${servizio} completata: "${testo.trim().substring(0, 80)}"`);
  return testo.trim();
}
