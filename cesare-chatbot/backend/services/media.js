/**
 * media.js — Link a contenuti media ufficiali del Rally di Roma Capitale
 *
 * Usa solo URL ufficiali verificati. Aggiorna quando escono nuovi contenuti 2026.
 */

// URL ufficiali media
const MEDIA_URLS = {
  sito: 'https://www.rallydiromacapitale.it',
  gallery: 'https://www.rallydiromacapitale.it/gallery',
  youtube_canale: 'https://www.youtube.com/@RallydiRomaCapitale',
  instagram: 'https://www.instagram.com/rallydiromacapitale',
  facebook: 'https://www.facebook.com/rallydiromacapitale',
  mappa_percorso: 'https://www.rallydiromacapitale.it/percorso',
};

/**
 * Risposta con link media, localizzata per lingua.
 *
 * @param {'it'|'en'} language - Lingua della risposta
 * @returns {string} - Testo con link ai contenuti media
 */
export function getMediaResponse(language = 'it') {
  if (language === 'en') {
    return (
      '📸 <b>Rally di Roma Capitale — Photos & Videos</b>\n\n' +
      `🖼 <a href="${MEDIA_URLS.gallery}">Official Photo Gallery</a>\n` +
      `▶️ <a href="${MEDIA_URLS.youtube_canale}">YouTube Channel</a>\n` +
      `📱 <a href="${MEDIA_URLS.instagram}">Instagram</a>\n` +
      `📘 <a href="${MEDIA_URLS.facebook}">Facebook</a>\n\n` +
      'Follow us on social media for live updates during the event!'
    );
  }

  // Italiano (default)
  return (
    '📸 <b>Rally di Roma Capitale — Foto e Video</b>\n\n' +
    `🖼 <a href="${MEDIA_URLS.gallery}">Galleria Foto Ufficiale</a>\n` +
    `▶️ <a href="${MEDIA_URLS.youtube_canale}">Canale YouTube</a>\n` +
    `📱 <a href="${MEDIA_URLS.instagram}">Instagram</a>\n` +
    `📘 <a href="${MEDIA_URLS.facebook}">Facebook</a>\n\n` +
    "Seguici sui social per aggiornamenti in diretta durante l'evento!"
  );
}

/**
 * Controlla se il messaggio contiene keyword relative a media/foto/video.
 *
 * @param {string} text - Testo del messaggio
 * @returns {boolean}
 */
export function isMediaRequest(text) {
  return /foto|video|gallery|galleria|immagin|picture|photo|watch|vedere|guarda/i.test(text);
}

export { MEDIA_URLS };
