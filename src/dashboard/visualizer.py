"""Market data visualization module."""
import logging
from typing import Dict, List, Optional
import numpy as np

logger = logging.getLogger(__name__)

class MarketVisualizer:
    """Generate charts and visualizations for market data."""

    def __init__(self, theme: str = "professional"):
        self.theme = theme
        self.color_palette = {
            "primary": "#0d9488", "secondary": "#6366f1",
            "danger": "#ef4444", "success": "#22c55e",
            "warning": "#f59e0b", "background": "#f8fafb",
        }

    def price_trend_chart(self, data: List[Dict]) -> Dict:
        """Generate price trend chart data."""
        months = [d["month"] for d in data]
        prices = [d["avg_price"] for d in data]
        volumes = [d.get("volume", 0) for d in data]
        return {
            "type": "line",
            "title": "Average Price Trend",
            "x_label": "Month", "y_label": "Price (AED)",
            "series": [
                {"name": "Avg Price", "data": prices, "color": self.color_palette["primary"]},
            ],
            "categories": months,
            "annotations": self._detect_trend_changes(prices, months),
        }

    def area_comparison_chart(self, areas: List[Dict]) -> Dict:
        """Generate area comparison bar chart."""
        return {
            "type": "bar",
            "title": "Price by Area",
            "categories": [a["area"] for a in areas],
            "series": [
                {"name": "Avg Price", "data": [a["avg_price"] for a in areas]},
                {"name": "Price/sqft", "data": [a.get("price_per_sqft", 0) for a in areas]},
            ],
        }

    def market_heatmap(self, emirate_data: Dict) -> Dict:
        """Generate market heatmap data."""
        areas = []
        for emirate, data in emirate_data.items():
            for area, metrics in data.get("areas", {}).items():
                areas.append({
                    "emirate": emirate, "area": area,
                    "intensity": metrics.get("growth_rate", 0),
                    "value": metrics.get("avg_price", 0),
                })
        return {"type": "heatmap", "title": "Market Activity Heatmap", "data": areas}

    def _detect_trend_changes(self, values: list, labels: list) -> List[Dict]:
        """Detect significant trend changes for annotations."""
        annotations = []
        for i in range(2, len(values)):
            if values[i] > values[i-1] > values[i-2]:
                annotations.append({"index": i, "label": "Upward trend", "type": "bullish"})
            elif values[i] < values[i-1] < values[i-2]:
                annotations.append({"index": i, "label": "Downward trend", "type": "bearish"})
        return annotations
