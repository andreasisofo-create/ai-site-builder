# 🚀 Guida Deploy - Site Builder su Vercel + Render

## 📋 Architettura Deploy

```
┌─────────────────┐      ┌──────────────────┐      ┌─────────────────┐
│   FRONTEND      │──────▶│     BACKEND      │──────▶│    DATABASE     │
│   (Vercel)      │      │   (Render.com)   │      │  (Supabase PG)  │
│  Next.js 14     │      │   FastAPI        │      │                 │
└─────────────────┘      └──────────────────┘      └─────────────────┘
                                │
                                ▼
                         ┌──────────────────┐
                         │   CACHE/QUEUE    │
                         │   (Upstash)      │
                         └──────────────────┘
```

---

## STEP 1: Database PostgreSQL (Supabase)

### 1.1 Crea Account Supabase
1. Vai su https://supabase.com
2. Sign up con GitHub
3. Crea nuovo progetto:
   - **Nome**: site-builder-db
   - **Password**: genera una password sicura (salvala!)
   - **Region**: Europa (Francoforte) o più vicina a te

### 1.2 Ottieni Connection String
1. Vai su Project Settings → Database
2. Trova **"Connection string"** → Tab **URI**
3. Copia la stringa:
   ```
   postgresql://postgres:[YOUR-PASSWORD]@db.xxxxxx.supabase.co:5432/postgres
   ```
4. Sostituisci `[YOUR-PASSWORD]` con la password del progetto

---

## STEP 2: Redis (Upstash)

### 2.1 Crea Database Redis
1. Vai su https://upstash.com
2. Sign up con GitHub/Google
3. Crea nuovo database:
   - **Nome**: site-builder-redis
   - **Region**: stessa di Supabase (Europa)
   - **Type**: Regional (non Global)

### 2.2 Ottieni URL Redis
1. Nella dashboard del database
2. Trova **"Redis URL"** nel formato:
   ```
   rediss://default:xxxx@xxx.upstash.io:6379
   ```
3. Copia questo URL

---

## STEP 3: Backend su Render

### 3.1 Prepara il codice
Assicurati di avere questi file nel backend:

**backend/render.yaml** (già esistente):
```yaml
services:
  - type: web
    name: site-builder-api
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: uvicorn app.main:app --host 0.0.0.0 --port $PORT
    envVars:
      - key: PYTHON_VERSION
        value: 3.11.0
```

**backend/requirements.txt** aggiornato:
```
fastapi==0.115.0
uvicorn[standard]==0.32.0
sqlalchemy==2.0.36
psycopg2-binary==2.9.9
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.5
httpx==0.27.0
redis==5.0.0
pydantic-settings==2.0.0
python-dotenv==1.0.0
```

### 3.2 Deploy su Render
1. Vai su https://render.com
2. Sign up con GitHub
3. Clicca **"New +"** → **"Web Service"**
4. Collega il repository GitHub
5. Configura:
   - **Name**: site-builder-api
   - **Environment**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

### 3.3 Variabili Ambiente su Render
Vai in Environment e aggiungi:

```bash
# App
DEBUG=false
SECRET_KEY=genera-una-chiave-lunga-e-sicura-32-caratteri

# Database (da Supabase)
DATABASE_URL=postgresql://postgres:password@db.xxx.supabase.co:5432/postgres

# Redis (da Upstash)
REDIS_URL=rediss://default:xxx@xxx.upstash.io:6379

# JWT
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Kimi AI
KIMI_API_KEY=la-tua-chiave-kimi

# Google OAuth (opzionale per ora)
GOOGLE_CLIENT_ID=xxx
GOOGLE_CLIENT_SECRET=xxx
```

### 3.4 Deploy
Clicca **"Create Web Service"**. Attendi il deploy (3-5 minuti).

URL sarà: `https://site-builder-api.onrender.com`

---

## STEP 4: Frontend su Vercel

### 4.1 Prepara il codice
Crea **frontend/.env.production**:
```
NEXT_PUBLIC_API_URL=https://site-builder-api.onrender.com
```

### 4.2 Deploy su Vercel
1. Vai su https://vercel.com
2. Sign up con GitHub
3. Clicca **"Add New Project"**
4. Importa il repository GitHub
5. Configura:
   - **Framework Preset**: Next.js
   - **Root Directory**: `frontend` ⚠️ IMPORTANTE!
   - **Build Command**: `npm run build` (default)
   - **Output Directory**: `.next` (default)

### 4.3 Variabili Ambiente su Vercel
Vai in Settings → Environment Variables:

```bash
# API Backend
NEXT_PUBLIC_API_URL=https://site-builder-api.onrender.com

# Google OAuth
NEXT_PUBLIC_GOOGLE_CLIENT_ID=xxx
GOOGLE_CLIENT_ID=xxx
GOOGLE_CLIENT_SECRET=xxx

# NextAuth
NEXTAUTH_URL=https://tuosito.vercel.app
NEXTAUTH_SECRET=genera-una-chiave-segreta-lunga
```

### 4.4 Deploy
Clicca **"Deploy"**. Attendi (2-3 minuti).

---

## STEP 5: Configurazioni Finali

### 5.1 CORS Backend (IMPORTANTE!)
Aggiorna `backend/app/core/config.py`:
```python
CORS_ORIGINS: List[str] = [
    "http://localhost:3000",
    "https://tuosito.vercel.app",  # ⬅️ AGGIUNGI QUESTO!
]
```

Pusha su GitHub e Render si aggiorna automaticamente.

### 5.2 Google OAuth Callback
Vai su https://console.cloud.google.com/apis/credentials

Aggiungi URI di redirect autorizzati:
```
https://tuosito.vercel.app/api/auth/callback/google
```

### 5.3 Database Migration (prima volta)
Sul terminale locale con database collegato:
```bash
cd backend
export DATABASE_URL="postgresql://..."
python -c "from app.core.database import engine, Base; Base.metadata.create_all(bind=engine)"
```

Oppure crea un endpoint admin temporaneo.

---

## ✅ VERIFICA DEPLOY

### Test API:
```bash
curl https://site-builder-api.onrender.com/health
# Dovrebbe restituire: {"status": "ok"}
```

### Test Frontend:
Apri `https://tuosito.vercel.app` e verifica:
1. ✅ Landing page carica
2. ✅ Login funziona
3. ✅ Dashboard mostra dati
4. ✅ Creazione sito funziona

---

## 🔧 TROUBLESHOOTING

### Errore CORS
```
Access-Control-Allow-Origin...
```
→ Aggiungi il dominio Vercel in `CORS_ORIGINS` nel backend

### Database non connesso
→ Verifica `DATABASE_URL` su Render, assicurati che sia la stringa corretta di Supabase

### 500 Internal Server Error
→ Guarda i log su Render Dashboard → Logs

### Build fallisce su Vercel
→ Verifica che `NEXT_PUBLIC_API_URL` sia impostata

---

## 💰 COSTI STIMATI

| Servizio | Piano | Costo/mese |
|----------|-------|------------|
| **Vercel** | Hobby (free) | $0 |
| **Render** | Web Service (free) | $0 |
| **Supabase** | Free tier | $0 |
| **Upstash** | Free tier | $0 |
| **Kimi API** | Pay per use | ~$0.05/generazione |

**Totale: $0 + costi AI**

⚠️ Limiti free tier:
- Render: si "spegne" dopo 15 min di inattività (cold start ~30s)
- Supabase: 500MB storage, 2GB trasferimento
- Vercel: 100GB bandwidth

---

## 🚀 PROSSIMI STEP

1. ✅ Verifica tutto funzioni
2. Setup dominio personalizzato (opzionale)
3. Configura Stripe per pagamenti reali
4. Aggiungi analytics (Plausible/PostHog)

Buon deploy! 🎉
