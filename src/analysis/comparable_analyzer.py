"""Comparable property analysis for property valuation."""
import numpy as np
import pandas as pd
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)

class ComparableAnalyzer:
    """Find and analyze comparable properties for valuation."""

    def __init__(self):
        self.weights = {
            "size": 0.25, "bedrooms": 0.20, "bathrooms": 0.10,
            "property_type": 0.15, "area": 0.20, "age": 0.10,
        }

    def find_comparables(self, target: Dict, candidates: pd.DataFrame,
                         n: int = 5) -> List[Dict]:
        """Find the most comparable properties."""
        scores = []
        for idx, row in candidates.iterrows():
            score = self._compute_similarity(target, row.to_dict())
            scores.append({"index": idx, "score": score, **row.to_dict()})
        scores.sort(key=lambda x: x["score"], reverse=True)
        return scores[:n]

    def _compute_similarity(self, target: Dict, candidate: Dict) -> float:
        """Compute similarity score between two properties."""
        score = 0
        if "size_sqft" in target and "size_sqft" in candidate:
            size_diff = abs(target["size_sqft"] - candidate["size_sqft"]) / max(target["size_sqft"], 1)
            score += self.weights["size"] * max(0, 1 - size_diff)
        if "bedrooms" in target and "bedrooms" in candidate:
            bed_match = 1.0 if target["bedrooms"] == candidate["bedrooms"] else 0.5
            score += self.weights["bedrooms"] * bed_match
        if "property_type" in target and "property_type" in candidate:
            type_match = 1.0 if target["property_type"] == candidate["property_type"] else 0.0
            score += self.weights["property_type"] * type_match
        if "area" in target and "area" in candidate:
            area_match = 1.0 if target["area"] == candidate["area"] else 0.3
            score += self.weights["area"] * area_match
        return round(score, 4)

    def estimate_value(self, comparables: List[Dict]) -> Dict:
        """Estimate property value from comparables."""
        if not comparables:
            return {"estimated_price": 0, "confidence": 0}
        prices = [c["price_aed"] for c in comparables if "price_aed" in c]
        if not prices:
            return {"estimated_price": 0, "confidence": 0}
        scores = [c.get("score", 0) for c in comparables]
        weights = np.array(scores) / sum(scores) if sum(scores) > 0 else np.ones(len(scores)) / len(scores)
        weighted_price = np.average(prices, weights=weights)
        return {
            "estimated_price": round(float(weighted_price), 0),
            "price_range": {
                "low": round(float(np.percentile(prices, 25)), 0),
                "high": round(float(np.percentile(prices, 75)), 0),
            },
            "n_comparables": len(comparables),
            "avg_similarity": round(float(np.mean(scores)), 4),
            "confidence": round(float(min(np.mean(scores) * 100, 95)), 1),
        }
