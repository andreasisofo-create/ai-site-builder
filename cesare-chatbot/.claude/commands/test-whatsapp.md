> ⚠️ **FASE 2** — WhatsApp è il canale della Fase 2, dopo il testing su Telegram.
> Il canale primario attuale è **Telegram** (vedi `test-telegram.md`).
> Aggiungi `backend/routes/whatsapp.js` e montalo in `server.js` solo dopo che Telegram funziona.

Testa l'endpoint WhatsApp del chatbot con curl.

## Pre-requisiti
Server in esecuzione su http://localhost:3000

## Test endpoint /api/whatsapp

### 1. Test base — domanda sul programma
```bash
curl -s -X POST http://localhost:3000/api/whatsapp \
  -H "Content-Type: application/json" \
  -d '{"message": "Quando si svolge il rally?", "session_id": "test-wa-001", "from": "+393331234567"}' \
  | jq .
```
Atteso: risposta con date evento, `success: true`

### 2. Test navigazione
```bash
curl -s -X POST http://localhost:3000/api/whatsapp \
  -H "Content-Type: application/json" \
  -d '{"message": "Come arrivo?", "session_id": "test-wa-001", "from": "+393331234567"}' \
  | jq .
```
Atteso: indicazioni stradali, parcheggi

### 3. Test biglietti
```bash
curl -s -X POST http://localhost:3000/api/whatsapp \
  -H "Content-Type: application/json" \
  -d '{"message": "Quanto costa il biglietto?", "session_id": "test-wa-001", "from": "+393331234567"}' \
  | jq .
```
Atteso: prezzi e link acquisto

### 4. Test location
```bash
curl -s -X POST http://localhost:3000/api/whatsapp \
  -H "Content-Type: application/json" \
  -d '{"message": "Dov'\''è il paddock?", "session_id": "test-wa-001", "from": "+393331234567"}' \
  | jq .
```

### 5. Test media
```bash
curl -s -X POST http://localhost:3000/api/whatsapp \
  -H "Content-Type: application/json" \
  -d '{"message": "Mandami le foto", "session_id": "test-wa-001", "from": "+393331234567"}' \
  | jq .
```
Atteso: links a galleria foto/video

### 6. Test multilingua (inglese)
```bash
curl -s -X POST http://localhost:3000/api/whatsapp \
  -H "Content-Type: application/json" \
  -d '{"message": "What is the schedule?", "session_id": "test-wa-eng", "from": "+441234567890"}' \
  | jq .
```
Atteso: risposta in inglese

### 7. Test continuità sessione
```bash
# Prima domanda
curl -s -X POST http://localhost:3000/api/whatsapp \
  -H "Content-Type: application/json" \
  -d '{"message": "Mi chiamo Marco", "session_id": "test-session-continuity", "from": "+393339999999"}' \
  | jq .response

# Seconda domanda (deve ricordare il nome)
curl -s -X POST http://localhost:3000/api/whatsapp \
  -H "Content-Type: application/json" \
  -d '{"message": "Come mi chiamo?", "session_id": "test-session-continuity", "from": "+393339999999"}' \
  | jq .response
```
Atteso: la seconda risposta menziona "Marco"

### 8. Test rate limiter
```bash
# Invia 35 richieste rapide (il limite è 30/minuto)
for i in $(seq 1 35); do
  curl -s -X POST http://localhost:3000/api/whatsapp \
    -H "Content-Type: application/json" \
    -d "{\"message\": \"Test $i\", \"session_id\": \"rate-test\", \"from\": \"+39000\"}" \
    | jq -r '.error // "OK"'
done
```
Atteso: le ultime 5+ risposte devono mostrare errore rate limit (429)

### 9. Test sessione nuova vs esistente
```bash
# Verifica che session_id diversi siano sessioni separate
curl -s -X POST http://localhost:3000/api/whatsapp \
  -H "Content-Type: application/json" \
  -d '{"message": "Ciao, sono il primo utente", "session_id": "utente-A", "from": "+393330000001"}' | jq .

curl -s -X POST http://localhost:3000/api/whatsapp \
  -H "Content-Type: application/json" \
  -d '{"message": "Ciao, sono il secondo utente", "session_id": "utente-B", "from": "+393330000002"}' | jq .
```
