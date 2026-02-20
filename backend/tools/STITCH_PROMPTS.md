# Prompt per Google Stitch — Guida Completa

Ogni sezione ha 3-5 prompt diversi per generare varianti uniche.
Dopo aver esportato l'HTML da Stitch, converti con:

```bash
python backend/tools/stitch_converter.py export.html --section SEZIONE --name "NOME" --tags tag1,tag2
```

> **Tip**: Aggiungi sempre "dark background" o "light background" per controllare il tema.
> Stitch non supporta animazioni — quelle vengono aggiunte automaticamente dal converter.

---

## HERO (29 varianti esistenti — obiettivo: 35+)

### hero-stitch-01: Split Editoriale
```
Hero section for a premium Italian restaurant website. Split layout: left side has large serif headline,
subtitle paragraph, and two CTA buttons (primary gradient, secondary outline). Right side has a full-height
food photography image with rounded corners. Dark background (#0a0a0a). Add a small floating stats card
showing "4.9 rating" in the bottom-left of the image area. Use generous whitespace.
```

### hero-stitch-02: Video Background
```
Full-screen hero section with video background placeholder (dark overlay at 60% opacity). Centered content:
small uppercase label, very large bold headline (72px+), subtitle text, and a single prominent CTA button.
Minimal design, lots of breathing room. Text is white on dark. Include a scroll-down indicator arrow at bottom.
```

### hero-stitch-03: Asymmetric Grid
```
Hero section with asymmetric bento grid layout. Main large image taking 60% width on the left, two stacked
smaller images on the right (40% width). Text overlay on the main image: headline, subtitle, CTA button.
Dark theme with subtle gradient overlay on images. Modern sans-serif typography.
```

### hero-stitch-04: Tipografia Bold
```
Typography-focused hero section. No images. Massive headline text (120px+) that spans full width, with
one word in a different color (the brand color). Small subtitle below. Two CTA buttons side by side.
Very minimal, lots of negative space. Light background with dark text.
```

### hero-stitch-05: Parallax Cards
```
Hero with a headline on the left and 3 floating cards on the right side arranged at different heights
(staggered). Each card has an icon, a short stat number, and label. Background is a subtle gradient.
Modern SaaS style with rounded corners on everything.
```

### hero-stitch-06: Magazine Layout
```
Magazine-style hero section. Large image taking top 2/3 of the section, with text content overlaid at
the bottom on a white card that overlaps the image. Headline, subtitle, author info with avatar, and
read time. Elegant serif fonts. Light theme.
```

---

## ABOUT (9 varianti — obiettivo: 15+)

### about-stitch-01: Timeline Verticale
```
About section with vertical timeline on the left side showing 4 milestone years (1985, 2000, 2015, 2024)
with descriptions. Right side has a large portrait photo. Section title at top. Light background.
Use connecting lines between timeline dots. Each milestone has year, title, and short description.
```

### about-stitch-02: Bento Grid
```
About us section using a bento grid layout (4 cells of different sizes). Top-left: large cell with
headline and description text. Top-right: image. Bottom-left: 3 stat counters in a row. Bottom-right:
team photo. Rounded corners on all cells, subtle shadows. Gap between cells.
```

### about-stitch-03: Split Scroll
```
About section split 50/50. Left side is sticky with a large image that stays fixed while scrolling.
Right side has scrollable content: title, long description paragraph, 3 key values with icons, and
a CTA link. Clean minimal design, light background.
```

### about-stitch-04: Citazione Grande
```
About section with a very large pull quote in the center (italic serif font, 36px+), attributed to
the founder with name, role, and small avatar photo. Above the quote: section subtitle. Below:
two-column text block with company story. Elegant, editorial feel.
```

### about-stitch-05: Cards con Valori
```
About section with heading and subtitle at top center. Below: 3 value cards in a row, each with
a large emoji icon, value title, and description. Under the cards: a full-width image with rounded
corners showing the team or workspace. Modern clean design.
```

### about-stitch-06: Numeri e Impatto
```
About section focused on impact numbers. Left side: 4 large stat numbers in a 2x2 grid (employees,
years, projects, clients) with labels below each. Right side: headline, description paragraph, and
a "Learn more" link. Dark background with white text.
```

---

## SERVICES (18 varianti — obiettivo: 22+)

### services-stitch-01: Hover Cards
```
Services section with title and subtitle centered at top. Below: 4 cards in a 2x2 grid. Each card
has a gradient icon background (small square), service title, description text, and a small arrow
link "Scopri di più". Cards have border and subtle hover shadow effect. Light background.
```

### services-stitch-02: Alternating Rows
```
Services section with alternating left-right layout. 3 service rows: odd rows have image left + text
right, even rows have text left + image right. Each row has: service number (01, 02, 03), title,
description, and a list of 3 bullet features. Clean spacious design.
```

### services-stitch-03: Icon List Minimal
```
Services section, ultra-minimal. Title at top-left. Below: vertical list of 5 services, each on its
own line with a small icon on the left, service name in bold, short description in muted text, and
a price or "Richiedi" on the far right. Thin separator lines between items.
```

### services-stitch-04: Tab Layout
```
Services section with horizontal tabs at the top (4 tab buttons). Below the tabs: content area
showing the selected service with large image on left, title, description, 4 feature bullet points,
and a CTA button on the right. Only show one tab's content. Modern design.
```

---

## TESTIMONIALS (12 varianti — obiettivo: 16+)

### testimonials-stitch-01: Cards Masonry
```
Testimonials section with masonry grid layout (3 columns, cards at different heights). Each card has:
5-star rating, quote text in italics, author name in bold, role in muted text, small avatar photo.
Cards have light background with subtle border. Section title centered at top.
```

### testimonials-stitch-02: Grande Citazione Singola
```
Single large testimonial displayed prominently. Very large quote text (28px, serif italic) centered
on the page. Below: large author avatar (80px round), name, company, and role. Background has a
subtle gradient. Navigation dots below for switching between testimonials.
```

### testimonials-stitch-03: Video Testimonials
```
Testimonials section with 3 cards in a row. Each card has a video thumbnail (16:9 with play button
overlay), quote excerpt text below, author name and company. Dark background. Cards have rounded
corners and subtle glow effect on hover.
```

### testimonials-stitch-04: Logo + Quote
```
Testimonial section showing company logos. Large quote text at center with quotation marks. Below
the quote: author name and role. Below that: a row of 6 company/client logos in grayscale.
Clean light background with lots of whitespace.
```

---

## CTA (11 varianti — obiettivo: 15+)

### cta-stitch-01: Banner Gradient
```
Full-width CTA banner section with bold gradient background (blue to purple). Centered content:
large headline, subtitle paragraph, and a white CTA button. Simple, high-impact. No images.
Generous vertical padding.
```

### cta-stitch-02: Split con Immagine
```
CTA section split 50/50. Left side: dark background with headline, description text, and primary
CTA button + secondary text link. Right side: image with rounded corners. Add decorative dots
pattern in the background.
```

### cta-stitch-03: Card Flottante
```
CTA as a floating card centered on the page with generous margin on all sides. Card has rounded
corners, subtle shadow, dark background. Inside: icon at top, headline, subtitle, email input
field with submit button inline. Newsletter-style CTA.
```

### cta-stitch-04: Countdown
```
CTA section with urgency. Large headline "Offerta Limitata", countdown timer showing days, hours,
minutes, seconds in separate boxes. Below: CTA button and a "Solo X posti rimasti" text.
Dark background with accent color highlights.
```

---

## CONTACT (9 varianti — obiettivo: 14+)

### contact-stitch-01: Form + Mappa
```
Contact section split layout. Left side: contact form with name, email, phone, message fields
and submit button. Right side: embedded map placeholder (gray rectangle with pin icon), address,
phone number, and email below. Light background.
```

### contact-stitch-02: Cards Info
```
Contact section with 3 info cards in a row at top: phone (with phone icon), email (with mail icon),
address (with map pin icon). Below the cards: full-width contact form with 2-column layout
(name + email side by side, message full width, submit button). Clean modern design.
```

### contact-stitch-03: Minimal Centrato
```
Ultra-minimal contact section. Everything centered. Small section label, headline "Parliamo del
tuo progetto", subtitle text. Below: just email address as a large clickable link, phone number,
and social media icon links in a row. Lots of whitespace. No form.
```

### contact-stitch-04: Chat Style
```
Contact section styled like a chat interface. Left side shows a mock chat conversation with
message bubbles. Right side: "Start a conversation" heading, name and email fields, message
field, and send button styled like a chat input. Fun, modern, approachable.
```

### contact-stitch-05: Orari e Info
```
Contact section for restaurants/shops. Left column: business hours table (Monday-Sunday with
times). Center column: address with map pin, phone, email, each with icon. Right column:
contact form (name, email, message, send button). Three equal columns. Dark background.
```

---

## GALLERY (7 varianti — obiettivo: 12+)

### gallery-stitch-01: Masonry Grid
```
Photo gallery section with masonry grid (3 columns, images at varying heights). 6-9 images total.
Each image has rounded corners and a subtle hover overlay showing image title. Section title and
subtitle centered at top. Filter tabs above the grid (Tutti, Interni, Piatti, Eventi).
```

### gallery-stitch-02: Carousel Full-Width
```
Gallery as a full-width horizontal carousel. Large images (16:9 aspect ratio) with slight overlap
showing the edge of next/previous images. Current image centered and larger. Navigation arrows
on left and right. Image counter (3/12) in bottom-right. No section title, immersive layout.
```

### gallery-stitch-03: Lightbox Grid
```
Gallery with uniform grid (3x2 = 6 images, all same size squares). Each image has a hover overlay
with a zoom/expand icon indicating lightbox functionality. Section title at top-left, subtitle
below. "Vedi tutte le foto" link at bottom-right. Clean borders, minimal spacing.
```

### gallery-stitch-04: Before/After Slider
```
Gallery section showing before/after comparisons. 2 large images side by side with a draggable
slider divider in the middle. "Prima" and "Dopo" labels. Section title above. A row of 4
thumbnail images below for selecting different comparisons. Dark background.
```

### gallery-stitch-05: Instagram Feed
```
Gallery styled like an Instagram feed. Grid of square images (3x3 = 9). Each image shows
heart icon and comment count on hover. Section title "Seguici su Instagram" with Instagram
icon. "Follow @ristorante" button at bottom. White background.
```

---

## PRICING (6 varianti — obiettivo: 10+)

### pricing-stitch-01: 3 Tier Cards
```
Pricing section with 3 plan cards side by side. Middle card is "highlighted" (slightly larger,
has "Popolare" badge, different border color). Each card: plan name, price with /mese,
description, list of 6 features with checkmarks, CTA button at bottom. Toggle switch at
top for "Mensile / Annuale". Light background.
```

### pricing-stitch-02: Comparison Table
```
Pricing as a comparison table. Top row: 3 plan names (Base, Pro, Enterprise) with prices.
Below: 10 feature rows with checkmarks or X marks for each plan. Sticky header.
"Scegli piano" button at bottom of each column. Clean grid lines.
```

### pricing-stitch-03: Cards Orizzontali
```
Pricing with horizontal cards stacked vertically. Each card is a full-width row showing:
plan name on left, price in center, 3 key features as tags, CTA button on right.
3 cards total. Middle card has accent border. Minimal, spacious design.
```

### pricing-stitch-04: Single Plan Focus
```
Pricing section focused on one plan. Large centered card with plan name, large price number,
billing period. Below: 2-column grid of 8 features, each with check icon and description.
CTA button below. "Hai bisogno di un piano custom?" link at very bottom. Dark card on
light background.
```

---

## FAQ (4 varianti — obiettivo: 8+)

### faq-stitch-01: Accordion Classico
```
FAQ section with accordion layout. Section title and subtitle centered at top. Below: 8 FAQ
items, each showing question text with a plus/chevron icon on the right. First item is
"expanded" showing the answer text below. Clean divider lines between items. Light background.
```

### faq-stitch-02: Due Colonne
```
FAQ section with 2-column layout. Title and subtitle at top spanning full width. Below:
questions split into two columns (4 per column). Each FAQ shows question in bold and answer
in muted text below it (all expanded, no accordion). Numbered questions (01-08).
```

### faq-stitch-03: Cards Grid
```
FAQ as a 2x3 grid of cards. Each card has a question mark icon, question text in bold, and
answer text below. Cards have light background with subtle border and rounded corners.
Section title centered above. Search bar at top for filtering FAQs.
```

### faq-stitch-04: Chat Stile
```
FAQ styled as a chat conversation. Left side shows "customer" questions in blue bubbles
(right-aligned). Right side shows "business" answers in gray bubbles (left-aligned).
6 Q&A pairs. Small bot avatar next to answers. "Hai altre domande?" CTA at bottom.
```

---

## TEAM (5 varianti — obiettivo: 9+)

### team-stitch-01: Cards con Social
```
Team section with 4 member cards in a row. Each card: large portrait photo (square, rounded),
member name in bold, role in muted text, 3 social media icons below (LinkedIn, Twitter, Email).
Cards have subtle hover effect. Section title and subtitle centered at top. Light background.
```

### team-stitch-02: Grid Overlay
```
Team section with image grid. 4 team members in a 2x2 grid. Each cell is a full image with
a dark gradient overlay at the bottom showing name and role. On hover, the overlay expands
to show a short bio text. Modern, visually-driven layout.
```

### team-stitch-03: Lista Orizzontale
```
Team section as a horizontal list. Each team member is a wide card (full-width row) showing:
large avatar on left, name and role in center, short bio text, and social links on right.
4 members stacked vertically. Alternating light/dark card backgrounds.
```

### team-stitch-04: Cerchi con Bio
```
Team section with circular avatar photos (5 members) arranged in a horizontal row. Below each
photo: name and role. When one member is "selected", a full-width bio panel appears below
showing their detailed bio text, skills, and contact. First member is pre-selected.
```

---

## STATS (3 varianti — obiettivo: 7+)

### stats-stitch-01: Counters Bold
```
Statistics section with dark background. 4 large numbers in a row: "500+", "15", "98%", "24/7".
Below each number: a short label (Clienti, Anni, Soddisfazione, Supporto). Numbers are very
large (64px+) in brand color. Labels in white muted text. Minimal, high-impact.
```

### stats-stitch-02: Cards con Icone
```
Stats section with 4 cards in a row. Each card has: a colored icon (in a circle background),
large number below, label text, and a small description. Cards have white background with
subtle shadow. Section on a light gray background. Numbers animate counting up.
```

### stats-stitch-03: Barra Orizzontale
```
Stats section with horizontal progress bars. 4 stats, each showing: label on left, progress
bar in center (filled to percentage), and number on right. Different colors for each bar.
Section title at top. Dark background. Bars have rounded ends.
```

### stats-stitch-04: Timeline Numeri
```
Stats displayed along a horizontal timeline line. 4 stat points along the line, each with
a dot marker, large number above the line, and label below. Line has gradient color.
Clean white background. Feels like a journey/progress visualization.
```

---

## FOOTER (12 varianti — obiettivo: 15+)

### footer-stitch-01: Multi-Colonna
```
Footer with 4 columns. Column 1: logo, company description, social icons. Column 2: "Servizi"
with 5 links. Column 3: "Azienda" with 5 links. Column 4: "Contatti" with address, phone,
email. Bottom bar: copyright text left, privacy/terms links right. Dark background.
```

### footer-stitch-02: Minimal Centrato
```
Ultra-minimal footer. Everything centered. Logo at top, one line of 5 nav links, social media
icons in a row, then copyright text. Single separator line. Very compact, lots of whitespace.
Dark or light background.
```

### footer-stitch-03: CTA + Footer
```
Footer that combines a CTA section at top with footer links below. Top area: "Pronto a
iniziare?" headline with email input and subscribe button. Below separator: 3 columns of
links and contact info. Bottom bar with copyright. Dark gradient background.
```

---

## NAV (3 varianti — obiettivo: 6+)

### nav-stitch-01: Sticky Trasparente
```
Navigation bar: logo on the left, 5 navigation links centered, CTA button on the right.
Transparent background (will overlay hero). White text. Sticky on scroll with blur backdrop
effect. Hamburger menu icon visible on mobile. Clean, minimal.
```

### nav-stitch-02: Centrato con Logo
```
Navigation bar with logo centered at top. Below the logo: horizontal row of 6 navigation
links evenly spaced. CTA button as the last item. Thin bottom border. White background.
Elegant, editorial feel.
```

### nav-stitch-03: Sidebar
```
Vertical sidebar navigation on the left side (250px wide). Logo at top, vertical stack of
6 nav links below, social icons at bottom. Main content area on the right. Dark sidebar
on light content. Fixed position, doesn't scroll.
```

---

## MENU (6 varianti — obiettivo: 9+)

### menu-stitch-01: Cards per Categoria
```
Restaurant menu section. 3 category tabs at top (Antipasti, Primi, Secondi). Below: grid of
menu item cards (3 per row). Each card: food photo, dish name, short description, price.
Cards have subtle border and rounded corners. Warm, inviting design.
```

### menu-stitch-02: Lista Elegante
```
Restaurant menu as an elegant list. Section divided into 2 columns. Each menu item is a line
with: dish name on left, dotted line connecting to price on right, and small description below
in italic muted text. Category headers (Antipasti, Primi, Dolci) separate groups. Serif font.
```

### menu-stitch-03: Magazine
```
Menu styled like a food magazine spread. Large featured dish image on left (50% width), with
dish name, chef's description, and price overlaid. Right side: scrollable list of other dishes
with small thumbnails. Dark background with warm accent colors.
```

---

## PROCESS (4 varianti — obiettivo: 7+)

### process-stitch-01: Steps Numerati
```
Process section showing 4 steps horizontally. Each step has: large step number (01-04) in accent
color, step title below, short description, and a small icon. Steps connected by a horizontal
dashed line. Section title centered above. Light background.
```

### process-stitch-02: Verticale con Icone
```
Vertical process/timeline. 5 steps stacked vertically with a connecting vertical line on the left.
Each step: colored dot on the line, step title, description paragraph, and small illustration/icon
on the right side. Alternating slightly for visual interest.
```

### process-stitch-03: Cards Numerate
```
Process shown as 3 large cards in a row. Each card has: large step number as watermark in
background, step title, detailed description, and a small "next arrow" pointing to the next
card. Cards have colored top border (different color each). White background.
```

---

## BLOG (3 varianti — obiettivo: 6+)

### blog-stitch-01: Cards Grid
```
Blog section with 3 article cards in a row. Each card: featured image (16:9), category tag badge,
article title, excerpt text (2 lines), author avatar + name + date at bottom. Cards have subtle
shadow on hover. Section title "Dal Nostro Blog" at top with "Vedi tutti" link.
```

### blog-stitch-02: Featured + Grid
```
Blog with featured article taking full width at top (large image, headline, excerpt, CTA) and
a 2x2 grid of 4 smaller articles below. Smaller articles show image, title, and date only.
Clean editorial design. Light background.
```

### blog-stitch-03: Lista Minimal
```
Blog as a minimal list. No images. Each article is a row with: date on far left (small, muted),
category tag, article title (bold), and arrow icon on far right. 6 articles with thin separator
lines. Section title at top-left. Very clean, text-focused.
```

---

## LOGOS / SOCIAL PROOF (1 variante — obiettivo: 4+)

### logos-stitch-01: Scorrimento
```
Client logos section. Single row of 6 company logos in grayscale. Logos auto-scroll horizontally
(marquee effect). Small text above: "Trusted by leading companies". White background, minimal
design. Logos are medium-sized and evenly spaced.
```

### logos-stitch-02: Grid con Counter
```
Social proof section. Top: 4 stat counters in a row (500+ clienti, 15 anni, etc.). Below:
grid of 8 client logos in 2 rows of 4. Logos in grayscale, colored on hover. "Le aziende
che ci hanno scelto" as section title. Light gray background.
```

### logos-stitch-03: Testimonial + Logos
```
Combined social proof: large single testimonial quote at top with author info. Below:
"Trusted by" text with a row of 6 client logos. Separator line between quote and logos.
Clean, trustworthy design. White background.
```

---

## TIMELINE (1 variante — obiettivo: 4+)

### timeline-stitch-01: Verticale Alternato
```
Timeline section with vertical line in center. Events alternate left and right of the center
line. Each event: year badge on the line, title, description, and small image. 5 events total.
Connected by the center line with dot markers. Light background.
```

### timeline-stitch-02: Orizzontale
```
Horizontal timeline section. Timeline line runs left to right with 5 event markers. Each marker
has year above the line and event title + description below. Scroll horizontally on mobile.
Active/current event is highlighted with brand color. Dark background.
```

### timeline-stitch-03: Cards Impilate
```
Timeline as stacked cards, each slightly offset to the right creating a cascading effect.
Each card: year badge, event title, description paragraph. Cards have left border in brand
color. 5 events. Section title "La Nostra Storia" at top.
```

---

## APP-DOWNLOAD (1 variante — obiettivo: 3+)

### app-stitch-01: Phone Mockup
```
App download section. Left side: headline "Scarica la nostra App", subtitle text, and two
download buttons (App Store + Google Play badges). Right side: smartphone mockup showing
app screenshot at an angle. Dark background with gradient. Modern, tech feel.
```

### app-stitch-02: Features + Download
```
App section split into 3 columns. Left: 3 feature items stacked (icon + title + description).
Center: phone mockup showing app UI. Right: 3 more feature items. Below: centered download
buttons (App Store + Google Play). Light background.
```

---

## BOOKING / RESERVATION (3+1 varianti — obiettivo: 5+)

### booking-stitch-01: Form Elegante
```
Reservation section for restaurant. Dark overlay on food background image. Centered content:
"Prenota un Tavolo" headline, subtitle. Form with: date picker, time picker, number of guests
dropdown, name, phone, special requests textarea. Submit button. Elegant, serif fonts.
```

### booking-stitch-02: Inline Compatto
```
Compact booking bar. Single horizontal row with: date field, time field, guests dropdown,
and "Prenota" button all inline. Below: small text "Oppure chiama +39 06 1234567".
Light background, rounded corners on the whole bar. Takes minimal vertical space.
```

---

## AWARDS (1 variante — obiettivo: 3+)

### awards-stitch-01: Badge Grid
```
Awards section with 2 rows of 3 award badges. Each badge: award icon/seal image, award name,
year, and issuing organization. "I Nostri Riconoscimenti" as section title. Badges in gold/amber
accent color. Dark background for prestige feel.
```

### awards-stitch-02: Banner Scorrimento
```
Awards as a horizontal scrolling banner. Each award: small trophy/medal icon, award name, and
year. Awards separated by decorative dots. Background is brand color. Text in white. Auto-scrolling
marquee effect. Compact, takes one line.
```

---

## VIDEO (2 varianti — obiettivo: 4+)

### video-stitch-01: Player Centrato
```
Video section with large centered video player (16:9). Play button overlay on video thumbnail.
Section title above, description text below. Video container has rounded corners and subtle
shadow. Dark background, video thumbnail shows a cinematic still.
```

### video-stitch-02: Background Immersivo
```
Full-width section with video as background (dark overlay). Centered text content over the
video: headline, subtitle, and play button (large circle with triangle). When "playing",
the overlay fades and video takes full attention. Immersive, cinematic feel.
```

---

## SCHEDULE / EVENTI (2 varianti — obiettivo: 4+)

### schedule-stitch-01: Agenda
```
Event schedule as a day agenda. Time slots on the left (09:00, 10:30, 12:00, etc.), event
details on the right (event title, speaker name, location tag). Color-coded by track.
Day tabs at top (Giorno 1, Giorno 2). Clean grid layout with light background.
```

### schedule-stitch-02: Cards per Giorno
```
Schedule with large cards. 3 cards in a row (one per day/session). Each card: date and day
at top, list of 4 events with times, speaker avatars. Highlighted "happening now" event.
CTA "Registrati" button at bottom of each card. Dark theme.
```

---

## COMPARISON (1 variante — obiettivo: 3+)

### comparison-stitch-01: Tabella VS
```
Comparison table with "Noi vs Concorrenza" header. Two columns: brand name (green/positive)
vs "Altri" (red/negative). 8 feature rows with checkmarks and X marks. Brand column is
highlighted with subtle background color. Clean, persuasive layout.
```

### comparison-stitch-02: Side by Side Cards
```
Two large cards side by side. Left card "Piano Base": features list with check/x icons,
price at bottom. Right card "Piano Premium" (highlighted): same features list but more checks,
"Consigliato" badge. Visual comparison made easy. Light background.
```

---

## DONATIONS (2 varianti — obiettivo: 3+)

### donations-stitch-01: Tiers con Progress
```
Donation section with 3 donation tier cards (€10, €25, €50). Each card shows what the donation
covers. Below cards: custom amount input with donate button. Progress bar at top showing
"€8.500 / €10.000 raccolti". Warm, inviting colors.
```

---

## LISTINGS (2 varianti — obiettivo: 4+)

### listings-stitch-01: Property Cards
```
Real estate listings section. 3 property cards in a row. Each card: large photo, address,
price tag, 3 detail icons (beds, baths, sqm), and "Dettagli" button. Cards have subtle
shadow and rounded corners. Filter bar above (Tipo, Prezzo, Zona). Light background.
```

### listings-stitch-02: Prodotti Grid
```
Product listing grid (2x3 = 6 items). Each item: product image (square), product name,
short description, price, "Aggiungi" button. Filter tabs at top (Tutti, Novità, Offerte).
Clean e-commerce style. White background.
```

---

## Tips per Prompt Migliori

1. **Specifica le dimensioni**: "72px headline", "16:9 image", "80px avatar"
2. **Specifica il tema**: "dark background #0a0a0a" o "light background #ffffff"
3. **Specifica la lingua**: "all text in Italian" per avere placeholder realistici
4. **Richiedi whitespace**: "generous padding", "lots of breathing room"
5. **Sii specifico sullo stile**: "serif fonts for headings" vs "modern sans-serif"
6. **Aggiungi contesto settore**: "for Italian restaurant", "for SaaS product", "for law firm"
7. **Chiedi varianti**: "generate 4 different variations"
8. **Evita animazioni**: Stitch non le supporta, le aggiunge il converter

## Conversione Rapida

```bash
# Dopo ogni export da Stitch:
cd backend/tools

# Preview (dry run)
python stitch_converter.py ~/Downloads/stitch-export.html \
  --section hero --name "Nome Variante" --tags modern,bold --dry-run

# Salva
python stitch_converter.py ~/Downloads/stitch-export.html \
  --section hero --name "Nome Variante" --tags modern,bold

# Verifica
python -c "from app.services.resource_catalog import catalog; print(catalog.get_section_coverage()['hero']['count'])"
```
