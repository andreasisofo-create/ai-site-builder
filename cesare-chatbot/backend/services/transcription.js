/**
 * transcription.js — Agente Trascrizione Vocale
 *
 * Usa Groq Whisper (whisper-large-v3-turbo) per trascrivere
 * note vocali OGG/Opus inviate su Telegram.
 * Groq è gratuito fino a 25.000 minuti/mese.
 */

const GROQ_API_KEY = process.env.GROQ_API_KEY;
const GROQ_TRANSCRIPTION_URL = 'https://api.groq.com/openai/v1/audio/transcriptions';

/**
 * Trascrive un buffer audio (OGG/Opus da Telegram) in testo.
 * @param {Buffer} audioBuffer - Buffer del file audio
 * @param {string} mimeType - es. 'audio/ogg' o 'audio/mpeg'
 * @param {string} language - 'it' o 'en' (hint per Whisper)
 * @returns {Promise<string>} - Testo trascritto
 */
export async function transcribeAudio(audioBuffer, mimeType = 'audio/ogg', language = 'it') {
  if (!GROQ_API_KEY) {
    throw new Error('GROQ_API_KEY non configurata — trascrizine vocale non disponibile');
  }

  // Crea FormData con il file audio
  const formData = new FormData();

  // Determina estensione dal mime type
  const ext = mimeType.includes('ogg') ? 'ogg'
    : mimeType.includes('mpeg') || mimeType.includes('mp3') ? 'mp3'
    : mimeType.includes('wav') ? 'wav'
    : mimeType.includes('mp4') || mimeType.includes('m4a') ? 'm4a'
    : 'ogg';

  // Crea Blob dal buffer
  const blob = new Blob([audioBuffer], { type: mimeType });
  formData.append('file', blob, `voice.${ext}`);
  formData.append('model', 'whisper-large-v3-turbo');
  formData.append('language', language === 'en' ? 'en' : 'it');
  formData.append('response_format', 'text');

  const resp = await fetch(GROQ_TRANSCRIPTION_URL, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${GROQ_API_KEY}`,
    },
    body: formData,
  });

  if (!resp.ok) {
    const err = await resp.text();
    throw new Error(`Groq Whisper error ${resp.status}: ${err}`);
  }

  const testo = await resp.text();
  console.log(`[${new Date().toISOString()}] Trascrizione vocale completata: "${testo.trim().substring(0, 80)}..."`);
  return testo.trim();
}
