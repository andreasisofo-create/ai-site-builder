# ─── Stage 1: installazione dipendenze ──────────────────────────────────────
FROM node:18-alpine AS deps

WORKDIR /app

# Copia solo i file necessari per npm install (cache layer ottimale)
COPY package.json ./

RUN npm install --omit=dev && npm cache clean --force

# ─── Stage 2: immagine di produzione ────────────────────────────────────────
FROM node:18-alpine AS production

# Crea utente non-root per sicurezza
RUN addgroup -S rally && adduser -S rally -G rally

WORKDIR /app

# Copia dipendenze dal stage precedente
COPY --from=deps /app/node_modules ./node_modules

# Copia il codice sorgente
COPY package.json ./
COPY backend/ ./backend/
COPY widget/   ./widget/

# Imposta permessi
RUN chown -R rally:rally /app

# Utente non-root
USER rally

# Porta di ascolto
EXPOSE 3000

# Health check tramite wget (incluso in alpine)
HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
  CMD wget -qO- http://localhost:3000/health || exit 1

# Avvio server
CMD ["node", "backend/server.js"]
