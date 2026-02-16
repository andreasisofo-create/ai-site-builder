"""
Knowledge Base per Ads AI - benchmark, template verticali, problem solving e articoli.
Ported from Node.js: backend/modules/knowledge.js
"""

import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

DATA_DIR = Path(__file__).resolve().parent.parent / "data"


class AdsKnowledgeBase:
    """Knowledge base con benchmark, template, problem solving e articoli per campagne ads."""

    def __init__(self) -> None:
        self.benchmarks: Dict[str, Any] = self._load_json("ads_benchmarks.json")
        self.templates: Dict[str, Any] = self._load_json("ads_templates.json")
        self.problems: List[Dict[str, Any]] = self._load_json("ads_problemsolving.json")
        self.articles: List[Dict[str, Any]] = self._load_json("ads_knowledge.json")

    def _load_json(self, filename: str) -> Any:
        filepath = DATA_DIR / filename
        try:
            return json.loads(filepath.read_text(encoding="utf-8"))
        except Exception as e:
            logger.error("Errore caricamento %s: %s", filename, e)
            return {} if filename.endswith("json") and not filename.startswith("ads_problem") and not filename.startswith("ads_knowledge") else []

    # --- Benchmark ---

    def get_benchmark(self, sector: str) -> Optional[Dict[str, Any]]:
        return self.benchmarks.get(sector) or self.benchmarks.get("default")

    def get_budget_min(self, sector: str) -> int:
        benchmark = self.get_benchmark(sector)
        return benchmark.get("recommendedBudget", 300) if benchmark else 300

    def get_platform_split(self, sector: str) -> Dict[str, int]:
        benchmark = self.get_benchmark(sector)
        return benchmark.get("platformSplit", {"google": 50, "meta": 50}) if benchmark else {"google": 50, "meta": 50}

    # --- Template verticali ---

    def get_template(self, sector: str) -> Optional[Dict[str, Any]]:
        return self.templates.get(sector) or self.templates.get("default")

    def get_keywords(self, sector: str) -> List[str]:
        template = self.get_template(sector)
        return template.get("keyword", []) if template else []

    def get_negative_keywords(self, sector: str) -> List[str]:
        template = self.get_template(sector)
        return template.get("keyword_negative", []) if template else []

    def get_ad_copy(self, sector: str) -> Optional[Dict[str, Any]]:
        template = self.get_template(sector)
        return template.get("ad_copy") if template else None

    def get_targeting(self, sector: str) -> Optional[Dict[str, Any]]:
        template = self.get_template(sector)
        return template.get("targeting") if template else None

    # --- Problem solving ---

    def get_problem_solution(self, symptom: str) -> Optional[Dict[str, Any]]:
        symptom_lower = symptom.lower()
        for p in self.problems:
            if (
                symptom_lower in p.get("sintomo", "").lower()
                or symptom_lower in p.get("diagnosi", "").lower()
            ):
                return p
        return None

    def get_all_problems(self) -> List[Dict[str, Any]]:
        return self.problems

    def get_problems_by_sector(self, sector: str) -> List[Dict[str, Any]]:
        return [
            p
            for p in self.problems
            if "tutti" in p.get("settori", []) or sector in p.get("settori", [])
        ]

    # --- Articoli ---

    def search_articles(self, query: str) -> List[Dict[str, Any]]:
        query_lower = query.lower()
        return [
            a
            for a in self.articles
            if query_lower in a.get("titolo", "").lower()
            or query_lower in a.get("contenuto", "").lower()
            or any(query_lower in t.lower() for t in a.get("tags", []))
        ]

    def get_articles_by_category(self, category: str) -> List[Dict[str, Any]]:
        return [a for a in self.articles if a.get("categoria") == category]

    # --- Utility ---

    def get_sectors(self) -> List[str]:
        return [s for s in self.benchmarks if s != "default"]

    def suggest_sector(self, description: str) -> str:
        desc_lower = description.lower()
        keyword_map: Dict[str, List[str]] = {
            "ristorante": ["ristorante", "pizzeria", "trattoria", "osteria", "food", "cucina"],
            "ecommerce": ["shop", "ecommerce", "e-commerce", "negozio online", "vendita online"],
            "studio_legale": ["avvocato", "legale", "studio legale", "diritto", "causa"],
            "commercialista": ["commercialista", "fiscale", "contabile", "730", "dichiarazione"],
            "palestra": ["palestra", "fitness", "gym", "allenamento", "bodybuilding"],
            "immobiliare": ["immobiliare", "agenzia", "casa", "appartamento", "vendita"],
            "estetica": ["estetica", "bellezza", "massaggi", "trattamenti", "spa"],
            "parrucchiere": ["parrucchiere", "hair", "taglio", "capelli", "barbiere"],
            "edile": ["edile", "costruzioni", "ristrutturazione", "impresa", "edilizia"],
            "fotografo": ["fotografo", "foto", "shooting", "matrimonio", "ritratto"],
            "creativo": ["design", "grafica", "logo", "brand", "creativo", "studio"],
            "startup": ["startup", "app", "innovazione", "tech", "software"],
            "saas": ["saas", "software", "cloud", "piattaforma", "tool"],
        }
        for sector, words in keyword_map.items():
            if any(w in desc_lower for w in words):
                return sector
        return "default"

    def calculate_recommended_budget(self, sector: str, days: int = 30) -> Dict[str, Any]:
        benchmark = self.get_benchmark(sector)
        recommended = benchmark.get("recommendedBudget", 350) if benchmark else 350
        daily = round(recommended / 30)
        return {
            "daily": daily,
            "monthly": recommended,
            "period": days,
            "total": round(daily * days),
        }

    def generate_campaign_tips(self, sector: str, platform: str) -> Dict[str, Any]:
        benchmark = self.get_benchmark(sector)
        platform_data = benchmark.get(platform, {}) if benchmark else {}
        return {
            "keywords": self.get_keywords(sector),
            "negativeKeywords": self.get_negative_keywords(sector),
            "adCopy": self.get_ad_copy(sector),
            "targeting": self.get_targeting(sector),
            "budget": {
                "min": platform_data.get("budgetMin", 150),
                "recommended": benchmark.get("recommendedBudget", 350) if benchmark else 350,
                "cpc": platform_data.get("cpc"),
            },
            "bestPractices": [
                a["titolo"] for a in self.get_articles_by_category(platform)
            ],
        }


ads_knowledge = AdsKnowledgeBase()
