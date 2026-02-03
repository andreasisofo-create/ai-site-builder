# AI Site Builder - Analisi Modello Freemium Pay-per-Page
## Homepage €200 | Pagine Aggiuntive €70

---

## 📊 MODELLO DI BUSINESS ANALIZZATO

### Flusso Utente Completo
```
┌─────────────────────────────────────────────────────────────────┐
│                    FREEMIUM FUNNEL                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  1. LANDING PAGE (Pubblica)                                     │
│     └── "Crea il tuo sito gratis, paga solo quando pubblichi"   │
│                                                                  │
│  2. REGISTRAZIONE GRATUITA                                      │
│     ├── Email + Password                                        │
│     └── Oppure Google OAuth                                     │
│                                                                  │
│  3. DASHBOARD BUILDER (Gratis)                                  │
│     ├── Crea progetto                                           │
│     ├── Aggiungi pagine                                         │
│     ├── Design con AI                                           │
│     └── Preview in tempo reale                                  │
│                                                                  │
│  4. CHECKOUT (Pay per Page)                                     │
│     ├── Homepage:     €200 (obbligatoria)                       │
│     ├── Pagine extra: €70 ciascuna                              │
│     ├── Esempio: 3 pagine = €200 + €140 = €340                  │
│     └── Scegli dominio                                          │
│                                                                  │
│  5. PUBBLICAZIONE                                               │
│     ├── Pagamento Stripe                                        │
│     └── Sito online!                                            │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Vantaggi di Questo Modello
| Vantaggio | Spiegazione |
|-----------|-------------|
| **Conversion Rate Alto** | Utente investe tempo nel builder, più propenso a pagare |
| **Average Order Value** | Upsell naturale pagine extra |
| **No Abandoned Cart** | Preview visibile prima del pagamento |
| **Viral Potential** | Utenti condividono preview gratuita |

### Rischio Principale
- **Costi AI anticipati:** Generazione preview = costo per te senza garanzia di conversione
- **Soluzione:** Limitare rigenerazioni, caching, tiered preview quality

---

## 💰 ANALISI COSTI INFRASTRUTTURA

### 1. COSTI FISSI MENSILI (Prod)

| Servizio | Provider | Costo/mese | Note |
|----------|----------|------------|------|
| **Hosting Frontend** | Vercel Pro | $20 | Next.js app, analytics |
| **Database** | Supabase Pro | $25 | PostgreSQL, 8GB storage |
| **Auth** | Supabase (incluso) | $0 | GoTrue incluso |
| **Storage Assets** | Cloudflare R2 | ~$5 | Immagini, loghi, reference |
| **Redis/Queue** | Upstash | $10 | Rate limiting, cache, sessions |
| **Email** | Resend | $0 | Fino a 3,000 email/mese |
| **AI API** | Anthropic/OpenAI | Variabile | Vedi sotto |
| **Monitoring** | Sentry | $0 | Free tier |
| **DNS** | Cloudflare | $0 | Free plan sufficiente |
| **Analytics** | Plausible/PostHog | $0 | Self-hosted o free tier |
| **TOTALE FISSO** | | **~$60/mese** | ~€55/mese |

### 2. COSTI VARIABILI PER PROGETTO

#### A. Costo AI Generazione
| Operazione | Tokens | Costo |
|------------|--------|-------|
| Analisi immagine (vision) | ~1,000 | $0.003 (Claude 3.5 Sonnet) |
| Generazione homepage | ~4,000 | $0.06 (Claude 3.5 Sonnet) |
| Generazione pagina interna | ~3,000 | $0.045 per pagina |
| Modifica/refinement | ~2,500 | $0.0375 |

**Esempio: Sito 3 pagine**
```
1 homepage:    $0.06
2 pagine:      $0.09  (2 × $0.045)
1 analisi img: $0.003
---------------
TOTALE:        ~$0.153 (~€0.14)
```

#### B. Costo Hosting Siti Utente
| Opzione | Costo | Note |
|---------|-------|------|
| **Vercel API** | $0 | Deploy su Vercel (hobby sufficiente per inizio) |
| **Netlify** | $0 | Alternative free tier |
| **Cloudflare Pages** | $0 | Migliore per traffico alto |

**Nota:** Con molti siti (>100/mese), considerare Vercel Pro $20

#### C. Costo Dominio (se fornito da te)
| Tipo | Costo/anno | Markup per utente |
|------|------------|-------------------|
| Sottodominio gratuito | $0 | Incluso nel prezzo |
| .com | $10-15 | Puoi includere o far pagare extra |
| .it | €8-12 | Registro.it o OVH |

### 3. BREAKEVEN ANALYSIS

#### Scenario Base
```
Prezzi:
├── Homepage:           €200
├── Pagina aggiuntiva:  €70
│
Costi per progetto (es. 3 pagine):
├── AI:                 €0.14
├── Storage:            €0.10
├── Bandwidth:          €0.05
├── Stripe fee (1.5%):  €5.10  (su €340)
└── TOTALE COSTO:       ~€5.40

MARGINE: €340 - €5.40 = €334.60 (98.4% margine!)
```

#### Quanti progetti servono?
```
Costi fissi: €55/mese

Se vendi solo homepage (€200):
→ 1 progetto ogni 4 mesi = break-even

Se vendi media 2 pagine/progetto (€270):
→ 1 progetto ogni 3 mesi = break-even

Se vendi 10 progetti/mese a €300:
→ Revenue: €3,000
→ Costi: €55 + €54 = €109
→ Margine: €2,891 (96%)
```

---

## 🏗️ ARCHITETTURA RACCOMANDATA

### Stack Tecnico Ottimale (Post-Ricerca)

```
┌─────────────────────────────────────────────────────────────────┐
│                    FRONTEND (Next.js 14)                        │
├─────────────────────────────────────────────────────────────────┤
│  Framework:        Next.js 14 (App Router)                      │
│  Styling:          Tailwind CSS + shadcn/ui                     │
│  State:            Zustand (leggero)                            │
│  Query:            TanStack Query v5                            │
│  Form:             React Hook Form + Zod                        │
│  Auth:             Supabase Auth (Google OAuth)                 │
└───────────────────────────┬─────────────────────────────────────┘
                            │
┌───────────────────────────┼─────────────────────────────────────┐
│                           │     BACKEND (Supabase + Edge)       │
├───────────────────────────┼─────────────────────────────────────┤
│                           │                                     │
│  DATABASE:                │  SERVERLESS FUNCTIONS:              │
│  ──────────────────────── │  ─────────────────────────────────  │
│  Supabase PostgreSQL      │  Supabase Edge Functions (Deno)     │
│  • Users                  │  • AI generation                    │
│  • Projects               │  • Webhook Stripe                   │
│  • Pages                  │  • Deploy automation                │
│  • Versions               │                                     │
│  • Assets                 │  AI PROVIDER:                       │
│  • Payments               │  ─────────────────                  │
│                           │  Anthropic Claude 3.5 Sonnet        │
│  STORAGE:                 │  • Miglior rapporto qualità/prezzo  │
│  ─────────                │  • Ottimo per HTML/CSS              │
│  Supabase Storage         │  • Vision per analisi immagini      │
│  • Loghi                  │                                     │
│  • Reference images       │  QUEUE/REDIS:                       │
│  • Generated assets       │  ─────────────                      │
│                           │  Upstash Redis                      │
│  REALTIME:                │  • Queue generazione                │
│  ─────────                │  • Rate limiting                    │
│  Supabase Realtime        │  • Caching                          │
│  • Preview updates        │                                     │
└───────────────────────────┴─────────────────────────────────────┘
                            │
┌───────────────────────────┴─────────────────────────────────────┐
│                    HOSTING SITI UTENTI                          │
├─────────────────────────────────────────────────────────────────┤
│  PRIMARY:           Vercel API                                  │
│  • Deploy automatico                                            │
│  • Preview deployments                                          │
│  • Wildcard SSL                                                 │
│                                                                 │
│  FALLBACK:          Cloudflare Pages                            │
│  • Se Vercel raggiunge limiti                                   │
│  • Migliore cache globale                                       │
└─────────────────────────────────────────────────────────────────┘
```

### Perché Questo Stack?

| Componente | Scelta | Motivazione |
|------------|--------|-------------|
| **Supabase** vs Railway/Neon | Supabase | Auth integrato, storage, realtime, edge functions - tutto in uno |
| **Claude 3.5 Sonnet** vs GPT-4 | Claude | 50% più economico, eccellente per codice |
| **Vercel** vs Netlify | Vercel | API deploy più matura, Next.js nativo |
| **Edge Functions** vs FastAPI | Edge | Serverless, scalabile, costo 0 fino a limite |

---

## 📋 DATABASE SCHEMA

### Tabelle Principali

```sql
-- UTENTI
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255), -- NULL per OAuth
    
    -- OAuth
    provider VARCHAR(50), -- 'google', 'github'
    provider_id VARCHAR(255),
    
    -- Profilo
    full_name VARCHAR(255),
    avatar_url TEXT,
    
    -- Meta
    created_at TIMESTAMP DEFAULT NOW(),
    last_login TIMESTAMP
);

-- PROGETTI (siti)
CREATE TABLE projects (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    
    name VARCHAR(255) NOT NULL,
    description TEXT,
    
    -- Branding
    logo_url TEXT,
    logo_key TEXT,
    favicon_url TEXT,
    
    -- Stile
    primary_color VARCHAR(7) DEFAULT '#3b82f6',
    font_family VARCHAR(100) DEFAULT 'Inter',
    style_config JSONB DEFAULT '{}',
    
    -- Stato
    status VARCHAR(50) DEFAULT 'draft', -- draft, ready, published, archived
    
    -- Dominio
    subdomain VARCHAR(100), -- {subdomain}.tuodominio.com
    custom_domain VARCHAR(255), -- www.cliente.com
    
    -- Deploy
    vercel_project_id VARCHAR(255),
    site_url TEXT,
    
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- PAGINE (pay-per-page)
CREATE TABLE pages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID REFERENCES projects(id) ON DELETE CASCADE,
    
    -- Configurazione
    name VARCHAR(255) NOT NULL, -- "Home", "About", "Services"
    slug VARCHAR(255) NOT NULL, -- "/", "about", "services"
    is_homepage BOOLEAN DEFAULT FALSE,
    
    -- Contenuto
    description TEXT, -- Per AI generation
    sections JSONB DEFAULT '[]', -- Config sezioni
    
    -- Stato pagamento
    is_paid BOOLEAN DEFAULT FALSE,
    paid_at TIMESTAMP,
    
    -- Versioning
    current_version_id UUID,
    
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    UNIQUE(project_id, slug)
);

-- VERSIONI HTML
CREATE TABLE versions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    page_id UUID REFERENCES pages(id) ON DELETE CASCADE,
    
    version_number INTEGER NOT NULL,
    html_content TEXT NOT NULL,
    
    -- AI metadata
    prompt TEXT,
    ai_model VARCHAR(100),
    tokens_used INTEGER,
    generation_time_ms INTEGER,
    
    created_at TIMESTAMP DEFAULT NOW(),
    
    UNIQUE(page_id, version_number)
);

-- PAGAMENTI
CREATE TABLE payments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    project_id UUID REFERENCES projects(id),
    
    -- Stripe
    stripe_session_id VARCHAR(255),
    stripe_payment_intent_id VARCHAR(255),
    
    -- Dettagli
    amount_cents INTEGER NOT NULL, -- €20000 = €200.00
    currency VARCHAR(3) DEFAULT 'EUR',
    
    -- Items (quali pagine paga)
    pages_paid UUID[], -- Array di page_id
    
    -- Stato
    status VARCHAR(50) DEFAULT 'pending', -- pending, completed, failed, refunded
    
    created_at TIMESTAMP DEFAULT NOW(),
    completed_at TIMESTAMP
);

-- ASSETS
CREATE TABLE assets (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID REFERENCES projects(id) ON DELETE CASCADE,
    
    type VARCHAR(50), -- 'logo', 'reference_image', 'generated'
    file_path TEXT NOT NULL,
    file_url TEXT NOT NULL,
    mime_type VARCHAR(100),
    file_size INTEGER,
    
    -- Per reference images
    ai_analysis JSONB, -- Risultato analisi vision AI
    
    created_at TIMESTAMP DEFAULT NOW()
);
```

---

## 🔧 SERVIZI DA REGISTRARE

### 1. OBBLIGATORI (Prima di Iniziare)

| Servizio | URL | Costo | Priorità |
|----------|-----|-------|----------|
| **Dominio principale** | Namecheap/Cloudflare | €10-15/anno | 🔴 Alta |
| **Supabase** | supabase.com | $0 (starter) | 🔴 Alta |
| **Stripe** | stripe.com | 1.5% + €0.25/trans | 🔴 Alta |
| **Vercel** | vercel.com | $0 (hobby) | 🔴 Alta |
| **Upstash Redis** | upstash.com | $0 (free) | 🔴 Alta |
| **Anthropic** | anthropic.com | Pay-per-use | 🔴 Alta |
| **Google OAuth** | console.cloud.google.com | $0 | 🟡 Media |
| **Cloudflare** | cloudflare.com | $0 | 🟡 Media |

### 2. RACCOMANDATI (Dopo MVP)

| Servizio | Utilizzo | Costo |
|----------|----------|-------|
| **Resend** | Email transazionali | $0 (fino a 3k/mese) |
| **Sentry** | Error tracking | $0 (free tier) |
| **Plausible** | Analytics | €9/mese |

### 3. GUIDA REGISTRAZIONE

#### Supabase Setup
```bash
1. Vai su https://supabase.com
2. Crea account con GitHub
3. Crea nuovo progetto
4. Salva:
   - Project URL
   - anon/public key
   - service_role key (segreta!)
5. Abilita Google Auth in Authentication > Providers
```

#### Stripe Setup
```bash
1. Vai su https://stripe.com
2. Completa verifica account (richiede documenti)
3. Attiva "Test mode" per sviluppo
4. Salva:
   - Publishable key (pk_test_...)
   - Secret key (sk_test_...)
   - Webhook secret (whsec_...)
5. Configura webhook endpoint: /api/webhooks/stripe
```

#### Anthropic Setup
```bash
1. Vai su https://console.anthropic.com
2. Richiedi accesso API
3. Genera API key
4. Imposta billing (prepaid o usage-based)
```

---

## ⚠️ FATTIBILITÀ E RISCHI

### ✅ Fattibilità Alta

| Aspetto | Valutazione |
|---------|-------------|
| **Tecnica** | ✅ Completamente fattibile con stack moderno |
| **Economica** | ✅ Margine >95% molto salubre |
| **Tempi** | ✅ MVP in 6-8 settimane |
| **Scalabilità** | ✅ Serverless, scala automatico |

### ⚠️ Rischi e Mitigazioni

| Rischio | Probabilità | Impatto | Mitigazione |
|---------|-------------|---------|-------------|
| **Costi AI imprevisti** | Media | Alto | Rate limiting, caching, limite rigenerazioni |
| **Qualità generazione** | Media | Alto | Prompt engineering, fallback templates |
| **Chargebacks** | Bassa | Medio | Clear refund policy, preview prima pagamento |
| **Abuso preview** | Media | Medio | Limit rigenerazioni utente, captcha |
| **Competizione** | Alta | Medio | Focus su UX, velocità, prezzo competitivo |

### 🎯 KPI da Monitorare

| Metrica | Target | Alert |
|---------|--------|-------|
| Conversion rate (signup → pay) | >15% | <10% |
| Average order value | >€250 | <€200 |
| Costo acquisizione cliente | <€50 | >€100 |
| Customer satisfaction | >4.5/5 | <4.0 |
| Tempo medio generazione | <90s | >120s |

---

## 📅 PIANO IMPLEMENTAZIONE AGGIORNATO

### Fase 1: Setup & Auth (Settimana 1)
- [ ] Registrare tutti i servizi
- [ ] Setup Supabase (DB, Auth, Storage)
- [ ] Landing page pubblica
- [ ] Sistema registrazione/login
- [ ] Dashboard base

**Milestone:** Utente può registrarsi e vedere dashboard

### Fase 2: Builder Core (Settimana 2-3)
- [ ] Creazione progetto
- [ ] Upload logo/reference
- [ ] Sistema pagine (CRUD)
- [ ] Form configurazione contenuti
- [ ] Preview iframe

**Milestone:** Utente può creare progetto con multi-pagine

### Fase 3: AI Generation (Settimana 4)
- [ ] Integrazione Anthropic Claude
- [ ] Vision API per analisi immagini
- [ ] Generation queue (Upstash)
- [ ] Versioning sistema
- [ ] Preview staging

**Milestone:** Utente genera e vede preview sito

### Fase 4: Pagamento & Deploy (Settimana 5)
- [ ] Stripe checkout multi-item
- [ ] Webhook pagamenti
- [ ] Vercel API integration
- [ ] Deploy automatico
- [ ] Sistema domini

**Milestone:** Utente paga e pubblica sito

### Fase 5: Polish (Settimana 6)
- [ ] Modifiche post-generazione
- [ ] Error handling
- [ ] Email notifiche
- [ ] Testing E2E
- [ ] Ottimizzazioni

**Milestone:** MVP pronto per launch

---

## 🚀 RACCOMANDAZIONI FINALI

### Prezzo
```
Homepage: €200      ← Prezzo premium percepito valore
Pagina extra: €70   ← Upsell accessibile

Bundle suggeriti:
- Starter: 1 pagina = €200
- Business: 3 pagine = €320 (sconto €10)
- Premium: 5 pagine = €450 (sconto €50)
```

### Limitazioni Preview (per contenere costi)
```
Free tier:
├── Max 3 progetti
├── Max 5 rigenerazioni/progetto
├── Max 2 pagine/progetto (in preview)
└── Watermark "Preview" sull'iframe

Piano paid (una tantum):
├── Illimitate rigenerazioni per 30 giorni
├── Pagine illimitate (paghi per pubblicazione)
└── No watermark
```

### Competitor Analysis
| Competitor | Modello | Prezzo |
|------------|---------|--------|
| Webflow | SaaS | $14-39/mese |
| Squarespace | SaaS | $16-49/mese |
| Wix | SaaS | $17-159/mese |
| **Tu (proposto)** | One-time | €200-450 una tantum |

**Vantaggio competitivo:** Nessun abbonamento, proprietà totale del sito.

---

## ✅ CHECKLIST GO/NO-GO

Prima di iniziare, assicurati di avere:

- [ ] Budget: €200-500 per setup iniziale (domini, depositi, tools)
- [ ] Dominio principale acquistato
- [ ] Stripe account verificato
- [ ] Anthropic API access
- [ ] 6-8 settimane di tempo sviluppo
- [ ] Piano marketing per acquisizione primi clienti

**Verdetto:** ✅ **PROGETTO FATTIBILE** - Margine economico eccellente, stack tecnico maturo, tempi ragionevoli.

---

Procediamo con l'implementazione? Conferma e partiamo con la Fase 1! 🚀
