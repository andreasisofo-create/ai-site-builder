/**
 * health.js — Endpoint health check
 */

import { Router } from 'express';
import { getSessionCount } from '../services/ai.js';
import { readFileSync } from 'fs';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';

const router = Router();
const __dirname = dirname(fileURLToPath(import.meta.url));

// Legge la versione dal package.json
let versione = '1.0.0';
try {
  const pkg = JSON.parse(
    readFileSync(join(__dirname, '../../package.json'), 'utf-8')
  );
  versione = pkg.version;
} catch {
  // Usa default se non riesce a leggere
}

const avvio = Date.now();

// GET /health — restituisce stato del servizio
router.get('/', (_req, res) => {
  res.json({
    status: 'ok',
    uptime: Math.floor((Date.now() - avvio) / 1000),
    version: versione,
    sessions_attive: getSessionCount(),
    timestamp: new Date().toISOString(),
  });
});

export default router;
