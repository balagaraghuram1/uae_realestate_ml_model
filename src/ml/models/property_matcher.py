 """Property matching algorithm for buyer preferences."""
import numpy as np
from typing import Dict, List

class PropertyMatcher:
    """Match properties to buyer preferences using weighted scoring."""

    DEFAULT_WEIGHTS = {
        "budget": 0.30, "location": 0.25, "size": 0.20,
        "bedrooms": 0.15, "type": 0.10,
    }

    def __init__(self, weights: Dict[str, float] = None):
        self.weights = weights or self.DEFAULT_WEIGHTS

    def match(self, preferences: Dict, properties: List[Dict], top_n: int = 10) -> List[Dict]:
        """Find best matching properties for buyer preferences."""
        scored = []
        for prop in properties:
            score = self._compute_match_score(preferences, prop)
            scored.append({**prop, "match_score": round(score, 2)})
        scored.sort(key=lambda x: x["match_score"], reverse=True)
        return scored[:top_n]

    def _compute_match_score(self, prefs: Dict, prop: Dict) -> float:
        """Compute match score between preferences and a property."""
        score = 0
        if "budget" in prefs and "price_aed" in prop:
            budget_diff = abs(prefs["budget"] - prop["price_aed"]) / prefs["budget"]
            score += self.weights["budget"] * max(0, 1 - budget_diff)
        if "area" in prefs and "area" in prop:
            score += self.weights["location"] * (1.0 if prefs["area"] == prop["area"] else 0.2)
        if "min_size" in prefs and "size_sqft" in prop:
            if prop["size_sqft"] >= prefs["min_size"]:
                score += self.weights["size"]
        if "bedrooms" in prefs and "bedrooms" in prop:
            score += self.weights["bedrooms"] * (1.0 if prefs["bedrooms"] == prop["bedrooms"] else 0.3)
        if "property_type" in prefs and "property_type" in prop:
            score += self.weights["type"] * (1.0 if prefs["property_type"] == prop["property_type"] else 0.1)
        return score
