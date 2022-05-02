"""Generate comprehensive market analysis reports."""
import logging
from typing import Dict, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class ReportGenerator:
    """Generate structured market analysis reports."""

    def __init__(self):
        self.sections: List[Dict] = []

    def add_section(self, title: str, content: Dict, section_type: str = "analysis"):
        """Add a section to the report."""
        self.sections.append({
            "title": title, "content": content,
            "type": section_type,
        })

    def executive_summary(self, market_data: Dict) -> Dict:
        """Generate executive summary section."""
        summary = market_data.get("summary", {})
        return {
            "title": "Executive Summary",
            "highlights": [
                f"Total listings analyzed: {summary.get('total_listings', 0):,}",
                f"Average property price: AED {summary.get('avg_price', 0):,.0f}",
                f"Median property price: AED {summary.get('median_price', 0):,.0f}",
                f"Average price per sqft: AED {summary.get('price_per_sqft_avg', 0):,.0f}",
            ],
            "market_outlook": "positive",
            "confidence_level": 0.85,
        }

    def price_analysis(self, trends: List[Dict]) -> Dict:
        """Analyze price trends."""
        if not trends:
            return {"error": "No trend data available"}
        prices = [t["avg_price"] for t in trends]
        yoy_change = ((prices[-1] - prices[0]) / prices[0] * 100) if prices[0] > 0 else 0
        return {
            "title": "Price Analysis",
            "period": f"{trends[0]['month']} to {trends[-1]['month']}",
            "yoy_change_pct": round(yoy_change, 2),
            "trend": "increasing" if yoy_change > 0 else "decreasing",
            "avg_monthly_change": round((prices[-1] - prices[0]) / len(prices), 0),
            "volatility": round(float(np.std(prices) / np.mean(prices) * 100), 2) if len(prices) > 1 else 0,
        }

    def investment_recommendations(self, hotspots: List[Dict]) -> Dict:
        """Generate investment recommendations."""
        recommendations = []
        for zone in hotspots[:5]:
            score = zone.get("growth_rate", 0) / 15 * 100
            recommendations.append({
                "area": zone["area"],
                "score": min(round(score, 1), 100),
                "rationale": f"High growth rate ({zone.get('growth_rate', 0)}%) with strong fundamentals",
                "risk_level": "Medium" if score > 60 else "Low",
            })
        return {
            "title": "Investment Recommendations",
            "recommendations": recommendations,
            "disclaimer": "This analysis is for informational purposes only and does not constitute financial advice.",
        }

    def generate_full_report(self, market_data: Dict) -> Dict:
        """Generate a complete market report."""
        self.sections = []
        self.add_section("executive_summary", self.executive_summary(market_data))
        if "price_trends" in market_data:
            self.add_section("price_analysis", self.price_analysis(market_data["price_trends"]))
        if "hotspots" in market_data:
            self.add_section("investment_recommendations",
                           self.investment_recommendations(market_data["hotspots"]))
        return {
            "report_title": "UAE Real Estate Market Analysis",
            "generated_at": datetime.utcnow().isoformat(),
            "sections": self.sections,
            "metadata": {
                "analyst": "UAE Real Estate ML Platform",
                "version": "1.0.0",
            },
        }
