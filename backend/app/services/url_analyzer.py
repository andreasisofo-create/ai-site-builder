"""
URL Analyzer - Fetches and analyzes reference websites to extract design cues.
Uses httpx for async HTTP requests and basic HTML parsing.
"""
import logging
import re
from typing import Dict, List, Optional

import httpx

logger = logging.getLogger(__name__)


async def analyze_reference_url(url: str, timeout: float = 25.0) -> Optional[Dict]:
    """
    Fetch a URL and extract design-relevant information.
    Returns a dict with: title, description, colors, fonts, style_cues, content_summary
    Returns None if the URL is invalid or the fetch fails.
    """
    if not url or not url.startswith(("http://", "https://")):
        return None

    try:
        async with httpx.AsyncClient(follow_redirects=True, timeout=timeout) as client:
            response = await client.get(url, headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.9,it;q=0.8",
            })
            response.raise_for_status()
            html = response.text[:50000]  # Limit to first 50KB
    except Exception as e:
        logger.warning(f"[URLAnalyzer] Failed to fetch {url}: {e}")
        return None

    result: Dict = {
        "url": url,
        "title": "",
        "description": "",
        "colors": [],
        "fonts": [],
        "style_cues": "",
        "content_summary": "",
    }

    # --- Extract title ---
    title_match = re.search(r'<title[^>]*>(.*?)</title>', html, re.IGNORECASE | re.DOTALL)
    if title_match:
        result["title"] = title_match.group(1).strip()[:200]

    # --- Extract meta description ---
    desc_match = re.search(
        r'<meta[^>]*name=["\']description["\'][^>]*content=["\']([^"\']*)',
        html, re.IGNORECASE,
    )
    if desc_match:
        result["description"] = desc_match.group(1).strip()[:300]

    # --- Extract colors from CSS (hex codes) ---
    hex_colors = re.findall(r'#(?:[0-9a-fA-F]{6}|[0-9a-fA-F]{3})\b', html)
    # Count frequency and filter out very common/neutral colors
    common = {
        '#000000', '#ffffff', '#000', '#fff',
        '#333', '#333333', '#666', '#666666',
        '#999', '#999999', '#ccc', '#cccccc',
    }
    color_freq: Dict[str, int] = {}
    for c in hex_colors:
        c_lower = c.lower()
        if c_lower not in common and len(c_lower) == 7:  # Only full 6-digit hex
            color_freq[c_lower] = color_freq.get(c_lower, 0) + 1
    top_colors = sorted(color_freq.items(), key=lambda x: -x[1])[:5]
    result["colors"] = [c for c, _ in top_colors]

    # --- Extract font families from inline/embedded CSS ---
    font_matches = re.findall(r'font-family\s*:\s*["\']?([^;"\'}\n]+)', html, re.IGNORECASE)
    fonts: set = set()
    generic_families = {
        'inherit', 'sans-serif', 'serif', 'monospace',
        'system-ui', '-apple-system', 'cursive', 'fantasy',
    }
    for f in font_matches:
        font_name = f.split(',')[0].strip().strip("'\"")
        if font_name and font_name.lower() not in generic_families:
            fonts.add(font_name)

    # --- Extract Google Fonts from <link> tags ---
    gfont_matches = re.findall(r'fonts\.googleapis\.com/css2?\?family=([^"&\s]+)', html)
    for gf in gfont_matches:
        font_name = gf.replace('+', ' ').split(':')[0]
        if font_name:
            fonts.add(font_name)
    result["fonts"] = list(fonts)[:5]

    # --- Extract visible text for content analysis ---
    # Remove script and style blocks first
    clean_html = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL | re.IGNORECASE)
    clean_html = re.sub(r'<style[^>]*>.*?</style>', '', clean_html, flags=re.DOTALL | re.IGNORECASE)

    headings = re.findall(r'<h[1-3][^>]*>(.*?)</h[1-3]>', clean_html, re.IGNORECASE | re.DOTALL)
    heading_texts = [re.sub(r'<[^>]+>', '', h).strip() for h in headings[:10]]
    heading_texts = [h for h in heading_texts if h and len(h) > 2]

    paragraphs = re.findall(r'<p[^>]*>(.*?)</p>', clean_html, re.IGNORECASE | re.DOTALL)
    para_texts = [re.sub(r'<[^>]+>', '', p).strip() for p in paragraphs[:5]]
    para_texts = [p for p in para_texts if p and len(p) > 20]

    # Build content summary
    summary_parts: List[str] = []
    if heading_texts:
        summary_parts.append("Headings: " + " | ".join(heading_texts[:5]))
    if para_texts:
        summary_parts.append("Key text: " + " | ".join([p[:100] for p in para_texts[:3]]))
    result["content_summary"] = "\n".join(summary_parts)[:500]

    # --- Build style cues ---
    style_parts: List[str] = []
    if result["colors"]:
        style_parts.append(f"Color palette: {', '.join(result['colors'])}")
    if result["fonts"]:
        style_parts.append(f"Fonts: {', '.join(result['fonts'])}")
    if result["title"]:
        style_parts.append(f"Site: {result['title']}")

    # Detect dark/light theme heuristic
    if html.count('dark') > html.count('light') or '#0' in ''.join(result["colors"][:2]):
        style_parts.append("Appears to use dark theme")

    result["style_cues"] = "\n".join(style_parts)[:400]

    return result


def format_analysis_for_prompt(analysis: Optional[Dict]) -> str:
    """Format the URL analysis into a string suitable for AI prompt injection."""
    if not analysis:
        return ""

    parts = [f"REFERENCE WEBSITE ANALYSIS ({analysis.get('url', '')}):"]

    if analysis.get("title"):
        parts.append(f"- Site: {analysis['title']}")
    if analysis.get("description"):
        parts.append(f"- Description: {analysis['description'][:200]}")
    if analysis.get("colors"):
        parts.append(f"- Colors found: {', '.join(analysis['colors'])}")
    if analysis.get("fonts"):
        parts.append(f"- Fonts found: {', '.join(analysis['fonts'])}")
    if analysis.get("content_summary"):
        parts.append(f"- Content: {analysis['content_summary'][:200]}")
    if analysis.get("style_cues"):
        parts.append(f"- Style: {analysis['style_cues'][:200]}")

    parts.append("Use this reference site's style, colors, and tone as inspiration.")

    return "\n".join(parts)
