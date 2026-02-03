# AI Site Builder - Pianificazione v2
## Modello: Prodotto One-Time €100 (Hosting + Dominio Inclusi)

---

## 1. VISIONE PRODOTTO RAFFINATA

### 1.1 Business Model
```
┌─────────────────────────────────────────────────────────────┐
│                    BUSINESS MODEL                            │
├─────────────────────────────────────────────────────────────┤
│ Prezzo:        €100 (one-time payment)                      │
│ Include:       - Generazione homepage AI                    │
│                - Hosting (illimitato o X anni)              │
│                - Dominio: scelta tra                        │
│                  • Sottodominio gratuito                    │
│                  • Dominio custom (utente compra/registra)  │
│                - SSL certificate                              │
│                - CDN + ottimizzazione performance           │
└─────────────────────────────────────────────────────────────┘
```

### 1.2 User Journey Completo

```
┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐
│  Landing │──▶│  Pagamento│──▶│  Registrazione│──▶│  Builder │──▶│ Preview  │
│  Page    │   │  Stripe  │   │  Completa    │   │  Wizard  │   │  Sito    │
└──────────┘   └──────────┘   └──────────┘   └──────────┘   └─────┬────┘
                                                                  │
┌─────────────────────────────────────────────────────────────────┘
│
▼
┌──────────────┐   ┌──────────────┐   ┌──────────────┐   ┌──────────────┐
│ Scegli       │──▶│ Configura    │──▶│ Deploy       │──▶│ Sito Online  │
│ Dominio      │   │ DNS (se      │   │ Automatico   │   │ ✓ Pubblicato │
│              │   │ custom)      │   │              │   │ ✓ SSL attivo │
└──────────────┘   └──────────────┘   └──────────────┘   └──────────────┘
```

### 1.3 Scope Progetto (Ridotto e Focusato)

| Feature | Incluso | Note |
|---------|---------|------|
| Homepage singola | ✅ | Una pagina completa, responsive |
| Sezioni multiple | ✅ | Hero, About, Services, Contact, Footer |
| Form di contatto | ✅ | Integrato (può usare Formspare o emailJS) |
| SEO base | ✅ | Meta tags, OpenGraph, favicon |
| Pagina multipla | ❌ | Solo homepage per ora |
| E-commerce | ❌ | Non incluso in questa versione |
| Blog | ❌ | Non incluso |
| Backend custom | ❌ | No DB utente, solo sito statico |

---

## 2. FLUSSO DETTAGLIATO

### 2.1 Landing Page (Pubblica)
```
URL: /
Contenuto:
├── Hero: "Il tuo sito professionale in 60 secondi - €100 una tantum"
├── Come funziona (3 step):
│   1. Descrivi il tuo business
│   2. Carica logo e riferimenti
│   3. Ricevi sito online con dominio
├── Esempi/screenshot siti generati
├── Prezzo: €100 (tutto incluso)
├── FAQ
└── CTA: "Inizia Ora" → /checkout
```

### 2.2 Checkout & Pagamento (Stripe)
```
URL: /checkout
Flusso:
1. Utente clicca "Inizia Ora"
2. Stripe Checkout Session (€100)
3. Pagamento completato → Webhook Stripe
4. Redirect a /register?session_id=xxx

Webhook Stripe gestisce:
- Creazione utente (email dal pagamento)
- Marcatura: payment_status = 'paid'
- Invio email di conferma con link accesso
```

### 2.3 Registrazione Completa
```
URL: /register (accessibile solo dopo pagamento)
Dati richiesti:
├── Email (pre-compilata da Stripe)
├── Password
├── Nome completo
└── Nome business (per default subdomain)

Dopo registrazione:
→ Redirect a /dashboard/benvenuto (onboarding)
```

### 2.4 Builder Wizard (3 Step)

#### Step 1: Brand & Info
```
URL: /dashboard/builder/step-1
Campi:
├── Nome sito / business (required)
├── Descrizione attività (required)
│   Esempio placeholder:
│   "Ristorante italiano a Roma centro, cucina tradizionale,
│    specialità pasta fatta in casa, aperto dal 1985..."
├── Upload logo (optional ma consigliato)
│   - Formati: PNG, JPG, SVG
│   - Max 2MB
│   - Auto-resize per web
└── Tagline/slogan (optional)
```

#### Step 2: Ispirazione
```
URL: /dashboard/builder/step-2
Campi:
├── Upload screenshot sito di riferimento #1 (optional)
│   - Analisi AI: palette colori, stile, layout
├── Upload screenshot sito di riferimento #2 (optional)
│   - Per combinare stili diversi
├── URL siti preferiti (text input, optional)
│   - Backup se non riesce upload
└── Stile preferito (select, fallback)
    ├── Moderno/Minimal
    ├── Classico/Elegante
    ├── Bold/Creativo
    ├── Corporate
    └── Vivo/Giocoso
```

#### Step 3: Contenuti
```
URL: /dashboard/builder/step-3
Campi:
├── Sezioni da includere (checkbox):
│   ├── Hero (con CTA)
│   ├── Chi Siamo / About
│   ├── Servizi / Prodotti
│   ├── Gallery (placeholder)
│   ├── Team (optional)
│   ├── Testimonianze (placeholder)
│   ├── Contatti / Form
│   └── Footer completo
│
├── Testi per ogni sezione (textarea)
│   - Oppure "Genera testo AI" che espande descrizione
│
├── Informazioni contatto:
│   ├── Indirizzo
│   ├── Telefono
│   ├── Email
│   ├── Orari apertura
│   └── Social links
│
└── Call to Action primaria:
    ├── "Contattaci"
    ├── "Prenota"
    ├── "Richiedi preventivo"
    └── "Acquista ora"
```

### 2.5 Generazione AI

```
Trigger: Click "Genera Sito" da step-3

Processo Backend:
1. Validazione dati
2. Upload file su storage (logo, reference images)
3. Costruzione prompt per Kimi K2.5
4. Queue task generazione
5. Real-time update via SSE
6. Ricezione HTML
7. Sanitizzazione
8. Salva su DB (versions)
9. Deploy su ambiente staging

Tempo stimato: 30-90 secondi
```

**Prompt Structure per Kimi K2.5:**
```
System: "Sei un esperto web designer. Genera HTML5 semantico 
con Tailwind CSS. Il sito deve essere responsive, moderno, 
e ottimizzato per performance."

User Context:
- Business: {nome} - {descrizione}
- Logo: {logo_url}
- Stile riferimento: {reference_analysis}
- Palette colori: {extracted_colors}
- Sezioni richieste: {sections}
- Contenuti: {content_text}
- CTA: {cta_text}

Output richiesto:
- HTML5 completo in un unico file
- Tailwind CSS via CDN
- JavaScript minimale (solo mobile menu)
- Placeholder immagini da placehold.co
- Form contatto funzionante (formspree action)
- Meta tags SEO
- Favicon link
```

### 2.6 Preview & Modifiche

```
URL: /dashboard/preview/{project_id}
Layout:
┌─────────────────────────────────────────────────────────────┐
│  Navbar: Logo | "Modifica" | "Scegli Dominio" | "Pubblica"  │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│                    ┌───────────────┐                        │
│                    │               │                        │
│     Sidebar        │   IFRAME      │                        │
│     (25%)          │   Preview     │                        │
│     Modifiche      │   (75%)       │                        │
│     - Colori       │               │                        │
│     - Font         │   Sito live   │                        │
│     - Testi        │   preview     │                        │
│     - Rigenera     │               │                        │
│       sezione      │               │                        │
│                    └───────────────┘                        │
└─────────────────────────────────────────────────────────────┘

Modifiche possibili:
1. "Cambia colore primario" → color picker → regenera CSS
2. "Modifica testo sezione X" → textarea → update HTML
3. "Rigenera hero" → prompt specifico → nuova versione
4. "Aggiungi/rimuovi sezione" → update struttura

Ogni modifica crea nuova versione (salvata in DB)
Possibilità di rollback a versioni precedenti
```

### 2.7 Scelta Dominio

```
URL: /dashboard/domain/{project_id}

Opzione A: Sottodominio Gratuito
├── Input: {username}.ai-site-builder.com
├── Verifica disponibilità in realtime
├── Se disponibile → prenota
└── Se non disponibile → suggerisci alternative

Opzione B: Dominio Personalizzato
├── Input: www.miosito.com
├── Verifica disponibilità (WHOIS API)
├── Se disponibile:
│   ├── Mostra prezzo (varia per TLD)
│   ├── "Acquista tramite nostro partner" → redirect
│   └── OPPURE "Ho già comprato questo dominio"
├── Se non disponibile:
│   └── Suggerisci alternative (.com, .it, .net)
└── Se utente ha già dominio:
    ├── Istruzioni configurazione DNS
    ├── Record CNAME/A da configurare
    └── Verifica propagazione DNS

Nota: Per MVP, supportiamo solo sottodominio gratuito + 
      dominio già posseduto dall'utente (configurazione manuale)
```

### 2.8 Deploy & Go Live

```
URL: /dashboard/publish/{project_id}

Processo:
1. Verifica dominio configurato
2. Ottimizzazione finale:
   ├── Minifica HTML
   ├── Ottimizza immagini
   ├── Genera favicon multi-size
   └── Crea sitemap.xml
3. Deploy su hosting:
   ├── Sottodominio: Deploy su Vercel/Netlify con subdomain
   └── Dominio custom: Configura DNS + SSL
4. SSL provisioning (Let's Encrypt)
5. Verifica sito online
6. Invio email conferma con URL sito

Tempo deploy: 1-5 minuti
```

---

## 3. ARCHITETTURA TECNICA V2

### 3.1 Stack Semplificato

```
┌─────────────────────────────────────────────────────────────────┐
│                      FRONTEND (Next.js 14)                       │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────────────────┐ │
│  │  Next.js App │ │  shadcn/ui   │ │  Stripe.js (checkout)    │ │
│  │  Router      │ │  Tailwind    │ │                          │ │
│  └──────────────┘ └──────────────┘ └──────────────────────────┘ │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────────────────┐ │
│  │  React Query │ │  Zustand     │ │  SSE Client (events)     │ │
│  └──────────────┘ └──────────────┘ └──────────────────────────┘ │
└───────────────────────────┬─────────────────────────────────────┘
                            │ HTTPS / JSON
┌─────────────────────────────────────────────────────────────────┐
│                       BACKEND (FastAPI)                          │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────────────────┐ │
│  │   FastAPI    │ │  SQLAlchemy  │ │    Redis (queue + cache) │ │
│  │   (async)    │ │   (Postgre)  │ │                          │ │
│  └──────────────┘ └──────────────┘ └──────────────────────────┘ │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────────────────┐ │
│  │   Stripe     │ │   Kimi SDK   │ │    Vercel API (deploy)   │ │
│  │   Webhooks   │ │   (async)    │ │                          │ │
│  └──────────────┘ └──────────────┘ └──────────────────────────┘ │
└───────────────────────────┬─────────────────────────────────────┘
                            │
┌─────────────────────────────────────────────────────────────────┐
│                      INFRASTRUCTURE                              │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────────────────┐ │
│  │  PostgreSQL  │ │    Redis     │ │   Cloudflare R2          │ │
│  │              │ │   (queue)    │ │   (assets storage)       │ │
│  └──────────────┘ └──────────────┘ └──────────────────────────┘ │
│  ┌──────────────┐ ┌──────────────┐                              │
│  │  Vercel      │ │  Cloudflare  │                              │
│  │  (hosting    │ │  (DNS + SSL  │                              │
│  │   sites)     │ │   + CDN)     │                              │
│  └──────────────┘ └──────────────┘                              │
└─────────────────────────────────────────────────────────────────┘
```

### 3.2 Hosting Strategy

| Aspetto | Soluzione | Motivo |
|---------|-----------|--------|
| **Siti utente** | Vercel API | Deploy automatico, CDN globale, SSL auto |
| **Sottodomini** | Wildcard *.ai-site-builder.com | DNS Cloudflare → Vercel |
| **Domini custom** | Vercel + Let's Encrypt | Utente punta DNS a noi |
| **Assets** | Cloudflare R2 | Costo basso, CDN integrato |
| **Database** | PostgreSQL | Dati utenti, progetti, versioni |

### 3.3 Modello Dati Semplificato

```sql
-- UTENTI (creati dopo pagamento Stripe)
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    
    -- Pagamento
    stripe_customer_id VARCHAR(255),
    stripe_payment_intent_id VARCHAR(255),
    payment_status VARCHAR(50) DEFAULT 'pending', -- pending, paid, refunded
    paid_at TIMESTAMP WITH TIME ZONE,
    
    -- Meta
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_login TIMESTAMP WITH TIME ZONE
);

-- PROGETTI (uno per utente in questa versione)
CREATE TABLE projects (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    -- Configurazione
    name VARCHAR(255) NOT NULL,
    business_description TEXT NOT NULL,
    tagline VARCHAR(500),
    
    -- Assets
    logo_url TEXT,
    logo_key VARCHAR(500),
    reference_image_1_url TEXT,
    reference_image_1_key VARCHAR(500),
    reference_image_2_url TEXT,
    reference_image_2_key VARCHAR(500),
    
    -- Stile estratto
    style_config JSONB DEFAULT '{}', -- colori, font, mood
    
    -- Contenuti
    sections JSONB DEFAULT '[]', -- array di sezioni con contenuti
    contact_info JSONB DEFAULT '{}',
    cta_text VARCHAR(255) DEFAULT 'Contattaci',
    
    -- Stato
    status VARCHAR(50) DEFAULT 'draft', -- draft, generating, ready, published, error
    generation_error TEXT,
    
    -- Dominio
    subdomain VARCHAR(100), -- {subdomain}.ai-site-builder.com
    custom_domain VARCHAR(255), -- www.example.com (NULL se usa subdomain)
    domain_status VARCHAR(50) DEFAULT 'pending', -- pending, configuring, active, error
    
    -- Deploy
    vercel_project_id VARCHAR(255),
    vercel_deployment_url TEXT,
    site_url TEXT, -- URL finale pubblico
    
    -- Timestamp
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    published_at TIMESTAMP WITH TIME ZONE
);

-- VERSIONI HTML
CREATE TABLE versions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    
    version_number INTEGER NOT NULL,
    html_content TEXT NOT NULL,
    
    -- AI metadata
    prompt_used TEXT,
    ai_model VARCHAR(100) DEFAULT 'kimi-k2.5',
    generation_time_ms INTEGER,
    
    -- Stato
    is_current BOOLEAN DEFAULT FALSE,
    is_published BOOLEAN DEFAULT FALSE,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    UNIQUE(project_id, version_number)
);

-- LOG ATTIVITÀ (per debug e supporto)
CREATE TABLE activity_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    project_id UUID REFERENCES projects(id) ON DELETE SET NULL,
    
    action VARCHAR(50) NOT NULL, -- 'payment_completed', 'generation_started', 
                                 -- 'generation_completed', 'domain_configured', 
                                 -- 'site_published', etc.
    status VARCHAR(50) NOT NULL, -- success, error
    details JSONB DEFAULT '{}',
    error_message TEXT,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indici
CREATE INDEX idx_projects_user ON projects(user_id);
CREATE INDEX idx_projects_subdomain ON projects(subdomain);
CREATE INDEX idx_projects_custom_domain ON projects(custom_domain);
CREATE INDEX idx_versions_project ON versions(project_id, version_number DESC);
CREATE INDEX idx_versions_current ON versions(project_id) WHERE is_current = TRUE;
CREATE INDEX idx_logs_user ON activity_logs(user_id, created_at DESC);
```

---

## 4. INTEGRAZIONI ESTERNE

### 4.1 Stripe (Pagamenti)

```
Prodotti:
├── Prodotto: "AI Site Builder - Sito Web Completo"
├── Prezzo: €100.00 (one-time)
└── Stripe Checkout Session

Flusso:
1. Crea Checkout Session (success_url: /register?session_id={})
2. Utente paga su Stripe
3. Webhook "checkout.session.completed"
4. Crea utente con payment_status = 'paid'
5. Invia email di benvenuto
```

### 4.2 Vercel API (Hosting)

```
Operazioni:
├── Create Project (per ogni sito utente)
├── Create Deployment (upload HTML + assets)
├── Configure Domain (subdomain o custom)
├── Get Deployment Status
└── Get Analytics (opzionale)

Autenticazione: Vercel Token
```

### 4.3 Cloudflare (DNS + SSL)

```
Configurazione:
├── Zone: ai-site-builder.com
├── Wildcard: *.ai-site-builder.com → Vercel
├── Custom domains: CNAME → cname.vercel-dns.com
└── SSL: Full (strict)
```

### 4.4 Kimi K2.5 (AI Generation)

```
Endpoint: API Kimi (K2.5 model)
Uso:
├── Analisi immagine riferimento (vision)
├── Generazione HTML completo
└── Refinement/modifiche

Gestione errori:
├── Retry 3x in caso di timeout
├── Fallback a modello alternativo se necessario
└── Cache risultati per 1h (se stesso input)
```

---

## 5. WORKFLOW CRITICI

### 5.1 Pagamento → Accesso

```
Utente clicca "Inizia Ora"
         │
         ▼
┌─────────────────┐
│ Stripe Checkout │
│   Session       │
└────────┬────────┘
         │
         ▼
┌─────────────────┐     ┌─────────────────┐
│  Utente paga    │────▶│ Webhook Stripe  │
│    €100         │     │  (backend)      │
└─────────────────┘     └────────┬────────┘
                                 │
                                 ▼
                    ┌────────────────────────┐
                    │ 1. Verifica pagamento  │
                    │ 2. Crea utente (email) │
                    │ 3. payment_status=paid │
                    │ 4. Invia email accesso │
                    └────────────────────────┘
                                 │
         ┌───────────────────────┘
         ▼
┌─────────────────┐
│ Redirect a      │
│ /register con   │
│ session_id      │
└─────────────────┘
         │
         ▼
┌─────────────────┐
│ Utente crea     │
│ password        │
└─────────────────┘
         │
         ▼
┌─────────────────┐
│ Accesso al      │
│ Dashboard       │
└─────────────────┘
```

### 5.2 Generazione Sito

```
Utente completa Step 3 (builder)
         │
         ▼
┌─────────────────┐
│ POST /generate  │
│ Con tutti i dati│
└────────┬────────┘
         │
         ▼
┌─────────────────────────┐
│ Backend:                │
│ 1. Valida dati          │
│ 2. Salva project config │
│ 3. Enqueue task Redis   │
│ 4. Ritorna job_id       │
└────────┬────────────────┘
         │
         ▼
┌─────────────────────────┐
│ Worker (ARQ):           │
│ 1. Recupera dati        │
│ 2. Analizza reference   │
│    images (Kimi Vision) │
│ 3. Costruisce prompt    │
│ 4. Genera HTML (Kimi)   │
│ 5. Sanitizza HTML       │
│ 6. Salva version        │
│ 7. Deploy staging       │
│ 8. Pubblica status      │
└─────────────────────────┘
         │
         ▼ (SSE/PubSub)
┌─────────────────────────┐
│ Frontend riceve:        │
│ - "generation_complete" │
│ - URL preview           │
└─────────────────────────┘
```

### 5.3 Deploy Live

```
Utente conferma: "Pubblica Sito"
         │
         ▼
┌─────────────────────────┐
│ 1. Verifica dominio     │
│    configurato          │
├─────────────────────────┤
│ 2. Ottimizza assets     │
│    (minify, compress)   │
├─────────────────────────┤
│ 3. Vercel API:          │
│    - Create deployment  │
│    - Upload files       │
├─────────────────────────┤
│ 4. Configura dominio:   │
│    - Se subdomain:      │
│      add domain to      │
│      Vercel project     │
│    - Se custom:         │
│      verify DNS +       │
│      configure SSL      │
├─────────────────────────┤
│ 5. Attiva deploy        │
│    (promote to prod)    │
├─────────────────────────┤
│ 6. Aggiorna DB:         │
│    status=published     │
│    site_url=xxx         │
├─────────────────────────┤
│ 7. Invia email:         │
│    "Sito online!"       │
└─────────────────────────┘
```

---

## 6. UI/UX WIREFRAMES

### 6.1 Landing Page

```
┌─────────────────────────────────────────────────────────────┐
│  Logo                              Login  [Inizia Ora - €100]│
├─────────────────────────────────────────────────────────────┤
│                                                             │
│         IL TUO SITO WEB IN 60 SECONDI                       │
│                                                             │
│    Descrivi la tua attività, carica il logo e ricevi        │
│    un sito professionale completo di dominio e hosting.     │
│                                                             │
│    [🚀 Inizia Ora - €100 (tutto incluso)]                   │
│                                                             │
│    ✓ Homepage personalizzata  ✓ Dominio incluso             │
│    ✓ Hosting illimitato       ✓ SSL gratuito                │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│  COME FUNZIONA                                                │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐                       │
│  │ 1️⃣ Descrivi│  │ 2️⃣ Carica │  │ 3️⃣ Ricevi │                       │
│  │  il tuo   │  │  logo e   │  │  sito     │                       │
│  │  business │  │  riferimenti│  │  online   │                       │
│  └─────────┘  └─────────┘  └─────────┘                       │
├─────────────────────────────────────────────────────────────┤
│  ESEMPI DI SITI GENERATI                                     │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐                      │
│  │ [Preview]│ │ [Preview]│ │ [Preview]│                      │
│  │Ristorante│ │ Negozio  │ │ Studio   │                      │
│  │Italiano  │ │ Online   │ │ Legale   │                      │
│  └──────────┘ └──────────┘ └──────────┘                      │
├─────────────────────────────────────────────────────────────┤
│  TUTTO INCLUSO PER €100 (una tantum)                         │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ ✓ Homepage professionale  ✓ Dominio a scelta           │ │
│  │ ✓ Hosting illimitato      ✓ Certificato SSL            │ │
│  │ ✓ Design responsive       ✓ Supporto email             │ │
│  │ ✓ Form contatto           ✓ Modifiche per 30 giorni    │ │
│  └────────────────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────────┤
│  [🚀 Crea il tuo sito ora - €100]                           │
│                                                             │
│  Hai domande? Scrivi a support@ai-site-builder.com          │
└─────────────────────────────────────────────────────────────┘
```

### 6.2 Dashboard Builder (Step 1)

```
┌─────────────────────────────────────────────────────────────┐
│  Logo    Step 1 di 3    [Exit]                              │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  📝 Informazioni del tuo Business                           │
│                                                             │
│  Nome del sito / attività *                                 │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ Trattoria Da Mario                                  │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  Descrivi la tua attività *                                 │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ Ristorante italiano nel centro storico di Roma.     │   │
│  │ Specialità pasta fresca fatta in casa e piatti      │   │
│  │ tradizionali. Atmosfera familiare e accogliente.    │   │
│  │ Aperto dal 1985.                                    │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  Logo (consigliato)                                         │
│  ┌─────────────────────────────────────────────────────┐   │
│  │                                                     │   │
│  │   [📁 Trascina qui o clicca per caricare]          │   │
│  │                                                     │   │
│  │   Formati: PNG, JPG, SVG | Max 2MB                 │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  Tagline / Slogan (opzionale)                               │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ "Il vero gusto della tradizione romana"             │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│                                       [Avanti →]           │
└─────────────────────────────────────────────────────────────┘
```

### 6.3 Preview & Pubblicazione

```
┌─────────────────────────────────────────────────────────────┐
│  Logo    Il tuo sito è pronto!                     [Profilo]│
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────┐  ┌──────────────────────────────────────┐ │
│  │              │  │                                      │ │
│  │  MODIFICHE   │  │                                      │ │
│  │              │  │     [IFRAME: Sito Generato]          │ │
│  │ Versione:    │  │                                      │ │
│  │ ▼ v1.0       │  │     Hero, About, Services...         │ │
│  │              │  │                                      │ │
│  │ Colore:      │  │     [Responsive Preview]             │ │
│  │ [🔵] [🟢] [🟣]│  │                                      │ │
│  │              │  │     Mobile | Tablet | Desktop        │ │
│  │ Modifica:    │  │                                      │ │
│  │ • Testi      │  └──────────────────────────────────────┘ │
│  │ • Colori     │                                           │
│  │ • Immagini   │  ┌──────────────────────────────────────┐ │
│  │ • Rigenera   │  │  🌐 Scegli dove pubblicare:          │ │
│  │              │  │                                      │ │
│  │ [💬 Chiedi   │  │  (•) Subdominio gratuito             │ │
│  │   modifiche] │  │      trattoria-da-mario.ai-site.com  │ │
│  │              │  │                                      │ │
│  │              │  │  ( ) Dominio personalizzato          │ │
│  │              │  │      [www._____________.com    ]     │ │
│  │              │  │      [Verifica disponibilità]        │ │
│  │              │  │                                      │ │
│  │              │  │  [🚀 Pubblica Sito Ora]              │ │
│  └──────────────┘  └──────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

---

## 7. PIANO IMPLEMENTAZIONE

### Fase 1: Foundation (Settimana 1)
| Task | Ore | Output |
|------|-----|--------|
| Setup Docker (DB, Redis) | 2h | Ambiente dev |
| Init Next.js + shadcn | 3h | Frontend base |
| Init FastAPI | 3h | Backend base |
| Database schema + migrations | 3h | Tabelle pronte |
| Stripe integration (checkout) | 4h | Pagamento funzionante |
| Landing page design | 4h | Homepage pubblica |

**Milestone:** Utente può pagare €100 e ricevere email di conferma

### Fase 2: Auth & Dashboard (Settimana 2)
| Task | Ore | Output |
|------|-----|--------|
| Registrazione post-pagamento | 3h | Flusso completo |
| Login/logout | 2h | Auth funzionante |
| Dashboard layout | 3h | UI dashboard |
| Builder Step 1 UI | 4h | Form brand/info |
| Builder Step 2 UI | 3h | Upload reference |
| Builder Step 3 UI | 4h | Sezioni e contenuti |

**Milestone:** Wizard completo, utente può compilare tutti i dati

### Fase 3: AI Generation (Settimana 3)
| Task | Ore | Output |
|------|-----|--------|
| Kimi API integration | 4h | Chiamate AI |
| Image analysis (vision) | 4h | Estrazione stile |
| Prompt engineering | 4h | HTML di qualità |
| ARQ queue setup | 3h | Background jobs |
| Generation worker | 4h | Task async |
| Preview iframe | 3h | Visualizzazione |

**Milestone:** Sito generato e visibile in preview

### Fase 4: Dominio & Deploy (Settimana 4)
| Task | Ore | Output |
|------|-----|--------|
| Vercel API integration | 4h | Deploy automatico |
| Subdomain management | 3h | *.ai-site.com |
| Custom domain config | 4h | DNS + SSL |
| Deploy automation | 4h | Go live flow |
| Email notifications | 2h | Email transazionali |

**Milestone:** Sito pubblicato e online su dominio scelto

### Fase 5: Polish (Settimana 5)
| Task | Ore | Output |
|------|-----|--------|
| Modifiche post-generazione | 4h | Refinement basic |
| Versioning | 3h | Storico versioni |
| Error handling | 3h | UX errori |
| Responsive testing | 3h | Mobile ok |
| Performance optimization | 3h | Speed test pass |

**Milestone:** MVP completo pronto per launch

---

## 8. DOMINI E INFRASTRUCTURE

### 8.1 Setup Dominio Principale

```
Acquistare: ai-site-builder.com
Configurazione DNS (Cloudflare):
├── A record: ai-site-builder.com → Vercel
├── CNAME: www → ai-site-builder.com
└── Wildcard: *.ai-site-builder.com → Vercel

Vercel:
├── Dominio principale: ai-site-builder.com
├── Wildcard: *.ai-site-builder.com
└── SSL: Auto-provisioned
```

### 8.2 Deploy Siti Utente

```
Per ogni progetto:
1. Vercel API: Create Project
2. Upload HTML + assets
3. Create Deployment
4. Assign domain:
   - subdomain: {sub}.ai-site-builder.com
   - custom: {custom-domain} (utente configura DNS)
```

### 8.3 SSL per Domini Custom

```
Vercel gestisce automaticamente SSL per:
- Tutti i sottodomini wildcard
- Domini custom verificati

Processo dominio custom:
1. Utente inserisce www.miosito.com
2. Verifichiamo DNS punti a Vercel
3. Vercel provisiona SSL (Let's Encrypt)
4. Sito live su HTTPS
```

---

## 9. COSTI STIMATI

### Costi Fissi Mensili (infrastruttura)
| Servizio | Costo/mese | Note |
|----------|------------|------|
| Vercel Pro | $20 | Deploy, CDN, SSL |
| Cloudflare | $0-20 | DNS, SSL wildcard |
| PostgreSQL | $0-15 | Supabase o Railway |
| Redis | $0-10 | Upstash o Railway |
| R2 Storage | $0-5 | Dipende uso |
| Email (Resend) | $0 | Fino a 3k/mese |
| **Totale** | **~$40-70/mese** | |

### Costi Variabili (per utente)
| Voce | Costo | Note |
|------|-------|------|
| Kimi API | ~$0.02-0.05 | Per generazione |
| Bandwidth | ~$0 | Vercel/CDN incluso |
| Storage assets | ~$0.01 | Per sito |
| **Totale per utente** | **~$0.05** | |

### Break-even Analysis
```
Prezzo vendita: €100
Costo variabile: ~€0.05
Margine: ~€99.95

Costi fissi: ~$60/mese = ~€55/mese
Break-even: 1 vendita ogni 2 mesi (!)
```

---

## 10. DECISIONI DA PRENDERE

### 10.1 Prima di Iniziare

1. **Dominio principale:** Quale compriamo?
   - `ai-site-builder.com` (disponibile?)
   - `instant-site.com`
   - `siteweb-ai.com`
   - Altro?

2. **Hosting:** Confermiamo Vercel?
   - ✅ Vercel: Semplice, API mature
   - Alternative: Netlify, Cloudflare Pages

3. **Database:** Quale provider?
   - Supabase (Postgre + Auth)
   - Railway
   - Neon
   - Self-hosted

4. **Scope refinement:**
   - Solo homepage o anche pagine interne?
   - Form contatto: formspree (semplice) o custom?
   - Modifiche post-pubblicazione incluse? Per quanto tempo?

5. **Pricing:**
   - €100 è il prezzo finale?
   - Early bird sconto?
   - Money-back guarantee?

---

## 11. PROSSI PASSI

1. **Confermare decisioni** (sopra)
2. **Acquistare dominio principale**
3. **Setup account:** Stripe, Vercel, Cloudflare
4. **Iniziare Fase 1** (Foundation)

Vuoi procedere? Confermiamo le decisioni e partiamo con l'implementazione! 🚀
