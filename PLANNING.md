# 📋 AI Site Builder - Pianificazione Architetturale

## 1. ANALISI REQUISITI & VINCOLI

### 1.1 Requisiti Funzionali Core
| ID | Requisito | Priorità | Note |
|----|-----------|----------|------|
| R1 | Auth JWT + Google OAuth | Alta | Protezione risorse utente |
| R2 | Wizard 3-step creazione | Alta | UX guidata |
| R3 | Upload logo/reference | Alta | Storage R2 |
| R4 | Generazione AI streaming | Critica | Timeout 120s, retry logic |
| R5 | Preview realtime iframe | Alta | Sandbox, isolamento CSS |
| R6 | Chat refinement iterativo | Media | Versioning automatico |
| R7 | Export HTML/ZIP | Media | Download immediato |
| R8 | Deploy Vercel (opzionale) | Bassa | Future enhancement |

### 1.2 Requisiti Non Funzionali
```
Performance:
├── Time to First Byte (TTFB) < 200ms
├── API response < 500ms (esclusa generazione AI)
├── Upload file < 3s (fino a 5MB)
├── Generazione AI < 90s (target 60s)
└── Preview update < 2s dopo generazione

Scalabilità:
├── 100 utenti concorrenti (MVP)
├── 1000 progetti/mese
├── 10MB storage medio per progetto
└── Orizzontale: +worker nodes per coda AI

Affidabilità:
├── 99.9% uptime target
├── Retry 3x generazione AI
├── Backup DB giornaliero
└── Dead letter queue per task falliti
```

### 1.3 Vincoli Tecnici
- **AI Rate Limits:** Max 5 req/min per utente (gestito via Redis)
- **File Size:** Max 5MB per upload (JPG/PNG/WEBP)
- **HTML Output:** Max 50KB (Tailwind CDN + HTML semantico)
- **Token AI:** Ottimizzare prompt per minore consumo

---

## 2. ARCHITETTURA OTTIMIZZATA

### 2.1 Stack Revisionato per Efficienza

```
┌─────────────────────────────────────────────────────────────────┐
│                    FRONTEND (Next.js 14 App Router)              │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────────────────┐ │
│  │  NextAuth v5 │ │  TanStack    │ │    shadcn/ui + Tailwind  │ │
│  │  (Auth.js)   │ │  Query v5    │ │    (Radix primitives)    │ │
│  └──────────────┘ └──────────────┘ └──────────────────────────┘ │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────────────────┐ │
│  │  Zustand     │ │  React Hook  │ │   Zod (validation)       │ │
│  │  (Lightweight)│ │    Form      │ │                          │ │
│  └──────────────┘ └──────────────┘ └──────────────────────────┘ │
└───────────────────────────┬─────────────────────────────────────┘
                            │ HTTPS / JSON
┌─────────────────────────────────────────────────────────────────┐
│                       BACKEND (FastAPI)                          │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────────────────┐ │
│  │   FastAPI    │ │  SQLAlchemy  │ │    Redis (async redis-py)│ │
│  │   (async)    │ │   2.0 + async│ │    - Rate limiting       │ │
│  └──────────────┘ └──────────────┘ │    - Caching             │ │
│  ┌──────────────┐ ┌──────────────┐ │    - Pub/Sub status      │ │
│  │   Pydantic   │ │   JWT (jose) │ │    - Task queue          │ │
│  │   v2         │ │   Middleware │ └──────────────────────────┘ │
│  └──────────────┘ └──────────────┘ ┌──────────────────────────┐ │
│  ┌──────────────┐ ┌──────────────┐ │    ARQ (async queue)     │ │
│  │   Kimi SDK   │ │   Boto3 (R2) │ │    - Background jobs     │ │
│  │   (async)    │ │   (async)    │ │    - Retry logic         │ │
│  └──────────────┘ └──────────────┘ └──────────────────────────┘ │
└───────────────────────────┬─────────────────────────────────────┘
                            │
┌─────────────────────────────────────────────────────────────────┐
│                      INFRASTRUCTURE                              │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────────────────┐ │
│  │  PostgreSQL  │ │    Redis     │ │   Cloudflare R2          │ │
│  │  16 (asyncpg)│ │   (valkey)   │ │   (S3-compatible)        │ │
│  │  - Pool conn │ │   - Queue    │ │   - CDN edge             │ │
│  └──────────────┘ └──────────────┘ └──────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

### 2.2 Pattern Architetturali Scelti

#### A. CQRS Semplificato (Read/Write Separation)
```python
# Letture veloci con cache
GET /api/projects → Redis cache (5min) → DB fallback

# Scritture dirette a DB + invalidazione cache
POST /api/projects → DB write → Cache invalidate
```

#### B. Queue-Based Task Processing
```
┌─────────┐     ┌─────────┐     ┌─────────┐     ┌─────────┐
│  API    │────▶│  Redis  │────▶│  ARQ    │────▶│  AI     │
│  Server │     │  Queue  │     │  Worker │     │  Kimi   │
└─────────┘     └─────────┘     └─────────┘     └─────────┘
     │                                              │
     │◀────────────── Pub/Sub Status ◀─────────────│
```

#### C. Event-Driven Updates
- WebSocket per real-time updates (generazione AI)
- Pub/Sub Redis per status tracking

---

## 3. MODELLO DATI RAFFINATO

### 3.1 Schema Ottimizzato

```sql
-- ENUM types
CREATE TYPE project_status AS ENUM ('draft', 'queued', 'processing', 'completed', 'error');
CREATE TYPE subscription_tier AS ENUM ('free', 'pro', 'enterprise');
CREATE TYPE asset_type AS ENUM ('logo', 'reference_image', 'generated_asset');

-- USERS: Profilo + quota giornaliera
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255), -- NULL per OAuth
    oauth_provider VARCHAR(50),   -- 'google', 'github', NULL
    oauth_id VARCHAR(255),        -- ID esterno OAuth
    
    -- Subscription & Quota
    tier subscription_tier DEFAULT 'free',
    generations_today INTEGER DEFAULT 0,
    generations_reset_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    daily_limit INTEGER DEFAULT 5, -- Free tier
    
    -- Metadata
    full_name VARCHAR(255),
    avatar_url TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Indici
    CONSTRAINT idx_users_email UNIQUE (email),
    CONSTRAINT idx_users_oauth UNIQUE (oauth_provider, oauth_id) 
        DEFERRABLE INITIALLY DEFERRED
);

-- PROJECTS: Configurazione sito
CREATE TABLE projects (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    -- Info base
    name VARCHAR(255) NOT NULL,
    description TEXT,
    status project_status DEFAULT 'draft',
    
    -- Assets
    logo_url TEXT,
    logo_key VARCHAR(500),        -- R2 object key
    reference_image_url TEXT,
    reference_image_key VARCHAR(500),
    
    -- Stile estratto/preference
    style_config JSONB DEFAULT '{}', -- {primary_color, font_family, layout_type, mood}
    
    -- Statistiche
    generation_count INTEGER DEFAULT 0, -- Quante versioni generate
    last_generated_at TIMESTAMP WITH TIME ZONE,
    
    -- Timestamp
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Indici
    CONSTRAINT idx_projects_user_created 
        UNIQUE (user_id, created_at, id) -- Per pagination efficiente
);
CREATE INDEX idx_projects_user_status ON projects(user_id, status);
CREATE INDEX idx_projects_updated ON projects(updated_at DESC);

-- VERSIONS: Storico codice generato (table partitioning ready)
CREATE TABLE versions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    
    version_number INTEGER NOT NULL,
    html_content TEXT NOT NULL,           -- Codice HTML completo
    css_overrides TEXT,                   -- CSS custom se presente
    
    -- Prompt & AI metadata
    prompt_used TEXT NOT NULL,            -- Snapshot del prompt
    ai_model VARCHAR(100) DEFAULT 'kimi-k2.5',
    tokens_input INTEGER,
    tokens_output INTEGER,
    generation_time_ms INTEGER,           -- Performance tracking
    
    -- Stato
    is_current BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Constraints
    CONSTRAINT idx_versions_project_number 
        UNIQUE (project_id, version_number),
    CONSTRAINT chk_version_number_positive CHECK (version_number > 0)
);
CREATE INDEX idx_versions_project_current ON versions(project_id, is_current) 
    WHERE is_current = TRUE;
CREATE INDEX idx_versions_project_created ON versions(project_id, created_at DESC);

-- ASSETS: File storage metadata
CREATE TABLE assets (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    
    asset_type asset_type NOT NULL,
    file_key VARCHAR(500) NOT NULL,       -- R2 object key
    file_url TEXT NOT NULL,               -- CDN URL (con expiry se private)
    file_size_bytes INTEGER NOT NULL,
    mime_type VARCHAR(100) NOT NULL,
    width INTEGER,                        -- Per immagini
    height INTEGER,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
CREATE INDEX idx_assets_project ON assets(project_id, asset_type);

-- GENERATION_LOGS: Audit & Analytics
CREATE TABLE generation_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    project_id UUID REFERENCES projects(id) ON DELETE SET NULL,
    
    action VARCHAR(50) NOT NULL,          -- 'create', 'refine', 'retry'
    status VARCHAR(50) NOT NULL,          -- 'success', 'error', 'timeout'
    
    -- AI metrics
    ai_model VARCHAR(100),
    tokens_input INTEGER,
    tokens_output INTEGER,
    duration_ms INTEGER,
    error_message TEXT,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
CREATE INDEX idx_logs_user_created ON generation_logs(user_id, created_at DESC);
CREATE INDEX idx_logs_project ON generation_logs(project_id);

-- Trigger per updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_projects_updated_at BEFORE UPDATE ON projects
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Trigger: Solo una versione current per progetto
CREATE OR REPLACE FUNCTION ensure_single_current_version()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.is_current THEN
        UPDATE versions 
        SET is_current = FALSE 
        WHERE project_id = NEW.project_id 
        AND id != NEW.id 
        AND is_current = TRUE;
    END IF;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER trg_single_current_version 
    BEFORE INSERT OR UPDATE ON versions
    FOR EACH ROW EXECUTE FUNCTION ensure_single_current_version();
```

### 3.2 Ottimizzazioni Database

| Ottimizzazione | Scopo | Implementazione |
|---------------|-------|-----------------|
| Connection Pooling | Performance concorrenza | asyncpg pool (min 5, max 20) |
| Query Pagination | Lista progetti | Cursor-based (created_at, id) |
| JSONB indexing | Ricerca per stile | GIN index su style_config |
| Soft delete | Recupero dati | deleted_at column (opzionale) |

---

## 4. PATTERN PERFORMANCE & SCALABILITÀ

### 4.1 Caching Strategy

```
┌─────────────────────────────────────────────────────────────┐
│                     CACHE LAYERS                             │
├─────────────────────────────────────────────────────────────┤
│ L1: React Query (Frontend)                                   │
│     ├── Stale Time: 2 min                                    │
│     ├── Cache Time: 5 min                                    │
│     └── Invalidation: On mutation                            │
├─────────────────────────────────────────────────────────────┤
│ L2: Redis (Backend)                                          │
│     ├── User quota: 1 min TTL                                │
│     ├── Project list: 5 min TTL                              │
│     └── HTML preview: 10 min TTL                             │
├─────────────────────────────────────────────────────────────┤
│ L3: CDN (Cloudflare R2)                                      │
│     ├── Images: 1 year cache                                 │
│     └── Generated HTML: 1 day cache                          │
└─────────────────────────────────────────────────────────────┘
```

### 4.2 Rate Limiting Strategy

```python
# Multi-tier rate limiting con Redis

# Tier 1: Global API (protezione DDoS)
# - 100 req/min per IP

# Tier 2: AI Generation (costo control)
# - Free: 5 gen/day
# - Pro: 50 gen/day  
# - Enterprise: illimitato

# Tier 3: Upload (storage protection)
# - 10 upload/hour per user

# Implementazione: Sliding window con Redis
KEY = f"rate_limit:{tier}:{user_id}"
CURRENT = ZCARD(KEY)  # Count requests in window
IF CURRENT < LIMIT:
    ZADD(KEY, timestamp, unique_id)
    EXPIRE(KEY, WINDOW_SECONDS)
    ALLOW
ELSE:
    DENY with Retry-After header
```

### 4.3 Async Task Flow

```
┌────────────┐    ┌────────────┐    ┌────────────┐    ┌────────────┐
│   Client   │───▶│   API      │───▶│   Redis    │───▶│   ARQ      │
│            │    │   Server   │    │   Queue    │    │   Worker   │
└────────────┘    └────────────┘    └────────────┘    └─────┬──────┘
     ▲                         │                          │
     │                         │ Pub/Sub                  │
     │    ┌────────────────────┘                          ▼
     │    │                                         ┌────────────┐
     │    │                                         │   AI       │
     │    └─────────────────────────────────────────│   Service  │
     │                                              └────────────┘
     │
WebSocket/SSE (status updates)
```

---

## 5. SECURITY & RATE LIMITING

### 5.1 Security Checklist

```yaml
Authentication:
  - JWT con refresh token rotation
  - HttpOnly cookies per token
  - CSRF protection su form
  - OAuth state parameter validation

Authorization:
  - Row-level security (user_id check)
  - Resource ownership verification
  - Tier-based feature gating

Data Protection:
  - Password hashing (bcrypt, 12 rounds)
  - PII encryption at rest (opzionale)
  - HTTPS everywhere
  - Secure headers (HSTS, CSP, X-Frame-Options)

Input Validation:
  - Zod schema validation (frontend + backend)
  - File type verification (magic numbers)
  - HTML sanitizzazione (bleach/ DOMPurify)
  - SQL injection prevention (ORM + parametrized)

Output Security:
  - HTML escaping
  - Content Security Policy
  - X-Content-Type-Options: nosniff
```

### 5.2 HTML Sanitization Strategy

```python
# Whitelist approach per HTML generato da AI
ALLOWED_TAGS = [
    'div', 'section', 'article', 'header', 'footer', 'nav', 'main', 'aside',
    'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'span', 'br', 'hr',
    'a', 'button', 'img', 'svg', 'path', 'circle', 'rect',
    'ul', 'ol', 'li', 'dl', 'dt', 'dd',
    'table', 'thead', 'tbody', 'tr', 'th', 'td',
    'form', 'input', 'textarea', 'select', 'option', 'label',
    'strong', 'em', 'b', 'i', 'u', 's', 'small', 'mark'
]

ALLOWED_ATTRIBUTES = {
    '*': ['class', 'id', 'data-*'],
    'a': ['href', 'target', 'rel'],
    'img': ['src', 'alt', 'width', 'height', 'loading'],
    'button': ['type', 'disabled'],
    'input': ['type', 'name', 'value', 'placeholder', 'required', 'disabled'],
    'svg': ['viewBox', 'xmlns', 'fill', 'stroke', 'width', 'height']
}

# Rimuovi event handlers pericolosi
REMOVE_ATTRIBUTES = ['onclick', 'onload', 'onerror', 'onmouseover', 'eval', 'javascript:']
```

---

## 6. OTTIMIZZAZIONE COSTI AI

### 6.1 Token Optimization Strategy

```python
# Strategia prompt engineering per minimo costo

# 1. System Message riutilizzabile (cached)
SYSTEM_PROMPT = """You are an expert frontend developer specializing in Tailwind CSS.
Generate clean, semantic HTML5 with inline Tailwind classes.
Rules:
- Mobile-first responsive design
- Use only Tailwind utility classes (no custom CSS)
- Include semantic HTML5 tags (header, nav, main, section, footer)
- Images: use placeholder URLs from placehold.co
- No JavaScript except mobile menu toggle
- Output ONLY HTML code, no explanations"""

# 2. Compressione contesto per refinement
# Invece di inviare tutto l'HTML, invia:
# - Sezione specifica (se modifiche localizzate)
# - Diff delle modifiche
# - ID elementi target

# 3. Image analysis caching
# - Estrai palette colori e stile una sola volta
# - Salva in style_config (JSONB)
# - Riutilizza per refinement successivi

# 4. Model selection per task
# - Vision analysis: kimi-k2.5 (vision capabilities)
# - HTML generation: kimi-k2.5 (balance quality/cost)
# - Refinement: kimi-k2.5-mini (se disponibile, per costi minori)
```

### 6.2 Cost Monitoring

```python
# Tracciamento costi per utente/progetto
class CostTracker:
    """
    Kimi K2.5 pricing (esempio):
    - Input: $3.00 / 1M tokens
    - Output: $15.00 / 1M tokens
    
    Media per generazione:
    - Input: 2000 tokens (prompt + image description)
    - Output: 1500 tokens (HTML)
    - Costo: ~$0.025/generazione
    """
    
    def log_generation(self, user_id, tokens_in, tokens_out):
        cost = (tokens_in * 3 + tokens_out * 15) / 1_000_000
        # Salva in generation_logs per analytics
        # Alert se costo utente > soglia
```

---

## 7. PIANO IMPLEMENTAZIONE FASI

### FASE 1: Foundation (Week 1-2)
**Goal:** Infrastruttura e autenticazione funzionante

| Task | Est. | Output |
|------|------|--------|
| Setup Docker Compose (DB, Redis) | 2h | Ambiente locale |
| Init Next.js + shadcn/ui | 3h | Frontend base |
| Init FastAPI + SQLAlchemy | 4h | Backend base |
| Database migrations (Alembic) | 3h | Schema DB |
| Auth JWT + Google OAuth | 6h | Login/logout funzionante |
| Protected routes (FE + BE) | 3h | Sicurezza base |

**Milestone:** Login funzionante, utente può registrarsi e vedere dashboard vuota

---

### FASE 2: Core Features (Week 3-4)
**Goal:** Creazione progetto e upload file

| Task | Est. | Output |
|------|------|--------|
| CRUD Projects API | 4h | Endpoints completi |
| Dashboard UI (lista progetti) | 5h | Grid progetti |
| Wizard 3-step UI | 6h | Form creazione |
| Upload service (R2) | 5h | Logo/reference upload |
| File validation & processing | 3h | Security |
| Create project flow E2E | 4h | Wizard funzionante |

**Milestone:** Utente può creare progetto con descrizione, logo, reference image

---

### FASE 3: AI Generation (Week 5-6)
**Goal:** Generazione sito con AI funzionante

| Task | Est. | Output |
|------|------|--------|
| ARQ setup + worker | 4h | Queue system |
| Kimi API integration | 5h | Generazione HTML |
| Prompt engineering | 6h | Quality output |
| HTML sanitization | 3h | Security |
| Status polling/WebSocket | 4h | Real-time updates |
| Preview iframe component | 5h | Visualizzazione sito |
| Version storage | 3h | Storico versioni |

**Milestone:** Utente genera sito e vede preview in 60 secondi

---

### FASE 4: Refinement (Week 7)
**Goal:** Chat per modifiche iterative

| Task | Est. | Output |
|------|------|--------|
| Chat UI component | 4h | Interfaccia chat |
| Refinement API | 4h | Modifica HTML |
| Version switching | 3h | Storico versioni |
| Context management | 3h | Memoria chat |
| Optimistic updates | 2h | UX fluida |

**Milestone:** Utente può modificare sito via chat e vedere versioni

---

### FASE 5: Export & Polish (Week 8)
**Goal:** Esportazione e UX finale

| Task | Est. | Output |
|------|------|--------|
| ZIP export | 3h | Download file |
| Rate limiting UI | 2h | Mostra crediti |
| Error handling | 4h | Toast notifications |
| Loading states | 3h | Skeleton UI |
| Responsive dashboard | 3h | Mobile support |
| Testing & bugfix | 5h | Stabilità |

**Milestone:** MVP completo funzionante

---

### FASE 6: Optimization (Post-MVP)
**Goal:** Performance e scaling

- [ ] CDN setup per assets
- [ ] Database query optimization
- [ ] Caching layer completo
- [ ] Monitoring (Sentry, Logfire)
- [ ] Analytics (Plausible/PostHog)
- [ ] Vercel deploy integration

---

## 8. STRUTTURA PROGETTO CONSIGLIATA

```
Site Bullder/
├── docker-compose.yml
├── .env.example
├── README.md
├── PLANNING.md
│
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py              # FastAPI app
│   │   ├── config.py            # Settings (pydantic-settings)
│   │   │
│   │   ├── api/                 # Routers
│   │   │   ├── __init__.py
│   │   │   ├── auth.py          # JWT + OAuth
│   │   │   ├── projects.py      # CRUD projects
│   │   │   ├── upload.py        # File upload
│   │   │   ├── generate.py      # AI generation
│   │   │   └── export.py        # Download/Export
│   │   │
│   │   ├── models/              # SQLAlchemy models
│   │   │   ├── __init__.py
│   │   │   ├── user.py
│   │   │   ├── project.py
│   │   │   ├── version.py
│   │   │   └── asset.py
│   │   │
│   │   ├── schemas/             # Pydantic schemas
│   │   │   ├── __init__.py
│   │   │   ├── user.py
│   │   │   ├── project.py
│   │   │   └── generation.py
│   │   │
│   │   ├── services/            # Business logic
│   │   │   ├── __init__.py
│   │   │   ├── auth_service.py
│   │   │   ├── project_service.py
│   │   │   ├── storage_service.py    # R2/S3
│   │   │   ├── generation_service.py # AI integration
│   │   │   └── rate_limiter.py
│   │   │
│   │   ├── core/                # Core utilities
│   │   │   ├── __init__.py
│   │   │   ├── security.py      # JWT, hashing
│   │   │   ├── database.py      # Async SQLAlchemy
│   │   │   ├── redis_client.py  # Redis connection
│   │   │   └── exceptions.py    # Custom exceptions
│   │   │
│   │   └── workers/             # ARQ background tasks
│   │       ├── __init__.py
│   │       └── generation_worker.py
│   │
│   ├── alembic/                 # Database migrations
│   ├── tests/
│   ├── requirements.txt
│   └── Dockerfile
│
├── frontend/
│   ├── app/                     # Next.js App Router
│   │   ├── layout.tsx
│   │   ├── page.tsx             # Landing
│   │   │
│   │   ├── (auth)/              # Auth group
│   │   │   ├── login/page.tsx
│   │   │   └── register/page.tsx
│   │   │
│   │   ├── (dashboard)/         # Protected group
│   │   │   ├── layout.tsx
│   │   │   ├── dashboard/page.tsx
│   │   │   ├── projects/
│   │   │   │   ├── page.tsx
│   │   │   │   ├── [id]/
│   │   │   │   │   ├── page.tsx       # Project detail
│   │   │   │   │   ├── edit/page.tsx  # Wizard
│   │   │   │   │   └── preview/page.tsx
│   │   │   │   └── new/page.tsx
│   │   │   └── settings/page.tsx
│   │   │
│   │   └── api/                 # API routes (Next Auth)
│   │       └── auth/[...nextauth]/route.ts
│   │
│   ├── components/
│   │   ├── ui/                  # shadcn components
│   │   ├── auth/                # Auth forms
│   │   ├── projects/            # Project cards, lists
│   │   ├── wizard/              # Wizard steps
│   │   ├── editor/              # Preview iframe, chat
│   │   └── layout/              # Navbar, sidebar
│   │
│   ├── hooks/                   # Custom React hooks
│   ├── lib/
│   │   ├── api.ts               # API client (axios/fetch)
│   │   ├── auth.ts              # Auth helpers
│   │   └── utils.ts             # Utilities
│   │
│   ├── types/                   # TypeScript types
│   ├── store/                   # Zustand stores
│   └── public/
│
└── shared/                      # Tipi/const condivisi (opzionale)
    └── types/
```

---

## 9. DECISIONI CHIAVE DA PRENDERE

Prima di iniziare l'implementazione, dobbiamo decidere:

### 9.1 Tech Choices
- [ ] **Queue:** ARQ vs Celery vs RQ (consiglio: ARQ per async nativo)
- [ ] **AI Provider:** Kimi vs OpenAI vs Altro (consiglio: Kimi per costi)
- [ ] **Storage:** Cloudflare R2 vs AWS S3 vs MinIO (consiglio: R2 per costi)
- [ ] **Hosting:** Vercel (FE) + Railway/Render (BE) vs VPS

### 9.2 Feature Scope
- [ ] **Refinement:** WebSocket vs SSE vs Polling (consiglio: SSE)
- [ ] **Versioning:** Tutte le versioni o limitate? (consiglio: ultime 10)
- [ ] **Export:** Solo HTML o anche ZIP con assets? (consiglio: entrambi)
- [ ] **Deploy:** Integrazione Vercel nel MVP o dopo? (consiglio: dopo)

### 9.3 Monetizzazione
- [ ] **Free Tier:** 3 o 5 generazioni/giorno?
- [ ] **Pro Tier:** Quanto? Cosa include?
- [ ] **Payment:** Stripe integration nel MVP o dopo?

---

## 10. RISCHI & MITIGAZIONI

| Rischio | Probabilità | Impatto | Mitigazione |
|---------|-------------|---------|-------------|
| AI lenta > 60s | Media | UX | Streaming progress, timeout 120s, retry |
| AI output non valido | Media | Qualità | Parsing robusto, fallback, validazione |
| Costi AI alti | Media | Business | Rate limiting, caching, prompt optimization |
| File upload abuso | Bassa | Sicurezza | Size limits, type validation, rate limiting |
| XSS da HTML generato | Bassa | Sicurezza | Strict sanitization, CSP, iframe sandbox |
| Scaling DB | Bassa | Performance | Connection pooling, query optimization |

---

**Prossimo Step:** Revisione di questo piano e decisioni sulle scelte tecniche, poi iniziamo Fase 1.
