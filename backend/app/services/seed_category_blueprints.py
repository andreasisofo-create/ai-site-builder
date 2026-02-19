"""Seed 10 category blueprints for the v2.0 component diversity system.

Executed at startup if the category_blueprints table is empty. Idempotent.
"""

import logging

from app.core.database import SessionLocal
from app.models.category_blueprint import CategoryBlueprint

logger = logging.getLogger(__name__)

BLUEPRINTS = [
    {
        "category_slug": "ristorante",
        "category_name": "Ristorante",
        "sections_required": ["hero", "menu", "about", "gallery", "contact", "footer"],
        "sections_optional": ["booking", "testimonials", "team", "faq", "cta"],
        "sections_forbidden": ["pricing", "cases"],
        "default_variant_cluster": "V1",
        "mood_required": ["warm", "food"],
        "mood_forbidden": ["tech", "corporate"],
        "style_names": ["restaurant-elegant", "restaurant-cozy", "restaurant-modern"],
    },
    {
        "category_slug": "studio_professionale",
        "category_name": "Studio Professionale",
        "sections_required": ["hero", "services", "about", "contact", "footer"],
        "sections_optional": ["team", "cases", "testimonials", "faq", "stats", "cta"],
        "sections_forbidden": ["menu", "gallery_food"],
        "default_variant_cluster": "V2",
        "mood_required": ["professional", "trust"],
        "mood_forbidden": ["playful", "food"],
        "style_names": ["business-corporate", "business-trust", "business-fresh"],
    },
    {
        "category_slug": "portfolio",
        "category_name": "Portfolio",
        "sections_required": ["hero", "gallery", "about", "contact", "footer"],
        "sections_optional": ["process", "testimonials", "services", "cta", "stats"],
        "sections_forbidden": ["menu", "pricing", "booking"],
        "default_variant_cluster": "V4",
        "mood_required": ["creative", "minimal"],
        "mood_forbidden": ["corporate", "food"],
        "style_names": ["portfolio-gallery", "portfolio-minimal", "portfolio-creative"],
    },
    {
        "category_slug": "fitness",
        "category_name": "Fitness",
        "sections_required": ["hero", "programs", "about", "gallery", "contact", "footer"],
        "sections_optional": ["testimonials", "team", "pricing", "faq", "cta", "stats"],
        "sections_forbidden": ["menu", "cases"],
        "default_variant_cluster": "V1",
        "mood_required": ["energetic"],
        "mood_forbidden": ["luxury", "minimal"],
        "style_names": [],
    },
    {
        "category_slug": "bellezza",
        "category_name": "Bellezza",
        "sections_required": ["hero", "services", "gallery", "about", "contact", "footer"],
        "sections_optional": ["testimonials", "team", "pricing", "booking", "cta"],
        "sections_forbidden": ["cases", "menu_food"],
        "default_variant_cluster": "V1/V4",
        "mood_required": ["elegant"],
        "mood_forbidden": ["tech", "corporate"],
        "style_names": [],
    },
    {
        "category_slug": "salute",
        "category_name": "Salute",
        "sections_required": ["hero", "services", "about", "team", "contact", "footer"],
        "sections_optional": ["testimonials", "faq", "booking", "stats", "cta"],
        "sections_forbidden": ["gallery_food", "menu"],
        "default_variant_cluster": "V2",
        "mood_required": ["trust", "professional"],
        "mood_forbidden": ["playful", "food"],
        "style_names": [],
    },
    {
        "category_slug": "saas",
        "category_name": "SaaS",
        "sections_required": ["hero", "features", "pricing", "about", "contact", "footer"],
        "sections_optional": ["testimonials", "faq", "stats", "cta", "process"],
        "sections_forbidden": ["menu", "gallery_food", "booking"],
        "default_variant_cluster": "V3",
        "mood_required": ["tech", "modern"],
        "mood_forbidden": ["warm", "food"],
        "style_names": ["saas-gradient", "saas-clean", "saas-dark"],
    },
    {
        "category_slug": "ecommerce",
        "category_name": "E-commerce",
        "sections_required": ["hero", "products", "about", "contact", "footer"],
        "sections_optional": ["testimonials", "faq", "trust_badges", "cta", "stats"],
        "sections_forbidden": ["menu_food", "cases"],
        "default_variant_cluster": "V3",
        "mood_required": ["modern"],
        "mood_forbidden": ["minimal"],
        "style_names": ["ecommerce-modern", "ecommerce-luxury"],
    },
    {
        "category_slug": "artigiani",
        "category_name": "Artigiani",
        "sections_required": ["hero", "services", "about", "gallery", "contact", "footer"],
        "sections_optional": ["process", "testimonials", "faq", "cta", "stats"],
        "sections_forbidden": ["pricing_saas", "cases"],
        "default_variant_cluster": "V5",
        "mood_required": ["warm", "handmade"],
        "mood_forbidden": ["tech", "corporate"],
        "style_names": [],
    },
    {
        "category_slug": "agenzia",
        "category_name": "Agenzia",
        "sections_required": ["hero", "services", "about", "portfolio", "contact", "footer"],
        "sections_optional": ["team", "testimonials", "cases", "cta", "stats", "process"],
        "sections_forbidden": ["menu", "booking_food"],
        "default_variant_cluster": "V2/V3",
        "mood_required": ["professional", "creative"],
        "mood_forbidden": ["food"],
        "style_names": [],
    },
]


def seed_category_blueprints():
    """Popola i category blueprints se la tabella e' vuota. Idempotente."""
    db = SessionLocal()
    try:
        existing = db.query(CategoryBlueprint).count()
        if existing > 0:
            logger.info(f"Category blueprints gia' popolati ({existing} categorie)")
            return existing

        for bp_data in BLUEPRINTS:
            bp = CategoryBlueprint(**bp_data)
            db.add(bp)

        db.commit()
        count = db.query(CategoryBlueprint).count()
        logger.info(f"Category blueprints seedati: {count} categorie")
        return count

    except Exception as e:
        db.rollback()
        logger.error(f"Errore seed category blueprints: {e}")
        raise
    finally:
        db.close()
