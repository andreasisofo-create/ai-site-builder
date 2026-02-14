"""
Seed script for Design Knowledge ChromaDB.
Populates the vector database with 100+ design patterns covering
scroll effects, text animations, image effects, layout patterns,
GSAP snippets, creative prompts, and more.

Run: python -m app.services.seed_design_knowledge
"""

from app.services.design_knowledge import add_pattern, get_collection_stats

PATTERNS = [
    # ====================================================
    # SCROLL EFFECTS (15)
    # ====================================================
    {
        "id": "scroll_fade_up",
        "content": "Fade-up scroll animation: elements slide up and fade in as they enter the viewport. The most versatile scroll effect - works for cards, text blocks, images. Use with staggered delays for cascade effect.",
        "category": "scroll_effects",
        "tags": ["fade", "scroll", "entrance", "versatile"],
        "complexity": "low",
        "impact_score": 7,
        "code": 'data-animate="fade-up"',
    },
    {
        "id": "scroll_parallax_hero",
        "content": "Parallax scrolling on hero images creates depth and immersion. Background moves slower than foreground content, giving a cinematic 3D feel. Best for hero sections with large background images.",
        "category": "scroll_effects",
        "tags": ["parallax", "hero", "depth", "cinematic"],
        "complexity": "low",
        "impact_score": 9,
        "code": 'data-animate="parallax" data-speed="0.3"',
    },
    {
        "id": "scroll_stagger_grid",
        "content": "Staggered grid animation: cards in a grid appear one-by-one with slight delays, creating a wave effect. Essential for service cards, feature grids, and portfolio galleries.",
        "category": "scroll_effects",
        "tags": ["stagger", "grid", "cards", "wave"],
        "complexity": "low",
        "impact_score": 8,
        "code": '<div data-animate="stagger"><div class="stagger-item">Card 1</div><div class="stagger-item">Card 2</div></div>',
    },
    {
        "id": "scroll_clip_reveal",
        "content": "Clip-path circle reveal: section reveals through an expanding circle from the center. Dramatic effect for hero sections or full-bleed image sections. Creates a wow moment.",
        "category": "scroll_effects",
        "tags": ["clip-path", "reveal", "dramatic", "circle"],
        "complexity": "medium",
        "impact_score": 9,
        "code": 'data-animate="clip-reveal"',
    },
    {
        "id": "scroll_blur_slide",
        "content": "Blur-slide entrance: elements enter with a dreamy blur that clears as they slide into view. Perfect for elegant/luxury sites, photography portfolios, and artistic sections.",
        "category": "scroll_effects",
        "tags": ["blur", "slide", "dreamy", "elegant"],
        "complexity": "low",
        "impact_score": 8,
        "code": 'data-animate="blur-slide" data-duration="1"',
    },
    {
        "id": "scroll_scale_in",
        "content": "Scale-in animation: elements zoom from small to full size. Great for logos, icons, profile images, and stats counters. Creates a pop effect.",
        "category": "scroll_effects",
        "tags": ["scale", "zoom", "pop", "entrance"],
        "complexity": "low",
        "impact_score": 6,
        "code": 'data-animate="scale-in"',
    },
    {
        "id": "scroll_rotate_3d",
        "content": "3D rotation entrance: cards rotate towards the viewer on the X axis as they enter. Adds depth and premium feel to card-based layouts. Best for feature cards and testimonials.",
        "category": "scroll_effects",
        "tags": ["3d", "rotate", "perspective", "cards"],
        "complexity": "medium",
        "impact_score": 7,
        "code": 'data-animate="rotate-3d"',
    },
    {
        "id": "scroll_horizontal_section",
        "content": "Horizontal scroll section: content scrolls horizontally while the user scrolls vertically. Creates an immersive gallery or timeline experience. Pin the section and translate inner content.",
        "category": "scroll_effects",
        "tags": ["horizontal", "scroll", "gallery", "immersive"],
        "complexity": "high",
        "impact_score": 10,
        "code": '<section data-horizontal-scroll><div class="hs-inner flex">panels...</div></section>',
    },
    {
        "id": "scroll_progress_bar",
        "content": "Scroll progress bar: a thin colored bar at the top of the page that fills as the user scrolls. Provides visual feedback and encourages full page reading. Auto-created by gsap-universal.js.",
        "category": "scroll_effects",
        "tags": ["progress", "bar", "feedback", "ux"],
        "complexity": "low",
        "impact_score": 5,
        "code": '<div data-scroll-progress class="fixed top-0 left-0 right-0 h-1 bg-primary z-50"></div>',
    },
    {
        "id": "scroll_split_screen",
        "content": "Split-screen parallax: two halves of a section move in opposite directions on scroll. Creates visual tension and draws attention. Great for before/after or comparison sections.",
        "category": "scroll_effects",
        "tags": ["split", "parallax", "tension", "comparison"],
        "complexity": "medium",
        "impact_score": 8,
        "code": '<div data-animate="split-screen"><div class="left">Left</div><div class="right">Right</div></div>',
    },
    {
        "id": "scroll_reveal_up",
        "content": "Reveal-up with clip-path: content slides up from behind a clip-path mask. More elegant than fade-up - the element appears to be unveiled. Perfect for headings and key content.",
        "category": "scroll_effects",
        "tags": ["reveal", "clip-path", "mask", "elegant"],
        "complexity": "medium",
        "impact_score": 8,
        "code": 'data-animate="reveal-up"',
    },
    {
        "id": "scroll_image_zoom",
        "content": "Ken Burns zoom on scroll: images slowly scale as the user scrolls past, creating a cinematic Ken Burns effect. Wrap the image in an overflow-hidden container.",
        "category": "scroll_effects",
        "tags": ["ken-burns", "zoom", "image", "cinematic"],
        "complexity": "low",
        "impact_score": 7,
        "code": '<div data-animate="image-zoom" class="overflow-hidden"><img src="..." class="w-full"></div>',
    },
    {
        "id": "scroll_fade_directions",
        "content": "Directional fades create layout rhythm. Use fade-left for text on the left, fade-right for images on the right (or vice versa). Alternating directions in split layouts creates a breathing pattern.",
        "category": "scroll_effects",
        "tags": ["fade", "direction", "rhythm", "alternating"],
        "complexity": "low",
        "impact_score": 6,
        "code": 'data-animate="fade-left" / data-animate="fade-right"',
    },
    {
        "id": "scroll_bounce_in",
        "content": "Bounce-in animation with elastic easing: elements pop into view with a bouncy overshoot. Fun and energetic, great for icons, badges, and playful UI elements.",
        "category": "scroll_effects",
        "tags": ["bounce", "elastic", "playful", "pop"],
        "complexity": "low",
        "impact_score": 6,
        "code": 'data-animate="bounce-in"',
    },
    {
        "id": "scroll_stagger_scale",
        "content": "Stagger-scale: children elements scale from 0 to 1 with stagger. Creates a popping-in effect like bubbles. Works great for icon grids, stats, and badge collections.",
        "category": "scroll_effects",
        "tags": ["stagger", "scale", "bubbles", "pop"],
        "complexity": "low",
        "impact_score": 7,
        "code": 'data-animate="stagger-scale"',
    },

    # ====================================================
    # TEXT ANIMATIONS (12)
    # ====================================================
    {
        "id": "text_split_chars",
        "content": "Character-by-character text split animation: each letter animates individually with slight rotation and fade. Most dramatic text effect - use ONLY on hero headlines for maximum impact.",
        "category": "text_animations",
        "tags": ["text-split", "chars", "hero", "dramatic"],
        "complexity": "medium",
        "impact_score": 10,
        "code": 'data-animate="text-split" data-split-type="chars" data-duration="1.2" data-ease="power3.out"',
    },
    {
        "id": "text_split_words",
        "content": "Word-by-word text split: each word animates separately. More readable than chars, perfect for section headings throughout the page. Creates elegance without overwhelming.",
        "category": "text_animations",
        "tags": ["text-split", "words", "headings", "elegant"],
        "complexity": "low",
        "impact_score": 8,
        "code": 'data-animate="text-split" data-split-type="words"',
    },
    {
        "id": "text_reveal_mask",
        "content": "Text reveal with overflow mask: lines slide up from behind a clip-path mask. Creates a curtain-lifting effect. Use on important quotes, testimonials, or feature descriptions.",
        "category": "text_animations",
        "tags": ["text-reveal", "mask", "curtain", "elegant"],
        "complexity": "medium",
        "impact_score": 8,
        "code": 'data-animate="text-reveal"',
    },
    {
        "id": "text_typewriter",
        "content": "Typewriter effect: text types out character by character with a blinking cursor. Creates a live, interactive feel. Best for hero subtitles or taglines. Avoid on long paragraphs.",
        "category": "text_animations",
        "tags": ["typewriter", "cursor", "interactive", "hero"],
        "complexity": "low",
        "impact_score": 7,
        "code": 'data-animate="typewriter" data-type-speed="0.04"',
    },
    {
        "id": "text_gradient_animated",
        "content": "Animated gradient text: use CSS background-clip text with gradient-flow animation. Text shimmers with moving color. Eye-catching for hero headlines and CTAs.",
        "category": "text_animations",
        "tags": ["gradient", "shimmer", "hero", "color"],
        "complexity": "medium",
        "impact_score": 9,
        "code": 'class="bg-gradient-to-r from-primary via-accent to-secondary bg-clip-text text-transparent" data-animate="gradient-flow" style="background-size:200% 200%"',
    },
    {
        "id": "text_counter_animation",
        "content": "Animated number counter: numbers count up from 0 to target value on scroll. Essential for statistics sections, achievement badges, and social proof numbers.",
        "category": "text_animations",
        "tags": ["counter", "numbers", "stats", "social-proof"],
        "complexity": "low",
        "impact_score": 8,
        "code": 'data-counter="150" data-counter-suffix="+"',
    },
    {
        "id": "text_split_lines",
        "content": "Line-by-line text split: each line of text animates separately. Best for multiline quotes, paragraphs, or poetic content. Creates a reading rhythm.",
        "category": "text_animations",
        "tags": ["text-split", "lines", "paragraphs", "rhythm"],
        "complexity": "medium",
        "impact_score": 7,
        "code": 'data-animate="text-split" data-split-type="lines"',
    },
    {
        "id": "text_blur_fade_in",
        "content": "Blur fade-in for subtitles: text starts blurred and fades to clear. Creates a dreamy, cinematic entrance. Perfect for hero subtitles after a dramatic heading animation.",
        "category": "text_animations",
        "tags": ["blur", "fade", "subtitle", "cinematic"],
        "complexity": "low",
        "impact_score": 7,
        "code": 'data-animate="blur-in" data-delay="0.3" data-duration="1.2"',
    },
    {
        "id": "text_cascade_delays",
        "content": "Cascade delays on text elements: stagger heading, subtitle, and CTA with increasing delays (0, 0.2, 0.4s). Creates a choreographed reveal sequence that guides the eye.",
        "category": "text_animations",
        "tags": ["cascade", "delay", "choreography", "sequence"],
        "complexity": "low",
        "impact_score": 8,
        "code": 'h1: data-delay="0" | p: data-delay="0.2" | button: data-delay="0.4"',
    },
    {
        "id": "text_outlined_heading",
        "content": "Outlined heading with stroke text: large text with transparent fill and stroke outline. Creates a modern, editorial look. Combine with solid color on hover for interactivity.",
        "category": "text_animations",
        "tags": ["outlined", "stroke", "editorial", "modern"],
        "complexity": "medium",
        "impact_score": 7,
        "code": 'style="-webkit-text-stroke: 2px var(--color-primary); color: transparent;"',
    },
    {
        "id": "text_responsive_clamp",
        "content": "Responsive typography with clamp(): smooth font scaling between breakpoints. No more jumpy size changes. Use for headings: clamp(2.5rem, 5vw, 5rem) for fluid scaling from mobile to desktop.",
        "category": "text_animations",
        "tags": ["responsive", "clamp", "fluid", "typography"],
        "complexity": "low",
        "impact_score": 6,
        "code": 'style="font-size: clamp(2.5rem, 5vw, 5rem);"',
    },
    {
        "id": "text_hover_underline",
        "content": "Animated underline on hover: line slides in from left to right under links. Creates elegant navigation feel. Use transform-origin and scale for the smoothest result.",
        "category": "text_animations",
        "tags": ["underline", "hover", "links", "navigation"],
        "complexity": "low",
        "impact_score": 5,
        "code": 'class="relative after:absolute after:bottom-0 after:left-0 after:w-full after:h-0.5 after:bg-primary after:scale-x-0 hover:after:scale-x-100 after:transition-transform after:origin-left"',
    },

    # ====================================================
    # IMAGE EFFECTS (10)
    # ====================================================
    {
        "id": "img_ken_burns",
        "content": "Ken Burns zoom: image slowly scales from 1 to 1.15 while scrolling past. Creates a subtle cinematic movement. Wrap image in overflow-hidden container for best results.",
        "category": "image_effects",
        "tags": ["ken-burns", "zoom", "cinematic", "scroll"],
        "complexity": "low",
        "impact_score": 8,
        "code": '<div data-animate="image-zoom" class="overflow-hidden rounded-2xl"><img src="..." class="w-full"></div>',
    },
    {
        "id": "img_reveal_overlay",
        "content": "Image reveal with colored overlay wipe: a solid color block slides across the image, then slides away to reveal the photo. Two-phase animation for maximum drama.",
        "category": "image_effects",
        "tags": ["reveal", "overlay", "wipe", "dramatic"],
        "complexity": "medium",
        "impact_score": 9,
        "code": '<div class="img-reveal-wrap"><div class="img-reveal-overlay bg-primary"></div><img src="..." style="opacity:0"></div>',
    },
    {
        "id": "img_parallax_depth",
        "content": "Parallax images create layered depth. Apply different speeds to foreground and background images. Foreground: data-speed=0.5, background: data-speed=0.1.",
        "category": "image_effects",
        "tags": ["parallax", "depth", "layers", "immersive"],
        "complexity": "medium",
        "impact_score": 8,
        "code": 'data-animate="parallax" data-speed="0.3"',
    },
    {
        "id": "img_tilt_hover",
        "content": "3D tilt on image hover: image tilts towards cursor position with perspective transform. Adds interactivity and premium feel to portfolio galleries and product showcases.",
        "category": "image_effects",
        "tags": ["tilt", "hover", "3d", "interactive"],
        "complexity": "medium",
        "impact_score": 8,
        "code": 'data-animate="card-hover-3d"',
    },
    {
        "id": "img_blur_lazy_reveal",
        "content": "Blur-to-sharp lazy reveal: image loads blurred and transitions to sharp as it enters viewport. Creates a smooth, progressive loading feel. Combine blur-in with image loading.",
        "category": "image_effects",
        "tags": ["blur", "lazy", "progressive", "loading"],
        "complexity": "low",
        "impact_score": 6,
        "code": 'data-animate="blur-slide" loading="lazy"',
    },
    {
        "id": "img_stagger_gallery",
        "content": "Staggered gallery loading: images in a gallery grid appear one-by-one with slight delays. Creates a satisfying waterfall effect. Use stagger animation on parent container.",
        "category": "image_effects",
        "tags": ["stagger", "gallery", "waterfall", "grid"],
        "complexity": "low",
        "impact_score": 7,
        "code": '<div data-animate="stagger" class="grid grid-cols-3"><div class="stagger-item">img1</div>...</div>',
    },
    {
        "id": "img_decorative_frame",
        "content": "Decorative image frame: offset border or double-border around images creates an elegant, editorial feel. Use absolute positioned pseudo-elements with slight offset from the image.",
        "category": "image_effects",
        "tags": ["frame", "border", "elegant", "editorial"],
        "complexity": "medium",
        "impact_score": 7,
        "code": '<div class="relative"><div class="absolute -inset-3 border border-primary/20 rounded-2xl"></div><img class="relative rounded-xl"></div>',
    },
    {
        "id": "img_gradient_overlay",
        "content": "Gradient overlay on images: semi-transparent gradient from bottom creates text readability zone. Essential for hero images with text overlay. Use from-black/60 via-transparent.",
        "category": "image_effects",
        "tags": ["gradient", "overlay", "readability", "hero"],
        "complexity": "low",
        "impact_score": 7,
        "code": '<div class="relative"><img src="..."><div class="absolute inset-0 bg-gradient-to-t from-black/60 via-transparent"></div></div>',
    },
    {
        "id": "img_hover_scale_shadow",
        "content": "Hover scale with shadow: image scales slightly (1.05) and shadow deepens on hover. Creates a lifting effect. Combine with translate-y for cards that pop forward.",
        "category": "image_effects",
        "tags": ["hover", "scale", "shadow", "lift"],
        "complexity": "low",
        "impact_score": 6,
        "code": 'class="transition-all duration-300 hover:scale-105 hover:shadow-2xl hover:-translate-y-2"',
    },
    {
        "id": "img_aspect_ratio",
        "content": "Consistent image aspect ratios: use aspect-ratio CSS for uniform image containers. Prevents layout shift and creates clean grids. 16/9 for heroes, 1/1 for profiles, 4/3 for cards.",
        "category": "image_effects",
        "tags": ["aspect-ratio", "consistent", "layout", "grid"],
        "complexity": "low",
        "impact_score": 5,
        "code": 'class="aspect-[16/9] object-cover w-full"',
    },

    # ====================================================
    # SECTION TRANSITIONS (10)
    # ====================================================
    {
        "id": "section_clip_circle",
        "content": "Circular clip-path reveal for full sections: section reveals through expanding circle. Most dramatic section transition - use sparingly on 1-2 key sections per page.",
        "category": "section_transitions",
        "tags": ["clip-path", "circle", "dramatic", "reveal"],
        "complexity": "medium",
        "impact_score": 10,
        "code": 'data-animate="clip-reveal"',
    },
    {
        "id": "section_alternating_bg",
        "content": "Alternate section backgrounds for visual rhythm: switch between bg-color and bg-alt-color. Prevents visual monotony and creates clear section boundaries without heavy dividers.",
        "category": "section_transitions",
        "tags": ["alternating", "background", "rhythm", "boundaries"],
        "complexity": "low",
        "impact_score": 7,
        "code": 'section 1: bg-[var(--color-bg)] | section 2: bg-[var(--color-bg-alt)] | repeat',
    },
    {
        "id": "section_gradient_transition",
        "content": "Gradient background transition: sections blend into each other through gradient backgrounds. Creates a seamless flow. Use radial-gradient or linear-gradient on alternating sections.",
        "category": "section_transitions",
        "tags": ["gradient", "seamless", "flow", "blend"],
        "complexity": "medium",
        "impact_score": 8,
        "code": 'style="background: linear-gradient(180deg, var(--color-bg), var(--color-bg-alt));"',
    },
    {
        "id": "section_svg_divider",
        "content": "SVG wave divider between sections: custom SVG shape separates sections with organic curves. More interesting than straight lines. Use fill matching the next section background.",
        "category": "section_transitions",
        "tags": ["svg", "wave", "divider", "organic"],
        "complexity": "medium",
        "impact_score": 7,
        "code": '<svg class="w-full -mb-1" viewBox="0 0 1440 100"><path fill="var(--color-bg-alt)" d="M0,50 C360,100 1080,0 1440,50 L1440,100 L0,100 Z"/></svg>',
    },
    {
        "id": "section_full_bleed",
        "content": "Full-bleed image sections break the content flow and create visual anchors. Place between text-heavy sections for breathing room. Use with parallax for depth.",
        "category": "section_transitions",
        "tags": ["full-bleed", "image", "anchor", "breathing"],
        "complexity": "low",
        "impact_score": 8,
        "code": '<section class="h-[50vh] relative overflow-hidden" data-animate="parallax"><img class="w-full h-full object-cover"></section>',
    },
    {
        "id": "section_stagger_entrance",
        "content": "Staggered section entrance: section heading, subtitle, and content blocks enter with cascading delays. Creates a choreographed reveal. Heading: delay 0, subtitle: 0.2, content: 0.4.",
        "category": "section_transitions",
        "tags": ["stagger", "entrance", "choreography", "cascade"],
        "complexity": "low",
        "impact_score": 7,
        "code": 'heading: data-delay="0" | subtitle: data-delay="0.2" | content: data-delay="0.4"',
    },
    {
        "id": "section_scale_transition",
        "content": "Scale-in section: entire section scales from 0.95 to 1 as it enters. Creates a subtle zoom-in feel that draws attention. Best for CTA sections and highlighted content.",
        "category": "section_transitions",
        "tags": ["scale", "zoom", "attention", "cta"],
        "complexity": "low",
        "impact_score": 6,
        "code": 'data-animate="scale-in"',
    },
    {
        "id": "section_dark_light_contrast",
        "content": "Dark-light section contrast: alternate between dark and light backgrounds for dramatic rhythm. Dark sections feel premium, light sections feel open. Strong contrast creates visual punctuation.",
        "category": "section_transitions",
        "tags": ["dark", "light", "contrast", "rhythm"],
        "complexity": "low",
        "impact_score": 8,
        "code": 'dark: bg-gray-900 text-white | light: bg-white text-gray-900',
    },
    {
        "id": "section_sticky_heading",
        "content": "Sticky section heading: section title stays pinned while content scrolls underneath. Creates a layered reading experience. Use position:sticky with ScrollTrigger for smooth behavior.",
        "category": "section_transitions",
        "tags": ["sticky", "pinned", "layered", "reading"],
        "complexity": "high",
        "impact_score": 7,
        "code": 'class="sticky top-0 z-10"',
    },
    {
        "id": "section_blur_bg_accent",
        "content": "Blurred background accent: large colored circles with blur in the background of sections. Creates depth without being distracting. Use primary and accent colors with low opacity.",
        "category": "section_transitions",
        "tags": ["blur", "accent", "depth", "background"],
        "complexity": "low",
        "impact_score": 7,
        "code": '<div class="absolute -top-40 -right-40 w-96 h-96 rounded-full blur-3xl opacity-10" style="background: var(--color-primary);"></div>',
    },

    # ====================================================
    # MICRO INTERACTIONS (10)
    # ====================================================
    {
        "id": "micro_magnetic_button",
        "content": "Magnetic button: button subtly follows cursor on hover with elastic snap-back on leave. Creates a premium, interactive feel. Essential for primary CTA buttons.",
        "category": "micro_interactions",
        "tags": ["magnetic", "button", "hover", "premium"],
        "complexity": "medium",
        "impact_score": 9,
        "code": 'data-animate="magnetic"',
    },
    {
        "id": "micro_3d_card_tilt",
        "content": "3D card tilt: card tilts towards cursor position with perspective transform and light reflection. Creates depth and interactivity. Best for service cards, feature cards, pricing.",
        "category": "micro_interactions",
        "tags": ["3d", "tilt", "card", "perspective"],
        "complexity": "medium",
        "impact_score": 9,
        "code": 'data-animate="card-hover-3d"',
    },
    {
        "id": "micro_hover_lift",
        "content": "Hover lift effect: card translates up (-4px) with enhanced shadow on hover. Simple but effective micro-interaction for any clickable card. The subtle lift implies interactivity.",
        "category": "micro_interactions",
        "tags": ["hover", "lift", "shadow", "card"],
        "complexity": "low",
        "impact_score": 6,
        "code": 'class="transition-all duration-300 hover:-translate-y-1 hover:shadow-xl"',
    },
    {
        "id": "micro_button_gradient_shift",
        "content": "Button gradient shift on hover: background-position changes to reveal different gradient colors. Creates a color-shifting effect that feels alive and responsive.",
        "category": "micro_interactions",
        "tags": ["button", "gradient", "shift", "hover"],
        "complexity": "low",
        "impact_score": 7,
        "code": 'class="bg-gradient-to-r from-primary to-secondary bg-[length:200%_100%] hover:bg-right transition-all duration-500"',
    },
    {
        "id": "micro_icon_rotate",
        "content": "Icon rotation on hover: icons rotate 360 degrees when their card is hovered. Adds playfulness to otherwise static icon grids. Use transition with cubic-bezier for smooth motion.",
        "category": "micro_interactions",
        "tags": ["icon", "rotate", "hover", "playful"],
        "complexity": "low",
        "impact_score": 5,
        "code": 'class="group-hover:rotate-[360deg] transition-transform duration-700"',
    },
    {
        "id": "micro_border_glow",
        "content": "Border glow on hover: card border shifts from subtle to glowing primary color on hover. Creates a neon/tech feel. Use box-shadow with primary color for the glow effect.",
        "category": "micro_interactions",
        "tags": ["border", "glow", "neon", "tech"],
        "complexity": "low",
        "impact_score": 7,
        "code": 'class="border border-transparent hover:border-primary/30 hover:shadow-lg hover:shadow-primary/10 transition-all duration-300"',
    },
    {
        "id": "micro_accordion_smooth",
        "content": "Smooth accordion with CSS grid: use grid-template-rows: 0fr to 1fr transition for buttery smooth expand/collapse. Superior to max-height hack. Works for FAQs and collapsible content.",
        "category": "micro_interactions",
        "tags": ["accordion", "smooth", "faq", "expand"],
        "complexity": "medium",
        "impact_score": 6,
        "code": 'class="grid transition-all duration-300" style="grid-template-rows: 0fr;" data-open: style="grid-template-rows: 1fr;"',
    },
    {
        "id": "micro_cursor_glow",
        "content": "Cursor glow follower: a soft radial gradient follows the cursor across the page. Creates an ambient, interactive feel. Best for dark-themed sites.",
        "category": "micro_interactions",
        "tags": ["cursor", "glow", "ambient", "dark"],
        "complexity": "medium",
        "impact_score": 8,
        "code": '<body data-cursor-glow> (auto-created by gsap-universal.js)',
    },
    {
        "id": "micro_text_highlight",
        "content": "Text highlight on hover: background color slides in behind text from left to right. Creates a marker/highlighter effect. Use background-size and background-position transitions.",
        "category": "micro_interactions",
        "tags": ["text", "highlight", "hover", "marker"],
        "complexity": "low",
        "impact_score": 5,
        "code": 'class="bg-gradient-to-r from-primary/20 to-primary/20 bg-[length:0%_100%] hover:bg-[length:100%_100%] bg-no-repeat transition-all duration-300"',
    },
    {
        "id": "micro_floating_elements",
        "content": "Floating decorative elements: small shapes (circles, squares, lines) with continuous floating animation. Adds life and motion to static backgrounds. Use sparingly with low opacity.",
        "category": "micro_interactions",
        "tags": ["floating", "decorative", "motion", "background"],
        "complexity": "low",
        "impact_score": 6,
        "code": 'data-animate="float" class="absolute w-8 h-8 rounded-full bg-primary/10"',
    },

    # ====================================================
    # COLOR PALETTES (10)
    # ====================================================
    {
        "id": "palette_deep_navy_gold",
        "content": "Deep navy and gold: luxury and authority. Navy (#1a1a2e) background with gold (#c5a04b) accents. Perfect for law firms, financial services, luxury brands. Use serif headings.",
        "category": "color_palettes",
        "tags": ["navy", "gold", "luxury", "authority"],
        "complexity": "low",
        "impact_score": 9,
    },
    {
        "id": "palette_dark_purple_gradient",
        "content": "Dark purple gradient: modern tech feel. Background #0f0f1a, primary gradient from #6c5ce7 to #0984e3. Perfect for SaaS, AI products, and tech startups. Use Inter or Space Grotesk.",
        "category": "color_palettes",
        "tags": ["purple", "gradient", "tech", "modern"],
        "complexity": "low",
        "impact_score": 9,
    },
    {
        "id": "palette_warm_cream_terracotta",
        "content": "Warm cream and terracotta: cozy and inviting. Background #fdf6ee, primary #c0392b, accent #e17055. Perfect for restaurants, bakeries, artisan brands. Use rounded shapes.",
        "category": "color_palettes",
        "tags": ["warm", "cream", "terracotta", "cozy"],
        "complexity": "low",
        "impact_score": 7,
    },
    {
        "id": "palette_dark_teal_mint",
        "content": "Dark with teal/mint accent: clean tech. Background #0d1117, primary #00cec9, text white/80. GitHub-inspired dark theme. Perfect for developer tools and SaaS products.",
        "category": "color_palettes",
        "tags": ["dark", "teal", "mint", "tech"],
        "complexity": "low",
        "impact_score": 8,
    },
    {
        "id": "palette_forest_sage",
        "content": "Forest green and sage: natural and grounding. Background #f0f4f0, primary #2d6a4f, accent #95d5b2. Perfect for organic brands, wellness, eco-companies. Calming and trustworthy.",
        "category": "color_palettes",
        "tags": ["green", "sage", "natural", "wellness"],
        "complexity": "low",
        "impact_score": 7,
    },
    {
        "id": "palette_sunset_gradient",
        "content": "Sunset gradient: warm and energetic. Background gradient from #ff6b6b through #feca57 to #48dbfb. Perfect for creative agencies, events, youth brands. Bold and memorable.",
        "category": "color_palettes",
        "tags": ["sunset", "gradient", "warm", "energetic"],
        "complexity": "low",
        "impact_score": 8,
    },
    {
        "id": "palette_monochrome_accent",
        "content": "Monochrome with single accent color: minimal and sophisticated. All grays (#0f172a to #f8fafc) with ONE vibrant accent (#3b82f6 or #e84393). The accent creates instant focus on CTAs.",
        "category": "color_palettes",
        "tags": ["monochrome", "accent", "minimal", "sophisticated"],
        "complexity": "low",
        "impact_score": 8,
    },
    {
        "id": "palette_coral_peach",
        "content": "Coral and peach: feminine and modern. Background #fff5f5, primary #e84393, secondary #fd79a8. Perfect for beauty, fashion, lifestyle brands. Soft but impactful.",
        "category": "color_palettes",
        "tags": ["coral", "peach", "feminine", "lifestyle"],
        "complexity": "low",
        "impact_score": 7,
    },
    {
        "id": "palette_charcoal_amber",
        "content": "Charcoal and amber: warm industrial. Background #1a1a1a, primary #f59e0b, text #e5e5e5. Perfect for craft breweries, woodworking, industrial brands. Use slab-serif headings.",
        "category": "color_palettes",
        "tags": ["charcoal", "amber", "industrial", "craft"],
        "complexity": "low",
        "impact_score": 7,
    },
    {
        "id": "palette_electric_neon",
        "content": "Electric neon on dark: cyberpunk energy. Background #0a0a0a, neon green #00ff88 or neon blue #00d4ff. Perfect for gaming, music, nightlife. High contrast, high energy.",
        "category": "color_palettes",
        "tags": ["neon", "electric", "cyberpunk", "energy"],
        "complexity": "low",
        "impact_score": 9,
    },

    # ====================================================
    # LAYOUT PATTERNS (10)
    # ====================================================
    {
        "id": "layout_bento_grid",
        "content": "Bento grid layout: asymmetric grid with mixed cell sizes (1x1, 2x1, 1x2). Creates visual interest and hierarchy. The largest cell draws attention first. Use grid-cols-4 with col-span variations.",
        "category": "layout_patterns",
        "tags": ["bento", "grid", "asymmetric", "hierarchy"],
        "complexity": "medium",
        "impact_score": 9,
    },
    {
        "id": "layout_split_screen",
        "content": "Split screen hero: 50/50 horizontal split with text on one side, image on the other. Clean and professional. Reverse the split on alternating sections for rhythm.",
        "category": "layout_patterns",
        "tags": ["split", "hero", "50-50", "professional"],
        "complexity": "low",
        "impact_score": 7,
    },
    {
        "id": "layout_centered_narrow",
        "content": "Centered narrow content: max-w-3xl centered text creates focused reading experience. Ideal for about sections, mission statements, and long-form content. Generous line-height (1.8).",
        "category": "layout_patterns",
        "tags": ["centered", "narrow", "focused", "reading"],
        "complexity": "low",
        "impact_score": 6,
    },
    {
        "id": "layout_card_grid_3col",
        "content": "3-column card grid: the default for services, features, and pricing. Use gap-8 for breathing room. Cards should have consistent height and hover effects (lift + shadow).",
        "category": "layout_patterns",
        "tags": ["card", "grid", "3-column", "services"],
        "complexity": "low",
        "impact_score": 7,
    },
    {
        "id": "layout_fullwidth_hero",
        "content": "Full viewport hero: min-h-screen with centered content. The first impression. Use dramatic typography (5xl-8xl), strong CTA, and decorative background elements (gradients, shapes, images).",
        "category": "layout_patterns",
        "tags": ["hero", "fullwidth", "viewport", "first-impression"],
        "complexity": "low",
        "impact_score": 10,
    },
    {
        "id": "layout_alternating_rows",
        "content": "Alternating image-text rows: image left/text right, then flip. Creates a zig-zag reading pattern that keeps attention. Each row should have generous spacing (gap-16).",
        "category": "layout_patterns",
        "tags": ["alternating", "zigzag", "rows", "attention"],
        "complexity": "low",
        "impact_score": 7,
    },
    {
        "id": "layout_floating_card",
        "content": "Floating card overlay: card element that overlaps the section boundary between two sections. Creates visual connection and breaks the horizontal monotony. Use negative margin or absolute positioning.",
        "category": "layout_patterns",
        "tags": ["floating", "card", "overlap", "connection"],
        "complexity": "medium",
        "impact_score": 8,
    },
    {
        "id": "layout_generous_spacing",
        "content": "Generous section spacing: py-20 to py-32 between sections. Breathing room is the #1 factor for professional feel. Cramped layouts look amateur. Give content room to exist.",
        "category": "layout_patterns",
        "tags": ["spacing", "padding", "breathing", "professional"],
        "complexity": "low",
        "impact_score": 9,
    },
    {
        "id": "layout_sticky_sidebar",
        "content": "Sticky sidebar with scrolling content: sidebar stays fixed while main content scrolls. Great for feature breakdowns, documentation, and product details. Use position:sticky.",
        "category": "layout_patterns",
        "tags": ["sticky", "sidebar", "scrolling", "details"],
        "complexity": "medium",
        "impact_score": 7,
    },
    {
        "id": "layout_masonry_gallery",
        "content": "Masonry gallery layout: varied-height items in a Pinterest-style grid. Creates organic, editorial feel. Use CSS columns or grid with row-span for the staggered effect.",
        "category": "layout_patterns",
        "tags": ["masonry", "gallery", "pinterest", "editorial"],
        "complexity": "medium",
        "impact_score": 8,
    },

    # ====================================================
    # TYPOGRAPHY (8)
    # ====================================================
    {
        "id": "typo_playfair_inter",
        "content": "Playfair Display + Inter: classic elegance meets modern clarity. Playfair for headings (serif, italic for drama), Inter for body. Perfect for luxury, restaurants, fashion.",
        "category": "typography",
        "tags": ["playfair", "inter", "serif", "elegant"],
        "complexity": "low",
        "impact_score": 8,
    },
    {
        "id": "typo_space_grotesk_dm_sans",
        "content": "Space Grotesk + DM Sans: geometric tech meets friendly readability. Space Grotesk headings have distinctive character, DM Sans body is warm and inviting. Perfect for SaaS, startups.",
        "category": "typography",
        "tags": ["space-grotesk", "dm-sans", "tech", "startup"],
        "complexity": "low",
        "impact_score": 8,
    },
    {
        "id": "typo_sora_jakarta",
        "content": "Sora + Plus Jakarta Sans: modern and approachable. Sora has geometric precision for headings, Jakarta is friendly for body text. Perfect for apps, digital products, modern businesses.",
        "category": "typography",
        "tags": ["sora", "jakarta", "modern", "approachable"],
        "complexity": "low",
        "impact_score": 7,
    },
    {
        "id": "typo_dm_serif_nunito",
        "content": "DM Serif Display + Nunito Sans: editorial sophistication meets soft readability. DM Serif for impactful headings, Nunito for comfortable reading. Perfect for magazines, blogs, editorial sites.",
        "category": "typography",
        "tags": ["dm-serif", "nunito", "editorial", "sophisticated"],
        "complexity": "low",
        "impact_score": 8,
    },
    {
        "id": "typo_hierarchy_sizes",
        "content": "Typography size hierarchy: H1 5xl-8xl (hero only), H2 3xl-4xl (section headings), H3 xl-2xl (card titles), body text-base (16px), small text-sm (14px). Consistent hierarchy = professional feel.",
        "category": "typography",
        "tags": ["hierarchy", "sizes", "consistency", "professional"],
        "complexity": "low",
        "impact_score": 8,
    },
    {
        "id": "typo_weight_contrast",
        "content": "Font weight contrast: bold headings (700-800) vs regular body (400). The weight difference creates visual hierarchy. Use font-extrabold for hero, font-bold for sections, font-normal for paragraphs.",
        "category": "typography",
        "tags": ["weight", "contrast", "hierarchy", "bold"],
        "complexity": "low",
        "impact_score": 7,
    },
    {
        "id": "typo_tracking_uppercase",
        "content": "Tracking + uppercase for labels: small uppercase text with wide letter-spacing (tracking-widest) creates elegant label/category text. Use for section pre-headings and tag labels.",
        "category": "typography",
        "tags": ["tracking", "uppercase", "labels", "elegant"],
        "complexity": "low",
        "impact_score": 6,
    },
    {
        "id": "typo_italic_accent",
        "content": "Italic accent: use italic style on serif headings for elegance and personality. Italic Playfair Display or italic DM Serif creates a magazine-quality feel. Use sparingly on key headings.",
        "category": "typography",
        "tags": ["italic", "accent", "serif", "magazine"],
        "complexity": "low",
        "impact_score": 7,
    },

    # ====================================================
    # GSAP SNIPPETS (10)
    # ====================================================
    {
        "id": "gsap_hero_sequence",
        "content": "Hero entrance sequence: heading text-split (chars) at delay 0, subtitle blur-in at 0.3s, CTA magnetic at 0.5s. Creates a cinematic reveal. The most impactful animation on any page.",
        "category": "gsap_snippets",
        "tags": ["hero", "sequence", "entrance", "cinematic"],
        "complexity": "medium",
        "impact_score": 10,
        "code": 'h1: data-animate="text-split" data-split-type="chars" | p: data-animate="blur-in" data-delay="0.3" | a: data-animate="magnetic"',
    },
    {
        "id": "gsap_card_grid_pattern",
        "content": "Card grid animation pattern: parent container with stagger, each child with stagger-item class. Cards can also have individual tilt or card-hover-3d for hover interaction.",
        "category": "gsap_snippets",
        "tags": ["cards", "grid", "stagger", "pattern"],
        "complexity": "low",
        "impact_score": 8,
        "code": '<div data-animate="stagger"><div class="stagger-item" data-animate="tilt">Card</div></div>',
    },
    {
        "id": "gsap_section_heading",
        "content": "Section heading pattern: pre-label with fade-up, main heading with text-split words, subtitle with fade-up delayed. Creates consistent professional headings across all sections.",
        "category": "gsap_snippets",
        "tags": ["heading", "section", "consistent", "pattern"],
        "complexity": "low",
        "impact_score": 7,
        "code": 'label: data-animate="fade-up" | h2: data-animate="text-split" data-split-type="words" | p: data-animate="fade-up" data-delay="0.2"',
    },
    {
        "id": "gsap_stats_counter",
        "content": "Stats counter section: numbers animate from 0 to target on scroll. Add suffix for units (+, %, K, /7). Combine with stagger for sequential counting effect.",
        "category": "gsap_snippets",
        "tags": ["counter", "stats", "numbers", "scroll"],
        "complexity": "low",
        "impact_score": 8,
        "code": '<div data-counter="500" data-counter-suffix="+">0</div>',
    },
    {
        "id": "gsap_image_reveal_sequence",
        "content": "Image reveal sequence: colored overlay slides across, then slides away revealing the image. Two-phase timeline creates anticipation. Use img-reveal-wrap structure.",
        "category": "gsap_snippets",
        "tags": ["image", "reveal", "timeline", "anticipation"],
        "complexity": "medium",
        "impact_score": 9,
        "code": '<div class="img-reveal-wrap overflow-hidden"><div class="img-reveal-overlay" style="background:var(--color-primary)"></div><img style="opacity:0"></div>',
    },
    {
        "id": "gsap_parallax_bg",
        "content": "Background parallax: hero image moves at different speed than content. Creates depth illusion. Speed 0.3 = gentle, 0.5 = moderate. Always on images, never on text.",
        "category": "gsap_snippets",
        "tags": ["parallax", "background", "depth", "hero"],
        "complexity": "low",
        "impact_score": 7,
        "code": '<img data-animate="parallax" data-speed="0.3" class="absolute inset-0 w-full h-full object-cover">',
    },
    {
        "id": "gsap_floating_decorations",
        "content": "Floating decoration pattern: absolute-positioned shapes with float animation and random delays. Creates living, breathing backgrounds. Use 3-5 elements with varying sizes and opacities.",
        "category": "gsap_snippets",
        "tags": ["floating", "decorations", "shapes", "background"],
        "complexity": "low",
        "impact_score": 6,
        "code": '<div class="absolute" data-animate="float" style="opacity:0.1"><div class="w-64 h-64 rounded-full bg-primary blur-3xl"></div></div>',
    },
    {
        "id": "gsap_marquee_logos",
        "content": "Infinite marquee for logos/partners: seamless horizontal scroll of logos or text. Inner content is auto-duplicated for seamless loop. Speed and direction configurable.",
        "category": "gsap_snippets",
        "tags": ["marquee", "logos", "infinite", "scroll"],
        "complexity": "medium",
        "impact_score": 7,
        "code": '<div data-animate="marquee" data-marquee-speed="30"><div class="marquee-inner flex gap-12">logos...</div></div>',
    },
    {
        "id": "gsap_cta_gradient_flow",
        "content": "CTA section with gradient-flow: animated gradient background that shifts colors continuously. Combine with morph-bg shapes and magnetic button for maximum impact.",
        "category": "gsap_snippets",
        "tags": ["cta", "gradient", "flow", "animated"],
        "complexity": "medium",
        "impact_score": 9,
        "code": '<section data-animate="gradient-flow" style="background:linear-gradient(135deg, var(--color-primary), var(--color-secondary), var(--color-accent)); background-size:400% 400%;">',
    },
    {
        "id": "gsap_draw_svg_icons",
        "content": "SVG draw animation: SVG paths animate their stroke from 0 to full length. Great for icons, decorative lines, and illustrations. Elements need visible stroke.",
        "category": "gsap_snippets",
        "tags": ["svg", "draw", "stroke", "icons"],
        "complexity": "medium",
        "impact_score": 7,
        "code": '<svg data-animate="draw-svg"><path stroke="var(--color-primary)" stroke-width="2" fill="none" d="..."/></svg>',
    },

    # ====================================================
    # CREATIVE PROMPTS (10)
    # ====================================================
    {
        "id": "prompt_text_split_all_headings",
        "content": "RULE: Every section heading (h2) must use data-animate='text-split' with data-split-type='words'. Hero h1 uses chars. This creates consistency and professional motion across the entire page.",
        "category": "creative_prompts",
        "tags": ["rule", "headings", "text-split", "consistency"],
        "complexity": "low",
        "impact_score": 9,
    },
    {
        "id": "prompt_stagger_all_grids",
        "content": "RULE: Every card grid or list must use data-animate='stagger' on the parent with class='stagger-item' on children. Individual cards should also have data-animate='tilt' for hover interaction.",
        "category": "creative_prompts",
        "tags": ["rule", "stagger", "grids", "cards"],
        "complexity": "low",
        "impact_score": 8,
    },
    {
        "id": "prompt_magnetic_cta",
        "content": "RULE: Every primary CTA button must have data-animate='magnetic' for the magnetic hover effect. This makes buttons feel alive and interactive, dramatically improving click-through rates.",
        "category": "creative_prompts",
        "tags": ["rule", "magnetic", "cta", "buttons"],
        "complexity": "low",
        "impact_score": 8,
    },
    {
        "id": "prompt_no_generic_copy",
        "content": "RULE: Never use generic copy like 'Benvenuti', 'Siamo un azienda leader', 'Qualita e professionalita'. Every headline must be specific, emotional, and memorable. Max 6 words for hero.",
        "category": "creative_prompts",
        "tags": ["rule", "copy", "creative", "emotional"],
        "complexity": "low",
        "impact_score": 10,
    },
    {
        "id": "prompt_section_rhythm",
        "content": "DESIGN: Create visual rhythm by alternating section backgrounds (dark/light), layout types (centered/split/grid), and animation types. Never use the same layout twice in a row.",
        "category": "creative_prompts",
        "tags": ["rhythm", "alternating", "variety", "layout"],
        "complexity": "low",
        "impact_score": 8,
    },
    {
        "id": "prompt_generous_whitespace",
        "content": "DESIGN: Use generous whitespace - py-20 minimum for sections, gap-8 for grids, mb-16 between heading and content. Whitespace is the #1 signal of professional design. Cramped = amateur.",
        "category": "creative_prompts",
        "tags": ["whitespace", "spacing", "professional", "breathing"],
        "complexity": "low",
        "impact_score": 9,
    },
    {
        "id": "prompt_bold_typography",
        "content": "DESIGN: Use Google Fonts with character, never system fonts. Heading fonts: Playfair Display, Space Grotesk, DM Serif Display, Sora. Body: Inter, DM Sans, Plus Jakarta Sans. Size hierarchy: hero 5xl-8xl, section 3xl-4xl.",
        "category": "creative_prompts",
        "tags": ["typography", "fonts", "google-fonts", "hierarchy"],
        "complexity": "low",
        "impact_score": 9,
    },
    {
        "id": "prompt_decorative_elements",
        "content": "DESIGN: Add subtle decorative elements to hero sections: floating shapes (data-animate='float'), gradient orbs (blur-3xl with primary color), geometric patterns (dotted grids). They create depth and visual interest.",
        "category": "creative_prompts",
        "tags": ["decorative", "shapes", "floating", "depth"],
        "complexity": "medium",
        "impact_score": 7,
    },
    {
        "id": "prompt_dark_premium",
        "content": "DESIGN: Dark backgrounds feel premium. Use dark bg (#0f172a, #1a1a2e) with high-contrast text (white/90) and vibrant accent colors. Dark sites with proper contrast outperform light sites for luxury brands.",
        "category": "creative_prompts",
        "tags": ["dark", "premium", "luxury", "contrast"],
        "complexity": "low",
        "impact_score": 8,
    },
    {
        "id": "prompt_hover_states_everywhere",
        "content": "DESIGN: Every interactive element needs hover states. Cards: lift + shadow. Buttons: scale(1.05) + color shift. Links: underline slide. Images: subtle zoom. No dead zones on hover.",
        "category": "creative_prompts",
        "tags": ["hover", "interactive", "states", "feedback"],
        "complexity": "low",
        "impact_score": 8,
    },

    # ====================================================
    # PROFESSIONAL BLUEPRINTS (8) - Complete design guides per category
    # ====================================================
    {
        "id": "blueprint_restaurant",
        "content": """RESTAURANT WEBSITE BLUEPRINT - Award-winning design:
PALETTE: Dark moody (bg #1a1a2e or warm cream #fdf6ee), accent gold/terracotta/burgundy. NEVER plain white bg.
FONTS: Heading=Playfair Display (italic for elegance) or DM Serif Display, Body=Inter or Nunito Sans.
HERO: Full-bleed food photography with dark gradient overlay (from-black/70). Hero title: evocative, max 4-5 words like "Dove il Gusto Diventa Arte" or "L'Essenza della Cucina Italiana". NEVER "Benvenuti al Ristorante". Include scroll-down indicator arrow.
ABOUT: Split layout (image left 50%, text right 50%) with the chef/founder story. Stats: "Anni di esperienza", "Piatti signature", "Stelle Michelin" or similar. Use data-counter.
SERVICES/MENU: Card grid with hover lift effect. Each card has food emoji icon, dish category name, evocative 2-line description. Use stagger animation. Cards: rounded corners, subtle shadow, bg-[var(--color-bg-alt)].
TESTIMONIALS: Quote cards with large decorative quote marks (text-6xl opacity-20), customer name + "Cliente fedele da 3 anni" type specifics.
CTA: Gradient background section with "Prenota il Tuo Tavolo" + phone number + reservation button (magnetic).
CONTACT: Map + address + hours. Clean card layout.
OVERALL FEEL: Intimate, luxurious, warm. Like dining at a Michelin restaurant. Every image should make you hungry.""",
        "category": "professional_blueprints",
        "tags": ["restaurant", "blueprint", "food", "dining"],
        "complexity": "medium",
        "impact_score": 10,
    },
    {
        "id": "blueprint_saas",
        "content": """SAAS/TECH WEBSITE BLUEPRINT - Modern startup landing page:
PALETTE: Dark theme (bg #0f172a or #0a0a0a) with vibrant gradient accents (purple-to-blue #6c5ce7→#0984e3 or teal-to-cyan #00cec9→#0984e3). Light variant: clean white bg with bold primary.
FONTS: Heading=Space Grotesk or Sora (geometric, tech feel), Body=Inter or DM Sans. NEVER serif for tech.
HERO: Centered layout, massive headline (text-5xl to text-7xl, font-extrabold). Gradient text effect on key word. Subtitle: clear value proposition in 1-2 lines. Two CTAs: primary (filled, magnetic) + secondary (outlined). Decorative: floating gradient orbs (blur-3xl, opacity-10), dot grid pattern.
FEATURES: Bento grid (2x3 or asymmetric) with icon + title + description per card. Cards have subtle border, hover glow effect (hover:border-primary/30 hover:shadow-primary/10). Icons: tech-relevant emojis (⚡🚀🔒🎯📊🤖).
SERVICES: 3-column cards with number/icon top, bold title, benefit-focused description. Stagger animation. Dark cards on light bg or vice versa.
SOCIAL PROOF: Stats counter row (data-counter): "10K+ Utenti", "99.9% Uptime", "4.9/5 Rating", "150+ Integrazioni". Then logo marquee of partner companies.
TESTIMONIALS: Grid of cards with profile image, name, role, company, quote. Or carousel.
PRICING: 3-tier pricing cards, center card "highlighted" (border-primary, scale-105, "Popolare" badge). Features checklist.
CTA: Full-width gradient section with bold headline + email input + button. Gradient-flow animation.
OVERALL FEEL: Cutting-edge, trustworthy, fast. Like Vercel, Linear, or Stripe landing pages.""",
        "category": "professional_blueprints",
        "tags": ["saas", "blueprint", "tech", "startup", "landing"],
        "complexity": "medium",
        "impact_score": 10,
    },
    {
        "id": "blueprint_portfolio",
        "content": """PORTFOLIO/CREATIVE WEBSITE BLUEPRINT - Artistic showcase:
PALETTE: Monochrome base (pure black #0a0a0a + white #ffffff) with ONE accent color (electric blue, coral, or neon green). OR editorial warm (cream bg, rich black text, subtle accent).
FONTS: Heading=Clash Display or Cabinet Grotesk (bold statement), Body=Inter. For editorial: Playfair Display heading + DM Sans body.
HERO: Full-screen with name/title huge (text-8xl+), subtitle in smaller text. Minimal elements, lots of whitespace. Name can be outlined text (-webkit-text-stroke). Scroll indicator at bottom.
GALLERY: Masonry grid or spotlight layout with image-zoom effect. Images should dominate. Minimal text overlays. Hover reveals project title + category. Use image-reveal animation.
ABOUT: Short personal statement, split layout with portrait photo. Stats: "Progetti completati", "Anni di esperienza", "Clienti soddisfatti". Keep it minimal and impactful.
SERVICES: Minimal list with hover-expand or alternating rows. Not card-heavy - clean, editorial feel.
CONTACT: Super clean - just email, social links, and optional form. Centered layout.
OVERALL FEEL: Clean, confident, artistic. Let the work speak. Like a top Awwwards portfolio.""",
        "category": "professional_blueprints",
        "tags": ["portfolio", "blueprint", "creative", "artistic"],
        "complexity": "medium",
        "impact_score": 10,
    },
    {
        "id": "blueprint_ecommerce",
        "content": """E-COMMERCE WEBSITE BLUEPRINT - Product-focused shopping:
PALETTE: Clean white bg (#ffffff) with bold primary (deep blue, emerald, or black), warm accent for CTAs (coral, amber). Luxury variant: dark bg with gold/champagne accent.
FONTS: Heading=Outfit or Epilogue (modern commerce), Body=Inter or Plus Jakarta Sans. Luxury: DM Serif Display + Nunito Sans.
HERO: Split layout - product image 60% right with parallax, text 40% left with headline + price highlight + CTA. OR full-bleed product photo with text overlay. Badge: "Spedizione Gratuita" or "Nuovo Arrivo".
PRODUCTS/SERVICES: Card grid with product images (aspect-ratio 1/1 or 4/5, object-cover). Hover: image scale 1.05 + quick-view overlay. Price prominent. Cards: clean white bg, subtle shadow.
FEATURES: Icon row showing benefits: 🚚 Spedizione Gratis, 🔒 Pagamento Sicuro, ↩️ Reso Facile, ⭐ Garanzia Qualità.
TESTIMONIALS: Customer reviews with star rating ⭐⭐⭐⭐⭐, photo, verified badge.
CTA: Product showcase + urgency ("Ultimi Pezzi", "Solo Questa Settimana") + big CTA button.
OVERALL FEEL: Trust-building, clean, product-focused. Like a premium Shopify store.""",
        "category": "professional_blueprints",
        "tags": ["ecommerce", "blueprint", "shop", "product"],
        "complexity": "medium",
        "impact_score": 10,
    },
    {
        "id": "blueprint_business",
        "content": """BUSINESS/CORPORATE WEBSITE BLUEPRINT - Professional trust-building:
PALETTE: Navy/dark blue primary (#1e3a5f or #1e40af), light gray bg (#f8fafc), warm accent (amber #f59e0b or teal #0d9488). OR modern: white bg with bold single accent.
FONTS: Heading=Epilogue or Outfit (professional yet modern), Body=Inter or Source Sans 3. For trust: DM Serif Display + Nunito Sans.
HERO: Split layout or centered. Photo of team/office/product. Headline: benefit-focused, NOT "La Nostra Azienda". Example: "Trasformiamo Idee in Risultati Concreti". Trust badges below CTA.
ABOUT: Company story with timeline or alternating image-text rows. Stats: revenue, clients, years, team size with data-counter. Split image + text.
SERVICES: 3 or 4 cards with icons, hover tilt effect. Each service: icon, bold title, 2-line benefit description, "Scopri di più" link.
TEAM: Grid of team member cards with photo, name, role. Hover effect reveals bio. Professional headshots.
TESTIMONIALS: Client quotes with company logos. Spotlight style for premium feel.
CTA: Bold section with gradient or dark bg. "Richiedi una Consulenza Gratuita" + contact form or phone.
CONTACT: Professional form (name, email, phone, company, message) + office address + map.
OVERALL FEEL: Trustworthy, competent, approachable. Like a top consulting firm website.""",
        "category": "professional_blueprints",
        "tags": ["business", "blueprint", "corporate", "professional"],
        "complexity": "medium",
        "impact_score": 10,
    },
    {
        "id": "blueprint_blog",
        "content": """BLOG/EDITORIAL WEBSITE BLUEPRINT - Content-focused reading:
PALETTE: Warm editorial: cream bg (#faf8f5), rich black text (#1a1a1a), accent coral or deep red. Dark variant: #121212 bg, white text, neon accent.
FONTS: Heading=Playfair Display or Fraunces (editorial character), Body=Source Serif 4 or Lora for reading. Display: Clash Display for modern editorial.
HERO: Editorial mastheadstyle. Large publication name, featured article with full-bleed image, headline overlay. Clean, magazine-like. OR minimal centered title with typewriter effect.
ABOUT: Short mission statement, centered narrow layout (max-w-3xl). Personal tone. "Chi Sono" with portrait.
SERVICES/CATEGORIES: Minimal list or card grid showing content categories. Clean hover underline effects. Tag-based navigation.
GALLERY: Article cards with featured image, category badge, title, excerpt, read time. Masonry or clean grid.
CONTACT: Newsletter signup (email input + subscribe button) + social links. "Resta Aggiornato" CTA.
OVERALL FEEL: Intellectual, clean, readable. Generous whitespace. Like Medium or a premium magazine.""",
        "category": "professional_blueprints",
        "tags": ["blog", "blueprint", "editorial", "magazine"],
        "complexity": "medium",
        "impact_score": 10,
    },
    {
        "id": "blueprint_event",
        "content": """EVENT/COMMUNITY WEBSITE BLUEPRINT - Energetic and time-sensitive:
PALETTE: Vibrant and energetic. Primary: electric purple (#7c3aed) or hot pink (#ec4899), accent: yellow (#fbbf24) or cyan (#06b6d4). Dark bg for energy, or white bg for corporate events.
FONTS: Heading=Sora or Space Grotesk (bold, geometric), Body=Inter or DM Sans. Festival: Clash Display for max impact.
HERO: Full-screen with event name massive (text-7xl+), date and location prominent, countdown timer (data-counter), animated shapes background (float + morph-bg). CTA: "Iscriviti Ora" or "Acquista Biglietti" (magnetic, gradient).
ABOUT: Event description with key highlights. Split layout with event photo/video. "Perché Partecipare" with benefit icons.
SERVICES/SCHEDULE: Timeline of event schedule with time, talk title, speaker. OR tab-based day selector. Process steps: 1. Registrati, 2. Partecipa, 3. Connettiti.
TEAM/SPEAKERS: Speaker cards with photo, name, role, company, talk topic. Grid or carousel.
CTA: Urgency-driven. "Solo 50 Posti Rimasti" + countdown + ticket button. Gradient animated background.
CONTACT: Registration form (name, email, ticket type) + venue address + map.
OVERALL FEEL: Exciting, urgent, community-driven. Creates FOMO. Like a tech conference or festival website.""",
        "category": "professional_blueprints",
        "tags": ["event", "blueprint", "conference", "community"],
        "complexity": "medium",
        "impact_score": 10,
    },
    {
        "id": "blueprint_general",
        "content": """UNIVERSAL DESIGN PRINCIPLES FOR ALL PROFESSIONAL WEBSITES:
1. HERO must be min-h-screen with massive typography (text-5xl to text-8xl heading). Never smaller.
2. EVERY section heading: data-animate="text-split" data-split-type="words". Hero h1: chars or words.
3. EVERY CTA button: data-animate="magnetic". Primary buttons: filled bg-primary with hover scale. Secondary: outlined.
4. EVERY card grid: data-animate="stagger" parent, stagger-item children. Cards: hover:-translate-y-1 hover:shadow-xl transition.
5. Section spacing: py-20 lg:py-32 minimum. Content max-w-7xl mx-auto px-6.
6. Visual rhythm: alternate bg-[var(--color-bg)] and bg-[var(--color-bg-alt)] between sections.
7. DECORATIVE ELEMENTS in hero: 2-3 blurred gradient orbs (absolute, blur-3xl, opacity-5 to opacity-15, primary/accent colors).
8. Images: all use loading="lazy", rounded corners (rounded-2xl), overflow-hidden container with image-zoom.
9. NO generic Italian text ever. Every word must be specific to the business.
10. Font hierarchy: h1 text-5xl md:text-7xl, h2 text-3xl md:text-5xl, h3 text-xl md:text-2xl, body text-base md:text-lg.
11. Color usage: primary for CTAs and accents, secondary for supporting elements, accent for highlights and badges.
12. Footer: always include business name, description, nav links, social links, copyright with CURRENT_YEAR.""",
        "category": "professional_blueprints",
        "tags": ["universal", "blueprint", "rules", "all-categories"],
        "complexity": "low",
        "impact_score": 10,
    },

    # ====================================================
    # SECTION REFERENCES (8) - Concrete HTML/CSS examples
    # ====================================================
    {
        "id": "ref_hero_professional",
        "content": "Professional hero section: full viewport height, centered content with max-w-4xl, massive headline with text-split animation, subtitle with blur-in, two CTAs (primary filled + secondary outlined), decorative gradient orbs in background, optional scroll indicator arrow at bottom.",
        "category": "section_references",
        "tags": ["hero", "reference", "professional", "fullscreen"],
        "complexity": "medium",
        "impact_score": 10,
        "code": """<section class="min-h-screen relative overflow-hidden flex items-center bg-[var(--color-bg)]">
  <div class="absolute inset-0 overflow-hidden">
    <div class="absolute -top-40 -right-40 w-[500px] h-[500px] rounded-full blur-3xl opacity-10" data-animate="float" style="background: var(--color-primary);"></div>
    <div class="absolute -bottom-40 -left-40 w-[400px] h-[400px] rounded-full blur-3xl opacity-8" data-animate="float" data-delay="1" style="background: var(--color-accent);"></div>
  </div>
  <div class="relative max-w-7xl mx-auto px-6 py-32 text-center">
    <p class="text-sm uppercase tracking-widest text-[var(--color-primary)] font-semibold mb-6" data-animate="fade-up">Etichetta</p>
    <h1 class="text-5xl md:text-7xl lg:text-8xl font-heading font-extrabold text-[var(--color-text)] mb-8 leading-tight" data-animate="text-split" data-split-type="words">Headline Potente</h1>
    <p class="text-xl md:text-2xl text-[var(--color-text-muted)] max-w-2xl mx-auto mb-12" data-animate="blur-in" data-delay="0.3">Sottotitolo evocativo che crea desiderio.</p>
    <div class="flex flex-col sm:flex-row gap-4 justify-center" data-animate="fade-up" data-delay="0.5">
      <a href="#contact" class="px-8 py-4 bg-[var(--color-primary)] text-white rounded-xl font-semibold text-lg hover:scale-105 transition-transform shadow-lg" data-animate="magnetic">CTA Primaria</a>
      <a href="#about" class="px-8 py-4 border-2 border-[var(--color-primary)] text-[var(--color-primary)] rounded-xl font-semibold text-lg hover:bg-[var(--color-primary)] hover:text-white transition-all">Scopri di Più</a>
    </div>
  </div>
</section>""",
    },
    {
        "id": "ref_services_professional",
        "content": "Professional services section: section heading with pre-label, 3-column card grid with stagger animation, each card has emoji icon, bold title, description, hover lift effect. Alternating background from hero.",
        "category": "section_references",
        "tags": ["services", "reference", "cards", "grid"],
        "complexity": "low",
        "impact_score": 9,
        "code": """<section class="py-20 lg:py-32 bg-[var(--color-bg-alt)]">
  <div class="max-w-7xl mx-auto px-6">
    <div class="text-center mb-16">
      <p class="text-sm uppercase tracking-widest text-[var(--color-primary)] font-semibold mb-4" data-animate="fade-up">I Nostri Servizi</p>
      <h2 class="text-3xl md:text-5xl font-heading font-bold text-[var(--color-text)] mb-6" data-animate="text-split" data-split-type="words">Titolo Sezione</h2>
      <p class="text-lg text-[var(--color-text-muted)] max-w-2xl mx-auto" data-animate="fade-up" data-delay="0.2">Sottotitolo descrittivo.</p>
    </div>
    <div class="grid grid-cols-1 md:grid-cols-3 gap-8" data-animate="stagger">
      <div class="stagger-item group bg-[var(--color-bg)] rounded-2xl p-8 shadow-sm hover:-translate-y-2 hover:shadow-xl transition-all duration-300 border border-transparent hover:border-[var(--color-primary)]/20">
        <div class="text-4xl mb-4 group-hover:scale-110 transition-transform">🎯</div>
        <h3 class="text-xl font-heading font-bold text-[var(--color-text)] mb-3">Servizio</h3>
        <p class="text-[var(--color-text-muted)] leading-relaxed">Descrizione benefit-focused.</p>
      </div>
    </div>
  </div>
</section>""",
    },
    {
        "id": "ref_about_professional",
        "content": "Professional about section: split layout (image left 45%, text right 55%), decorative frame around image, stats counters row, business story paragraph. Image uses image-zoom effect.",
        "category": "section_references",
        "tags": ["about", "reference", "split", "stats"],
        "complexity": "medium",
        "impact_score": 9,
        "code": """<section class="py-20 lg:py-32 bg-[var(--color-bg)]">
  <div class="max-w-7xl mx-auto px-6">
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-16 items-center">
      <div class="relative" data-animate="fade-right">
        <div class="absolute -inset-4 border border-[var(--color-primary)]/20 rounded-2xl"></div>
        <div class="relative overflow-hidden rounded-2xl" data-animate="image-zoom">
          <img src="..." alt="..." class="w-full aspect-[4/3] object-cover" loading="lazy">
        </div>
      </div>
      <div>
        <p class="text-sm uppercase tracking-widest text-[var(--color-primary)] font-semibold mb-4" data-animate="fade-up">Chi Siamo</p>
        <h2 class="text-3xl md:text-5xl font-heading font-bold text-[var(--color-text)] mb-6" data-animate="text-split" data-split-type="words">La Nostra Storia</h2>
        <p class="text-lg text-[var(--color-text-muted)] leading-relaxed mb-8" data-animate="fade-up" data-delay="0.2">Testo descrittivo.</p>
        <div class="grid grid-cols-3 gap-6" data-animate="stagger">
          <div class="stagger-item text-center">
            <div class="text-3xl font-heading font-bold text-[var(--color-primary)]" data-counter="25" data-counter-suffix="+">0</div>
            <div class="text-sm text-[var(--color-text-muted)] mt-1">Anni</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</section>""",
    },
    {
        "id": "ref_testimonials_professional",
        "content": "Professional testimonials section: large decorative quote marks, client quote in larger text (text-xl), author name with role, optional profile image or initial avatar. Cards with subtle bg and shadow.",
        "category": "section_references",
        "tags": ["testimonials", "reference", "quotes", "social-proof"],
        "complexity": "low",
        "impact_score": 8,
        "code": """<section class="py-20 lg:py-32 bg-[var(--color-bg-alt)]">
  <div class="max-w-7xl mx-auto px-6">
    <div class="text-center mb-16">
      <h2 class="text-3xl md:text-5xl font-heading font-bold text-[var(--color-text)]" data-animate="text-split" data-split-type="words">Cosa Dicono di Noi</h2>
    </div>
    <div class="grid grid-cols-1 md:grid-cols-3 gap-8" data-animate="stagger">
      <div class="stagger-item bg-[var(--color-bg)] rounded-2xl p-8 shadow-sm relative">
        <div class="text-6xl text-[var(--color-primary)] opacity-20 absolute top-4 left-6 font-serif">"</div>
        <p class="text-lg text-[var(--color-text)] leading-relaxed mb-6 relative z-10 pt-8">Citazione specifica e dettagliata.</p>
        <div class="flex items-center gap-3">
          <div class="w-12 h-12 rounded-full bg-[var(--color-primary)] flex items-center justify-center text-white font-bold">M</div>
          <div>
            <p class="font-semibold text-[var(--color-text)]">Nome Cognome</p>
            <p class="text-sm text-[var(--color-text-muted)]">Ruolo, Azienda</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</section>""",
    },
    {
        "id": "ref_cta_professional",
        "content": "Professional CTA section: bold gradient or dark background with gradient-flow animation, large headline (text-4xl), subtitle, single prominent CTA button with magnetic effect. Creates urgency.",
        "category": "section_references",
        "tags": ["cta", "reference", "conversion", "gradient"],
        "complexity": "low",
        "impact_score": 9,
        "code": """<section class="py-20 lg:py-32 relative overflow-hidden" data-animate="gradient-flow" style="background: linear-gradient(135deg, var(--color-primary), var(--color-secondary)); background-size: 400% 400%;">
  <div class="absolute inset-0 overflow-hidden">
    <div class="absolute top-0 right-0 w-96 h-96 rounded-full blur-3xl opacity-20 bg-white" data-animate="float"></div>
  </div>
  <div class="relative max-w-4xl mx-auto px-6 text-center">
    <h2 class="text-3xl md:text-5xl font-heading font-bold text-white mb-6" data-animate="text-split" data-split-type="words">Pronto a Iniziare?</h2>
    <p class="text-xl text-white/80 mb-10 max-w-2xl mx-auto" data-animate="fade-up" data-delay="0.2">Testo persuasivo che crea urgenza.</p>
    <a href="#contact" class="inline-block px-10 py-5 bg-white text-[var(--color-primary)] rounded-xl font-bold text-lg hover:scale-105 transition-transform shadow-2xl" data-animate="magnetic">Testo CTA</a>
  </div>
</section>""",
    },
    {
        "id": "ref_contact_professional",
        "content": "Professional contact section: split layout with form on one side and contact info (address, phone, email, hours) on the other. Form has proper inputs with labels, submit button with magnetic effect.",
        "category": "section_references",
        "tags": ["contact", "reference", "form", "split"],
        "complexity": "medium",
        "impact_score": 8,
        "code": """<section class="py-20 lg:py-32 bg-[var(--color-bg)]" id="contact">
  <div class="max-w-7xl mx-auto px-6">
    <div class="text-center mb-16">
      <h2 class="text-3xl md:text-5xl font-heading font-bold text-[var(--color-text)]" data-animate="text-split" data-split-type="words">Contattaci</h2>
      <p class="text-lg text-[var(--color-text-muted)] mt-4" data-animate="fade-up">Sottotitolo.</p>
    </div>
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-16">
      <div data-animate="fade-right">
        <form class="space-y-6">
          <div><label class="block text-sm font-medium text-[var(--color-text)] mb-2">Nome</label><input type="text" class="w-full px-4 py-3 rounded-xl border border-[var(--color-text-muted)]/20 bg-[var(--color-bg-alt)] focus:border-[var(--color-primary)] focus:ring-2 focus:ring-[var(--color-primary)]/20 outline-none transition"></div>
          <div><label class="block text-sm font-medium text-[var(--color-text)] mb-2">Email</label><input type="email" class="w-full px-4 py-3 rounded-xl border border-[var(--color-text-muted)]/20 bg-[var(--color-bg-alt)] focus:border-[var(--color-primary)] focus:ring-2 focus:ring-[var(--color-primary)]/20 outline-none transition"></div>
          <div><label class="block text-sm font-medium text-[var(--color-text)] mb-2">Messaggio</label><textarea rows="4" class="w-full px-4 py-3 rounded-xl border border-[var(--color-text-muted)]/20 bg-[var(--color-bg-alt)] focus:border-[var(--color-primary)] focus:ring-2 focus:ring-[var(--color-primary)]/20 outline-none transition resize-none"></textarea></div>
          <button type="submit" class="w-full py-4 bg-[var(--color-primary)] text-white rounded-xl font-semibold hover:scale-[1.02] transition-transform" data-animate="magnetic">Invia Messaggio</button>
        </form>
      </div>
      <div class="space-y-8" data-animate="fade-left">
        <div class="flex gap-4"><div class="w-12 h-12 rounded-xl bg-[var(--color-primary)]/10 flex items-center justify-center text-[var(--color-primary)]">📍</div><div><p class="font-semibold text-[var(--color-text)]">Indirizzo</p><p class="text-[var(--color-text-muted)]">Via Example 123</p></div></div>
      </div>
    </div>
  </div>
</section>""",
    },
    {
        "id": "ref_features_professional",
        "content": "Professional features section: bento grid layout with mixed card sizes, icon + title + description per feature. Cards have gradient border on hover, stagger entrance animation. Modern tech feel.",
        "category": "section_references",
        "tags": ["features", "reference", "bento", "grid"],
        "complexity": "medium",
        "impact_score": 9,
        "code": """<section class="py-20 lg:py-32 bg-[var(--color-bg)]">
  <div class="max-w-7xl mx-auto px-6">
    <div class="text-center mb-16">
      <p class="text-sm uppercase tracking-widest text-[var(--color-primary)] font-semibold mb-4" data-animate="fade-up">Funzionalità</p>
      <h2 class="text-3xl md:text-5xl font-heading font-bold text-[var(--color-text)] mb-6" data-animate="text-split" data-split-type="words">Perché Scegliere Noi</h2>
    </div>
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6" data-animate="stagger">
      <div class="stagger-item group bg-[var(--color-bg-alt)] rounded-2xl p-8 border border-transparent hover:border-[var(--color-primary)]/30 hover:shadow-lg hover:shadow-[var(--color-primary)]/5 transition-all duration-300">
        <div class="w-14 h-14 rounded-xl bg-[var(--color-primary)]/10 flex items-center justify-center text-2xl mb-5 group-hover:scale-110 transition-transform">⚡</div>
        <h3 class="text-lg font-heading font-bold text-[var(--color-text)] mb-3">Feature Title</h3>
        <p class="text-[var(--color-text-muted)] leading-relaxed">Benefit-focused description.</p>
      </div>
    </div>
  </div>
</section>""",
    },
    {
        "id": "ref_footer_professional",
        "content": "Professional footer: dark background, multi-column layout with business info, nav links, contact details. Social media icons. Copyright bar at bottom. Clean, comprehensive.",
        "category": "section_references",
        "tags": ["footer", "reference", "navigation", "dark"],
        "complexity": "low",
        "impact_score": 7,
        "code": """<footer class="bg-[var(--color-text)] text-white/80 pt-16 pb-8">
  <div class="max-w-7xl mx-auto px-6">
    <div class="grid grid-cols-1 md:grid-cols-4 gap-12 mb-12">
      <div class="md:col-span-2">
        <h3 class="text-2xl font-heading font-bold text-white mb-4">{{BUSINESS_NAME}}</h3>
        <p class="text-white/60 leading-relaxed max-w-md">{{FOOTER_DESCRIPTION}}</p>
      </div>
      <div>
        <h4 class="font-semibold text-white mb-4">Link Utili</h4>
        <ul class="space-y-2 text-white/60"><li><a href="#about" class="hover:text-white transition">Chi Siamo</a></li><li><a href="#services" class="hover:text-white transition">Servizi</a></li><li><a href="#contact" class="hover:text-white transition">Contatti</a></li></ul>
      </div>
      <div>
        <h4 class="font-semibold text-white mb-4">Contatti</h4>
        <ul class="space-y-2 text-white/60"><li>{{CONTACT_EMAIL}}</li><li>{{CONTACT_PHONE}}</li><li>{{CONTACT_ADDRESS}}</li></ul>
      </div>
    </div>
    <div class="border-t border-white/10 pt-8 text-center text-white/40 text-sm">
      <p>&copy; {{CURRENT_YEAR}} {{BUSINESS_NAME}}. Tutti i diritti riservati.</p>
    </div>
  </div>
</footer>""",
    },
]


def seed_all():
    """Seed all design patterns into ChromaDB."""
    count = 0
    for p in PATTERNS:
        add_pattern(
            pattern_id=p["id"],
            content=p["content"],
            category=p["category"],
            tags=p.get("tags", []),
            complexity=p.get("complexity", "medium"),
            impact_score=p.get("impact_score", 5),
            code_snippet=p.get("code", ""),
        )
        count += 1
    print(f"Seeded {count} design patterns into ChromaDB.")
    return count


if __name__ == "__main__":
    seed_all()
    stats = get_collection_stats()
    print(f"Collection stats: {stats}")
