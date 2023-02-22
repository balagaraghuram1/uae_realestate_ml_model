import json
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, field


@dataclass
class KPICard:
    title: str
    value: float
    previous_value: float
    change_pct: float
    change_direction: str
    icon: str
    color: str
    format: str = "number"


@dataclass
class DashboardConfig:
    title: str = "UAE Real Estate Market Dashboard"
    refresh_interval_seconds: int = 300
    theme: str = "light"
    default_emirate: str = "dubai"
    default_property_type: str = "apartment"
    date_range_days: int = 365
    max_chart_points: int = 500
    enable_real_time: bool = False
    widgets: List[str] = field(default_factory=lambda: [
        "market_overview", "price_trends", "volume_analysis",
        "geospatial_map", "top_areas", "segment_performance",
        "investment_heatmap", "recent_transactions",
    ])


class DashboardApp:
    def __init__(self, config: Optional[DashboardConfig] = None):
        self.config = config or DashboardConfig()

    def build_kpi_cards(self, data: Dict[str, Any]) -> List[KPICard]:
        return [
            KPICard(
                title="Total Listings",
                value=data.get("total_listings", 0),
                previous_value=data.get("prev_total_listings", 0),
                change_pct=self._calc_change(
                    data.get("total_listings", 0), data.get("prev_total_listings", 0)
                ),
                change_direction=self._direction(
                    data.get("total_listings", 0), data.get("prev_total_listings", 0)
                ),
                icon="building",
                color="blue",
                format="number",
            ),
            KPICard(
                title="Avg Price (AED)",
                value=data.get("avg_price", 0),
                previous_value=data.get("prev_avg_price", 0),
                change_pct=self._calc_change(
                    data.get("avg_price", 0), data.get("prev_avg_price", 0)
                ),
                change_direction=self._direction(
                    data.get("avg_price", 0), data.get("prev_avg_price", 0)
                ),
                icon="cash",
                color="green",
                format="currency",
            ),
            KPICard(
                title="Avg Price/Sqft",
                value=data.get("avg_price_per_sqft", 0),
                previous_value=data.get("prev_avg_price_per_sqft", 0),
                change_pct=self._calc_change(
                    data.get("avg_price_per_sqft", 0), data.get("prev_avg_price_per_sqft", 0)
                ),
                change_direction=self._direction(
                    data.get("avg_price_per_sqft", 0), data.get("prev_avg_price_per_sqft", 0)
                ),
                icon="ruler",
                color="purple",
                format="currency",
            ),
            KPICard(
                title="Days on Market",
                value=data.get("avg_days_on_market", 0),
                previous_value=data.get("prev_avg_days_on_market", 0),
                change_pct=self._calc_change(
                    data.get("avg_days_on_market", 0), data.get("prev_avg_days_on_market", 0)
                ),
                change_direction="up" if data.get("avg_days_on_market", 0) > data.get("prev_avg_days_on_market", 0) else "down",
                icon="clock",
                color="orange",
                format="number",
            ),
            KPICard(
                title="Total Volume (AED)",
                value=data.get("total_volume", 0),
                previous_value=data.get("prev_total_volume", 0),
                change_pct=self._calc_change(
                    data.get("total_volume", 0), data.get("prev_total_volume", 0)
                ),
                change_direction=self._direction(
                    data.get("total_volume", 0), data.get("prev_total_volume", 0)
                ),
                icon="chart",
                color="teal",
                format="currency",
            ),
            KPICard(
                title="Absorption Rate (%)",
                value=data.get("absorption_rate", 0),
                previous_value=data.get("prev_absorption_rate", 0),
                change_pct=self._calc_change(
                    data.get("absorption_rate", 0), data.get("prev_absorption_rate", 0)
                ),
                change_direction=self._direction(
                    data.get("absorption_rate", 0), data.get("prev_absorption_rate", 0)
                ),
                icon="trending",
                color="red",
                format="percent",
            ),
        ]

    def _calc_change(self, current: float, previous: float) -> float:
        if previous == 0:
            return 0.0
        return round(((current - previous) / previous) * 100, 2)

    def _direction(self, current: float, previous: float) -> str:
        if current > previous:
            return "up"
        elif current < previous:
            return "down"
        return "stable"

    def serialize_state(self) -> str:
        return json.dumps({
            "config": {
                "title": self.config.title,
                "refresh_interval": self.config.refresh_interval_seconds,
                "theme": self.config.theme,
                "default_emirate": self.config.default_emirate,
            }
        })
