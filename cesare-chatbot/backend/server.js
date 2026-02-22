/**
 * server.js — Entry point del chatbot Rally di Roma Capitale
 *
 * Avvia il server Express con:
 * - Middleware: CORS, rate limiting, JSON parsing
 * - Routes: /health, /api/chat, /api/telegram
 * - Static: /widget (widget HTML embeddabile)
 * - Error handler globale
 * - Graceful shutdown su SIGTERM
 */

import 'dotenv/config';
import express from 'express';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';

import { corsMiddleware } from './middleware/cors.js';
import { chatRateLimit, telegramRateLimit } from './middleware/rateLimit.js';
import healthRouter from './routes/health.js';
import chatRouter from './routes/chat.js';
import telegramRouter from './routes/telegram.js';

const __dirname = dirname(fileURLToPath(import.meta.url));
const app = express();
const PORT = parseInt(process.env.PORT) || 3000;

// Fiducia al proxy (nginx) per IP reale nei rate limiter
app.set('trust proxy', 1);

// ─── Middleware globali ──────────────────────────────────────────────────────

app.use(corsMiddleware);
app.use(express.json({ limit: '10kb' }));

// Logging richieste
app.use((req, _res, next) => {
  console.log(`[${new Date().toISOString()}] ${req.method} ${req.path}`);
  next();
});

// ─── Serve widget statico ────────────────────────────────────────────────────

const widgetPath = join(__dirname, '../widget');
app.use('/widget', express.static(widgetPath));

// ─── Routes ─────────────────────────────────────────────────────────────────

app.use('/health', healthRouter);
app.use('/api/chat', chatRateLimit, chatRouter);
app.use('/api/telegram', telegramRateLimit, telegramRouter);

// ─── Error handler globale ───────────────────────────────────────────────────

// eslint-disable-next-line no-unused-vars
app.use((err, req, res, _next) => {
  console.error(`[${new Date().toISOString()}] Errore non gestito:`, err.message);
  res.status(500).json({
    success: false,
    error: 'Errore interno del server.',
    // Stack trace solo in development
    ...(process.env.NODE_ENV !== 'production' && { detail: err.message }),
  });
});

// ─── Avvio server ────────────────────────────────────────────────────────────

const server = app.listen(PORT, () => {
  console.log(`[${new Date().toISOString()}] Server avviato su porta ${PORT}`);
  console.log(`[${new Date().toISOString()}] Widget disponibile su http://localhost:${PORT}/widget/chat-widget.html`);
  console.log(`[${new Date().toISOString()}] Health check: http://localhost:${PORT}/health`);

  if (!process.env.OPENROUTER_API_KEY) {
    console.warn(`[${new Date().toISOString()}] ⚠️  OPENROUTER_API_KEY non configurata!`);
  }
  if (!process.env.TELEGRAM_BOT_TOKEN) {
    console.warn(`[${new Date().toISOString()}] ⚠️  TELEGRAM_BOT_TOKEN non configurato (Telegram disabilitato)`);
  }
});

// ─── Graceful shutdown ───────────────────────────────────────────────────────

process.on('SIGTERM', () => {
  console.log(`[${new Date().toISOString()}] SIGTERM ricevuto — chiusura server...`);
  server.close(() => {
    console.log(`[${new Date().toISOString()}] Server chiuso correttamente.`);
    process.exit(0);
  });
});
