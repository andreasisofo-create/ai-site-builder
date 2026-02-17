"""Seed del catalogo servizi con pacchetti e servizi a la carte.

Prezzi allineati con la landing page (Pricing.tsx + ServicesList.tsx).
Viene eseguito all'avvio se la tabella service_catalog e' vuota.
"""

import json
import logging
from app.core.database import SessionLocal
from app.models.service import ServiceCatalog

logger = logging.getLogger(__name__)

# ============ CATALOGO SERVIZI ============

SERVICES = [
    # ---- PACCHETTI ----
    {
        "slug": "pack-presenza",
        "name": "Pack Presenza",
        "name_en": "Presence Pack",
        "category": "pack",
        "setup_price_cents": 49900,   # €499
        "monthly_price_cents": 3900,  # €39/mese
        "description": "Il tuo biglietto da visita digitale. Sito AI completo con hosting e dominio.",
        "description_en": "Your digital business card. Complete AI website with hosting and domain.",
        "features_json": json.dumps([
            "Homepage AI completa",
            "3 pagine extra incluse (4 totali)",
            "Dominio personalizzato (1° anno)",
            "Hosting + SSL + Backup",
            "Modifiche illimitate via chat",
        ]),
        "features_en_json": json.dumps([
            "Complete AI Homepage",
            "3 extra pages included (4 total)",
            "Custom domain (1st year)",
            "Hosting + SSL + Backup",
            "Unlimited chat edits",
        ]),
        "included_services_json": json.dumps([
            "homepage-ai", "domain-year", "hosting-maintenance",
        ]),
        "is_highlighted": False,
        "display_order": 1,
        "generations_limit": 3,
        "refines_limit": 20,
        "pages_limit": 4,
    },
    {
        "slug": "pack-clienti",
        "name": "Pack Clienti",
        "name_en": "Clients Pack",
        "category": "pack",
        "setup_price_cents": 49900,   # €499
        "monthly_price_cents": 19900, # €199/mese
        "description": "Sito web + primi clienti con Meta Ads e contenuti AI.",
        "description_en": "Website + first clients with Meta Ads and AI content.",
        "features_json": json.dumps([
            "Tutto del Pack Presenza",
            "Meta Ads (Instagram & Facebook)",
            "Contenuti Base (8 post AI/mese)",
            "Report mensile performance",
            "Supporto via chat",
        ]),
        "features_en_json": json.dumps([
            "Everything in Presence Pack",
            "Meta Ads (Instagram & Facebook)",
            "Base Content (8 AI posts/month)",
            "Monthly performance report",
            "Chat support",
        ]),
        "included_services_json": json.dumps([
            "homepage-ai", "domain-year", "hosting-maintenance",
            "meta-ads-base", "content-base",
        ]),
        "is_highlighted": False,
        "display_order": 2,
        "generations_limit": 3,
        "refines_limit": 20,
        "pages_limit": 4,
    },
    {
        "slug": "pack-crescita",
        "name": "Pack Crescita",
        "name_en": "Growth Pack",
        "category": "pack",
        "setup_price_cents": 49900,    # €499 (SETUP GRATUITO badge)
        "monthly_price_cents": 39900,  # €399/mese
        "description": "Crescita completa: sito custom, ads su tutti i canali, contenuti illimitati.",
        "description_en": "Complete growth: custom site, ads on all channels, unlimited content.",
        "features_json": json.dumps([
            "Sito Web Custom completo (8 pagine)",
            "Dominio personalizzato incluso",
            "Full Ads: Meta Pro + Google Ads",
            "DM automatici ai lead",
            "Contenuti Pro (illimitati)",
            "Report settimanale dettagliato",
            "Manutenzione inclusa",
            "Supporto prioritario",
        ]),
        "features_en_json": json.dumps([
            "Complete Custom Website (8 pages)",
            "Custom domain included",
            "Full Ads: Meta Pro + Google Ads",
            "Automatic DMs to leads",
            "Pro Content (unlimited)",
            "Detailed weekly report",
            "Maintenance included",
            "Priority support",
        ]),
        "included_services_json": json.dumps([
            "custom-site-8", "domain-year", "hosting-maintenance",
            "full-ads", "content-pro",
        ]),
        "is_highlighted": True,  # "CONSIGLIATO"
        "display_order": 3,
        "generations_limit": 5,
        "refines_limit": 30,
        "pages_limit": 8,
    },
    {
        "slug": "pack-premium",
        "name": "Pack Premium",
        "name_en": "Premium Pack",
        "category": "pack",
        "setup_price_cents": 149900,   # €1.499
        "monthly_price_cents": 99900,  # €999/mese
        "description": "Il pacchetto completo per chi vuole dominare il mercato digitale.",
        "description_en": "The complete package for those who want to dominate the digital market.",
        "features_json": json.dumps([
            "Tutto del Pack Crescita",
            "Pagine sito illimitate",
            "Campagne illimitate su tutti i canali",
            "Account manager dedicato",
            "Strategia marketing mensile",
            "Report personalizzato e call mensile",
            "Supporto 24/7 dedicato",
        ]),
        "features_en_json": json.dumps([
            "Everything in Growth Pack",
            "Unlimited website pages",
            "Unlimited campaigns on all channels",
            "Dedicated account manager",
            "Monthly marketing strategy",
            "Custom report and monthly call",
            "Dedicated 24/7 support",
        ]),
        "included_services_json": json.dumps([
            "custom-site-8", "domain-year", "hosting-maintenance",
            "full-ads", "content-pro",
        ]),
        "is_highlighted": False,
        "display_order": 4,
        "generations_limit": 10,
        "refines_limit": 9999,
        "pages_limit": 9999,
    },

    # ---- SERVIZI A LA CARTE: SITO WEB ----
    {
        "slug": "homepage-ai",
        "name": "Homepage AI",
        "name_en": "AI Homepage",
        "category": "site",
        "setup_price_cents": 29900,  # €299 una tantum
        "monthly_price_cents": 0,
        "description": "Homepage professionale generata dall'AI con animazioni GSAP.",
        "description_en": "Professional AI-generated homepage with GSAP animations.",
        "features_json": json.dumps(["1 pagina AI completa", "Animazioni GSAP", "Responsive"]),
        "display_order": 10,
        "generations_limit": 1,
        "refines_limit": 5,
        "pages_limit": 1,
    },
    {
        "slug": "custom-site-8",
        "name": "Sito Web Custom (8 pag)",
        "name_en": "Custom Website (8 pages)",
        "category": "site",
        "setup_price_cents": 99900,  # €999 una tantum
        "monthly_price_cents": 0,
        "description": "Sito web completo fino a 8 pagine, design personalizzato.",
        "description_en": "Complete website up to 8 pages, custom design.",
        "features_json": json.dumps(["Fino a 8 pagine", "Design personalizzato", "SEO ottimizzato"]),
        "display_order": 11,
        "generations_limit": 3,
        "refines_limit": 20,
        "pages_limit": 8,
    },
    {
        "slug": "extra-page",
        "name": "Pagina Extra",
        "name_en": "Extra Page",
        "category": "site",
        "setup_price_cents": 10000,  # €100 cad.
        "monthly_price_cents": 0,
        "description": "Pagina aggiuntiva per il tuo sito.",
        "description_en": "Additional page for your website.",
        "display_order": 12,
    },
    {
        "slug": "domain-year",
        "name": "Dominio .it/.com",
        "name_en": "Domain .it/.com",
        "category": "domain",
        "setup_price_cents": 5900,  # €59/anno
        "monthly_price_cents": 0,
        "yearly_price_cents": 5900,
        "description": "Registrazione dominio personalizzato per 1 anno.",
        "description_en": "Custom domain registration for 1 year.",
        "display_order": 13,
    },
    {
        "slug": "hosting-maintenance",
        "name": "Manutenzione & Hosting",
        "name_en": "Maintenance & Hosting",
        "category": "hosting",
        "setup_price_cents": 0,
        "monthly_price_cents": 3900,  # €39/mese
        "description": "Hosting veloce, SSL, backup automatici, aggiornamenti.",
        "description_en": "Fast hosting, SSL, automatic backups, updates.",
        "display_order": 14,
    },

    # ---- SERVIZI A LA CARTE: ADS ----
    {
        "slug": "meta-ads-base",
        "name": "Meta Ads",
        "name_en": "Meta Ads",
        "category": "ads",
        "setup_price_cents": 0,
        "monthly_price_cents": 14900,  # €149/mese
        "description": "Gestione campagne Instagram & Facebook Ads.",
        "description_en": "Instagram & Facebook Ads campaign management.",
        "features_json": json.dumps(["Instagram Ads", "Facebook Ads", "Report mensile"]),
        "display_order": 20,
    },
    {
        "slug": "meta-ads-pro",
        "name": "Meta Ads Pro",
        "name_en": "Meta Ads Pro",
        "category": "ads",
        "setup_price_cents": 0,
        "monthly_price_cents": 24900,  # €249/mese
        "description": "Gestione avanzata Meta Ads con ottimizzazione AI continua.",
        "description_en": "Advanced Meta Ads management with continuous AI optimization.",
        "features_json": json.dumps(["Instagram & Facebook Ads Pro", "Ottimizzazione AI", "A/B testing", "Report settimanale"]),
        "display_order": 21,
    },
    {
        "slug": "google-ads",
        "name": "Google Ads",
        "name_en": "Google Ads",
        "category": "ads",
        "setup_price_cents": 0,
        "monthly_price_cents": 19900,  # €199/mese
        "description": "Gestione campagne Google Search & Display.",
        "description_en": "Google Search & Display campaign management.",
        "features_json": json.dumps(["Google Search Ads", "Display Ads", "Keyword research", "Report mensile"]),
        "display_order": 22,
    },
    {
        "slug": "full-ads",
        "name": "Full Ads (Meta + Google)",
        "name_en": "Full Ads (Meta + Google)",
        "category": "ads",
        "setup_price_cents": 0,
        "monthly_price_cents": 34900,  # €349/mese
        "description": "Gestione completa su tutti i canali: Meta Pro + Google Ads.",
        "description_en": "Complete management on all channels: Meta Pro + Google Ads.",
        "features_json": json.dumps(["Meta Ads Pro", "Google Ads", "Cross-channel optimization", "Report settimanale"]),
        "display_order": 23,
    },

    # ---- SERVIZI A LA CARTE: CONTENUTI ----
    {
        "slug": "content-base",
        "name": "Contenuti Base (8/mese)",
        "name_en": "Base Content (8/month)",
        "category": "content",
        "setup_price_cents": 0,
        "monthly_price_cents": 7900,  # €79/mese
        "description": "8 post social AI al mese con grafiche e copy.",
        "description_en": "8 AI social posts per month with graphics and copy.",
        "display_order": 30,
    },
    {
        "slug": "content-pro",
        "name": "Contenuti Pro (Illimitati)",
        "name_en": "Pro Content (Unlimited)",
        "category": "content",
        "setup_price_cents": 0,
        "monthly_price_cents": 14900,  # €149/mese
        "description": "Contenuti social illimitati con AI, video, grafiche e copy.",
        "description_en": "Unlimited AI social content with video, graphics and copy.",
        "display_order": 31,
    },
]


def seed_service_catalog():
    """Popola il catalogo servizi se vuoto. Idempotente."""
    db = SessionLocal()
    try:
        existing = db.query(ServiceCatalog).count()
        if existing > 0:
            logger.info(f"Catalogo servizi gia' popolato ({existing} servizi)")
            return existing

        for svc_data in SERVICES:
            svc = ServiceCatalog(**svc_data)
            db.add(svc)

        db.commit()
        count = db.query(ServiceCatalog).count()
        logger.info(f"Catalogo servizi seedato: {count} servizi")
        return count

    except Exception as e:
        db.rollback()
        logger.error(f"Errore seed catalogo servizi: {e}")
        raise
    finally:
        db.close()
