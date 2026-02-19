// ============ TEMPLATE DATA ============

export interface TemplateStyle {
  id: string;
  label: string;
  description: string;
  image: string;
  mood: string;
  primaryColor: string;
  secondaryColor: string;
  sections: string[];
}

export interface TemplateCategory {
  id: string;
  label: string;
  description: string;
  icon: string;
  image: string;
  styles: TemplateStyle[];
}

export const TEMPLATE_CATEGORIES: TemplateCategory[] = [
  {
    id: "restaurant",
    label: "Ristorante & Food",
    description: "Ristoranti, bar, pizzerie, pasticcerie",
    icon: "\u{1F37D}\uFE0F",
    image: "https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?w=600&h=400&fit=crop",
    styles: [
      {
        id: "restaurant-elegant",
        label: "Elegante & Raffinato",
        description: "Atmosfera sofisticata per ristoranti di classe",
        image: "https://images.unsplash.com/photo-1414235077428-338989a2e8c0?w=600&h=400&fit=crop",
        mood: "elegant",
        primaryColor: "#b8860b",
        secondaryColor: "#1a1a2e",
        sections: ["hero", "about", "services", "gallery", "testimonials", "contact", "footer"],
      },
      {
        id: "restaurant-cozy",
        label: "Accogliente & Tradizionale",
        description: "Calore e tradizione per trattorie e osterie",
        image: "https://images.unsplash.com/photo-1555396273-367ea4eb4db5?w=600&h=400&fit=crop",
        mood: "cozy",
        primaryColor: "#c0392b",
        secondaryColor: "#f5e6d3",
        sections: ["hero", "about", "services", "testimonials", "contact", "footer"],
      },
      {
        id: "restaurant-modern",
        label: "Moderno & Minimal",
        description: "Design pulito e contemporaneo per locali trendy",
        image: "https://images.unsplash.com/photo-1559329007-40df8a9345d8?w=600&h=400&fit=crop",
        mood: "modern",
        primaryColor: "#2d3436",
        secondaryColor: "#00b894",
        sections: ["hero", "about", "services", "gallery", "contact", "footer"],
      },
    ],
  },
  {
    id: "saas",
    label: "SaaS / Landing Page",
    description: "Startup, SaaS, prodotti digitali",
    icon: "\u{1F680}",
    image: "https://images.unsplash.com/photo-1460925895917-afdab827c52f?w=600&h=400&fit=crop",
    styles: [
      {
        id: "saas-gradient",
        label: "Gradient & Bold",
        description: "Gradiente audace per landing page d'impatto",
        image: "https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=600&h=400&fit=crop",
        mood: "bold",
        primaryColor: "#6c5ce7",
        secondaryColor: "#0984e3",
        sections: ["hero", "about", "services", "features", "testimonials", "cta", "contact", "footer"],
      },
      {
        id: "saas-clean",
        label: "Pulito & Professionale",
        description: "Layout chiaro e professionale per SaaS B2B",
        image: "https://images.unsplash.com/photo-1498050108023-c5249f4df085?w=600&h=400&fit=crop",
        mood: "modern",
        primaryColor: "#3B82F6",
        secondaryColor: "#dfe6e9",
        sections: ["hero", "about", "services", "features", "cta", "contact", "footer"],
      },
      {
        id: "saas-dark",
        label: "Dark & Tech",
        description: "Stile GitHub dark per prodotti developer",
        image: "https://images.unsplash.com/photo-1555066931-4365d14bab8c?w=600&h=400&fit=crop",
        mood: "bold",
        primaryColor: "#00cec9",
        secondaryColor: "#636e72",
        sections: ["hero", "about", "services", "features", "testimonials", "contact", "footer"],
      },
    ],
  },
  {
    id: "portfolio",
    label: "Portfolio / Creativo",
    description: "Fotografi, designer, artisti, freelancer",
    icon: "\u{1F3A8}",
    image: "https://images.unsplash.com/photo-1558618666-fcd25c85f82e?w=600&h=400&fit=crop",
    styles: [
      {
        id: "portfolio-gallery",
        label: "Galleria Editoriale",
        description: "Layout editoriale dark per fotografi e artisti",
        image: "https://images.unsplash.com/photo-1545235617-9465d2a55698?w=600&h=400&fit=crop",
        mood: "modern",
        primaryColor: "#2d3436",
        secondaryColor: "#fdcb6e",
        sections: ["hero", "about", "gallery", "services", "testimonials", "contact", "footer"],
      },
      {
        id: "portfolio-minimal",
        label: "Ultra Minimal",
        description: "Design ultra-pulito per designer e creativi",
        image: "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=600&h=400&fit=crop",
        mood: "modern",
        primaryColor: "#0c0c0c",
        secondaryColor: "#e17055",
        sections: ["hero", "about", "gallery", "contact", "footer"],
      },
      {
        id: "portfolio-creative",
        label: "Brutalist & Creativo",
        description: "Stile brutalist per creativi audaci",
        image: "https://images.unsplash.com/photo-1561070791-2526d30994b5?w=600&h=400&fit=crop",
        mood: "bold",
        primaryColor: "#e84393",
        secondaryColor: "#0984e3",
        sections: ["hero", "about", "gallery", "services", "contact", "footer"],
      },
    ],
  },
  {
    id: "ecommerce",
    label: "E-commerce / Shop",
    description: "Negozi online, vetrine prodotti",
    icon: "\u{1F6CD}\uFE0F",
    image: "https://images.unsplash.com/photo-1472851294608-062f824d29cc?w=600&h=400&fit=crop",
    styles: [
      {
        id: "ecommerce-modern",
        label: "Shop Moderno",
        description: "Layout moderno per e-commerce e vetrine",
        image: "https://images.unsplash.com/photo-1441986300917-64674bd600d8?w=600&h=400&fit=crop",
        mood: "modern",
        primaryColor: "#10B981",
        secondaryColor: "#1a1a2e",
        sections: ["hero", "about", "services", "gallery", "testimonials", "contact", "footer"],
      },
      {
        id: "ecommerce-luxury",
        label: "Luxury & Premium",
        description: "Design lussuoso per brand premium",
        image: "https://images.unsplash.com/photo-1490367532201-b9bc1dc483f6?w=600&h=400&fit=crop",
        mood: "elegant",
        primaryColor: "#c5a04b",
        secondaryColor: "#1a1a1a",
        sections: ["hero", "about", "services", "gallery", "testimonials", "contact", "footer"],
      },
    ],
  },
  {
    id: "business",
    label: "Business / Corporate",
    description: "Aziende, studi professionali, consulenze",
    icon: "\u{1F4BC}",
    image: "https://images.unsplash.com/photo-1497366216548-37526070297c?w=600&h=400&fit=crop",
    styles: [
      {
        id: "business-corporate",
        label: "Corporate Classico",
        description: "Stile professionale per aziende strutturate",
        image: "https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?w=600&h=400&fit=crop",
        mood: "corporate",
        primaryColor: "#2c3e50",
        secondaryColor: "#3498db",
        sections: ["hero", "about", "services", "features", "testimonials", "contact", "footer"],
      },
      {
        id: "business-trust",
        label: "Autorevole & Fiducia",
        description: "Design autorevole per studi professionali",
        image: "https://images.unsplash.com/photo-1507679799987-c73779587ccf?w=600&h=400&fit=crop",
        mood: "classic",
        primaryColor: "#1a3c5e",
        secondaryColor: "#c5a04b",
        sections: ["hero", "about", "services", "team", "testimonials", "contact", "footer"],
      },
      {
        id: "business-fresh",
        label: "Fresco & Innovativo",
        description: "Look fresco e moderno per startup e PMI",
        image: "https://images.unsplash.com/photo-1553877522-43269d4ea984?w=600&h=400&fit=crop",
        mood: "modern",
        primaryColor: "#00b894",
        secondaryColor: "#0984e3",
        sections: ["hero", "about", "services", "features", "cta", "contact", "footer"],
      },
    ],
  },
  {
    id: "blog",
    label: "Blog / Magazine",
    description: "Blog personali, riviste online, magazine",
    icon: "\u{1F4DD}",
    image: "https://images.unsplash.com/photo-1499750310107-5fef28a66643?w=600&h=400&fit=crop",
    styles: [
      {
        id: "blog-editorial",
        label: "Editoriale Classico",
        description: "Layout editoriale pulito per blog e magazine",
        image: "https://images.unsplash.com/photo-1457369804613-52c61a468e7d?w=600&h=400&fit=crop",
        mood: "classic",
        primaryColor: "#1a1a2e",
        secondaryColor: "#e17055",
        sections: ["hero", "about", "services", "gallery", "contact", "footer"],
      },
      {
        id: "blog-dark",
        label: "Dark Magazine",
        description: "Magazine dark con accenti neon",
        image: "https://images.unsplash.com/photo-1432821596592-e2c18b78144f?w=600&h=400&fit=crop",
        mood: "bold",
        primaryColor: "#8B5CF6",
        secondaryColor: "#1a1a1a",
        sections: ["hero", "about", "services", "gallery", "contact", "footer"],
      },
    ],
  },
  {
    id: "event",
    label: "Evento / Community",
    description: "Eventi, conferenze, meetup, community",
    icon: "\u{1F3AA}",
    image: "https://images.unsplash.com/photo-1540575467063-178a50c2df87?w=600&h=400&fit=crop",
    styles: [
      {
        id: "event-vibrant",
        label: "Vibrante & Energico",
        description: "Design vibrante per eventi e festival",
        image: "https://images.unsplash.com/photo-1492684223066-81342ee5ff30?w=600&h=400&fit=crop",
        mood: "bold",
        primaryColor: "#8B5CF6",
        secondaryColor: "#EC4899",
        sections: ["hero", "about", "services", "team", "cta", "contact", "footer"],
      },
      {
        id: "event-minimal",
        label: "Minimal & Pulito",
        description: "Layout pulito per conferenze e meetup",
        image: "https://images.unsplash.com/photo-1505373877841-8d25f7d46678?w=600&h=400&fit=crop",
        mood: "modern",
        primaryColor: "#3B82F6",
        secondaryColor: "#dfe6e9",
        sections: ["hero", "about", "services", "team", "contact", "footer"],
      },
    ],
  },
  {
    id: "custom",
    label: "Personalizzato",
    description: "Design completamente personalizzato",
    icon: "\u2728",
    image: "https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?w=600&h=400&fit=crop",
    styles: [
      {
        id: "custom-free",
        label: "Design Libero",
        description: "Inizia da zero con un design personalizzato",
        image: "https://images.unsplash.com/photo-1557672172-298e090bd0f1?w=600&h=400&fit=crop",
        mood: "modern, creative",
        primaryColor: "#6366f1",
        secondaryColor: "#8b5cf6",
        sections: ["hero", "about", "services", "features", "testimonials", "cta", "contact", "footer"],
      },
    ],
  },
];

// ============ CONSTANTS ============

export const SECTION_LABELS: Record<string, string> = {
  hero: "Hero (Header principale)",
  about: "Chi Siamo / About",
  services: "Servizi / Prodotti",
  gallery: "Galleria",
  testimonials: "Testimonianze",
  team: "Team",
  features: "Funzionalit\u00E0",
  cta: "Call to Action",
  contact: "Contatti / Form",
  footer: "Footer completo",
  menu: "Menu / Listino",
  programs: "Programmi / Corsi",
  products: "Prodotti",
  pricing: "Prezzi / Piani",
  portfolio: "Portfolio / Lavori",
};

export const SECTION_LABELS_EN: Record<string, string> = {
  hero: "Hero (Main Header)",
  about: "About Us",
  services: "Services / Products",
  gallery: "Gallery",
  testimonials: "Testimonials",
  team: "Team",
  features: "Features",
  cta: "Call to Action",
  contact: "Contact / Form",
  footer: "Full Footer",
  menu: "Menu / Price List",
  programs: "Programs / Courses",
  products: "Products",
  pricing: "Pricing / Plans",
  portfolio: "Portfolio / Work",
};

export function getSectionLabels(lang: string): Record<string, string> {
  return lang === "en" ? SECTION_LABELS_EN : SECTION_LABELS;
}

export const STYLE_OPTIONS = [
  { id: "modern-minimal", label: "Moderno / Minimal" },
  { id: "classic-elegant", label: "Classico / Elegante" },
  { id: "bold-creative", label: "Bold / Creativo" },
  { id: "corporate", label: "Corporate" },
  { id: "playful", label: "Vivo / Giocoso" },
];

export const STYLE_OPTIONS_EN = [
  { id: "modern-minimal", label: "Modern / Minimal" },
  { id: "classic-elegant", label: "Classic / Elegant" },
  { id: "bold-creative", label: "Bold / Creative" },
  { id: "corporate", label: "Corporate" },
  { id: "playful", label: "Vibrant / Playful" },
];

export function getStyleOptions(lang: string) {
  return lang === "en" ? STYLE_OPTIONS_EN : STYLE_OPTIONS;
}

export const CTA_OPTIONS = [
  { id: "contact", label: "Contattaci" },
  { id: "book", label: "Prenota" },
  { id: "quote", label: "Richiedi preventivo" },
  { id: "buy", label: "Acquista ora" },
];

export const CTA_OPTIONS_EN = [
  { id: "contact", label: "Contact Us" },
  { id: "book", label: "Book Now" },
  { id: "quote", label: "Request a Quote" },
  { id: "buy", label: "Buy Now" },
];

export function getCtaOptions(lang: string) {
  return lang === "en" ? CTA_OPTIONS_EN : CTA_OPTIONS;
}

export const ALL_SECTIONS = [
  { id: "hero", label: "Hero (Header principale)", default: true },
  { id: "about", label: "Chi Siamo", default: true },
  { id: "services", label: "Servizi / Prodotti", default: true },
  { id: "gallery", label: "Galleria", default: false },
  { id: "team", label: "Team", default: false },
  { id: "testimonials", label: "Testimonianze", default: false },
  { id: "contact", label: "Contatti / Form", default: true },
  { id: "footer", label: "Footer completo", default: true },
];

export const ALL_SECTIONS_EN = [
  { id: "hero", label: "Hero (Main Header)", default: true },
  { id: "about", label: "About Us", default: true },
  { id: "services", label: "Services / Products", default: true },
  { id: "gallery", label: "Gallery", default: false },
  { id: "team", label: "Team", default: false },
  { id: "testimonials", label: "Testimonials", default: false },
  { id: "contact", label: "Contact / Form", default: true },
  { id: "footer", label: "Full Footer", default: true },
];

export function getAllSections(lang: string) {
  return lang === "en" ? ALL_SECTIONS_EN : ALL_SECTIONS;
}

export function getCategoryLabel(category: TemplateCategory, lang: string): string {
  const labels: Record<string, string> = {
    "restaurant": lang === "en" ? "Restaurant & Food" : "Ristorante & Food",
    "saas": "SaaS / Landing Page",
    "portfolio": lang === "en" ? "Portfolio / Creative" : "Portfolio / Creativo",
    "ecommerce": "E-commerce / Shop",
    "business": "Business / Corporate",
    "blog": "Blog / Magazine",
    "event": lang === "en" ? "Event / Community" : "Evento / Community",
    "custom": lang === "en" ? "Custom" : "Personalizzato",
  };
  return labels[category.id] || category.label;
}

export function getCategoryDescription(category: TemplateCategory, lang: string): string {
  const descriptions: Record<string, string> = {
    "restaurant": lang === "en" ? "Restaurants, bars, pizzerias, bakeries" : "Ristoranti, bar, pizzerie, pasticcerie",
    "saas": lang === "en" ? "Startups, SaaS, digital products" : "Startup, SaaS, prodotti digitali",
    "portfolio": lang === "en" ? "Photographers, designers, artists, freelancers" : "Fotografi, designer, artisti, freelancer",
    "ecommerce": lang === "en" ? "Online shops, product showcases" : "Negozi online, vetrine prodotti",
    "business": lang === "en" ? "Companies, professional firms, consulting" : "Aziende, studi professionali, consulenze",
    "blog": lang === "en" ? "Personal blogs, online magazines" : "Blog personali, riviste online, magazine",
    "event": lang === "en" ? "Events, conferences, meetups, communities" : "Eventi, conferenze, meetup, community",
    "custom": lang === "en" ? "Fully custom design" : "Design completamente personalizzato",
  };
  return descriptions[category.id] || category.description;
}

const STYLE_LABELS_EN: Record<string, { label: string; description: string }> = {
  "restaurant-elegant": { label: "Elegant & Refined", description: "Sophisticated atmosphere for fine dining" },
  "restaurant-cozy": { label: "Cozy & Traditional", description: "Warmth and tradition for trattorias and taverns" },
  "restaurant-modern": { label: "Modern & Minimal", description: "Clean, contemporary design for trendy venues" },
  "saas-gradient": { label: "Gradient & Bold", description: "Bold gradients for impactful landing pages" },
  "saas-clean": { label: "Clean & Professional", description: "Clear, professional layout for B2B SaaS" },
  "saas-dark": { label: "Dark & Tech", description: "GitHub dark style for developer products" },
  "portfolio-gallery": { label: "Editorial Gallery", description: "Dark editorial layout for photographers and artists" },
  "portfolio-minimal": { label: "Ultra Minimal", description: "Ultra-clean design for designers and creatives" },
  "portfolio-creative": { label: "Brutalist & Creative", description: "Brutalist style for bold creatives" },
  "ecommerce-modern": { label: "Modern Shop", description: "Modern layout for e-commerce and showcases" },
  "ecommerce-luxury": { label: "Luxury & Premium", description: "Luxurious design for premium brands" },
  "business-corporate": { label: "Classic Corporate", description: "Professional style for structured companies" },
  "business-trust": { label: "Authoritative & Trustworthy", description: "Authoritative design for professional firms" },
  "business-fresh": { label: "Fresh & Innovative", description: "Fresh, modern look for startups and SMBs" },
  "blog-editorial": { label: "Classic Editorial", description: "Clean editorial layout for blogs and magazines" },
  "blog-dark": { label: "Dark Magazine", description: "Dark magazine with neon accents" },
  "event-vibrant": { label: "Vibrant & Energetic", description: "Vibrant design for events and festivals" },
  "event-minimal": { label: "Minimal & Clean", description: "Clean layout for conferences and meetups" },
  "custom-free": { label: "Free Design", description: "Start from scratch with a custom design" },
};

export function getStyleLabel(style: TemplateStyle, lang: string): string {
  if (lang === "en" && STYLE_LABELS_EN[style.id]) return STYLE_LABELS_EN[style.id].label;
  return style.label;
}

export function getStyleDescription(style: TemplateStyle, lang: string): string {
  if (lang === "en" && STYLE_LABELS_EN[style.id]) return STYLE_LABELS_EN[style.id].description;
  return style.description;
}

export const STYLE_TO_MOOD: Record<string, { mood: string; primaryColor: string; secondaryColor: string }> = {
  "modern-minimal": { mood: "modern", primaryColor: "#2d3436", secondaryColor: "#00b894" },
  "classic-elegant": { mood: "elegant", primaryColor: "#b8860b", secondaryColor: "#1a1a2e" },
  "bold-creative": { mood: "bold", primaryColor: "#e84393", secondaryColor: "#0984e3" },
  "corporate": { mood: "corporate", primaryColor: "#2c3e50", secondaryColor: "#3498db" },
  "playful": { mood: "modern, creative", primaryColor: "#6366f1", secondaryColor: "#8b5cf6" },
};

// ============ V2 CATEGORIES (pgvector pipeline) ============

export interface V2Category {
  slug: string;
  name: string;
  nameEn: string;
  description: string;
  descriptionEn: string;
  icon: string;
  defaultCluster: string;
  defaultColor: string;
  /** Maps to backend CategoryBlueprint.sections_required */
  sectionsRequired: string[];
}

export const V2_CATEGORIES: V2Category[] = [
  {
    slug: "ristorante",
    name: "Ristorante",
    nameEn: "Restaurant",
    description: "Ristoranti, trattorie, pizzerie, bar",
    descriptionEn: "Restaurants, trattorias, pizzerias, bars",
    icon: "🍽️",
    defaultCluster: "V1",
    defaultColor: "#b8860b",
    sectionsRequired: ["hero", "menu", "about", "gallery", "contact", "footer"],
  },
  {
    slug: "studio_professionale",
    name: "Studio Professionale",
    nameEn: "Professional Firm",
    description: "Studi legali, commercialisti, consulenti",
    descriptionEn: "Law firms, accountants, consultants",
    icon: "⚖️",
    defaultCluster: "V2",
    defaultColor: "#1a3c5e",
    sectionsRequired: ["hero", "services", "about", "contact", "footer"],
  },
  {
    slug: "portfolio",
    name: "Portfolio",
    nameEn: "Portfolio",
    description: "Fotografi, designer, artisti, freelancer",
    descriptionEn: "Photographers, designers, artists, freelancers",
    icon: "🎨",
    defaultCluster: "V4",
    defaultColor: "#2d3436",
    sectionsRequired: ["hero", "gallery", "about", "contact", "footer"],
  },
  {
    slug: "fitness",
    name: "Fitness",
    nameEn: "Fitness",
    description: "Palestre, personal trainer, centri sportivi",
    descriptionEn: "Gyms, personal trainers, sports centers",
    icon: "💪",
    defaultCluster: "V1",
    defaultColor: "#e84393",
    sectionsRequired: ["hero", "programs", "about", "gallery", "contact", "footer"],
  },
  {
    slug: "bellezza",
    name: "Bellezza",
    nameEn: "Beauty",
    description: "Parrucchieri, estetisti, centri benessere",
    descriptionEn: "Hairdressers, beauticians, wellness centers",
    icon: "💅",
    defaultCluster: "V1",
    defaultColor: "#c5a04b",
    sectionsRequired: ["hero", "services", "gallery", "about", "contact", "footer"],
  },
  {
    slug: "salute",
    name: "Salute",
    nameEn: "Healthcare",
    description: "Medici, dentisti, fisioterapisti, cliniche",
    descriptionEn: "Doctors, dentists, physiotherapists, clinics",
    icon: "🏥",
    defaultCluster: "V2",
    defaultColor: "#3B82F6",
    sectionsRequired: ["hero", "services", "about", "team", "contact", "footer"],
  },
  {
    slug: "saas",
    name: "SaaS / Tech",
    nameEn: "SaaS / Tech",
    description: "Startup, prodotti digitali, landing page",
    descriptionEn: "Startups, digital products, landing pages",
    icon: "🚀",
    defaultCluster: "V3",
    defaultColor: "#6c5ce7",
    sectionsRequired: ["hero", "features", "pricing", "about", "contact", "footer"],
  },
  {
    slug: "ecommerce",
    name: "E-commerce",
    nameEn: "E-commerce",
    description: "Negozi online, vetrine prodotti, shop",
    descriptionEn: "Online shops, product showcases",
    icon: "🛍️",
    defaultCluster: "V3",
    defaultColor: "#10B981",
    sectionsRequired: ["hero", "products", "about", "contact", "footer"],
  },
  {
    slug: "artigiani",
    name: "Artigiani",
    nameEn: "Craftsmen",
    description: "Idraulici, elettricisti, falegnami, artigiani",
    descriptionEn: "Plumbers, electricians, carpenters, craftsmen",
    icon: "🔧",
    defaultCluster: "V5",
    defaultColor: "#d35400",
    sectionsRequired: ["hero", "services", "about", "gallery", "contact", "footer"],
  },
  {
    slug: "agenzia",
    name: "Agenzia",
    nameEn: "Agency",
    description: "Agenzie marketing, comunicazione, digitali",
    descriptionEn: "Marketing, communication, digital agencies",
    icon: "📊",
    defaultCluster: "V2",
    defaultColor: "#8B5CF6",
    sectionsRequired: ["hero", "services", "about", "portfolio", "contact", "footer"],
  },
];

export function getV2CategoryName(cat: V2Category, lang: string): string {
  return lang === "en" ? cat.nameEn : cat.name;
}

export function getV2CategoryDescription(cat: V2Category, lang: string): string {
  return lang === "en" ? cat.descriptionEn : cat.description;
}

export function findV2CategoryBySlug(slug: string): V2Category | null {
  return V2_CATEGORIES.find(c => c.slug === slug) || null;
}

// ============ HELPER: find style by ID ============
export function findStyleById(styleId: string): { category: TemplateCategory; style: TemplateStyle } | null {
  for (const cat of TEMPLATE_CATEGORIES) {
    for (const st of cat.styles) {
      if (st.id === styleId) return { category: cat, style: st };
    }
  }
  return null;
}

// ============ PREVIEW HTML GENERATORS ============

const wrap = (body: string, bg: string, text: string, fontFamily: string) =>
  `<!DOCTYPE html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><style>*{margin:0;padding:0;box-sizing:border-box}body{font-family:${fontFamily};background:${bg};color:${text};overflow-x:hidden}a{text-decoration:none;color:inherit}</style></head><body>${body}</body></html>`;

const sans = "'Inter',system-ui,-apple-system,sans-serif";
const serif = "'Georgia','Times New Roman',serif";

export function generateStylePreviewHtml(style: TemplateStyle, categoryLabel: string): string {
  const generators: Record<string, () => string> = {

    "restaurant-elegant": () => {
      const body = `
<div style="position:relative;min-height:70vh;display:flex;align-items:center;justify-content:center;background:#0c0a08;overflow:hidden">
  <div style="position:absolute;top:20px;left:20px;width:60px;height:60px;border-top:2px solid #b8860b;border-left:2px solid #b8860b"></div>
  <div style="position:absolute;top:20px;right:20px;width:60px;height:60px;border-top:2px solid #b8860b;border-right:2px solid #b8860b"></div>
  <div style="position:absolute;bottom:20px;left:20px;width:60px;height:60px;border-bottom:2px solid #b8860b;border-left:2px solid #b8860b"></div>
  <div style="position:absolute;bottom:20px;right:20px;width:60px;height:60px;border-bottom:2px solid #b8860b;border-right:2px solid #b8860b"></div>
  <div style="text-align:center;padding:40px">
    <div style="font-size:12px;letter-spacing:6px;color:#b8860b;text-transform:uppercase;margin-bottom:16px">Ristorante</div>
    <h1 style="font-family:${serif};font-size:52px;font-style:italic;color:#f5f0e8;margin-bottom:12px;font-weight:400">La Bella Cucina</h1>
    <div style="width:80px;height:1px;background:#b8860b;margin:16px auto"></div>
    <p style="font-size:15px;color:#a09882;max-width:400px;margin:0 auto 28px;line-height:1.7">Un viaggio gastronomico attraverso i sapori autentici della tradizione italiana</p>
    <a style="display:inline-block;padding:12px 36px;border:1px solid #b8860b;color:#b8860b;font-size:12px;letter-spacing:3px;text-transform:uppercase">Prenota un Tavolo</a>
  </div>
</div>
<div style="padding:70px 40px;background:#0f0d0a">
  <div style="text-align:center;margin-bottom:48px">
    <div style="font-size:11px;letter-spacing:5px;color:#b8860b;text-transform:uppercase;margin-bottom:10px">Menu</div>
    <h2 style="font-family:${serif};font-size:30px;color:#f5f0e8;font-weight:400;font-style:italic">Le Nostre Specialit\u00E0</h2>
  </div>
  <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:32px;max-width:900px;margin:0 auto">
    <div style="text-align:center;padding:32px 20px;border:1px solid rgba(184,134,11,0.2)">
      <div style="font-size:11px;letter-spacing:4px;color:#b8860b;text-transform:uppercase;margin-bottom:14px">Antipasti</div>
      <div style="width:40px;height:1px;background:#b8860b;margin:0 auto 14px"></div>
      <p style="font-size:13px;color:#8a7e6c;line-height:1.8">Carpaccio di manzo<br>Bruschetta mista<br>Tartare di tonno</p>
    </div>
    <div style="text-align:center;padding:32px 20px;border:1px solid rgba(184,134,11,0.2)">
      <div style="font-size:11px;letter-spacing:4px;color:#b8860b;text-transform:uppercase;margin-bottom:14px">Primi Piatti</div>
      <div style="width:40px;height:1px;background:#b8860b;margin:0 auto 14px"></div>
      <p style="font-size:13px;color:#8a7e6c;line-height:1.8">Risotto al tartufo<br>Tagliatelle al rag\u00F9<br>Ravioli di ricotta</p>
    </div>
    <div style="text-align:center;padding:32px 20px;border:1px solid rgba(184,134,11,0.2)">
      <div style="font-size:11px;letter-spacing:4px;color:#b8860b;text-transform:uppercase;margin-bottom:14px">Secondi</div>
      <div style="width:40px;height:1px;background:#b8860b;margin:0 auto 14px"></div>
      <p style="font-size:13px;color:#8a7e6c;line-height:1.8">Filetto al pepe<br>Branzino al forno<br>Ossobuco milanese</p>
    </div>
  </div>
</div>`;
      return wrap(body, "#0c0a08", "#f5f0e8", serif);
    },

    "restaurant-cozy": () => {
      const body = `
<div style="min-height:70vh;display:flex;align-items:center;justify-content:center;background:#fdf6ee;position:relative;overflow:hidden">
  <div style="position:absolute;top:-80px;right:-80px;width:300px;height:300px;border-radius:50%;background:rgba(192,57,43,0.06)"></div>
  <div style="position:absolute;bottom:-60px;left:-60px;width:250px;height:250px;border-radius:50%;background:rgba(192,57,43,0.04)"></div>
  <div style="text-align:center;padding:40px;position:relative;z-index:1">
    <div style="font-size:48px;margin-bottom:16px">\u{1F372}</div>
    <h1 style="font-size:46px;color:#3d2c1e;margin-bottom:12px;font-weight:800">Sapori di Casa</h1>
    <p style="font-size:16px;color:#7a6555;max-width:420px;margin:0 auto 28px;line-height:1.7">Dove ogni piatto racconta una storia di famiglia e tradizione</p>
    <a style="display:inline-block;padding:14px 32px;background:#c0392b;color:#fff;border-radius:50px;font-size:14px;font-weight:600">Scopri il Menu</a>
  </div>
</div>
<div style="padding:70px 40px;background:#fdf6ee">
  <div style="text-align:center;margin-bottom:48px">
    <h2 style="font-size:30px;color:#3d2c1e;font-weight:700">I Nostri Valori</h2>
    <p style="color:#7a6555;margin-top:8px">Cosa ci rende speciali dal 1985</p>
  </div>
  <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:28px;max-width:900px;margin:0 auto">
    <div style="background:#fff;padding:32px 24px;border-radius:16px;text-align:center;box-shadow:0 2px 12px rgba(0,0,0,0.05)">
      <div style="font-size:32px;margin-bottom:12px">\u{1F331}</div>
      <h3 style="font-size:17px;color:#3d2c1e;margin-bottom:8px;font-weight:700">Ingredienti Freschi</h3>
      <p style="font-size:13px;color:#7a6555;line-height:1.6">Selezioniamo ogni giorno i migliori prodotti locali e di stagione</p>
    </div>
    <div style="background:#fff;padding:32px 24px;border-radius:16px;text-align:center;box-shadow:0 2px 12px rgba(0,0,0,0.05)">
      <div style="font-size:32px;margin-bottom:12px">\u{2764}\uFE0F</div>
      <h3 style="font-size:17px;color:#3d2c1e;margin-bottom:8px;font-weight:700">Ricette di Famiglia</h3>
      <p style="font-size:13px;color:#7a6555;line-height:1.6">Tradizioni tramandate di generazione in generazione</p>
    </div>
    <div style="background:#fff;padding:32px 24px;border-radius:16px;text-align:center;box-shadow:0 2px 12px rgba(0,0,0,0.05)">
      <div style="font-size:32px;margin-bottom:12px">\u{1F37D}\uFE0F</div>
      <h3 style="font-size:17px;color:#3d2c1e;margin-bottom:8px;font-weight:700">Atmosfera Unica</h3>
      <p style="font-size:13px;color:#7a6555;line-height:1.6">Un ambiente caldo e accogliente dove sentirsi a casa</p>
    </div>
  </div>
</div>`;
      return wrap(body, "#fdf6ee", "#3d2c1e", sans);
    },

    "restaurant-modern": () => {
      const body = `
<div style="min-height:70vh;display:flex;align-items:center;background:#fafaf8">
  <div style="display:grid;grid-template-columns:1fr 1px 1fr;width:100%;max-width:1000px;margin:0 auto;padding:40px">
    <div style="display:flex;flex-direction:column;justify-content:center;padding-right:48px">
      <div style="font-size:11px;letter-spacing:4px;color:#00b894;text-transform:uppercase;margin-bottom:20px;font-family:monospace">Est. 2024</div>
      <h1 style="font-size:64px;font-weight:200;color:#2d3436;line-height:1;margin-bottom:16px">Puro.</h1>
      <p style="font-size:14px;color:#888;line-height:1.8;max-width:300px">Cucina essenziale. Ingredienti puri. Sapore autentico senza compromessi.</p>
    </div>
    <div style="background:#e0e0e0"></div>
    <div style="display:flex;flex-direction:column;justify-content:center;padding-left:48px">
      <div style="margin-bottom:24px">
        <div style="font-size:11px;letter-spacing:3px;color:#aaa;text-transform:uppercase;margin-bottom:6px">Pranzo</div>
        <div style="font-size:16px;color:#2d3436;font-weight:300">12:00 \u2014 14:30</div>
      </div>
      <div style="margin-bottom:24px">
        <div style="font-size:11px;letter-spacing:3px;color:#aaa;text-transform:uppercase;margin-bottom:6px">Cena</div>
        <div style="font-size:16px;color:#2d3436;font-weight:300">19:00 \u2014 23:00</div>
      </div>
      <a style="display:inline-block;padding:10px 0;font-size:12px;letter-spacing:3px;color:#00b894;text-transform:uppercase;border-bottom:1px solid #00b894;align-self:flex-start">Riserva \u2192</a>
    </div>
  </div>
</div>
<div style="padding:70px 40px;background:#fff">
  <div style="max-width:900px;margin:0 auto">
    <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:40px">
      <div style="border-top:1px solid #e0e0e0;padding-top:20px">
        <div style="font-size:11px;letter-spacing:3px;color:#00b894;text-transform:uppercase;margin-bottom:10px;font-family:monospace">01</div>
        <h3 style="font-size:16px;color:#2d3436;font-weight:400;margin-bottom:8px">Stagionale</h3>
        <p style="font-size:13px;color:#999;line-height:1.6">Menu che cambia con le stagioni, rispettando i ritmi della natura</p>
      </div>
      <div style="border-top:1px solid #e0e0e0;padding-top:20px">
        <div style="font-size:11px;letter-spacing:3px;color:#00b894;text-transform:uppercase;margin-bottom:10px;font-family:monospace">02</div>
        <h3 style="font-size:16px;color:#2d3436;font-weight:400;margin-bottom:8px">Locale</h3>
        <p style="font-size:13px;color:#999;line-height:1.6">Produttori locali selezionati entro 50km dal nostro ristorante</p>
      </div>
      <div style="border-top:1px solid #e0e0e0;padding-top:20px">
        <div style="font-size:11px;letter-spacing:3px;color:#00b894;text-transform:uppercase;margin-bottom:10px;font-family:monospace">03</div>
        <h3 style="font-size:16px;color:#2d3436;font-weight:400;margin-bottom:8px">Essenziale</h3>
        <p style="font-size:13px;color:#999;line-height:1.6">Pochi ingredienti, massima qualit\u00E0. La perfezione nella semplicit\u00E0</p>
      </div>
    </div>
  </div>
</div>`;
      return wrap(body, "#fafaf8", "#2d3436", sans);
    },

    "saas-gradient": () => {
      const body = `
<div style="position:relative;min-height:70vh;display:flex;align-items:center;justify-content:center;background:#08070e;overflow:hidden">
  <div style="position:absolute;inset:0;background:repeating-linear-gradient(0deg,transparent,transparent 2px,rgba(255,255,255,0.015) 2px,rgba(255,255,255,0.015) 4px)"></div>
  <div style="position:absolute;top:10%;left:15%;width:350px;height:350px;border-radius:50%;background:radial-gradient(circle,rgba(108,92,231,0.25),transparent 70%);filter:blur(80px)"></div>
  <div style="position:absolute;bottom:10%;right:15%;width:300px;height:300px;border-radius:50%;background:radial-gradient(circle,rgba(9,132,227,0.2),transparent 70%);filter:blur(80px)"></div>
  <div style="text-align:center;padding:40px;position:relative;z-index:1">
    <div style="display:inline-block;padding:6px 16px;border:1px solid rgba(108,92,231,0.3);border-radius:50px;font-size:12px;color:#a29bfe;margin-bottom:24px">Lancia il futuro oggi \u{1F680}</div>
    <h1 style="font-size:56px;font-weight:800;line-height:1.1;margin-bottom:16px"><span style="background:linear-gradient(135deg,#6c5ce7,#0984e3);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text">THE FUTURE</span><br><span style="color:#fff">IS NOW</span></h1>
    <p style="font-size:15px;color:#8a8a9a;max-width:440px;margin:0 auto 28px;line-height:1.7">La piattaforma all-in-one che trasforma la tua idea in un prodotto di successo</p>
    <div style="display:flex;gap:12px;justify-content:center">
      <a style="display:inline-block;padding:13px 28px;background:linear-gradient(135deg,#6c5ce7,#0984e3);color:#fff;border-radius:8px;font-size:14px;font-weight:600">Inizia Gratis</a>
      <a style="display:inline-block;padding:13px 28px;border:1px solid rgba(255,255,255,0.15);color:#ccc;border-radius:8px;font-size:14px">Guarda Demo</a>
    </div>
  </div>
</div>
<div style="padding:70px 40px;background:#0a0914">
  <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:24px;max-width:900px;margin:0 auto;text-align:center">
    <div style="padding:24px 16px">
      <div style="font-size:36px;font-weight:800;background:linear-gradient(135deg,#6c5ce7,#0984e3);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;margin-bottom:6px">10K+</div>
      <div style="font-size:12px;color:#6a6a7a;letter-spacing:1px;text-transform:uppercase">Utenti Attivi</div>
    </div>
    <div style="padding:24px 16px">
      <div style="font-size:36px;font-weight:800;background:linear-gradient(135deg,#6c5ce7,#0984e3);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;margin-bottom:6px">99.9%</div>
      <div style="font-size:12px;color:#6a6a7a;letter-spacing:1px;text-transform:uppercase">Uptime</div>
    </div>
    <div style="padding:24px 16px">
      <div style="font-size:36px;font-weight:800;background:linear-gradient(135deg,#6c5ce7,#0984e3);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;margin-bottom:6px">50+</div>
      <div style="font-size:12px;color:#6a6a7a;letter-spacing:1px;text-transform:uppercase">Integrazioni</div>
    </div>
    <div style="padding:24px 16px">
      <div style="font-size:36px;font-weight:800;background:linear-gradient(135deg,#6c5ce7,#0984e3);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;margin-bottom:6px">4.9\u2605</div>
      <div style="font-size:12px;color:#6a6a7a;letter-spacing:1px;text-transform:uppercase">Rating</div>
    </div>
  </div>
</div>`;
      return wrap(body, "#08070e", "#e0e0e8", sans);
    },

    "saas-clean": () => {
      const body = `
<div style="border-top:4px solid transparent;border-image:linear-gradient(90deg,#3B82F6,#60a5fa) 1">
  <div style="min-height:70vh;display:flex;align-items:center;background:#fff;padding:60px 40px">
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:60px;max-width:1000px;margin:0 auto;width:100%;align-items:center">
      <div>
        <div style="display:inline-block;padding:4px 12px;background:#EBF5FF;color:#3B82F6;border-radius:4px;font-size:12px;font-weight:600;margin-bottom:20px">Nuovo: AI integrata</div>
        <h1 style="font-size:42px;font-weight:700;color:#1a1a2e;line-height:1.15;margin-bottom:14px">Gestisci tutto<br>in un unico posto</h1>
        <p style="font-size:15px;color:#6b7280;line-height:1.7;margin-bottom:24px">La piattaforma che semplifica il tuo lavoro quotidiano con strumenti intelligenti e intuitivi.</p>
        <div style="display:flex;gap:12px">
          <a style="display:inline-block;padding:12px 24px;background:#3B82F6;color:#fff;border-radius:6px;font-size:14px;font-weight:600">Prova Gratis</a>
          <a style="display:inline-block;padding:12px 24px;color:#3B82F6;font-size:14px;font-weight:600">Scopri di pi\u00F9 \u2192</a>
        </div>
      </div>
      <div style="display:grid;grid-template-columns:1fr 1fr;gap:14px">
        <div style="background:#f8fafc;padding:22px 18px;border-radius:10px;border:1px solid #e5e7eb">
          <div style="width:32px;height:32px;background:#EBF5FF;border-radius:8px;display:flex;align-items:center;justify-content:center;font-size:16px;margin-bottom:10px">\u26A1</div>
          <div style="font-size:14px;font-weight:600;color:#1a1a2e;margin-bottom:4px">Veloce</div>
          <div style="font-size:12px;color:#9ca3af">Setup in 2 min</div>
        </div>
        <div style="background:#f8fafc;padding:22px 18px;border-radius:10px;border:1px solid #e5e7eb">
          <div style="width:32px;height:32px;background:#EBF5FF;border-radius:8px;display:flex;align-items:center;justify-content:center;font-size:16px;margin-bottom:10px">\u{1F512}</div>
          <div style="font-size:14px;font-weight:600;color:#1a1a2e;margin-bottom:4px">Sicuro</div>
          <div style="font-size:12px;color:#9ca3af">Crittografia E2E</div>
        </div>
        <div style="background:#f8fafc;padding:22px 18px;border-radius:10px;border:1px solid #e5e7eb">
          <div style="width:32px;height:32px;background:#EBF5FF;border-radius:8px;display:flex;align-items:center;justify-content:center;font-size:16px;margin-bottom:10px">\u{1F4CA}</div>
          <div style="font-size:14px;font-weight:600;color:#1a1a2e;margin-bottom:4px">Analytics</div>
          <div style="font-size:12px;color:#9ca3af">Dati in real-time</div>
        </div>
        <div style="background:#f8fafc;padding:22px 18px;border-radius:10px;border:1px solid #e5e7eb">
          <div style="width:32px;height:32px;background:#EBF5FF;border-radius:8px;display:flex;align-items:center;justify-content:center;font-size:16px;margin-bottom:10px">\u{1F916}</div>
          <div style="font-size:14px;font-weight:600;color:#1a1a2e;margin-bottom:4px">AI</div>
          <div style="font-size:12px;color:#9ca3af">Automazione smart</div>
        </div>
      </div>
    </div>
  </div>
</div>
<div style="padding:32px 40px;background:#f8fafc;border-top:1px solid #e5e7eb;border-bottom:1px solid #e5e7eb">
  <div style="display:grid;grid-template-columns:repeat(4,1fr);max-width:900px;margin:0 auto;text-align:center">
    <div style="padding:12px;border-right:1px solid #e5e7eb"><div style="font-size:24px;font-weight:700;color:#1a1a2e">2M+</div><div style="font-size:12px;color:#9ca3af">Download</div></div>
    <div style="padding:12px;border-right:1px solid #e5e7eb"><div style="font-size:24px;font-weight:700;color:#1a1a2e">150+</div><div style="font-size:12px;color:#9ca3af">Paesi</div></div>
    <div style="padding:12px;border-right:1px solid #e5e7eb"><div style="font-size:24px;font-weight:700;color:#1a1a2e">99.9%</div><div style="font-size:12px;color:#9ca3af">Uptime</div></div>
    <div style="padding:12px"><div style="font-size:24px;font-weight:700;color:#1a1a2e">24/7</div><div style="font-size:12px;color:#9ca3af">Supporto</div></div>
  </div>
</div>`;
      return wrap(body, "#fff", "#1a1a2e", sans);
    },

    "saas-dark": () => {
      const body = `
<div style="position:relative;min-height:70vh;display:flex;align-items:center;justify-content:center;background:#0d1117;overflow:hidden">
  <div style="position:absolute;top:5%;right:20%;width:400px;height:400px;border-radius:50%;background:radial-gradient(circle,rgba(0,206,201,0.12),transparent 70%);filter:blur(80px)"></div>
  <div style="position:absolute;bottom:10%;left:10%;width:300px;height:300px;border-radius:50%;background:radial-gradient(circle,rgba(0,206,201,0.08),transparent 70%);filter:blur(60px)"></div>
  <div style="text-align:center;padding:40px;position:relative;z-index:1">
    <div style="display:inline-block;padding:5px 14px;background:rgba(0,206,201,0.1);border:1px solid rgba(0,206,201,0.2);border-radius:50px;font-size:12px;color:#00cec9;margin-bottom:24px">v2.0 \u2014 Now with AI</div>
    <h1 style="font-size:50px;font-weight:700;color:#e6edf3;line-height:1.15;margin-bottom:14px">Build faster with<br><span style="color:#00cec9">DevPlatform</span></h1>
    <p style="font-size:15px;color:#8b949e;max-width:440px;margin:0 auto 28px;line-height:1.7">Developer tools that accelerate your workflow. Ship code with confidence.</p>
    <a style="display:inline-block;padding:13px 28px;background:#00cec9;color:#0d1117;border-radius:8px;font-size:14px;font-weight:600">Get Started Free</a>
  </div>
</div>
<div style="padding:70px 40px;background:#0d1117">
  <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:20px;max-width:900px;margin:0 auto">
    <div style="background:rgba(255,255,255,0.03);backdrop-filter:blur(12px);border:1px solid rgba(255,255,255,0.06);border-radius:12px;padding:28px 22px">
      <div style="width:36px;height:36px;background:rgba(0,206,201,0.1);border-radius:8px;display:flex;align-items:center;justify-content:center;font-size:18px;margin-bottom:14px">\u26A1</div>
      <h3 style="font-size:16px;color:#e6edf3;margin-bottom:8px;font-weight:600">Lightning Fast</h3>
      <p style="font-size:13px;color:#8b949e;line-height:1.6">Sub-millisecond response times with edge computing worldwide</p>
    </div>
    <div style="background:rgba(255,255,255,0.03);backdrop-filter:blur(12px);border:1px solid rgba(255,255,255,0.06);border-radius:12px;padding:28px 22px">
      <div style="width:36px;height:36px;background:rgba(0,206,201,0.1);border-radius:8px;display:flex;align-items:center;justify-content:center;font-size:18px;margin-bottom:14px">\u{1F6E1}\uFE0F</div>
      <h3 style="font-size:16px;color:#e6edf3;margin-bottom:8px;font-weight:600">Secure by Default</h3>
      <p style="font-size:13px;color:#8b949e;line-height:1.6">Enterprise-grade security with zero-trust architecture built in</p>
    </div>
    <div style="background:rgba(255,255,255,0.03);backdrop-filter:blur(12px);border:1px solid rgba(255,255,255,0.06);border-radius:12px;padding:28px 22px">
      <div style="width:36px;height:36px;background:rgba(0,206,201,0.1);border-radius:8px;display:flex;align-items:center;justify-content:center;font-size:18px;margin-bottom:14px">\u{1F504}</div>
      <h3 style="font-size:16px;color:#e6edf3;margin-bottom:8px;font-weight:600">Auto Scaling</h3>
      <p style="font-size:13px;color:#8b949e;line-height:1.6">Seamless horizontal scaling from zero to millions of requests</p>
    </div>
  </div>
</div>`;
      return wrap(body, "#0d1117", "#e6edf3", sans);
    },

    "portfolio-gallery": () => {
      const body = `
<div style="min-height:70vh;display:flex;align-items:center;background:#111;padding:60px 40px;position:relative">
  <div style="position:absolute;left:50%;top:60px;bottom:60px;width:1px;background:rgba(253,203,110,0.15)"></div>
  <div style="display:grid;grid-template-columns:1fr 1fr;gap:80px;max-width:1000px;margin:0 auto;width:100%;align-items:center">
    <div>
      <div style="font-size:11px;letter-spacing:5px;color:#fdcb6e;text-transform:uppercase;margin-bottom:20px">Portfolio</div>
      <h1 style="font-family:${serif};font-size:48px;font-style:italic;color:#f5f5f0;line-height:1.15;margin-bottom:14px;font-weight:400">Marco Visconti</h1>
      <p style="font-size:14px;color:#777;line-height:1.8;margin-bottom:24px">Fotografo e direttore creativo con 15 anni di esperienza in moda, architettura e ritrattistica artistica.</p>
      <a style="font-size:12px;letter-spacing:3px;color:#fdcb6e;text-transform:uppercase;border-bottom:1px solid #fdcb6e;padding-bottom:2px">Vedi i lavori \u2192</a>
    </div>
    <div style="position:relative">
      <div style="background:#1a1a1a;border:1px solid rgba(253,203,110,0.15);aspect-ratio:3/4;display:flex;align-items:center;justify-content:center;transform:rotate(2deg)">
        <div style="font-size:11px;letter-spacing:3px;color:#555;text-transform:uppercase">Featured Work</div>
      </div>
    </div>
  </div>
</div>
<div style="padding:70px 40px;background:#0e0e0e">
  <div style="max-width:900px;margin:0 auto">
    <div style="font-size:11px;letter-spacing:5px;color:#fdcb6e;text-transform:uppercase;margin-bottom:32px">Progetti Selezionati</div>
    <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:24px">
      <div>
        <div style="background:#1a1a1a;aspect-ratio:4/3;display:flex;align-items:flex-end;padding:16px;border:1px solid rgba(255,255,255,0.05)">
          <div style="font-family:${serif};font-size:13px;color:#999;font-style:italic">01 \u2014 Architettura</div>
        </div>
      </div>
      <div>
        <div style="background:#1a1a1a;aspect-ratio:4/3;display:flex;align-items:flex-end;padding:16px;border:1px solid rgba(255,255,255,0.05)">
          <div style="font-family:${serif};font-size:13px;color:#999;font-style:italic">02 \u2014 Ritratti</div>
        </div>
      </div>
      <div>
        <div style="background:#1a1a1a;aspect-ratio:4/3;display:flex;align-items:flex-end;padding:16px;border:1px solid rgba(255,255,255,0.05)">
          <div style="font-family:${serif};font-size:13px;color:#999;font-style:italic">03 \u2014 Moda</div>
        </div>
      </div>
    </div>
  </div>
</div>`;
      return wrap(body, "#111", "#f5f5f0", serif);
    },

    "portfolio-minimal": () => {
      const body = `
<div style="min-height:70vh;display:flex;align-items:center;justify-content:center;background:#fff;padding:60px 40px">
  <div style="text-align:center;max-width:600px">
    <div style="font-size:11px;letter-spacing:4px;color:#e17055;text-transform:uppercase;margin-bottom:20px">Portfolio 2024</div>
    <h1 style="font-size:52px;font-weight:200;color:#0c0c0c;line-height:1.15;margin-bottom:14px">Designer &amp; Maker</h1>
    <p style="font-size:15px;color:#999;line-height:1.7;margin-bottom:32px">Creo esperienze digitali che connettono brand e persone attraverso design intenzionale e minimalista.</p>
    <a style="font-size:12px;letter-spacing:3px;color:#0c0c0c;text-transform:uppercase;border-bottom:1px solid #0c0c0c;padding-bottom:4px">Esplora \u2192</a>
  </div>
</div>
<div style="padding:70px 40px;background:#fff">
  <div style="max-width:600px;margin:0 auto">
    <div style="font-size:11px;letter-spacing:3px;color:#bbb;text-transform:uppercase;margin-bottom:32px">Indice lavori</div>
    <div style="border-top:1px solid #eee">
      <div style="display:flex;align-items:center;justify-content:space-between;padding:20px 0;border-bottom:1px solid #eee">
        <div style="display:flex;align-items:baseline;gap:16px">
          <span style="font-size:11px;color:#e17055;font-family:monospace">01</span>
          <span style="font-size:16px;color:#0c0c0c;font-weight:400">Brand Identity \u2014 Luxe Studio</span>
        </div>
        <span style="font-size:14px;color:#ccc">\u2192</span>
      </div>
      <div style="display:flex;align-items:center;justify-content:space-between;padding:20px 0;border-bottom:1px solid #eee">
        <div style="display:flex;align-items:baseline;gap:16px">
          <span style="font-size:11px;color:#e17055;font-family:monospace">02</span>
          <span style="font-size:16px;color:#0c0c0c;font-weight:400">Web Design \u2014 Arch Magazine</span>
        </div>
        <span style="font-size:14px;color:#ccc">\u2192</span>
      </div>
      <div style="display:flex;align-items:center;justify-content:space-between;padding:20px 0;border-bottom:1px solid #eee">
        <div style="display:flex;align-items:baseline;gap:16px">
          <span style="font-size:11px;color:#e17055;font-family:monospace">03</span>
          <span style="font-size:16px;color:#0c0c0c;font-weight:400">App Design \u2014 Mindful</span>
        </div>
        <span style="font-size:14px;color:#ccc">\u2192</span>
      </div>
      <div style="display:flex;align-items:center;justify-content:space-between;padding:20px 0;border-bottom:1px solid #eee">
        <div style="display:flex;align-items:baseline;gap:16px">
          <span style="font-size:11px;color:#e17055;font-family:monospace">04</span>
          <span style="font-size:16px;color:#0c0c0c;font-weight:400">Packaging \u2014 Olio Toscano</span>
        </div>
        <span style="font-size:14px;color:#ccc">\u2192</span>
      </div>
    </div>
  </div>
</div>`;
      return wrap(body, "#fff", "#0c0c0c", sans);
    },

    "portfolio-creative": () => {
      const body = `
<div style="min-height:70vh;display:flex;align-items:center;background:#f5f5f0;padding:60px 40px;position:relative">
  <div style="position:absolute;inset:0;background-image:radial-gradient(circle,#ddd 1px,transparent 1px);background-size:24px 24px;opacity:0.4"></div>
  <div style="display:grid;grid-template-columns:1fr 2px 1fr;gap:48px;max-width:1000px;margin:0 auto;width:100%;position:relative;z-index:1">
    <div style="display:flex;flex-direction:column;justify-content:center">
      <div style="font-size:11px;letter-spacing:4px;color:#e84393;text-transform:uppercase;margin-bottom:16px;font-weight:700">Creative Studio</div>
      <h1 style="font-size:56px;font-weight:900;color:#0c0c0c;line-height:1;margin-bottom:14px;text-transform:uppercase">CREATIVO.</h1>
      <p style="font-size:14px;color:#666;line-height:1.7">Design audace per brand coraggiosi. Rompiamo le regole con intenzione.</p>
    </div>
    <div style="background:#0c0c0c"></div>
    <div style="display:flex;flex-direction:column;justify-content:center">
      <div style="margin-bottom:24px">
        <div style="font-size:48px;font-weight:900;color:#0c0c0c;line-height:1">01</div>
        <div style="font-size:14px;color:#666;margin-top:4px">Brand Identity</div>
      </div>
      <div style="margin-bottom:24px">
        <div style="font-size:48px;font-weight:900;color:#0c0c0c;line-height:1">02</div>
        <div style="font-size:14px;color:#666;margin-top:4px">Web & Digital</div>
      </div>
      <div>
        <div style="font-size:48px;font-weight:900;color:#0c0c0c;line-height:1">03</div>
        <div style="font-size:14px;color:#666;margin-top:4px">Art Direction</div>
      </div>
    </div>
  </div>
</div>
<div style="padding:70px 40px;background:#f5f5f0;border-top:2px solid #0c0c0c">
  <div style="max-width:900px;margin:0 auto">
    <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:20px">
      <div style="border:2px solid #0c0c0c;padding:28px 20px">
        <div style="font-size:11px;letter-spacing:3px;color:#e84393;text-transform:uppercase;font-weight:700;margin-bottom:10px">Sezione 01</div>
        <h3 style="font-size:18px;font-weight:900;color:#0c0c0c;text-transform:uppercase;margin-bottom:8px">Branding</h3>
        <p style="font-size:13px;color:#666;line-height:1.6">Identit\u00E0 visive che lasciano il segno e raccontano storie autentiche</p>
      </div>
      <div style="border:2px solid #0c0c0c;padding:28px 20px">
        <div style="font-size:11px;letter-spacing:3px;color:#0984e3;text-transform:uppercase;font-weight:700;margin-bottom:10px">Sezione 02</div>
        <h3 style="font-size:18px;font-weight:900;color:#0c0c0c;text-transform:uppercase;margin-bottom:8px">Digital</h3>
        <p style="font-size:13px;color:#666;line-height:1.6">Esperienze web che sfidano le convenzioni del design tradizionale</p>
      </div>
      <div style="border:2px solid #0c0c0c;padding:28px 20px">
        <div style="font-size:11px;letter-spacing:3px;color:#e84393;text-transform:uppercase;font-weight:700;margin-bottom:10px">Sezione 03</div>
        <h3 style="font-size:18px;font-weight:900;color:#0c0c0c;text-transform:uppercase;margin-bottom:8px">Motion</h3>
        <p style="font-size:13px;color:#666;line-height:1.6">Animazioni e video che catturano l'attenzione in ogni frame</p>
      </div>
    </div>
  </div>
</div>`;
      return wrap(body, "#f5f5f0", "#0c0c0c", sans);
    },

    "ecommerce-modern": () => {
      const body = `
<div style="min-height:70vh;display:flex;align-items:center;background:#fff;padding:60px 40px">
  <div style="max-width:1000px;margin:0 auto;width:100%;text-align:center">
    <div style="display:inline-block;padding:4px 14px;background:#ECFDF5;color:#10B981;border-radius:50px;font-size:12px;font-weight:600;margin-bottom:20px">Nuova Collezione</div>
    <h1 style="font-size:48px;font-weight:700;color:#1a1a2e;line-height:1.15;margin-bottom:14px">Scopri il tuo stile</h1>
    <p style="font-size:16px;color:#6b7280;max-width:480px;margin:0 auto 28px;line-height:1.7">Prodotti selezionati con cura per chi cerca qualit\u00E0 e design senza compromessi.</p>
    <a style="display:inline-block;padding:14px 32px;background:linear-gradient(135deg,#10B981,#059669);color:#fff;border-radius:10px;font-size:15px;font-weight:600">Esplora il Catalogo</a>
  </div>
</div>
<div style="padding:70px 40px;background:#f9fafb">
  <div style="text-align:center;margin-bottom:40px">
    <h2 style="font-size:28px;color:#1a1a2e;font-weight:700">Prodotti in Evidenza</h2>
    <p style="font-size:14px;color:#9ca3af;margin-top:6px">I pi\u00F9 amati dai nostri clienti</p>
  </div>
  <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:24px;max-width:900px;margin:0 auto">
    <div style="background:#fff;border-radius:14px;overflow:hidden;border:1px solid #e5e7eb">
      <div style="background:#f3f4f6;aspect-ratio:4/3;display:flex;align-items:center;justify-content:center;position:relative">
        <div style="font-size:13px;color:#aaa">Prodotto</div>
        <div style="position:absolute;top:12px;right:12px;background:#10B981;color:#fff;font-size:11px;padding:3px 10px;border-radius:50px;font-weight:600">\u20AC 49.90</div>
      </div>
      <div style="padding:18px">
        <h3 style="font-size:15px;color:#1a1a2e;font-weight:600;margin-bottom:4px">Essential Tee</h3>
        <p style="font-size:12px;color:#9ca3af">Cotone organico 100%</p>
      </div>
    </div>
    <div style="background:#fff;border-radius:14px;overflow:hidden;border:1px solid #e5e7eb">
      <div style="background:#f3f4f6;aspect-ratio:4/3;display:flex;align-items:center;justify-content:center;position:relative">
        <div style="font-size:13px;color:#aaa">Prodotto</div>
        <div style="position:absolute;top:12px;right:12px;background:#10B981;color:#fff;font-size:11px;padding:3px 10px;border-radius:50px;font-weight:600">\u20AC 89.00</div>
      </div>
      <div style="padding:18px">
        <h3 style="font-size:15px;color:#1a1a2e;font-weight:600;margin-bottom:4px">Minimal Jacket</h3>
        <p style="font-size:12px;color:#9ca3af">Tessuto tecnico waterproof</p>
      </div>
    </div>
    <div style="background:#fff;border-radius:14px;overflow:hidden;border:1px solid #e5e7eb">
      <div style="background:#f3f4f6;aspect-ratio:4/3;display:flex;align-items:center;justify-content:center;position:relative">
        <div style="font-size:13px;color:#aaa">Prodotto</div>
        <div style="position:absolute;top:12px;right:12px;background:#10B981;color:#fff;font-size:11px;padding:3px 10px;border-radius:50px;font-weight:600">\u20AC 129.00</div>
      </div>
      <div style="padding:18px">
        <h3 style="font-size:15px;color:#1a1a2e;font-weight:600;margin-bottom:4px">Canvas Sneaker</h3>
        <p style="font-size:12px;color:#9ca3af">Design italiano artigianale</p>
      </div>
    </div>
  </div>
</div>`;
      return wrap(body, "#fff", "#1a1a2e", sans);
    },

    "ecommerce-luxury": () => {
      const body = `
<div style="min-height:70vh;display:flex;align-items:center;justify-content:center;background:#0a0a0a;position:relative;overflow:hidden">
  <div style="position:absolute;top:0;left:0;right:0;height:1px;background:linear-gradient(90deg,transparent,#c5a04b,transparent)"></div>
  <div style="text-align:center;padding:40px;position:relative;z-index:1">
    <div style="font-family:${serif};font-size:12px;letter-spacing:8px;color:#c5a04b;text-transform:uppercase;margin-bottom:20px">Collezione Esclusiva</div>
    <h1 style="font-family:${serif};font-size:52px;color:#f5f0e8;line-height:1.15;margin-bottom:14px;font-weight:400;font-style:italic">Lusso Senza Tempo</h1>
    <div style="width:60px;height:1px;background:#c5a04b;margin:20px auto"></div>
    <p style="font-size:14px;color:#8a8070;max-width:400px;margin:0 auto 28px;line-height:1.8">Artigianato italiano d'eccellenza. Ogni pezzo racconta una storia di maestria e passione.</p>
    <a style="display:inline-block;padding:13px 36px;border:1px solid #c5a04b;color:#c5a04b;font-size:12px;letter-spacing:3px;text-transform:uppercase;font-family:${serif}">Scopri</a>
  </div>
</div>
<div style="padding:70px 40px;background:#0e0e0e">
  <div style="text-align:center;margin-bottom:48px">
    <div style="font-family:${serif};font-size:11px;letter-spacing:6px;color:#c5a04b;text-transform:uppercase;margin-bottom:10px">Selezione</div>
    <h2 style="font-family:${serif};font-size:28px;color:#f5f0e8;font-weight:400;font-style:italic">Pezzi Iconici</h2>
  </div>
  <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:24px;max-width:900px;margin:0 auto">
    <div style="border:1px solid rgba(197,160,75,0.15);overflow:hidden">
      <div style="background:#151515;aspect-ratio:3/4;display:flex;align-items:center;justify-content:center;position:relative">
        <div style="font-family:${serif};font-size:12px;color:#555;font-style:italic">Articolo I</div>
        <div style="position:absolute;top:14px;left:14px;background:rgba(197,160,75,0.15);color:#c5a04b;font-size:9px;padding:4px 10px;letter-spacing:2px;text-transform:uppercase">Exclusive</div>
      </div>
      <div style="padding:18px;text-align:center;border-top:1px solid rgba(197,160,75,0.1)">
        <h3 style="font-family:${serif};font-size:15px;color:#f5f0e8;font-weight:400;margin-bottom:6px">Borsa Classica</h3>
        <div style="font-size:13px;color:#c5a04b">\u20AC 1.290</div>
      </div>
    </div>
    <div style="border:1px solid rgba(197,160,75,0.15);overflow:hidden">
      <div style="background:#151515;aspect-ratio:3/4;display:flex;align-items:center;justify-content:center;position:relative">
        <div style="font-family:${serif};font-size:12px;color:#555;font-style:italic">Articolo II</div>
        <div style="position:absolute;top:14px;left:14px;background:rgba(197,160,75,0.15);color:#c5a04b;font-size:9px;padding:4px 10px;letter-spacing:2px;text-transform:uppercase">Exclusive</div>
      </div>
      <div style="padding:18px;text-align:center;border-top:1px solid rgba(197,160,75,0.1)">
        <h3 style="font-family:${serif};font-size:15px;color:#f5f0e8;font-weight:400;margin-bottom:6px">Orologio Heritage</h3>
        <div style="font-size:13px;color:#c5a04b">\u20AC 3.450</div>
      </div>
    </div>
    <div style="border:1px solid rgba(197,160,75,0.15);overflow:hidden">
      <div style="background:#151515;aspect-ratio:3/4;display:flex;align-items:center;justify-content:center;position:relative">
        <div style="font-family:${serif};font-size:12px;color:#555;font-style:italic">Articolo III</div>
        <div style="position:absolute;top:14px;left:14px;background:rgba(197,160,75,0.15);color:#c5a04b;font-size:9px;padding:4px 10px;letter-spacing:2px;text-transform:uppercase">Exclusive</div>
      </div>
      <div style="padding:18px;text-align:center;border-top:1px solid rgba(197,160,75,0.1)">
        <h3 style="font-family:${serif};font-size:15px;color:#f5f0e8;font-weight:400;margin-bottom:6px">Scarpe Artigianali</h3>
        <div style="font-size:13px;color:#c5a04b">\u20AC 890</div>
      </div>
    </div>
  </div>
</div>`;
      return wrap(body, "#0a0a0a", "#f5f0e8", serif);
    },

    "business-corporate": () => {
      const body = `
<div style="min-height:70vh;display:flex;align-items:center;background:#fff">
  <div style="display:grid;grid-template-columns:1fr 1fr;width:100%">
    <div style="background:#2c3e50;padding:60px 48px;display:flex;flex-direction:column;justify-content:center">
      <div style="font-size:11px;letter-spacing:4px;color:#3498db;text-transform:uppercase;margin-bottom:20px">Consulenza Strategica</div>
      <h1 style="font-size:42px;font-weight:700;color:#fff;line-height:1.15;margin-bottom:14px">Il partner per la crescita del tuo business</h1>
      <p style="font-size:15px;color:#95a5b8;line-height:1.7;margin-bottom:24px">Soluzioni aziendali su misura per guidare la tua impresa verso risultati concreti e misurabili.</p>
      <a style="display:inline-block;padding:12px 28px;background:#3498db;color:#fff;border-radius:6px;font-size:14px;font-weight:600;align-self:flex-start">Richiedi Consulenza</a>
    </div>
    <div style="background:#f1f5f9;padding:60px 48px;display:flex;flex-direction:column;justify-content:center;gap:20px">
      <div style="background:#fff;padding:22px;border-radius:10px;border:1px solid #e2e8f0;display:flex;align-items:center;gap:16px">
        <div style="width:40px;height:40px;background:#EBF5FF;border-radius:8px;display:flex;align-items:center;justify-content:center;font-size:18px;flex-shrink:0">\u{1F4C8}</div>
        <div><div style="font-size:14px;font-weight:600;color:#2c3e50">Crescita del 40%</div><div style="font-size:12px;color:#94a3b8">Media clienti nel primo anno</div></div>
      </div>
      <div style="background:#fff;padding:22px;border-radius:10px;border:1px solid #e2e8f0;display:flex;align-items:center;gap:16px">
        <div style="width:40px;height:40px;background:#EBF5FF;border-radius:8px;display:flex;align-items:center;justify-content:center;font-size:18px;flex-shrink:0">\u{1F3C6}</div>
        <div><div style="font-size:14px;font-weight:600;color:#2c3e50">500+ Progetti</div><div style="font-size:12px;color:#94a3b8">Completati con successo</div></div>
      </div>
      <div style="background:#fff;padding:22px;border-radius:10px;border:1px solid #e2e8f0;display:flex;align-items:center;gap:16px">
        <div style="width:40px;height:40px;background:#EBF5FF;border-radius:8px;display:flex;align-items:center;justify-content:center;font-size:18px;flex-shrink:0">\u{1F310}</div>
        <div><div style="font-size:14px;font-weight:600;color:#2c3e50">20 Paesi</div><div style="font-size:12px;color:#94a3b8">Presenza internazionale</div></div>
      </div>
    </div>
  </div>
</div>
<div style="padding:28px 40px;background:#2c3e50;border-top:1px solid rgba(52,152,219,0.2)">
  <div style="display:grid;grid-template-columns:repeat(4,1fr);max-width:900px;margin:0 auto;text-align:center">
    <div style="padding:12px;border-right:1px solid rgba(255,255,255,0.1)"><div style="font-size:22px;font-weight:700;color:#3498db">15+</div><div style="font-size:11px;color:#95a5b8;margin-top:2px">Anni Esperienza</div></div>
    <div style="padding:12px;border-right:1px solid rgba(255,255,255,0.1)"><div style="font-size:22px;font-weight:700;color:#3498db">98%</div><div style="font-size:11px;color:#95a5b8;margin-top:2px">Clienti Soddisfatti</div></div>
    <div style="padding:12px;border-right:1px solid rgba(255,255,255,0.1)"><div style="font-size:22px;font-weight:700;color:#3498db">50+</div><div style="font-size:11px;color:#95a5b8;margin-top:2px">Professionisti</div></div>
    <div style="padding:12px"><div style="font-size:22px;font-weight:700;color:#3498db">24/7</div><div style="font-size:11px;color:#95a5b8;margin-top:2px">Supporto</div></div>
  </div>
</div>`;
      return wrap(body, "#fff", "#2c3e50", sans);
    },

    "business-trust": () => {
      const body = `
<div style="min-height:70vh;display:flex;align-items:center;justify-content:center;background:linear-gradient(180deg,#1a3c5e 0%,#2a5a8a 50%,#f4f0ec 50%,#f4f0ec 100%)">
  <div style="text-align:center;padding:40px;max-width:700px">
    <div style="font-family:${serif};font-size:11px;letter-spacing:6px;color:#c5a04b;text-transform:uppercase;margin-bottom:20px">Studio Legale Associato</div>
    <h1 style="font-family:${serif};font-size:46px;color:#fff;line-height:1.2;margin-bottom:14px;font-weight:400">Tradizione, Competenza, Fiducia</h1>
    <p style="font-size:15px;color:rgba(255,255,255,0.7);line-height:1.7;margin-bottom:28px;max-width:500px;margin-left:auto;margin-right:auto">Da oltre 30 anni al fianco di imprese e professionisti con competenza e dedizione</p>
    <a style="display:inline-block;padding:13px 32px;background:#c5a04b;color:#fff;font-size:13px;letter-spacing:2px;text-transform:uppercase;font-family:${serif}">Consulenza Gratuita</a>
  </div>
</div>
<div style="padding:70px 40px;background:#f4f0ec">
  <div style="max-width:700px;margin:0 auto">
    <div style="text-align:center;margin-bottom:48px">
      <h2 style="font-family:${serif};font-size:28px;color:#1a3c5e;font-weight:400">Le Nostre Tappe</h2>
    </div>
    <div style="position:relative;padding-left:48px">
      <div style="position:absolute;left:14px;top:8px;bottom:8px;width:1px;background:#e0d6c8"></div>
      <div style="margin-bottom:32px;position:relative">
        <div style="position:absolute;left:-42px;top:4px;width:10px;height:10px;background:#c5a04b;border-radius:50%"></div>
        <div style="font-family:${serif};font-size:13px;color:#c5a04b;margin-bottom:4px">1993</div>
        <h3 style="font-family:${serif};font-size:18px;color:#1a3c5e;font-weight:400;margin-bottom:4px">Fondazione</h3>
        <p style="font-size:13px;color:#7a7060;line-height:1.6">Nasce lo studio con la missione di offrire eccellenza nel diritto commerciale</p>
      </div>
      <div style="margin-bottom:32px;position:relative">
        <div style="position:absolute;left:-42px;top:4px;width:10px;height:10px;background:#c5a04b;border-radius:50%"></div>
        <div style="font-family:${serif};font-size:13px;color:#c5a04b;margin-bottom:4px">2008</div>
        <h3 style="font-family:${serif};font-size:18px;color:#1a3c5e;font-weight:400;margin-bottom:4px">Espansione Internazionale</h3>
        <p style="font-size:13px;color:#7a7060;line-height:1.6">Apertura della divisione internazionale con partnership europee</p>
      </div>
      <div style="position:relative">
        <div style="position:absolute;left:-42px;top:4px;width:10px;height:10px;background:#c5a04b;border-radius:50%"></div>
        <div style="font-family:${serif};font-size:13px;color:#c5a04b;margin-bottom:4px">2024</div>
        <h3 style="font-family:${serif};font-size:18px;color:#1a3c5e;font-weight:400;margin-bottom:4px">Innovazione Digitale</h3>
        <p style="font-size:13px;color:#7a7060;line-height:1.6">Integrazione di strumenti AI per servizi legali pi\u00F9 efficienti e accessibili</p>
      </div>
    </div>
  </div>
</div>`;
      return wrap(body, "#f4f0ec", "#1a3c5e", serif);
    },

    "business-fresh": () => {
      const body = `
<div style="min-height:70vh;display:flex;align-items:center;justify-content:center;background:#fff;padding:60px 40px">
  <div style="text-align:center;max-width:600px">
    <div style="display:inline-block;padding:5px 16px;background:linear-gradient(135deg,rgba(0,184,148,0.1),rgba(9,132,227,0.1));border-radius:50px;font-size:12px;font-weight:600;color:#00b894;margin-bottom:20px">Innovazione per PMI</div>
    <h1 style="font-size:46px;font-weight:700;color:#1a1a2e;line-height:1.15;margin-bottom:14px">Fai crescere il tuo business</h1>
    <p style="font-size:15px;color:#6b7280;line-height:1.7;margin-bottom:28px">Strategie digitali e consulenza su misura per portare la tua azienda al livello successivo.</p>
    <a style="display:inline-block;padding:13px 28px;background:linear-gradient(135deg,#00b894,#0984e3);color:#fff;border-radius:10px;font-size:14px;font-weight:600">Inizia Ora</a>
  </div>
</div>
<div style="padding:70px 40px;background:#f9fafb">
  <div style="max-width:900px;margin:0 auto">
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:20px">
      <div style="background:linear-gradient(135deg,#00b894,#0984e3);border-radius:16px;padding:40px 28px;grid-row:1/3;display:flex;flex-direction:column;justify-content:flex-end">
        <div style="font-size:48px;font-weight:800;color:#fff;margin-bottom:8px">+127%</div>
        <h3 style="font-size:20px;color:#fff;font-weight:600;margin-bottom:6px">Crescita Media</h3>
        <p style="font-size:13px;color:rgba(255,255,255,0.8);line-height:1.6">I nostri clienti registrano una crescita media del 127% nel primo anno di collaborazione</p>
      </div>
      <div style="background:#fff;border-radius:16px;padding:28px;border:1px solid #e5e7eb">
        <div style="font-size:28px;margin-bottom:8px">\u{1F4CA}</div>
        <h3 style="font-size:16px;font-weight:600;color:#1a1a2e;margin-bottom:6px">Data Analytics</h3>
        <p style="font-size:13px;color:#9ca3af;line-height:1.5">Decisioni basate su dati reali e insights azionabili</p>
      </div>
      <div style="background:#fff;border-radius:16px;padding:28px;border:1px solid #e5e7eb">
        <div style="font-size:28px;margin-bottom:8px">\u{1F916}</div>
        <h3 style="font-size:16px;font-weight:600;color:#1a1a2e;margin-bottom:6px">AI & Automazione</h3>
        <p style="font-size:13px;color:#9ca3af;line-height:1.5">Processi automatizzati con intelligenza artificiale</p>
      </div>
    </div>
  </div>
</div>`;
      return wrap(body, "#fff", "#1a1a2e", sans);
    },

    "blog-editorial": () => {
      const body = `
<div style="min-height:70vh;display:flex;align-items:center;justify-content:center;background:#fafafa;padding:60px 40px">
  <div style="text-align:center;max-width:700px">
    <div style="font-size:11px;letter-spacing:5px;color:#e17055;text-transform:uppercase;margin-bottom:20px">Magazine Digitale</div>
    <h1 style="font-family:${serif};font-size:52px;color:#1a1a2e;line-height:1.15;margin-bottom:16px;font-weight:400">Storie che ispirano, idee che trasformano</h1>
    <p style="font-size:16px;color:#6b7280;line-height:1.7;margin-bottom:28px;max-width:500px;margin-left:auto;margin-right:auto">Esploriamo design, tecnologia e cultura con uno sguardo fresco e indipendente.</p>
    <a style="display:inline-block;padding:12px 28px;background:#1a1a2e;color:#fff;border-radius:6px;font-size:14px;font-weight:500">Leggi l'ultimo numero</a>
  </div>
</div>
<div style="padding:70px 40px;background:#fff">
  <div style="max-width:900px;margin:0 auto">
    <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:32px">
      <h2 style="font-family:${serif};font-size:24px;color:#1a1a2e;font-weight:400">Articoli Recenti</h2>
      <a style="font-size:13px;color:#e17055">Vedi tutti \u2192</a>
    </div>
    <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:28px">
      <div>
        <div style="background:#f3f4f6;aspect-ratio:16/10;border-radius:8px;margin-bottom:14px;display:flex;align-items:center;justify-content:center">
          <div style="font-size:12px;color:#aaa">Immagine</div>
        </div>
        <div style="display:flex;gap:8px;margin-bottom:8px">
          <span style="font-size:10px;letter-spacing:1px;color:#e17055;text-transform:uppercase;font-weight:600">Design</span>
          <span style="font-size:10px;color:#ccc">\u00B7</span>
          <span style="font-size:10px;color:#aaa">5 min lettura</span>
        </div>
        <h3 style="font-family:${serif};font-size:17px;color:#1a1a2e;font-weight:400;line-height:1.4;margin-bottom:6px">Il futuro del design \u00E8 nell'intelligenza artificiale</h3>
        <p style="font-size:13px;color:#9ca3af;line-height:1.5">Come l'AI sta ridefinendo il processo creativo dei designer moderni</p>
      </div>
      <div>
        <div style="background:#f3f4f6;aspect-ratio:16/10;border-radius:8px;margin-bottom:14px;display:flex;align-items:center;justify-content:center">
          <div style="font-size:12px;color:#aaa">Immagine</div>
        </div>
        <div style="display:flex;gap:8px;margin-bottom:8px">
          <span style="font-size:10px;letter-spacing:1px;color:#e17055;text-transform:uppercase;font-weight:600">Tech</span>
          <span style="font-size:10px;color:#ccc">\u00B7</span>
          <span style="font-size:10px;color:#aaa">8 min lettura</span>
        </div>
        <h3 style="font-family:${serif};font-size:17px;color:#1a1a2e;font-weight:400;line-height:1.4;margin-bottom:6px">10 strumenti essenziali per sviluppatori nel 2024</h3>
        <p style="font-size:13px;color:#9ca3af;line-height:1.5">La nostra selezione degli strumenti che ogni developer dovrebbe conoscere</p>
      </div>
      <div>
        <div style="background:#f3f4f6;aspect-ratio:16/10;border-radius:8px;margin-bottom:14px;display:flex;align-items:center;justify-content:center">
          <div style="font-size:12px;color:#aaa">Immagine</div>
        </div>
        <div style="display:flex;gap:8px;margin-bottom:8px">
          <span style="font-size:10px;letter-spacing:1px;color:#e17055;text-transform:uppercase;font-weight:600">Cultura</span>
          <span style="font-size:10px;color:#ccc">\u00B7</span>
          <span style="font-size:10px;color:#aaa">3 min lettura</span>
        </div>
        <h3 style="font-family:${serif};font-size:17px;color:#1a1a2e;font-weight:400;line-height:1.4;margin-bottom:6px">Minimalismo digitale: meno \u00E8 davvero di pi\u00F9</h3>
        <p style="font-size:13px;color:#9ca3af;line-height:1.5">Un approccio consapevole alla tecnologia per una vita pi\u00F9 equilibrata</p>
      </div>
    </div>
  </div>
</div>`;
      return wrap(body, "#fafafa", "#1a1a2e", sans);
    },

    "blog-dark": () => {
      const body = `
<div style="min-height:70vh;display:flex;align-items:center;justify-content:center;background:#0f0f1a;position:relative;overflow:hidden;padding:60px 40px">
  <div style="position:absolute;top:20%;left:30%;width:300px;height:300px;border-radius:50%;background:radial-gradient(circle,rgba(139,92,246,0.15),transparent 70%);filter:blur(60px)"></div>
  <div style="text-align:center;position:relative;z-index:1;max-width:600px">
    <div style="display:inline-block;padding:5px 14px;background:rgba(139,92,246,0.1);border:1px solid rgba(139,92,246,0.2);border-radius:50px;font-size:12px;color:#8B5CF6;margin-bottom:20px">Neon Magazine</div>
    <h1 style="font-size:48px;font-weight:700;color:#f0eef6;line-height:1.15;margin-bottom:14px">Dove le idee<br>prendono luce</h1>
    <p style="font-size:15px;color:#6b6880;line-height:1.7;margin-bottom:28px">Tech, cultura e innovazione. Il magazine per chi guarda al futuro con curiosit\u00E0.</p>
    <a style="display:inline-block;padding:12px 28px;background:#8B5CF6;color:#fff;border-radius:8px;font-size:14px;font-weight:600">Esplora</a>
  </div>
</div>
<div style="padding:70px 40px;background:#0f0f1a">
  <div style="max-width:900px;margin:0 auto">
    <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:20px">
      <div style="background:rgba(255,255,255,0.03);border:1px solid rgba(139,92,246,0.1);border-radius:12px;overflow:hidden">
        <div style="background:rgba(139,92,246,0.05);aspect-ratio:16/10;display:flex;align-items:center;justify-content:center">
          <div style="font-size:12px;color:#4a4660">Immagine</div>
        </div>
        <div style="padding:18px">
          <div style="font-size:10px;letter-spacing:1px;color:#8B5CF6;text-transform:uppercase;font-weight:600;margin-bottom:8px">AI & Future</div>
          <h3 style="font-size:15px;color:#f0eef6;font-weight:600;line-height:1.4;margin-bottom:6px">Generative AI: il prossimo capitolo</h3>
          <p style="font-size:12px;color:#6b6880;line-height:1.5">Come l'AI generativa sta cambiando creativit\u00E0 e produttivit\u00E0</p>
        </div>
      </div>
      <div style="background:rgba(255,255,255,0.03);border:1px solid rgba(139,92,246,0.1);border-radius:12px;overflow:hidden">
        <div style="background:rgba(139,92,246,0.05);aspect-ratio:16/10;display:flex;align-items:center;justify-content:center">
          <div style="font-size:12px;color:#4a4660">Immagine</div>
        </div>
        <div style="padding:18px">
          <div style="font-size:10px;letter-spacing:1px;color:#8B5CF6;text-transform:uppercase;font-weight:600;margin-bottom:8px">Design</div>
          <h3 style="font-size:15px;color:#f0eef6;font-weight:600;line-height:1.4;margin-bottom:6px">Dark mode: non solo estetica</h3>
          <p style="font-size:12px;color:#6b6880;line-height:1.5">La scienza dietro la preferenza per le interfacce scure</p>
        </div>
      </div>
      <div style="background:rgba(255,255,255,0.03);border:1px solid rgba(139,92,246,0.1);border-radius:12px;overflow:hidden">
        <div style="background:rgba(139,92,246,0.05);aspect-ratio:16/10;display:flex;align-items:center;justify-content:center">
          <div style="font-size:12px;color:#4a4660">Immagine</div>
        </div>
        <div style="padding:18px">
          <div style="font-size:10px;letter-spacing:1px;color:#8B5CF6;text-transform:uppercase;font-weight:600;margin-bottom:8px">Startup</div>
          <h3 style="font-size:15px;color:#f0eef6;font-weight:600;line-height:1.4;margin-bottom:6px">Da zero a IPO in 18 mesi</h3>
          <p style="font-size:12px;color:#6b6880;line-height:1.5">La storia di una startup italiana nel mondo della fintech</p>
        </div>
      </div>
    </div>
  </div>
</div>`;
      return wrap(body, "#0f0f1a", "#f0eef6", sans);
    },

    "event-vibrant": () => {
      const body = `
<div style="min-height:70vh;display:flex;align-items:center;justify-content:center;background:linear-gradient(135deg,#8B5CF6,#EC4899);position:relative;overflow:hidden;padding:60px 40px">
  <div style="position:absolute;top:10%;right:10%;width:200px;height:200px;border:2px solid rgba(255,255,255,0.1);border-radius:50%"></div>
  <div style="position:absolute;bottom:10%;left:10%;width:150px;height:150px;border:2px solid rgba(255,255,255,0.08);border-radius:50%"></div>
  <div style="text-align:center;position:relative;z-index:1">
    <div style="display:inline-block;padding:6px 16px;background:rgba(255,255,255,0.15);border-radius:50px;font-size:12px;color:#fff;margin-bottom:20px;backdrop-filter:blur(4px)">15-17 Marzo 2025</div>
    <h1 style="font-size:54px;font-weight:800;color:#fff;line-height:1.1;margin-bottom:14px">DESIGN<br>FESTIVAL</h1>
    <p style="font-size:16px;color:rgba(255,255,255,0.85);max-width:440px;margin:0 auto 28px;line-height:1.7">Tre giorni di talk, workshop e networking con i migliori creativi italiani e internazionali.</p>
    <a style="display:inline-block;padding:14px 32px;background:#fff;color:#8B5CF6;border-radius:50px;font-size:15px;font-weight:700">Acquista il Biglietto</a>
  </div>
</div>
<div style="padding:70px 40px;background:#fff">
  <div style="text-align:center;margin-bottom:48px">
    <h2 style="font-size:28px;color:#1a1a2e;font-weight:700">Speaker Principali</h2>
    <p style="font-size:14px;color:#9ca3af;margin-top:6px">I protagonisti dell'edizione 2025</p>
  </div>
  <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:28px;max-width:800px;margin:0 auto">
    <div style="text-align:center">
      <div style="width:80px;height:80px;border-radius:50%;background:linear-gradient(135deg,#8B5CF6,#EC4899);margin:0 auto 14px;display:flex;align-items:center;justify-content:center;font-size:28px;color:#fff">\u{1F468}\u200D\u{1F3A8}</div>
      <h3 style="font-size:16px;color:#1a1a2e;font-weight:600;margin-bottom:4px">Luca Moretti</h3>
      <p style="font-size:12px;color:#8B5CF6;font-weight:500;margin-bottom:6px">Creative Director</p>
      <p style="font-size:12px;color:#9ca3af">Ex Google, ora founder di uno studio creativo a Milano</p>
    </div>
    <div style="text-align:center">
      <div style="width:80px;height:80px;border-radius:50%;background:linear-gradient(135deg,#EC4899,#F59E0B);margin:0 auto 14px;display:flex;align-items:center;justify-content:center;font-size:28px;color:#fff">\u{1F469}\u200D\u{1F4BB}</div>
      <h3 style="font-size:16px;color:#1a1a2e;font-weight:600;margin-bottom:4px">Sara Chen</h3>
      <p style="font-size:12px;color:#EC4899;font-weight:500;margin-bottom:6px">UX Lead</p>
      <p style="font-size:12px;color:#9ca3af">15 anni di esperienza in UX per prodotti globali</p>
    </div>
    <div style="text-align:center">
      <div style="width:80px;height:80px;border-radius:50%;background:linear-gradient(135deg,#8B5CF6,#3B82F6);margin:0 auto 14px;display:flex;align-items:center;justify-content:center;font-size:28px;color:#fff">\u{1F468}\u200D\u{1F680}</div>
      <h3 style="font-size:16px;color:#1a1a2e;font-weight:600;margin-bottom:4px">Marco Bianchi</h3>
      <p style="font-size:12px;color:#3B82F6;font-weight:500;margin-bottom:6px">Tech Innovator</p>
      <p style="font-size:12px;color:#9ca3af">Co-founder di una startup AI con 10M di funding</p>
    </div>
  </div>
</div>`;
      return wrap(body, "#fff", "#1a1a2e", sans);
    },

    "event-minimal": () => {
      const body = `
<div style="min-height:70vh;display:flex;align-items:center;background:#fff;padding:60px 40px">
  <div style="max-width:900px;margin:0 auto;width:100%">
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:60px;align-items:center">
      <div>
        <div style="font-size:11px;letter-spacing:4px;color:#3B82F6;text-transform:uppercase;margin-bottom:20px">Conferenza 2025</div>
        <h1 style="font-size:44px;font-weight:700;color:#1a1a2e;line-height:1.15;margin-bottom:14px">Tech Connect<br>Italia</h1>
        <p style="font-size:15px;color:#6b7280;line-height:1.7;margin-bottom:24px">La conferenza tech pi\u00F9 attesa dell'anno. Innovazione, networking e ispirazione.</p>
        <a style="display:inline-block;padding:12px 28px;background:#3B82F6;color:#fff;border-radius:8px;font-size:14px;font-weight:600">Registrati Ora</a>
      </div>
      <div style="display:grid;grid-template-columns:1fr 1fr;gap:14px">
        <div style="background:#f8fafc;padding:22px 18px;border-radius:10px;border:1px solid #e5e7eb;text-align:center">
          <div style="font-size:11px;color:#9ca3af;text-transform:uppercase;letter-spacing:1px;margin-bottom:6px">Data</div>
          <div style="font-size:18px;font-weight:700;color:#1a1a2e">22 Apr</div>
        </div>
        <div style="background:#f8fafc;padding:22px 18px;border-radius:10px;border:1px solid #e5e7eb;text-align:center">
          <div style="font-size:11px;color:#9ca3af;text-transform:uppercase;letter-spacing:1px;margin-bottom:6px">Location</div>
          <div style="font-size:18px;font-weight:700;color:#1a1a2e">Milano</div>
        </div>
        <div style="background:#f8fafc;padding:22px 18px;border-radius:10px;border:1px solid #e5e7eb;text-align:center">
          <div style="font-size:11px;color:#9ca3af;text-transform:uppercase;letter-spacing:1px;margin-bottom:6px">Speaker</div>
          <div style="font-size:18px;font-weight:700;color:#1a1a2e">30+</div>
        </div>
        <div style="background:#f8fafc;padding:22px 18px;border-radius:10px;border:1px solid #e5e7eb;text-align:center">
          <div style="font-size:11px;color:#9ca3af;text-transform:uppercase;letter-spacing:1px;margin-bottom:6px">Partecipanti</div>
          <div style="font-size:18px;font-weight:700;color:#1a1a2e">500+</div>
        </div>
      </div>
    </div>
  </div>
</div>
<div style="padding:70px 40px;background:#f9fafb">
  <div style="max-width:700px;margin:0 auto">
    <h2 style="font-size:24px;color:#1a1a2e;font-weight:700;margin-bottom:32px;text-align:center">Programma</h2>
    <div style="position:relative;padding-left:36px">
      <div style="position:absolute;left:10px;top:10px;bottom:10px;width:2px;background:#e5e7eb"></div>
      <div style="margin-bottom:28px;position:relative">
        <div style="position:absolute;left:-31px;top:4px;width:12px;height:12px;background:#3B82F6;border-radius:50%"></div>
        <div style="background:#fff;padding:20px;border-radius:10px;border:1px solid #e5e7eb">
          <div style="font-size:12px;color:#3B82F6;font-weight:600;margin-bottom:4px">09:00 - 10:30</div>
          <h3 style="font-size:15px;color:#1a1a2e;font-weight:600;margin-bottom:4px">Keynote: Il Futuro \u00E8 Adesso</h3>
          <p style="font-size:13px;color:#9ca3af">Opening talk con i leader dell'innovazione italiana</p>
        </div>
      </div>
      <div style="margin-bottom:28px;position:relative">
        <div style="position:absolute;left:-31px;top:4px;width:12px;height:12px;background:#3B82F6;border-radius:50%"></div>
        <div style="background:#fff;padding:20px;border-radius:10px;border:1px solid #e5e7eb">
          <div style="font-size:12px;color:#3B82F6;font-weight:600;margin-bottom:4px">11:00 - 12:30</div>
          <h3 style="font-size:15px;color:#1a1a2e;font-weight:600;margin-bottom:4px">Workshop: AI per il Business</h3>
          <p style="font-size:13px;color:#9ca3af">Sessione pratica su come integrare l'AI nei processi aziendali</p>
        </div>
      </div>
      <div style="position:relative">
        <div style="position:absolute;left:-31px;top:4px;width:12px;height:12px;background:#3B82F6;border-radius:50%"></div>
        <div style="background:#fff;padding:20px;border-radius:10px;border:1px solid #e5e7eb">
          <div style="font-size:12px;color:#3B82F6;font-weight:600;margin-bottom:4px">14:00 - 16:00</div>
          <h3 style="font-size:15px;color:#1a1a2e;font-weight:600;margin-bottom:4px">Panel: Startup & Venture Capital</h3>
          <p style="font-size:13px;color:#9ca3af">Tavola rotonda con founder e investitori del panorama italiano</p>
        </div>
      </div>
    </div>
  </div>
</div>`;
      return wrap(body, "#fff", "#1a1a2e", sans);
    },

    "custom-free": () => {
      const body = `
<div style="position:relative;min-height:70vh;display:flex;align-items:center;justify-content:center;background:#0f0f1a;overflow:hidden;padding:60px 40px">
  <div style="position:absolute;top:15%;left:20%;width:350px;height:350px;border-radius:50%;background:radial-gradient(circle,rgba(99,102,241,0.2),transparent 70%);filter:blur(80px)"></div>
  <div style="position:absolute;bottom:15%;right:20%;width:300px;height:300px;border-radius:50%;background:radial-gradient(circle,rgba(139,92,246,0.15),transparent 70%);filter:blur(80px)"></div>
  <div style="text-align:center;position:relative;z-index:1">
    <div style="display:inline-block;padding:5px 14px;background:rgba(99,102,241,0.1);border:1px solid rgba(99,102,241,0.2);border-radius:50px;font-size:12px;color:#818cf8;margin-bottom:24px">Template Personalizzato</div>
    <h1 style="font-size:50px;font-weight:700;line-height:1.15;margin-bottom:16px"><span style="background:linear-gradient(135deg,#6366f1,#8b5cf6,#a78bfa);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text">Il Tuo Design</span><br><span style="color:#f0eef6">Personalizzato</span></h1>
    <p style="font-size:15px;color:#6b6880;max-width:460px;margin:0 auto 28px;line-height:1.7">Crea un sito web unico che rispecchi la tua visione. Nessun limite, totale libert\u00E0 creativa.</p>
    <a style="display:inline-block;padding:13px 28px;background:linear-gradient(135deg,#6366f1,#8b5cf6);color:#fff;border-radius:10px;font-size:14px;font-weight:600">Inizia a Creare</a>
  </div>
</div>
<div style="padding:70px 40px;background:#0f0f1a">
  <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:20px;max-width:900px;margin:0 auto">
    <div style="background:rgba(255,255,255,0.02);border:1px solid rgba(99,102,241,0.15);border-radius:14px;padding:28px 22px">
      <div style="width:36px;height:36px;background:rgba(99,102,241,0.1);border-radius:8px;display:flex;align-items:center;justify-content:center;font-size:18px;margin-bottom:14px">\u{1F3A8}</div>
      <h3 style="font-size:16px;color:#f0eef6;margin-bottom:8px;font-weight:600">Design Libero</h3>
      <p style="font-size:13px;color:#6b6880;line-height:1.6">Scegli colori, font e layout. Ogni elemento \u00E8 personalizzabile al 100%</p>
    </div>
    <div style="background:rgba(255,255,255,0.02);border:1px solid rgba(139,92,246,0.15);border-radius:14px;padding:28px 22px">
      <div style="width:36px;height:36px;background:rgba(139,92,246,0.1);border-radius:8px;display:flex;align-items:center;justify-content:center;font-size:18px;margin-bottom:14px">\u{1F9E9}</div>
      <h3 style="font-size:16px;color:#f0eef6;margin-bottom:8px;font-weight:600">Sezioni Modulari</h3>
      <p style="font-size:13px;color:#6b6880;line-height:1.6">Aggiungi, rimuovi e riordina le sezioni come preferisci</p>
    </div>
    <div style="background:rgba(255,255,255,0.02);border:1px solid rgba(99,102,241,0.15);border-radius:14px;padding:28px 22px">
      <div style="width:36px;height:36px;background:rgba(99,102,241,0.1);border-radius:8px;display:flex;align-items:center;justify-content:center;font-size:18px;margin-bottom:14px">\u{1F680}</div>
      <h3 style="font-size:16px;color:#f0eef6;margin-bottom:8px;font-weight:600">Pronto in Minuti</h3>
      <p style="font-size:13px;color:#6b6880;line-height:1.6">L'AI genera il tuo sito personalizzato in pochi minuti</p>
    </div>
  </div>
</div>`;
      return wrap(body, "#0f0f1a", "#f0eef6", sans);
    },
  };

  const generator = generators[style.id];
  if (generator) {
    return generator();
  }

  // Fallback for unknown style IDs
  const fallbackBody = `
<div style="min-height:70vh;display:flex;align-items:center;justify-content:center;background:${style.secondaryColor || "#1a1a2e"};padding:60px 40px">
  <div style="text-align:center;max-width:600px">
    <div style="font-size:11px;letter-spacing:4px;color:${style.primaryColor || "#6366f1"};text-transform:uppercase;margin-bottom:20px">${categoryLabel}</div>
    <h1 style="font-size:44px;font-weight:700;color:#fff;line-height:1.15;margin-bottom:14px">${style.label}</h1>
    <p style="font-size:15px;color:rgba(255,255,255,0.6);line-height:1.7;margin-bottom:28px">${style.description}</p>
    <a style="display:inline-block;padding:12px 28px;background:${style.primaryColor || "#6366f1"};color:#fff;border-radius:8px;font-size:14px;font-weight:600">Scopri di pi\u00F9</a>
  </div>
</div>
<div style="padding:70px 40px;background:${style.secondaryColor || "#111"}">
  <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:20px;max-width:900px;margin:0 auto">
    <div style="background:rgba(255,255,255,0.05);border:1px solid rgba(255,255,255,0.08);border-radius:12px;padding:28px 22px">
      <h3 style="font-size:16px;color:#fff;margin-bottom:8px;font-weight:600">Sezione 1</h3>
      <p style="font-size:13px;color:rgba(255,255,255,0.5);line-height:1.6">Contenuto di esempio per la prima sezione del template</p>
    </div>
    <div style="background:rgba(255,255,255,0.05);border:1px solid rgba(255,255,255,0.08);border-radius:12px;padding:28px 22px">
      <h3 style="font-size:16px;color:#fff;margin-bottom:8px;font-weight:600">Sezione 2</h3>
      <p style="font-size:13px;color:rgba(255,255,255,0.5);line-height:1.6">Contenuto di esempio per la seconda sezione del template</p>
    </div>
    <div style="background:rgba(255,255,255,0.05);border:1px solid rgba(255,255,255,0.08);border-radius:12px;padding:28px 22px">
      <h3 style="font-size:16px;color:#fff;margin-bottom:8px;font-weight:600">Sezione 3</h3>
      <p style="font-size:13px;color:rgba(255,255,255,0.5);line-height:1.6">Contenuto di esempio per la terza sezione del template</p>
    </div>
  </div>
</div>`;
  return wrap(fallbackBody, style.secondaryColor || "#1a1a2e", "#fff", sans);
}
