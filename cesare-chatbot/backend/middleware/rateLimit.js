/**
 * rateLimit.js — Configurazione rate limiter per gli endpoint API
 */

import rateLimit from 'express-rate-limit';

// Rate limiter per il widget web — max 30 req/minuto per IP
export const chatRateLimit = rateLimit({
  windowMs: 60 * 1000,
  max: parseInt(process.env.RATE_LIMIT_CHAT_PER_MINUTE) || 30,
  standardHeaders: true,
  legacyHeaders: false,
  message: {
    success: false,
    error: 'Troppe richieste. Attendi un momento prima di continuare.',
  },
  skip: (req) => {
    // Non applicare il limite alle richieste locali in sviluppo
    return process.env.NODE_ENV === 'development' && req.ip === '::1';
  },
});

// Rate limiter per Telegram — più alto perché tutti i messaggi
// arrivano dai server Telegram (stesso IP) — max 200 req/minuto
export const telegramRateLimit = rateLimit({
  windowMs: 60 * 1000,
  max: parseInt(process.env.RATE_LIMIT_TELEGRAM_PER_MINUTE) || 200,
  standardHeaders: true,
  legacyHeaders: false,
  message: {
    success: false,
    error: 'Rate limit superato.',
  },
});
