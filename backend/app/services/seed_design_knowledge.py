"""
Seed script for Design Knowledge ChromaDB.
Populates the vector database with 175+ design patterns covering
scroll effects, text animations, image effects, layout patterns,
GSAP snippets, creative prompts, Aceternity UI, Magic UI, UIverse,
and modern interaction patterns.

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

    # ====================================================
    # CODEPEN EFFECTS (9) - Advanced CSS/JS techniques from real demos
    # ====================================================
    {
        "id": "codepen_expanding_gallery",
        "content": """Expanding gallery with CSS :has() selector: a grid of overlapping image cards where hovering one card causes it to expand (6fr) while others shrink (1fr) using CSS grid-template-columns animation. Cards use corner-shape:notch for decorative cut corners and overlap via grid-column spanning. Pure CSS, no JavaScript. The :has(:nth-child(N):hover) pattern on the parent drives all state changes. Creates an elegant, interactive image showcase with smooth 300ms transitions.""",
        "category": "micro_interactions",
        "tags": ["gallery", "hover", "grid", "expanding", "css-has", "interactive"],
        "complexity": "medium",
        "impact_score": 9,
        "code": """.wrapper {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr 1fr 1fr 1fr 1fr 1fr 1fr;
  aspect-ratio: 2/1;
  transition: grid 300ms ease-in-out;
}
.wrapper:has(:nth-child(1):hover) { grid-template-columns: 6fr 1fr 1fr 1fr 1fr 1fr 1fr 1fr 1fr; }
.wrapper > * {
  grid-row: 1;
  overflow: hidden;
  border-radius: 0 0 0 30%/0 0 0 50%;
  transition: all 300ms ease-in-out;
  background-size: cover;
}
.wrapper > :nth-child(1) { grid-column: 1 / span 3; }
.wrapper > :nth-child(2) { grid-column: 3 / span 3; }""",
    },
    {
        "id": "codepen_scroll_focus_text",
        "content": """Scroll-driven text focus effect using CSS view-timeline and scroll-linked animations. Text starts dim/muted and becomes bright/focused as it scrolls into the viewport center. A sticky visual panel on the right shows geometric shapes that fade in/out synced to scroll position. Uses CSS timeline-scope, view-timeline-name, and animation-timeline properties for zero-JS scroll synchronization. The 'focus-text' class uses animation-range: cover 0% cover 100% to map scroll position to opacity/color. Creates an editorial, storytelling experience with text that 'lights up' as you read.""",
        "category": "scroll_effects",
        "tags": ["scroll-driven", "text-focus", "view-timeline", "css-animation", "editorial", "storytelling"],
        "complexity": "high",
        "impact_score": 9,
        "code": """.focus-text {
  font-size: 3.5rem;
  color: var(--text-muted);
  animation: content-focus linear both;
  animation-timeline: view();
  animation-range: cover 0% cover 100%;
}
.scroll-section {
  view-timeline-axis: block;
  view-timeline-inset: 40% 40%;
}
.shape-container {
  animation-name: shape-fade;
  animation-fill-mode: both;
  animation-timing-function: cubic-bezier(0.4, 0, 0.2, 1);
}""",
    },
    {
        "id": "codepen_warm_product_card",
        "content": """Warm minimal product card with CSS-only day-to-night mode toggle. Uses corner-shape:squircle for smooth Apple-style rounded corners. The card has glassmorphism (backdrop-filter:blur + semi-transparent bg), warm radial gradient backgrounds with soft golden tones, and multi-layer box-shadows for depth. The day/night transition changes entire palette using CSS custom properties. Split layout: image left in squircle container, info right with brand, title (scaleY(2) for condensed elegance), price, description. CTA button uses golden gradient with hover lift. Creates a premium, boutique feel perfect for luxury e-commerce.""",
        "category": "layout_patterns",
        "tags": ["product-card", "glassmorphism", "squircle", "luxury", "warm", "ecommerce", "css-only"],
        "complexity": "medium",
        "impact_score": 9,
        "code": """.product-card {
  border-radius: 12rem;
  corner-shape: squircle;
  background: linear-gradient(145deg, rgba(255,255,255,0.75), rgba(255,255,255,0.55));
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255,255,255,0.4);
  box-shadow: 0 40px 80px rgba(206,168,132,0.1), 0 20px 40px rgba(0,0,0,0.1), 0 0 120px rgba(198,169,126,0.25), inset 0 1px 0 rgba(255,255,255,0.6);
}
.btn-primary {
  background: linear-gradient(145deg, #d8a45c, #b97a2f);
  box-shadow: 0 8px 20px rgba(201,155,94,0.35), 0 0 25px rgba(201,155,94,0.15), inset 0 2px 6px rgba(255,255,255,0.3);
}""",
    },
    {
        "id": "codepen_text_fill_scroll",
        "content": """Text fill on scroll with GSAP ScrollTrigger: text starts with muted color and progressively fills with a bright foreground color as the user scrolls. Uses background-clip:text with a gradient (bright 50%, muted 60%) and animates background-size from 0% to 200% via GSAP scrub. The text appears to be 'painted' word-by-word as you scroll. Dark background (#0b0c0f), light text (#f3f4f6), muted base (#3f434a). Font: Syne, bold 600, large clamp(22px, 4vw, 48px). Simple but extremely effective for hero/manifesto sections. Respects prefers-reduced-motion.""",
        "category": "text_animations",
        "tags": ["text-fill", "scroll", "gsap", "scrub", "progressive", "hero", "manifesto"],
        "complexity": "medium",
        "impact_score": 10,
        "code": """.fill-text > span {
  -webkit-background-clip: text;
  background-clip: text;
  background-color: var(--muted);
  background-image: linear-gradient(135deg, var(--fg) 50%, var(--muted) 60%);
  background-size: 0% 200%;
  color: transparent;
  will-change: background-size;
}
/* GSAP */
gsap.to(target, {
  backgroundSize: "200% 200%",
  ease: "none",
  scrollTrigger: { trigger: ".js-fill", start: "top 80%", end: "bottom 35%", scrub: true }
});""",
    },
    {
        "id": "codepen_dark_bento_blog",
        "content": """Dark bento-grid blog layout with glassmorphism UI: full dark theme (#0a0a0a) with purple-indigo gradient accents (#667eea → #764ba2). Features: glass cards (rgba(255,255,255,0.03) + backdrop-blur(10px)), gradient-border technique (background padding-box + border-box), animated shimmer loading effect (background-position sliding), bento cards with scale(1.02)+translateY(-4px) hover, floating keyframe animation, gradient text via background-clip, and cursor-glow follower. The gradient-border creates an animated rainbow border using transparent border + gradient background. Perfect for dark SaaS/tech/blog layouts.""",
        "category": "layout_patterns",
        "tags": ["bento", "dark", "glassmorphism", "gradient-border", "shimmer", "blog", "tech"],
        "complexity": "medium",
        "impact_score": 9,
        "code": """.glass {
  background: rgba(255,255,255,0.03);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255,255,255,0.1);
}
.gradient-border {
  background: linear-gradient(#0a0a0a, #0a0a0a) padding-box,
              linear-gradient(135deg, #667eea, #764ba2, #f093fb) border-box;
  border: 2px solid transparent;
}
@keyframes shimmer {
  0% { background-position: -1000px 0; }
  100% { background-position: 1000px 0; }
}
.bento-card:hover { transform: scale(1.02) translateY(-4px); }""",
    },
    {
        "id": "codepen_fullscreen_slider",
        "content": """Full-screen animated image slider with GSAP: immersive slider with background images covering entire viewport, massive title text (clamp(64px, 15vw, 200px)), custom circular cursor (80px border circle following mouse with GSAP), and smooth slide transitions. Each slide has: bg image, large title with word-by-word reveal (inline-block spans with will-change:transform), description in small uppercase tracking, location info. Transitions use GSAP timeline with staggered word animations. Custom cursor replaces default, showing navigation arrows. Dark cinematic feel with subtle white borders. Perfect for hero sections, portfolio showcases, and immersive full-page experiences.""",
        "category": "micro_interactions",
        "tags": ["slider", "fullscreen", "gsap", "cursor", "immersive", "hero", "portfolio", "cinematic"],
        "complexity": "high",
        "impact_score": 10,
        "code": """.slider { width: 100%; height: 100vh; overflow: hidden; cursor: none; }
.slider__title {
  font-size: clamp(64px, 15vw, 200px);
  font-weight: 700; color: #fff;
  line-height: 1.15; letter-spacing: -0.02em;
}
.slider__title span { display: inline-block; will-change: transform; }
.slider__cursor {
  position: fixed; width: 80px; height: 80px;
  border-radius: 50%; border: 1px solid rgba(255,255,255,0.3);
  pointer-events: none; will-change: transform; z-index: 10;
}""",
    },
    {
        "id": "codepen_scroll_card_fan",
        "content": """CSS scroll-based card fan animation: cards spread from a stacked deck into a fan layout as user scrolls, using CSS sibling-index() and scroll-driven animations. Each card calculates its rotation angle based on its sibling index: --angle = (angle-min + angle-step * index) * progress. Also features: 3D calendar perspective reveal (translateZ + rotateX on scroll), radial progress spinner animated by scroll (conic-gradient with CSS counter showing percentage), image clip-path morphing on scroll (shape() function), and staggered review card entries. All animations use animation-timeline: view(block) with no JavaScript. Creates rich, layered scroll storytelling.""",
        "category": "scroll_effects",
        "tags": ["card-fan", "scroll-driven", "css-animation", "sibling-index", "perspective", "radial-progress", "no-js"],
        "complexity": "high",
        "impact_score": 10,
        "code": """.card {
  --index: sibling-index();
  --count: sibling-count();
  --angle: calc(var(--angle-min) + var(--angle-step) * var(--index));
  --angle-deg: calc((var(--angle) * var(--card-rotation-progress)) * 1deg);
  position: absolute;
  transform-origin: bottom center;
  rotate: var(--angle-deg);
  animation: cardUp 1ms ease-out both;
  animation-timeline: view(block);
}
.spinner { background: conic-gradient(from 0deg, #8b5cf6 0deg, #8b5cf6 var(--progress), transparent var(--progress)); }
.cover-image { clip-path: shape(...); animation-timeline: view(block); }""",
    },
    {
        "id": "codepen_obsidian_gold_landing",
        "content": """Obsidian gold luxury landing page template (Tailwind + GSAP): dark theme (#121212 bg, #F5F5F0 text, #C5A059 gold accent). Features: page loader with fade-in text, stagger reveal-on-load animations, -webkit-text-stroke for decorative outlined headings (1px gold stroke on transparent), glass-panel (rgba(255,255,255,0.06) + backdrop-blur + subtle border), showcase-frame with radial gold gradients and repeating diagonal line pattern overlay. Image containers with hover scale(1.1) zoom. Custom gold scrollbar. Prefers-reduced-motion support. The gold+dark combination creates an ultra-premium feel for luxury brands, high-end restaurants, and exclusive services. Uses Cormorant Garamond serif for elegance.""",
        "category": "professional_blueprints",
        "tags": ["luxury", "dark", "gold", "tailwind", "gsap", "text-stroke", "glass", "premium", "landing"],
        "complexity": "medium",
        "impact_score": 10,
        "code": """:root { --bg:#121212; --fg:#F5F5F0; --gold:#C5A059; }
.text-stroke {
  -webkit-text-stroke: 1px rgba(197,160,89,0.55);
  color: rgba(245,245,240,0.05);
  text-shadow: 0 0 18px rgba(197,160,89,0.1);
}
.glass-panel {
  background: rgba(255,255,255,0.06);
  border: 1px solid rgba(255,255,255,0.1);
  backdrop-filter: blur(10px);
}
.showcase-frame {
  border: 1px solid rgba(197,160,89,0.25);
  background: radial-gradient(700px at 20% 20%, rgba(197,160,89,0.18), transparent 60%);
}
.showcase-frame::before {
  background: repeating-linear-gradient(135deg, rgba(255,255,255,0.06) 0px, rgba(255,255,255,0.06) 1px, transparent 1px, transparent 14px);
}""",
    },
    {
        "id": "codepen_glassmorphism_portfolio",
        "content": """Modern glassmorphism portfolio with animated canvas background and theme toggle. Dark (#050505) and light (#e8e8e8) themes via CSS custom properties and [data-theme] attribute. App-style layout: fixed sidebar (260px, glassmorphism panel with blur(20px)), main scrollable content area. Nav links with translateX(4px) hover shift. Bento grid for project cards. Canvas background with animated particles/shapes (Three.js or vanilla Canvas). CSS variables for consistent glass: --panel-bg: rgba(20,20,25,0.4), --panel-border: rgba(255,255,255,0.08), --glass-blur: 20px. Accent color #6d5dfc (indigo-purple). Avatar with gradient. Smooth 0.5s cubic-bezier transitions on all theme changes. Creates a dashboard-like portfolio with depth and interactivity.""",
        "category": "layout_patterns",
        "tags": ["glassmorphism", "portfolio", "sidebar", "canvas", "theme-toggle", "bento", "dashboard", "dark-light"],
        "complexity": "high",
        "impact_score": 9,
        "code": """:root {
  --panel-bg: rgba(20,20,25,0.4);
  --panel-border: rgba(255,255,255,0.08);
  --panel-hover: rgba(255,255,255,0.12);
  --glass-blur: 20px;
  --radius-lg: 24px;
}
[data-theme="light"] {
  --panel-bg: rgba(255,255,255,0.4);
  --panel-border: rgba(0,0,0,0.05);
}
.sidebar {
  background: var(--panel-bg);
  border: 1px solid var(--panel-border);
  backdrop-filter: blur(var(--glass-blur));
  border-radius: var(--radius-lg);
}
.nav-link:hover { background: var(--panel-hover); transform: translateX(4px); }""",
    },
    # --- CodePen: Highlighter SVG Draw Effect ---
    {
        "id": "codepen_svg_highlighter",
        "content": """SVG hand-drawn highlighter effect for navigation menus and text emphasis. Each menu item
has an SVG path positioned absolutely behind/around the text that looks like a hand-drawn circle or underline.
On click (or hover), GSAP DrawSVGPlugin animates the stroke from 0% to 100%, creating the appearance of someone
circling the word with a marker pen in real-time. Two overlapping SVG paths with different colors (a lighter
background stroke and a darker foreground stroke) create depth and a natural pen-on-paper feel. The SVG uses
preserveAspectRatio="none" so it stretches to fit any word length. Paths use quadratic bezier curves (Q commands)
for organic, imperfect circular shapes. Reset animation on other items when a new one is selected. The effect
works beautifully for portfolio navigation, service category selectors, or any interactive text menu where you
want a playful, editorial, hand-crafted aesthetic. Can be adapted to underlines or squiggly lines instead of
circles. Font pairing: bold uppercase sans-serif (900 weight) for maximum impact.""",
        "category": "interactive_elements",
        "tags": ["svg", "draw-svg", "highlighter", "hand-drawn", "navigation", "menu", "gsap", "stroke-animation", "editorial", "click-effect"],
        "complexity": "medium",
        "impact_score": 9,
        "code": """.link {
  position: relative;
  display: inline-flex;
  font-size: 80px;
  font-weight: 900;
  text-transform: uppercase;
  color: #c2c1bd;
  text-decoration: none;
}
.link:hover, .link.active { color: #1e1f21; }
.word { position: relative; z-index: 1; }
.highlighter {
  position: absolute;
  left: -50px; right: -50px; bottom: -20px;
  width: calc(100% + 100px);
  z-index: 2;
  scale: 1.1;
}
/* SVG path: organic hand-drawn circle */
<svg viewBox="0 0 220 80" preserveAspectRatio="none">
  <path class="stroke-path stroke-path--2"
    d="M 20 40 Q 10 10 70 15 Q 140 0 190 35 Q 210 55 180 65 Q 100 85 40 70 Q 15 60 30 45"
    fill="none" stroke="#A0A7E1" stroke-width="5"
    stroke-linecap="round" stroke-linejoin="round"/>
  <path class="stroke-path stroke-path--1"
    d="M 20 40 Q 10 10 70 15 Q 140 0 190 35 Q 210 55 180 65 Q 100 85 40 70 Q 15 60 30 45"
    fill="none" stroke="#3E4DC2" stroke-width="5"
    stroke-linecap="round" stroke-linejoin="round"/>
</svg>
/* GSAP: */
gsap.registerPlugin(DrawSVGPlugin);
gsap.set(allPaths, { drawSVG: '0% 0%', opacity: 0 });
container.addEventListener('click', () => {
  gsap.to(allPaths, { drawSVG: '0% 0%', opacity: 0, duration: 0.3 });
  gsap.to(paths, { drawSVG: '0% 100%', opacity: 1, duration: 0.8, ease: 'power2.out' });
});""",
    },

    # ====================================================
    # ACETERNITY UI EFFECTS (16)
    # ====================================================
    {
        "id": "aceternity_spotlight",
        "content": "Spotlight effect (Aceternity UI): a radial gradient glow that scales in from off-center, drawing attention to hero sections or featured cards. Starts invisible and scaled-down (50%), animates to full opacity and scale over 2s with a 0.75s delay. Uses a large CSS radial-gradient positioned absolutely behind the content. The glow color matches the brand primary. Best for dark backgrounds where the light cone is clearly visible. Creates a cinematic, stage-lighting feel perfect for SaaS hero sections and product showcases.",
        "category": "visual_effects",
        "tags": ["spotlight", "glow", "hero", "attention", "aceternity", "radial-gradient"],
        "complexity": "medium",
        "impact_score": 9,
        "code": """@keyframes spotlight {
  0% { opacity: 0; transform: translate(-72%, -62%) scale(0.5); }
  100% { opacity: 1; transform: translate(-50%, -40%) scale(1); }
}
.spotlight {
  position: absolute; top: 0; left: 0;
  width: 140%; height: 200%;
  background: radial-gradient(ellipse, rgba(var(--color-primary-rgb),0.15) 0%, transparent 70%);
  animation: spotlight 2s ease 0.75s 1 forwards;
  opacity: 0; pointer-events: none;
}""",
    },
    {
        "id": "aceternity_meteor_shower",
        "content": "Meteor shower effect (Aceternity UI): animated diagonal beams that streak across a container background like falling stars. Multiple beams at 215-degree angle translate -500px horizontally while fading from full opacity to transparent. Each meteor has a randomized delay and duration (5-15s) for organic feel. Thin white/colored lines (1-2px width, 50-100px length) with a soft glow trail via box-shadow. Creates a magical, cosmic atmosphere. Best for dark hero sections, card backgrounds, and event pages. Spawn 10-30 meteors with random top/left positions.",
        "category": "backgrounds",
        "tags": ["meteor", "particles", "cosmic", "animated", "aceternity", "beams"],
        "complexity": "medium",
        "impact_score": 8,
        "code": """@keyframes meteor {
  0% { transform: rotate(215deg) translateX(0); opacity: 1; }
  70% { opacity: 1; }
  100% { transform: rotate(215deg) translateX(-500px); opacity: 0; }
}
.meteor {
  position: absolute; top: 50%; left: 50%;
  width: 1px; height: 80px;
  background: linear-gradient(to bottom, rgba(255,255,255,0.8), transparent);
  border-radius: 50%;
  box-shadow: 0 0 6px 2px rgba(255,255,255,0.3);
  animation: meteor 5s linear infinite;
}""",
    },
    {
        "id": "aceternity_3d_card",
        "content": "3D card tilt effect (Aceternity UI): card rotates towards the mouse pointer in 3D space using CSS perspective and transform. On mousemove, calculate rotateX and rotateY based on cursor position relative to card center (typically +/-15deg range). Card children can have translateZ values to create layered depth (icons float above, shadows below). Uses perspective: 1000px on parent, will-change: transform on card. Smooth transition on mouse-leave to reset rotation. Creates a premium, tactile feel for feature cards, pricing tiers, and portfolio items.",
        "category": "card_designs",
        "tags": ["3d", "tilt", "perspective", "hover", "aceternity", "interactive", "depth"],
        "complexity": "medium",
        "impact_score": 9,
        "code": """.card-3d-container { perspective: 1000px; }
.card-3d {
  transform-style: preserve-3d;
  transition: transform 0.3s ease;
  will-change: transform;
}
.card-3d:hover { transform: rotateY(10deg) rotateX(-5deg); }
.card-3d .card-float { transform: translateZ(50px); transition: transform 0.3s ease; }
.card-3d .card-shadow { transform: translateZ(-20px); filter: blur(10px); opacity: 0.3; }
/* JS: card.style.transform = `rotateY(${(x-cx)/rect.width*30}deg) rotateX(${-(y-cy)/rect.height*30}deg)` */""",
    },
    {
        "id": "aceternity_background_beams",
        "content": "Background beams effect (Aceternity UI): multiple SVG path-based beams that curve across the hero section background, creating organic light trails. Each beam follows a unique cubic bezier path, animated with stroke-dashoffset or motion path. Beams use gradient strokes (primary to transparent) with 1-3px width and soft glow via filter:blur. Stagger beam animations with different durations (3-8s) and delays for a living, breathing background. Best on dark backgrounds. Creates a futuristic, data-flow aesthetic perfect for SaaS, AI, and tech landing pages.",
        "category": "backgrounds",
        "tags": ["beams", "svg", "paths", "hero", "aceternity", "futuristic", "tech"],
        "complexity": "high",
        "impact_score": 9,
        "code": """.beam-container { position: absolute; inset: 0; overflow: hidden; }
.beam-path {
  stroke: url(#beam-gradient); stroke-width: 2; fill: none;
  stroke-dasharray: 500; stroke-dashoffset: 500;
  animation: beam-draw 4s ease-in-out infinite alternate;
  filter: blur(1px);
}
@keyframes beam-draw {
  0% { stroke-dashoffset: 500; opacity: 0.3; }
  50% { opacity: 1; }
  100% { stroke-dashoffset: 0; opacity: 0.3; }
}
/* SVG: <path d="M0,200 C150,100 350,300 500,150 S800,50 1000,200" class="beam-path"/> */""",
    },
    {
        "id": "aceternity_wavy_background",
        "content": "Wavy background effect (Aceternity UI): animated SVG waves layered at the bottom or behind content, creating an organic, fluid motion. Multiple wave paths with different amplitudes, frequencies, and animation speeds produce a living ocean effect. Each wave layer has decreasing opacity (0.7, 0.5, 0.3) and different fill colors (primary shades). Animate via CSS transform translateX with different durations (5-15s). Best for creative sections, hero bottoms, and section dividers. Creates a calm, organic feel contrasting sharp geometric layouts.",
        "category": "backgrounds",
        "tags": ["waves", "svg", "organic", "animated", "aceternity", "fluid", "ocean"],
        "complexity": "medium",
        "impact_score": 8,
        "code": """.wave-container { position: absolute; bottom: 0; left: 0; width: 200%; }
.wave { animation: wave-move linear infinite; }
.wave-1 { animation-duration: 7s; opacity: 0.7; }
.wave-2 { animation-duration: 11s; opacity: 0.5; }
.wave-3 { animation-duration: 15s; opacity: 0.3; }
@keyframes wave-move {
  0% { transform: translateX(0); }
  100% { transform: translateX(-50%); }
}
/* SVG wave: <path d="M0,100 C200,150 400,50 600,100 C800,150 1000,50 1200,100 V200 H0 Z"/> */""",
    },
    {
        "id": "aceternity_aurora_background",
        "content": "Aurora background effect (Aceternity UI): subtle northern lights animation using layered gradient blobs that shift position, scale, and color over time. Multiple absolutely-positioned divs (200-600px) with radial gradients in primary/accent colors, large blur (blur-3xl to blur-[100px]), and low opacity (5-20%). Animate with CSS keyframes changing transform translate and scale over 10-20s infinite loops. Each blob has different timing for organic, never-repeating movement. Creates an ethereal, premium atmosphere. Best for dark hero sections and full-page backgrounds on SaaS and creative sites.",
        "category": "backgrounds",
        "tags": ["aurora", "gradient", "blobs", "animated", "aceternity", "ethereal", "premium"],
        "complexity": "medium",
        "impact_score": 9,
        "code": """.aurora-blob {
  position: absolute; border-radius: 50%;
  filter: blur(80px); opacity: 0.15;
  will-change: transform;
}
.aurora-1 {
  width: 500px; height: 500px; top: -20%; left: 10%;
  background: radial-gradient(circle, var(--color-primary), transparent 70%);
  animation: aurora-drift-1 15s ease-in-out infinite alternate;
}
.aurora-2 {
  width: 400px; height: 400px; bottom: -10%; right: 5%;
  background: radial-gradient(circle, var(--color-accent), transparent 70%);
  animation: aurora-drift-2 20s ease-in-out infinite alternate;
}
@keyframes aurora-drift-1 { 0% { transform: translate(0,0) scale(1); } 100% { transform: translate(100px,50px) scale(1.3); } }""",
    },
    {
        "id": "aceternity_lamp_effect",
        "content": "Lamp effect (Aceternity UI, inspired by Linear): a conic or radial gradient that appears to emanate from a point above the section heading, creating a dramatic desk lamp illumination. Uses a wide conic-gradient (from 270deg, primary color to transparent) positioned at top-center with scaleY animation expanding from 0 to 1. The light cone illuminates the heading below it. Often paired with a horizontal line or border at the emission point. Creates a dramatic, theatrical reveal for section titles. Best for dark backgrounds, landing page sections.",
        "category": "visual_effects",
        "tags": ["lamp", "light-cone", "linear", "dramatic", "aceternity", "section-header"],
        "complexity": "medium",
        "impact_score": 9,
        "code": """.lamp-container { position: relative; overflow: hidden; padding-top: 8rem; }
.lamp-beam {
  position: absolute; top: 0; left: 50%; transform: translateX(-50%);
  width: 60%; height: 300px;
  background: conic-gradient(from 270deg at 50% 0%, var(--color-primary), transparent 35%, transparent 65%, var(--color-primary));
  opacity: 0.2;
  mask-image: linear-gradient(to bottom, white, transparent);
  animation: lamp-on 1.5s ease-out forwards;
}
@keyframes lamp-on { from { transform: translateX(-50%) scaleY(0); } to { transform: translateX(-50%) scaleY(1); } }""",
    },
    {
        "id": "aceternity_sparkles",
        "content": "Sparkles effect (Aceternity UI): randomly positioned and timed sparkle particles that appear, scale up, rotate, and fade around text or elements. Each sparkle is a small SVG star (4-point or 6-point) with randomized size (4-12px), position, color (white or primary), animation delay (0-3s), and duration (1-3s). Keyframes: scale from 0 to 1 back to 0, with rotation 0 to 180deg, and opacity 0 to 1 to 0. Spawn 15-30 sparkles. Creates a magical, celebratory accent. Best for highlighting special text, prices, badges, or CTA buttons.",
        "category": "visual_effects",
        "tags": ["sparkles", "particles", "magical", "accent", "aceternity", "stars"],
        "complexity": "low",
        "impact_score": 7,
        "code": """.sparkle-container { position: relative; display: inline-block; }
.sparkle {
  position: absolute; pointer-events: none;
  animation: sparkle-anim var(--duration, 2s) ease-in-out var(--delay, 0s) infinite;
}
@keyframes sparkle-anim {
  0%, 100% { transform: scale(0) rotate(0deg); opacity: 0; }
  50% { transform: scale(1) rotate(180deg); opacity: 1; }
}
/* SVG star: <svg width="12" height="12"><path d="M6 0L7.5 4.5L12 6L7.5 7.5L6 12L4.5 7.5L0 6L4.5 4.5Z" fill="currentColor"/></svg> */""",
    },
    {
        "id": "aceternity_text_generate",
        "content": "Text generate effect (Aceternity UI): text fades in word by word with a staggered delay, simulating AI text generation. Each word starts at opacity 0 with a slight blur(4px) and translateY(10px), then transitions to full visibility. Stagger delay of 50-100ms per word creates a natural, typewriter-like reveal. Uses IntersectionObserver to trigger on scroll or fires on page load for hero text. Different from typewriter because words appear simultaneously with stagger rather than sequentially. Creates a modern, AI-native feel for hero headlines.",
        "category": "text_animations",
        "tags": ["text-generate", "stagger", "word-reveal", "ai", "aceternity", "hero"],
        "complexity": "low",
        "impact_score": 8,
        "code": """.text-generate span {
  opacity: 0; filter: blur(4px); display: inline-block;
  transform: translateY(10px);
  animation: text-gen 0.4s ease forwards;
  animation-delay: calc(var(--word-index) * 80ms);
}
@keyframes text-gen {
  to { opacity: 1; filter: blur(0); transform: translateY(0); }
}
/* JS: text.split(' ').forEach((w,i) => span.style.setProperty('--word-index', i)) */""",
    },
    {
        "id": "aceternity_hero_parallax",
        "content": "Hero parallax effect (Aceternity UI): a scroll-driven layout where product images/screenshots rotate and translate in 3D as the user scrolls. The container has perspective:1000px, and child elements transform with rotateX, translateY, and translateZ values mapped to scroll progress. Images start rotated (rotateX 15-25deg) and flatten to 0deg as they scroll into full view. Creates a dramatic Apple-style product showcase. Often combined with a sticky container so the effect plays within a defined scroll range. Best for product landing pages and SaaS hero sections.",
        "category": "scroll_animations",
        "tags": ["parallax", "3d", "product", "scroll", "aceternity", "apple-style", "perspective"],
        "complexity": "high",
        "impact_score": 10,
        "code": """.hero-parallax { perspective: 1000px; height: 200vh; }
.hero-parallax-content {
  position: sticky; top: 0; height: 100vh;
  transform-style: preserve-3d;
  overflow: hidden;
}
.hero-parallax-images {
  transform: rotateX(25deg) translateZ(-100px) translateY(var(--scroll-y, 0));
  transition: transform 0.1s linear;
}
/* GSAP: gsap.to('.hero-parallax-images', { rotateX:0, translateZ:0, scrollTrigger:{ trigger:'.hero-parallax', start:'top top', end:'bottom top', scrub:true }}) */""",
    },
    {
        "id": "aceternity_infinite_cards",
        "content": "Infinite moving cards (Aceternity UI): a horizontal marquee of cards/testimonials that scrolls infinitely in a loop. Cards are duplicated to fill the track, then animated with translateX from 0 to -50% (since content is doubled). CSS animation with linear timing for seamless loop. Add pause-on-hover with animation-play-state:paused. Cards can scroll left or right. Multiple rows with different speeds create a dynamic testimonial wall. Essential for social proof sections, client logos, and testimonial showcases.",
        "category": "micro_interactions",
        "tags": ["marquee", "infinite", "cards", "loop", "aceternity", "testimonials", "social-proof"],
        "complexity": "low",
        "impact_score": 8,
        "code": """.infinite-track {
  display: flex; gap: 1.5rem; width: max-content;
  animation: scroll-cards 30s linear infinite;
}
.infinite-track:hover { animation-play-state: paused; }
@keyframes scroll-cards {
  0% { transform: translateX(0); }
  100% { transform: translateX(-50%); }
}
/* Duplicate children in JS: track.innerHTML += track.innerHTML; */
.infinite-card { flex-shrink: 0; width: 350px; }""",
    },
    {
        "id": "aceternity_moving_border",
        "content": "Moving border effect (Aceternity UI): an animated gradient that travels around the perimeter of a button or card border. Uses a conic-gradient that rotates 360deg continuously, masked to only show on the border area. The gradient has a bright segment (primary color) and transparent rest, creating a single light beam circling the element. Implementation: outer container with rotating conic-gradient background, inner element with solid background slightly inset (1-2px) to reveal the animated border. Perfect for CTAs, highlighted cards, and premium UI elements.",
        "category": "micro_interactions",
        "tags": ["moving-border", "animated", "gradient", "button", "aceternity", "cta", "premium"],
        "complexity": "medium",
        "impact_score": 8,
        "code": """.moving-border {
  position: relative; padding: 2px; border-radius: 12px; overflow: hidden;
}
.moving-border::before {
  content: ''; position: absolute; inset: -50%;
  background: conic-gradient(from 0deg, transparent 0%, var(--color-primary) 10%, transparent 20%);
  animation: rotate-border 3s linear infinite;
}
@keyframes rotate-border { 100% { transform: rotate(360deg); } }
.moving-border-inner {
  position: relative; background: var(--color-bg); border-radius: 10px;
  padding: 12px 24px; z-index: 1;
}""",
    },
    {
        "id": "aceternity_tracing_beam",
        "content": "Tracing beam effect (Aceternity UI): an SVG line that draws itself along the page as the user scrolls, following the content flow. Uses a vertical SVG path with stroke-dasharray and stroke-dashoffset animated by scroll position. A gradient from primary to secondary colors the drawn portion. A glowing dot at the current draw position (filter:drop-shadow) acts as a scroll progress indicator. Best used alongside content sections (timeline, about, process steps) to guide the eye. Creates an elegant, connected reading experience.",
        "category": "scroll_animations",
        "tags": ["tracing-beam", "svg", "scroll-progress", "path", "aceternity", "timeline"],
        "complexity": "high",
        "impact_score": 8,
        "code": """.tracing-beam-svg { position: absolute; left: 20px; top: 0; height: 100%; width: 20px; }
.tracing-line {
  stroke: url(#tracing-gradient); stroke-width: 2; fill: none;
  stroke-dasharray: var(--path-length);
  stroke-dashoffset: var(--path-length);
  transition: stroke-dashoffset 0.1s linear;
}
.tracing-dot {
  r: 5; fill: var(--color-primary);
  filter: drop-shadow(0 0 6px var(--color-primary));
}
/* JS: window.addEventListener('scroll', () => { line.style.strokeDashoffset = pathLength * (1 - scrollProgress); }) */""",
    },
    {
        "id": "aceternity_background_gradient_animation",
        "content": "Background gradient animation (Aceternity UI): a smooth, slowly shifting background gradient that cycles through colors. Uses background-size: 400% 400% with a CSS keyframe animating background-position through all four corners. Gradient uses 3-4 colors (primary, secondary, accent variations). Duration 10-20s for subtle, hypnotic movement. Creates a living, breathing background that adds depth without distraction. Best for hero sections, full-page backgrounds, and CTA sections. Works on both dark and light themes.",
        "category": "backgrounds",
        "tags": ["gradient-animation", "background", "shifting", "aceternity", "smooth", "ambient"],
        "complexity": "low",
        "impact_score": 8,
        "code": """.gradient-animate {
  background: linear-gradient(-45deg, var(--color-primary), var(--color-secondary), var(--color-accent), var(--color-primary));
  background-size: 400% 400%;
  animation: gradient-shift 15s ease infinite;
}
@keyframes gradient-shift {
  0% { background-position: 0% 50%; }
  25% { background-position: 100% 0%; }
  50% { background-position: 100% 100%; }
  75% { background-position: 0% 100%; }
  100% { background-position: 0% 50%; }
}""",
    },
    {
        "id": "aceternity_animated_tooltip",
        "content": "Animated tooltip (Aceternity UI): a tooltip that scales in from the trigger point with a spring-like overshoot animation, follows mouse position horizontally within the trigger element bounds. Uses scale(0.5) to scale(1) with a cubic-bezier spring curve. Tooltip has a subtle backdrop-filter:blur, rounded corners, and a small arrow/triangle. The tooltip position updates on mousemove for a fluid, connected feel. Content can include images, text, or mini profiles. Creates a polished, interactive detail layer for team sections, feature explanations, and link previews.",
        "category": "micro_interactions",
        "tags": ["tooltip", "animated", "hover", "spring", "aceternity", "interactive", "detail"],
        "complexity": "medium",
        "impact_score": 7,
        "code": """.animated-tooltip {
  position: absolute; bottom: calc(100% + 8px); left: 50%;
  transform: translateX(-50%) scale(0.5); opacity: 0;
  transition: transform 0.3s cubic-bezier(0.175,0.885,0.32,1.275), opacity 0.2s ease;
  background: rgba(0,0,0,0.85); backdrop-filter: blur(8px);
  border-radius: 8px; padding: 8px 12px; pointer-events: none;
  white-space: nowrap; color: white; font-size: 0.875rem;
}
.tooltip-trigger:hover .animated-tooltip {
  transform: translateX(-50%) scale(1); opacity: 1;
}""",
    },
    {
        "id": "aceternity_macbook_scroll",
        "content": "Macbook scroll effect (Aceternity UI): a 3D laptop mockup where the screen content/image emerges and grows as the user scrolls. The laptop starts small and rotated, then scales up and flattens to show a full product screenshot. Uses perspective, rotateX, and scale transforms driven by GSAP ScrollTrigger scrub. The screen can show a video or animated demo. Creates an Apple-keynote-style product reveal. Best for SaaS product showcases, app launches, and feature highlights. Pin the section for the full scroll animation range.",
        "category": "scroll_animations",
        "tags": ["macbook", "product-reveal", "3d", "scroll", "aceternity", "apple", "showcase"],
        "complexity": "high",
        "impact_score": 10,
        "code": """.macbook-section { height: 300vh; }
.macbook-container {
  position: sticky; top: 10vh; height: 80vh;
  display: flex; align-items: center; justify-content: center;
  perspective: 1200px;
}
.macbook-frame {
  transform: rotateX(25deg) scale(0.6);
  transform-origin: center bottom;
  transition: transform 0.15s linear;
  border-radius: 12px; overflow: hidden;
  box-shadow: 0 40px 80px rgba(0,0,0,0.4);
}
/* GSAP: gsap.to('.macbook-frame', { rotateX:0, scale:1, scrollTrigger:{ trigger:'.macbook-section', scrub:1, pin:true }}) */""",
    },

    # ====================================================
    # MAGIC UI EFFECTS (11)
    # ====================================================
    {
        "id": "magicui_shimmer_button",
        "content": "Shimmer button (Magic UI): a CTA button with a traveling light sweep across its surface. A linear gradient highlight (white at 10-15% opacity) slides horizontally across the button using background-position animation. The shimmer band is narrow against a wider background-size, creating a focused sweep. Animation alternates (ease-in-out infinite alternate) for continuous, premium feel. The button surface often has a subtle gradient base color. Creates an eye-catching, premium CTA that draws attention without being distracting. Perfect for primary action buttons.",
        "category": "micro_interactions",
        "tags": ["shimmer", "button", "cta", "shine", "magicui", "premium", "sweep"],
        "complexity": "low",
        "impact_score": 8,
        "code": """.shimmer-btn {
  position: relative; overflow: hidden;
  background: var(--color-primary);
  color: white; padding: 12px 32px;
  border-radius: 12px; font-weight: 600;
}
.shimmer-btn::after {
  content: ''; position: absolute; inset: 0;
  background: linear-gradient(90deg, transparent 0%, rgba(255,255,255,0.15) 50%, transparent 100%);
  background-size: 200% 100%;
  animation: shimmer-slide 2s ease-in-out infinite alternate;
}
@keyframes shimmer-slide {
  0% { background-position: -100% 0; }
  100% { background-position: 100% 0; }
}""",
    },
    {
        "id": "magicui_border_beam",
        "content": "Border beam (Magic UI): an animated beam of light that travels along the border of a container. Uses a conic-gradient with a very narrow bright segment (5-10%) that rotates around the element. The beam is visible through a 1-2px transparent border gap. Creates a subtle, high-tech scanning effect on cards and containers. Often used on featured cards, notification banners, and dialog boxes. Pairs well with dark themes where the beam is clearly visible against dark card backgrounds.",
        "category": "micro_interactions",
        "tags": ["border-beam", "animated", "light", "scanning", "magicui", "card", "tech"],
        "complexity": "medium",
        "impact_score": 8,
        "code": """.border-beam {
  position: relative; border-radius: 16px; padding: 1px;
  background: var(--color-bg-alt);
  overflow: hidden;
}
.border-beam::before {
  content: ''; position: absolute; inset: 0;
  background: conic-gradient(from var(--beam-angle, 0deg), transparent 0%, transparent 85%, var(--color-primary) 90%, var(--color-accent) 95%, transparent 100%);
  animation: beam-rotate 4s linear infinite;
}
.border-beam > * { position: relative; z-index: 1; background: var(--color-bg); border-radius: 15px; }
@keyframes beam-rotate { 100% { --beam-angle: 360deg; } }
/* Use @property for --beam-angle in browsers that support it */""",
    },
    {
        "id": "magicui_magic_card",
        "content": "Magic card (Magic UI): a card with a radial gradient spotlight that follows the mouse cursor. On mousemove, update CSS custom properties --mouse-x and --mouse-y with the cursor position relative to the card. A radial-gradient at that position creates a soft glow (primary color at 10-20% opacity, fading to transparent). The border also illuminates near the cursor using the same technique on a pseudo-element. Creates a premium, interactive card that feels alive. Best for feature grids, pricing cards, and bento layouts on dark themes.",
        "category": "card_designs",
        "tags": ["magic-card", "spotlight", "mouse-follow", "glow", "magicui", "interactive", "premium"],
        "complexity": "medium",
        "impact_score": 9,
        "code": """.magic-card {
  position: relative; overflow: hidden;
  background: var(--color-bg-alt); border-radius: 16px;
  border: 1px solid rgba(255,255,255,0.1);
}
.magic-card::before {
  content: ''; position: absolute; inset: 0;
  background: radial-gradient(600px circle at var(--mouse-x, 50%) var(--mouse-y, 50%), rgba(var(--color-primary-rgb),0.12), transparent 40%);
  pointer-events: none; opacity: 0;
  transition: opacity 0.3s ease;
}
.magic-card:hover::before { opacity: 1; }
/* JS: card.addEventListener('mousemove', e => { card.style.setProperty('--mouse-x', e.offsetX+'px'); card.style.setProperty('--mouse-y', e.offsetY+'px'); }) */""",
    },
    {
        "id": "magicui_number_ticker",
        "content": "Number ticker (Magic UI): animated counter that rolls digits like an odometer. Each digit column scrolls vertically through 0-9, landing on the target number. Uses translateY animation on a strip of stacked digits (0 through 9), with each digit position calculated as -(targetDigit * 10)%. Different digits animate with slight stagger for a cascading roll effect. Duration 1-2s with ease-out for satisfying deceleration. Great for stats sections, pricing displays, and dashboard numbers. More visually engaging than a simple counting animation.",
        "category": "text_animations",
        "tags": ["number-ticker", "counter", "odometer", "digits", "magicui", "stats", "rolling"],
        "complexity": "medium",
        "impact_score": 8,
        "code": """.ticker-digit {
  display: inline-block; overflow: hidden; height: 1em; line-height: 1;
}
.ticker-column {
  display: flex; flex-direction: column;
  animation: tick-roll 1.5s cubic-bezier(0.16,1,0.3,1) forwards;
  animation-delay: var(--digit-delay, 0s);
}
.ticker-column span { height: 1em; display: flex; align-items: center; justify-content: center; }
@keyframes tick-roll {
  from { transform: translateY(0); }
  to { transform: translateY(calc(var(--target) * -1em)); }
}
/* JS: column.style.setProperty('--target', targetDigit) */""",
    },
    {
        "id": "magicui_dock",
        "content": "macOS dock effect (Magic UI): a horizontal icon bar where icons scale up as the mouse approaches them, with neighboring icons also scaling proportionally (creating a fisheye magnification). Calculate distance from mouse to each icon center, apply scale based on inverse distance (closest = scale 1.5-2x, neighbors scale 1.2-1.4x, far = scale 1x). Use GSAP or CSS transitions for smooth scaling. The dock container should expand its height to accommodate scaled icons. Creates a playful, familiar interaction for navigation bars and toolbars.",
        "category": "micro_interactions",
        "tags": ["dock", "macos", "fisheye", "scale", "magicui", "navigation", "icons"],
        "complexity": "high",
        "impact_score": 8,
        "code": """.dock {
  display: flex; align-items: flex-end; gap: 4px;
  padding: 8px 12px; background: rgba(255,255,255,0.1);
  backdrop-filter: blur(12px); border-radius: 20px;
  border: 1px solid rgba(255,255,255,0.15);
}
.dock-item {
  width: 48px; height: 48px; border-radius: 12px;
  transition: transform 0.2s cubic-bezier(0.2,0,0,1), width 0.2s;
  transform-origin: bottom center;
}
/* JS: scale = 1 + maxScale * Math.max(0, 1 - Math.abs(mouseX - iconCenterX) / range) */
.dock-item.active { transform: scale(1.6); width: 64px; }""",
    },
    {
        "id": "magicui_globe",
        "content": "Interactive 3D globe (Magic UI): a rotating wireframe or dotted globe rendered with Three.js or canvas, showing connection arcs between geographic points. The globe auto-rotates slowly and responds to mouse drag for manual rotation. Connection arcs animate from origin to destination with a traveling light point. Dots on the globe surface represent locations. Uses WebGL for smooth rendering. Creates a global, connected feel for international businesses, SaaS platforms, and tech companies. Best as a hero section background element or standalone interactive feature.",
        "category": "visual_effects",
        "tags": ["globe", "3d", "threejs", "interactive", "magicui", "global", "connections"],
        "complexity": "high",
        "impact_score": 9,
        "code": """/* Three.js globe setup */
const globe = new THREE.Mesh(
  new THREE.SphereGeometry(1, 48, 48),
  new THREE.MeshBasicMaterial({ wireframe: true, color: 0x6c5ce7, transparent: true, opacity: 0.3 })
);
/* Arc connections */
function createArc(start, end) {
  const curve = new THREE.QuadraticBezierCurve3(startVec, midVec, endVec);
  return new THREE.Line(new THREE.BufferGeometry().setFromPoints(curve.getPoints(50)),
    new THREE.LineBasicMaterial({ color: 0x00cec9, transparent: true, opacity: 0.6 }));
}
/* Auto-rotate: globe.rotation.y += 0.002 per frame */""",
    },
    {
        "id": "magicui_particles",
        "content": "Particle field (Magic UI): a canvas-based particle system with floating dots that connect with lines when within proximity. Particles drift slowly with slight randomness. Mouse interaction: particles near the cursor are attracted or repelled (configurable). Connection lines fade with distance (opacity mapped to distance). Particle count adapts to screen size (50-150). Colors match the theme (white/primary on dark, gray on light). Creates a living, tech-forward background. Best for hero sections, about sections, and full-page backgrounds on tech/SaaS sites.",
        "category": "backgrounds",
        "tags": ["particles", "canvas", "connected", "floating", "magicui", "tech", "interactive"],
        "complexity": "medium",
        "impact_score": 8,
        "code": """/* Canvas particle system */
class Particle {
  constructor(canvas) {
    this.x = Math.random() * canvas.width;
    this.y = Math.random() * canvas.height;
    this.vx = (Math.random() - 0.5) * 0.5;
    this.vy = (Math.random() - 0.5) * 0.5;
    this.radius = Math.random() * 2 + 1;
  }
  draw(ctx) { ctx.beginPath(); ctx.arc(this.x, this.y, this.radius, 0, Math.PI*2); ctx.fill(); }
}
function connectParticles(a, b, ctx) {
  const dist = Math.hypot(a.x-b.x, a.y-b.y);
  if (dist < 120) { ctx.globalAlpha = 1 - dist/120; ctx.beginPath(); ctx.moveTo(a.x,a.y); ctx.lineTo(b.x,b.y); ctx.stroke(); }
}""",
    },
    {
        "id": "magicui_ripple",
        "content": "Ripple button effect (Magic UI): concentric circles expand outward from the click point on a button, creating a material-design-inspired ripple. On click, inject a span at the click coordinates with scale(0) to scale(4) animation and opacity 0.4 to 0. Duration 600ms with ease-out. The ripple color is a lighter shade of the button background. Remove the span after animation completes. Can also be used on cards and interactive surfaces. Creates tactile, responsive feedback that confirms user interaction.",
        "category": "micro_interactions",
        "tags": ["ripple", "click", "material", "feedback", "magicui", "button", "tactile"],
        "complexity": "low",
        "impact_score": 7,
        "code": """.ripple-btn { position: relative; overflow: hidden; }
.ripple-btn .ripple-circle {
  position: absolute; border-radius: 50%;
  background: rgba(255,255,255,0.35);
  transform: scale(0); animation: ripple-expand 0.6s ease-out forwards;
  pointer-events: none;
}
@keyframes ripple-expand {
  to { transform: scale(4); opacity: 0; }
}
/* JS: btn.addEventListener('click', e => { const r = document.createElement('span'); r.className='ripple-circle';
  r.style.left = (e.offsetX-10)+'px'; r.style.top = (e.offsetY-10)+'px';
  r.style.width = r.style.height = '20px'; btn.appendChild(r); setTimeout(() => r.remove(), 600); }) */""",
    },
    {
        "id": "magicui_shine_border",
        "content": "Shine border (Magic UI): an animated rainbow or gradient shine that continuously sweeps around a card or container border. Uses a rotating conic-gradient background behind a solid inner container. The gradient includes multiple color stops (primary, accent, secondary) or rainbow colors. Unlike border-beam (single point), shine-border has a broad, smooth color sweep covering 30-50% of the perimeter at once. Animation: continuous rotation at 3-5s. Creates an eye-catching, premium highlight for featured content, testimonial cards, and promotional banners.",
        "category": "visual_effects",
        "tags": ["shine-border", "rainbow", "gradient", "card", "magicui", "featured", "highlight"],
        "complexity": "medium",
        "impact_score": 8,
        "code": """.shine-border-wrapper {
  position: relative; padding: 2px; border-radius: 16px;
  background: conic-gradient(from var(--shine-angle, 0deg), #ff0080, #ff8c00, #40e0d0, #8b5cf6, #ff0080);
  animation: shine-rotate 4s linear infinite;
}
@property --shine-angle { syntax: '<angle>'; initial-value: 0deg; inherits: false; }
@keyframes shine-rotate { to { --shine-angle: 360deg; } }
.shine-border-inner {
  background: var(--color-bg); border-radius: 14px; padding: 24px;
}""",
    },
    {
        "id": "magicui_blur_fade",
        "content": "Blur fade entrance (Magic UI): elements enter the viewport with a combination of blur and fade, clearing to sharp focus. Start with filter:blur(8-12px) and opacity:0, animate to blur(0) and opacity:1. Add translateY(20px) to translateY(0) for upward motion. Duration 0.6-0.8s with ease-out. Stagger children by 100-200ms for cascading clarity. Creates a dreamy, cinematic entrance that feels more premium than a simple fade. Best for hero content, section reveals, and image galleries.",
        "category": "visual_effects",
        "tags": ["blur-fade", "entrance", "dreamy", "cinematic", "magicui", "scroll-trigger", "premium"],
        "complexity": "low",
        "impact_score": 8,
        "code": """.blur-fade {
  opacity: 0; filter: blur(10px);
  transform: translateY(20px);
  transition: opacity 0.7s ease, filter 0.7s ease, transform 0.7s ease;
}
.blur-fade.visible {
  opacity: 1; filter: blur(0); transform: translateY(0);
}
.blur-fade:nth-child(1) { transition-delay: 0s; }
.blur-fade:nth-child(2) { transition-delay: 0.15s; }
.blur-fade:nth-child(3) { transition-delay: 0.3s; }
/* JS: IntersectionObserver -> add 'visible' class on entry */""",
    },
    {
        "id": "magicui_hyper_text",
        "content": "Hyper text effect (Magic UI): text characters rapidly cycle through random characters before settling on the correct letter, creating a decryption/hacking animation. On hover or on load, each character cycles through 5-10 random alphanumeric characters with 30-50ms intervals before revealing the actual character. Characters settle left-to-right with stagger. Uses monospace font during animation for consistent width. Creates a tech, cyberpunk, or AI-decoded feel. Best for hero headlines, tech product names, and interactive section titles.",
        "category": "text_animations",
        "tags": ["hyper-text", "scramble", "decode", "hacking", "magicui", "tech", "cyberpunk"],
        "complexity": "medium",
        "impact_score": 8,
        "code": """.hyper-text { font-family: 'Space Grotesk', monospace; display: inline-block; }
.hyper-text span {
  display: inline-block; min-width: 0.6em;
  transition: opacity 0.1s;
}
/* JS: function scramble(el) {
  const original = el.textContent;
  const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
  let iterations = 0;
  const interval = setInterval(() => {
    el.textContent = original.split('').map((c, i) =>
      i < iterations ? original[i] : chars[Math.floor(Math.random() * chars.length)]
    ).join('');
    if (iterations >= original.length) clearInterval(interval);
    iterations += 1/3;
  }, 30);
} */""",
    },

    # ====================================================
    # UIVERSE & CSS EFFECTS (10)
    # ====================================================
    {
        "id": "uiverse_glassmorphism_panel",
        "content": "Glassmorphism panel (UIverse): frosted glass UI elements using backdrop-filter:blur(20px) with semi-transparent backgrounds (rgba white 5-15%). Requires a vibrant background (gradient, image, or colored shapes) behind the glass element for the blur to be visible. Add a subtle 1px border with rgba(255,255,255,0.1-0.2) for edge definition. Multi-layer depth: stack glass panels with decreasing opacity for parallax depth. ~95% browser support in 2025. Best for navigation bars, modal dialogs, card overlays, and floating panels. Creates Apple-inspired premium UI.",
        "category": "glassmorphism",
        "tags": ["glassmorphism", "backdrop-filter", "glass", "frosted", "uiverse", "apple", "premium"],
        "complexity": "low",
        "impact_score": 9,
        "code": """.glass-panel {
  background: rgba(255, 255, 255, 0.08);
  backdrop-filter: blur(20px) saturate(180%);
  -webkit-backdrop-filter: blur(20px) saturate(180%);
  border: 1px solid rgba(255, 255, 255, 0.15);
  border-radius: 16px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
}
.glass-panel-light {
  background: rgba(255, 255, 255, 0.6);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.4);
}""",
    },
    {
        "id": "uiverse_neumorphic_card",
        "content": "Neumorphic card (UIverse): soft UI elements that appear extruded from or pressed into the background surface. Uses dual box-shadows: one light (top-left, white/lighter shade) and one dark (bottom-right, darker shade). The element background matches the parent background color exactly. For pressed/inset state, use inset shadows. Works best on soft, muted backgrounds (light gray, soft pastels). NOT suitable for dark themes. Creates a tactile, physical feel for buttons, cards, and input fields. Best for minimal, clean interfaces.",
        "category": "card_designs",
        "tags": ["neumorphism", "soft-ui", "shadow", "extruded", "uiverse", "tactile", "minimal"],
        "complexity": "low",
        "impact_score": 7,
        "code": """.neumorphic {
  background: #e0e5ec;
  border-radius: 20px; padding: 24px;
  box-shadow: 8px 8px 16px #b8bec7, -8px -8px 16px #ffffff;
}
.neumorphic-inset {
  background: #e0e5ec;
  border-radius: 20px; padding: 24px;
  box-shadow: inset 4px 4px 8px #b8bec7, inset -4px -4px 8px #ffffff;
}
.neumorphic-btn:active {
  box-shadow: inset 4px 4px 8px #b8bec7, inset -4px -4px 8px #ffffff;
}""",
    },
    {
        "id": "uiverse_gradient_border",
        "content": "Gradient border technique (UIverse): create animated or static gradient borders on elements. Primary technique: background with padding-box + border-box trick. Set element background as solid-color padding-box, overlay with gradient border-box, and use a transparent border to reveal the gradient. Alternative: pseudo-element slightly larger than the parent with gradient background, main content on top. Animatable by rotating the gradient angle or shifting colors. Best for featured cards, highlighted sections, and premium UI elements.",
        "category": "visual_effects",
        "tags": ["gradient-border", "border", "technique", "uiverse", "featured", "css-trick"],
        "complexity": "medium",
        "impact_score": 8,
        "code": """.gradient-border {
  border: 2px solid transparent;
  background: linear-gradient(var(--color-bg), var(--color-bg)) padding-box,
              linear-gradient(135deg, var(--color-primary), var(--color-accent)) border-box;
  border-radius: 16px;
}
.gradient-border-animated {
  border: 2px solid transparent;
  background: linear-gradient(var(--color-bg), var(--color-bg)) padding-box,
              linear-gradient(var(--border-angle, 135deg), var(--color-primary), var(--color-accent), var(--color-primary)) border-box;
  animation: border-rotate 4s linear infinite;
}
@property --border-angle { syntax: '<angle>'; initial-value: 0deg; inherits: false; }
@keyframes border-rotate { to { --border-angle: 360deg; } }""",
    },
    {
        "id": "uiverse_animated_toggle",
        "content": "Animated toggle switch (UIverse): a beautifully animated on/off toggle with smooth state transitions. The thumb slides with a squish effect (scaleX(1.2) at midpoint), background color transitions from gray to primary. Add micro-interactions: checkmark/X icons that fade in/out, inner glow on active state, subtle bounce at rest position. Size the toggle 52x28px for comfortable touch targets. Creates polished form interactions for settings pages, preference panels, and theme switchers.",
        "category": "form_design",
        "tags": ["toggle", "switch", "animated", "form", "uiverse", "interaction", "settings"],
        "complexity": "low",
        "impact_score": 7,
        "code": """.toggle {
  width: 52px; height: 28px; border-radius: 14px;
  background: #cbd5e1; cursor: pointer;
  transition: background 0.3s ease; position: relative;
}
.toggle.active { background: var(--color-primary); }
.toggle-thumb {
  position: absolute; top: 2px; left: 2px;
  width: 24px; height: 24px; border-radius: 50%;
  background: white; box-shadow: 0 2px 4px rgba(0,0,0,0.2);
  transition: transform 0.3s cubic-bezier(0.68,-0.55,0.27,1.55);
}
.toggle.active .toggle-thumb { transform: translateX(24px); }""",
    },
    {
        "id": "uiverse_3d_flip_card",
        "content": "3D flip card (UIverse): a card that rotates 180deg on hover to reveal back content. Uses transform-style:preserve-3d on the container, two absolutely-positioned faces (front and back), back face has backface-visibility:hidden and rotateY(180deg) default. On hover, container rotates 180deg on Y axis. Transition 0.6-0.8s with ease-in-out. Front shows preview (image, title), back shows details (description, CTA). Creates an interactive, game-like element for team members, service cards, and product features.",
        "category": "card_designs",
        "tags": ["flip-card", "3d", "hover", "reveal", "uiverse", "interactive", "two-sided"],
        "complexity": "medium",
        "impact_score": 8,
        "code": """.flip-card { perspective: 1000px; width: 100%; height: 350px; cursor: pointer; }
.flip-inner {
  position: relative; width: 100%; height: 100%;
  transform-style: preserve-3d;
  transition: transform 0.7s cubic-bezier(0.4, 0, 0.2, 1);
}
.flip-card:hover .flip-inner { transform: rotateY(180deg); }
.flip-front, .flip-back {
  position: absolute; inset: 0;
  backface-visibility: hidden;
  border-radius: 16px; overflow: hidden;
}
.flip-back { transform: rotateY(180deg); }""",
    },
    {
        "id": "uiverse_morphing_shapes",
        "content": "CSS morphing shapes (UIverse): organic blob shapes that morph continuously using animated border-radius. Set border-radius with 8 values and animate between different configurations. Duration 8-15s, ease-in-out, infinite. Add subtle rotation for more organic movement. Use as decorative background elements, profile image masks, or section dividers. Multiple overlapping blobs with different colors and timing create a lava-lamp effect. Best for creative/artistic sites and as hero section decoration.",
        "category": "visual_effects",
        "tags": ["morphing", "blob", "organic", "border-radius", "uiverse", "decorative", "lava-lamp"],
        "complexity": "low",
        "impact_score": 7,
        "code": """.morph-blob {
  width: 300px; height: 300px;
  background: var(--color-primary);
  opacity: 0.15; filter: blur(40px);
  animation: morph 10s ease-in-out infinite alternate;
}
@keyframes morph {
  0% { border-radius: 60% 40% 30% 70% / 60% 30% 70% 40%; transform: rotate(0deg); }
  25% { border-radius: 30% 60% 70% 40% / 50% 60% 30% 60%; }
  50% { border-radius: 50% 60% 40% 60% / 40% 50% 60% 50%; transform: rotate(90deg); }
  75% { border-radius: 40% 60% 50% 50% / 60% 40% 60% 40%; }
  100% { border-radius: 70% 30% 50% 50% / 30% 70% 40% 60%; transform: rotate(180deg); }
}""",
    },
    {
        "id": "uiverse_css_scroll_animations",
        "content": "CSS-only scroll animations using animation-timeline:view() and scroll(). Modern browsers support scroll-driven animations without JavaScript. Elements with animation-timeline:view() animate based on their visibility in the viewport. Use animation-range to control when the animation starts and ends. Supports all standard CSS animations. Combine with animation-timeline:scroll() for scroll-progress-based effects. Reduces dependency on GSAP for simple entrance animations. Graceful fallback: elements show normally without animation in unsupported browsers.",
        "category": "scroll_animations",
        "tags": ["scroll-driven", "css-only", "view-timeline", "animation-timeline", "modern", "no-js"],
        "complexity": "medium",
        "impact_score": 9,
        "code": """.scroll-reveal {
  animation: scroll-fade-up linear both;
  animation-timeline: view();
  animation-range: entry 0% entry 100%;
}
@keyframes scroll-fade-up {
  from { opacity: 0; transform: translateY(40px) scale(0.95); }
  to { opacity: 1; transform: translateY(0) scale(1); }
}
.scroll-progress {
  transform-origin: left;
  animation: grow-progress linear;
  animation-timeline: scroll(root);
}
@keyframes grow-progress { from { transform: scaleX(0); } to { transform: scaleX(1); } }""",
    },
    {
        "id": "uiverse_clip_path_transitions",
        "content": "Clip-path transitions (UIverse/FreeFrontend): use CSS clip-path to create dramatic shape-based reveals and transitions. Animate clip-path between shapes: circle(0% at 50% 50%) to circle(150%), inset(50% 50% 50% 50%) to inset(0%), polygon shapes for diagonal wipes. Works for page transitions, image reveals, section entrances, and hover effects. Smooth with transition:clip-path 0.8s ease. Combine with IntersectionObserver for scroll-triggered reveals. Creates cinematic, editorial transitions. polygon() allows diamonds, triangles, and custom paths.",
        "category": "visual_effects",
        "tags": ["clip-path", "transitions", "shape", "reveal", "cinematic", "editorial", "wipe"],
        "complexity": "medium",
        "impact_score": 9,
        "code": """.clip-reveal-circle {
  clip-path: circle(0% at 50% 50%);
  transition: clip-path 0.8s cubic-bezier(0.4, 0, 0.2, 1);
}
.clip-reveal-circle.visible { clip-path: circle(150% at 50% 50%); }
.clip-reveal-inset {
  clip-path: inset(50% 50% 50% 50%);
  transition: clip-path 0.6s ease-out;
}
.clip-reveal-inset.visible { clip-path: inset(0% 0% 0% 0%); }
.clip-diagonal {
  clip-path: polygon(0 0, 0 0, 0 100%, 0 100%);
  transition: clip-path 0.8s ease;
}
.clip-diagonal.visible { clip-path: polygon(0 0, 100% 0, 100% 100%, 0 100%); }""",
    },
    {
        "id": "uiverse_noise_texture",
        "content": "Noise texture overlay (FreeFrontend): add a subtle film grain or noise texture to backgrounds for tactile, printed-paper feel. Use a tiny noise PNG as a repeating background-image with low opacity (3-8%) layered over gradients or solid colors. Alternatively, generate noise with CSS: a small SVG feTurbulence filter applied to a pseudo-element. The noise breaks the digital flatness and adds warmth. Best for creative, editorial, and luxury sites. Combine with a slight vignette (radial-gradient darker at edges) for photographic depth.",
        "category": "backgrounds",
        "tags": ["noise", "texture", "grain", "film", "editorial", "luxury", "tactile"],
        "complexity": "low",
        "impact_score": 7,
        "code": """.noise-overlay::after {
  content: ''; position: absolute; inset: 0;
  opacity: 0.05; pointer-events: none; z-index: 1;
  background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E");
  background-size: 200px 200px;
}
.vignette::before {
  content: ''; position: absolute; inset: 0;
  background: radial-gradient(ellipse at center, transparent 50%, rgba(0,0,0,0.3) 100%);
  pointer-events: none;
}""",
    },
    {
        "id": "uiverse_gradient_mesh",
        "content": "Gradient mesh background (FreeFrontend): a multi-color gradient with overlapping radial gradients positioned at different points, creating a mesh-like color blend similar to Figma's gradient mesh. Place 3-5 radial-gradient layers at different positions with different colors, sizes, and opacities. Each gradient is a separate background-image layer. The result is a rich, multi-dimensional color field that feels organic and premium. Animate individual gradient positions for subtle movement. Best for hero backgrounds, CTA sections, and landing pages.",
        "category": "backgrounds",
        "tags": ["gradient-mesh", "multi-color", "organic", "background", "premium", "figma-style"],
        "complexity": "medium",
        "impact_score": 9,
        "code": """.gradient-mesh {
  background-color: #0f172a;
  background-image:
    radial-gradient(at 20% 30%, rgba(124,58,237,0.3) 0%, transparent 50%),
    radial-gradient(at 80% 20%, rgba(6,182,212,0.25) 0%, transparent 50%),
    radial-gradient(at 50% 80%, rgba(236,72,153,0.2) 0%, transparent 50%),
    radial-gradient(at 90% 70%, rgba(34,211,238,0.15) 0%, transparent 50%);
}
.gradient-mesh-animated {
  animation: mesh-shift 20s ease-in-out infinite alternate;
}
@keyframes mesh-shift {
  0% { background-position: 0% 0%, 100% 0%, 50% 100%, 90% 70%; }
  100% { background-position: 30% 20%, 70% 40%, 20% 60%, 60% 90%; }
}""",
    },

    # ====================================================
    # MODERN LAYOUT & INTERACTION PATTERNS (8)
    # ====================================================
    {
        "id": "modern_bento_grid",
        "content": "Bento grid layout: an asymmetric grid where cards have different sizes (1x1, 2x1, 1x2, 2x2) creating a magazine-like, visually dynamic layout. Use CSS grid with grid-template-columns:repeat(4, 1fr) and cards spanning different rows/columns via grid-column:span 2, grid-row:span 2. Featured content gets larger cards. Each card can contain different content types (stats, images, text, interactive elements). Mobile: stack to single column. Creates a modern, editorial feel popularized by Apple, Vercel, and Stripe. Essential for feature showcases and dashboards.",
        "category": "layout_patterns",
        "tags": ["bento", "grid", "asymmetric", "magazine", "apple", "vercel", "feature-showcase"],
        "complexity": "medium",
        "impact_score": 10,
        "code": """.bento-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  grid-auto-rows: minmax(200px, auto);
  gap: 1rem;
}
.bento-card { border-radius: 16px; padding: 24px; overflow: hidden; }
.bento-card.span-2-col { grid-column: span 2; }
.bento-card.span-2-row { grid-row: span 2; }
.bento-card.span-2x2 { grid-column: span 2; grid-row: span 2; }
@media (max-width: 768px) {
  .bento-grid { grid-template-columns: 1fr; }
  .bento-card.span-2-col, .bento-card.span-2x2 { grid-column: span 1; grid-row: span 1; }
}""",
    },
    {
        "id": "modern_sticky_scroll_sections",
        "content": "Sticky scroll sections: content panels that stick to the viewport and stack/overlap as the user scrolls, creating a card-stacking or presentation effect. Each section is position:sticky with top:0 and increasing z-index. As you scroll past one section, the next one slides up and covers it. Add scale(0.95) and opacity reduction to departing sections for depth. Creates a presentation/slide-deck feel for storytelling, feature walkthroughs, and process explanations. Works with pure CSS.",
        "category": "scroll_animations",
        "tags": ["sticky", "stacking", "scroll", "presentation", "storytelling", "css-only", "sections"],
        "complexity": "medium",
        "impact_score": 9,
        "code": """.sticky-container { position: relative; }
.sticky-section {
  position: sticky; top: 0;
  min-height: 100vh;
  display: flex; align-items: center; justify-content: center;
  transition: transform 0.3s ease, opacity 0.3s ease;
}
.sticky-section:nth-child(1) { z-index: 1; background: var(--color-bg); }
.sticky-section:nth-child(2) { z-index: 2; background: var(--color-bg-alt); }
.sticky-section:nth-child(3) { z-index: 3; background: var(--color-bg); }
/* GSAP: ScrollTrigger to scale(0.9) + opacity(0.5) departing sections */""",
    },
    {
        "id": "modern_text_reveal_scroll",
        "content": "Text reveal on scroll: large text where each word or line transitions from muted/transparent to bold/visible as the scroll position advances. Words are wrapped in spans with initial opacity:0.2 and transition to opacity:1 based on scroll progress. Uses GSAP ScrollTrigger with scrub for smooth, scroll-synced animation. Each word triggers slightly after the previous one (stagger based on DOM position). Creates an editorial, manifesto-style reading experience. Best for mission statements, about sections, and storytelling pages. Font should be large (text-4xl to text-6xl).",
        "category": "text_animations",
        "tags": ["text-reveal", "scroll", "word-by-word", "editorial", "manifesto", "gsap", "scrub"],
        "complexity": "medium",
        "impact_score": 9,
        "code": """.text-reveal-container { max-width: 800px; margin: 0 auto; padding: 20vh 0; }
.text-reveal-word {
  display: inline-block; opacity: 0.15;
  font-size: clamp(1.5rem, 4vw, 3.5rem);
  font-weight: 700; line-height: 1.3;
  transition: opacity 0.3s ease;
}
.text-reveal-word.active { opacity: 1; }
/* GSAP: gsap.to('.text-reveal-word', { opacity:1, stagger:0.05,
  scrollTrigger:{ trigger:'.text-reveal-container', start:'top 80%', end:'bottom 20%', scrub:1 }}) */""",
    },
    {
        "id": "modern_parallax_depth_layers",
        "content": "Parallax depth layers: multiple absolutely-positioned elements (shapes, images, text) that move at different speeds on scroll, creating a multi-plane 3D depth effect. Foreground elements move faster than background elements. Assign data-speed attributes (0.1 for far back, 0.5 for mid, 1.0 for foreground) and calculate translateY offset based on scroll * speed. Decorative elements (circles, lines, dots) at different depths add richness. Creates immersive, cinematic hero sections. Best combined with a focal content element in the mid-ground.",
        "category": "scroll_animations",
        "tags": ["parallax", "depth", "layers", "3d", "multi-plane", "immersive", "cinematic"],
        "complexity": "medium",
        "impact_score": 9,
        "code": """.parallax-container { position: relative; min-height: 100vh; overflow: hidden; }
.parallax-layer {
  position: absolute; will-change: transform;
}
.parallax-bg { z-index: 1; } /* data-speed="0.1" */
.parallax-mid { z-index: 2; } /* data-speed="0.4" */
.parallax-fg { z-index: 3; } /* data-speed="0.8" */
/* GSAP: gsap.to('[data-speed]', { y: (i,el) => -ScrollTrigger.maxScroll(window) * el.dataset.speed,
  ease:'none', scrollTrigger:{ scrub:true }}) */""",
    },
    {
        "id": "modern_split_screen_hero",
        "content": "Split-screen hero layout: viewport divided into two equal halves (50/50) with content on one side and media (image, video, 3D) on the other. The split can be vertical (side by side) or diagonal (using clip-path on the dividing line). On scroll, the two halves can slide apart or one can scroll away while the other stays sticky. Add a creative dividing line: gradient, animated, or jagged via SVG. Content side: heading + subtitle + CTA. Media side: full-bleed image or interactive element. Creates impact through contrast and simplicity.",
        "category": "layout_patterns",
        "tags": ["split-screen", "hero", "50-50", "contrast", "media", "sticky", "diagonal"],
        "complexity": "medium",
        "impact_score": 9,
        "code": """.split-hero {
  display: grid; grid-template-columns: 1fr 1fr;
  min-height: 100vh;
}
.split-content {
  display: flex; flex-direction: column;
  justify-content: center; padding: 4rem;
}
.split-media { position: relative; overflow: hidden; }
.split-media img { width: 100%; height: 100%; object-fit: cover; }
.split-diagonal .split-media {
  clip-path: polygon(15% 0, 100% 0, 100% 100%, 0 100%);
}
@media (max-width: 768px) {
  .split-hero { grid-template-columns: 1fr; }
}""",
    },
    {
        "id": "modern_scroll_snap_sections",
        "content": "Scroll-snap full-page sections: each section takes 100vh and the page snaps to section boundaries during scrolling, creating a full-page scroll experience (like fullPage.js but CSS-only). Use scroll-snap-type:y mandatory on the container with overflow-y:scroll and height:100vh. Each section has scroll-snap-align:start. Add scroll-padding-top for fixed headers. Creates a presentation-style layout perfect for product showcases, portfolios, and landing pages. Mobile: consider disabling snap for better UX.",
        "category": "scroll_animations",
        "tags": ["scroll-snap", "full-page", "snap", "presentation", "css-only", "sections"],
        "complexity": "low",
        "impact_score": 8,
        "code": """.snap-container {
  height: 100vh; overflow-y: scroll;
  scroll-snap-type: y mandatory;
  scroll-behavior: smooth;
}
.snap-section {
  height: 100vh; scroll-snap-align: start;
  display: flex; align-items: center; justify-content: center;
}
.snap-container { scroll-padding-top: 64px; }
@media (max-width: 768px) {
  .snap-container { scroll-snap-type: none; height: auto; overflow: visible; }
  .snap-section { height: auto; min-height: 100vh; }
}""",
    },
    {
        "id": "modern_horizontal_scroll_section",
        "content": "Horizontal scroll section: a section that scrolls horizontally while the user scrolls vertically. The container is pinned (position:sticky or GSAP ScrollTrigger pin) and content translates left as the user scrolls down. Calculate horizontal distance from content width minus viewport width. Content items are arranged in a flex row. Creates a unique, engaging experience for timelines, project galleries, and feature tours. The outer container height must equal the total horizontal scroll distance for proper scroll mapping.",
        "category": "scroll_animations",
        "tags": ["horizontal-scroll", "pin", "gallery", "timeline", "gsap", "unique", "tour"],
        "complexity": "high",
        "impact_score": 9,
        "code": """.horizontal-section {
  height: 400vh; position: relative;
}
.horizontal-sticky {
  position: sticky; top: 0; height: 100vh;
  overflow: hidden; display: flex; align-items: center;
}
.horizontal-track {
  display: flex; gap: 2rem;
  will-change: transform;
}
.horizontal-item { flex-shrink: 0; width: 80vw; max-width: 600px; }
/* GSAP: gsap.to('.horizontal-track', { x: () => -(track.scrollWidth - window.innerWidth),
  ease:'none', scrollTrigger:{ trigger:'.horizontal-section', start:'top top', end:'bottom bottom', scrub:1 }}) */""",
    },
    {
        "id": "modern_cursor_glow_follower",
        "content": "Cursor glow follower: a soft, blurred circle of light that follows the mouse cursor across the page, illuminating content underneath. The glow is a fixed-position div (200-400px, border-radius:50%, blur(60-100px), primary color at 5-15% opacity) that updates position on mousemove with slight easing for smooth trailing. Use pointer-events:none so it does not block interactions. On dark backgrounds, the glow subtly highlights whatever the user is looking at, creating a spotlight exploration feel. Only show on desktop (hover:hover media query).",
        "category": "micro_interactions",
        "tags": ["cursor-glow", "mouse-follow", "spotlight", "interactive", "desktop", "ambient"],
        "complexity": "low",
        "impact_score": 8,
        "code": """.cursor-glow {
  position: fixed; width: 300px; height: 300px;
  border-radius: 50%; pointer-events: none; z-index: 9999;
  background: radial-gradient(circle, rgba(var(--color-primary-rgb), 0.12), transparent 70%);
  filter: blur(40px);
  transform: translate(-50%, -50%);
  transition: left 0.15s ease, top 0.15s ease;
}
@media (hover: none) { .cursor-glow { display: none; } }
/* JS: document.addEventListener('mousemove', e => { glow.style.left = e.clientX+'px'; glow.style.top = e.clientY+'px'; }) */""",
    },
]


def seed_all():
    """Seed all design patterns into the in-memory pattern store."""
    from app.services.design_knowledge import add_patterns_batch

    ids = []
    documents = []
    metadatas = []

    for p in PATTERNS:
        code_snippet = p.get("code", "")
        metadata = {
            "category": p["category"],
            "tags": ",".join(p.get("tags", [])),
            "complexity": p.get("complexity", "medium"),
            "impact_score": p.get("impact_score", 5),
        }
        if code_snippet:
            metadata["code_snippet"] = code_snippet[:4000]

        document = f"{p['content']}\n\nCode:\n{code_snippet}" if code_snippet else p["content"]

        ids.append(p["id"])
        documents.append(document)
        metadatas.append(metadata)

    add_patterns_batch(ids, documents, metadatas)
    print(f"Seeded {len(ids)} design patterns.")
    return len(ids)


if __name__ == "__main__":
    seed_all()
    stats = get_collection_stats()
    print(f"Collection stats: {stats}")
