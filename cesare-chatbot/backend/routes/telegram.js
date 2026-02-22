/**
 * telegram.js — Webhook per il bot Telegram del Rally di Roma Capitale
 *
 * Flusso:
 * 1. Verifica il secret token nell'header
 * 2. Risponde 200 immediatamente a Telegram (evita timeout/ritrasmissioni)
 * 3. Elabora l'update in modo asincrono
 * 4. Invia la risposta al chat_id tramite Bot API
 */

import { Router } from 'express';
import { chat, detectLanguage, analyzeRallyCarPhoto } from '../services/ai.js';
import { getMediaResponse, isMediaRequest } from '../services/media.js';
import { PROGRAMMA, BIGLIETTI, EVENT_INFO, LOCATION, STORIA } from '../services/knowledge.js';

const router = Router();

const BOT_TOKEN = process.env.TELEGRAM_BOT_TOKEN;
const WEBHOOK_SECRET = process.env.TELEGRAM_WEBHOOK_SECRET;

// ─── Funzioni di invio Telegram ───────────────────────────────────────────────

/**
 * Invia un messaggio di testo HTML.
 */
async function sendMessage(chatId, text, extra = {}) {
  if (!BOT_TOKEN) {
    console.warn(`[${new Date().toISOString()}] TELEGRAM_BOT_TOKEN non configurato`);
    return;
  }
  try {
    const url = `https://api.telegram.org/bot${BOT_TOKEN}/sendMessage`;
    const resp = await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        chat_id: chatId,
        text,
        parse_mode: 'HTML',
        disable_web_page_preview: false,
        ...extra,
      }),
    });
    if (!resp.ok) {
      const err = await resp.text();
      console.error(`[${new Date().toISOString()}] Telegram sendMessage error ${resp.status}: ${err}`);
    }
  } catch (e) {
    console.error(`[${new Date().toISOString()}] Errore sendMessage:`, e.message);
  }
}

/**
 * Invia una posizione GPS — mostra la mappa direttamente in chat.
 */
async function sendLocation(chatId, lat, lon) {
  if (!BOT_TOKEN) return;
  try {
    const url = `https://api.telegram.org/bot${BOT_TOKEN}/sendLocation`;
    await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ chat_id: chatId, latitude: lat, longitude: lon }),
    });
  } catch (e) {
    console.error(`[${new Date().toISOString()}] Errore sendLocation:`, e.message);
  }
}

/**
 * Scarica un file da Telegram e restituisce il Buffer.
 * @param {string} fileId
 * @returns {Promise<{buffer: Buffer, mimeType: string}>}
 */
async function downloadTelegramFile(fileId) {
  // Ottieni il percorso del file
  const getFileUrl = `https://api.telegram.org/bot${BOT_TOKEN}/getFile?file_id=${fileId}`;
  const metaResp = await fetch(getFileUrl);
  const meta = await metaResp.json();

  if (!meta.ok) throw new Error(`getFile failed: ${JSON.stringify(meta)}`);

  const filePath = meta.result.file_path;
  const downloadUrl = `https://api.telegram.org/file/bot${BOT_TOKEN}/${filePath}`;

  const fileResp = await fetch(downloadUrl);
  if (!fileResp.ok) throw new Error(`Download file failed: ${fileResp.status}`);

  const arrayBuffer = await fileResp.arrayBuffer();
  const buffer = Buffer.from(arrayBuffer);

  // Determina MIME type dall'estensione
  const ext = filePath.split('.').pop().toLowerCase();
  const mimeMap = { jpg: 'image/jpeg', jpeg: 'image/jpeg', png: 'image/png', webp: 'image/webp' };
  const mimeType = mimeMap[ext] || 'image/jpeg';

  return { buffer, mimeType };
}

/**
 * Invia un'azione "digitando..." o "caricando foto..." per feedback visivo.
 */
async function sendChatAction(chatId, action = 'typing') {
  if (!BOT_TOKEN) return;
  try {
    await fetch(`https://api.telegram.org/bot${BOT_TOKEN}/sendChatAction`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ chat_id: chatId, action }),
    });
  } catch { /* ignora */ }
}

// ─── Keyword per richieste di posizione ──────────────────────────────────────

const KEYWORD_POSIZIONE = /dove si svolge|dove è|dove siete|dove si tiene|come arrivo|come si arriva|indicazioni|posizione|mappa|maps|location|dove trovo|dove sta|how to get|where is|directions|navigate|navigazione/i;

const KEYWORD_LUOGHI = {
  colosseo:        /colosseo|ps serale|prova serale|venerdì sera|friday night/i,
  bocca_della_verita: /bocca della verità|bocca della verita|parade|partenza parata/i,
  fiuggi:          /fiuggi|podio|village|parco assistenza/i,
  colle_oppio:     /colle oppio|roma.*spettatori|spettatori.*roma/i,
  jenne:           /jenne|power stage/i,
  vico_nel_lazio:  /vico nel lazio|vico lazio/i,
};

/**
 * Determina quale luogo l'utente sta cercando e invia GPS + link.
 */
async function gestisciRichiestaPosizione(chatId, testo, language) {
  const luoghi = LOCATION.luoghi_gps;

  // Cerca un luogo specifico nel testo
  for (const [chiave, regex] of Object.entries(KEYWORD_LUOGHI)) {
    if (regex.test(testo) && luoghi[chiave]) {
      const luogo = luoghi[chiave];
      await sendLocation(chatId, luogo.lat, luogo.lon);
      await sendMessage(chatId,
        `📍 <b>${luogo.nome}</b>\n\n` +
        `${luogo.descrizione}\n\n` +
        `🗺 <a href="${luogo.maps}">Apri in Google Maps</a>`
      );
      return true;
    }
  }

  // Nessun luogo specifico → menu con tutti i luoghi chiave
  const it = language !== 'en';
  await sendMessage(chatId,
    it
      ? `📍 <b>Dove vuoi andare?</b>\n\nEcco i luoghi principali del Rally di Roma Capitale 2026:\n\n` +
        `🏛 <b>Bocca della Verità</b> — Partenza Parade (ven. 18:00)\n` +
        `<a href="${luoghi.bocca_della_verita.maps}">📍 Apri mappa</a>\n\n` +
        `🏟 <b>Area Colosseo</b> — PS serale (ven. 20:05)\n` +
        `<a href="${luoghi.colosseo.maps}">📍 Apri mappa</a>\n\n` +
        `🌿 <b>Colle Oppio</b> — Area spettatori Roma\n` +
        `<a href="${luoghi.colle_oppio.maps}">📍 Apri mappa</a>\n\n` +
        `🏆 <b>Fiuggi</b> — Village + Cerimonia Podio (dom. 18:30)\n` +
        `<a href="${luoghi.fiuggi.maps}">📍 Apri mappa</a>\n\n` +
        `⚡ <b>Jenne</b> — Power Stage (dom. 17:05)\n` +
        `<a href="${luoghi.jenne.maps}">📍 Apri mappa</a>\n\n` +
        `Scrivi il nome del luogo per ricevere la posizione GPS direttamente qui!`
      : `📍 <b>Where do you want to go?</b>\n\nMain locations for Rally di Roma Capitale 2026:\n\n` +
        `🏛 <b>Bocca della Verità</b> — Parade Start (Fri 18:00)\n` +
        `<a href="${luoghi.bocca_della_verita.maps}">📍 Open map</a>\n\n` +
        `🏟 <b>Colosseum area</b> — Evening SS (Fri 20:05)\n` +
        `<a href="${luoghi.colosseo.maps}">📍 Open map</a>\n\n` +
        `🏆 <b>Fiuggi</b> — Village + Podium Ceremony (Sun 18:30)\n` +
        `<a href="${luoghi.fiuggi.maps}">📍 Open map</a>`
  );
  return true;
}

// ─── Handler comandi slash ────────────────────────────────────────────────────

function getComandoRisposta(comando, from) {
  const nome = from?.first_name || 'Pilota';

  switch (comando) {
    case 'start':
      return (
        `🏎️ <b>Salve, ${nome}! Sono Cesare.</b>\n\n` +
        `L'assistente ufficiale del <b>Rally di Roma Capitale 2026</b>, ` +
        `valido per FIA ERC e CIAR Sparco.\n\n` +
        `📅 <b>4-6 luglio 2026</b> — segna la data!\n` +
        `✅ Ingresso <b>gratuito</b> per tutti\n\n` +
        `Cosa posso fare per te?\n` +
        `/programma — Programma e prove speciali\n` +
        `/biglietti — Accesso gratuito, info VIP\n` +
        `/dove — Posizioni GPS dei luoghi chiave\n` +
        `/storia — Albo d'oro e curiosità\n` +
        `/info — Informazioni generali\n` +
        `/help — Mostra questo menu\n\n` +
        `Oppure scrivimi liberamente! 💬`
      );

    case 'help':
      return (
        `📋 <b>Comandi di Cesare:</b>\n\n` +
        `/start — Messaggio di benvenuto\n` +
        `/programma — Programma 4-6 luglio 2026\n` +
        `/biglietti — Ingresso (è gratuito!)\n` +
        `/dove — Mappa e posizioni GPS\n` +
        `/storia — Albo d'oro dal 2013\n` +
        `/info — Info generali evento\n` +
        `/help — Questo messaggio\n\n` +
        `💬 Puoi anche scrivermi liberamente!\n` +
        `📍 Chiedimi "dove si trova il Colosseo" per ricevere la posizione GPS direttamente qui.`
      );

    case 'programma':
      return (
        `🗓 <b>Rally di Roma Capitale 2026 — Programma</b>\n\n` +
        `📅 <b>4-6 luglio 2026</b>\n\n` +
        `<b>🏙️ Venerdì 4 luglio — Roma</b>\n` +
        `• 18:00 — Roma Parade, Bocca della Verità\n` +
        `• 19:00 — VIP Lounge aperta, Colle Oppio\n` +
        `• 20:05 — PS Colosseo (prova spettacolo serale)\n\n` +
        `<b>🏔️ Sabato 5 luglio — Frusinate</b>\n` +
        `• 08:30 — PS Vico nel Lazio – Collepardo 1\n` +
        `• 09:40 — PS Torre di Cicerone 1\n` +
        `• 11:10 — PS Santopadre 1\n` +
        `• 14:45 — Ripetizione prove (x2)\n\n` +
        `<b>🏁 Domenica 6 luglio — Power Stage + Podio</b>\n` +
        `• 08:25 — PS Guarcino – Altipiani 1\n` +
        `• 09:20 — PS Canterano – Subiaco 1\n` +
        `• 11:05 — PS Jenne – Monastero 1\n` +
        `• 13:45 — Ripetizione prove\n` +
        `• 17:05 — ⚡ POWER STAGE Jenne – Monastero 2\n` +
        `• 18:30 — 🏆 Podio a Fiuggi, Corso Nuova Italia\n\n` +
        `📏 Totale km PS: 140-160 km su asfalto\n` +
        `📰 <a href="${EVENT_INFO.sito_ufficiale}">Orari ufficiali sul sito</a>`
      );

    case 'biglietti':
      return (
        `🎫 <b>Accesso al Rally di Roma Capitale 2026</b>\n\n` +
        `✅ <b>INGRESSO GRATUITO!</b>\n\n` +
        `Nessun biglietto necessario per le zone pubbliche:\n` +
        `• Roma — Colle Oppio e PS Colosseo\n` +
        `• Tutte le prove speciali nella provincia\n` +
        `• Fiuggi — Village, Paddock e Podio\n\n` +
        `🌟 <b>Pacchetti VIP/Hospitality</b> disponibili:\n` +
        `VIP Lounge, zone riservate, catering, paddock walk\n` +
        `📧 ${EVENT_INFO.email_contatto}\n` +
        `📞 ${EVENT_INFO.telefono[0]}\n\n` +
        `💡 Arriva almeno 2 ore prima per i posti migliori!`
      );

    case 'dove':
      // Gestito separatamente con invio GPS
      return null;

    case 'storia':
      return (
        `🏆 <b>Albo d'Oro Rally di Roma Capitale</b>\n\n` +
        `🥇 2025 — Giandomenico Basso (Škoda Fabia RS Rally2)\n` +
        `🥇 2024 — Andrea Crugnola (Citroën C3 Rally2)\n` +
        `🥇 2023 — Andrea Crugnola (Citroën C3 Rally2)\n` +
        `🥇 2022 — Damiano De Tommaso (Škoda Fabia Rally2 evo)\n` +
        `🥇 2021 — Giandomenico Basso (Škoda Fabia Rally2 evo)\n` +
        `🥇 2020 — Alexey Lukyanuk (Citroën C3 R5)\n` +
        `🥇 2019 — Giandomenico Basso (Škoda Fabia R5)\n` +
        `🥇 2018 — Alexey Lukyanuk (Ford Fiesta R5)\n` +
        `🥇 2017 — Bryan Bouffier (Ford Fiesta R5) — 1ª edizione ERC\n` +
        `🥇 2016 — Umberto Scandola (Škoda Fabia R5)\n` +
        `🥇 2015 — Umberto Scandola (Škoda Fabia R5)\n` +
        `🥇 2013 — "Dedo" Maurizio Davide (Ford Focus RS WRC)\n\n` +
        `⭐ <b>Record:</b> Basso è il più vincente con 3 vittorie!\n` +
        `📺 L'edizione 2025 ha raggiunto 9 milioni di spettatori`
      );

    case 'info':
      return (
        `🏁 <b>Rally di Roma Capitale 2026</b>\n\n` +
        `${EVENT_INFO.descrizione}\n\n` +
        `<b>Novità 2026:</b>\n` +
        EVENT_INFO.novita_2026.map((n) => `• ${n}`).join('\n') +
        `\n\n🌐 <a href="${EVENT_INFO.sito_ufficiale}">Sito ufficiale</a>\n` +
        `📧 ${EVENT_INFO.email_contatto}\n` +
        `📱 <a href="${EVENT_INFO.social.instagram}">Instagram</a> | ` +
        `<a href="${EVENT_INFO.social.facebook}">Facebook</a> | ` +
        `<a href="${EVENT_INFO.social.youtube}">YouTube</a>`
      );

    default:
      return null;
  }
}

// ─── Route POST /api/telegram ─────────────────────────────────────────────────

router.post('/', async (req, res) => {
  // 1. Verifica secret
  const secretRicevuto = req.headers['x-telegram-bot-api-secret-token'];
  if (!WEBHOOK_SECRET || secretRicevuto !== WEBHOOK_SECRET) {
    console.warn(`[${new Date().toISOString()}] Telegram webhook: secret non valido`);
    return res.status(403).json({ error: 'Unauthorized' });
  }

  // 2. Risposta immediata 200 a Telegram
  res.status(200).json({ ok: true });

  // 3. Elaborazione asincrona
  const update = req.body;

  // Gestione foto — riconoscimento auto da rally con Vision
  if (update?.message?.photo) {
    const { message } = update;
    const chatId = message.chat.id;
    const language = detectLanguage(message.caption || '');

    try {
      await sendChatAction(chatId, 'upload_photo');

      // Prendi la foto in massima risoluzione (ultimo elemento dell'array)
      const foto = message.photo[message.photo.length - 1];

      const intro = language === 'en'
        ? '🔍 Analyzing the rally car... one moment!'
        : '🔍 Analizzo l\'auto da rally... un attimo!';
      await sendMessage(chatId, intro);

      const { buffer, mimeType } = await downloadTelegramFile(foto.file_id);
      const analisi = await analyzeRallyCarPhoto(buffer, mimeType, language);

      await sendMessage(chatId, analisi);

      // Aggiunge invito a continuare la conversazione
      const footer = language === 'en'
        ? '\n\n💬 Ask me anything else about the rally!'
        : '\n\n💬 Chiedimi altro sul rally!';
      // Il footer è già nel testo — evita doppio messaggio
    } catch (errore) {
      console.error(`[${new Date().toISOString()}] Errore analisi foto:`, errore.message);
      await sendMessage(
        chatId,
        language === 'en'
          ? '⚠️ I couldn\'t analyze the photo. Try with a clearer image of the car!'
          : '⚠️ Non sono riuscito ad analizzare la foto. Prova con un\'immagine più nitida dell\'auto!'
      );
    }
    return;
  }

  if (!update?.message?.text) return;

  const { message } = update;
  const chatId = message.chat.id;
  const testo = message.text.trim();
  const from = message.from;

  console.log(`[${new Date().toISOString()}] Telegram msg chat=${chatId} text="${testo.substring(0, 60)}"`);

  try {
    // Rilevamento lingua
    const language = detectLanguage(testo);

    // Comandi slash
    if (testo.startsWith('/')) {
      const partiComando = testo.split(/[\s@]/);
      const comando = partiComando[0].substring(1).toLowerCase();

      // Comando /dove → invia GPS menu
      if (comando === 'dove') {
        await gestisciRichiestaPosizione(chatId, '', language);
        return;
      }

      const rispostaComando = getComandoRisposta(comando, from);
      if (rispostaComando) {
        await sendMessage(chatId, rispostaComando);
        return;
      }
    }

    // Richiesta di posizione / mappa
    if (KEYWORD_POSIZIONE.test(testo)) {
      const gestito = await gestisciRichiestaPosizione(chatId, testo, language);
      if (gestito) return;
    }

    // Richiesta media (foto/video)
    if (isMediaRequest(testo)) {
      await sendMessage(chatId, getMediaResponse(language));
      return;
    }

    // Fallback AI con sessione per chat_id
    const sessionId = `telegram_${chatId}`;
    const risultato = await chat(sessionId, testo, 'html');
    await sendMessage(chatId, risultato.response);

  } catch (errore) {
    console.error(`[${new Date().toISOString()}] Errore elaborazione update:`, errore.message);
    await sendMessage(
      chatId,
      '⚠️ Si è verificato un errore. Riprova o visita <a href="https://www.rallydiromacapitale.it">rallydiromacapitale.it</a>'
    );
  }
});

export default router;
