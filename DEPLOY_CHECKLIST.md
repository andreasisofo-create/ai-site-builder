# ✅ CHECKLIST DEPLOY

## Pre-requisiti
- [ ] Account GitHub con codice pushato
- [ ] Account Vercel (https://vercel.com)
- [ ] Account Render (https://render.com) 
- [ ] Account Supabase (https://supabase.com)
- [ ] Account Upstash (https://upstash.com)
- [ ] API Key Kimi (https://platform.moonshot.cn)

---

## STEP 1: Database (Supabase) ⏱️ 5 min
- [ ] Crea progetto su Supabase
- [ ] Copia password database
- [ ] Ottieni Connection String
- [ ] **SALVA**: `postgresql://postgres:xxx@db.xxx.supabase.co:5432/postgres`

---

## STEP 2: Redis (Upstash) ⏱️ 3 min  
- [ ] Crea database Redis
- [ ] Seleziona regione Europa
- [ ] Copia Redis URL
- [ ] **SALVA**: `rediss://default:xxx@xxx.upstash.io:6379`

---

## STEP 3: Backend (Render) ⏱️ 10 min

### 3.1 Crea Web Service
- [ ] Vai su dashboard.render.com
- [ ] New + → Web Service
- [ ] Collega repository GitHub
- [ ] Seleziona directory: `backend`

### 3.2 Configurazione
- [ ] Name: `site-builder-api`
- [ ] Environment: `Python 3`
- [ ] Build Command: `pip install -r requirements.txt`
- [ ] Start Command: `cd app && uvicorn main:app --host 0.0.0.0 --port $PORT`

### 3.3 Environment Variables
Aggiungi queste variabili:
```
DEBUG=false
SECRET_KEY=(genera casuale: openssl rand -hex 32)
DATABASE_URL=(da Supabase)
REDIS_URL=(da Upstash)
KIMI_API_KEY=(tua chiave Kimi)
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### 3.4 Deploy
- [ ] Clicca "Create Web Service"
- [ ] Attendi il deploy (log verde = successo!)
- [ ] **SALVA URL**: `https://xxx.onrender.com`

---

## STEP 4: Frontend (Vercel) ⏱️ 5 min

### 4.1 Crea Progetto
- [ ] Vai su vercel.com
- [ ] Add New Project
- [ ] Importa repository GitHub

### 4.2 Configurazione
- [ ] Framework: Next.js
- [ ] Root Directory: `frontend` ⚠️ IMPORTANTE!
- [ ] Build: lascia default

### 4.3 Environment Variables
```
NEXT_PUBLIC_API_URL=https://xxx.onrender.com (dal backend)
NEXT_PUBLIC_GOOGLE_CLIENT_ID=xxx
GOOGLE_CLIENT_SECRET=xxx
NEXTAUTH_URL=https://xxx.vercel.app (questo URL)
NEXTAUTH_SECRET=(genera casuale)
```

### 4.4 Deploy
- [ ] Clicca Deploy
- [ ] Attendi 2-3 minuti
- [ ] **SALVA URL**: `https://xxx.vercel.app`

---

## STEP 5: Configurazioni Finali ⏱️ 5 min

### 5.1 CORS Backend
- [ ] Vai su Render → Environment
- [ ] Aggiungi: `CORS_ALLOW_ALL=true` (temporaneo per test)
- [ ] Oppure aggiungi il dominio Vercel esatto a `CORS_ORIGINS`
- [ ] Redeploy automatico

### 5.2 Google OAuth
- [ ] Vai su console.cloud.google.com
- [ ] APIs & Services → Credentials
- [ ] Aggiungi URI redirect:
  - `https://xxx.vercel.app/api/auth/callback/google`
- [ ] Salva

### 5.3 Database Init (prima volta)
Apri terminale e esegui:
```bash
curl https://xxx.onrender.com/health
# Se OK, il DB si è creato automaticamente!
```

---

## STEP 6: Test Finale ⏱️ 5 min

- [ ] Apri sito Vercel (https://xxx.vercel.app)
- [ ] Landing page carica? ✅
- [ ] Registrazione funziona? ✅
- [ ] Login funziona? ✅
- [ ] Dashboard si carica? ✅
- [ ] Crea sito di test? ✅
- [ ] Generazione AI funziona? ✅
- [ ] Editor mostra preview? ✅

---

## 🐛 SE QUALCOSA NON VA

### Errore 500 / CORS
```
Render → Environment → CORS_ALLOW_ALL = true
```

### Database non connesso
```
Render → Logs → cerca errori database
Verifica DATABASE_URL su Supabase
```

### Frontend non vede backend
```
Vercel → Settings → Environment Variables
Verifica NEXT_PUBLIC_API_URL sia corretto
```

### Login Google non funziona
```
Google Cloud Console → Verifica URI redirect
Assicurati sia: https://TUO-SITO.vercel.app/api/auth/callback/google
```

---

## 🎉 DEPLOY COMPLETATO!

Il tuo Site Builder è online!

**URLs:**
- Frontend: https://xxx.vercel.app
- Backend: https://xxx.onrender.com
- Database: Supabase
- Cache: Upstash

**Costi mensili:**
- Vercel: $0 (hobby)
- Render: $0 (free tier)
- Supabase: $0 (500MB)
- Upstash: $0 (10k req/giorno)
- Kimi AI: ~$0.05/generazione

---

## 🔒 PRODUZIONE (opzionale)

Per andare in produzione seria:
- [ ] Rimuovi `CORS_ALLOW_ALL=true`
- [ ] Imposta domini CORS esatti
- [ ] Configura Stripe per pagamenti
- [ ] Setup dominio personalizzato
- [ ] SSL certificate (già incluso)
- [ ] Monitoring (Sentry)
- [ ] Backup database (giornaliero)

Buon lavoro! 🚀
