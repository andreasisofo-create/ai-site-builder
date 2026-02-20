"""
Site Quality Guide - Expert knowledge base for AI site planning.

This module provides structured best practices from web design experts.
The AI planner consults this when planning websites to ensure professional
quality across layout, content, UX, and visual coherence.

Usage:
    guide = SiteQualityGuide()
    rules = guide.get_rules_for_category("restaurant")
    prompt = guide.get_planning_prompt("restaurant", ["hero", "about", "services", "contact"])
    score, issues = guide.evaluate_plan(plan_dict)
"""

from typing import Dict, Any, List, Optional, Tuple


class SiteQualityGuide:
    """Expert site quality knowledge for AI planning prompts."""

    # =================================================================
    # 1. LAYOUT RULES
    # =================================================================
    LAYOUT_RULES: Dict[str, Any] = {
        "hero_section": {
            "height": "Full viewport (100vh) on desktop, 70-85vh on mobile",
            "cta_position": "Above the fold, visible without scrolling",
            "contrast": "Text over image must have min 4.5:1 WCAG AA contrast ratio",
            "content_limit": "Headline + subtitle + 1-2 CTAs. No clutter.",
            "image_treatment": "Full-bleed background or split layout. Always overlay for readability.",
        },
        "section_rhythm": {
            "background_alternation": "Alternate light/dark or white/tinted backgrounds between sections",
            "pattern": "heavy (hero) -> light (about) -> medium (services) -> light (testimonials) -> heavy (cta) -> light (contact)",
            "visual_breaks": "Use background color changes, not dividers, to separate sections",
            "avoid": "Never stack 3+ sections with identical white backgrounds",
        },
        "visual_weight": {
            "distribution": "Heavy -> Light -> Heavy -> Light pattern creates natural reading flow",
            "heavy_sections": "Hero, CTA, Gallery (full-bleed images, dark backgrounds, large type)",
            "light_sections": "About, Contact, FAQ (white/cream backgrounds, standard type)",
            "medium_sections": "Services, Testimonials, Team (cards, grid layouts, moderate density)",
        },
        "whitespace": {
            "section_padding": "Minimum 80px top/bottom between sections (py-20), 120px preferred for breathing room",
            "inner_spacing": "32-48px between elements within a section",
            "card_gaps": "24-32px gap in card grids",
            "text_margins": "Paragraphs: margin-bottom 1.5em. Headings: margin-bottom 0.75em.",
            "mobile_reduction": "Reduce section padding to 48-64px on mobile",
        },
        "content_width": {
            "text_content": "Max 1280px container for text sections, 65ch max-width for paragraph blocks",
            "full_width": "Hero backgrounds, gallery sections, CTA backgrounds extend full viewport width",
            "cards_grid": "Max 1280px container, 3 columns desktop, 2 tablet, 1 mobile",
            "narrow_content": "Testimonial quotes, about text: max 800px centered for optimal readability",
        },
        "mobile_layout": {
            "stack_order": "All multi-column layouts stack vertically on mobile",
            "image_priority": "Image after text on mobile (text-first for conversion)",
            "cta_visibility": "Primary CTA sticky at bottom on mobile if form-based",
            "font_scaling": "H1: 32-40px mobile (vs 48-72px desktop). Body: 16px minimum always.",
        },
    }

    # =================================================================
    # 2. CONTENT HIERARCHY per section type
    # =================================================================
    CONTENT_HIERARCHY: Dict[str, Dict[str, Any]] = {
        "hero": {
            "hierarchy": ["headline", "subtitle", "cta_primary", "cta_secondary", "background_image"],
            "headline_max_words": 8,
            "subtitle_max_lines": 3,
            "cta_count": "1 primary + 1 optional secondary",
            "rules": [
                "Headline must communicate WHO you are and WHAT you do",
                "Subtitle expands with specific value proposition or differentiator",
                "Primary CTA uses action verb + benefit (e.g., 'Prenota il tuo Tavolo')",
                "Secondary CTA is exploratory (e.g., 'Scopri i Servizi')",
                "Background image or illustration must reinforce the message, not distract",
            ],
        },
        "about": {
            "hierarchy": ["section_title", "story_paragraph", "key_values", "team_photo"],
            "paragraph_limit": 3,
            "rules": [
                "Story-first: lead with founding story or mission, not generic description",
                "Show personality: include a real photo of team, space, or founder",
                "Max 3 short paragraphs or 1 paragraph + 3 value bullets",
                "Include concrete details: year founded, number served, specific expertise",
                "Avoid generic phrases: 'siamo un team di professionisti', 'azienda leader'",
            ],
        },
        "services": {
            "hierarchy": ["section_title", "section_subtitle", "service_cards"],
            "max_visible_items": 6,
            "card_structure": ["icon_or_image", "title", "short_description"],
            "rules": [
                "Max 6 services visible at once (3-6 sweet spot for visual balance)",
                "Each service needs: icon/image + title (3-5 words) + description (1-2 lines)",
                "Lead with benefit, not feature name",
                "Use consistent card design: all with icons OR all with images, never mixed",
                "If more than 6 services, use tabs or accordion to organize",
            ],
        },
        "testimonials": {
            "hierarchy": ["section_title", "testimonial_cards"],
            "min_testimonials": 3,
            "card_structure": ["quote_text", "person_name", "person_role", "person_photo"],
            "rules": [
                "Minimum 3 testimonials for credibility (2 looks sparse, 1 looks fake)",
                "Each testimonial: name + role/company + photo + quote",
                "Quotes should be specific about results, not generic praise",
                "Mix different types of clients/outcomes for breadth",
                "Star ratings add visual credibility if available",
            ],
        },
        "contact": {
            "hierarchy": ["section_title", "contact_form", "address_info", "map"],
            "form_fields": ["name", "email", "message"],
            "optional_fields": ["phone", "subject", "company"],
            "rules": [
                "Core form: name + email + message (3 fields minimum)",
                "Phone field optional but include clickable phone number nearby",
                "Always show physical address if applicable",
                "Map integration adds trust (even static image of location)",
                "Include business hours if relevant",
                "Max 5-6 form fields total; more fields = lower conversion",
            ],
        },
        "footer": {
            "hierarchy": ["logo", "nav_links", "contact_info", "social_links", "copyright"],
            "rules": [
                "Logo or business name anchors the footer",
                "Navigation: repeat main nav links for accessibility",
                "Contact: address, phone, email (all clickable)",
                "Social: icon links to active profiles only",
                "Copyright line with current year",
                "Legal links: Privacy Policy, Cookie Policy if applicable",
            ],
        },
        "gallery": {
            "hierarchy": ["section_title", "gallery_grid"],
            "min_images": 4,
            "max_images": 12,
            "rules": [
                "Minimum 4 images (less looks incomplete), maximum 12 (more overwhelms)",
                "Consistent aspect ratios within the grid",
                "Hover effect on each image (zoom, overlay with title, or lightbox)",
                "Lazy loading mandatory for performance",
                "Alt text on every image for accessibility",
            ],
        },
        "pricing": {
            "hierarchy": ["section_title", "pricing_cards", "faq_or_note"],
            "recommended_tiers": 3,
            "rules": [
                "3 tiers is optimal (basic/pro/enterprise pattern)",
                "Highlight the recommended plan with visual prominence (border, badge, scale)",
                "Show prices clearly; hidden pricing kills trust",
                "Feature comparison list under each plan",
                "CTA button on each pricing card",
                "Annual vs monthly toggle if applicable",
            ],
        },
        "faq": {
            "hierarchy": ["section_title", "accordion_items"],
            "min_items": 4,
            "max_items": 10,
            "rules": [
                "4-10 questions is the sweet spot",
                "Questions in natural language (how customers actually ask)",
                "Answers concise: 2-4 sentences max",
                "Accordion UI for clean layout",
                "Group by topic if more than 6 questions",
            ],
        },
        "team": {
            "hierarchy": ["section_title", "team_cards"],
            "card_structure": ["photo", "name", "role", "short_bio_or_social"],
            "rules": [
                "Professional but approachable photos",
                "Name + role + optional 1-line bio or social links",
                "Grid: 3-4 per row desktop, 2 tablet, 1 mobile",
                "Consistent photo treatment: all same crop, filter, background",
                "Hover effect: social links appear or bio expands",
            ],
        },
        "stats": {
            "hierarchy": ["stat_numbers"],
            "min_stats": 3,
            "max_stats": 4,
            "rules": [
                "3-4 stats is ideal (years, clients, projects, satisfaction %)",
                "Each stat: large animated number + short label",
                "Use counter animation (data-counter) for engagement",
                "Place between content-heavy sections as a visual break",
                "Numbers must be specific and credible, not obviously inflated",
            ],
        },
        "cta": {
            "hierarchy": ["headline", "subtitle", "cta_button"],
            "rules": [
                "Clear action-oriented headline",
                "Contrasting background (dark on light sites, gradient, or accent color)",
                "Single prominent CTA button",
                "Optionally add urgency or benefit: 'Consulenza gratuita', 'Risposta in 24h'",
                "Position: before footer as the final push to convert",
            ],
        },
    }

    # =================================================================
    # 3. CATEGORY-SPECIFIC RULES
    # =================================================================
    CATEGORY_SPECIFIC_RULES: Dict[str, Dict[str, Any]] = {
        "restaurant": {
            "must_have_sections": ["hero", "about", "services", "gallery", "contact", "footer"],
            "recommended_sections": ["testimonials", "stats", "cta"],
            "tone_of_voice": "Evocative, sensory, warm. Use food-related adjectives: fragrante, croccante, vellutato. Tell the story of the place.",
            "color_schemes": [
                "Elegant: black + gold + cream (#1A1A2E, #D4AF37, #FAF7F2)",
                "Casual: olive green + warm orange + ivory (#556B2F, #E8751A, #FFFDF7)",
                "Modern: deep navy + white + coral accent (#0A1628, #FAFAFA, #FF6B6B)",
            ],
            "font_style": "Heading: serif with character (Playfair Display, DM Serif Display). Body: clean sans-serif (Inter, DM Sans). Optional: calligraphic accent for specials.",
            "photo_requirements": "Hero: signature dish or dining room. Gallery: 60% food, 20% interior, 10% details, 10% chef. Warm lighting, never cold/blue tones.",
            "specific_rules": [
                "Menu/specialties section is mandatory - show what you serve",
                "Reservation CTA must be above the fold",
                "Include opening hours prominently",
                "Phone number must be clickable (tel: link)",
                "Never use cold colors (blue, grey) as primary - restaurants need warmth",
            ],
        },
        "saas": {
            "must_have_sections": ["hero", "services", "features", "testimonials", "cta", "footer"],
            "recommended_sections": ["pricing", "faq", "stats", "logos"],
            "tone_of_voice": "Clear, benefit-driven, confident. Lead with results and numbers. Avoid jargon. Action verbs over descriptions.",
            "color_schemes": [
                "Dark premium: navy + purple + cyan (#0F172A, #7C3AED, #22D3EE)",
                "Clean light: white + blue + pale grey (#FAFAFA, #3B82F6, #F1F5F9)",
                "Neon dark: black + green neon + grey (#09090B, #22C55E, #27272A)",
            ],
            "font_style": "Heading: geometric bold (Space Grotesk 700-800, Sora, Unbounded). Body: clean sans-serif (Inter, DM Sans). Stats: mono or tabular nums.",
            "photo_requirements": "Product screenshots with rounded corners and shadow. UI mockups on device frames. Lucide/Heroicons for features. No stock photography of offices.",
            "specific_rules": [
                "Product screenshot or mockup in hero is mandatory",
                "Social proof (logos, user count) right after hero",
                "Features must show benefits, not technical specs",
                "Pricing transparency builds trust - show it",
                "CTA text: action verb + free/benefit ('Inizia Gratis', 'Prova 14 giorni')",
                "Include trust badges: 'Nessuna carta richiesta', 'Setup in 2 minuti'",
            ],
        },
        "portfolio": {
            "must_have_sections": ["hero", "gallery", "about", "contact", "footer"],
            "recommended_sections": ["services", "testimonials"],
            "tone_of_voice": "Confident, concise, personality-forward. Let the work speak. Minimal but impactful copy.",
            "color_schemes": [
                "Minimal B&W: black + white + single vivid accent (#0D0D0D, #FAFAFA, #FF3366)",
                "Creative bold: dark purple + magenta + yellow (#1A1A2E, #E94560, #FDCB6E)",
                "Warm neutral: off-white + charcoal + terracotta (#F5F0EB, #2D3436, #CC5A47)",
            ],
            "font_style": "Heading: strong personality (Space Grotesk 800-900, Playfair Display). Body: minimal readable (Inter 16px, DM Sans). Hero name: oversized 72-120px.",
            "photo_requirements": "Projects ARE the photos. Realistic mockups for web/app work. Full-bleed for branding. Hover: subtle zoom + overlay. Consistent aspect ratios.",
            "specific_rules": [
                "Quality over quantity: max 8-12 selected projects",
                "The design must be a frame, not compete with the work",
                "Generous whitespace is mandatory - less is more",
                "Each project: image + title + category + 1-line description",
                "Contact section must be clear and easy to find",
                "Custom cursor effect is a strong differentiator for creative portfolios",
            ],
        },
        "ecommerce": {
            "must_have_sections": ["hero", "services", "gallery", "testimonials", "contact", "footer"],
            "recommended_sections": ["stats", "cta", "faq"],
            "tone_of_voice": "Persuasive, benefit-focused, urgency-appropriate. Specific product details. Trust-building language.",
            "color_schemes": [
                "Luxury: black + gold + white (#0A0A0A, #C9A96E, #FFFFFF)",
                "Modern clean: white + black + green CTA (#FFFFFF, #111111, #22C55E)",
                "Fashion: beige + black + terracotta (#F5F0EB, #1A1A1A, #C67D5B)",
            ],
            "font_style": "Heading: modern clean (Plus Jakarta Sans 700, Sora). Body: maximum readability (Inter 16px). Prices: bold 24-32px. Badges: 10-12px uppercase.",
            "photo_requirements": "Product photos on white/neutral background. Consistent lighting across all products. Multiple angles. Lifestyle context shots. Zoom on hover.",
            "specific_rules": [
                "Price must always be visible and prominent",
                "'Add to cart' CTA must use the most vivid color in the palette",
                "Trust signals mandatory: shipping, returns, secure payment icons",
                "Product grid: consistent card sizes, hover reveals quick-view",
                "Discount badges: red/orange for urgency",
                "Include social proof: reviews with stars, customer count",
            ],
        },
        "business": {
            "must_have_sections": ["hero", "services", "about", "contact", "footer"],
            "recommended_sections": ["testimonials", "stats", "team", "faq", "cta"],
            "tone_of_voice": "Professional but human. Specific results over vague claims. Credibility through numbers and testimonials.",
            "color_schemes": [
                "Trust classic: navy + white + orange accent (#1E3A5F, #FAFAFA, #F97316)",
                "Modern fresh: teal + cream + black + lime (#0F766E, #FAF7F2, #1A1A2E, #84CC16)",
                "Premium: black + grey + gold (#0A0A0A, #4B5563, #D4AF37)",
            ],
            "font_style": "Heading: authoritative modern (Plus Jakarta Sans 700-800, Space Grotesk). Body: professional readable (Inter, DM Sans 16px). Stats: bold 48-64px accent color.",
            "photo_requirements": "Team photos: professional but natural. Office/workspace: real, not stock. Client logos: greyscale grid. Case studies: screenshots, graphs, before/after.",
            "specific_rules": [
                "Hero must state WHAT you do + FOR WHOM in 1 line",
                "Stats section is highly recommended (years, clients, projects)",
                "Services: describe benefits, not just features",
                "Include a clear 'request consultation' or 'contact us' CTA",
                "Testimonials with full name + role + company for credibility",
                "FAQ section reduces support load and builds trust",
            ],
        },
        "blog": {
            "must_have_sections": ["hero", "about", "gallery", "contact", "footer"],
            "recommended_sections": ["services", "cta"],
            "tone_of_voice": "Informative, engaging, authoritative. Clear headlines that promise value. Concise excerpts that hook the reader.",
            "color_schemes": [
                "Editorial classic: white + black + red accent (#FFFFFF, #111111, #E63946)",
                "Dark reader: black + dark grey + blue accent (#0D1117, #21262D, #58A6FF)",
                "Minimal warm: cream + charcoal + teal (#FAF7F2, #374151, #0D9488)",
            ],
            "font_style": "Heading: editorial serif (Playfair Display, DM Serif Display). Body: high readability serif or sans (Source Serif 4 or Inter 18px). Category labels: 12px uppercase sans.",
            "photo_requirements": "Article covers: 16:9 high quality, relevant to content. Author avatar: 48px circle. Inline images: max content width with captions. All with descriptive alt text.",
            "specific_rules": [
                "Reading experience is paramount - optimize for readability",
                "Article body: 18-20px, line-height 1.8, max-width 680px",
                "Featured post in hero section with large cover image",
                "Show author + date + reading time on every article card",
                "Newsletter signup must be prominent but not aggressive",
                "Minimal animations - content is king, design is the frame",
            ],
        },
        "event": {
            "must_have_sections": ["hero", "about", "services", "team", "contact", "footer"],
            "recommended_sections": ["schedule", "pricing", "faq", "cta", "stats", "gallery"],
            "tone_of_voice": "Exciting, urgent, exclusive. Create FOMO. Date and location must be instantly visible.",
            "color_schemes": [
                "Tech conference: dark + purple + cyan (#0A0A1A, #7C3AED, #06B6D4)",
                "Music festival: black + neon pink + gold (#000000, #FF2D87, #FFD700)",
                "Corporate event: navy + white + orange (#1E3A5F, #FFFFFF, #FB923C)",
            ],
            "font_style": "Heading: display impact (Unbounded 800-900, Space Grotesk 800). Body: clean readable (Inter, DM Sans 16px). Countdown: mono/tabular 48-72px. Event name: 56-80px.",
            "photo_requirements": "Hero: previous edition crowd/stage energy or bold gradient. Speaker: professional square photos. Gallery: previous events. Venue: location exterior + interior.",
            "specific_rules": [
                "Date + location must be visible within 1 second of landing",
                "Countdown timer in hero creates urgency",
                "Speaker/performer section with photos is mandatory for credibility",
                "Schedule/program should be navigable (tabs per day/track)",
                "Ticket pricing must be transparent - hidden prices = lost attendees",
                "Early bird or limited availability messaging drives conversions",
                "Include logistics FAQ: parking, dress code, accessibility",
            ],
        },
        "custom": {
            "must_have_sections": ["hero", "about", "services", "contact", "footer"],
            "recommended_sections": ["testimonials", "gallery", "cta", "stats"],
            "tone_of_voice": "Adapt to the business personality. Specific > generic. Benefits > features. Stories > corporate-speak.",
            "color_schemes": [
                "Warm/welcoming: amber, terracotta, cream tones",
                "Cool/professional: navy, grey, white with vivid accent",
                "Energetic/young: purple, pink, gradient neon",
                "Elegant/luxury: black, gold, champagne",
                "Natural/eco: green, beige, earth tones",
            ],
            "font_style": "Heading: font with personality, weight 700+. Body: readable sans-serif, 16-18px. Never same font for heading and body.",
            "photo_requirements": "Real business photos over stock. Consistent style/filter across all images. Optimized for web (WebP, max 400KB). Lazy loading for galleries.",
            "specific_rules": [
                "Hero must communicate WHO + WHAT + WHY in 3 seconds",
                "At least one form of social proof (testimonials, client logos, stats)",
                "CTA visible above the fold and repeated 3+ times through the page",
                "Contact information must be easily accessible",
                "Mobile experience must be flawless",
            ],
        },
    }

    # =================================================================
    # 4. UX PATTERNS
    # =================================================================
    UX_PATTERNS: Dict[str, Dict[str, Any]] = {
        "navigation": {
            "behavior": "Sticky on scroll with background transition (transparent -> solid)",
            "max_links": 6,
            "mobile": "Hamburger menu with slide-in overlay",
            "cta_in_nav": "Primary CTA button at the right end of the navbar",
            "active_state": "Highlight current section on scroll (scroll-spy)",
            "rules": [
                "Logo always links to top of page",
                "Max 6 navigation links (more creates decision paralysis)",
                "CTA button in navbar should match the site's primary action",
                "On mobile: hamburger icon, full-screen or slide-in menu",
                "Smooth scroll to sections with URL hash anchors",
            ],
        },
        "cta_placement": {
            "primary_above_fold": "Main CTA must be visible without scrolling",
            "section_ctas": "Repeat CTA at the end of services, testimonials, and before footer",
            "final_cta": "Dedicated CTA section before footer as last conversion push",
            "mobile_sticky": "Consider sticky bottom CTA on mobile for high-intent pages",
            "rules": [
                "Primary action above the fold (hero section)",
                "Secondary actions within relevant sections",
                "Final CTA section before footer wraps up the conversion funnel",
                "Button text: verb + benefit, never just 'Click here' or 'Submit'",
                "Color: most contrasting color in the palette for maximum visibility",
            ],
        },
        "forms": {
            "max_fields": 5,
            "required_fields": ["name", "email", "message"],
            "validation": "Inline validation with clear error messages",
            "submit_feedback": "Success state with confirmation message, disable button during submission",
            "rules": [
                "3-5 fields maximum for conversion-focused forms",
                "Clear labels above each field (not just placeholders)",
                "Inline validation on blur, not on submit",
                "Submit button: descriptive text ('Invia Richiesta', not 'Submit')",
                "Success feedback: green confirmation message or redirect",
                "Phone field: optional, with tel: link as alternative",
            ],
        },
        "loading_and_performance": {
            "images": "Lazy loading for all images below the fold",
            "hero_image": "Preload hero image for instant display",
            "skeleton": "Skeleton screens during content load",
            "progressive_reveal": "Sections animate in on scroll (not all at once)",
            "rules": [
                "Hero image preloaded (not lazy loaded)",
                "All other images use lazy loading with blur-up placeholders",
                "Web fonts: display swap to prevent invisible text flash",
                "Critical CSS inlined, non-critical deferred",
                "Target: First Contentful Paint under 2 seconds",
            ],
        },
        "mobile_ux": {
            "tap_targets": "Minimum 44px touch target size for all interactive elements",
            "thumb_zone": "Critical actions in bottom 60% of screen (thumb-reachable)",
            "galleries": "Swipeable with snap points, not just scrollable",
            "text_size": "16px minimum body text (prevents iOS zoom on focus)",
            "rules": [
                "All buttons and links: minimum 44x44px tap target",
                "No horizontal scroll on any viewport (common bug to check)",
                "Phone numbers: always clickable with tel: protocol",
                "Forms: proper input types (email, tel, url) for mobile keyboards",
                "Galleries: swipeable with pagination dots or arrows",
                "Sticky CTAs: bottom-fixed bar for primary action on mobile",
            ],
        },
        "accessibility": {
            "contrast": "WCAG AA minimum: 4.5:1 for normal text, 3:1 for large text",
            "focus": "Visible focus indicators on all interactive elements",
            "alt_text": "Descriptive alt text on all images",
            "semantic_html": "Proper heading hierarchy (h1 > h2 > h3), landmark roles",
            "rules": [
                "Color contrast meets WCAG AA (4.5:1 normal, 3:1 large text)",
                "All images have descriptive alt text",
                "Keyboard navigation works for all interactive elements",
                "Focus states are visible (never outline: none without replacement)",
                "Heading hierarchy is logical (one h1, h2s for sections, h3s for subsections)",
                "Form fields have associated labels",
            ],
        },
    }

    # =================================================================
    # 5. VISUAL COHERENCE RULES
    # =================================================================
    VISUAL_COHERENCE_RULES: Dict[str, Dict[str, str]] = {
        "color": {
            "max_palette": "3 main colors + 1-2 neutrals (black/white/grey). Max 5 total.",
            "accent_usage": "Accent color ONLY for CTAs, links, and key highlights. Not backgrounds.",
            "consistency": "Same color for the same role everywhere (all CTAs same color, all links same color).",
            "dark_sections": "Dark backgrounds use light text. Light backgrounds use dark text. Never reversed.",
            "gradient_rule": "If using gradients, stick to one gradient direction and palette. Not random per section.",
        },
        "typography": {
            "max_families": "Exactly 2 font families: one for headings, one for body. Never more.",
            "weight_hierarchy": "h1: 700-900, h2: 700, h3: 600, body: 400. Consistent throughout.",
            "size_scale": "Use a consistent type scale (e.g., 16, 20, 24, 32, 48, 64px).",
            "line_height": "Body: 1.6-1.8. Headings: 1.1-1.3. Consistent across sections.",
            "letter_spacing": "Headings: -0.02em to -0.03em. Body: normal. Uppercase labels: 0.05-0.1em.",
        },
        "spacing": {
            "grid_system": "Use 8px base grid. All spacing values should be multiples of 8.",
            "section_padding": "Same vertical padding for all sections of the same type.",
            "card_padding": "Same internal padding for all cards across the site.",
            "consistent_gaps": "Grid gaps the same everywhere cards appear.",
        },
        "border_radius": {
            "rule": "Choose ONE border-radius philosophy and stick to it everywhere.",
            "sharp": "0px - corporate, editorial, brutalist",
            "soft": "8-16px - modern, friendly, most business sites",
            "round": "24px+ or pill (99px) - playful, SaaS, casual",
            "never_mix": "Never mix sharp cards with round buttons or round cards with sharp inputs.",
        },
        "shadows": {
            "rule": "Choose ONE shadow intensity and apply consistently.",
            "none": "Flat design - separation through color/spacing only",
            "subtle": "shadow-sm to shadow-md - modern clean look",
            "prominent": "shadow-lg to shadow-xl - elevated card design",
            "consistency": "All cards same shadow level. All hover states same shadow increase.",
        },
        "animation": {
            "intensity": "Same animation intensity throughout the site. Not subtle then suddenly dramatic.",
            "timing": "Consistent duration (0.6-1s) and easing across all scroll animations.",
            "scroll_pattern": "Pick 2-3 animation types and use them consistently (e.g., fade-up for cards, text-split for headings, magnetic for CTAs).",
            "reduced_motion": "Always respect prefers-reduced-motion for accessibility.",
        },
    }

    # =================================================================
    # 6. QUALITY CHECKLIST
    # =================================================================
    QUALITY_CHECKLIST: List[Dict[str, str]] = [
        {"id": "no_placeholder_text", "check": "All placeholder text replaced with real content", "severity": "critical"},
        {"id": "all_images_alt", "check": "All images have descriptive alt text", "severity": "critical"},
        {"id": "links_work", "check": "All links work (use # anchors for same-page, real URLs for external)", "severity": "critical"},
        {"id": "wcag_contrast", "check": "Color contrast meets WCAG AA (4.5:1 text, 3:1 large text)", "severity": "critical"},
        {"id": "mobile_responsive", "check": "All sections display correctly on mobile (375px viewport)", "severity": "critical"},
        {"id": "no_horizontal_scroll", "check": "No unexpected horizontal scroll on any viewport width", "severity": "critical"},
        {"id": "cta_above_fold", "check": "Primary CTA visible above the fold without scrolling", "severity": "high"},
        {"id": "contact_info", "check": "Contact information present and accessible (phone, email, or form)", "severity": "high"},
        {"id": "footer_complete", "check": "Footer has: logo/name, nav links, contact info, social, copyright", "severity": "high"},
        {"id": "heading_hierarchy", "check": "Proper heading hierarchy (h1 > h2 > h3, only one h1)", "severity": "high"},
        {"id": "font_loading", "check": "Google Fonts loaded with display=swap to prevent FOIT", "severity": "medium"},
        {"id": "image_optimization", "check": "Images optimized (lazy loading, appropriate sizes, WebP where possible)", "severity": "medium"},
        {"id": "consistent_spacing", "check": "Consistent section padding and element spacing throughout", "severity": "medium"},
        {"id": "animation_coherence", "check": "Animations are consistent in style, timing, and intensity", "severity": "medium"},
        {"id": "color_consistency", "check": "Same colors used for same purposes throughout (CTAs, links, accents)", "severity": "medium"},
        {"id": "social_proof", "check": "At least one form of social proof present (testimonials, logos, stats)", "severity": "medium"},
        {"id": "nav_functional", "check": "Navigation links scroll to correct sections, mobile menu works", "severity": "high"},
        {"id": "form_validation", "check": "Contact form has proper validation and submit feedback", "severity": "medium"},
        {"id": "meta_complete", "check": "Page title, meta description, and favicon are set", "severity": "low"},
        {"id": "reduced_motion", "check": "Animations respect prefers-reduced-motion media query", "severity": "low"},
    ]

    # =================================================================
    # Section ordering rules
    # =================================================================
    SECTION_ORDER_RULES: Dict[str, Any] = {
        "fixed_positions": {
            "nav": "Always first (position 0)",
            "hero": "Always second (position 1, right after nav)",
            "footer": "Always last",
        },
        "recommended_flow": [
            "nav", "hero", "logos", "about", "services", "features",
            "gallery", "stats", "team", "process", "testimonials",
            "pricing", "faq", "schedule", "blog", "cta", "contact", "footer",
        ],
        "rules": [
            "Hero immediately after nav - never skip",
            "Social proof (logos, stats) works best right after hero or services",
            "Services/features before testimonials (show what you do, then prove it)",
            "CTA section before contact as final conversion push",
            "Contact always second-to-last (before footer)",
            "Footer always last",
            "Testimonials after services creates a 'claim then prove' pattern",
            "Stats can go after about (credibility boost) or after services",
        ],
    }

    # =================================================================
    # Methods
    # =================================================================

    def get_rules_for_category(self, category: str) -> Dict[str, Any]:
        """Return all relevant rules for a specific business category.

        Args:
            category: One of restaurant, saas, portfolio, ecommerce, business, blog, event, custom

        Returns:
            Dict with layout, content, ux, visual, category-specific rules, and checklist
        """
        category = category.lower().strip()

        # Map aliases
        alias_map = {
            "ristorante": "restaurant",
            "tech": "saas",
            "corporate": "business",
            "shop": "ecommerce",
            "creative": "portfolio",
            "evento": "event",
        }
        category = alias_map.get(category, category)

        if category not in self.CATEGORY_SPECIFIC_RULES:
            category = "custom"

        return {
            "category": category,
            "layout_rules": self.LAYOUT_RULES,
            "content_hierarchy": self.CONTENT_HIERARCHY,
            "category_rules": self.CATEGORY_SPECIFIC_RULES[category],
            "ux_patterns": self.UX_PATTERNS,
            "visual_coherence": self.VISUAL_COHERENCE_RULES,
            "section_order": self.SECTION_ORDER_RULES,
            "quality_checklist": self.QUALITY_CHECKLIST,
        }

    def get_planning_prompt(self, category: str, sections: List[str]) -> str:
        """Return a formatted prompt string for the AI planner.

        This is the main output method - generates a comprehensive prompt block
        that can be injected into the AI generation pipeline.

        Args:
            category: Business category (restaurant, saas, etc.)
            sections: List of section types the user selected (hero, about, services, etc.)

        Returns:
            Formatted string ready for prompt injection
        """
        category = category.lower().strip()
        alias_map = {
            "ristorante": "restaurant",
            "tech": "saas",
            "corporate": "business",
            "shop": "ecommerce",
            "creative": "portfolio",
            "evento": "event",
        }
        category = alias_map.get(category, category)
        if category not in self.CATEGORY_SPECIFIC_RULES:
            category = "custom"

        cat_rules = self.CATEGORY_SPECIFIC_RULES[category]

        lines: List[str] = []
        lines.append("=" * 60)
        lines.append("SITE QUALITY GUIDE - Expert Design Rules")
        lines.append("=" * 60)

        # Category overview
        lines.append(f"\n## Category: {category.upper()}")
        lines.append(f"Tone of voice: {cat_rules['tone_of_voice']}")
        lines.append(f"Font style: {cat_rules['font_style']}")
        lines.append(f"Photo requirements: {cat_rules['photo_requirements']}")

        # Color schemes
        lines.append("\n### Recommended Color Schemes:")
        for scheme in cat_rules["color_schemes"]:
            lines.append(f"  - {scheme}")

        # Category-specific rules
        lines.append("\n### Category-Specific Rules:")
        for rule in cat_rules["specific_rules"]:
            lines.append(f"  - {rule}")

        # Section-specific content rules
        lines.append("\n### Content Rules for Selected Sections:")
        for section in sections:
            section_lower = section.lower().strip()
            if section_lower in self.CONTENT_HIERARCHY:
                hierarchy = self.CONTENT_HIERARCHY[section_lower]
                lines.append(f"\n  [{section_lower.upper()}]")
                if "hierarchy" in hierarchy:
                    lines.append(f"  Content order: {' -> '.join(hierarchy['hierarchy'])}")
                for rule in hierarchy.get("rules", []):
                    lines.append(f"    - {rule}")

        # Section ordering
        lines.append("\n### Section Ordering:")
        for rule in self.SECTION_ORDER_RULES["rules"]:
            lines.append(f"  - {rule}")

        # Layout rules summary
        lines.append("\n### Layout Rules:")
        lines.append(f"  - Hero: {self.LAYOUT_RULES['hero_section']['height']}")
        lines.append(f"  - Section padding: {self.LAYOUT_RULES['whitespace']['section_padding']}")
        lines.append(f"  - Content width: {self.LAYOUT_RULES['content_width']['text_content']}")
        lines.append(f"  - Background rhythm: {self.LAYOUT_RULES['section_rhythm']['background_alternation']}")
        lines.append(f"  - Mobile font: {self.LAYOUT_RULES['mobile_layout']['font_scaling']}")

        # Visual coherence essentials
        lines.append("\n### Visual Coherence (MUST follow):")
        lines.append(f"  - Color: {self.VISUAL_COHERENCE_RULES['color']['max_palette']}")
        lines.append(f"  - Typography: {self.VISUAL_COHERENCE_RULES['typography']['max_families']}")
        lines.append(f"  - Spacing: {self.VISUAL_COHERENCE_RULES['spacing']['grid_system']}")
        lines.append(f"  - Border radius: {self.VISUAL_COHERENCE_RULES['border_radius']['rule']}")
        lines.append(f"  - Shadows: {self.VISUAL_COHERENCE_RULES['shadows']['rule']}")
        lines.append(f"  - Animation: {self.VISUAL_COHERENCE_RULES['animation']['intensity']}")

        # UX essentials
        lines.append("\n### UX Essentials:")
        lines.append(f"  - Navigation: {self.UX_PATTERNS['navigation']['behavior']}, max {self.UX_PATTERNS['navigation']['max_links']} links")
        lines.append(f"  - CTA placement: {self.UX_PATTERNS['cta_placement']['primary_above_fold']}")
        lines.append(f"  - Forms: {self.UX_PATTERNS['forms']['max_fields']} fields max")
        lines.append(f"  - Mobile: {self.UX_PATTERNS['mobile_ux']['tap_targets']}")
        lines.append(f"  - Accessibility: {self.UX_PATTERNS['accessibility']['contrast']}")

        # Critical quality checks
        lines.append("\n### Critical Quality Checks:")
        for item in self.QUALITY_CHECKLIST:
            if item["severity"] in ("critical", "high"):
                lines.append(f"  [{item['severity'].upper()}] {item['check']}")

        lines.append("\n" + "=" * 60)

        return "\n".join(lines)

    def evaluate_plan(self, plan_dict: Dict[str, Any]) -> Tuple[float, List[Dict[str, str]]]:
        """Score a site plan against quality rules.

        Args:
            plan_dict: The site plan dictionary. Expected keys:
                - category (str): Business category
                - sections (list): List of section type strings
                - colors (dict, optional): {primary, secondary, accent, background, text}
                - fonts (dict, optional): {heading, body}
                - content (dict, optional): Per-section content

        Returns:
            Tuple of (score: 0-100, issues: list of {severity, section, message})
        """
        issues: List[Dict[str, str]] = []
        max_score = 0
        earned_score = 0

        category = plan_dict.get("category", "custom").lower().strip()
        alias_map = {
            "ristorante": "restaurant", "tech": "saas", "corporate": "business",
            "shop": "ecommerce", "creative": "portfolio", "evento": "event",
        }
        category = alias_map.get(category, category)
        if category not in self.CATEGORY_SPECIFIC_RULES:
            category = "custom"

        cat_rules = self.CATEGORY_SPECIFIC_RULES[category]
        sections = [s.lower().strip() for s in plan_dict.get("sections", [])]

        # --- Check 1: Must-have sections (20 points) ---
        max_score += 20
        must_have = cat_rules.get("must_have_sections", [])
        missing_sections = [s for s in must_have if s not in sections]
        if not missing_sections:
            earned_score += 20
        else:
            penalty = min(20, len(missing_sections) * 5)
            earned_score += max(0, 20 - penalty)
            for s in missing_sections:
                issues.append({
                    "severity": "critical",
                    "section": s,
                    "message": f"Missing required section '{s}' for {category} category",
                })

        # --- Check 2: Section ordering (10 points) ---
        max_score += 10
        order_ok = True
        if sections:
            if sections[0] != "nav" and "nav" in sections:
                order_ok = False
                issues.append({"severity": "high", "section": "nav", "message": "Nav should be the first section"})
            if "hero" in sections:
                hero_idx = sections.index("hero")
                if hero_idx > 1:
                    order_ok = False
                    issues.append({"severity": "high", "section": "hero", "message": "Hero should be right after nav (position 0 or 1)"})
            if "footer" in sections and sections[-1] != "footer":
                order_ok = False
                issues.append({"severity": "high", "section": "footer", "message": "Footer should be the last section"})
            if "contact" in sections and "footer" in sections:
                contact_idx = sections.index("contact")
                footer_idx = sections.index("footer")
                if footer_idx - contact_idx > 2:
                    issues.append({"severity": "medium", "section": "contact", "message": "Contact section should be near the end, just before footer"})
        earned_score += 10 if order_ok else 5

        # --- Check 3: Hero section quality (15 points) ---
        max_score += 15
        content = plan_dict.get("content", {})
        hero_content = content.get("hero", {})
        hero_score = 15
        if hero_content:
            headline = hero_content.get("headline", hero_content.get("title", ""))
            if headline:
                word_count = len(headline.split())
                if word_count > 10:
                    hero_score -= 3
                    issues.append({"severity": "medium", "section": "hero", "message": f"Hero headline too long ({word_count} words). Aim for 6-8 words max."})
            else:
                hero_score -= 5
                issues.append({"severity": "critical", "section": "hero", "message": "Hero section missing headline"})

            cta = hero_content.get("cta_text", hero_content.get("cta", ""))
            if not cta:
                hero_score -= 5
                issues.append({"severity": "high", "section": "hero", "message": "Hero section missing CTA"})
        elif "hero" in sections:
            hero_score -= 5
            issues.append({"severity": "medium", "section": "hero", "message": "Hero section has no content defined"})
        earned_score += max(0, hero_score)

        # --- Check 4: Color palette (10 points) ---
        max_score += 10
        colors = plan_dict.get("colors", {})
        if colors:
            color_count = len([v for v in colors.values() if v and isinstance(v, str)])
            if color_count > 6:
                earned_score += 5
                issues.append({"severity": "medium", "section": "global", "message": f"Too many colors ({color_count}). Aim for 3 main + 1-2 neutrals."})
            elif color_count >= 3:
                earned_score += 10
            else:
                earned_score += 5
                issues.append({"severity": "medium", "section": "global", "message": "Color palette too limited. Need at least primary, secondary/background, and accent."})
        else:
            earned_score += 5  # No colors defined yet, neutral score

        # --- Check 5: Typography (10 points) ---
        max_score += 10
        fonts = plan_dict.get("fonts", {})
        if fonts:
            heading_font = fonts.get("heading", "")
            body_font = fonts.get("body", "")
            if heading_font and body_font:
                if heading_font.lower() == body_font.lower():
                    earned_score += 5
                    issues.append({"severity": "medium", "section": "global", "message": "Heading and body fonts should be different for visual hierarchy."})
                else:
                    earned_score += 10
            elif heading_font or body_font:
                earned_score += 7
                issues.append({"severity": "low", "section": "global", "message": "Define both heading and body fonts."})
            else:
                earned_score += 5
        else:
            earned_score += 5  # No fonts defined yet, neutral score

        # --- Check 6: Content completeness (15 points) ---
        max_score += 15
        if content:
            sections_with_content = len([s for s in sections if s in content and content[s]])
            coverage = sections_with_content / max(len(sections), 1)
            content_score = int(coverage * 15)
            earned_score += content_score
            if coverage < 0.7:
                issues.append({
                    "severity": "high",
                    "section": "global",
                    "message": f"Only {sections_with_content}/{len(sections)} sections have content defined ({coverage:.0%}). Aim for 100%.",
                })
        else:
            earned_score += 0
            issues.append({"severity": "high", "section": "global", "message": "No content defined for any section."})

        # --- Check 7: Social proof present (10 points) ---
        max_score += 10
        social_proof_sections = {"testimonials", "stats", "logos", "social-proof"}
        has_social_proof = bool(social_proof_sections & set(sections))
        if has_social_proof:
            earned_score += 10
        else:
            earned_score += 3
            issues.append({
                "severity": "medium",
                "section": "global",
                "message": "No social proof section (testimonials, stats, or logos). Strongly recommended for credibility.",
            })

        # --- Check 8: Contact/conversion path (10 points) ---
        max_score += 10
        has_contact = "contact" in sections
        has_cta = "cta" in sections
        if has_contact and has_cta:
            earned_score += 10
        elif has_contact or has_cta:
            earned_score += 7
            if not has_contact:
                issues.append({"severity": "medium", "section": "global", "message": "No contact section. Users need a way to reach you."})
            if not has_cta:
                issues.append({"severity": "low", "section": "global", "message": "No dedicated CTA section. Consider adding one before footer for final conversion push."})
        else:
            earned_score += 2
            issues.append({"severity": "high", "section": "global", "message": "No contact or CTA section. Site has no conversion path."})

        # Calculate final score
        final_score = round((earned_score / max(max_score, 1)) * 100, 1)
        final_score = min(100.0, max(0.0, final_score))

        # Sort issues by severity
        severity_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
        issues.sort(key=lambda x: severity_order.get(x.get("severity", "low"), 4))

        return final_score, issues

    def get_section_content_rules(self, section_type: str) -> Optional[Dict[str, Any]]:
        """Get content hierarchy rules for a specific section type.

        Args:
            section_type: Section type (hero, about, services, etc.)

        Returns:
            Content hierarchy dict or None if section type not found
        """
        return self.CONTENT_HIERARCHY.get(section_type.lower().strip())

    def get_must_have_sections(self, category: str) -> List[str]:
        """Get the must-have sections for a category.

        Args:
            category: Business category

        Returns:
            List of required section type strings
        """
        category = category.lower().strip()
        alias_map = {
            "ristorante": "restaurant", "tech": "saas", "corporate": "business",
            "shop": "ecommerce", "creative": "portfolio", "evento": "event",
        }
        category = alias_map.get(category, category)
        if category not in self.CATEGORY_SPECIFIC_RULES:
            category = "custom"
        return self.CATEGORY_SPECIFIC_RULES[category].get("must_have_sections", [])

    def get_recommended_sections(self, category: str) -> List[str]:
        """Get the recommended (optional but valuable) sections for a category.

        Args:
            category: Business category

        Returns:
            List of recommended section type strings
        """
        category = category.lower().strip()
        alias_map = {
            "ristorante": "restaurant", "tech": "saas", "corporate": "business",
            "shop": "ecommerce", "creative": "portfolio", "evento": "event",
        }
        category = alias_map.get(category, category)
        if category not in self.CATEGORY_SPECIFIC_RULES:
            category = "custom"
        return self.CATEGORY_SPECIFIC_RULES[category].get("recommended_sections", [])


# Singleton instance for import convenience
quality_guide = SiteQualityGuide()
