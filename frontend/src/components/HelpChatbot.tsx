"use client";

import { useState, useRef, useEffect, FormEvent, useCallback } from "react";
import { chatMessage } from "@/lib/api";
import { useLanguage } from "@/lib/i18n";

// ============ TYPES ============

interface Message {
  id: number;
  text: string;
  sender: "bot" | "user";
  timestamp: Date;
  type?: "text" | "contact-form" | "contact-success" | "quick-actions";
}

interface ContactFormData {
  nome: string;
  contatto: string;
  messaggio: string;
}

// ============ KNOWLEDGE BASE ============

interface KnowledgeTopic {
  id: string;
  keywords: { it: string[][]; en: string[][] };
  answer: { it: string; en: string };
  followUp?: string[];
}

const KNOWLEDGE_BASE: KnowledgeTopic[] = [
  {
    id: "creare-sito",
    keywords: {
      it: [
        ["creare", "sito"],
        ["crea", "sito"],
        ["creo", "sito"],
        ["nuovo", "sito"],
        ["costruire", "sito"],
        ["fare", "sito"],
        ["come", "creare"],
        ["come", "faccio"],
        ["voglio", "creare"],
        ["iniziare"],
        ["primo", "sito"],
        ["generare"],
        ["genera"],
      ],
      en: [
        ["create", "site"],
        ["create", "website"],
        ["new", "site"],
        ["new", "website"],
        ["build", "site"],
        ["build", "website"],
        ["make", "site"],
        ["how", "create"],
        ["how", "do"],
        ["want", "create"],
        ["get", "started"],
        ["first", "site"],
        ["generate"],
      ],
    },
    answer: {
      it:
        "Per creare un sito con E-quipe:\n\n" +
        "1. Dalla dashboard, scegli un template tra le 8 categorie (19 stili disponibili)\n" +
        "2. Inserisci i dati della tua attivita: nome, descrizione, colori, logo\n" +
        "3. L'AI genera il tuo sito in circa 60 secondi con animazioni GSAP professionali\n" +
        "4. Puoi poi modificarlo con la chat AI nell'editor",
      en:
        "To create a site with E-quipe:\n\n" +
        "1. From the dashboard, choose a template from 8 categories (19 styles available)\n" +
        "2. Enter your business info: name, description, colors, logo\n" +
        "3. AI generates your site in about 60 seconds with professional GSAP animations\n" +
        "4. You can then edit it with the AI chat in the editor",
    },
    followUp: ["modificare-sito", "template", "pubblicare"],
  },
  {
    id: "modificare-sito",
    keywords: {
      it: [
        ["modificare", "sito"],
        ["modifica", "sito"],
        ["modifico"],
        ["cambiare"],
        ["cambio"],
        ["editare"],
        ["editor"],
        ["personalizzare"],
        ["aggiungere", "sezione"],
        ["cambiare", "colori"],
        ["cambiare", "testi"],
        ["aggiungere", "foto"],
        ["aggiungere", "immagini"],
        ["aggiungere", "video"],
        ["inserire", "video"],
        ["youtube"],
        ["embed"],
        ["codice", "embed"],
      ],
      en: [
        ["edit", "site"],
        ["edit", "website"],
        ["modify"],
        ["change"],
        ["customize"],
        ["editor"],
        ["personalize"],
        ["add", "section"],
        ["change", "colors"],
        ["change", "text"],
        ["add", "photo"],
        ["add", "images"],
        ["add", "video"],
        ["insert", "video"],
        ["youtube"],
        ["embed"],
        ["embed", "code"],
      ],
    },
    answer: {
      it:
        "Per modificare il tuo sito:\n\n" +
        "1. Apri l'editor cliccando \"Modifica\" sul tuo sito nella dashboard\n" +
        "2. Usa la chat AI a destra per descrivere le modifiche\n" +
        "3. Puoi chiedere di cambiare colori, testi, layout, sezioni\n" +
        "4. Puoi aggiungere foto (incolla URL o carica dal dispositivo)\n" +
        "5. Puoi aggiungere video YouTube (incolla il link)\n" +
        "6. Puoi inserire codice embed da qualsiasi provider\n\n" +
        "Le modifiche vengono applicate in tempo reale nell'anteprima.",
      en:
        "To edit your site:\n\n" +
        "1. Open the editor by clicking \"Edit\" on your site in the dashboard\n" +
        "2. Use the AI chat on the right to describe your changes\n" +
        "3. You can ask to change colors, text, layout, sections\n" +
        "4. You can add photos (paste URL or upload from device)\n" +
        "5. You can add YouTube videos (paste the link)\n" +
        "6. You can insert embed code from any provider\n\n" +
        "Changes are applied in real-time in the preview.",
    },
    followUp: ["pubblicare", "piani-prezzi"],
  },
  {
    id: "pubblicare",
    keywords: {
      it: [
        ["pubblicare"],
        ["pubblica"],
        ["pubblico"],
        ["online"],
        ["deploy"],
        ["mettere", "online"],
        ["andare", "online"],
        ["live"],
        ["dominio"],
        ["url"],
        ["link"],
        ["indirizzo"],
        ["visibile"],
        ["vercel"],
      ],
      en: [
        ["publish"],
        ["deploy"],
        ["go", "online"],
        ["put", "online"],
        ["go", "live"],
        ["live"],
        ["domain"],
        ["url"],
        ["link"],
        ["address"],
        ["visible"],
        ["vercel"],
      ],
    },
    answer: {
      it:
        "Per pubblicare il tuo sito:\n\n" +
        "1. Apri l'editor del tuo sito\n" +
        "2. Clicca il pulsante \"Pubblica\" in alto a destra\n" +
        "3. Il sito viene pubblicato su tuosito.e-quipe.app\n\n" +
        "NOTA: La pubblicazione richiede il piano Sito Web (EUR 200) o superiore. Il piano Starter gratuito permette solo l'anteprima.",
      en:
        "To publish your site:\n\n" +
        "1. Open your site's editor\n" +
        "2. Click the \"Publish\" button at the top right\n" +
        "3. The site is published at yoursite.e-quipe.app\n\n" +
        "NOTE: Publishing requires the Website plan (EUR 200) or higher. The free Starter plan only allows preview.",
    },
    followUp: ["piani-prezzi", "dominio"],
  },
  {
    id: "piani-prezzi",
    keywords: {
      it: [
        ["piano", "piani"],
        ["prezzo", "prezzi"],
        ["costo", "costi"],
        ["quanto", "costa"],
        ["abbonamento"],
        ["pagamento"],
        ["gratuito", "gratis"],
        ["free"],
        ["starter"],
        ["base"],
        ["premium"],
        ["upgrade"],
        ["pagare"],
        ["comprare"],
        ["acquistare"],
        ["ads"],
        ["pubblicita"],
      ],
      en: [
        ["plan", "plans"],
        ["price", "pricing"],
        ["cost"],
        ["how", "much"],
        ["subscription"],
        ["payment"],
        ["free"],
        ["starter"],
        ["base"],
        ["premium"],
        ["upgrade"],
        ["pay"],
        ["buy"],
        ["purchase"],
        ["ads"],
        ["advertising"],
      ],
    },
    answer: {
      it:
        "I piani E-quipe (pagamento unico, NO abbonamento):\n\n" +
        "STARTER (Gratuito)\n" +
        "- 1 generazione AI, 3 modifiche chat, solo anteprima\n\n" +
        "SITO WEB (EUR 200)\n" +
        "- 3 generazioni AI, 20 modifiche chat\n" +
        "- Pubblicazione su sottodominio e-quipe.app\n\n" +
        "PREMIUM (EUR 500)\n" +
        "- 5 generazioni AI, modifiche illimitate\n" +
        "- Dominio personalizzato incluso\n\n" +
        "SITO + ADS (EUR 700)\n" +
        "- Tutto Premium + gestione campagne Meta Ads e Google Ads\n" +
        "- Gestite dagli esperti di E-quipe",
      en:
        "E-quipe plans (one-time payment, NO subscription):\n\n" +
        "STARTER (Free)\n" +
        "- 1 AI generation, 3 chat edits, preview only\n\n" +
        "WEBSITE (EUR 200)\n" +
        "- 3 AI generations, 20 chat edits\n" +
        "- Publishing on e-quipe.app subdomain\n\n" +
        "PREMIUM (EUR 500)\n" +
        "- 5 AI generations, unlimited edits\n" +
        "- Custom domain included\n\n" +
        "SITE + ADS (EUR 700)\n" +
        "- Everything in Premium + Meta Ads and Google Ads campaign management\n" +
        "- Managed by E-quipe experts",
    },
    followUp: ["creare-sito", "upgrade"],
  },
  {
    id: "template",
    keywords: {
      it: [
        ["template"],
        ["modello", "modelli"],
        ["temi", "tema"],
        ["categorie"],
        ["ristorante"],
        ["portfolio"],
        ["business"],
        ["stile", "stili"],
        ["saas"],
        ["blog"],
        ["evento"],
        ["ecommerce"],
      ],
      en: [
        ["template"],
        ["model"],
        ["theme", "themes"],
        ["categories"],
        ["restaurant"],
        ["portfolio"],
        ["business"],
        ["style", "styles"],
        ["saas"],
        ["blog"],
        ["event"],
        ["ecommerce"],
      ],
    },
    answer: {
      it:
        "Template disponibili in E-quipe:\n\n" +
        "8 categorie, 19 stili professionali:\n" +
        "- Ristorante: 3 stili (Elegante, Accogliente, Moderno)\n" +
        "- SaaS: 3 stili (Gradient, Clean, Dark)\n" +
        "- Portfolio: 3 stili (Galleria, Minimal, Creativo)\n" +
        "- E-commerce: 2 stili (Modern, Luxury)\n" +
        "- Business: 3 stili (Corporate, Trust, Fresh)\n" +
        "- Blog: 2 stili (Editorial, Dark)\n" +
        "- Eventi: 2 stili (Vibrant, Minimal)\n" +
        "- Custom: 1 stile (l'AI crea da zero)",
      en:
        "Templates available in E-quipe:\n\n" +
        "8 categories, 19 professional styles:\n" +
        "- Restaurant: 3 styles (Elegant, Cozy, Modern)\n" +
        "- SaaS: 3 styles (Gradient, Clean, Dark)\n" +
        "- Portfolio: 3 styles (Gallery, Minimal, Creative)\n" +
        "- E-commerce: 2 styles (Modern, Luxury)\n" +
        "- Business: 3 styles (Corporate, Trust, Fresh)\n" +
        "- Blog: 2 styles (Editorial, Dark)\n" +
        "- Events: 2 styles (Vibrant, Minimal)\n" +
        "- Custom: 1 style (AI creates from scratch)",
    },
    followUp: ["creare-sito", "piani-prezzi"],
  },
  {
    id: "ads",
    keywords: {
      it: [
        ["ads"],
        ["pubblicita"],
        ["campagne"],
        ["meta", "ads"],
        ["google", "ads"],
        ["facebook"],
        ["instagram"],
        ["advertising"],
        ["sponsorizzate"],
      ],
      en: [
        ["ads"],
        ["advertising"],
        ["campaigns"],
        ["meta", "ads"],
        ["google", "ads"],
        ["facebook"],
        ["instagram"],
        ["sponsored"],
      ],
    },
    answer: {
      it:
        "E-quipe offre gestione campagne pubblicitarie:\n\n" +
        "- Campagne Meta Ads (Facebook/Instagram) e Google Ads\n" +
        "- Gestite dagli esperti di E-quipe (team umano dedicato)\n" +
        "- Setup completo, monitoraggio e ottimizzazione continua\n" +
        "- Report mensili dettagliati\n\n" +
        "Incluso nel piano Sito + Ads (EUR 700) oppure contatta il supporto per maggiori info.",
      en:
        "E-quipe offers advertising campaign management:\n\n" +
        "- Meta Ads (Facebook/Instagram) and Google Ads campaigns\n" +
        "- Managed by E-quipe experts (dedicated human team)\n" +
        "- Complete setup, monitoring and continuous optimization\n" +
        "- Detailed monthly reports\n\n" +
        "Included in the Site + Ads plan (EUR 700) or contact support for more info.",
    },
    followUp: ["piani-prezzi", "contatto"],
  },
  {
    id: "problema-generazione",
    keywords: {
      it: [
        ["non", "genera"],
        ["non", "funziona"],
        ["errore", "generazione"],
        ["bloccato"],
        ["non", "carica"],
        ["problema", "generazione"],
        ["sito", "non", "genera"],
      ],
      en: [
        ["not", "generating"],
        ["not", "working"],
        ["generation", "error"],
        ["stuck"],
        ["not", "loading"],
        ["generation", "problem"],
        ["site", "not", "generating"],
      ],
    },
    answer: {
      it:
        "Se il sito non si genera:\n\n" +
        "1. Verifica la connessione internet e riprova\n" +
        "2. Se il problema persiste, potrebbe essere un sovraccarico temporaneo dei server\n" +
        "3. Attendi qualche minuto e riprova\n" +
        "4. Assicurati di aver inserito il nome del business e la descrizione\n\n" +
        "Se il problema continua, contatta il supporto tramite il pulsante qui sotto.",
      en:
        "If the site is not generating:\n\n" +
        "1. Check your internet connection and try again\n" +
        "2. If the problem persists, it may be a temporary server overload\n" +
        "3. Wait a few minutes and try again\n" +
        "4. Make sure you entered the business name and description\n\n" +
        "If the problem continues, contact support using the button below.",
    },
    followUp: ["contatto"],
  },
  {
    id: "problema-pubblicazione",
    keywords: {
      it: [
        ["non", "riesco", "pubblicare"],
        ["non", "pubblica"],
        ["errore", "pubblicazione"],
        ["pubblicazione", "fallita"],
      ],
      en: [
        ["can't", "publish"],
        ["cannot", "publish"],
        ["publish", "error"],
        ["publish", "failed"],
        ["publishing", "failed"],
      ],
    },
    answer: {
      it:
        "Se non riesci a pubblicare il sito:\n\n" +
        "- Verifica di avere un piano Sito Web (EUR 200) o superiore\n" +
        "- Il piano Starter gratuito NON include la pubblicazione\n" +
        "- Per fare l'upgrade, dalla dashboard clicca su uno dei pulsanti di upgrade\n\n" +
        "Se hai gia un piano a pagamento e il problema persiste, contatta il supporto.",
      en:
        "If you can't publish the site:\n\n" +
        "- Make sure you have the Website plan (EUR 200) or higher\n" +
        "- The free Starter plan does NOT include publishing\n" +
        "- To upgrade, click one of the upgrade buttons in the dashboard\n\n" +
        "If you already have a paid plan and the problem persists, contact support.",
    },
    followUp: ["piani-prezzi", "contatto"],
  },
  {
    id: "problema-modifiche",
    keywords: {
      it: [
        ["modifiche", "non", "vedono"],
        ["non", "vedo", "modifiche"],
        ["non", "salva"],
        ["non", "aggiorna"],
        ["modifiche", "perse"],
      ],
      en: [
        ["changes", "not", "showing"],
        ["can't", "see", "changes"],
        ["not", "saving"],
        ["not", "updating"],
        ["changes", "lost"],
      ],
    },
    answer: {
      it:
        "Se le modifiche non si vedono:\n\n" +
        "1. Ricarica la pagina dell'editor (F5 o Ctrl+R)\n" +
        "2. Le modifiche vengono salvate automaticamente\n" +
        "3. Verifica di non aver esaurito le modifiche AI del tuo piano\n" +
        "4. Controlla la connessione internet\n\n" +
        "Se il problema persiste, contatta il supporto.",
      en:
        "If changes are not showing:\n\n" +
        "1. Reload the editor page (F5 or Ctrl+R)\n" +
        "2. Changes are saved automatically\n" +
        "3. Check that you haven't used up your plan's AI edits\n" +
        "4. Check your internet connection\n\n" +
        "If the problem persists, contact support.",
    },
    followUp: ["contatto", "piani-prezzi"],
  },
  {
    id: "problema-template",
    keywords: {
      it: [
        ["non", "vedo", "template"],
        ["template", "bloccati"],
        ["template", "non", "disponibili"],
        ["sbloccare", "template"],
      ],
      en: [
        ["can't", "see", "templates"],
        ["templates", "locked"],
        ["templates", "not", "available"],
        ["unlock", "templates"],
      ],
    },
    answer: {
      it:
        "I template sono disponibili solo con piano Creazione Sito (EUR 200) o Premium (EUR 500).\n\n" +
        "Con il piano Starter gratuito puoi usare solo la modalita \"Personalizzato\", dove l'AI crea il sito da zero basandosi sulla tua descrizione.\n\n" +
        "Per sbloccare i template, fai l'upgrade dalla dashboard.",
      en:
        "Templates are only available with the Website plan (EUR 200) or Premium (EUR 500).\n\n" +
        "With the free Starter plan you can only use the \"Custom\" mode, where AI creates the site from scratch based on your description.\n\n" +
        "To unlock templates, upgrade from the dashboard.",
    },
    followUp: ["piani-prezzi", "template"],
  },
  {
    id: "problema-login",
    keywords: {
      it: [
        ["errore", "login"],
        ["non", "riesco", "accedere"],
        ["non", "entra"],
        ["password", "sbagliata"],
        ["accesso", "negato"],
        ["login", "fallito"],
        ["registrazione"],
        ["registrare"],
      ],
      en: [
        ["login", "error"],
        ["can't", "log", "in"],
        ["can't", "sign", "in"],
        ["wrong", "password"],
        ["access", "denied"],
        ["login", "failed"],
        ["registration"],
        ["register"],
        ["sign", "up"],
      ],
    },
    answer: {
      it:
        "Se hai problemi di accesso:\n\n" +
        "1. Verifica che email e password siano corretti\n" +
        "2. Se hai usato Google per registrarti, usa il pulsante \"Accedi con Google\"\n" +
        "3. Controlla di aver verificato l'email (link nella mail di registrazione)\n" +
        "4. Se hai dimenticato la password, prova il recupero password\n\n" +
        "Se il problema persiste, contatta il supporto.",
      en:
        "If you have login issues:\n\n" +
        "1. Verify that email and password are correct\n" +
        "2. If you registered with Google, use the \"Sign in with Google\" button\n" +
        "3. Check that you verified your email (link in the registration email)\n" +
        "4. If you forgot your password, try password recovery\n\n" +
        "If the problem persists, contact support.",
    },
    followUp: ["contatto"],
  },
  {
    id: "upgrade",
    keywords: {
      it: [
        ["cambio", "piano"],
        ["cambiare", "piano"],
        ["upgrade"],
        ["passare", "premium"],
        ["passare", "base"],
        ["migliorare", "piano"],
      ],
      en: [
        ["change", "plan"],
        ["upgrade"],
        ["switch", "plan"],
        ["go", "premium"],
        ["improve", "plan"],
      ],
    },
    answer: {
      it:
        "Per cambiare piano:\n\n" +
        "1. Vai alla dashboard\n" +
        "2. Nella sezione upgrade, scegli il piano desiderato\n" +
        "3. Verrai reindirizzato al pagamento sicuro\n" +
        "4. Dopo il pagamento, il piano si attiva immediatamente\n\n" +
        "Il pagamento e una tantum, non e un abbonamento mensile.",
      en:
        "To change your plan:\n\n" +
        "1. Go to the dashboard\n" +
        "2. In the upgrade section, choose your desired plan\n" +
        "3. You'll be redirected to secure payment\n" +
        "4. After payment, the plan activates immediately\n\n" +
        "Payment is one-time, not a monthly subscription.",
    },
    followUp: ["piani-prezzi"],
  },
  {
    id: "rimborso",
    keywords: {
      it: [
        ["rimborso"],
        ["rimborsare"],
        ["soldi", "indietro"],
        ["annullare", "pagamento"],
        ["disdetta"],
      ],
      en: [
        ["refund"],
        ["money", "back"],
        ["cancel", "payment"],
        ["cancellation"],
      ],
    },
    answer: {
      it:
        "Per richiedere un rimborso o informazioni sui pagamenti, contatta il supporto direttamente.\n\n" +
        "Usa il pulsante \"Contatta il supporto\" qui sotto per inviarci i tuoi dati e ti risponderemo il prima possibile.",
      en:
        "To request a refund or payment information, contact support directly.\n\n" +
        "Use the \"Contact support\" button below to send us your details and we'll get back to you as soon as possible.",
    },
    followUp: ["contatto"],
  },
  {
    id: "dominio",
    keywords: {
      it: [
        ["dominio", "personalizzato"],
        ["dominio", "custom"],
        ["mio", "dominio"],
        ["collegare", "dominio"],
        ["dns"],
        ["sottodominio"],
      ],
      en: [
        ["custom", "domain"],
        ["my", "domain"],
        ["connect", "domain"],
        ["dns"],
        ["subdomain"],
      ],
    },
    answer: {
      it:
        "Informazioni sul dominio:\n\n" +
        "- Piano Sito Web: il sito viene pubblicato su un sottodominio (tuosito.e-quipe.app)\n" +
        "- Piano Premium: dominio personalizzato incluso (es. tuosito.it)\n" +
        "- Il certificato SSL e incluso in tutti i piani a pagamento\n" +
        "- L'hosting e illimitato\n\n" +
        "Per collegare un dominio personalizzato, serve il piano Premium (EUR 500).",
      en:
        "Domain information:\n\n" +
        "- Website plan: site is published on a subdomain (yoursite.e-quipe.app)\n" +
        "- Premium plan: custom domain included (e.g. yoursite.com)\n" +
        "- SSL certificate is included in all paid plans\n" +
        "- Hosting is unlimited\n\n" +
        "To connect a custom domain, the Premium plan (EUR 500) is required.",
    },
    followUp: ["piani-prezzi", "pubblicare"],
  },
  {
    id: "servizi-professionali",
    keywords: {
      it: [
        ["servizi", "professionali"],
        ["e-quipe", "studio"],
        ["sito", "complesso"],
        ["e-commerce"],
        ["funzionalita", "avanzate"],
        ["design", "su", "misura"],
        ["integrazioni"],
        ["professionale"],
        ["agenzia"],
      ],
      en: [
        ["professional", "services"],
        ["e-quipe", "studio"],
        ["complex", "site"],
        ["e-commerce"],
        ["advanced", "features"],
        ["custom", "design"],
        ["integrations"],
        ["professional"],
        ["agency"],
      ],
    },
    answer: {
      it:
        "Per siti piu complessi e personalizzati, E-quipe offre servizi professionali:\n\n" +
        "- Design su misura\n" +
        "- Funzionalita avanzate\n" +
        "- E-commerce\n" +
        "- Integrazioni custom\n" +
        "- Gestione campagne Ads (Meta + Google)\n\n" +
        "Contatta il supporto tramite il pulsante qui sotto per maggiori informazioni.",
      en:
        "For more complex and customized sites, E-quipe offers professional services:\n\n" +
        "- Custom design\n" +
        "- Advanced features\n" +
        "- E-commerce\n" +
        "- Custom integrations\n" +
        "- Ads campaign management (Meta + Google)\n\n" +
        "Contact support using the button below for more information.",
    },
    followUp: ["contatto"],
  },
  {
    id: "contatto",
    keywords: {
      it: [
        ["contatto", "contatti"],
        ["supporto"],
        ["aiuto"],
        ["help"],
        ["assistenza"],
        ["email"],
        ["parlare", "persona"],
        ["operatore"],
        ["umano"],
        ["contattare"],
        ["scrivere"],
        ["chiamare"],
      ],
      en: [
        ["contact"],
        ["support"],
        ["help"],
        ["assistance"],
        ["email"],
        ["talk", "person"],
        ["operator"],
        ["human"],
        ["reach", "out"],
        ["write"],
        ["call"],
      ],
    },
    answer: { it: "__SHOW_CONTACT_FORM__", en: "__SHOW_CONTACT_FORM__" },
    followUp: [],
  },
];

// ============ QUICK ACTIONS ============

const QUICK_ACTIONS = {
  it: [
    { label: "Come creare un sito", topicId: "creare-sito" },
    { label: "Piani e prezzi", topicId: "piani-prezzi" },
    { label: "Problemi tecnici", topicId: "problemi-tecnici" },
    { label: "Contatta il supporto", topicId: "contatto" },
  ],
  en: [
    { label: "How to create a site", topicId: "creare-sito" },
    { label: "Plans and pricing", topicId: "piani-prezzi" },
    { label: "Technical issues", topicId: "problemi-tecnici" },
    { label: "Contact support", topicId: "contatto" },
  ],
};

const PROBLEMS_QUICK_ACTIONS = {
  it: [
    { label: "Il sito non si genera", topicId: "problema-generazione" },
    { label: "Non riesco a pubblicare", topicId: "problema-pubblicazione" },
    { label: "Le modifiche non si vedono", topicId: "problema-modifiche" },
    { label: "Non vedo i template", topicId: "problema-template" },
    { label: "Errore di login", topicId: "problema-login" },
    { label: "Indietro", topicId: "__back__" },
  ],
  en: [
    { label: "Site not generating", topicId: "problema-generazione" },
    { label: "Can't publish", topicId: "problema-pubblicazione" },
    { label: "Changes not showing", topicId: "problema-modifiche" },
    { label: "Can't see templates", topicId: "problema-template" },
    { label: "Login error", topicId: "problema-login" },
    { label: "Back", topicId: "__back__" },
  ],
};

// ============ I18N STRINGS ============

const UI_STRINGS = {
  it: {
    welcomeMessage:
      "Ciao! Sono l'assistente AI di E-quipe. Posso aiutarti con qualsiasi domanda sui nostri servizi di creazione siti web e gestione campagne Ads. Come posso aiutarti?",
    defaultAnswer:
      "Non sono sicuro di aver capito la tua domanda. Prova a usare i pulsanti qui sotto oppure riformula la domanda.\n\nPosso aiutarti con: creazione siti, modifiche, pubblicazione, piani e prezzi, gestione Ads e contatto supporto.",
    contactPrompt:
      "Certo! Per metterti in contatto con il nostro team, compila i campi qui sotto e invieremo la tua richiesta.",
    contactPromptShort:
      "Certo! Per metterti in contatto con il nostro team, compila i campi qui sotto.",
    contactSuccess: "Grazie! La tua richiesta e stata inviata a e-quipe Studio.",
    contactSuccessReply: "\nTi risponderemo il prima possibile!",
    contactName: "Nome",
    contactNamePlaceholder: "Il tuo nome",
    contactEmailLabel: "Email o Cellulare",
    contactEmailPlaceholder: "email@esempio.it o +39...",
    contactMessageLabel: "Messaggio (opzionale)",
    contactMessagePlaceholder: "Descrivi la tua richiesta...",
    contactSubmit: "Invia richiesta",
    contactNameField: "Nome",
    contactContactField: "Contatto",
    contactMessageField: "Messaggio",
    contactNotSpecified: "Non specificato",
    headerTitle: "Assistente E-quipe",
    headerSubtitle: "AI - Sempre disponibile",
    openLabel: "Apri assistenza",
    closeLabel: "Chiudi",
    inputPlaceholder: "Scrivi un messaggio...",
    emailSubject: "Richiesta assistenza - E-quipe",
    noMessage: "Nessun messaggio aggiuntivo",
  },
  en: {
    welcomeMessage:
      "Hi! I'm the E-quipe AI assistant. I can help you with any questions about our website creation and Ads campaign management services. How can I help you?",
    defaultAnswer:
      "I'm not sure I understood your question. Try using the buttons below or rephrase your question.\n\nI can help with: site creation, edits, publishing, plans and pricing, Ads management and support contact.",
    contactPrompt:
      "Sure! To get in touch with our team, fill in the fields below and we'll send your request.",
    contactPromptShort:
      "Sure! To get in touch with our team, fill in the fields below.",
    contactSuccess: "Thanks! Your request has been sent to e-quipe Studio.",
    contactSuccessReply: "\nWe'll get back to you as soon as possible!",
    contactName: "Name",
    contactNamePlaceholder: "Your name",
    contactEmailLabel: "Email or Phone",
    contactEmailPlaceholder: "email@example.com or +1...",
    contactMessageLabel: "Message (optional)",
    contactMessagePlaceholder: "Describe your request...",
    contactSubmit: "Send request",
    contactNameField: "Name",
    contactContactField: "Contact",
    contactMessageField: "Message",
    contactNotSpecified: "Not specified",
    headerTitle: "E-quipe Assistant",
    headerSubtitle: "AI - Always available",
    openLabel: "Open support",
    closeLabel: "Close",
    inputPlaceholder: "Type a message...",
    emailSubject: "Support request - E-quipe",
    noMessage: "No additional message",
  },
};

// ============ SMART MATCHING ============

function normalizeText(text: string): string {
  return text
    .toLowerCase()
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .replace(/[^a-z0-9\s]/g, " ")
    .replace(/\s+/g, " ")
    .trim();
}

function findBestMatch(input: string, lastTopicId: string | null, lang: "it" | "en"): KnowledgeTopic | null {
  const normalized = normalizeText(input);
  const words = normalized.split(" ");

  let bestMatch: KnowledgeTopic | null = null;
  let bestScore = 0;

  for (const topic of KNOWLEDGE_BASE) {
    let topicScore = 0;
    const keywords = topic.keywords[lang];

    for (const keywordSet of keywords) {
      let allMatch = true;
      let matchCount = 0;

      for (const keyword of keywordSet) {
        const normalizedKeyword = normalizeText(keyword);
        const found = words.some(
          (word) =>
            word === normalizedKeyword ||
            word.startsWith(normalizedKeyword) ||
            normalizedKeyword.startsWith(word)
        );
        if (found) {
          matchCount++;
        } else {
          allMatch = false;
        }
      }

      if (allMatch && keywordSet.length > 0) {
        const setScore = keywordSet.length * 3 + matchCount;
        topicScore = Math.max(topicScore, setScore);
      } else if (matchCount > 0) {
        const partialScore = matchCount;
        topicScore = Math.max(topicScore, partialScore);
      }
    }

    // Context bonus: if this topic is a follow-up of the last topic
    if (lastTopicId) {
      const lastTopic = KNOWLEDGE_BASE.find((t) => t.id === lastTopicId);
      if (lastTopic?.followUp?.includes(topic.id)) {
        topicScore += 1;
      }
    }

    if (topicScore > bestScore) {
      bestScore = topicScore;
      bestMatch = topic;
    }
  }

  if (bestScore < 1) return null;

  return bestMatch;
}

// ============ HELPERS ============

function formatTime(date: Date, lang: "it" | "en"): string {
  return date.toLocaleTimeString(lang === "en" ? "en-US" : "it-IT", { hour: "2-digit", minute: "2-digit" });
}

function sendContactEmail(data: ContactFormData, lang: "it" | "en") {
  const strings = UI_STRINGS[lang];
  const subject = encodeURIComponent(strings.emailSubject);
  const body = encodeURIComponent(
    `${strings.contactNameField}: ${data.nome}\n${strings.contactContactField}: ${data.contatto}\n${strings.contactMessageField}: ${data.messaggio || strings.noMessage}`
  );
  window.open(
    `mailto:andrea.sisofo@e-quipe.it?subject=${subject}&body=${body}`,
    "_blank"
  );
}

// ============ COMPONENT ============

export default function HelpChatbot() {
  const { language } = useLanguage();
  const lang = language as "it" | "en";
  const strings = UI_STRINGS[lang];

  const [open, setOpen] = useState(false);
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [isTyping, setIsTyping] = useState(false);
  const [lastTopicId, setLastTopicId] = useState<string | null>(null);
  const [showProblems, setShowProblems] = useState(false);
  const [contactForm, setContactForm] = useState<ContactFormData>({
    nome: "",
    contatto: "",
    messaggio: "",
  });
  const [contactFormVisible, setContactFormVisible] = useState(false);

  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  const nextId = useRef(1);
  const initialized = useRef(false);

  // Welcome message on first open
  useEffect(() => {
    if (open && !initialized.current) {
      initialized.current = true;
      setMessages([
        {
          id: nextId.current++,
          text: strings.welcomeMessage,
          sender: "bot",
          timestamp: new Date(),
        },
      ]);
    }
    if (open) {
      setTimeout(() => inputRef.current?.focus(), 200);
    }
  }, [open, strings.welcomeMessage]);

  // Scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isTyping, contactFormVisible]);

  const addBotMessage = useCallback(
    (text: string, type?: Message["type"]) => {
      setMessages((prev) => [
        ...prev,
        {
          id: nextId.current++,
          text,
          sender: "bot",
          timestamp: new Date(),
          type: type || "text",
        },
      ]);
    },
    []
  );

  const handleTopicResponse = useCallback(
    (topicId: string) => {
      if (topicId === "__back__") {
        setShowProblems(false);
        return;
      }
      if (topicId === "problemi-tecnici") {
        setShowProblems(true);
        return;
      }

      const topic = KNOWLEDGE_BASE.find((t) => t.id === topicId);
      if (!topic) return;

      setShowProblems(false);
      setLastTopicId(topicId);

      const answer = topic.answer[lang];

      if (answer === "__SHOW_CONTACT_FORM__") {
        setIsTyping(true);
        setTimeout(() => {
          setIsTyping(false);
          addBotMessage(strings.contactPrompt);
          setContactFormVisible(true);
        }, 300);
      } else {
        setIsTyping(true);
        setTimeout(() => {
          setIsTyping(false);
          addBotMessage(answer);
        }, 300);
      }
    },
    [addBotMessage, lang, strings.contactPrompt]
  );

  const handleSubmit = useCallback(
    async (e: FormEvent) => {
      e.preventDefault();
      const text = input.trim();
      if (!text || isTyping) return;

      // Add user message
      setMessages((prev) => [
        ...prev,
        {
          id: nextId.current++,
          text,
          sender: "user",
          timestamp: new Date(),
        },
      ]);
      setInput("");
      setContactFormVisible(false);
      setShowProblems(false);

      // Check for contact keywords locally first (instant)
      const contactMatch = findBestMatch(text, lastTopicId, lang);
      if (contactMatch?.answer[lang] === "__SHOW_CONTACT_FORM__") {
        setLastTopicId(contactMatch.id);
        setIsTyping(true);
        setTimeout(() => {
          setIsTyping(false);
          addBotMessage(strings.contactPromptShort);
          setContactFormVisible(true);
        }, 300);
        return;
      }

      setIsTyping(true);

      // Try AI first, fallback to local matching
      try {
        const history = messages
          .filter((m) => m.sender === "user" || m.sender === "bot")
          .slice(-10)
          .map((m) => ({
            role: m.sender === "user" ? "user" : "assistant",
            content: m.text,
          }));

        const result = await chatMessage(text, history, lang);

        setIsTyping(false);

        if (result.reply && !result.error) {
          addBotMessage(result.reply);
        } else {
          // Fallback to local matching
          const match = findBestMatch(text, lastTopicId, lang);
          if (match) {
            setLastTopicId(match.id);
            addBotMessage(match.answer[lang]);
          } else {
            addBotMessage(strings.defaultAnswer);
          }
        }
      } catch {
        // API failed - fallback to local matching
        setIsTyping(false);
        const match = findBestMatch(text, lastTopicId, lang);
        if (match) {
          setLastTopicId(match.id);
          addBotMessage(match.answer[lang]);
        } else {
          addBotMessage(strings.defaultAnswer);
        }
      }
    },
    [input, isTyping, lastTopicId, messages, addBotMessage, lang, strings]
  );

  const handleContactSubmit = useCallback(
    (e: FormEvent) => {
      e.preventDefault();
      if (!contactForm.contatto.trim()) return;

      sendContactEmail(contactForm, lang);

      setContactFormVisible(false);
      addBotMessage(
        strings.contactSuccess + "\n\n" +
          strings.contactNameField + ": " + (contactForm.nome || strings.contactNotSpecified) + "\n" +
          strings.contactContactField + ": " + contactForm.contatto + "\n" +
          (contactForm.messaggio ? strings.contactMessageField + ": " + contactForm.messaggio + "\n" : "") +
          strings.contactSuccessReply,
        "contact-success"
      );

      setContactForm({ nome: "", contatto: "", messaggio: "" });
    },
    [contactForm, addBotMessage, lang, strings]
  );

  const handleQuickAction = useCallback(
    (topicId: string) => {
      const quickActions = QUICK_ACTIONS[lang];
      const problemActions = PROBLEMS_QUICK_ACTIONS[lang];
      const action = [...quickActions, ...problemActions].find(
        (a) => a.topicId === topicId
      );
      if (action && topicId !== "__back__" && topicId !== "problemi-tecnici") {
        setMessages((prev) => [
          ...prev,
          {
            id: nextId.current++,
            text: action.label,
            sender: "user",
            timestamp: new Date(),
          },
        ]);
      }
      setContactFormVisible(false);
      handleTopicResponse(topicId);
    },
    [handleTopicResponse, lang]
  );

  const quickActions = QUICK_ACTIONS[lang];
  const problemActions = PROBLEMS_QUICK_ACTIONS[lang];

  return (
    <>
      {/* Floating toggle button */}
      <button
        onClick={() => setOpen((v) => !v)}
        aria-label={strings.openLabel}
        className="fixed bottom-6 right-6 z-[9999] flex h-14 w-14 items-center justify-center rounded-full bg-blue-600 text-white shadow-lg shadow-blue-600/30 transition-transform hover:scale-105 hover:bg-blue-500 active:scale-95"
      >
        {open ? (
          <svg
            xmlns="http://www.w3.org/2000/svg"
            className="h-6 w-6"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
            strokeWidth={2}
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              d="M6 18L18 6M6 6l12 12"
            />
          </svg>
        ) : (
          <svg
            xmlns="http://www.w3.org/2000/svg"
            className="h-6 w-6"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
            strokeWidth={2}
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"
            />
          </svg>
        )}
      </button>

      {/* Chat window */}
      <div
        className={`fixed bottom-24 right-6 z-[9999] flex flex-col overflow-hidden rounded-2xl border border-white/10 bg-[#111] shadow-2xl transition-all duration-300 ${
          open
            ? "pointer-events-auto translate-y-0 opacity-100"
            : "pointer-events-none translate-y-4 opacity-0"
        }`}
        style={{ width: 380, height: 520 }}
      >
        {/* Header */}
        <div className="flex items-center justify-between border-b border-white/10 bg-gradient-to-r from-blue-600/20 to-violet-600/20 px-4 py-3">
          <div className="flex items-center gap-2.5">
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-gradient-to-br from-blue-500 to-violet-600">
              <svg
                xmlns="http://www.w3.org/2000/svg"
                className="h-4 w-4 text-white"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
                strokeWidth={2}
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  d="M9.813 15.904L9 18.75l-.813-2.846a4.5 4.5 0 00-3.09-3.09L2.25 12l2.846-.813a4.5 4.5 0 003.09-3.09L9 5.25l.813 2.846a4.5 4.5 0 003.09 3.09L15.75 12l-2.846.813a4.5 4.5 0 00-3.09 3.09zM18.259 8.715L18 9.75l-.259-1.035a3.375 3.375 0 00-2.455-2.456L14.25 6l1.036-.259a3.375 3.375 0 002.455-2.456L18 2.25l.259 1.035a3.375 3.375 0 002.455 2.456L21.75 6l-1.036.259a3.375 3.375 0 00-2.455 2.456z"
                />
              </svg>
            </div>
            <div>
              <h3 className="text-sm font-semibold text-white">
                {strings.headerTitle}
              </h3>
              <p className="text-[10px] text-slate-400">{strings.headerSubtitle}</p>
            </div>
          </div>
          <button
            onClick={() => setOpen(false)}
            aria-label={strings.closeLabel}
            className="rounded p-1 text-slate-400 transition-colors hover:bg-white/10 hover:text-white"
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              className="h-4 w-4"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
              strokeWidth={2}
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                d="M6 18L18 6M6 6l12 12"
              />
            </svg>
          </button>
        </div>

        {/* Messages */}
        <div className="flex-1 space-y-3 overflow-y-auto px-4 py-3 scrollbar-thin scrollbar-thumb-white/10 scrollbar-track-transparent">
          {messages.map((msg) => (
            <div key={msg.id}>
              <div
                className={`flex ${
                  msg.sender === "user" ? "justify-end" : "justify-start"
                }`}
              >
                <div
                  className={`max-w-[85%] whitespace-pre-line rounded-xl px-3 py-2 text-sm leading-relaxed ${
                    msg.sender === "bot"
                      ? msg.type === "contact-success"
                        ? "border border-emerald-500/20 bg-emerald-500/10 text-slate-200"
                        : "border border-blue-500/20 bg-blue-500/10 text-slate-200"
                      : "bg-white/10 text-white"
                  }`}
                >
                  {msg.text}
                </div>
              </div>
              <p
                className={`mt-0.5 text-[10px] text-slate-600 ${
                  msg.sender === "user" ? "text-right" : "text-left"
                }`}
              >
                {formatTime(msg.timestamp, lang)}
              </p>
            </div>
          ))}

          {/* Typing indicator */}
          {isTyping && (
            <div className="flex justify-start">
              <div className="flex items-center gap-1.5 rounded-xl border border-blue-500/20 bg-blue-500/10 px-4 py-2.5">
                <span
                  className="inline-block h-1.5 w-1.5 animate-bounce rounded-full bg-blue-400"
                  style={{ animationDelay: "0ms" }}
                />
                <span
                  className="inline-block h-1.5 w-1.5 animate-bounce rounded-full bg-blue-400"
                  style={{ animationDelay: "150ms" }}
                />
                <span
                  className="inline-block h-1.5 w-1.5 animate-bounce rounded-full bg-blue-400"
                  style={{ animationDelay: "300ms" }}
                />
              </div>
            </div>
          )}

          {/* Contact form inline */}
          {contactFormVisible && !isTyping && (
            <div className="rounded-xl border border-blue-500/20 bg-blue-500/5 p-3">
              <form onSubmit={handleContactSubmit} className="space-y-2.5">
                <div>
                  <label className="mb-1 block text-xs text-slate-400">
                    {strings.contactName}
                  </label>
                  <input
                    type="text"
                    value={contactForm.nome}
                    onChange={(e) =>
                      setContactForm((prev) => ({
                        ...prev,
                        nome: e.target.value,
                      }))
                    }
                    placeholder={strings.contactNamePlaceholder}
                    className="w-full rounded-lg border border-white/10 bg-white/5 px-3 py-1.5 text-xs text-white placeholder-slate-500 outline-none transition-colors focus:border-blue-500/50"
                  />
                </div>
                <div>
                  <label className="mb-1 block text-xs text-slate-400">
                    {strings.contactEmailLabel} <span className="text-red-400">*</span>
                  </label>
                  <input
                    type="text"
                    value={contactForm.contatto}
                    onChange={(e) =>
                      setContactForm((prev) => ({
                        ...prev,
                        contatto: e.target.value,
                      }))
                    }
                    placeholder={strings.contactEmailPlaceholder}
                    required
                    className="w-full rounded-lg border border-white/10 bg-white/5 px-3 py-1.5 text-xs text-white placeholder-slate-500 outline-none transition-colors focus:border-blue-500/50"
                  />
                </div>
                <div>
                  <label className="mb-1 block text-xs text-slate-400">
                    {strings.contactMessageLabel}
                  </label>
                  <textarea
                    value={contactForm.messaggio}
                    onChange={(e) =>
                      setContactForm((prev) => ({
                        ...prev,
                        messaggio: e.target.value,
                      }))
                    }
                    placeholder={strings.contactMessagePlaceholder}
                    rows={2}
                    className="w-full resize-none rounded-lg border border-white/10 bg-white/5 px-3 py-1.5 text-xs text-white placeholder-slate-500 outline-none transition-colors focus:border-blue-500/50"
                  />
                </div>
                <button
                  type="submit"
                  disabled={!contactForm.contatto.trim()}
                  className="w-full rounded-lg bg-blue-600 py-2 text-xs font-semibold text-white transition-colors hover:bg-blue-500 disabled:opacity-40 disabled:hover:bg-blue-600"
                >
                  {strings.contactSubmit}
                </button>
              </form>
            </div>
          )}

          {/* Quick action buttons */}
          {!isTyping && !contactFormVisible && messages.length > 0 && (
            <div className="flex flex-wrap gap-1.5 pt-1">
              {(showProblems ? problemActions : quickActions).map(
                (action) => (
                  <button
                    key={action.topicId}
                    onClick={() => handleQuickAction(action.topicId)}
                    className="rounded-full border border-white/10 bg-white/5 px-3 py-1 text-[11px] text-slate-300 transition-colors hover:border-blue-500/30 hover:bg-blue-500/10 hover:text-white"
                  >
                    {action.label}
                  </button>
                )
              )}
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Input */}
        <form
          onSubmit={handleSubmit}
          className="flex items-center gap-2 border-t border-white/10 px-3 py-3"
        >
          <input
            ref={inputRef}
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder={strings.inputPlaceholder}
            disabled={isTyping}
            className="flex-1 rounded-lg border border-white/10 bg-white/5 px-3 py-2 text-sm text-white placeholder-slate-500 outline-none transition-colors focus:border-blue-500/50 focus:bg-white/10 disabled:opacity-50"
          />
          <button
            type="submit"
            disabled={!input.trim() || isTyping}
            className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-blue-600 text-white transition-colors hover:bg-blue-500 disabled:opacity-40 disabled:hover:bg-blue-600"
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              className="h-4 w-4"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
              strokeWidth={2}
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                d="M5 12h14M12 5l7 7-7 7"
              />
            </svg>
          </button>
        </form>
      </div>
    </>
  );
}
