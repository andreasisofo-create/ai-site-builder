# Site Builder - Architecture Deep Dive & Audit Report

> Generated: February 2026 | Based on deep audit by 4 specialized agents

---

## Table of Contents

1. [System Overview](#1-system-overview)
2. [Generation Pipeline](#2-generation-pipeline)
3. [Component System](#3-component-system)
4. [AI Prompt Chain](#4-ai-prompt-chain)
5. [Theme & Visual System](#5-theme--visual-system)
6. [GSAP Animation Engine](#6-gsap-animation-engine)
7. [Template Selection Logic](#7-template-selection-logic)
8. [Audit: Why All Sites Look the Same](#8-audit-why-all-sites-look-the-same)
9. [Recommended Fixes](#9-recommended-fixes)

---

## 1. System Overview

**Stack**: Next.js 14 (Vercel) + FastAPI (Render) + PostgreSQL + Kimi K2.5 AI + ChromaDB

**Flow**: User picks template style (1 of 19) → fills wizard (brand, sections, style) → backend generates complete one-page HTML with GSAP animations.

```
Frontend (Vercel)                    Backend (Render)
┌─────────────────┐                 ┌──────────────────────────────┐
│ Dashboard        │  HTTP/JSON     │ FastAPI                      │
│  └─ Template     │ ──────────────►│  └─ /api/sites/              │
│     Gallery (19) │                │     └─ databinding_generator  │
│                  │                │        ├─ ChromaDB query      │
│ Wizard (3 steps) │                │        ├─ Kimi: theme JSON    │
│  1. Brand & Info │                │        ├─ Kimi: texts JSON    │
│  2. Sections     │                │        ├─ Component selection │
│  3. Style & Prev │                │        └─ TemplateAssembler   │
│                  │  ◄─────────────│            └─ Final HTML      │
│ Editor           │  HTML response │                               │
│  └─ Live preview │                │ ChromaDB (105 patterns)       │
│  └─ Chat refine  │                │ PostgreSQL (users, sites)     │
└─────────────────┘                 └──────────────────────────────┘
```

### Key Files

| File | Purpose |
|------|---------|
| `frontend/src/lib/templates.ts` | 8 categories, 19 template styles, preview HTML |
| `frontend/src/app/dashboard/page.tsx` | Template gallery with iframe previews |
| `frontend/src/app/dashboard/new/page.tsx` | 3-step creation wizard |
| `backend/app/services/databinding_generator.py` | **Main generation pipeline** (~2700 lines) |
| `backend/app/services/template_assembler.py` | Assembles HTML from component templates |
| `backend/app/services/ai_service.py` | Fallback: direct HTML generation |
| `backend/app/services/design_knowledge.py` | ChromaDB vector DB service |
| `backend/app/components/components.json` | Component registry (91 variants) |
| `backend/app/components/gsap-universal.js` | GSAP animation engine (29 effects) |
| `backend/app/components/head/head-template.html` | Global CSS (352 lines) |

---

## 2. Generation Pipeline

The primary pipeline (`databinding_generator.py`) runs in 4 steps:

### Step 0: Preparation
```
Input: business_name, business_description, template_style_id, sections[], hero_type, hero_video_url
│
├─ Query ChromaDB for creative_context (top-K design patterns)
├─ Pick variety_context: random personality (1/12), color_mood (1/12), font_pairing (1/17)
└─ Extract category from template_style_id (e.g., "restaurant-elegant" → "restaurant")
```

### Step 1: Theme Generation (Kimi AI)
```
Prompt: "You are a Dribbble/Awwwards-level UI designer..."
├─ Inputs: business info, color_mood hint, font_pairing suggestion, creative_context
├─ Temperature: 0.3 (reference mode) or 0.75 (creative mode)
├─ Output: JSON with colors (primary, secondary, accent, bg, bg-alt, text, text-muted)
│          + fonts (heading, body) + Google Fonts URLs
└─ Fallback: FALLBACK_THEME_POOL (8 hardcoded palettes) if AI fails
```

### Step 2: Text Generation (Kimi AI)
```
Prompt: "You are Italy's most awarded copywriter..."
├─ Inputs: business info, personality directive, category tone, few-shot examples,
│          banned phrases list, ChromaDB creative_context, reference hints
├─ Temperature: 0.75 (first try), 0.5 (retry)
├─ Output: JSON with all section content (hero_title, hero_subtitle, about_text,
│          services[], testimonials[], stats[], CTAs, etc.)
└─ Business description limited to 800 chars
```

### Step 3: Component Selection (Deterministic)
```
template_style_id → STYLE_VARIANT_MAP (fixed defaults)
                  → STYLE_VARIANT_POOL (2-5 random options per section)
                  → _select_components_deterministic() picks one variant per section
                  → Override: hero_type="video" → forces hero-video-bg-01
```

### Step 4: HTML Assembly
```
TemplateAssembler:
├─ Reads head-template.html (global CSS + meta)
├─ For each section: loads component .html template
├─ Replaces {{PLACEHOLDERS}} with AI-generated content
├─ Injects CSS variables from theme JSON
├─ Appends gsap-universal.js
└─ Returns complete standalone HTML document
```

---

## 3. Component System

### Inventory (94 HTML files, 91 registered)

| Section | Variants | Registered | Used in STYLE_VARIANT_MAP |
|---------|----------|------------|--------------------------|
| **hero** | 18 | 17 | 18 (strong diversity) |
| **services** | 9 | 9 | 9 (100%) |
| **features** | 8 | 8 | 8 (100%) |
| **about** | 8 | 8 | 8 (100%) |
| **testimonials** | 6 | 6 | 6 (100%) |
| **footer** | 6 | 6 | 6 (100%) |
| **contact** | 6 | 6 | 6 (100%) |
| **cta** | 6 | 6 | ~5 (83%) |
| **pricing** | 5 | 5 | 5 (100%) |
| **gallery** | 4 | 4 | 4 (100%) |
| **faq** | 4 | 4 | ~2 (50%) |
| **nav** | 3 | 3 | 3 (BOTTLENECK) |
| **process** | 3 | 3 | 3 (100%) |
| **team** | 2 | 2 | 2 (100%) |
| **video** | 2 | 2 | 2 (100%) |
| **stats** | 1 | 1 | 1 |
| **logos** | 1 | 1 | 1 |
| **timeline** | 1 | 1 | 1 |

**Total: 94 files on disk, 91 in registry**

### Component Structure (All Follow Same Pattern)

Every component uses:
- **Tailwind CSS** utility classes for layout
- **CSS Variables** for colors: `var(--color-primary)`, `var(--color-bg)`, etc.
- **data-animate** attributes for GSAP: `data-animate="fade-up"`, `data-animate="text-split"`, etc.
- **Consistent spacing**: `py-24 lg:py-32` sections, `max-w-7xl mx-auto px-6` containers
- **{{PLACEHOLDER}}** syntax for AI-generated content

Example structure:
```html
<section id="about" class="py-24 lg:py-32 bg-[var(--color-bg)]">
  <div class="max-w-7xl mx-auto px-6">
    <div class="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
      <h2 class="text-4xl font-heading font-bold" data-animate="text-split">
        {{ABOUT_TITLE}}
      </h2>
      <p>{{ABOUT_TEXT}}</p>
    </div>
  </div>
</section>
```

### Hero Variants (18 types)
split, centered, gradient, parallax, typewriter, glassmorphism, dark-bold, video-bg, animated-shapes, brutalist, editorial, zen, neon, classic, organic, linear, rotating, physics

### Layout Types Used Across Components
- **Grid**: 2-col, 3-col, 4-col, 12-col
- **Bento**: Asymmetric grids
- **Split**: Left/right with image
- **Alternating**: Zigzag rows
- **Cards**: Hover effects, stacks
- **Carousel/Marquee**: Horizontal scroll
- **Masonry**: Pinterest-style
- **Tabs**: Interactive switching

---

## 4. AI Prompt Chain

### Variety Injection System

Three randomized pools create the "creative seed" for each generation:

**PERSONALITY_POOL (12 options)**:
provocative, poetic, minimal, bold, storytelling, ironic, technical, warm, avant-garde, luxurious, punk, zen

**COLOR_MOOD_POOL (12 options)**:
Sunset Warmth, Ocean Depth, Forest Calm, Electric Night, Desert Minimal, Nordic Clean, Art Deco Luxe, Candy Pop, Monochrome Power, Terracotta Earth, Cyber Fresh, Royal Velvet

**FONT_PAIRING_POOL (17 pairs)**:
Playfair/Inter, Space Grotesk/DM Sans, Sora/Inter, DM Serif/Manrope, Outfit/Inter, Fraunces/Outfit, Epilogue/Inter, Bricolage/DM Sans, Instrument Serif/Inter, Libre Baskerville/Source Sans, Unbounded/DM Sans, Cormorant/Montserrat, Archivo Black/Inter, Josefin Sans/Open Sans, Bitter/Raleway, Albert Sans/Inter, + system default

**Theoretical combinations**: 12 x 12 x 17 = **2,448**
**Practical variety**: ~50-100 truly distinct outputs (convergence due to AI behavior)

### Theme Prompt (Step 1) - Key Directives

```
"You are a Dribbble/Awwwards-level UI designer"
├─ PRIMARY: "The brand's emotional core"
├─ SECONDARY: "Must create VISUAL TENSION with primary"
├─ ACCENT: "CTA/action color. Must POP against background"
├─ FORBIDDEN: "Muddy browns, desaturated greens, pure gray, neon"
├─ COLOR_MOOD direction: "follow this closely"
└─ FONT suggestion: "use unless it clashes with the business"
```

### Text Prompt (Step 2) - Key Directives

```
"You are Italy's most awarded copywriter — Oliviero Toscani meets Apple"
├─ Personality: ONE of 12 personalities per generation
├─ Category tone: 8 tones (restaurant=sensorial, saas=sharp, etc.)
├─ Few-shot examples: vary per category
├─ Banned phrases: "Benvenuti", "Siamo un'azienda", "I nostri servizi"
├─ Hero: MAX 6 words, metaphors/contrasts/provocations
├─ Stats: SPECIFIC non-round numbers
├─ CTAs: action verb + urgency
└─ Business description: max 800 chars
```

### ChromaDB Creative Context

- **105 design patterns** seeded on startup
- Queried per generation → truncated to 500-2500 chars
- Injected as "DESIGN KNOWLEDGE (follow these professional guidelines closely)"
- **Problem**: Treated as reference, not binding constraint

---

## 5. Theme & Visual System

### Global CSS (head-template.html - 352 lines)

All 19 template styles share the SAME global CSS foundation:

**CSS Variables (AI-populated per site)**:
```css
:root {
  --color-primary: <from AI>;
  --color-secondary: <from AI>;
  --color-accent: <from AI>;
  --color-bg: <from AI>;
  --color-bg-alt: <from AI>;
  --color-text: <from AI>;
  --color-text-muted: <from AI>;
  --font-heading: <from AI>;
  --font-body: <from AI>;
  --radius-sm/md/lg: <fixed>;
  --space-section: <fixed>;
  --max-width: <fixed>;
}
```

**Fixed Global Rules (identical for ALL sites)**:
- `.section-dark { background-color: var(--color-bg); }`
- `.section-light { background-color: var(--color-bg-alt); }`
- Section overlap: `margin-top: -4rem` on all sections
- Gradient bridge between sections (same gradient-to-bottom everywhere)
- Z-index stacking: identical across all styles

**Fallback Theme Pool (8 palettes)**:
When Kimi fails, falls back to 8 hardcoded palettes:
1. Purple + cream (#7C3AED)
2. Teal + light teal (#0D9488)
3. Red + yellow (#DC2626)
4. Green + pastel green (#059669)
5. Blue + light blue
6. Orange + cream
7. Indigo + lavender
8. Rose + pink

---

## 6. GSAP Animation Engine

### gsap-universal.js (v3.0, 29 effects)

**Scroll Entrance Effects**: fade-up, fade-down, fade-left, fade-right, scale-in, scale-up, rotate-in, flip-up, blur-in, slide-up, reveal-left/right/up/down, bounce-in, zoom-out

**Advanced Effects**: text-split (chars/words/lines), text-reveal, typewriter, clip-reveal, blur-slide, rotate-3d, stagger, stagger-scale

**Interactive Effects**: tilt, magnetic, card-hover-3d, float, gradient-flow, morph-bg, image-zoom, draw-svg, split-screen

**Utility**: data-counter, data-scroll-progress, marquee, horizontal-scroll, cursor-glow, nav-scroll

**Key Behaviors**:
- ALL sites get all 29 effects (no per-style customization)
- In iframe (editor preview): GSAP is disabled, all content shown immediately
- If GSAP fails to load: fallback shows all content with `opacity: 1`
- All `[data-animate]` elements start hidden (`opacity: 0; transform: translateY(20px)`)
- Same easing, same duration, same stagger timing across all styles

---

## 7. Template Selection Logic

### 8 Categories x 19 Styles

| Category | Styles |
|----------|--------|
| Restaurant (3) | restaurant-elegant, restaurant-cozy, restaurant-modern |
| SaaS (3) | saas-gradient, saas-clean, saas-dark |
| Portfolio (3) | portfolio-gallery, portfolio-minimal, portfolio-creative |
| E-commerce (2) | ecommerce-modern, ecommerce-luxury |
| Business (3) | business-corporate, business-trust, business-fresh |
| Blog (2) | blog-editorial, blog-dark |
| Event (2) | event-vibrant, event-minimal |
| Custom (1) | custom-free (uses ai_service.py fallback) |

### Selection Mechanism

**STYLE_VARIANT_MAP** (deterministic defaults, lines 865-1050):
```python
"restaurant-elegant": {
    "nav": "nav-classic-01",
    "hero": "hero-classic-01",
    "about": "about-magazine-01",
    "services": "services-alternating-rows-01",
    "gallery": "gallery-spotlight-01",
    "testimonials": "testimonials-spotlight-01",
    "contact": "contact-minimal-01",
    "footer": "footer-centered-01"
}
```

**STYLE_VARIANT_POOL** (randomization, lines 1058+):
```python
"saas-gradient": {
    "hero": ["hero-linear-01", "hero-gradient-03", "hero-animated-shapes-01",
             "hero-parallax-01", "hero-rotating-01"],  # 5 options
    "about": ["about-bento-01", "about-split-scroll-01"],  # 2 options
    ...
}
```

**_select_components_deterministic()**: Picks from POOL randomly; falls back to MAP defaults; falls back to _DEFAULT_SECTION_VARIANTS.

---

## 8. Audit: Why All Sites Look the Same

### Problem Summary

> "19 styles are 75-90% IDENTICAL structurally. Differences are colors/fonts only."

### Root Cause #1: Component Reuse (74% average)

Cross-industry component sharing destroys visual identity:

| Component | Used By (different industries) |
|-----------|-------------------------------|
| `nav-minimal-01` | 7 styles (37% of all sites) |
| `nav-classic-01` | 6 styles |
| `contact-modern-form-01` | 5 styles (SaaS, Business, Ecommerce, Restaurant, Event) |
| `about-alternating-01` | 4 styles (Portfolio, Blog, SaaS, Business) |
| `hero-classic-01` | 3 styles (Restaurant, Ecommerce, Business) |
| `footer-centered-01` | 5+ styles |

**Impact**: A restaurant and a SaaS product share the same navigation, contact form, and about section. Only hero and color differ.

### Root Cause #2: Nav Bottleneck (Only 3 Variants)

Navigation is the most persistent visible element, and there are ONLY 3 options:
- `nav-classic-01` — used in 6 styles
- `nav-minimal-01` — used in 7 styles
- `nav-centered-01` — used in 5 styles

Every generated site starts with one of just 3 navigations.

### Root Cause #3: Identical CSS Foundation

ALL components share the exact same structural DNA:

```css
/* Every section */
py-24 lg:py-32          /* Same vertical spacing */
max-w-7xl mx-auto px-6  /* Same max width + horizontal padding */
gap-8 lg:gap-4          /* Same gap patterns */
shadow-xl, shadow-2xl   /* Same shadow depths */
rounded-xl, rounded-2xl /* Same border radius */
```

Even when colors change and layouts change, the **spatial rhythm** is identical:
- Same section height
- Same content width
- Same card spacing
- Same shadow depth
- Same corner radius
- Same responsive breakpoints

### Root Cause #4: template_style_id Doesn't Influence Text Prompts

The template style (e.g., "restaurant-elegant" vs "restaurant-cozy") only affects:
- **Component selection** (Step 3) — different layout variants
- **Category few-shot examples** (Step 2) — but same category = same examples

It does NOT affect:
- The personality directive (random, not style-matched)
- The color mood (random, not style-matched)
- The copywriting tone (same for all styles in a category)

"restaurant-elegant" and "restaurant-cozy" get the SAME text prompt with the SAME personality pool.

### Root Cause #5: AI Convergence

Even with 12 personalities x 12 moods x 17 fonts = 2,448 combinations:
- AI follows mood hints too literally (temp 0.75 isn't enough)
- Business description limited to 800 chars — not enough context
- Personality is ONE line applied to entire site
- No instruction to mix personalities or reorder sections
- ChromaDB context truncated and treated as reference, not constraint

### Root Cause #6: Uniform Animations

All 19 styles get the exact same GSAP effects:
- Same fade-up entrance timing
- Same text-split animation
- Same stagger delays
- Same easing curves
- No per-style animation profiles (fast for SaaS, slow for luxury, etc.)

### Root Cause #7: Section Alternation is Uniform

Every site alternates between just 2 backgrounds:
```
section-dark (--color-bg) → gradient bridge → section-light (--color-bg-alt) → gradient bridge → ...
```
No site has: full-width images, colored section backgrounds, pattern overlays, or section shapes.

### Quantitative Impact

| Layer | Variety Potential | Actual Variety | Why |
|-------|------------------|----------------|-----|
| Colors | 12 moods + AI = high | Medium | AI converges + 8 fallback palettes reused |
| Fonts | 17 pairs = good | Medium | Some pairs too similar |
| Hero layout | 18 variants = great | Good | Best layer of variety |
| Nav layout | 3 variants = poor | **Very Low** | Biggest bottleneck |
| About layout | 8 variants, but pools of 2-3 | Low | `about-alternating-01` in 4 categories |
| Services layout | 9 variants | Medium | `services-cards-grid-01` in 5+ styles |
| Footer layout | 6 variants | Low | `footer-centered-01` dominates |
| Spacing/shadow | Fixed across all | **None** | All Tailwind classes identical |
| Animations | Same 29 effects | **None** | No per-style profiles |
| Text content | 12 personalities | Low-Medium | Structural repetition, style not in prompt |

---

## 9. Recommended Fixes

### Priority 1: Structural Diversity (Highest Impact)

#### 1a. Add Per-Style CSS Overrides
Create style-specific CSS variables that modify the visual rhythm:

```css
/* In head-template.html, injected based on template_style_id */
.style-restaurant-elegant {
  --space-section: 8rem;      /* Generous, luxurious */
  --radius-card: 1rem;        /* Softer curves */
  --shadow-card: 0 25px 50px rgba(0,0,0,0.12); /* Deep, soft */
  --text-scale: 1.1;          /* Larger type */
  --animation-speed: 1.2;     /* Slower, elegant */
}
.style-saas-dark {
  --space-section: 5rem;      /* Tight, efficient */
  --radius-card: 0.5rem;      /* Sharp corners */
  --shadow-card: 0 4px 6px rgba(0,0,0,0.4); /* Subtle, dark */
  --text-scale: 0.95;         /* Compact */
  --animation-speed: 0.7;     /* Snappy, fast */
}
```

#### 1b. Expand Navigation Variants (3 → 10+)
Add: sticky-transparent, center-logo, mega-menu, hamburger-only, side-drawer, split-nav, floating-bar, breadcrumb-nav, tab-nav, command-palette

#### 1c. Expand Footer Variants (6 → 12+)
Add: mega-footer, minimal-line, social-focused, newsletter-centric, sitemap-grid, animated-footer

### Priority 2: AI Prompt Improvements (High Impact)

#### 2a. Style-to-Tone Mapping
Map each template_style_id to specific copywriting directives:

```python
STYLE_TONE_MAP = {
    "restaurant-elegant": "Use formal Italian, refined adjectives, aristocratic metaphors. Evoke exclusivity.",
    "restaurant-cozy": "Use warm, familiar language. Evoke home, family, comfort. Short, intimate sentences.",
    "restaurant-modern": "Use clean, innovative language. Short punchy lines. Tech-food fusion vocabulary.",
    "saas-gradient": "Bold claims, data-driven. 'Transform X in Y minutes' style. Silicon Valley energy.",
    "saas-clean": "Understated confidence. Let the product speak. Minimal copy, maximum clarity.",
    ...
}
```

#### 2b. Personality Blending
Instead of picking ONE personality, blend 2:
```python
# Current: random.choice(PERSONALITY_POOL) → ONE
# Proposed: Pick 2, set ratio
primary = random.choice(PERSONALITY_POOL)
secondary = random.choice([p for p in PERSONALITY_POOL if p != primary])
directive = f"Be 70% {primary['name']} and 30% {secondary['name']}"
```

#### 2c. Increase Business Description Limit
800 chars → 2000 chars. More context = more unique output.

#### 2d. Section Reordering
Add a directive: "For this style, consider leading with [testimonials/stats/about] instead of the standard hero→about→services flow."

### Priority 3: Animation Differentiation (Medium Impact)

#### 3a. Per-Style Animation Profiles
```javascript
const STYLE_ANIMATION_PROFILES = {
  "restaurant-elegant": { speed: 1.3, ease: "power2.out", staggerGap: 0.15 },
  "saas-dark":          { speed: 0.6, ease: "power3.out", staggerGap: 0.05 },
  "portfolio-minimal":  { speed: 1.0, ease: "sine.out",   staggerGap: 0.1  },
  "event-vibrant":      { speed: 0.5, ease: "back.out",   staggerGap: 0.03 },
};
```

#### 3b. Stagger Randomization (Already in TODO)
Add `Math.random() * 0.1` offset to stagger delays for organic feel.

### Priority 4: Color & Visual Polish (Lower Impact)

#### 4a. Section Background Variety
Instead of just section-dark/section-light alternation:
- Full-width image backgrounds (with overlay)
- Gradient sections (not just between sections)
- Pattern/texture overlays (subtle grids, dots)
- Colored accent sections using --color-primary at 10% opacity

#### 4b. Typography Scale Per Style
```css
.style-saas-gradient h1 { font-size: clamp(3rem, 8vw, 7rem); }     /* Large, bold */
.style-portfolio-minimal h1 { font-size: clamp(2rem, 4vw, 3.5rem); } /* Controlled */
.style-event-vibrant h1 { font-size: clamp(4rem, 10vw, 9rem); }     /* Oversized */
```

#### 4c. Expand Fallback Theme Pool
8 → 16 palettes. Add rotation tracking so consecutive users don't get the same fallback.

### Priority 5: Component Pool Expansion (Ongoing)

| Section | Current Variants | Target | Gap |
|---------|-----------------|--------|-----|
| Nav | 3 | 10+ | +7 |
| Footer | 6 | 12 | +6 |
| About | 8 (but pools of 2-3) | Pools of 5+ | Expand pools |
| FAQ | 4 (2 in pools) | 4 in pools | Expand pools |
| Contact | 6 | 10 | +4 |

---

## Architecture Diagram: Where Sameness Originates

```
┌────────────────────────────────────────────────────────────────────┐
│                    WHAT CHANGES PER SITE                           │
│                                                                    │
│  ┌──────────┐  ┌──────────┐  ┌───────────────┐  ┌──────────────┐ │
│  │ Colors   │  │ Fonts    │  │ Hero Layout   │  │ Text Content │ │
│  │ (12mood) │  │ (17pair) │  │ (18 variants) │  │ (12 person.) │ │
│  └──────────┘  └──────────┘  └───────────────┘  └──────────────┘ │
│         GOOD         GOOD         GOOD              MEDIUM        │
└────────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────────┐
│                    WHAT STAYS THE SAME (PROBLEM)                   │
│                                                                    │
│  ┌──────────┐  ┌──────────┐  ┌───────────────┐  ┌──────────────┐ │
│  │ Spacing  │  │ Shadows  │  │ Nav (3 only)  │  │ Animations   │ │
│  │ py-24    │  │ shadow-xl│  │ footer (6)    │  │ (same 29     │ │
│  │ max-7xl  │  │ fixed    │  │ contact (6)   │  │  for all)    │ │
│  └──────────┘  └──────────┘  └───────────────┘  └──────────────┘ │
│                                                                    │
│  ┌──────────┐  ┌──────────┐  ┌───────────────┐                   │
│  │ Section  │  │ Border   │  │ Style doesn't │                   │
│  │ bg alter │  │ radius   │  │ affect text   │                   │
│  │ dark/lgt │  │ fixed    │  │ prompts       │                   │
│  └──────────┘  └──────────┘  └───────────────┘                   │
│       ALL IDENTICAL ACROSS 19 STYLES                               │
└────────────────────────────────────────────────────────────────────┘
```

---

## Quick Reference: Code Locations

| What | File | Lines |
|------|------|-------|
| STYLE_VARIANT_MAP | `databinding_generator.py` | ~865-1050 |
| STYLE_VARIANT_POOL | `databinding_generator.py` | ~1058-1200 |
| PERSONALITY_POOL | `databinding_generator.py` | ~80-141 |
| COLOR_MOOD_POOL | `databinding_generator.py` | ~144-157 |
| FONT_PAIRING_POOL | `databinding_generator.py` | ~160-177 |
| Theme prompt | `databinding_generator.py` | ~2085-2155 |
| Text prompt | `databinding_generator.py` | ~2347-2413 |
| Variety context pick | `databinding_generator.py` | ~240-246 |
| Component selection | `databinding_generator.py` | ~2589-2662 |
| Global CSS | `head-template.html` | 1-352 |
| GSAP engine | `gsap-universal.js` | Full file |
| Component registry | `components.json` | Full file |
| FALLBACK_THEME_POOL | `databinding_generator.py` | ~180-237 |
| _DEFAULT_SECTION_VARIANTS | `databinding_generator.py` | Before STYLE_VARIANT_MAP |
