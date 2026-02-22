Testa il widget chat del Rally di Roma Capitale in modo completo.

## Pre-requisiti
Assicurati che il server sia in esecuzione su http://localhost:3000

## Test da eseguire

### 1. Avvio server
```bash
npm run dev
```
Verifica che il server parta senza errori e mostri: "Server avviato su porta 3000"

### 2. Health check
```bash
curl http://localhost:3000/health
```
Risposta attesa: `{"status":"ok","uptime":...,"version":"1.0.0"}`

### 3. Caricamento widget
Apri nel browser: http://localhost:3000/widget/chat-widget.html
Verifica:
- Il bottone flottante appare in basso a destra
- Il colore è rosso #E31937
- Non ci sono errori in console

### 4. Apertura widget
Clicca il bottone flottante.
Verifica:
- La finestra chat si apre con animazione fluida
- L'header mostra "Rally di Roma Capitale" e logo
- Appare il messaggio di benvenuto del bot
- I quick action buttons sono visibili

### 5. Quick action buttons
Clicca ogni bottone e verifica la risposta:
- "📅 Programma" → risposta con date/orari evento
- "🗺️ Come arrivare" → risposta con indicazioni stradali
- "📸 Foto & Video" → risposta con links media
- "📞 Contatti" → risposta con info contatto

### 6. Conversazione libera
Invia questi messaggi e verifica le risposte:
- "Quando si svolge il rally?"
- "Quanto costano i biglietti?"
- "Dov'è il paddock?"
- "C'è parcheggio disponibile?"
- "What is the schedule?" (test inglese)

### 7. Test mobile
Ridimensiona il browser a 375px di larghezza.
Verifica:
- Il widget occupa tutta la larghezza/altezza disponibile
- I bottoni sono sufficientemente grandi per il touch
- Il testo è leggibile

### 8. Chiusura widget
Clicca la X per chiudere.
Verifica:
- Il widget si chiude con animazione
- Il bottone flottante riappare
- La sessione viene mantenuta alla riapertura
