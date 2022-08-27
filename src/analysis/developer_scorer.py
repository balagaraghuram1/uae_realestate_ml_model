 """Score real estate developers based on project history."""
import logging
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

class DeveloperScorer:
    """Score developers based on delivery quality and track record."""

    WEIGHTS = {
        "delivery_rate": 0.30,
        "quality_score": 0.25,
        "customer_satisfaction": 0.20,
        "financial_stability": 0.15,
        "innovation": 0.10,
    }

    def score_developer(self, metrics: Dict) -> Dict:
        """Calculate developer score."""
        score = 0
        breakdown = {}
        for factor, weight in self.WEIGHTS.items():
            value = metrics.get(factor, 50)
            weighted = value * weight
            score += weighted
            breakdown[factor] = {"raw": value, "weighted": round(weighted, 2)}
        return {
            "total_score": round(score, 1),
            "grade": self._get_grade(score),
            "breakdown": breakdown,
            "tier": self._get_tier(score),
        }

    def compare_developers(self, developers: Dict[str, Dict]) -> List[Dict]:
        """Rank developers by score."""
        scored = []
        for name, metrics in developers.items():
            result = self.score_developer(metrics)
            scored.append({"developer": name, **result})
        return sorted(scored, key=lambda x: x["total_score"], reverse=True)

    def _get_grade(self, score: float) -> str:
        if score >= 90: return "A+"
        if score >= 80: return "A"
        if score >= 70: return "B+"
        if score >= 60: return "B"
        if score >= 50: return "C"
        return "D"

    def _get_tier(self, score: float) -> str:
        if score >= 80: return "Premium"
        if score >= 60: return "Standard"
        return "Budget"
