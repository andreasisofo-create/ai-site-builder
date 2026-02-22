# Setup Telegram Bot — Rally di Roma Capitale

Guida completa per configurare il bot Telegram dal BotFather al webhook attivo.

## Fase 1 — Crea il bot su BotFather

1. Apri Telegram e cerca **@BotFather**
2. Invia `/newbot`
3. Scegli un nome: `Rally di Roma Capitale`
4. Scegli uno username (deve finire in `bot`): es. `RallyRomaCapitaleBot`
5. BotFather risponde con il **token**: `7123456789:AAH...xyz`
6. Salva il token — ti servirà nel `.env`

### Comandi opzionali su BotFather
```
/setdescription → "Assistente ufficiale Rally di Roma Capitale 2026"
/setabouttext   → "Chatbot per info su programma, biglietti e logistica"
/setuserpic     → (carica logo evento)
/setcommands    →
start - Avvia il chatbot
help - Mostra i comandi disponibili
programma - Programma dell'evento
biglietti - Info biglietti e acquisto
info - Informazioni generali
```

## Fase 2 — Configura le variabili d'ambiente

```bash
# Nel file .env del progetto
TELEGRAM_BOT_TOKEN=7123456789:AAH...xyz
TELEGRAM_WEBHOOK_SECRET=<generato al passo successivo>
```

### Genera il secret token
```bash
openssl rand -hex 32
# Su Windows (PowerShell):
[System.Web.Security.Membership]::GeneratePassword(64, 0)
# Oppure usa Node.js:
node -e "console.log(require('crypto').randomBytes(32).toString('hex'))"
```

## Fase 3 — Deploy del backend

```bash
# Locale (testing)
npm install
npm run dev

# VPS
git pull
docker-compose up -d --build
```

## Fase 4 — Registra il webhook

```bash
# Sostituisci BOT_TOKEN e SECRET con i valori reali
BOT_TOKEN="7123456789:AAH...xyz"
SECRET="il_tuo_secret_generato"

curl -X POST "https://api.telegram.org/bot${BOT_TOKEN}/setWebhook" \
  -H "Content-Type: application/json" \
  -d "{
    \"url\": \"https://srv1352958.hstgr.cloud/api/telegram\",
    \"secret_token\": \"${SECRET}\",
    \"allowed_updates\": [\"message\"]
  }"
```

**Risposta attesa:**
```json
{"ok":true,"result":true,"description":"Webhook was set"}
```

## Fase 5 — Verifica

```bash
# Controlla info webhook
curl "https://api.telegram.org/bot${BOT_TOKEN}/getWebhookInfo"
```

Dovresti vedere:
```json
{
  "ok": true,
  "result": {
    "url": "https://srv1352958.hstgr.cloud/api/telegram",
    "has_custom_certificate": false,
    "pending_update_count": 0,
    "last_error_message": ""
  }
}
```

## Fase 6 — Test dal vivo

1. Cerca il tuo bot su Telegram per username
2. Invia `/start`
3. Atteso: messaggio di benvenuto con menu comandi
4. Invia `/programma`, `/biglietti`, `/info`
5. Invia una domanda libera: "Quando si svolge il rally?"

## Troubleshooting

| Problema | Soluzione |
|----------|-----------|
| Webhook non risponde | Verifica che HTTPS sia attivo sul VPS |
| 403 Forbidden | Controlla che TELEGRAM_WEBHOOK_SECRET sia uguale in .env e nel webhook |
| Bot non risponde | Controlla i log: `docker-compose logs -f chatbot` |
| "Webhook was set" ma nessun messaggio | Verifica nginx stia proxando `/api/telegram` |
| Messaggi duplicati | Telegram ritrasmette se non riceve 200 — verifica risposta immediata |

## Rimozione webhook (per testing locale con polling)

```bash
curl "https://api.telegram.org/bot${BOT_TOKEN}/deleteWebhook"
```
