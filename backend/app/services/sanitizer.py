"""
Servizio sanitizzazione input/output per protezione AI.
- Input: blocca prompt injection, limita lunghezza
- Output: rimuovi script/iframe, whitelist CDN, valida HTML
"""

import re
import logging
from typing import List, Optional, Tuple

logger = logging.getLogger(__name__)

# Pattern sospetti di prompt injection
INJECTION_PATTERNS = [
    r"ignore\s+(all\s+)?previous\s+instructions",
    r"ignore\s+(all\s+)?above",
    r"disregard\s+(all\s+)?previous",
    r"forget\s+(all\s+)?previous",
    r"you\s+are\s+now\s+a",
    r"act\s+as\s+if",
    r"pretend\s+you\s+are",
    r"new\s+instructions?:",
    r"system\s*:\s*",
    r"<\s*system\s*>",
    r"\[INST\]",
    r"\[/INST\]",
    r"<<SYS>>",
    r"<\|im_start\|>",
]

# CDN/domini esterni consentiti nell'HTML generato
ALLOWED_DOMAINS = [
    "cdn.tailwindcss.com",
    "fonts.googleapis.com",
    "fonts.gstatic.com",
    "placehold.co",
    "images.unsplash.com",
    "unpkg.com",
    "cdnjs.cloudflare.com",
    "fal.media",           # fal.ai generated images
    "v3.fal.media",        # fal.ai generated images (v3)
]

# Tag HTML pericolosi da rimuovere
# NOTA: "script" NON e' in lista perche' serve per Tailwind CDN e vanilla JS menu.
# Gli script vengono filtrati selettivamente in sanitize_output().
DANGEROUS_TAGS = ["iframe", "object", "embed", "applet"]

# Event handler inline da rimuovere
EVENT_HANDLERS = [
    "onclick", "ondblclick", "onmousedown", "onmouseup", "onmouseover",
    "onmousemove", "onmouseout", "onkeypress", "onkeydown", "onkeyup",
    "onfocus", "onblur", "onsubmit", "onreset", "onselect", "onchange",
    "onload", "onerror", "onabort", "onresize", "onscroll", "onunload",
    "onbeforeunload", "onhashchange", "onpopstate", "onstorage",
    "ondrag", "ondragend", "ondragenter", "ondragleave", "ondragover",
    "ondragstart", "ondrop", "oncontextmenu",
]

MAX_BUSINESS_NAME_LENGTH = 200
MAX_DESCRIPTION_LENGTH = 2000
MAX_SECTION_NAME_LENGTH = 50


def sanitize_input(
    business_name: str,
    business_description: str,
    sections: Optional[List[str]] = None,
) -> Tuple[str, str, List[str]]:
    """
    Sanitizza input utente prima di inviarli all'AI.
    Ritorna (name, description, sections) sanitizzati.
    Lancia ValueError se input sospetto.
    """
    # Controlla prompt injection nel nome
    name_lower = business_name.lower()
    for pattern in INJECTION_PATTERNS:
        if re.search(pattern, name_lower, re.IGNORECASE):
            logger.warning(f"Prompt injection detected in business_name: {business_name[:100]}")
            raise ValueError("Input non valido: contenuto sospetto rilevato nel nome")

    # Controlla prompt injection nella descrizione
    desc_lower = business_description.lower()
    for pattern in INJECTION_PATTERNS:
        if re.search(pattern, desc_lower, re.IGNORECASE):
            logger.warning(f"Prompt injection detected in description: {business_description[:100]}")
            raise ValueError("Input non valido: contenuto sospetto rilevato nella descrizione")

    # Tronca lunghezze
    business_name = business_name.strip()[:MAX_BUSINESS_NAME_LENGTH]
    business_description = business_description.strip()[:MAX_DESCRIPTION_LENGTH]

    # Sanitizza sezioni
    if sections:
        sections = [s.strip()[:MAX_SECTION_NAME_LENGTH] for s in sections if s.strip()]

    return business_name, business_description, sections or []


# Script src consentiti (CDN whitelist)
ALLOWED_SCRIPT_SRCS = [
    "cdn.tailwindcss.com",
    "unpkg.com",
    "cdnjs.cloudflare.com",
    "fonts.googleapis.com",
]


def _sanitize_scripts(html: str) -> str:
    """
    Filtra script tag selettivamente:
    - Mantieni <script src="..."> da CDN whitelistate
    - Mantieni <script>...</script> inline (vanilla JS per menu toggle, smooth scroll)
    - Rimuovi script con src da domini non consentiti
    """
    import re as _re

    def _check_script(match):
        tag = match.group(0)
        # Script con src
        src_match = _re.search(r'src\s*=\s*["\']([^"\']+)["\']', tag)
        if src_match:
            src_url = src_match.group(1)
            # Controlla se il dominio e' nella whitelist
            for allowed in ALLOWED_SCRIPT_SRCS:
                if allowed in src_url:
                    return tag  # Mantieni
            logger.warning(f"Blocked script src: {src_url}")
            return ""  # Rimuovi
        # Script inline (senza src) - mantieni per vanilla JS
        return tag

    html = _re.sub(
        r'<script[^>]*>.*?</script>',
        _check_script,
        html,
        flags=_re.DOTALL | _re.IGNORECASE,
    )
    return html


def sanitize_output(html: str) -> str:
    """
    Sanitizza HTML generato dall'AI.
    Rimuove script, iframe, event handler inline, domini non consentiti.
    """
    if not html:
        return html

    # Rimuovi script pericolosi ma mantieni Tailwind CDN e inline vanilla JS
    html = _sanitize_scripts(html)

    # Rimuovi tag pericolosi (iframe, object, embed, applet)
    tags_to_remove = DANGEROUS_TAGS
    for tag in tags_to_remove:
        # Rimuovi tag apertura e chiusura con contenuto
        html = re.sub(
            rf'<{tag}[^>]*>.*?</{tag}>',
            '',
            html,
            flags=re.DOTALL | re.IGNORECASE
        )
        # Rimuovi tag self-closing
        html = re.sub(
            rf'<{tag}[^>]*/?>',
            '',
            html,
            flags=re.IGNORECASE
        )

    # Rimuovi event handler inline
    for handler in EVENT_HANDLERS:
        html = re.sub(
            rf'\s{handler}\s*=\s*["\'][^"\']*["\']',
            '',
            html,
            flags=re.IGNORECASE
        )
        html = re.sub(
            rf'\s{handler}\s*=\s*\S+',
            '',
            html,
            flags=re.IGNORECASE
        )

    # Rimuovi javascript: URLs
    html = re.sub(
        r'href\s*=\s*["\']javascript:[^"\']*["\']',
        'href="#"',
        html,
        flags=re.IGNORECASE
    )

    # Controlla domini esterni nelle src/href (non bloccare, solo log)
    external_urls = re.findall(r'(?:src|href)\s*=\s*["\']https?://([^/\s"\']+)', html)
    for domain in external_urls:
        if not any(domain.endswith(allowed) for allowed in ALLOWED_DOMAINS):
            logger.info(f"External domain in generated HTML: {domain}")

    # Assicurati che ci sia struttura HTML minima
    if "<!DOCTYPE" not in html.upper() and "<html" not in html.lower():
        html = f"<!DOCTYPE html>\n<html lang=\"it\">\n<head><meta charset=\"UTF-8\"><meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\"></head>\n<body>\n{html}\n</body>\n</html>"

    return html


def sanitize_refine_input(message: str) -> str:
    """Sanitizza messaggio di chat/refine."""
    message = message.strip()
    if len(message) > 1000:
        message = message[:1000]

    msg_lower = message.lower()
    for pattern in INJECTION_PATTERNS:
        if re.search(pattern, msg_lower, re.IGNORECASE):
            logger.warning(f"Prompt injection in refine message: {message[:100]}")
            raise ValueError("Messaggio non valido: contenuto sospetto rilevato")

    return message
