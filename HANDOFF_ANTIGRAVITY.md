# 🚀 HANDOFF - Site Builder per Antigravity

## 📋 Panoramica Progetto

**Site Builder** è una piattaforma web che permette agli utenti di creare siti web professionali usando l'AI (Kimi).

### Funzionalità Core
- 🔐 Autenticazione (email/password + Google OAuth)
- 🎨 Wizard 4-step per creazione sito
- 🤖 Generazione AI siti web completi (HTML + Tailwind)
- 📊 Dashboard gestione progetti
- 👁️ Preview in tempo reale
- 💰 Modello freemium: 2 generazioni gratis, poi upgrade

---

## 🏗️ Architettura

```
┌─────────────────────────────────────────────────────────┐
│  FRONTEND (Next.js 14)                                  │
│  ├── App Router                                          │
│  ├── NextAuth.js (autenticazione)                        │
│  ├── Tailwind CSS (dark UI)                              │
│  └── API Client → Backend                                │
└─────────────────────────┬───────────────────────────────┘
                          │ HTTPS + JWT
┌─────────────────────────▼───────────────────────────────┐
│  BACKEND (FastAPI + Python)                             │
│  ├── API RESTful                                         │
│  ├── JWT Auth                                            │
│  ├── SQLAlchemy (PostgreSQL)                             │
│  ├── Redis (cache/rate limiting)                         │
│  └── Kimi AI Integration                                 │
└─────────────────────────────────────────────────────────┘
```

---

## 📁 Struttura Repository

```
Site Builder/
├── backend/                    # FastAPI Python
│   ├── app/
│   │   ├── api/routes/         # Endpoints
│   │   ├── core/               # Config, DB, Security
│   │   ├── models/             # SQLAlchemy models
│   │   ├── services/           # AI service, OAuth
│   │   └── main.py             # Entry point
│   ├── requirements.txt
│   ├── render.yaml             # Config Render.com
│   └── Procfile
│
├── frontend/                   # Next.js 14
│   ├── src/
│   │   ├── app/                # Pages (App Router)
│   │   ├── components/         # React components
│   │   ├── lib/api.ts          # API client
│   │   └── types/              # TypeScript types
│   ├── package.json
│   └── next.config.js
│
├── DEPLOY_GUIDE.md             # Guida deploy completa
└── DEPLOY_CHECKLIST.md         # Checklist step-by-step
```

---

## 🎯 COSA DEVE FARE ANTIGRAVITY

### Step 1: Preparazione Account (10 min)

Devi creare/ottieni accesso a:

1. **GitHub Repository** - Codice sorgente già pushato
2. **Supabase** (https://supabase.com) - Database PostgreSQL
3. **Upstash** (https://upstash.com) - Redis
4. **Render** (https://render.com) - Hosting backend Python
5. **Vercel** (https://vercel.com) - Hosting frontend Next.js
6. **Kimi AI** (https://platform.moonshot.cn) - API Key per AI
7. **Google Cloud** (https://console.cloud.google.com) - OAuth credentials

---

### Step 2: Database Setup (5 min)

Su **Supabase**:
1. Crea nuovo progetto
2. Salva la password
3. Vai in Project Settings → Database
4. Copia la **"Connection string"** → URI format

```
postgresql://postgres:[PASSWORD]@db.xxxxx.supabase.co:5432/postgres
```

**Salva questa stringa**, servirà per Render.

---

### Step 3: Redis Setup (3 min)

Su **Upstash**:
1. Crea nuovo database Redis
2. Seleziona regione "eu-central-1" (vicina a Supabase)
3. Copia il **"Redis URL"**

```
rediss://default:xxxxx@xxxxx.upstash.io:6379
```

**Salva questa stringa**.

---

### Step 4: Backend Deploy su Render (10 min)

Vai su https://dashboard.render.com

**Nuovo Web Service:**
- Click "New +" → "Web Service"
- Collega repository GitHub
- Seleziona la cartella `backend/`

**Configurazione:**
```
Name: site-builder-api
Environment: Python 3
Build Command: pip install -r requirements.txt
Start Command: cd app && uvicorn main:app --host 0.0.0.0 --port $PORT
```

**Environment Variables** (SEZIONE CRITICA):
```bash
# App
DEBUG=false
SECRET_KEY=genera_con: openssl rand -hex 32
CORS_ALLOW_ALL=true  # ← PER ORA, poi va cambiato

# Database (da Supabase)
DATABASE_URL=postgresql://postgres:xxx@db.xxx.supabase.co:5432/postgres

# Redis (da Upstash)  
REDIS_URL=rediss://default:xxx@xxx.upstash.io:6379

# JWT
ACCESS_TOKEN_EXPIRE_MINUTES=30

# AI
KIMI_API_KEY=chiave_da_platform.moonshot.cn

# Google OAuth (temporaneo, puoi usare credenziali fake per test)
GOOGLE_CLIENT_ID=fake_for_now
GOOGLE_CLIENT_SECRET=fake_for_now
```

**Crea Web Service** e attendi il deploy (3-5 minuti).

**TEST:**
```bash
curl https://TUO-URL.onrender.com/health
# Deve rispondere: {"status": "ok"}
```

---

### Step 5: Frontend Deploy su Vercel (10 min)

Vai su https://vercel.com

**Nuovo Progetto:**
- Click "Add New Project"
- Importa repository GitHub
- Configura:

```
Framework Preset: Next.js
Root Directory: frontend    ⚠️ IMPORTANTE! Non la root!
Build Command: (lascia default)
Output Directory: (lascia default)
```

**Environment Variables**:
```bash
# API Backend (da Render Step 4)
NEXT_PUBLIC_API_URL=https://TUO-URL.onrender.com

# Google OAuth
NEXT_PUBLIC_GOOGLE_CLIENT_ID=xxx.apps.googleusercontent.com
GOOGLE_CLIENT_ID=xxx.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=GOCSPX-xxx

# NextAuth
NEXTAUTH_URL=https://TUO-URL.vercel.app    # ← Questo URL stesso
NEXTAUTH_SECRET=genera_con: openssl rand -base64 32
```

**Deploy** e attendi (2-3 minuti).

---

### Step 6: Configurazione CORS (CRITICO)

Dopo che il frontend è deployato, hai l'URL tipo:
```
https://site-builder-xxx.vercel.app
```

**Su Render** (backend):
1. Vai in Environment
2. Cambia `CORS_ALLOW_ALL` da `true` a `false`
3. Aggiungi variabile:
```
CORS_ORIGINS=["https://site-builder-xxx.vercel.app","http://localhost:3000"]
```
4. Il deploy è automatico

---

### Step 7: Google OAuth Setup (5 min)

Su https://console.cloud.google.com/apis/credentials

1. Crea credenziali OAuth 2.0 (se non esistono)
2. Aggiungi URI di redirect autorizzati:
   ```
   https://TUO-FRONTEND.vercel.app/api/auth/callback/google
   ```
3. Aggiungi origini JavaScript autorizzate:
   ```
   https://TUO-FRONTEND.vercel.app
   ```
4. Copia Client ID e Secret nelle env var di Vercel

---

### Step 8: Verifica Finale

**Test questi flussi:**

1. ✅ Landing page carica (https://xxx.vercel.app)
2. ✅ Registrazione utente funziona
3. ✅ Login funziona
4. ✅ Dashboard mostra "2 generazioni disponibili"
5. ✅ Wizard creazione sito (4 step)
6. ✅ Generazione AI crea sito
7. ✅ Editor mostra preview
8. ✅ Dopo 2 generazioni, compare modal upgrade

---

## 🐛 TROUBLESHOOTING COMUNE

### "Failed to fetch" / CORS errors
```
Verifica CORS_ORIGINS su Render includa il dominio Vercel esatto
```

### "Database connection failed"
```
Verifica DATABASE_URL su Render
Assicurati che la password Supabase sia corretta
```

### "AI generation failed"
```
Verifica KIMI_API_KEY
Verifica che ci siano crediti su platform.moonshot.cn
```

### "Login Google non funziona"
```
Verifica URI redirect su Google Cloud Console
Verifica che NEXTAUTH_URL sia corretto
```

---

## 📞 DOVE TROVARE LE COSE

### File Importanti
- `backend/app/core/config.py` - Configurazioni
- `backend/app/api/routes/` - API endpoints
- `frontend/src/lib/api.ts` - Client API
- `frontend/src/app/dashboard/` - Dashboard pages

### Variabili Critiche
- `CORS_ORIGINS` - Deve matchare dominio frontend
- `NEXT_PUBLIC_API_URL` - URL backend Render
- `DATABASE_URL` - Connection string Supabase
- `KIMI_API_KEY` - API key Moonshot

---

## ✅ CHECKLIST PRE-CONSEGNA

Prima di dire "fatto", verifica:

- [ ] Backend risponde a /health
- [ ] Frontend carica senza errori 500
- [ ] Login/registrazione funziona
- [ ] Creazione sito completo funziona
- [ ] Generazione AI produce HTML
- [ ] Sistema quota (2 gratis) funziona
- [ ] Modal upgrade appare al limite

---

## 💰 COSTI

Tutto free tier:
- Vercel: $0
- Render: $0 (si spegne dopo 15min inattività)
- Supabase: $0 (500MB)
- Upstash: $0
- Kimi AI: ~$0.05 a generazione (pay-per-use)

---

**DOMANDE?** Controlla prima:
1. `DEPLOY_CHECKLIST.md` nella root
2. Log di Render (per errori backend)
3. Console browser (per errori frontend)

Buon deploy! 🚀
