# Rally di Roma Capitale — Chatbot Project

## Contesto
Stiamo costruendo un chatbot per il Rally di Roma Capitale 2026, un evento del
FIA European Rally Championship. Il chatbot funziona sia come widget web
embeddabile sul sito WordPress dell'evento, sia su Telegram (canale primario di
testing), sia come backend per WhatsApp via n8n (Fase 2).

## Strategia Canali
- **Fase 1 (attuale)**: Telegram + Widget web — per testing e deploy iniziale
- **Fase 2**: Aggiunta WhatsApp Business via n8n in parallelo a Telegram
- Telegram rimane sempre attivo; WhatsApp si affianca senza rimuoverlo

## Stack Tecnico
- Backend: Node.js + Express (ESM modules)
- AI: Anthropic Claude API (claude-sonnet-4-6)
- Widget: HTML/CSS/JS vanilla (singolo file, leggero)
- Telegram: Bot API nativa (no librerie esterne)
- Automazione: n8n per WhatsApp Business API (Fase 2)
- n8n URL: https://n8n.srv1352958.hstgr.cloud
- Deploy: Docker su VPS Hetzner (IP: 72.62.42.113, host: srv1352958.hstgr.cloud)

## Regole di Codice
- Usa ESM modules (import/export), MAI require()
- Commenti in italiano
- Error handling robusto con try/catch su ogni endpoint
- Logging con timestamp ISO
- Variabili d'ambiente via dotenv
- CORS configurabile
- Rate limiting su tutti gli endpoint pubblici
- Telegram: usa sempre `parse_mode: 'HTML'` (mai MarkdownV2 — problemi escape)

## Struttura Progetto
```
rally-roma-chatbot/
├── backend/
│   ├── server.js
│   ├── routes/
│   │   ├── chat.js
│   │   ├── telegram.js       ← Fase 1 (attivo)
│   │   ├── whatsapp.js       ← Fase 2 (da aggiungere)
│   │   └── health.js
│   ├── services/
│   │   ├── ai.js
│   │   ├── knowledge.js
│   │   └── media.js
│   └── middleware/
│       ├── rateLimit.js
│       └── cors.js
├── widget/
│   ├── chat-widget.html
│   └── embed.js
├── n8n/
│   ├── whatsapp-flow.json    ← Fase 2
│   └── setup-guide.md       ← Fase 2
├── docker/
│   ├── Dockerfile
│   └── docker-compose.yml
├── .env.example
├── .gitignore
├── CLAUDE.md
└── README.md
```

## Stile Widget
- Colori: rosso #E31937, nero #1A1A1A, bianco #FFFFFF
- Font: system fonts (no external dependencies)
- Posizione: flottante basso-destra
- Mobile-first responsive
- Ispirato a Intercom/Drift ma in un singolo file senza dipendenze

## Knowledge Base
La knowledge base è in `backend/services/knowledge.js`.
NON inventare mai informazioni. Se non conosci la risposta, indirizza ai contatti ufficiali.
Supporto multilingua: italiano (primario) e inglese.
Le date 2026 non sono ancora annunciate — rimandare sempre a rallydiromacapitale.it

## Endpoint API
- POST /api/chat      — chatbot web widget
- POST /api/telegram  — webhook Telegram Bot API ← NUOVO (Fase 1)
- POST /api/whatsapp  — webhook n8n/WhatsApp ← Fase 2 (da aggiungere)
- GET  /health        — health check
- GET  /widget/chat-widget.html — widget statico

## Infrastruttura
- VPS: srv1352958.hstgr.cloud (72.62.42.113)
- n8n: https://n8n.srv1352958.hstgr.cloud
- Credenziali in .env (MAI in git)

## Testing
- Testa ogni endpoint con curl (vedi .claude/commands/)
- Verifica rate limiter
- Verifica sessioni multi-turn
- Telegram: usa `.claude/commands/test-telegram.md`
