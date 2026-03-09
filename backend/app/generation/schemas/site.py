"""Complete site data schema combining theme + all sections."""

from typing import Any, Dict, List

from pydantic import BaseModel, ConfigDict, Field

from .theme import ThemeSchema


class SectionData(BaseModel):
    """A single section with its type, variant, and content.

    The content dict is validated lazily via validators.validate_section_content()
    rather than at parse time, so the assembler can handle partial/invalid data
    gracefully and provide targeted error messages for AI retry.
    """

    model_config = ConfigDict(populate_by_name=True)

    section_type: str = Field(
        ...,
        min_length=2,
        max_length=50,
        description="Section type key, e.g. 'hero', 'about', 'services'",
    )
    variant_id: str = Field(
        ...,
        min_length=2,
        max_length=100,
        description="Component variant ID, e.g. 'hero-classic-01', 'about-magazine-01'",
    )
    content: Dict[str, Any] = Field(
        default_factory=dict,
        description="Section content dict validated by section-specific schema",
    )


class SiteSchema(BaseModel):
    """Complete site data for assembly.

    Combines the global theme configuration with an ordered list of sections,
    each containing its type, component variant, and validated content.
    """

    model_config = ConfigDict(populate_by_name=True)

    theme: ThemeSchema = Field(
        ...,
        description="Global design configuration (colors, fonts, border-radius)",
    )
    sections: List[SectionData] = Field(
        ...,
        min_length=1,
        description="Ordered list of site sections",
    )
    business_name: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="Business/brand name",
    )
    business_description: str = Field(
        default="",
        max_length=2000,
        description="Business description provided by user",
    )
