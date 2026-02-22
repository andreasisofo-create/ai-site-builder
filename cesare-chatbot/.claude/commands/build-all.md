Costruisci l'intero progetto del chatbot Rally di Roma Capitale 2026.

Leggi prima CLAUDE.md per capire il contesto e le convenzioni.

Esegui questi passi nell'ordine esatto:

1. **Inizializza il progetto Node.js**
   - Crea `package.json` con `"type": "module"` e tutti gli script necessari
   - Installa dipendenze: express, @anthropic-ai/sdk, dotenv, cors, express-rate-limit

2. **Crea la knowledge base** (`backend/services/knowledge.js`)
   - Informazioni complete sull'evento Rally di Roma Capitale 2026
   - Date, location, programma, prezzi biglietti, come arrivare, contatti
   - Funzione di ricerca contestuale

3. **Crea il servizio AI** (`backend/services/ai.js`)
   - Integrazione Anthropic Claude SDK (ESM)
   - System prompt specifico per il Rally
   - Gestione sessioni con Map in memoria (TTL 30 minuti)
   - Funzione `chat(sessionId, message)` che ritorna la risposta

4. **Crea il servizio media** (`backend/services/media.js`)
   - Links a foto, video, mappe del percorso
   - Funzione per recuperare media per categoria

5. **Crea i middleware** (`backend/middleware/`)
   - `rateLimit.js` — 30 richieste/minuto per IP
   - `cors.js` — CORS configurabile via .env

6. **Crea le routes** (`backend/routes/`)
   - `chat.js` — POST /api/chat per il widget web
   - `whatsapp.js` — POST /api/whatsapp per webhook n8n
   - `health.js` — GET /health con uptime e versione

7. **Crea il server principale** (`backend/server.js`)
   - Express app con tutte le routes
   - Static serving della cartella widget/
   - Error handler globale

8. **Crea il widget chat** (`widget/chat-widget.html`)
   - Usa l'agente @frontend-designer
   - Singolo file HTML+CSS+JS
   - Design professionale con colori Rally

9. **Crea lo script embed** (`widget/embed.js`)
   - Snippet minimalista per WordPress
   - Carica il widget in modo lazy

10. **Crea la configurazione Docker** (usa @devops-engineer)
    - `docker/Dockerfile` multi-stage
    - `docker/docker-compose.yml`

11. **Crea il workflow n8n** (usa @n8n-integrator)
    - `n8n/whatsapp-flow.json` importabile
    - `n8n/setup-guide.md` in italiano

12. **Crea i file di configurazione**
    - `.env.example` con tutte le variabili documentate
    - `.gitignore` completo
    - `README.md` con istruzioni

13. **Testa il backend**
    - Avvia con `npm run dev`
    - Testa /health con curl
    - Testa /api/chat con un messaggio di prova
