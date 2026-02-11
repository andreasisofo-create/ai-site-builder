# Site Builder - Project Context

## Overview
AI-powered website builder (SaaS). Users choose a template, fill in business info, and the system generates a complete one-page website with GSAP animations.

**Stack**: Next.js 14 (frontend, Vercel) + FastAPI (backend, Render) + PostgreSQL + Kimi K2.5 AI + ChromaDB

## Architecture

### Frontend (Next.js 14, App Router)
- `/dashboard` — Template gallery with 19 live iframe previews, filter tabs by category
- `/dashboard/new` — 3-step wizard: Brand & Info → Sections → Style & Preview
- `/editor/[id]` — Live editor with chat refinement
- `/auth` — Login/register with email + Google OAuth
- Shared template data: `src/lib/templates.ts` (8 categories, 19 styles)

### Backend (FastAPI, Python)
- **Two generation pipelines**:
  1. `databinding_generator.py` — PRIMARY: Kimi generates JSON → TemplateAssembler builds HTML from pre-built components. Faster, consistent, GSAP guaranteed.
  2. `ai_service.py` — FALLBACK: Kimi generates complete HTML directly. Used for custom-free style.
- **Component system**: 85 HTML templates in `backend/app/components/` organized by section type (hero/, about/, services/, etc.)
- **GSAP engine**: `gsap-universal.js` (v3.0, 29 effects) auto-injected into every generated site
- **ChromaDB**: Vector database with 105 design patterns, queried during generation for creative context
- **Template assembler**: `template_assembler.py` reads components, replaces placeholders, injects GSAP

### Key Files
| File | Purpose |
|------|---------|
| `frontend/src/lib/templates.ts` | 8 categories, 19 template styles, preview HTML generators |
| `frontend/src/app/dashboard/page.tsx` | Dashboard with template gallery (iframe previews) |
| `frontend/src/app/dashboard/new/page.tsx` | 3-step creation wizard |
| `backend/app/services/databinding_generator.py` | Main generation pipeline (Kimi JSON → templates) |
| `backend/app/services/ai_service.py` | Direct HTML generation pipeline (fallback) |
| `backend/app/services/template_assembler.py` | Assembles HTML from component templates |
| `backend/app/services/design_knowledge.py` | ChromaDB vector DB service |
| `backend/app/services/seed_design_knowledge.py` | 105 design patterns seed script |
| `backend/app/components/gsap-universal.js` | GSAP animation engine (29 effects) |
| `backend/app/components/components.json` | Component registry with variant mappings |

## Template System

### 8 Categories × 19 Styles
1. **Restaurant** (3): restaurant-elegant, restaurant-cozy, restaurant-modern
2. **SaaS** (3): saas-gradient, saas-clean, saas-dark
3. **Portfolio** (3): portfolio-gallery, portfolio-minimal, portfolio-creative
4. **E-commerce** (2): ecommerce-modern, ecommerce-luxury
5. **Business** (3): business-corporate, business-trust, business-fresh
6. **Blog** (2): blog-editorial, blog-dark
7. **Event** (2): event-vibrant, event-minimal
8. **Custom** (1): custom-free

### STYLE_VARIANT_MAP
Each frontend style ID maps to specific backend component variants in `databinding_generator.py`. This is how each template style gets its unique visual identity.

## GSAP Animation System
The `gsap-universal.js` engine supports these `data-animate` attributes:
- **Scroll entrance**: fade-up, fade-down, fade-left, fade-right, scale-in, scale-up, rotate-in, flip-up, blur-in, slide-up, reveal-left/right/up/down, bounce-in, zoom-out
- **Advanced**: text-split (chars/words/lines), text-reveal, typewriter, clip-reveal, blur-slide, rotate-3d, stagger, stagger-scale
- **Interactive**: tilt, magnetic, card-hover-3d, float, gradient-flow, morph-bg, image-zoom, draw-svg, split-screen
- **Utility**: data-counter, data-scroll-progress, marquee, horizontal-scroll, cursor-glow, nav-scroll
- **Modifiers**: data-delay, data-duration, data-ease, data-speed, data-split-type

## Generation Pipeline (databinding_generator.py)
1. **Query ChromaDB** for creative context (local, instant)
2. **Step 1+2 (parallel)**: Theme JSON (colors, fonts) + Texts JSON (all section content)
3. **Step 3**: Component selection (deterministic via STYLE_VARIANT_MAP)
4. **Step 4**: TemplateAssembler builds complete HTML

## Deployment
- **Frontend**: Vercel (auto-deploy from GitHub) — `site-generator-v2.vercel.app`
- **Backend**: Render (auto-deploy from GitHub) — `site-builder-api.onrender.com`
- **Database**: PostgreSQL on Render
- **AI**: Kimi K2.5 via Moonshot API (`api.moonshot.cn/v1`)

## Recent Work (Feb 2026)
1. Restructured wizard from 5 steps to 3 steps
2. Moved template selection to dashboard homepage with live iframe previews
3. Created 19 professional template styles across 8 categories
4. Built creative engine: GSAP v3.0 (29 effects), ChromaDB (105 patterns)
5. Enhanced AI prompts: creative copywriting rules, banned generic text, bold design directives
6. Fixed STYLE_VARIANT_MAP: all 19 styles now have backend component mappings
7. Enhanced 17+ HTML component templates with rich animations

## Important Notes
- User speaks Italian. Content generation is in Italian.
- ChromaDB auto-seeds on startup (105 patterns) via main.py lifespan hook
- The AI prompts explicitly ban generic phrases like "benvenuti", "siamo un'azienda"
- Font pairings are enforced: heading fonts with CHARACTER (Playfair, Space Grotesk, Sora, DM Serif), not system defaults
- All section headings must use `data-animate="text-split"`, all CTAs must use `data-animate="magnetic"`
