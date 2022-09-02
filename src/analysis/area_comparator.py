 """Generate detailed area comparison reports."""
import logging
from typing import Dict, List

logger = logging.getLogger(__name__)

class AreaComparator:
    """Compare multiple areas across various metrics."""

    def compare(self, areas_data: Dict[str, Dict]) -> Dict:
        """Generate a comparison report for multiple areas."""
        comparison = {}
        metrics = ["avg_price", "avg_size", "avg_price_per_sqft", "total_listings"]
        for metric in metrics:
            values = {area: data.get(metric, 0) for area, data in areas_data.items()}
            if values:
                best = max(values, key=values.get)
                worst = min(values, key=values.get)
                comparison[metric] = {
                    "values": values,
                    "best": {"area": best, "value": values[best]},
                    "worst": {"area": worst, "value": values[worst]},
                    "spread": round(values[best] - values[worst], 2),
                }
        rankings = []
        for area, data in areas_data.items():
            score = self._compute_area_score(data)
            rankings.append({"area": area, "score": score})
        rankings.sort(key=lambda x: x["score"], reverse=True)
        return {"comparison": comparison, "rankings": rankings}

    def _compute_area_score(self, data: Dict) -> float:
        """Compute overall score for an area."""
        score = 0
        score += min(data.get("avg_price_per_sqft", 0) / 100, 30)
        score += min(data.get("total_listings", 0) / 100, 25)
        score += min(data.get("avg_size", 0) / 200, 20)
        score += min(data.get("growth_rate", 0) * 2, 25)
        return round(score, 1)
