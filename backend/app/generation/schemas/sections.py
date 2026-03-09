"""Pydantic schemas for every section type in the Site Builder.

Each schema validates the AI-generated content for a specific section type,
mapping UPPERCASE placeholder names (used in HTML templates) to snake_case
Python field names via aliases. Lists use min_length to enforce minimum items
where content is expected.

Placeholders verified against backend/app/components/components.json.
"""

from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


# ---------------------------------------------------------------------------
# Shared sub-models for repeated items
# ---------------------------------------------------------------------------


class StatItem(BaseModel):
    """A single stat/highlight (number + label)."""

    model_config = ConfigDict(populate_by_name=True)

    stat_number: str = Field(
        ..., min_length=1, max_length=30, alias="STAT_NUMBER",
        description="Numeric value, e.g. '500+' or '98%'"
    )
    stat_label: str = Field(
        ..., min_length=1, max_length=80, alias="STAT_LABEL",
        description="Label for the stat, e.g. 'Clienti Soddisfatti'"
    )


class ServiceItem(BaseModel):
    """A single service entry."""

    model_config = ConfigDict(populate_by_name=True)

    service_icon: str = Field(
        default="", max_length=20, alias="SERVICE_ICON",
        description="Emoji icon for the service"
    )
    service_title: str = Field(
        ..., min_length=2, max_length=120, alias="SERVICE_TITLE",
    )
    service_description: str = Field(
        ..., min_length=10, max_length=500, alias="SERVICE_DESCRIPTION",
    )
    service_image_url: Optional[str] = Field(
        default="", alias="SERVICE_IMAGE_URL",
    )


class FeatureItem(BaseModel):
    """A single feature entry."""

    model_config = ConfigDict(populate_by_name=True)

    feature_icon: str = Field(
        default="", max_length=20, alias="FEATURE_ICON",
        description="Emoji icon for the feature"
    )
    feature_title: str = Field(
        ..., min_length=2, max_length=120, alias="FEATURE_TITLE",
    )
    feature_description: str = Field(
        ..., min_length=10, max_length=500, alias="FEATURE_DESCRIPTION",
    )


class TestimonialItem(BaseModel):
    """A single testimonial entry."""

    model_config = ConfigDict(populate_by_name=True)

    testimonial_text: str = Field(
        ..., min_length=20, max_length=600, alias="TESTIMONIAL_TEXT",
    )
    testimonial_author: str = Field(
        ..., min_length=2, max_length=100, alias="TESTIMONIAL_AUTHOR",
    )
    testimonial_role: str = Field(
        default="", max_length=100, alias="TESTIMONIAL_ROLE",
    )
    testimonial_initial: str = Field(
        default="", max_length=5, alias="TESTIMONIAL_INITIAL",
        description="First letter of author name for avatar fallback"
    )
    testimonial_avatar_url: Optional[str] = Field(
        default="", alias="TESTIMONIAL_AVATAR_URL",
    )
    testimonial_rating: Optional[int] = Field(
        default=5, ge=1, le=5, alias="TESTIMONIAL_RATING",
    )


class GalleryItem(BaseModel):
    """A single gallery image entry."""

    model_config = ConfigDict(populate_by_name=True)

    gallery_image_url: Optional[str] = Field(
        default="", alias="GALLERY_IMAGE_URL",
    )
    gallery_image_alt: str = Field(
        default="", max_length=200, alias="GALLERY_IMAGE_ALT",
    )
    gallery_caption: str = Field(
        default="", max_length=200, alias="GALLERY_CAPTION",
    )
    gallery_category: str = Field(
        default="", max_length=60, alias="GALLERY_CATEGORY",
        description="Category tag for filterable galleries"
    )


class TeamMember(BaseModel):
    """A single team member entry."""

    model_config = ConfigDict(populate_by_name=True)

    member_name: str = Field(
        ..., min_length=2, max_length=100, alias="MEMBER_NAME",
    )
    member_role: str = Field(
        ..., min_length=2, max_length=100, alias="MEMBER_ROLE",
    )
    member_image_url: Optional[str] = Field(
        default="", alias="MEMBER_IMAGE_URL",
    )
    member_bio: str = Field(
        default="", max_length=400, alias="MEMBER_BIO",
    )
    member_icon: str = Field(
        default="", max_length=20, alias="MEMBER_ICON",
    )


class PricingPlan(BaseModel):
    """A single pricing plan."""

    model_config = ConfigDict(populate_by_name=True)

    plan_name: str = Field(
        ..., min_length=2, max_length=60, alias="PLAN_NAME",
    )
    plan_price: str = Field(
        ..., min_length=1, max_length=30, alias="PLAN_PRICE",
        description="Price string e.g. '29/mese' or 'Gratis'"
    )
    plan_description: str = Field(
        default="", max_length=300, alias="PLAN_DESCRIPTION",
    )
    plan_features: List[str] = Field(
        default_factory=list, alias="PLAN_FEATURES",
        description="List of feature strings included in this plan"
    )
    plan_cta_text: str = Field(
        default="Inizia Ora", max_length=60, alias="PLAN_CTA_TEXT",
    )
    plan_cta_url: str = Field(
        default="#", max_length=500, alias="PLAN_CTA_URL",
    )
    plan_highlighted: bool = Field(
        default=False, alias="PLAN_HIGHLIGHTED",
        description="Whether this plan is the recommended/featured one"
    )
    plan_icon: str = Field(
        default="", max_length=20, alias="PLAN_ICON",
    )


class FaqItem(BaseModel):
    """A single FAQ question/answer pair."""

    model_config = ConfigDict(populate_by_name=True)

    question: str = Field(
        ..., min_length=5, max_length=300, alias="QUESTION",
    )
    answer: str = Field(
        ..., min_length=10, max_length=1000, alias="ANSWER",
    )


class BlogPost(BaseModel):
    """A single blog post preview."""

    model_config = ConfigDict(populate_by_name=True)

    post_title: str = Field(
        ..., min_length=5, max_length=200, alias="POST_TITLE",
    )
    post_excerpt: str = Field(
        ..., min_length=10, max_length=500, alias="POST_EXCERPT",
    )
    post_image_url: Optional[str] = Field(
        default="", alias="POST_IMAGE_URL",
    )
    post_category: str = Field(
        default="", max_length=60, alias="POST_CATEGORY",
    )
    post_date: str = Field(
        default="", max_length=30, alias="POST_DATE",
    )
    post_author: str = Field(
        default="", max_length=100, alias="POST_AUTHOR",
    )


class MenuItem(BaseModel):
    """A single menu item (restaurant)."""

    model_config = ConfigDict(populate_by_name=True)

    item_name: str = Field(
        ..., min_length=2, max_length=120, alias="ITEM_NAME",
    )
    item_description: str = Field(
        default="", max_length=300, alias="ITEM_DESCRIPTION",
    )
    item_price: str = Field(
        ..., min_length=1, max_length=30, alias="ITEM_PRICE",
    )
    item_category: str = Field(
        default="", max_length=60, alias="ITEM_CATEGORY",
        description="Category grouping, e.g. 'Antipasti', 'Primi'"
    )
    item_image_url: Optional[str] = Field(
        default="", alias="ITEM_IMAGE_URL",
    )
    item_badge: str = Field(
        default="", max_length=40, alias="ITEM_BADGE",
        description="Optional badge like 'Nuovo', 'Chef Consiglia'"
    )


class ProcessStep(BaseModel):
    """A single process/workflow step."""

    model_config = ConfigDict(populate_by_name=True)

    step_title: str = Field(
        ..., min_length=2, max_length=120, alias="STEP_TITLE",
    )
    step_description: str = Field(
        ..., min_length=10, max_length=400, alias="STEP_DESCRIPTION",
    )
    step_icon: str = Field(
        default="", max_length=20, alias="STEP_ICON",
    )


class LogoItem(BaseModel):
    """A single partner/client logo."""

    model_config = ConfigDict(populate_by_name=True)

    logo_name: str = Field(
        ..., min_length=1, max_length=100, alias="LOGO_NAME",
    )
    logo_image_url: Optional[str] = Field(
        default="", alias="LOGO_IMAGE_URL",
    )


class ComparisonItem(BaseModel):
    """A single comparison row (our feature vs competitor)."""

    model_config = ConfigDict(populate_by_name=True)

    feature_name: str = Field(
        ..., min_length=2, max_length=120, alias="FEATURE_NAME",
    )
    us: bool = Field(default=True, alias="US", description="We offer this")
    them: bool = Field(default=False, alias="THEM", description="Competitor offers this")


class SocialItem(BaseModel):
    """A single social proof / social media entry."""

    model_config = ConfigDict(populate_by_name=True)

    social_platform: str = Field(
        ..., min_length=1, max_length=60, alias="SOCIAL_PLATFORM",
    )
    social_count: str = Field(
        default="", max_length=30, alias="SOCIAL_COUNT",
    )
    social_icon: str = Field(
        default="", max_length=20, alias="SOCIAL_ICON",
    )


class AppFeatureItem(BaseModel):
    """A single app feature for download section."""

    model_config = ConfigDict(populate_by_name=True)

    feature_text: str = Field(
        ..., min_length=2, max_length=200, alias="FEATURE_TEXT",
    )


# ---------------------------------------------------------------------------
# Section schemas
# ---------------------------------------------------------------------------


class HeroSection(BaseModel):
    """Hero section content.

    Core placeholders: HERO_TITLE, HERO_SUBTITLE, HERO_CTA_TEXT, HERO_CTA_URL,
    HERO_IMAGE_URL, HERO_IMAGE_ALT, BUSINESS_NAME.
    Some variants add: HERO_VIDEO_EMBED, HERO_ROTATING_TEXTS, HERO_DESCRIPTION,
    BUSINESS_HOURS, BUSINESS_ADDRESS, BUSINESS_PHONE, EVENT_DATE, EVENT_LOCATION,
    FORM_TITLE, FORM_LABEL_*, FORM_BUTTON_TEXT, SEARCH_LABEL_*, HERO_CTA_TEXT_2/URL_2.
    """

    model_config = ConfigDict(populate_by_name=True)

    hero_title: str = Field(
        ..., min_length=3, max_length=200, alias="HERO_TITLE",
        description="Main headline"
    )
    hero_subtitle: str = Field(
        default="", max_length=500, alias="HERO_SUBTITLE",
        description="Supporting text below headline"
    )
    hero_description: str = Field(
        default="", max_length=500, alias="HERO_DESCRIPTION",
        description="Extended description (used by some variants instead of subtitle)"
    )
    hero_cta_text: str = Field(
        default="Scopri di Piu", max_length=60, alias="HERO_CTA_TEXT",
    )
    hero_cta_url: str = Field(
        default="#contatti", max_length=500, alias="HERO_CTA_URL",
    )
    hero_cta_text_2: str = Field(
        default="", max_length=60, alias="HERO_CTA_TEXT_2",
    )
    hero_cta_url_2: str = Field(
        default="", max_length=500, alias="HERO_CTA_URL_2",
    )
    hero_image_url: Optional[str] = Field(
        default="", alias="HERO_IMAGE_URL",
    )
    hero_image_alt: str = Field(
        default="", max_length=200, alias="HERO_IMAGE_ALT",
    )
    hero_video_embed: str = Field(
        default="", max_length=1000, alias="HERO_VIDEO_EMBED",
    )
    hero_rotating_texts: str = Field(
        default="", max_length=500, alias="HERO_ROTATING_TEXTS",
        description="Comma-separated rotating text phrases"
    )
    business_name: str = Field(
        default="", max_length=200, alias="BUSINESS_NAME",
    )
    business_hours: str = Field(
        default="", max_length=200, alias="BUSINESS_HOURS",
    )
    business_address: str = Field(
        default="", max_length=300, alias="BUSINESS_ADDRESS",
    )
    business_phone: str = Field(
        default="", max_length=50, alias="BUSINESS_PHONE",
    )
    event_date: str = Field(
        default="", max_length=100, alias="EVENT_DATE",
    )
    event_location: str = Field(
        default="", max_length=200, alias="EVENT_LOCATION",
    )
    form_title: str = Field(
        default="", max_length=120, alias="FORM_TITLE",
    )
    form_label_1: str = Field(
        default="", max_length=60, alias="FORM_LABEL_1",
    )
    form_label_2: str = Field(
        default="", max_length=60, alias="FORM_LABEL_2",
    )
    form_label_3: str = Field(
        default="", max_length=60, alias="FORM_LABEL_3",
    )
    form_label_4: str = Field(
        default="", max_length=60, alias="FORM_LABEL_4",
    )
    form_button_text: str = Field(
        default="", max_length=60, alias="FORM_BUTTON_TEXT",
    )
    search_label_1: str = Field(
        default="", max_length=60, alias="SEARCH_LABEL_1",
    )
    search_label_2: str = Field(
        default="", max_length=60, alias="SEARCH_LABEL_2",
    )
    search_label_3: str = Field(
        default="", max_length=60, alias="SEARCH_LABEL_3",
    )


class AboutSection(BaseModel):
    """About/Chi Siamo section content.

    Core placeholders: ABOUT_TITLE, ABOUT_SUBTITLE, ABOUT_TEXT,
    ABOUT_IMAGE_URL, ABOUT_IMAGE_ALT, ABOUT_DESCRIPTION, ABOUT_STATS (repeat),
    ABOUT_HIGHLIGHT_NUM_1..3, ABOUT_HIGHLIGHT_1..3, BUSINESS_NAME.
    Some variants add: MILESTONE_YEAR_1..3, MILESTONE_DESC_1..3,
    ABOUT_BADGE_NUMBER, ABOUT_BADGE_LABEL, ABOUT_SKILLS, ABOUT_CTA_TEXT/URL.
    """

    model_config = ConfigDict(populate_by_name=True)

    about_title: str = Field(
        ..., min_length=3, max_length=200, alias="ABOUT_TITLE",
    )
    about_subtitle: str = Field(
        default="", max_length=400, alias="ABOUT_SUBTITLE",
    )
    about_text: str = Field(
        default="", max_length=2000, alias="ABOUT_TEXT",
        description="Main body text for the about section"
    )
    about_description: str = Field(
        default="", max_length=2000, alias="ABOUT_DESCRIPTION",
        description="Alternative to about_text used by some variants"
    )
    about_image_url: Optional[str] = Field(
        default="", alias="ABOUT_IMAGE_URL",
    )
    about_image_alt: str = Field(
        default="", max_length=200, alias="ABOUT_IMAGE_ALT",
    )
    business_name: str = Field(
        default="", max_length=200, alias="BUSINESS_NAME",
    )
    about_stats: List[StatItem] = Field(
        default_factory=list, alias="ABOUT_STATS",
        description="List of stat items (STAT_NUMBER + STAT_LABEL)"
    )
    about_highlight_num_1: str = Field(
        default="", max_length=30, alias="ABOUT_HIGHLIGHT_NUM_1",
    )
    about_highlight_1: str = Field(
        default="", max_length=80, alias="ABOUT_HIGHLIGHT_1",
    )
    about_highlight_num_2: str = Field(
        default="", max_length=30, alias="ABOUT_HIGHLIGHT_NUM_2",
    )
    about_highlight_2: str = Field(
        default="", max_length=80, alias="ABOUT_HIGHLIGHT_2",
    )
    about_highlight_num_3: str = Field(
        default="", max_length=30, alias="ABOUT_HIGHLIGHT_NUM_3",
    )
    about_highlight_3: str = Field(
        default="", max_length=80, alias="ABOUT_HIGHLIGHT_3",
    )
    milestone_year_1: str = Field(
        default="", max_length=10, alias="MILESTONE_YEAR_1",
    )
    milestone_desc_1: str = Field(
        default="", max_length=200, alias="MILESTONE_DESC_1",
    )
    milestone_year_2: str = Field(
        default="", max_length=10, alias="MILESTONE_YEAR_2",
    )
    milestone_desc_2: str = Field(
        default="", max_length=200, alias="MILESTONE_DESC_2",
    )
    milestone_year_3: str = Field(
        default="", max_length=10, alias="MILESTONE_YEAR_3",
    )
    milestone_desc_3: str = Field(
        default="", max_length=200, alias="MILESTONE_DESC_3",
    )
    about_badge_number: str = Field(
        default="", max_length=30, alias="ABOUT_BADGE_NUMBER",
    )
    about_badge_label: str = Field(
        default="", max_length=80, alias="ABOUT_BADGE_LABEL",
    )
    about_skills: str = Field(
        default="", max_length=500, alias="ABOUT_SKILLS",
        description="Skills/competencies (may be JSON array or comma-separated)"
    )
    about_cta_text: str = Field(
        default="", max_length=60, alias="ABOUT_CTA_TEXT",
    )
    about_cta_url: str = Field(
        default="", max_length=500, alias="ABOUT_CTA_URL",
    )


class ServicesSection(BaseModel):
    """Services/Servizi section content.

    Core placeholders: SERVICES_TITLE, SERVICES_SUBTITLE, SERVICES (repeat array).
    Each SERVICES item: SERVICE_ICON, SERVICE_TITLE, SERVICE_DESCRIPTION, SERVICE_IMAGE_URL.
    """

    model_config = ConfigDict(populate_by_name=True)

    services_title: str = Field(
        ..., min_length=3, max_length=200, alias="SERVICES_TITLE",
    )
    services_subtitle: str = Field(
        default="", max_length=400, alias="SERVICES_SUBTITLE",
    )
    services: List[ServiceItem] = Field(
        ..., min_length=3, alias="SERVICES",
        description="List of service items (minimum 3)"
    )


class FeaturesSection(BaseModel):
    """Features/Caratteristiche section content.

    Core placeholders: FEATURES_TITLE, FEATURES_SUBTITLE, FEATURES (repeat array).
    Each FEATURES item: FEATURE_ICON, FEATURE_TITLE, FEATURE_DESCRIPTION.
    """

    model_config = ConfigDict(populate_by_name=True)

    features_title: str = Field(
        ..., min_length=3, max_length=200, alias="FEATURES_TITLE",
    )
    features_subtitle: str = Field(
        default="", max_length=400, alias="FEATURES_SUBTITLE",
    )
    features: List[FeatureItem] = Field(
        ..., min_length=3, alias="FEATURES",
        description="List of feature items (minimum 3)"
    )


class TestimonialsSection(BaseModel):
    """Testimonials/Testimonianze section content.

    Core placeholders: TESTIMONIALS_TITLE, TESTIMONIALS_SUBTITLE,
    TESTIMONIALS (repeat array).
    Each TESTIMONIALS item: TESTIMONIAL_TEXT, TESTIMONIAL_AUTHOR,
    TESTIMONIAL_ROLE, TESTIMONIAL_INITIAL, TESTIMONIAL_AVATAR_URL.
    """

    model_config = ConfigDict(populate_by_name=True)

    testimonials_title: str = Field(
        ..., min_length=3, max_length=200, alias="TESTIMONIALS_TITLE",
    )
    testimonials_subtitle: str = Field(
        default="", max_length=400, alias="TESTIMONIALS_SUBTITLE",
    )
    testimonials: List[TestimonialItem] = Field(
        ..., min_length=3, alias="TESTIMONIALS",
        description="List of testimonial items (minimum 3)"
    )


class GallerySection(BaseModel):
    """Gallery/Galleria section content.

    Core placeholders: GALLERY_TITLE, GALLERY_SUBTITLE, GALLERY_ITEMS (repeat array).
    Each item: GALLERY_IMAGE_URL, GALLERY_IMAGE_ALT, GALLERY_CAPTION, GALLERY_CATEGORY.
    """

    model_config = ConfigDict(populate_by_name=True)

    gallery_title: str = Field(
        ..., min_length=3, max_length=200, alias="GALLERY_TITLE",
    )
    gallery_subtitle: str = Field(
        default="", max_length=400, alias="GALLERY_SUBTITLE",
    )
    gallery_items: List[GalleryItem] = Field(
        ..., min_length=4, alias="GALLERY_ITEMS",
        description="List of gallery images (minimum 4)"
    )


class ContactSection(BaseModel):
    """Contact/Contatti section content.

    Core placeholders: CONTACT_TITLE, CONTACT_SUBTITLE,
    CONTACT_EMAIL, CONTACT_PHONE, CONTACT_ADDRESS.
    Some variants use BUSINESS_* instead of CONTACT_*.
    Some add: BUSINESS_HOURS, BUSINESS_NAME, CONTACT_MAP_EMBED,
    CONTACT_CTA_TEXT, CONTACT_CTA_URL, CONTACT_TEXT.
    """

    model_config = ConfigDict(populate_by_name=True)

    contact_title: str = Field(
        ..., min_length=3, max_length=200, alias="CONTACT_TITLE",
    )
    contact_subtitle: str = Field(
        default="", max_length=400, alias="CONTACT_SUBTITLE",
    )
    contact_email: str = Field(
        default="", max_length=200, alias="CONTACT_EMAIL",
    )
    contact_phone: str = Field(
        default="", max_length=50, alias="CONTACT_PHONE",
    )
    contact_address: str = Field(
        default="", max_length=300, alias="CONTACT_ADDRESS",
    )
    contact_text: str = Field(
        default="", max_length=500, alias="CONTACT_TEXT",
    )
    contact_cta_text: str = Field(
        default="", max_length=60, alias="CONTACT_CTA_TEXT",
    )
    contact_cta_url: str = Field(
        default="", max_length=500, alias="CONTACT_CTA_URL",
    )
    contact_map_embed: str = Field(
        default="", max_length=2000, alias="CONTACT_MAP_EMBED",
    )
    business_name: str = Field(
        default="", max_length=200, alias="BUSINESS_NAME",
    )
    business_email: str = Field(
        default="", max_length=200, alias="BUSINESS_EMAIL",
    )
    business_phone: str = Field(
        default="", max_length=50, alias="BUSINESS_PHONE",
    )
    business_address: str = Field(
        default="", max_length=300, alias="BUSINESS_ADDRESS",
    )
    business_hours: str = Field(
        default="", max_length=500, alias="BUSINESS_HOURS",
    )


class CtaSection(BaseModel):
    """Call to Action section content.

    Core placeholders: CTA_TITLE, CTA_SUBTITLE, CTA_BUTTON_TEXT, CTA_BUTTON_URL.
    """

    model_config = ConfigDict(populate_by_name=True)

    cta_title: str = Field(
        ..., min_length=3, max_length=200, alias="CTA_TITLE",
    )
    cta_subtitle: str = Field(
        default="", max_length=400, alias="CTA_SUBTITLE",
    )
    cta_button_text: str = Field(
        default="Inizia Ora", max_length=60, alias="CTA_BUTTON_TEXT",
    )
    cta_button_url: str = Field(
        default="#contatti", max_length=500, alias="CTA_BUTTON_URL",
    )


class FooterSection(BaseModel):
    """Footer section content.

    Core placeholder: FOOTER_DESCRIPTION.
    Some variants add: FOOTER_TEXT, FOOTER_COPYRIGHT, BUSINESS_NAME,
    FOOTER_LINKS, FOOTER_CTA_TEXT, FOOTER_CTA_URL.
    """

    model_config = ConfigDict(populate_by_name=True)

    footer_description: str = Field(
        default="", max_length=500, alias="FOOTER_DESCRIPTION",
        description="Short business description for footer"
    )
    footer_text: str = Field(
        default="", max_length=500, alias="FOOTER_TEXT",
    )
    footer_copyright: str = Field(
        default="", max_length=200, alias="FOOTER_COPYRIGHT",
    )
    business_name: str = Field(
        default="", max_length=200, alias="BUSINESS_NAME",
    )
    footer_cta_text: str = Field(
        default="", max_length=60, alias="FOOTER_CTA_TEXT",
    )
    footer_cta_url: str = Field(
        default="", max_length=500, alias="FOOTER_CTA_URL",
    )


class NavSection(BaseModel):
    """Navigation section content.

    Core placeholders: NAV_LOGO_TEXT, NAV_LINKS, NAV_CTA_TEXT, NAV_CTA_URL.
    Note: Most nav variants are auto-generated from section list,
    so this schema is minimal.
    """

    model_config = ConfigDict(populate_by_name=True)

    nav_logo_text: str = Field(
        default="", max_length=100, alias="NAV_LOGO_TEXT",
    )
    nav_cta_text: str = Field(
        default="", max_length=60, alias="NAV_CTA_TEXT",
    )
    nav_cta_url: str = Field(
        default="#contatti", max_length=500, alias="NAV_CTA_URL",
    )


class PricingSection(BaseModel):
    """Pricing/Prezzi section content.

    Core placeholders: PRICING_TITLE, PRICING_SUBTITLE, PRICING_PLANS (repeat array).
    Each plan: PLAN_NAME, PLAN_PRICE, PLAN_DESCRIPTION, PLAN_FEATURES,
    PLAN_CTA_TEXT, PLAN_CTA_URL, PLAN_HIGHLIGHTED, PLAN_ICON.
    """

    model_config = ConfigDict(populate_by_name=True)

    pricing_title: str = Field(
        ..., min_length=3, max_length=200, alias="PRICING_TITLE",
    )
    pricing_subtitle: str = Field(
        default="", max_length=400, alias="PRICING_SUBTITLE",
    )
    pricing_plans: List[PricingPlan] = Field(
        ..., min_length=2, alias="PRICING_PLANS",
        description="List of pricing plans (minimum 2, typically 3)"
    )


class FaqSection(BaseModel):
    """FAQ section content.

    Core placeholders: FAQ_TITLE, FAQ_SUBTITLE, FAQ_ITEMS (repeat array).
    Each item: QUESTION, ANSWER.
    """

    model_config = ConfigDict(populate_by_name=True)

    faq_title: str = Field(
        ..., min_length=3, max_length=200, alias="FAQ_TITLE",
    )
    faq_subtitle: str = Field(
        default="", max_length=400, alias="FAQ_SUBTITLE",
    )
    faq_items: List[FaqItem] = Field(
        ..., min_length=3, alias="FAQ_ITEMS",
        description="List of FAQ items (minimum 3)"
    )


class BlogSection(BaseModel):
    """Blog section content.

    Core placeholders: BLOG_TITLE, BLOG_SUBTITLE, BLOG_POSTS (repeat array).
    Each post: POST_TITLE, POST_EXCERPT, POST_IMAGE_URL, POST_CATEGORY,
    POST_DATE, POST_AUTHOR.
    """

    model_config = ConfigDict(populate_by_name=True)

    blog_title: str = Field(
        ..., min_length=3, max_length=200, alias="BLOG_TITLE",
    )
    blog_subtitle: str = Field(
        default="", max_length=400, alias="BLOG_SUBTITLE",
    )
    blog_posts: List[BlogPost] = Field(
        ..., min_length=2, alias="BLOG_POSTS",
        description="List of blog post previews (minimum 2)"
    )


class TeamSection(BaseModel):
    """Team section content.

    Core placeholders: TEAM_TITLE, TEAM_SUBTITLE, TEAM_MEMBERS (repeat array).
    Each member: MEMBER_NAME, MEMBER_ROLE, MEMBER_IMAGE_URL, MEMBER_BIO, MEMBER_ICON.
    """

    model_config = ConfigDict(populate_by_name=True)

    team_title: str = Field(
        ..., min_length=3, max_length=200, alias="TEAM_TITLE",
    )
    team_subtitle: str = Field(
        default="", max_length=400, alias="TEAM_SUBTITLE",
    )
    team_members: List[TeamMember] = Field(
        ..., min_length=2, alias="TEAM_MEMBERS",
        description="List of team members (minimum 2)"
    )


class MenuSection(BaseModel):
    """Menu section content (restaurant).

    Core placeholders: MENU_TITLE, MENU_SUBTITLE, MENU_ITEMS (repeat array).
    Each item: ITEM_NAME, ITEM_DESCRIPTION, ITEM_PRICE, ITEM_CATEGORY,
    ITEM_IMAGE_URL, ITEM_BADGE.
    """

    model_config = ConfigDict(populate_by_name=True)

    menu_title: str = Field(
        ..., min_length=3, max_length=200, alias="MENU_TITLE",
    )
    menu_subtitle: str = Field(
        default="", max_length=400, alias="MENU_SUBTITLE",
    )
    menu_items: List[MenuItem] = Field(
        ..., min_length=4, alias="MENU_ITEMS",
        description="List of menu items (minimum 4)"
    )


class StatsSection(BaseModel):
    """Stats/Statistiche section content.

    Core placeholders: STATS_TITLE, STATS_SUBTITLE, STATS_ITEMS (repeat array).
    Each item uses StatItem (STAT_NUMBER + STAT_LABEL).
    Some variants add: STATS_BG_IMAGE.
    """

    model_config = ConfigDict(populate_by_name=True)

    stats_title: str = Field(
        default="", max_length=200, alias="STATS_TITLE",
    )
    stats_subtitle: str = Field(
        default="", max_length=400, alias="STATS_SUBTITLE",
    )
    stats_items: List[StatItem] = Field(
        ..., min_length=3, alias="STATS_ITEMS",
        description="List of stat items (minimum 3)"
    )
    stats_bg_image: Optional[str] = Field(
        default="", alias="STATS_BG_IMAGE",
    )


class ProcessSection(BaseModel):
    """Process/Processo section content.

    Core placeholders: PROCESS_TITLE, PROCESS_SUBTITLE, PROCESS_STEPS (repeat array).
    Each step: STEP_TITLE, STEP_DESCRIPTION, STEP_ICON.
    """

    model_config = ConfigDict(populate_by_name=True)

    process_title: str = Field(
        ..., min_length=3, max_length=200, alias="PROCESS_TITLE",
    )
    process_subtitle: str = Field(
        default="", max_length=400, alias="PROCESS_SUBTITLE",
    )
    process_steps: List[ProcessStep] = Field(
        ..., min_length=3, alias="PROCESS_STEPS",
        description="List of process steps (minimum 3)"
    )


class ReservationSection(BaseModel):
    """Reservation/Prenotazione section (restaurant).

    Core placeholders: RESERVATION_TITLE, RESERVATION_SUBTITLE,
    RESERVATION_PHONE, RESERVATION_EMAIL.
    Some variants add: BUSINESS_HOURS, BUSINESS_ADDRESS, HERO_IMAGE_URL.
    """

    model_config = ConfigDict(populate_by_name=True)

    reservation_title: str = Field(
        ..., min_length=3, max_length=200, alias="RESERVATION_TITLE",
    )
    reservation_subtitle: str = Field(
        default="", max_length=400, alias="RESERVATION_SUBTITLE",
    )
    reservation_phone: str = Field(
        default="", max_length=50, alias="RESERVATION_PHONE",
    )
    reservation_email: str = Field(
        default="", max_length=200, alias="RESERVATION_EMAIL",
    )
    business_hours: str = Field(
        default="", max_length=500, alias="BUSINESS_HOURS",
    )
    business_address: str = Field(
        default="", max_length=300, alias="BUSINESS_ADDRESS",
    )
    hero_image_url: Optional[str] = Field(
        default="", alias="HERO_IMAGE_URL",
    )


class BookingSection(BaseModel):
    """Booking/Prenotazione Appuntamento section.

    Core placeholders: BOOKING_TITLE, BOOKING_SUBTITLE, BOOKING_DESCRIPTION,
    BOOKING_PHONE, BOOKING_EMAIL, BOOKING_HOURS,
    BOOKING_SERVICE_LABEL, BOOKING_NOTES_LABEL, BOOKING_BUTTON_TEXT.
    """

    model_config = ConfigDict(populate_by_name=True)

    booking_title: str = Field(
        ..., min_length=3, max_length=200, alias="BOOKING_TITLE",
    )
    booking_subtitle: str = Field(
        default="", max_length=400, alias="BOOKING_SUBTITLE",
    )
    booking_description: str = Field(
        default="", max_length=500, alias="BOOKING_DESCRIPTION",
    )
    booking_phone: str = Field(
        default="", max_length=50, alias="BOOKING_PHONE",
    )
    booking_email: str = Field(
        default="", max_length=200, alias="BOOKING_EMAIL",
    )
    booking_hours: str = Field(
        default="", max_length=500, alias="BOOKING_HOURS",
    )
    booking_service_label: str = Field(
        default="Servizio", max_length=60, alias="BOOKING_SERVICE_LABEL",
    )
    booking_notes_label: str = Field(
        default="Note", max_length=60, alias="BOOKING_NOTES_LABEL",
    )
    booking_button_text: str = Field(
        default="Prenota", max_length=60, alias="BOOKING_BUTTON_TEXT",
    )


class ComparisonSection(BaseModel):
    """Comparison/Confronto section.

    Core placeholders: COMPARISON_TITLE, COMPARISON_SUBTITLE,
    COMPARISON_BRAND_NAME, COMPARISON_ITEMS, COMPARISON_CTA_TEXT, COMPARISON_CTA_URL.
    """

    model_config = ConfigDict(populate_by_name=True)

    comparison_title: str = Field(
        ..., min_length=3, max_length=200, alias="COMPARISON_TITLE",
    )
    comparison_subtitle: str = Field(
        default="", max_length=400, alias="COMPARISON_SUBTITLE",
    )
    comparison_brand_name: str = Field(
        default="", max_length=100, alias="COMPARISON_BRAND_NAME",
    )
    comparison_items: List[ComparisonItem] = Field(
        ..., min_length=3, alias="COMPARISON_ITEMS",
        description="List of comparison rows (minimum 3)"
    )
    comparison_cta_text: str = Field(
        default="", max_length=60, alias="COMPARISON_CTA_TEXT",
    )
    comparison_cta_url: str = Field(
        default="#contatti", max_length=500, alias="COMPARISON_CTA_URL",
    )


class LogosSection(BaseModel):
    """Logos/Loghi Partner section.

    Core placeholders: LOGOS_TITLE, LOGOS_ITEMS (repeat array).
    """

    model_config = ConfigDict(populate_by_name=True)

    logos_title: str = Field(
        default="", max_length=200, alias="LOGOS_TITLE",
    )
    logos_items: List[LogoItem] = Field(
        ..., min_length=3, alias="LOGOS_ITEMS",
        description="List of partner/client logos (minimum 3)"
    )


class VideoSection(BaseModel):
    """Video section content.

    Minimal placeholders -- most video variants are self-contained.
    """

    model_config = ConfigDict(populate_by_name=True)

    video_title: str = Field(
        default="", max_length=200, alias="VIDEO_TITLE",
    )
    video_subtitle: str = Field(
        default="", max_length=400, alias="VIDEO_SUBTITLE",
    )
    video_url: str = Field(
        default="", max_length=1000, alias="VIDEO_URL",
    )
    video_embed: str = Field(
        default="", max_length=2000, alias="VIDEO_EMBED",
    )


class PortfolioSection(BaseModel):
    """Portfolio section content.

    Core placeholders: PORTFOLIO_TITLE, PORTFOLIO_SUBTITLE, PORTFOLIO_ITEMS.
    """

    model_config = ConfigDict(populate_by_name=True)

    portfolio_title: str = Field(
        default="", max_length=200, alias="PORTFOLIO_TITLE",
    )
    portfolio_subtitle: str = Field(
        default="", max_length=400, alias="PORTFOLIO_SUBTITLE",
    )
    portfolio_items: List[GalleryItem] = Field(
        default_factory=list, alias="PORTFOLIO_ITEMS",
        description="Reuses GalleryItem structure for portfolio pieces"
    )


class SocialProofSection(BaseModel):
    """Social Proof section content.

    Core placeholders: SOCIAL_TITLE, SOCIAL_ITEMS (repeat array).
    """

    model_config = ConfigDict(populate_by_name=True)

    social_title: str = Field(
        default="", max_length=200, alias="SOCIAL_TITLE",
    )
    social_items: List[SocialItem] = Field(
        ..., min_length=2, alias="SOCIAL_ITEMS",
        description="List of social proof entries (minimum 2)"
    )


class AppDownloadSection(BaseModel):
    """App Download section content.

    Core placeholders: APP_TITLE, APP_SUBTITLE, APP_FEATURES,
    APP_IMAGE_URL, APP_STORE_URL, APP_PLAY_URL.
    """

    model_config = ConfigDict(populate_by_name=True)

    app_title: str = Field(
        ..., min_length=3, max_length=200, alias="APP_TITLE",
    )
    app_subtitle: str = Field(
        default="", max_length=400, alias="APP_SUBTITLE",
    )
    app_features: List[AppFeatureItem] = Field(
        default_factory=list, alias="APP_FEATURES",
        description="List of app feature highlights"
    )
    app_image_url: Optional[str] = Field(
        default="", alias="APP_IMAGE_URL",
    )
    app_store_url: str = Field(
        default="#", max_length=500, alias="APP_STORE_URL",
    )
    app_play_url: str = Field(
        default="#", max_length=500, alias="APP_PLAY_URL",
    )
