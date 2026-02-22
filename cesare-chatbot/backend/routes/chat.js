/**
 * chat.js — Endpoint POST /api/chat per il widget web
 */

import { Router } from 'express';
import { randomUUID } from 'crypto';
import { chat } from '../services/ai.js';

const router = Router();

// POST /api/chat — riceve messaggio dal widget web
router.post('/', async (req, res) => {
  try {
    const { message, session_id } = req.body;

    // Validazione input
    if (!message || typeof message !== 'string' || message.trim().length === 0) {
      return res.status(400).json({
        success: false,
        error: 'Il campo "message" è obbligatorio e non può essere vuoto.',
      });
    }

    if (message.length > 1000) {
      return res.status(400).json({
        success: false,
        error: 'Il messaggio è troppo lungo (max 1000 caratteri).',
      });
    }

    // Usa session_id fornito o genera uno nuovo
    const sessionId = session_id && typeof session_id === 'string'
      ? session_id
      : randomUUID();

    const risultato = await chat(sessionId, message.trim(), 'text');

    res.json({
      success: true,
      response: risultato.response,
      session_id: sessionId,
      language: risultato.language,
    });
  } catch (errore) {
    console.error(`[${new Date().toISOString()}] Errore /api/chat:`, errore.message);
    res.status(500).json({
      success: false,
      error: 'Si è verificato un errore. Riprova tra qualche istante.',
    });
  }
});

export default router;
