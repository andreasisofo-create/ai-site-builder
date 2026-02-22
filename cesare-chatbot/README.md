# Rally di Roma Capitale — Chatbot 2026

Chatbot ufficiale per il Rally di Roma Capitale 2026 (FIA ERC).
Supporta: **widget web embeddabile** + **bot Telegram** (Fase 1) + **WhatsApp via n8n** (Fase 2).

---

## Setup locale

### 1. Prerequisiti
- Node.js ≥ 18
- Chiave API Anthropic
- (Opzionale) Token bot Telegram

### 2. Installazione

```bash
git clone <repo>
cd rally-roma-chatbot
npm install
```

### 3. Configurazione

```bash
cp .env.example .env
# Modifica .env con i tuoi valori reali:
# ANTHROPIC_API_KEY=sk-ant-...
# TELEGRAM_BOT_TOKEN=7123...  (opzionale per il widget)
# TELEGRAM_WEBHOOK_SECRET=... (opzionale per il widget)
```

### 4. Avvio in sviluppo

```bash
npm run dev
```

### 5. Verifica

```bash
# Health check
curl http://localhost:3000/health

# Test chat API
curl -X POST http://localhost:3000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"Quando si svolge il rally?"}'

# Widget nel browser
open http://localhost:3000/widget/chat-widget.html
```

---

## Setup Telegram Bot (Fase 1)

Segui la guida completa: `.claude/commands/setup-telegram.md`

**In breve:**
1. Crea bot con BotFather → ottieni token
2. Aggiungi `TELEGRAM_BOT_TOKEN` e `TELEGRAM_WEBHOOK_SECRET` nel `.env`
3. Deploya il backend sul VPS
4. Registra il webhook:

```bash
curl -X POST "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/setWebhook" \
  -H "Content-Type: application/json" \
  -d '{"url":"https://srv1352958.hstgr.cloud/api/telegram","secret_token":"<SECRET>"}'
```

---

## Deploy VPS (Docker)

```bash
# Sul VPS — prima volta
git clone <repo>
cd rally-roma-chatbot
cp .env.example .env
# Compila .env con valori reali

# Avvio
docker-compose -f docker/docker-compose.yml up -d --build

# Log
docker-compose -f docker/docker-compose.yml logs -f chatbot

# Aggiornamento
git pull
docker-compose -f docker/docker-compose.yml up -d --build
```

---

## Nginx — Reverse Proxy

Aggiungi al virtual host nginx del VPS:

```nginx
server {
    listen 443 ssl;
    server_name srv1352958.hstgr.cloud;

    # SSL (Let's Encrypt)
    ssl_certificate     /etc/letsencrypt/live/srv1352958.hstgr.cloud/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/srv1352958.hstgr.cloud/privkey.pem;

    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

---

## Embedding Widget su WordPress

Incolla questo snippet nel footer del tema WordPress (o tramite plugin "Header and Footer Scripts"):

```html
<script
  src="https://srv1352958.hstgr.cloud/widget/embed.js"
  data-url="https://srv1352958.hstgr.cloud">
</script>
```

---

## Struttura progetto

```
rally-roma-chatbot/
├── backend/
│   ├── server.js               ← Entry point
│   ├── routes/
│   │   ├── health.js           ← GET /health
│   │   ├── chat.js             ← POST /api/chat (widget)
│   │   └── telegram.js         ← POST /api/telegram (bot)
│   ├── services/
│   │   ├── ai.js               ← Anthropic + sessioni
│   │   ├── knowledge.js        ← Knowledge base evento
│   │   └── media.js            ← Link media ufficiali
│   └── middleware/
│       ├── rateLimit.js
│       └── cors.js
├── widget/
│   ├── chat-widget.html        ← Widget standalone
│   └── embed.js                ← Script embedding WordPress
├── docker/
│   ├── Dockerfile
│   └── docker-compose.yml
├── .env.example
├── .gitignore
└── README.md
```

---

## Roadmap — Migrazione Telegram → WhatsApp (Fase 2)

1. **Crea** `backend/routes/whatsapp.js` — gestisce webhook Meta/n8n
2. **Monta** in `server.js` su `/api/whatsapp`
3. **Crea** `n8n/whatsapp-flow.json` — workflow importabile su n8n
4. **Configura** n8n su `https://n8n.srv1352958.hstgr.cloud`
5. Telegram rimane attivo in parallelo

---

## Test rapido completo

```bash
# Health
curl http://localhost:3000/health

# Chat con sessione
SESSION=$(curl -s -X POST http://localhost:3000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"Ciao!"}' | python3 -c "import sys,json; print(json.load(sys.stdin)['session_id'])")

echo "Session: $SESSION"

curl -X POST http://localhost:3000/api/chat \
  -H "Content-Type: application/json" \
  -d "{\"message\":\"E i biglietti?\",\"session_id\":\"$SESSION\"}"

# Telegram (necessita TELEGRAM_WEBHOOK_SECRET nel .env)
SECRET=$(grep TELEGRAM_WEBHOOK_SECRET .env | cut -d= -f2)
curl -X POST http://localhost:3000/api/telegram \
  -H "Content-Type: application/json" \
  -H "X-Telegram-Bot-Api-Secret-Token: $SECRET" \
  -d '{"update_id":1,"message":{"message_id":1,"from":{"id":123,"first_name":"Test"},"chat":{"id":123,"type":"private"},"text":"/start","date":1}}'
```
