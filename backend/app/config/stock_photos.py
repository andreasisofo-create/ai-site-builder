"""Stock photo pools by business category.

High-quality Unsplash photo URLs organized by category and section type.
These replace placeholder grey boxes when no user photos or AI-generated
images are available.
"""

import random
from typing import Dict, List


# High-quality Unsplash photo pools (by business category)
_UNSPLASH_PHOTOS: Dict[str, Dict[str, List[str]]] = {
    "restaurant": {
        "hero": [
            "https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?w=1200&h=800&fit=crop",
            "https://images.unsplash.com/photo-1552566626-52f8b828add9?w=1200&h=800&fit=crop",
            "https://images.unsplash.com/photo-1414235077428-338989a2e8c0?w=1200&h=800&fit=crop",
        ],
        "gallery": [
            "https://images.unsplash.com/photo-1504674900247-0877df9cc836?w=600&h=400&fit=crop",
            "https://images.unsplash.com/photo-1476224203421-9ac39bcb3327?w=600&h=400&fit=crop",
            "https://images.unsplash.com/photo-1540189549336-e6e99c3679fe?w=600&h=400&fit=crop",
            "https://images.unsplash.com/photo-1565299624946-b28f40a0ae38?w=600&h=400&fit=crop",
            "https://images.unsplash.com/photo-1482049016688-2d3e1b311543?w=600&h=400&fit=crop",
            "https://images.unsplash.com/photo-1567620905732-2d1ec7ab7445?w=600&h=400&fit=crop",
            "https://images.unsplash.com/photo-1555396273-367ea4eb4db5?w=600&h=400&fit=crop",
            "https://images.unsplash.com/photo-1414235077428-338989a2e8c0?w=600&h=400&fit=crop",
            "https://images.unsplash.com/photo-1551218808-94e220e084d2?w=600&h=400&fit=crop",
        ],
        "about": [
            "https://images.unsplash.com/photo-1600891964092-4316c288032e?w=800&h=600&fit=crop",
            "https://images.unsplash.com/photo-1559339352-11d035aa65de?w=800&h=600&fit=crop",
        ],
        "team": [
            "https://images.unsplash.com/photo-1577219491135-ce391730fb2c?w=300&h=300&fit=crop",
            "https://images.unsplash.com/photo-1581299894007-aaa50297cf16?w=300&h=300&fit=crop",
            "https://images.unsplash.com/photo-1583394838336-acd977736f90?w=300&h=300&fit=crop",
        ],
    },
    "saas": {
        "hero": [
            "https://images.unsplash.com/photo-1460925895917-afdab827c52f?w=1200&h=800&fit=crop",
            "https://images.unsplash.com/photo-1551434678-e076c223a692?w=1200&h=800&fit=crop",
            "https://images.unsplash.com/photo-1498050108023-c5249f4df085?w=1200&h=800&fit=crop",
        ],
        "gallery": [
            "https://images.unsplash.com/photo-1517694712202-14dd9538aa97?w=600&h=400&fit=crop",
            "https://images.unsplash.com/photo-1555066931-4365d14bab8c?w=600&h=400&fit=crop",
            "https://images.unsplash.com/photo-1461749280684-dccba630e2f6?w=600&h=400&fit=crop",
            "https://images.unsplash.com/photo-1504868584819-f8e8b4b6d7e3?w=600&h=400&fit=crop",
            "https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=600&h=400&fit=crop",
            "https://images.unsplash.com/photo-1519389950473-47ba0277781c?w=600&h=400&fit=crop",
            "https://images.unsplash.com/photo-1558494949-ef010cbdcc31?w=600&h=400&fit=crop",
            "https://images.unsplash.com/photo-1573164713988-8665fc963095?w=600&h=400&fit=crop",
            "https://images.unsplash.com/photo-1550751827-4bd374c3f58b?w=600&h=400&fit=crop",
        ],
        "about": [
            "https://images.unsplash.com/photo-1522071820081-009f0129c71c?w=800&h=600&fit=crop",
        ],
        "team": [
            "https://images.unsplash.com/photo-1560250097-0b93528c311a?w=300&h=300&fit=crop",
            "https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?w=300&h=300&fit=crop",
            "https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=300&h=300&fit=crop",
        ],
    },
    "portfolio": {
        "hero": [
            "https://images.unsplash.com/photo-1558655146-9f40138edfeb?w=1200&h=800&fit=crop",
            "https://images.unsplash.com/photo-1561070791-2526d30994b5?w=1200&h=800&fit=crop",
            "https://images.unsplash.com/photo-1545665277-5937489d95eb?w=1200&h=800&fit=crop",
        ],
        "gallery": [
            "https://images.unsplash.com/photo-1561070791-2526d30994b5?w=600&h=400&fit=crop",
            "https://images.unsplash.com/photo-1558655146-d09347e92766?w=600&h=400&fit=crop",
            "https://images.unsplash.com/photo-1572044162444-ad60f128bdea?w=600&h=400&fit=crop",
            "https://images.unsplash.com/photo-1586717791821-3f44a563fa4c?w=600&h=400&fit=crop",
            "https://images.unsplash.com/photo-1626785774573-4b799315345d?w=600&h=400&fit=crop",
            "https://images.unsplash.com/photo-1611532736597-de2d4265fba3?w=600&h=400&fit=crop",
            "https://images.unsplash.com/photo-1545235617-9465d2a55698?w=600&h=400&fit=crop",
            "https://images.unsplash.com/photo-1507238691740-187a5b1d37b8?w=600&h=400&fit=crop",
            "https://images.unsplash.com/photo-1559028012-481c04fa702d?w=600&h=400&fit=crop",
        ],
        "about": [
            "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=800&h=600&fit=crop",
        ],
        "team": [
            "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=300&h=300&fit=crop",
            "https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=300&h=300&fit=crop",
            "https://images.unsplash.com/photo-1438761681033-6461ffad8d80?w=300&h=300&fit=crop",
        ],
    },
    "ecommerce": {
        "hero": [
            "https://images.unsplash.com/photo-1441986300917-64674bd600d8?w=1200&h=800&fit=crop",
            "https://images.unsplash.com/photo-1472851294608-062f824d29cc?w=1200&h=800&fit=crop",
            "https://images.unsplash.com/photo-1556742049-0cfed4f6a45d?w=1200&h=800&fit=crop",
        ],
        "gallery": [
            "https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=600&h=400&fit=crop",
            "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=600&h=400&fit=crop",
            "https://images.unsplash.com/photo-1526170375885-4d8ecf77b99f?w=600&h=400&fit=crop",
            "https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=600&h=400&fit=crop",
            "https://images.unsplash.com/photo-1560343090-f0409e92791a?w=600&h=400&fit=crop",
            "https://images.unsplash.com/photo-1491553895911-0055eca6402d?w=600&h=400&fit=crop",
            "https://images.unsplash.com/photo-1553062407-98eeb64c6a62?w=600&h=400&fit=crop",
            "https://images.unsplash.com/photo-1572635196237-14b3f281503f?w=600&h=400&fit=crop",
            "https://images.unsplash.com/photo-1585386959984-a4155224a1ad?w=600&h=400&fit=crop",
        ],
        "about": [
            "https://images.unsplash.com/photo-1556742111-a301076d9d18?w=800&h=600&fit=crop",
        ],
        "team": [
            "https://images.unsplash.com/photo-1560250097-0b93528c311a?w=300&h=300&fit=crop",
            "https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?w=300&h=300&fit=crop",
            "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=300&h=300&fit=crop",
        ],
    },
    "business": {
        "hero": [
            "https://images.unsplash.com/photo-1497366216548-37526070297c?w=1200&h=800&fit=crop",
            "https://images.unsplash.com/photo-1497215842964-222b430dc094?w=1200&h=800&fit=crop",
            "https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?w=1200&h=800&fit=crop",
        ],
        "gallery": [
            "https://images.unsplash.com/photo-1497366811353-6870744d04b2?w=600&h=400&fit=crop",
            "https://images.unsplash.com/photo-1497215728101-856f4ea42174?w=600&h=400&fit=crop",
            "https://images.unsplash.com/photo-1454165804606-c3d57bc86b40?w=600&h=400&fit=crop",
            "https://images.unsplash.com/photo-1521737711867-e3b97375f902?w=600&h=400&fit=crop",
            "https://images.unsplash.com/photo-1552664730-d307ca884978?w=600&h=400&fit=crop",
            "https://images.unsplash.com/photo-1553877522-43269d4ea984?w=600&h=400&fit=crop",
            "https://images.unsplash.com/photo-1556761175-4b46a572b786?w=600&h=400&fit=crop",
            "https://images.unsplash.com/photo-1542744173-8e7e53415bb0?w=600&h=400&fit=crop",
            "https://images.unsplash.com/photo-1559136555-9303baea8ebd?w=600&h=400&fit=crop",
        ],
        "about": [
            "https://images.unsplash.com/photo-1521737604893-d14cc237f11d?w=800&h=600&fit=crop",
        ],
        "team": [
            "https://images.unsplash.com/photo-1560250097-0b93528c311a?w=300&h=300&fit=crop",
            "https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?w=300&h=300&fit=crop",
            "https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=300&h=300&fit=crop",
        ],
    },
    "blog": {
        "hero": [
            "https://images.unsplash.com/photo-1499750310107-5fef28a66643?w=1200&h=800&fit=crop",
            "https://images.unsplash.com/photo-1432821596592-e2c18b78144f?w=1200&h=800&fit=crop",
        ],
        "gallery": [
            "https://images.unsplash.com/photo-1488190211105-8b0e65b80b4e?w=600&h=400&fit=crop",
            "https://images.unsplash.com/photo-1501504905252-473c47e087f8?w=600&h=400&fit=crop",
            "https://images.unsplash.com/photo-1455390582262-044cdead277a?w=600&h=400&fit=crop",
            "https://images.unsplash.com/photo-1519389950473-47ba0277781c?w=600&h=400&fit=crop",
            "https://images.unsplash.com/photo-1486312338219-ce68d2c6f44d?w=600&h=400&fit=crop",
            "https://images.unsplash.com/photo-1499951360447-b19be8fe80f5?w=600&h=400&fit=crop",
            "https://images.unsplash.com/photo-1434030216411-0b793f4b4173?w=600&h=400&fit=crop",
            "https://images.unsplash.com/photo-1457369804613-52c61a468e7d?w=600&h=400&fit=crop",
            "https://images.unsplash.com/photo-1471107340929-a87cd0f5b5f3?w=600&h=400&fit=crop",
        ],
        "about": [
            "https://images.unsplash.com/photo-1522202176988-66273c2fd55f?w=800&h=600&fit=crop",
        ],
        "team": [
            "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=300&h=300&fit=crop",
            "https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=300&h=300&fit=crop",
            "https://images.unsplash.com/photo-1438761681033-6461ffad8d80?w=300&h=300&fit=crop",
        ],
    },
    "event": {
        "hero": [
            "https://images.unsplash.com/photo-1540575467063-178a50c2df87?w=1200&h=800&fit=crop",
            "https://images.unsplash.com/photo-1505236858219-8359eb29e329?w=1200&h=800&fit=crop",
        ],
        "gallery": [
            "https://images.unsplash.com/photo-1492684223066-81342ee5ff30?w=600&h=400&fit=crop",
            "https://images.unsplash.com/photo-1501281668745-f7f57925c3b4?w=600&h=400&fit=crop",
            "https://images.unsplash.com/photo-1475721027785-f74eccf877e2?w=600&h=400&fit=crop",
            "https://images.unsplash.com/photo-1464366400600-7168b8af9bc3?w=600&h=400&fit=crop",
            "https://images.unsplash.com/photo-1429962714451-bb934ecdc4ec?w=600&h=400&fit=crop",
            "https://images.unsplash.com/photo-1514525253161-7a46d19cd819?w=600&h=400&fit=crop",
            "https://images.unsplash.com/photo-1533174072545-7a4b6ad7a6c3?w=600&h=400&fit=crop",
            "https://images.unsplash.com/photo-1470229722913-7c0e2dbbafd3?w=600&h=400&fit=crop",
            "https://images.unsplash.com/photo-1459749411175-04bf5292ceea?w=600&h=400&fit=crop",
        ],
        "about": [
            "https://images.unsplash.com/photo-1511795409834-ef04bbd61622?w=800&h=600&fit=crop",
        ],
        "team": [
            "https://images.unsplash.com/photo-1560250097-0b93528c311a?w=300&h=300&fit=crop",
            "https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?w=300&h=300&fit=crop",
            "https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=300&h=300&fit=crop",
        ],
    },
}

# Fallback for unknown categories
_UNSPLASH_PHOTOS["default"] = _UNSPLASH_PHOTOS["business"]


def get_stock_photos(category: str) -> Dict[str, List[str]]:
    """Get stock photo URLs for a business category. Picks from pool with shuffling."""
    # Detect category from template_style_id prefix
    for cat in _UNSPLASH_PHOTOS:
        if cat != "default" and category and category.startswith(cat):
            photos = _UNSPLASH_PHOTOS[cat]
            break
    else:
        photos = _UNSPLASH_PHOTOS["default"]
    # Return shuffled copies so each generation gets different photos
    return {k: random.sample(v, len(v)) for k, v in photos.items()}
