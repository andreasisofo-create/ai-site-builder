# Site Builder - Project Context

## Overview
AI-powered website builder (SaaS). Users choose a template, fill in business info, and the system generates a complete one-page website with GSAP animations.

**Stack**: Next.js 14 (frontend, Vercel) + FastAPI (backend, Render) + PostgreSQL + Gemini 2.5 Pro/Flash AI (via OpenRouter) + ChromaDB

## Architecture

### Frontend (Next.js 14, App Router)
- `/dashboard` — Template gallery with 19 live iframe previews, filter tabs by category
- `/dashboard/new` — 3-step wizard: Brand & Info → Sections → Style & Preview
- `/editor/[id]` — Live editor with chat refinement
- `/auth` — Login/register with email + Google OAuth
- Shared template data: `src/lib/templates.ts` (8 categories, 19 styles)

### Backend (FastAPI, Python)
- **Two generation pipelines**:
  1. `databinding_generator.py` — PRIMARY: Gemini generates JSON → TemplateAssembler builds HTML from pre-built components. Faster, consistent, GSAP guaranteed.
  2. `ai_service.py` — FALLBACK: Gemini generates complete HTML directly. Used for custom-free style.
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
| `backend/app/services/databinding_generator.py` | Main generation pipeline (Gemini JSON → templates) |
| `backend/app/services/kimi_client.py` | Provider-agnostic AI client (legacy name, uses Gemini via OpenRouter) |
| `backend/app/services/color_palette.py` | Color harmony palette generation (5 schemes) |
| `backend/app/services/seed_category_guides.py` | Per-category design knowledge (8 categories × 11 fields) |
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
1. **Query ChromaDB** for creative context + category design guide (local, instant)
2. **Color palette**: If user picked a primary color, generate harmony palette (5 schemes) as AI hint
3. **Step 1+2 (parallel)**: Theme JSON (colors, fonts) + Texts JSON (all section content) via Gemini 2.5 Pro
4. **Step 3**: Component selection (deterministic via STYLE_VARIANT_MAP)
5. **Step 4**: TemplateAssembler builds complete HTML with WCAG contrast enforcement

## Deployment
- **Frontend**: Vercel (auto-deploy from GitHub) — `site-generator-v2.vercel.app`
- **Backend**: Render (auto-deploy from GitHub) — `site-builder-api.onrender.com`
- **Database**: PostgreSQL on Render
- **AI**: Gemini 2.5 Pro (generation) + Gemini 2.5 Flash (refine/text) via OpenRouter
- **AI Client**: `kimi_client.py` — provider-agnostic, legacy name. Routes to Gemini via OpenRouter API

## Recent Work (Feb 2026)
1. Restructured wizard from 5 steps to 3 steps
2. Moved template selection to dashboard homepage with live iframe previews
3. Created 19 professional template styles across 8 categories
4. Built creative engine: GSAP v3.0 (29 effects), ChromaDB (105 patterns)
5. Enhanced AI prompts: creative copywriting rules, banned generic text, bold design directives
6. Fixed STYLE_VARIANT_MAP: all 19 styles now have backend component mappings
7. Enhanced 17+ HTML component templates with rich animations
8. Switched AI from Kimi K2.5 to Gemini 2.5 Pro/Flash via OpenRouter
9. Added color harmony palette system (5 schemes: complementary, analogous, triadic, split-comp, mono)
10. Added per-category design guides database (8 categories × 11 design rules)
11. Added WCAG AA contrast enforcement in template_assembler and databinding_generator
12. Added HTML sanitizer + image placeholder generator + quality control system

## Important Notes
- User speaks Italian. Content generation is in Italian.
- ChromaDB auto-seeds on startup (105 patterns) + category design guides (8 categories) via main.py lifespan hook
- The AI prompts explicitly ban generic phrases like "benvenuti", "siamo un'azienda"
- Font pairings are enforced: heading fonts with CHARACTER (Playfair, Space Grotesk, Sora, DM Serif), not system defaults
- All section headings must use `data-animate="text-split"`, all CTAs must use `data-animate="magnetic"`
- AI client class is named `KimiClient` for legacy reasons but actually uses Gemini via OpenRouter. Do NOT reference "Kimi" in new code/comments — use "Gemini" or "AI"

## TODO: Next Session ("riprendiamo")
When the user says "riprendiamo", implement these 3 features:

### 1. Pre-Rendering Predittivo (Streaming Progressivo)
Improve the generation UX so users "watch the site being born" instead of waiting:
- When theme JSON arrives (Step 1): immediately show color palette preview + font names
- When texts JSON arrives (Step 2): show hero title with typewriter effect, section names
- Show skeleton placeholders with pulsing animation matching actual section dimensions
- File: `frontend/src/app/dashboard/new/page.tsx` (wizard), uses `getGenerationStatus()` API
- The backend already sends `preview_data` with colors, fonts, hero_title, sections

### 2. Organic Entropy (Imperfezione Controllata)
Add subtle randomness to break the "template" feel:
- CSS micro-rotation on cards/grid items: `transform: rotate(calc(var(--entropy) * 1deg))` where --entropy is random between -1 and 1
- Add to `head-template.html` as global CSS rule for `.stagger-item, .bento-card` etc.
- In `gsap-universal.js`: randomize stagger delays slightly (add Math.random() * 0.1 offset)

### 3. Card Border Glow (Linear-style hover)
Upgrade the existing cursor-glow to also create a radial-gradient glow on card borders:
- In `gsap-universal.js`: detect mousemove on elements with `data-animate="tilt"` or `.bento-card`
- Apply a `radial-gradient` mask on the card border that follows the mouse position
- CSS: `background: radial-gradient(600px circle at var(--mouse-x) var(--mouse-y), rgba(255,255,255,0.1), transparent 40%)`
- Only on desktop (hover: hover media query)
