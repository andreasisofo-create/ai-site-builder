/**
 * cors.js — Configurazione CORS per il server Express
 *
 * Permette richieste da:
 * - Origini nella allowlist (CORS_ORIGINS env)
 * - Richieste senza origin (curl, Postman, tool di sviluppo)
 */

import cors from 'cors';

// Origini sempre permesse (aggiuntive all'env)
const ORIGINI_FISSE = [
  'https://www.rallydiromacapitale.it',
  'https://rallydiromacapitale.it',
];

/**
 * Costruisce la lista di origini permesse combinando env e origini fisse.
 * @returns {string[]}
 */
function getOriginiPermesse() {
  const originiEnv = process.env.CORS_ORIGINS
    ? process.env.CORS_ORIGINS.split(',').map((o) => o.trim()).filter(Boolean)
    : [];

  // Unifica evitando duplicati
  return [...new Set([...ORIGINI_FISSE, ...originiEnv])];
}

export const corsMiddleware = cors({
  origin: (origin, callback) => {
    const permesse = getOriginiPermesse();

    // Permetti richieste senza origin (curl, Postman, app mobile)
    if (!origin) {
      return callback(null, true);
    }

    if (permesse.includes(origin)) {
      return callback(null, true);
    }

    // In sviluppo permetti localhost su qualsiasi porta
    if (process.env.NODE_ENV !== 'production' && /^http:\/\/localhost(:\d+)?$/.test(origin)) {
      return callback(null, true);
    }

    console.warn(`[${new Date().toISOString()}] CORS bloccato per origin: ${origin}`);
    callback(new Error(`Origin non permessa: ${origin}`));
  },
  methods: ['GET', 'POST', 'OPTIONS'],
  allowedHeaders: ['Content-Type', 'Authorization'],
  credentials: false,
});
