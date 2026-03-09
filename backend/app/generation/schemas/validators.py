"""Validation utilities for AI-generated content.

Provides functions to validate section content against Pydantic schemas,
auto-fix common AI output mistakes, and generate JSON schemas for AI prompts.
"""

import json
import re
from copy import deepcopy
from typing import Any, Dict, List, Optional, Tuple, Type

from pydantic import BaseModel, ValidationError

from .sections import (
    AboutSection,
    AppDownloadSection,
    BlogSection,
    BookingSection,
    ComparisonSection,
    ContactSection,
    CtaSection,
    FaqSection,
    FeaturesSection,
    FooterSection,
    GallerySection,
    HeroSection,
    LogosSection,
    MenuSection,
    NavSection,
    PortfolioSection,
    PricingSection,
    ProcessSection,
    ReservationSection,
    ServicesSection,
    SocialProofSection,
    StatsSection,
    TeamSection,
    TestimonialsSection,
    VideoSection,
)

# ---------------------------------------------------------------------------
# Section type -> Pydantic schema mapping
# ---------------------------------------------------------------------------

SECTION_SCHEMA_MAP: Dict[str, Type[BaseModel]] = {
    "hero": HeroSection,
    "about": AboutSection,
    "services": ServicesSection,
    "features": FeaturesSection,
    "testimonials": TestimonialsSection,
    "gallery": GallerySection,
    "contact": ContactSection,
    "cta": CtaSection,
    "footer": FooterSection,
    "nav": NavSection,
    "pricing": PricingSection,
    "faq": FaqSection,
    "blog": BlogSection,
    "team": TeamSection,
    "menu": MenuSection,
    "stats": StatsSection,
    "process": ProcessSection,
    "reservation": ReservationSection,
    "booking": BookingSection,
    "comparison": ComparisonSection,
    "logos": LogosSection,
    "video": VideoSection,
    "portfolio": PortfolioSection,
    "social-proof": SocialProofSection,
    "app-download": AppDownloadSection,
}


# ---------------------------------------------------------------------------
# Key alias mappings for common AI mistakes
# ---------------------------------------------------------------------------

# Maps wrong/alternative keys the AI might produce -> canonical key name.
# Only includes cross-section patterns; per-section aliases handled in schemas.
_KEY_ALIASES: Dict[str, str] = {
    # Services
    "SERVICE_ITEMS": "SERVICES",
    "SERVICES_ITEMS": "SERVICES",
    "SERVICE_LIST": "SERVICES",
    "SERVICES_LIST": "SERVICES",
    "items": "SERVICES",  # generic
    # Features
    "FEATURE_ITEMS": "FEATURES",
    "FEATURES_ITEMS": "FEATURES",
    "FEATURE_LIST": "FEATURES",
    "FEATURES_LIST": "FEATURES",
    # Testimonials
    "TESTIMONIAL_ITEMS": "TESTIMONIALS",
    "TESTIMONIALS_ITEMS": "TESTIMONIALS",
    "TESTIMONIAL_LIST": "TESTIMONIALS",
    # Gallery
    "GALLERY": "GALLERY_ITEMS",
    "GALLERY_LIST": "GALLERY_ITEMS",
    "GALLERY_IMAGES": "GALLERY_ITEMS",
    # Team
    "TEAM": "TEAM_MEMBERS",
    "TEAM_ITEMS": "TEAM_MEMBERS",
    "TEAM_LIST": "TEAM_MEMBERS",
    "MEMBERS": "TEAM_MEMBERS",
    # FAQ
    "FAQ_LIST": "FAQ_ITEMS",
    "FAQS": "FAQ_ITEMS",
    # Blog
    "POSTS": "BLOG_POSTS",
    "BLOG_LIST": "BLOG_POSTS",
    # Pricing
    "PLANS": "PRICING_PLANS",
    "PRICING_LIST": "PRICING_PLANS",
    # Menu
    "MENU_LIST": "MENU_ITEMS",
    "MENU_DISHES": "MENU_ITEMS",
    # Stats
    "STATS": "STATS_ITEMS",
    "STATS_LIST": "STATS_ITEMS",
    # Process
    "STEPS": "PROCESS_STEPS",
    "PROCESS_LIST": "PROCESS_STEPS",
    # Logos
    "LOGOS": "LOGOS_ITEMS",
    "LOGOS_LIST": "LOGOS_ITEMS",
    # Comparison
    "COMPARISON_LIST": "COMPARISON_ITEMS",
    "COMPARISON_ROWS": "COMPARISON_ITEMS",
    # Social proof
    "SOCIAL_LIST": "SOCIAL_ITEMS",
    # About stats alternative keys
    "ABOUT_HIGHLIGHTS": "ABOUT_STATS",
    "HIGHLIGHTS": "ABOUT_STATS",
    "ABOUT_NUMBERS": "ABOUT_STATS",
    "about_stats": "ABOUT_STATS",
    # Contact duplication
    "CONTACT_EMAIL": "CONTACT_EMAIL",
    "CONTACT_PHONE": "CONTACT_PHONE",
    "CONTACT_ADDRESS": "CONTACT_ADDRESS",
}

# Maps CamelCase field names the AI might produce -> UPPER_SNAKE_CASE
_CAMEL_TO_UPPER: Dict[str, str] = {
    "heroTitle": "HERO_TITLE",
    "heroSubtitle": "HERO_SUBTITLE",
    "heroCtaText": "HERO_CTA_TEXT",
    "heroCtaUrl": "HERO_CTA_URL",
    "heroImageUrl": "HERO_IMAGE_URL",
    "heroImageAlt": "HERO_IMAGE_ALT",
    "servicesTitle": "SERVICES_TITLE",
    "servicesSubtitle": "SERVICES_SUBTITLE",
    "aboutTitle": "ABOUT_TITLE",
    "aboutSubtitle": "ABOUT_SUBTITLE",
    "aboutText": "ABOUT_TEXT",
    "contactTitle": "CONTACT_TITLE",
    "contactSubtitle": "CONTACT_SUBTITLE",
    "contactEmail": "CONTACT_EMAIL",
    "contactPhone": "CONTACT_PHONE",
    "contactAddress": "CONTACT_ADDRESS",
    "ctaTitle": "CTA_TITLE",
    "ctaSubtitle": "CTA_SUBTITLE",
    "ctaButtonText": "CTA_BUTTON_TEXT",
    "ctaButtonUrl": "CTA_BUTTON_URL",
    "testimonialsTitle": "TESTIMONIALS_TITLE",
    "galleryTitle": "GALLERY_TITLE",
    "gallerySubtitle": "GALLERY_SUBTITLE",
    "featuresTitle": "FEATURES_TITLE",
    "featuresSubtitle": "FEATURES_SUBTITLE",
    "pricingTitle": "PRICING_TITLE",
    "pricingSubtitle": "PRICING_SUBTITLE",
    "faqTitle": "FAQ_TITLE",
    "faqSubtitle": "FAQ_SUBTITLE",
    "teamTitle": "TEAM_TITLE",
    "teamSubtitle": "TEAM_SUBTITLE",
    "blogTitle": "BLOG_TITLE",
    "blogSubtitle": "BLOG_SUBTITLE",
    "menuTitle": "MENU_TITLE",
    "menuSubtitle": "MENU_SUBTITLE",
    "footerDescription": "FOOTER_DESCRIPTION",
    "businessName": "BUSINESS_NAME",
    "serviceTitle": "SERVICE_TITLE",
    "serviceDescription": "SERVICE_DESCRIPTION",
    "serviceIcon": "SERVICE_ICON",
    "featureTitle": "FEATURE_TITLE",
    "featureDescription": "FEATURE_DESCRIPTION",
    "featureIcon": "FEATURE_ICON",
    "testimonialText": "TESTIMONIAL_TEXT",
    "testimonialAuthor": "TESTIMONIAL_AUTHOR",
    "testimonialRole": "TESTIMONIAL_ROLE",
    "memberName": "MEMBER_NAME",
    "memberRole": "MEMBER_ROLE",
    "memberBio": "MEMBER_BIO",
    "planName": "PLAN_NAME",
    "planPrice": "PLAN_PRICE",
    "planDescription": "PLAN_DESCRIPTION",
    "planFeatures": "PLAN_FEATURES",
    "postTitle": "POST_TITLE",
    "postExcerpt": "POST_EXCERPT",
    "itemName": "ITEM_NAME",
    "itemDescription": "ITEM_DESCRIPTION",
    "itemPrice": "ITEM_PRICE",
    "itemCategory": "ITEM_CATEGORY",
    "stepTitle": "STEP_TITLE",
    "stepDescription": "STEP_DESCRIPTION",
}


def _camel_to_upper_snake(key: str) -> str:
    """Convert camelCase to UPPER_SNAKE_CASE."""
    # Check explicit map first
    if key in _CAMEL_TO_UPPER:
        return _CAMEL_TO_UPPER[key]
    # Generic conversion: insert underscore before uppercase letters
    s = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", key)
    return s.upper()


def _fix_keys_recursive(data: Any) -> Any:
    """Recursively fix key names in a dict/list structure."""
    if isinstance(data, dict):
        fixed: Dict[str, Any] = {}
        for key, value in data.items():
            # Fix CamelCase keys
            new_key = key
            if key and key[0].islower() and any(c.isupper() for c in key):
                new_key = _camel_to_upper_snake(key)
            # Fix alias keys
            if new_key in _KEY_ALIASES:
                canonical = _KEY_ALIASES[new_key]
                # Only use alias if canonical key is not already present
                if canonical not in fixed:
                    new_key = canonical
            fixed[new_key] = _fix_keys_recursive(value)
        return fixed
    if isinstance(data, list):
        return [_fix_keys_recursive(item) for item in data]
    return data


def _copy_contact_business_fields(content: Dict[str, Any]) -> Dict[str, Any]:
    """Copy CONTACT_* <-> BUSINESS_* fields for template compatibility.

    Some contact templates use CONTACT_EMAIL while others use BUSINESS_EMAIL.
    Ensure both exist when one is present.
    """
    mapping = {
        "CONTACT_EMAIL": "BUSINESS_EMAIL",
        "CONTACT_PHONE": "BUSINESS_PHONE",
        "CONTACT_ADDRESS": "BUSINESS_ADDRESS",
    }
    result = dict(content)
    for contact_key, business_key in mapping.items():
        if contact_key in result and not result.get(business_key):
            result[business_key] = result[contact_key]
        elif business_key in result and not result.get(contact_key):
            result[contact_key] = result[business_key]
    return result


def fix_common_ai_errors(content: Dict[str, Any], section_type: Optional[str] = None) -> Dict[str, Any]:
    """Auto-fix known AI output issues before validation.

    Fixes applied:
    1. CamelCase keys -> UPPER_SNAKE_CASE
    2. Alternative key names -> canonical names
    3. Empty strings in required fields -> removal (let defaults apply)
    4. Contact/Business field mirroring
    5. Flat numbered keys -> array format for repeat sections

    Returns a new dict (does not mutate the input).
    """
    result = deepcopy(content)

    # 1. Fix keys recursively (CamelCase + aliases)
    result = _fix_keys_recursive(result)

    # 2. Remove keys with None values (let Pydantic defaults apply)
    result = {k: v for k, v in result.items() if v is not None}

    # 3. Contact/Business field mirroring
    if section_type == "contact":
        result = _copy_contact_business_fields(result)

    # 4. Convert flat numbered keys to arrays for about stats
    if section_type == "about" and "ABOUT_STATS" not in result:
        stats: List[Dict[str, str]] = []
        for i in range(1, 10):
            num_key = f"ABOUT_HIGHLIGHT_NUM_{i}"
            label_key = f"ABOUT_HIGHLIGHT_{i}"
            if num_key in result and label_key in result:
                stats.append({
                    "STAT_NUMBER": str(result[num_key]),
                    "STAT_LABEL": str(result[label_key]),
                })
        if stats:
            result["ABOUT_STATS"] = stats

    # 5. Fix service/feature items with wrong inner key names
    for array_key in ("SERVICES", "FEATURES"):
        if array_key in result and isinstance(result[array_key], list):
            fixed_items = []
            prefix = "SERVICE" if array_key == "SERVICES" else "FEATURE"
            for item in result[array_key]:
                if isinstance(item, dict):
                    fixed_item = _fix_keys_recursive(item)
                    # Map common inner-key variants
                    for src, dst in [
                        ("title", f"{prefix}_TITLE"),
                        ("description", f"{prefix}_DESCRIPTION"),
                        ("icon", f"{prefix}_ICON"),
                        ("name", f"{prefix}_TITLE"),
                        ("desc", f"{prefix}_DESCRIPTION"),
                    ]:
                        if src in fixed_item and dst not in fixed_item:
                            fixed_item[dst] = fixed_item.pop(src)
                    fixed_items.append(fixed_item)
                else:
                    fixed_items.append(item)
            result[array_key] = fixed_items

    # 6. Fix testimonial items with wrong inner key names
    if "TESTIMONIALS" in result and isinstance(result["TESTIMONIALS"], list):
        fixed_items = []
        for item in result["TESTIMONIALS"]:
            if isinstance(item, dict):
                fixed_item = _fix_keys_recursive(item)
                for src, dst in [
                    ("text", "TESTIMONIAL_TEXT"),
                    ("quote", "TESTIMONIAL_TEXT"),
                    ("author", "TESTIMONIAL_AUTHOR"),
                    ("name", "TESTIMONIAL_AUTHOR"),
                    ("role", "TESTIMONIAL_ROLE"),
                    ("position", "TESTIMONIAL_ROLE"),
                ]:
                    if src in fixed_item and dst not in fixed_item:
                        fixed_item[dst] = fixed_item.pop(src)
                fixed_items.append(fixed_item)
            else:
                fixed_items.append(item)
        result["TESTIMONIALS"] = fixed_items

    # 7. Fix FAQ items with wrong inner key names
    if "FAQ_ITEMS" in result and isinstance(result["FAQ_ITEMS"], list):
        fixed_items = []
        for item in result["FAQ_ITEMS"]:
            if isinstance(item, dict):
                fixed_item = _fix_keys_recursive(item)
                for src, dst in [
                    ("question", "QUESTION"),
                    ("q", "QUESTION"),
                    ("domanda", "QUESTION"),
                    ("answer", "ANSWER"),
                    ("a", "ANSWER"),
                    ("risposta", "ANSWER"),
                ]:
                    if src in fixed_item and dst not in fixed_item:
                        fixed_item[dst] = fixed_item.pop(src)
                fixed_items.append(fixed_item)
            else:
                fixed_items.append(item)
        result["FAQ_ITEMS"] = fixed_items

    # 8. Fix menu items with wrong inner key names
    if "MENU_ITEMS" in result and isinstance(result["MENU_ITEMS"], list):
        fixed_items = []
        for item in result["MENU_ITEMS"]:
            if isinstance(item, dict):
                fixed_item = _fix_keys_recursive(item)
                for src, dst in [
                    ("name", "ITEM_NAME"),
                    ("dish", "ITEM_NAME"),
                    ("piatto", "ITEM_NAME"),
                    ("description", "ITEM_DESCRIPTION"),
                    ("descrizione", "ITEM_DESCRIPTION"),
                    ("price", "ITEM_PRICE"),
                    ("prezzo", "ITEM_PRICE"),
                    ("category", "ITEM_CATEGORY"),
                    ("categoria", "ITEM_CATEGORY"),
                ]:
                    if src in fixed_item and dst not in fixed_item:
                        fixed_item[dst] = fixed_item.pop(src)
                fixed_items.append(fixed_item)
            else:
                fixed_items.append(item)
        result["MENU_ITEMS"] = fixed_items

    # 9. Fix team members with wrong inner key names
    if "TEAM_MEMBERS" in result and isinstance(result["TEAM_MEMBERS"], list):
        fixed_items = []
        for item in result["TEAM_MEMBERS"]:
            if isinstance(item, dict):
                fixed_item = _fix_keys_recursive(item)
                for src, dst in [
                    ("name", "MEMBER_NAME"),
                    ("nome", "MEMBER_NAME"),
                    ("role", "MEMBER_ROLE"),
                    ("ruolo", "MEMBER_ROLE"),
                    ("bio", "MEMBER_BIO"),
                ]:
                    if src in fixed_item and dst not in fixed_item:
                        fixed_item[dst] = fixed_item.pop(src)
                fixed_items.append(fixed_item)
            else:
                fixed_items.append(item)
        result["TEAM_MEMBERS"] = fixed_items

    # 10. Fix pricing plans with wrong inner key names
    if "PRICING_PLANS" in result and isinstance(result["PRICING_PLANS"], list):
        fixed_items = []
        for item in result["PRICING_PLANS"]:
            if isinstance(item, dict):
                fixed_item = _fix_keys_recursive(item)
                for src, dst in [
                    ("name", "PLAN_NAME"),
                    ("nome", "PLAN_NAME"),
                    ("price", "PLAN_PRICE"),
                    ("prezzo", "PLAN_PRICE"),
                    ("description", "PLAN_DESCRIPTION"),
                    ("features", "PLAN_FEATURES"),
                ]:
                    if src in fixed_item and dst not in fixed_item:
                        fixed_item[dst] = fixed_item.pop(src)
                # Convert comma-separated features to list
                if "PLAN_FEATURES" in fixed_item and isinstance(fixed_item["PLAN_FEATURES"], str):
                    fixed_item["PLAN_FEATURES"] = [
                        f.strip() for f in fixed_item["PLAN_FEATURES"].split(",")
                        if f.strip()
                    ]
                fixed_items.append(fixed_item)
            else:
                fixed_items.append(item)
        result["PRICING_PLANS"] = fixed_items

    return result


def validate_section_content(
    section_type: str, content: Dict[str, Any]
) -> Tuple[bool, List[str]]:
    """Validate section content against its Pydantic schema.

    Args:
        section_type: The section type key (e.g. 'hero', 'services').
        content: The content dict to validate.

    Returns:
        Tuple of (is_valid, list_of_error_strings).
        Error strings are human-readable and suitable for AI retry prompts.
    """
    schema_cls = SECTION_SCHEMA_MAP.get(section_type)
    if schema_cls is None:
        return True, []  # Unknown section types pass without validation

    # Apply auto-fixes before validation
    fixed_content = fix_common_ai_errors(content, section_type=section_type)

    try:
        schema_cls.model_validate(fixed_content)
        return True, []
    except ValidationError as e:
        errors: List[str] = []
        for err in e.errors():
            loc = " -> ".join(str(part) for part in err["loc"])
            msg = err["msg"]
            errors.append(f"[{section_type}] {loc}: {msg}")
        return False, errors


def generate_prompt_schema(section_type: str) -> str:
    """Generate a JSON schema string suitable for injecting into an AI prompt.

    Returns the schema in a compact format that tells the AI exactly what
    fields are expected and their constraints.

    Args:
        section_type: The section type key (e.g. 'hero', 'services').

    Returns:
        A JSON string of the schema, or empty string if section type is unknown.
    """
    schema_cls = SECTION_SCHEMA_MAP.get(section_type)
    if schema_cls is None:
        return ""

    schema = schema_cls.model_json_schema(mode="serialization")

    # Simplify the schema for prompt injection: remove $defs references
    # and inline them for clarity
    defs = schema.pop("$defs", {})

    def _resolve_refs(obj: Any) -> Any:
        if isinstance(obj, dict):
            if "$ref" in obj:
                ref_name = obj["$ref"].split("/")[-1]
                if ref_name in defs:
                    return _resolve_refs(deepcopy(defs[ref_name]))
                return obj
            return {k: _resolve_refs(v) for k, v in obj.items()}
        if isinstance(obj, list):
            return [_resolve_refs(item) for item in obj]
        return obj

    resolved = _resolve_refs(schema)

    return json.dumps(resolved, indent=2, ensure_ascii=False)
