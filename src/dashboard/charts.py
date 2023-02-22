from typing import Dict, Any, List, Optional
from dataclasses import dataclass


@dataclass
class ChartConfig:
    type: str
    title: str
    x_label: str
    y_label: str
    data: List[Dict[str, Any]]
    options: Optional[Dict[str, Any]] = None


class ChartBuilder:
    @staticmethod
    def price_trend_chart(
        dates: List[str], prices: List[float], forecast: Optional[List[float]] = None
    ) -> ChartConfig:
        data = [{"date": d, "price": p} for d, p in zip(dates, prices)]
        if forecast:
            forecast_dates = dates[-len(forecast):] if len(forecast) <= len(dates) else dates
            for i, f in enumerate(forecast):
                data[i]["forecast"] = f
        return ChartConfig(
            type="line",
            title="Price Trends",
            x_label="Date",
            y_label="Average Price (AED)",
            data=data,
            options={"show_forecast": forecast is not None, "smooth": True},
        )

    @staticmethod
    def distribution_chart(
        labels: List[str], values: List[float], chart_type: str = "bar"
    ) -> ChartConfig:
        return ChartConfig(
            type=chart_type,
            title="Distribution",
            x_label="Category",
            y_label="Count",
            data=[{"label": l, "value": v} for l, v in zip(labels, values)],
            options={"show_percentage": True},
        )

    @staticmethod
    def heatmap_data(
        emirates: List[str], areas: List[str], values: List[List[float]]
    ) -> ChartConfig:
        data = []
        for i, emirate in enumerate(emirates):
            for j, area in enumerate(areas):
                if i < len(values) and j < len(values[i]):
                    data.append({"emirate": emirate, "area": area, "value": values[i][j]})
        return ChartConfig(
            type="heatmap",
            title="Investment Heatmap",
            x_label="Area",
            y_label="Emirate",
            data=data,
        )

    @staticmethod
    def comparables_chart(properties: List[Dict[str, Any]]) -> ChartConfig:
        data = [
            {
                "id": p.get("id"),
                "title": p.get("title", ""),
                "price": p.get("price_aed", 0),
                "price_per_sqft": p.get("price_per_sqft", 0),
                "size": p.get("size_sqft", 0),
                "bedrooms": p.get("bedrooms", 0),
                "distance_km": p.get("distance_km", 0),
            }
            for p in properties
        ]
        return ChartConfig(
            type="scatter",
            title="Comparable Properties",
            x_label="Size (sqft)",
            y_label="Price (AED)",
            data=data,
        )

    @staticmethod
    def portfolio_performance(months: List[str], returns: List[float], benchmark: List[float]) -> ChartConfig:
        data = [
            {"month": m, "portfolio": r, "benchmark": b}
            for m, r, b in zip(months, returns, benchmark)
        ]
        return ChartConfig(
            type="line",
            title="Portfolio Performance",
            x_label="Month",
            y_label="Return (%)",
            data=data,
            options={"show_benchmark": True},
        )

    @staticmethod
    def yield_comparison_chart(segments: List[Dict[str, Any]]) -> ChartConfig:
        data = [
            {"segment": s.get("name", ""), "gross_yield": s.get("gross_yield", 0), "net_yield": s.get("net_yield", 0)}
            for s in segments
        ]
        return ChartConfig(
            type="bar",
            title="Rental Yield by Segment",
            x_label="Segment",
            y_label="Yield (%)",
            data=data,
            options={"grouped": True, "show_values": True},
        )
