# Test Telegram Bot — Rally di Roma Capitale

Testa l'endpoint Telegram del chatbot con curl e dal bot reale.

## Pre-requisiti
- Server in esecuzione su http://localhost:3000
- `TELEGRAM_WEBHOOK_SECRET` configurato nel .env
- (Opzionale) `TELEGRAM_BOT_TOKEN` per test reali

## Test 1 — Simulazione update Telegram via curl

### /start
```bash
SECRET=$(grep TELEGRAM_WEBHOOK_SECRET .env | cut -d= -f2)

curl -s -X POST http://localhost:3000/api/telegram \
  -H "Content-Type: application/json" \
  -H "X-Telegram-Bot-Api-Secret-Token: $SECRET" \
  -d '{
    "update_id": 1,
    "message": {
      "message_id": 1,
      "from": {"id": 123456, "first_name": "Mario", "username": "mario_rossi"},
      "chat": {"id": 123456, "type": "private"},
      "text": "/start",
      "date": 1700000000
    }
  }'
```
Atteso: HTTP 200, il bot invia messaggio di benvenuto a chat_id 123456 (visibile nei log)

### /programma
```bash
curl -s -X POST http://localhost:3000/api/telegram \
  -H "Content-Type: application/json" \
  -H "X-Telegram-Bot-Api-Secret-Token: $SECRET" \
  -d '{
    "update_id": 2,
    "message": {
      "message_id": 2,
      "from": {"id": 123456, "first_name": "Mario"},
      "chat": {"id": 123456, "type": "private"},
      "text": "/programma",
      "date": 1700000001
    }
  }'
```

### /biglietti
```bash
curl -s -X POST http://localhost:3000/api/telegram \
  -H "Content-Type: application/json" \
  -H "X-Telegram-Bot-Api-Secret-Token: $SECRET" \
  -d '{
    "update_id": 3,
    "message": {
      "message_id": 3,
      "from": {"id": 123456, "first_name": "Mario"},
      "chat": {"id": 123456, "type": "private"},
      "text": "/biglietti",
      "date": 1700000002
    }
  }'
```

### Domanda libera (AI)
```bash
curl -s -X POST http://localhost:3000/api/telegram \
  -H "Content-Type: application/json" \
  -H "X-Telegram-Bot-Api-Secret-Token: $SECRET" \
  -d '{
    "update_id": 4,
    "message": {
      "message_id": 4,
      "from": {"id": 123456, "first_name": "Mario"},
      "chat": {"id": 123456, "type": "private"},
      "text": "Quando si svolge il rally?",
      "date": 1700000003
    }
  }'
```

### Keyword media — foto
```bash
curl -s -X POST http://localhost:3000/api/telegram \
  -H "Content-Type: application/json" \
  -H "X-Telegram-Bot-Api-Secret-Token: $SECRET" \
  -d '{
    "update_id": 5,
    "message": {
      "message_id": 5,
      "from": {"id": 123456, "first_name": "Mario"},
      "chat": {"id": 123456, "type": "private"},
      "text": "Hai delle foto del rally?",
      "date": 1700000004
    }
  }'
```

### Domanda in inglese
```bash
curl -s -X POST http://localhost:3000/api/telegram \
  -H "Content-Type: application/json" \
  -H "X-Telegram-Bot-Api-Secret-Token: $SECRET" \
  -d '{
    "update_id": 6,
    "message": {
      "message_id": 6,
      "from": {"id": 789012, "first_name": "John"},
      "chat": {"id": 789012, "type": "private"},
      "text": "What is the schedule for the rally?",
      "date": 1700000005
    }
  }'
```

## Test 2 — Sicurezza

### Secret errato (atteso 403)
```bash
curl -s -o /dev/null -w "%{http_code}" \
  -X POST http://localhost:3000/api/telegram \
  -H "Content-Type: application/json" \
  -H "X-Telegram-Bot-Api-Secret-Token: secret_sbagliato" \
  -d '{"update_id": 99, "message": {"text": "/start", "chat": {"id": 999}, "from": {"id": 999}, "message_id": 1, "date": 1}}'
```
Atteso: `403`

### Secret assente (atteso 403)
```bash
curl -s -o /dev/null -w "%{http_code}" \
  -X POST http://localhost:3000/api/telegram \
  -H "Content-Type: application/json" \
  -d '{"update_id": 99, "message": {"text": "/start", "chat": {"id": 999}, "from": {"id": 999}, "message_id": 1, "date": 1}}'
```
Atteso: `403`

## Test 3 — Sessione continuata (memoria chat_id)

```bash
# Messaggio 1: si presenta
curl -s -X POST http://localhost:3000/api/telegram \
  -H "Content-Type: application/json" \
  -H "X-Telegram-Bot-Api-Secret-Token: $SECRET" \
  -d '{"update_id": 10, "message": {"message_id": 10, "from": {"id": 55555, "first_name": "Luigi"}, "chat": {"id": 55555, "type": "private"}, "text": "Ciao, mi chiamo Luigi", "date": 1700000010}}'

sleep 1

# Messaggio 2: deve ricordare il nome
curl -s -X POST http://localhost:3000/api/telegram \
  -H "Content-Type: application/json" \
  -H "X-Telegram-Bot-Api-Secret-Token: $SECRET" \
  -d '{"update_id": 11, "message": {"message_id": 11, "from": {"id": 55555, "first_name": "Luigi"}, "chat": {"id": 55555, "type": "private"}, "text": "Come mi chiamo?", "date": 1700000011}}'
```
Atteso nei log: la risposta al messaggio 11 menziona "Luigi"

## Test 4 — Rate limit (200 req/min per Telegram)

```bash
# Invia 205 richieste rapide (limite è 200/minuto)
for i in $(seq 1 205); do
  curl -s -o /dev/null -w "%{http_code}\n" \
    -X POST http://localhost:3000/api/telegram \
    -H "Content-Type: application/json" \
    -H "X-Telegram-Bot-Api-Secret-Token: $SECRET" \
    -d "{\"update_id\": $i, \"message\": {\"message_id\": $i, \"from\": {\"id\": 1}, \"chat\": {\"id\": 1, \"type\": \"private\"}, \"text\": \"test $i\", \"date\": 1}}"
done | sort | uniq -c
```
Atteso: 200 risposte `200`, poi alcune `429`

## Test 5 — Dal bot reale

1. Cerca il bot su Telegram per username
2. Invia `/start` → deve rispondere con messaggio di benvenuto
3. Invia `/programma` → info programma
4. Invia `/biglietti` → info biglietti
5. Invia "foto" → link galleria
6. Invia domanda libera → risposta AI
7. Verifica i log: `docker-compose logs -f chatbot` oppure `npm run dev`
