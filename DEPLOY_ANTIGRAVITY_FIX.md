# 🚀 DEPLOY FIX GUIDE

Questo documento serve per ripristinare il backend su Render con la configurazione corretta.

## 1. Aggiornamento Codice (Già Fatto)
Antigravity ha già caricato i fix per:
- CORS (permette connessione da Vercel)
- Health Check (per verificare che il DB risponda)
- Logging migliorato

## 2. Configurazione Render (MANUALE RICHIESTA)

Poiché il backend attuale è offline/404, dobbiamo assicurarci che sia configurato correttamente.

Vai su [Dashboard Render](https://dashboard.render.com), seleziona il servizio `site-builder-api` (o creane uno nuovo) e verifica queste impostazioni:

### "Settings" Tab
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
  *(Nota: Assicurati di NON usare 'cd app', il comando corretto parte dalla root del backend)*
- **Root Directory**: `backend`

### "Environment" Tab (Variabili d'Ambiente)
Aggiungi o Aggiorna queste variabili:

| Chiave | Valore |
|--------|--------|
| `PYTHON_VERSION` | `3.9.0` (o versione supportata) |
| `DATABASE_URL` | `postgresql://postgres.xdnpsxjjaupmxocjkngt:E-quipe!12345@aws-1-eu-west-1.pooler.supabase.com:6543/postgres` |
| `REDIS_URL` | *(Inserisci il tuo URL Upstash qui se ce l'hai, altrimenti usa un Redis interno)* |
| `CORS_ALLOW_ALL` | `true` |
| `DEBUG` | `false` |
| `SECRET_KEY` | `site-builder-super-secret-key-change-me` |
| `KIMI_API_KEY` | *(La tua chiave API Kimi/Moonshot)* |

## 3. Deployment
1. Vai su "Manual Deploy" -> "Deploy latest commit".
2. Attendi che il log mostri "Application startup complete".
3. Copia l'URL del servizio (es: `https://site-builder-api-xxxx.onrender.com`).

## 4. Aggiornamento Frontend
Una volta che hai l'URL del backend funzionante:

1. Vai sul progetto Vercel
2. Settings -> Environment Variables
3. Modifica `NEXT_PUBLIC_API_URL` con il nuovo URL di Render.
4. Redeploy del frontend.
