"""
Outfit scorer — picks the best outfit combination from a user's wardrobe
given weather context, occasion, and basic color harmony rules.

Phase 1: rule-based scoring (fast, no GPU needed).
Phase 2: will be replaced by the learned ranking model.
"""

from __future__ import annotations
import logging
import random
from itertools import product

from app.services.weather import weather_item_score, WeatherContext

logger = logging.getLogger(__name__)

# Occasion → required roles
OCCASION_REQUIRED_ROLES = {
    "casual":       ["top", "bottom", "footwear"],
    "work":         ["top", "bottom", "footwear"],
    "date":         ["top", "bottom", "footwear"],
    "formal":       ["top", "bottom", "footwear"],
    "sport":        ["top", "bottom", "footwear"],
    "full_outfit":  ["full_outfit", "footwear"],   # dress / jumpsuit
}

# Occasion → ideal formality range
OCCASION_FORMALITY = {
    "casual":  (0.0, 0.45),
    "work":    (0.4, 0.75),
    "date":    (0.35, 0.7),
    "formal":  (0.65, 1.0),
    "sport":   (0.0, 0.25),
}

# Basic color harmony rules (hue compatibility on a 0-360 wheel)
# Two colors are "harmonious" if their hue difference falls in these ranges
HARMONY_RANGES = [
    (0, 30),     # analogous
    (150, 210),  # complementary ± 30
    (350, 360),  # wrap-around analogous
]

NEUTRAL_COLORS = {"white", "black", "gray", "cream", "beige", "ivory",
                  "charcoal", "silver", "tan", "camel"}


def _colors_harmonious(colors_a: list[dict], colors_b: list[dict]) -> bool:
    """True if the dominant colors of two items are compatible."""
    # Neutrals match everything
    def is_neutral(colors):
        return any(c.get("name", "") in NEUTRAL_COLORS for c in colors)

    if is_neutral(colors_a) or is_neutral(colors_b):
        return True

    # Simple: check if any pair of dominant colors are analogous/complementary
    # (In Phase 2 this becomes a learned model)
    return True   # permissive for now; add real hue math in Phase 2


def _occasion_score(item: dict, occasion: str) -> float:
    """How well an item's formality matches the occasion."""
    lo, hi = OCCASION_FORMALITY.get(occasion, (0.0, 1.0))
    formality = item.get("formality_score", 0.5)
    if lo <= formality <= hi:
        return 1.0
    dist = min(abs(formality - lo), abs(formality - hi))
    return max(0.0, 1.0 - dist * 2)


def score_outfit(items: list[dict], weather: WeatherContext, occasion: str) -> float:
    """
    Score an outfit (list of wardrobe item dicts).
    Returns 0–1.
    """
    if not items:
        return 0.0

    # Weather score (average across items)
    weather_scores = [weather_item_score(i, weather) for i in items]
    weather_avg = sum(weather_scores) / len(weather_scores)

    # Occasion score (average across items)
    occasion_scores = [_occasion_score(i, occasion) for i in items]
    occasion_avg = sum(occasion_scores) / len(occasion_scores)

    # Color harmony (all pairs)
    harmony = 1.0
    for i in range(len(items)):
        for j in range(i + 1, len(items)):
            if not _colors_harmonious(items[i].get("colors", []), items[j].get("colors", [])):
                harmony *= 0.6

    # Combine
    score = (
        weather_avg * 0.45
        + occasion_avg * 0.35
        + harmony * 0.20
    )
    return round(score, 4)


def pick_best_outfit(
    wardrobe_items: list[dict],
    weather: WeatherContext,
    occasion: str = "casual",
    top_n: int = 3,
) -> list[list[dict]]:
    """
    Given all wardrobe items, return the top_n best outfit combinations.

    Each item dict must have: id, category, role, colors, formality_score,
    warmth_score, image_url, attributes.
    """
    # Group by role
    by_role: dict[str, list[dict]] = {}
    for item in wardrobe_items:
        role = item.get("role", "other")
        by_role.setdefault(role, []).append(item)

    # Check for full_outfit (dress/jumpsuit) first
    full_outfits = by_role.get("full_outfit", [])
    footwear = by_role.get("footwear", [{"id": "none", "role": "footwear",
                                           "category": "barefoot", "colors": [],
                                           "formality_score": 0.3, "warmth_score": 0.1,
                                           "image_url": "", "attributes": {}}])

    tops = by_role.get("top", [])
    bottoms = by_role.get("bottom", [])

    candidates: list[tuple[float, list[dict]]] = []

    # Option A: top + bottom + shoes
    if tops and bottoms:
        combos = list(product(tops, bottoms, footwear))
        # Sample if too many
        if len(combos) > 200:
            combos = random.sample(combos, 200)
        for combo in combos:
            outfit = list(combo)
            sc = score_outfit(outfit, weather, occasion)
            candidates.append((sc, outfit))

    # Option B: full outfit + shoes
    for fo in full_outfits:
        for shoe in footwear:
            outfit = [fo, shoe]
            sc = score_outfit(outfit, weather, occasion)
            candidates.append((sc, outfit))

    if not candidates:
        logger.warning("No outfit candidates found — wardrobe may be empty")
        return []

    candidates.sort(key=lambda x: x[0], reverse=True)
    return [outfit for _, outfit in candidates[:top_n]]
