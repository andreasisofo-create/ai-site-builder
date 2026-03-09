"""Pydantic schemas for theme/design configuration."""

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ThemeSchema(BaseModel):
    """Schema for AI-generated theme configuration.

    Validates color hex codes, font names (banning system defaults),
    and provides sensible defaults for optional fields.
    """

    model_config = ConfigDict(populate_by_name=True)

    primary_color: str = Field(
        ...,
        pattern=r"^#[0-9a-fA-F]{6}$",
        description="Primary brand color in hex format",
        alias="PRIMARY_COLOR",
    )
    secondary_color: str = Field(
        ...,
        pattern=r"^#[0-9a-fA-F]{6}$",
        description="Secondary brand color",
        alias="SECONDARY_COLOR",
    )
    accent_color: str = Field(
        ...,
        pattern=r"^#[0-9a-fA-F]{6}$",
        description="Accent/highlight color",
        alias="ACCENT_COLOR",
    )
    bg_color: str = Field(
        default="#FFFFFF",
        pattern=r"^#[0-9a-fA-F]{6}$",
        description="Page background color",
        alias="BG_COLOR",
    )
    bg_alt_color: str = Field(
        default="#F8FAFC",
        pattern=r"^#[0-9a-fA-F]{6}$",
        description="Alternate background for sections",
        alias="BG_ALT_COLOR",
    )
    text_color: str = Field(
        ...,
        pattern=r"^#[0-9a-fA-F]{6}$",
        description="Primary text color",
        alias="TEXT_COLOR",
    )
    text_muted_color: str = Field(
        ...,
        pattern=r"^#[0-9a-fA-F]{6}$",
        description="Muted/secondary text color",
        alias="TEXT_MUTED_COLOR",
    )
    font_heading: str = Field(
        ...,
        min_length=2,
        max_length=100,
        description="Google Font name for headings (e.g. Playfair Display)",
        alias="FONT_HEADING",
    )
    font_body: str = Field(
        ...,
        min_length=2,
        max_length=100,
        description="Google Font name for body text (e.g. Inter)",
        alias="FONT_BODY",
    )
    border_radius: str = Field(
        default="0.75rem",
        max_length=20,
        description="Border radius for cards and buttons",
        alias="BORDER_RADIUS",
    )

    @field_validator("font_heading", "font_body")
    @classmethod
    def validate_font(cls, v: str) -> str:
        """Reject system/default fonts -- only Google Fonts are allowed."""
        banned = {
            "arial",
            "helvetica",
            "times new roman",
            "times",
            "verdana",
            "georgia",
            "system-ui",
            "sans-serif",
            "serif",
            "monospace",
            "cursive",
            "tahoma",
            "courier",
            "courier new",
            "lucida console",
            "comic sans ms",
            "impact",
            "trebuchet ms",
        }
        if v.lower().strip() in banned:
            raise ValueError(
                f"Font '{v}' is a system default. "
                "Use Google Fonts with character like Playfair Display, "
                "Space Grotesk, Sora, DM Serif Display, Inter, etc."
            )
        return v.strip()

    @field_validator(
        "primary_color",
        "secondary_color",
        "accent_color",
        "bg_color",
        "bg_alt_color",
        "text_color",
        "text_muted_color",
    )
    @classmethod
    def normalize_hex(cls, v: str) -> str:
        """Ensure hex colors are uppercase for consistency."""
        return v.upper()
