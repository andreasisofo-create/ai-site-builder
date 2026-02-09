/**
 * Deploy Site Generation workflow to n8n via REST API.
 *
 * Usage: node deploy-workflow.js
 *
 * Requires: N8N_API_URL, N8N_API_KEY environment variables
 * OR pass them as arguments: node deploy-workflow.js <api_url> <api_key>
 */

const N8N_API_URL = process.argv[2] || process.env.N8N_API_URL || "https://n8n.srv1352958.hstgr.cloud";
const N8N_API_KEY = process.argv[3] || process.env.N8N_API_KEY || "";
const EXISTING_WORKFLOW_ID = process.argv[4] || process.env.N8N_WORKFLOW_ID || "";

if (!N8N_API_KEY) {
  console.error("ERROR: N8N_API_KEY required. Pass as env var or 2nd argument.");
  process.exit(1);
}

// ============ PROMPTS (identical to databinding_generator.py) ============

function buildThemePrompt(businessName, businessDescription, stylePreferences) {
  let styleHint = "";
  if (stylePreferences) {
    if (stylePreferences.primary_color) styleHint += `Primary color requested: ${stylePreferences.primary_color}. `;
    if (stylePreferences.mood) styleHint += `Mood/style: ${stylePreferences.mood}. `;
  }
  return `Generate a color palette and typography for a website. Return ONLY valid JSON, no markdown, no explanation.

BUSINESS: ${businessName} - ${businessDescription.slice(0, 500)}
${styleHint}

Return this exact JSON structure:
{
  "primary_color": "#hex",
  "secondary_color": "#hex",
  "accent_color": "#hex",
  "bg_color": "#hex",
  "bg_alt_color": "#hex",
  "text_color": "#hex",
  "text_muted_color": "#hex",
  "font_heading": "Google Font Name",
  "font_heading_url": "FontName:wght@400;600;700;800",
  "font_body": "Google Font Name",
  "font_body_url": "FontName:wght@400;500;600"
}

Rules:
- Professional, accessible colors (WCAG AA contrast between text and bg)
- bg_color = main page background (light or dark)
- bg_alt_color = alternating section background
- Google Fonts that match the business type
- Return ONLY the JSON object`;
}

function buildTextsPrompt(businessName, businessDescription, sections, contactInfo) {
  let contactStr = "";
  if (contactInfo && Object.keys(contactInfo).length > 0) {
    contactStr = "CONTACT INFO: " + Object.entries(contactInfo).map(([k,v]) => `${k}: ${v}`).join(", ");
  }
  const sectionsStr = sections.join(", ");

  return `Generate Italian text content for a one-page website. Return ONLY valid JSON, no markdown.

BUSINESS: ${businessName}
DESCRIPTION: ${businessDescription.slice(0, 800)}
SECTIONS NEEDED: ${sectionsStr}
${contactStr}

Return this JSON (include only the sections listed above):
{
  "meta": {
    "title": "Page title (max 60 chars)",
    "description": "Meta description (max 155 chars)",
    "og_title": "OG title",
    "og_description": "OG description"
  },
  "hero": {
    "HERO_TITLE": "Headline impattante (max 8 parole)",
    "HERO_SUBTITLE": "Sottotitolo (2-3 frasi)",
    "HERO_CTA_TEXT": "Testo bottone CTA",
    "HERO_CTA_URL": "#contact",
    "HERO_IMAGE_URL": "https://placehold.co/800x600/3b82f6/white?text=${businessName}",
    "HERO_IMAGE_ALT": "Descrizione immagine"
  },
  "about": {
    "ABOUT_TITLE": "Titolo sezione",
    "ABOUT_SUBTITLE": "Sottotitolo",
    "ABOUT_TEXT": "2-4 frasi sulla storia/missione",
    "ABOUT_HIGHLIGHT_1": "Fatto chiave 1",
    "ABOUT_HIGHLIGHT_2": "Fatto chiave 2",
    "ABOUT_HIGHLIGHT_3": "Fatto chiave 3",
    "ABOUT_HIGHLIGHT_NUM_1": "25",
    "ABOUT_HIGHLIGHT_NUM_2": "500",
    "ABOUT_HIGHLIGHT_NUM_3": "98"
  },
  "services": {
    "SERVICES_TITLE": "Titolo sezione",
    "SERVICES_SUBTITLE": "Sottotitolo",
    "SERVICES": [
      {"SERVICE_ICON": "emoji", "SERVICE_TITLE": "Nome servizio", "SERVICE_DESCRIPTION": "Descrizione breve"},
      {"SERVICE_ICON": "emoji", "SERVICE_TITLE": "Nome servizio", "SERVICE_DESCRIPTION": "Descrizione breve"},
      {"SERVICE_ICON": "emoji", "SERVICE_TITLE": "Nome servizio", "SERVICE_DESCRIPTION": "Descrizione breve"}
    ]
  },
  "features": {
    "FEATURES_TITLE": "Titolo sezione",
    "FEATURES_SUBTITLE": "Sottotitolo",
    "FEATURES": [
      {"FEATURE_ICON": "emoji", "FEATURE_TITLE": "Feature", "FEATURE_DESCRIPTION": "Descrizione breve"},
      {"FEATURE_ICON": "emoji", "FEATURE_TITLE": "Feature", "FEATURE_DESCRIPTION": "Descrizione breve"},
      {"FEATURE_ICON": "emoji", "FEATURE_TITLE": "Feature", "FEATURE_DESCRIPTION": "Descrizione breve"},
      {"FEATURE_ICON": "emoji", "FEATURE_TITLE": "Feature", "FEATURE_DESCRIPTION": "Descrizione breve"},
      {"FEATURE_ICON": "emoji", "FEATURE_TITLE": "Feature", "FEATURE_DESCRIPTION": "Descrizione breve"},
      {"FEATURE_ICON": "emoji", "FEATURE_TITLE": "Feature", "FEATURE_DESCRIPTION": "Descrizione breve"}
    ]
  },
  "testimonials": {
    "TESTIMONIALS_TITLE": "Titolo sezione",
    "TESTIMONIALS": [
      {"TESTIMONIAL_TEXT": "Citazione", "TESTIMONIAL_AUTHOR": "Nome", "TESTIMONIAL_ROLE": "Ruolo", "TESTIMONIAL_INITIAL": "N"},
      {"TESTIMONIAL_TEXT": "Citazione", "TESTIMONIAL_AUTHOR": "Nome", "TESTIMONIAL_ROLE": "Ruolo", "TESTIMONIAL_INITIAL": "N"},
      {"TESTIMONIAL_TEXT": "Citazione", "TESTIMONIAL_AUTHOR": "Nome", "TESTIMONIAL_ROLE": "Ruolo", "TESTIMONIAL_INITIAL": "N"}
    ]
  },
  "cta": {
    "CTA_TITLE": "Headline CTA",
    "CTA_SUBTITLE": "Testo supporto",
    "CTA_BUTTON_TEXT": "Testo bottone",
    "CTA_BUTTON_URL": "#contact"
  },
  "contact": {
    "CONTACT_TITLE": "Titolo sezione",
    "CONTACT_SUBTITLE": "Sottotitolo",
    "CONTACT_ADDRESS": "indirizzo o vuoto",
    "CONTACT_PHONE": "telefono o vuoto",
    "CONTACT_EMAIL": "email o vuoto"
  },
  "footer": {
    "FOOTER_DESCRIPTION": "Breve descrizione per footer (1 frase)"
  }
}

IMPORTANT:
- ALL text MUST be in Italian
- Be creative and specific to this business (no generic text)
- Hero title: max 8 words, impactful
- Use relevant emojis for service/feature icons
- TESTIMONIAL_INITIAL = first letter of author name
- Return ONLY the JSON object`;
}

function buildSelectionPrompt(businessDescription, sections, mood) {
  const available = {
    hero: ["hero-split-01", "hero-centered-02", "hero-gradient-03"],
    about: ["about-alternating-01"],
    services: ["services-cards-grid-01", "services-bento-02"],
    features: ["features-icons-grid-01"],
    testimonials: ["testimonials-grid-01"],
    cta: ["cta-banner-01"],
    contact: ["contact-form-01"],
    footer: ["footer-multi-col-01", "footer-minimal-02"],
  };
  const relevant = {};
  for (const s of sections) {
    if (available[s]) relevant[s] = available[s];
  }

  return `Select the best website component variant for each section. Return ONLY valid JSON.

BUSINESS TYPE: ${businessDescription.slice(0, 300)}
STYLE/MOOD: ${mood}
SECTIONS NEEDED: ${sections.join(", ")}

AVAILABLE VARIANTS:
${JSON.stringify(relevant, null, 2)}

Return a JSON object mapping each section to the best variant ID:
{
  "hero": "variant-id",
  "about": "variant-id",
  ...
}

Choose variants whose style matches the business type and mood.
For footer, prefer "footer-multi-col-01" for sites with 4+ sections, "footer-minimal-02" for simpler sites.
Return ONLY the JSON object.`;
}

// ============ WORKFLOW DEFINITION ============

function buildWorkflow() {
  // Node positions for visual layout
  const pos = {
    webhook:    [250, 300],
    setup:      [470, 300],
    progress1:  [690, 300],
    themeCall:  [930, 160],
    textsCall:  [930, 440],
    merge:      [1170, 300],
    parse:      [1390, 300],
    progress2:  [1610, 300],
    selectCall: [1830, 300],
    buildData:  [2050, 300],
    progress3:  [2270, 300],
    callback:   [2490, 300],
  };

  return {
    name: "Site Generation Pipeline",
    nodes: [
      // 1. Webhook Trigger
      {
        parameters: {
          httpMethod: "POST",
          path: "site-generation",
          responseMode: "onReceived",
          responseCode: 200,
          responseData: "allEntries",
          options: {},
        },
        id: "webhook-trigger",
        name: "Webhook",
        type: "n8n-nodes-base.webhook",
        typeVersion: 2,
        position: pos.webhook,
        webhookId: "site-generation",
      },

      // 2. Setup Code - Extract fields and build all prompts
      {
        parameters: {
          jsCode: `
const body = $input.first().json.body;

// Extract and validate
const siteId = body.site_id;
const businessName = body.business_name || "Business";
const businessDescription = body.business_description || "";
const sections = body.sections || ["hero", "about", "services", "contact", "footer"];
const stylePreferences = body.style_preferences || {};
const contactInfo = body.contact_info || {};
const callbackUrl = body.callback_url;
const progressUrl = body.progress_url;
const secret = body.secret;
const apiKey = body.moonshot_api_key;

// Build style hint for theme prompt
let styleHint = "";
if (stylePreferences.primary_color) styleHint += "Primary color requested: " + stylePreferences.primary_color + ". ";
if (stylePreferences.mood) styleHint += "Mood/style: " + stylePreferences.mood + ". ";

// Theme prompt
const themePrompt = "Generate a color palette and typography for a website. Return ONLY valid JSON, no markdown, no explanation.\\n\\nBUSINESS: " + businessName + " - " + businessDescription.slice(0, 500) + "\\n" + styleHint + "\\n\\nReturn this exact JSON structure:\\n{\\n  \\"primary_color\\": \\"#hex\\",\\n  \\"secondary_color\\": \\"#hex\\",\\n  \\"accent_color\\": \\"#hex\\",\\n  \\"bg_color\\": \\"#hex\\",\\n  \\"bg_alt_color\\": \\"#hex\\",\\n  \\"text_color\\": \\"#hex\\",\\n  \\"text_muted_color\\": \\"#hex\\",\\n  \\"font_heading\\": \\"Google Font Name\\",\\n  \\"font_heading_url\\": \\"FontName:wght@400;600;700;800\\",\\n  \\"font_body\\": \\"Google Font Name\\",\\n  \\"font_body_url\\": \\"FontName:wght@400;500;600\\"\\n}\\n\\nRules:\\n- Professional, accessible colors (WCAG AA contrast between text and bg)\\n- bg_color = main page background (light or dark)\\n- bg_alt_color = alternating section background\\n- Google Fonts that match the business type\\n- Return ONLY the JSON object";

// Texts prompt
let contactStr = "";
if (contactInfo && Object.keys(contactInfo).length > 0) {
  contactStr = "CONTACT INFO: " + Object.entries(contactInfo).map(function(e) { return e[0] + ": " + e[1]; }).join(", ");
}
const sectionsStr = sections.join(", ");
const textsPrompt = "Generate Italian text content for a one-page website. Return ONLY valid JSON, no markdown.\\n\\nBUSINESS: " + businessName + "\\nDESCRIPTION: " + businessDescription.slice(0, 800) + "\\nSECTIONS NEEDED: " + sectionsStr + "\\n" + contactStr + "\\n\\nReturn this JSON (include only the sections listed above):\\n{\\n  \\"meta\\": { \\"title\\": \\"Page title (max 60 chars)\\", \\"description\\": \\"Meta description (max 155 chars)\\", \\"og_title\\": \\"OG title\\", \\"og_description\\": \\"OG description\\" },\\n  \\"hero\\": { \\"HERO_TITLE\\": \\"Headline impattante (max 8 parole)\\", \\"HERO_SUBTITLE\\": \\"Sottotitolo (2-3 frasi)\\", \\"HERO_CTA_TEXT\\": \\"Testo bottone CTA\\", \\"HERO_CTA_URL\\": \\"#contact\\", \\"HERO_IMAGE_URL\\": \\"https://placehold.co/800x600/3b82f6/white?text=" + encodeURIComponent(businessName) + "\\", \\"HERO_IMAGE_ALT\\": \\"Descrizione immagine\\" },\\n  \\"about\\": { \\"ABOUT_TITLE\\": \\"Titolo sezione\\", \\"ABOUT_SUBTITLE\\": \\"Sottotitolo\\", \\"ABOUT_TEXT\\": \\"2-4 frasi sulla storia/missione\\", \\"ABOUT_HIGHLIGHT_1\\": \\"Fatto chiave 1\\", \\"ABOUT_HIGHLIGHT_2\\": \\"Fatto chiave 2\\", \\"ABOUT_HIGHLIGHT_3\\": \\"Fatto chiave 3\\", \\"ABOUT_HIGHLIGHT_NUM_1\\": \\"25\\", \\"ABOUT_HIGHLIGHT_NUM_2\\": \\"500\\", \\"ABOUT_HIGHLIGHT_NUM_3\\": \\"98\\" },\\n  \\"services\\": { \\"SERVICES_TITLE\\": \\"Titolo sezione\\", \\"SERVICES_SUBTITLE\\": \\"Sottotitolo\\", \\"SERVICES\\": [ {\\"SERVICE_ICON\\": \\"emoji\\", \\"SERVICE_TITLE\\": \\"Nome servizio\\", \\"SERVICE_DESCRIPTION\\": \\"Descrizione breve\\"}, {\\"SERVICE_ICON\\": \\"emoji\\", \\"SERVICE_TITLE\\": \\"Nome servizio\\", \\"SERVICE_DESCRIPTION\\": \\"Descrizione breve\\"}, {\\"SERVICE_ICON\\": \\"emoji\\", \\"SERVICE_TITLE\\": \\"Nome servizio\\", \\"SERVICE_DESCRIPTION\\": \\"Descrizione breve\\"} ] },\\n  \\"features\\": { \\"FEATURES_TITLE\\": \\"Titolo sezione\\", \\"FEATURES_SUBTITLE\\": \\"Sottotitolo\\", \\"FEATURES\\": [ {\\"FEATURE_ICON\\": \\"emoji\\", \\"FEATURE_TITLE\\": \\"Feature\\", \\"FEATURE_DESCRIPTION\\": \\"Descrizione breve\\"}, {\\"FEATURE_ICON\\": \\"emoji\\", \\"FEATURE_TITLE\\": \\"Feature\\", \\"FEATURE_DESCRIPTION\\": \\"Descrizione breve\\"}, {\\"FEATURE_ICON\\": \\"emoji\\", \\"FEATURE_TITLE\\": \\"Feature\\", \\"FEATURE_DESCRIPTION\\": \\"Descrizione breve\\"}, {\\"FEATURE_ICON\\": \\"emoji\\", \\"FEATURE_TITLE\\": \\"Feature\\", \\"FEATURE_DESCRIPTION\\": \\"Descrizione breve\\"}, {\\"FEATURE_ICON\\": \\"emoji\\", \\"FEATURE_TITLE\\": \\"Feature\\", \\"FEATURE_DESCRIPTION\\": \\"Descrizione breve\\"}, {\\"FEATURE_ICON\\": \\"emoji\\", \\"FEATURE_TITLE\\": \\"Feature\\", \\"FEATURE_DESCRIPTION\\": \\"Descrizione breve\\"} ] },\\n  \\"testimonials\\": { \\"TESTIMONIALS_TITLE\\": \\"Titolo sezione\\", \\"TESTIMONIALS\\": [ {\\"TESTIMONIAL_TEXT\\": \\"Citazione\\", \\"TESTIMONIAL_AUTHOR\\": \\"Nome\\", \\"TESTIMONIAL_ROLE\\": \\"Ruolo\\", \\"TESTIMONIAL_INITIAL\\": \\"N\\"}, {\\"TESTIMONIAL_TEXT\\": \\"Citazione\\", \\"TESTIMONIAL_AUTHOR\\": \\"Nome\\", \\"TESTIMONIAL_ROLE\\": \\"Ruolo\\", \\"TESTIMONIAL_INITIAL\\": \\"N\\"}, {\\"TESTIMONIAL_TEXT\\": \\"Citazione\\", \\"TESTIMONIAL_AUTHOR\\": \\"Nome\\", \\"TESTIMONIAL_ROLE\\": \\"Ruolo\\", \\"TESTIMONIAL_INITIAL\\": \\"N\\"} ] },\\n  \\"cta\\": { \\"CTA_TITLE\\": \\"Headline CTA\\", \\"CTA_SUBTITLE\\": \\"Testo supporto\\", \\"CTA_BUTTON_TEXT\\": \\"Testo bottone\\", \\"CTA_BUTTON_URL\\": \\"#contact\\" },\\n  \\"contact\\": { \\"CONTACT_TITLE\\": \\"Titolo sezione\\", \\"CONTACT_SUBTITLE\\": \\"Sottotitolo\\", \\"CONTACT_ADDRESS\\": \\"indirizzo o vuoto\\", \\"CONTACT_PHONE\\": \\"telefono o vuoto\\", \\"CONTACT_EMAIL\\": \\"email o vuoto\\" },\\n  \\"footer\\": { \\"FOOTER_DESCRIPTION\\": \\"Breve descrizione per footer (1 frase)\\" }\\n}\\n\\nIMPORTANT:\\n- ALL text MUST be in Italian\\n- Be creative and specific to this business (no generic text)\\n- Hero title: max 8 words, impactful\\n- Use relevant emojis for service/feature icons\\n- TESTIMONIAL_INITIAL = first letter of author name\\n- Return ONLY the JSON object";

// Build Kimi request bodies
const themeBody = {
  model: "kimi-k2.5",
  messages: [{ role: "user", content: themePrompt }],
  max_tokens: 500,
  temperature: 0.6,
  thinking: { type: "disabled" }
};

const textsBody = {
  model: "kimi-k2.5",
  messages: [{ role: "user", content: textsPrompt }],
  max_tokens: 2500,
  temperature: 0.6,
  thinking: { type: "disabled" }
};

return [{json: {
  site_id: siteId,
  business_name: businessName,
  business_description: businessDescription,
  sections: sections,
  style_preferences: stylePreferences,
  contact_info: contactInfo,
  callback_url: callbackUrl,
  progress_url: progressUrl,
  secret: secret,
  api_key: apiKey,
  theme_body: themeBody,
  texts_body: textsBody,
  mood: stylePreferences.mood || "modern",
}}];
`,
          mode: "runOnceForAllItems",
        },
        id: "setup-code",
        name: "Setup",
        type: "n8n-nodes-base.code",
        typeVersion: 2,
        position: pos.setup,
      },

      // 3. Progress Step 1
      {
        parameters: {
          method: "POST",
          url: "={{ $json.progress_url }}",
          sendHeaders: true,
          headerParameters: {
            parameters: [
              { name: "Content-Type", value: "application/json" },
            ],
          },
          sendBody: true,
          specifyBody: "json",
          jsonBody: '={{ JSON.stringify({ site_id: $json.site_id, step: 1, message: "Analisi stile e generazione testi...", secret: $json.secret, preview_data: { phase: "analyzing" } }) }}',
          options: { timeout: 10000 },
        },
        id: "progress-1",
        name: "Progress 1",
        type: "n8n-nodes-base.httpRequest",
        typeVersion: 4.2,
        position: pos.progress1,
      },

      // 4. Kimi Theme Call (parallel branch A)
      // NOTE: $json here = Progress 1 HTTP response, NOT Setup output.
      // Must reference Setup node explicitly.
      {
        parameters: {
          method: "POST",
          url: "https://api.moonshot.ai/v1/chat/completions",
          sendHeaders: true,
          headerParameters: {
            parameters: [
              { name: "Authorization", value: "=Bearer {{ $('Setup').first().json.api_key }}" },
              { name: "Content-Type", value: "application/json" },
            ],
          },
          sendBody: true,
          specifyBody: "json",
          jsonBody: "={{ JSON.stringify($('Setup').first().json.theme_body) }}",
          options: { timeout: 60000 },
        },
        id: "theme-call",
        name: "Kimi Theme",
        type: "n8n-nodes-base.httpRequest",
        typeVersion: 4.2,
        position: pos.themeCall,
      },

      // 5. Kimi Texts Call (parallel branch B)
      {
        parameters: {
          method: "POST",
          url: "https://api.moonshot.ai/v1/chat/completions",
          sendHeaders: true,
          headerParameters: {
            parameters: [
              { name: "Authorization", value: "=Bearer {{ $('Setup').first().json.api_key }}" },
              { name: "Content-Type", value: "application/json" },
            ],
          },
          sendBody: true,
          specifyBody: "json",
          jsonBody: "={{ JSON.stringify($('Setup').first().json.texts_body) }}",
          options: { timeout: 90000 },
        },
        id: "texts-call",
        name: "Kimi Texts",
        type: "n8n-nodes-base.httpRequest",
        typeVersion: 4.2,
        position: pos.textsCall,
      },

      // 6. Merge (wait for both theme and texts)
      {
        parameters: {
          mode: "combine",
          combineBy: "combineAll",
          options: {},
        },
        id: "merge-results",
        name: "Merge",
        type: "n8n-nodes-base.merge",
        typeVersion: 3,
        position: pos.merge,
      },

      // 7. Parse Results Code
      {
        parameters: {
          jsCode: `
// Get original data from Setup node
const setupData = $('Setup').first().json;

// Get Kimi responses
const themeResponse = $('Kimi Theme').first().json;
const textsResponse = $('Kimi Texts').first().json;

// Helper: extract JSON from Kimi response
function extractJson(content) {
  // Try code block
  const codeMatch = content.match(/\x60{3}(?:json)?\\s*\\n?([\\s\\S]*?)\\n?\\s*\x60{3}/);
  if (codeMatch) return JSON.parse(codeMatch[1].trim());
  // Try raw JSON
  const start = content.indexOf("{");
  const end = content.lastIndexOf("}");
  if (start !== -1 && end > start) return JSON.parse(content.slice(start, end + 1));
  throw new Error("No JSON found");
}

// Parse theme
let theme;
try {
  const themeContent = themeResponse.choices[0].message.content;
  theme = extractJson(themeContent);
} catch (e) {
  // Fallback theme
  const primaryColor = (setupData.style_preferences && setupData.style_preferences.primary_color) || "#3b82f6";
  theme = {
    primary_color: primaryColor,
    secondary_color: "#1e40af",
    accent_color: "#f59e0b",
    bg_color: "#ffffff",
    bg_alt_color: "#f8fafc",
    text_color: "#0f172a",
    text_muted_color: "#64748b",
    font_heading: "Inter",
    font_heading_url: "Inter:wght@400;600;700;800",
    font_body: "Inter",
    font_body_url: "Inter:wght@400;500;600",
  };
}

// Parse texts
let texts;
let textsOk = true;
try {
  const textsContent = textsResponse.choices[0].message.content;
  texts = extractJson(textsContent);
} catch (e) {
  textsOk = false;
  texts = {};
}

// Build available variants for selection
const available = {
  hero: ["hero-split-01", "hero-centered-02", "hero-gradient-03"],
  about: ["about-alternating-01"],
  services: ["services-cards-grid-01", "services-bento-02"],
  features: ["features-icons-grid-01"],
  testimonials: ["testimonials-grid-01"],
  cta: ["cta-banner-01"],
  contact: ["contact-form-01"],
  footer: ["footer-multi-col-01", "footer-minimal-02"],
};

const sections = setupData.sections;
const relevant = {};
for (const s of sections) {
  if (available[s]) relevant[s] = available[s];
}

// Build selection prompt
const selectionPrompt = "Select the best website component variant for each section. Return ONLY valid JSON.\\n\\nBUSINESS TYPE: " + setupData.business_description.slice(0, 300) + "\\nSTYLE/MOOD: " + setupData.mood + "\\nSECTIONS NEEDED: " + sections.join(", ") + "\\n\\nAVAILABLE VARIANTS:\\n" + JSON.stringify(relevant, null, 2) + "\\n\\nReturn a JSON object mapping each section to the best variant ID:\\n{\\n  \\"hero\\": \\"variant-id\\",\\n  \\"about\\": \\"variant-id\\"\\n}\\n\\nChoose variants whose style matches the business type and mood.\\nFor footer, prefer \\"footer-multi-col-01\\" for sites with 4+ sections, \\"footer-minimal-02\\" for simpler sites.\\nReturn ONLY the JSON object.";

const selectionBody = {
  model: "kimi-k2.5",
  messages: [{ role: "user", content: selectionPrompt }],
  max_tokens: 300,
  temperature: 0.6,
  thinking: { type: "disabled" }
};

// Preview data for Step 2
const progress2Preview = {
  phase: "theme_complete",
  colors: {
    primary: theme.primary_color || "#3b82f6",
    secondary: theme.secondary_color || "#1e40af",
    accent: theme.accent_color || "#f59e0b",
    bg: theme.bg_color || "#ffffff",
    text: theme.text_color || "#0f172a",
  },
  font_heading: theme.font_heading || "Inter",
  font_body: theme.font_body || "Inter",
};

return [{json: {
  ...setupData,
  theme: theme,
  texts: texts,
  texts_ok: textsOk,
  available_variants: available,
  selection_body: selectionBody,
  progress2_preview: progress2Preview,
}}];
`,
          mode: "runOnceForAllItems",
        },
        id: "parse-results",
        name: "Parse Results",
        type: "n8n-nodes-base.code",
        typeVersion: 2,
        position: pos.parse,
      },

      // 8. Progress Step 2
      {
        parameters: {
          method: "POST",
          url: "={{ $json.progress_url }}",
          sendHeaders: true,
          headerParameters: {
            parameters: [
              { name: "Content-Type", value: "application/json" },
            ],
          },
          sendBody: true,
          specifyBody: "json",
          jsonBody: '={{ JSON.stringify({ site_id: $json.site_id, step: 2, message: "Palette e stile identificati", secret: $json.secret, preview_data: $json.progress2_preview }) }}',
          options: { timeout: 10000 },
        },
        id: "progress-2",
        name: "Progress 2",
        type: "n8n-nodes-base.httpRequest",
        typeVersion: 4.2,
        position: pos.progress2,
      },

      // 9. Kimi Selection Call
      // NOTE: $json here = Progress 2 HTTP response. Reference Parse Results.
      {
        parameters: {
          method: "POST",
          url: "https://api.moonshot.ai/v1/chat/completions",
          sendHeaders: true,
          headerParameters: {
            parameters: [
              { name: "Authorization", value: "=Bearer {{ $('Parse Results').first().json.api_key }}" },
              { name: "Content-Type", value: "application/json" },
            ],
          },
          sendBody: true,
          specifyBody: "json",
          jsonBody: "={{ JSON.stringify($('Parse Results').first().json.selection_body) }}",
          options: { timeout: 30000 },
        },
        id: "select-call",
        name: "Kimi Selection",
        type: "n8n-nodes-base.httpRequest",
        typeVersion: 4.2,
        position: pos.selectCall,
      },

      // 10. Build site_data Code
      {
        parameters: {
          jsCode: `
// Get data from Parse Results and Selection response
const parsed = $('Parse Results').first().json;
const selectionResponse = $('Kimi Selection').first().json;

// Helper: extract JSON from Kimi response
function extractJson(content) {
  const codeMatch = content.match(/\x60{3}(?:json)?\\s*\\n?([\\s\\S]*?)\\n?\\s*\x60{3}/);
  if (codeMatch) return JSON.parse(codeMatch[1].trim());
  const start = content.indexOf("{");
  const end = content.lastIndexOf("}");
  if (start !== -1 && end > start) return JSON.parse(content.slice(start, end + 1));
  throw new Error("No JSON found");
}

// Parse selections
let selections;
try {
  const selContent = selectionResponse.choices[0].message.content;
  selections = extractJson(selContent);
} catch (e) {
  // Fallback: first variant of each section
  selections = {};
  const available = parsed.available_variants;
  for (const s of parsed.sections) {
    if (available[s] && available[s].length > 0) {
      selections[s] = available[s][0];
    }
  }
}

// Build components array
const components = [];
for (const section of parsed.sections) {
  const variantId = selections[section];
  if (!variantId) continue;
  const sectionTexts = parsed.texts[section] || {};
  components.push({ variant_id: variantId, data: sectionTexts });
}

// Build complete site_data
const contactInfo = parsed.contact_info || {};
const siteData = {
  theme: parsed.theme,
  meta: parsed.texts.meta || {
    title: parsed.business_name,
    description: "Sito web di " + parsed.business_name,
    og_title: parsed.business_name,
    og_description: "Sito web di " + parsed.business_name,
  },
  components: components,
  global: {
    BUSINESS_NAME: parsed.business_name,
    LOGO_URL: parsed.logo_url || "",
    BUSINESS_PHONE: contactInfo.phone || "",
    BUSINESS_EMAIL: contactInfo.email || "",
    BUSINESS_ADDRESS: contactInfo.address || "",
    CURRENT_YEAR: "2026",
  },
};

// Build preview data for step 3
const heroTexts = parsed.texts.hero || {};
const servicesTexts = parsed.texts.services || {};
const progress3Preview = {
  phase: "content_complete",
  sections: parsed.sections,
  hero_title: heroTexts.HERO_TITLE || "",
  hero_subtitle: heroTexts.HERO_SUBTITLE || "",
  hero_cta: heroTexts.HERO_CTA_TEXT || "",
  services_titles: Array.isArray(servicesTexts.SERVICES)
    ? servicesTexts.SERVICES.map(function(s) { return s.SERVICE_TITLE || ""; })
    : [],
};

return [{json: {
  site_id: parsed.site_id,
  callback_url: parsed.callback_url,
  progress_url: parsed.progress_url,
  secret: parsed.secret,
  site_data: siteData,
  progress3_preview: progress3Preview,
}}];
`,
          mode: "runOnceForAllItems",
        },
        id: "build-sitedata",
        name: "Build SiteData",
        type: "n8n-nodes-base.code",
        typeVersion: 2,
        position: pos.buildData,
      },

      // 11. Progress Step 3
      {
        parameters: {
          method: "POST",
          url: "={{ $json.progress_url }}",
          sendHeaders: true,
          headerParameters: {
            parameters: [
              { name: "Content-Type", value: "application/json" },
            ],
          },
          sendBody: true,
          specifyBody: "json",
          jsonBody: '={{ JSON.stringify({ site_id: $json.site_id, step: 3, message: "Contenuti e layout pronti", secret: $json.secret, preview_data: $json.progress3_preview }) }}',
          options: { timeout: 10000 },
        },
        id: "progress-3",
        name: "Progress 3",
        type: "n8n-nodes-base.httpRequest",
        typeVersion: 4.2,
        position: pos.progress3,
      },

      // 12. Callback to Backend
      // NOTE: $json here = Progress 3 HTTP response. Reference Build SiteData.
      {
        parameters: {
          method: "POST",
          url: "={{ $('Build SiteData').first().json.callback_url }}",
          sendHeaders: true,
          headerParameters: {
            parameters: [
              { name: "Content-Type", value: "application/json" },
            ],
          },
          sendBody: true,
          specifyBody: "json",
          jsonBody: '={{ JSON.stringify({ site_id: $("Build SiteData").first().json.site_id, site_data: $("Build SiteData").first().json.site_data, secret: $("Build SiteData").first().json.secret }) }}',
          options: { timeout: 30000 },
        },
        id: "callback",
        name: "Callback",
        type: "n8n-nodes-base.httpRequest",
        typeVersion: 4.2,
        position: pos.callback,
      },
    ],

    connections: {
      "Webhook": {
        main: [[{ node: "Setup", type: "main", index: 0 }]],
      },
      "Setup": {
        main: [[{ node: "Progress 1", type: "main", index: 0 }]],
      },
      "Progress 1": {
        main: [[
          { node: "Kimi Theme", type: "main", index: 0 },
          { node: "Kimi Texts", type: "main", index: 0 },
        ]],
      },
      "Kimi Theme": {
        main: [[{ node: "Merge", type: "main", index: 0 }]],
      },
      "Kimi Texts": {
        main: [[{ node: "Merge", type: "main", index: 1 }]],
      },
      "Merge": {
        main: [[{ node: "Parse Results", type: "main", index: 0 }]],
      },
      "Parse Results": {
        main: [[{ node: "Progress 2", type: "main", index: 0 }]],
      },
      "Progress 2": {
        main: [[{ node: "Kimi Selection", type: "main", index: 0 }]],
      },
      "Kimi Selection": {
        main: [[{ node: "Build SiteData", type: "main", index: 0 }]],
      },
      "Build SiteData": {
        main: [[{ node: "Progress 3", type: "main", index: 0 }]],
      },
      "Progress 3": {
        main: [[{ node: "Callback", type: "main", index: 0 }]],
      },
    },

    settings: {
      executionOrder: "v1",
    },
  };
}

// ============ DEPLOY ============

async function deploy() {
  const workflow = buildWorkflow();

  console.log("Deploying workflow to n8n...");
  console.log("URL:", N8N_API_URL);
  console.log("Nodes:", workflow.nodes.length);

  try {
    let workflowId;

    if (EXISTING_WORKFLOW_ID) {
      // Update existing workflow
      console.log("Updating existing workflow:", EXISTING_WORKFLOW_ID);
      const updateRes = await fetch(`${N8N_API_URL}/api/v1/workflows/${EXISTING_WORKFLOW_ID}`, {
        method: "PUT",
        headers: {
          "X-N8N-API-KEY": N8N_API_KEY,
          "Content-Type": "application/json",
        },
        body: JSON.stringify(workflow),
      });

      if (!updateRes.ok) {
        const errText = await updateRes.text();
        console.error("Update failed:", updateRes.status, errText);
        process.exit(1);
      }

      const updated = await updateRes.json();
      workflowId = updated.id;
      console.log("Workflow updated! ID:", workflowId);
    } else {
      // Create new workflow
      const createRes = await fetch(`${N8N_API_URL}/api/v1/workflows`, {
        method: "POST",
        headers: {
          "X-N8N-API-KEY": N8N_API_KEY,
          "Content-Type": "application/json",
        },
        body: JSON.stringify(workflow),
      });

      if (!createRes.ok) {
        const errText = await createRes.text();
        console.error("Create failed:", createRes.status, errText);
        process.exit(1);
      }

      const created = await createRes.json();
      workflowId = created.id;
      console.log("Workflow created! ID:", workflowId);
    }

    // Activate workflow
    const activateRes = await fetch(`${N8N_API_URL}/api/v1/workflows/${workflowId}/activate`, {
      method: "POST",
      headers: {
        "X-N8N-API-KEY": N8N_API_KEY,
        "Content-Type": "application/json",
      },
    });

    if (activateRes.ok) {
      console.log("Workflow activated!");
    } else {
      console.log("Activation response:", activateRes.status, await activateRes.text());
      console.log("You may need to activate manually in n8n UI.");
    }

    console.log("\n=== DEPLOYMENT COMPLETE ===");
    console.log("Webhook URL:", `${N8N_API_URL}/webhook/site-generation`);
    console.log("Workflow ID:", workflowId);
    console.log("\nSet these env vars on Render:");
    console.log(`GENERATION_PIPELINE=n8n`);
    console.log(`N8N_WEBHOOK_URL=${N8N_API_URL}/webhook/site-generation`);
    console.log(`N8N_CALLBACK_SECRET=<generate-a-uuid>`);

  } catch (err) {
    console.error("Deploy error:", err);
    process.exit(1);
  }
}

deploy();
