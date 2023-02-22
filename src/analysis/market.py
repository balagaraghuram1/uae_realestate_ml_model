import pandas as pd
import numpy as np
from typing import Optional, Dict, Any, List
from dataclasses import dataclass


@dataclass
class MarketSegment:
    name: str
    total_listings: int
    avg_price: float
    median_price: float
    price_per_sqft: float
    inventory_turnover_days: float
    price_trend: str
    growth_rate: float
    demand_score: float
    supply_score: float


class MarketAnalyzer:
    def __init__(self, df: pd.DataFrame):
        self.df = df

    def segment_analysis(self, by: str = "emirate") -> List[MarketSegment]:
        segments = []
        for group, data in self.df.groupby(by):
            segments.append(self._analyze_segment(group, data))
        return sorted(segments, key=lambda x: x.total_listings, reverse=True)

    def _analyze_segment(self, name: str, data: pd.DataFrame) -> MarketSegment:
        prices = data["price_aed"].dropna()
        sizes = data["size_sqft"].dropna()
        price_per_sqft = (prices / sizes).mean() if len(sizes) > 0 else 0
        return MarketSegment(
            name=str(name),
            total_listings=len(data),
            avg_price=float(prices.mean()),
            median_price=float(prices.median()),
            price_per_sqft=float(price_per_sqft) if not np.isnan(price_per_sqft) else 0,
            inventory_turnover_days=self._calc_turnover(data),
            price_trend=self._detect_trend(data),
            growth_rate=self._calc_growth(data),
            demand_score=self._score_demand(data),
            supply_score=self._score_supply(data),
        )

    def _calc_turnover(self, data: pd.DataFrame) -> float:
        if "listing_date" not in data.columns or "sold_date" not in data.columns:
            return 0
        dated = data.dropna(subset=["listing_date", "sold_date"])
        if len(dated) == 0:
            return 0
        return float((dated["sold_date"] - dated["listing_date"]).dt.days.mean())

    def _detect_trend(self, data: pd.DataFrame) -> str:
        if "listing_date" not in data.columns:
            return "stable"
        ts = data.set_index("listing_date").sort_index()
        monthly = ts["price_aed"].resample("ME").mean().dropna()
        if len(monthly) < 3:
            return "stable"
        first_half = monthly[: len(monthly) // 2].mean()
        second_half = monthly[len(monthly) // 2:].mean()
        change = (second_half - first_half) / first_half * 100
        if change > 5:
            return "increasing"
        elif change < -5:
            return "decreasing"
        return "stable"

    def _calc_growth(self, data: pd.DataFrame) -> float:
        if "listing_date" not in data.columns:
            return 0
        ts = data.set_index("listing_date").sort_index()
        monthly = ts["price_aed"].resample("ME").mean().dropna()
        if len(monthly) < 2:
            return 0
        return float((monthly.iloc[-1] - monthly.iloc[0]) / monthly.iloc[0] * 100)

    def _score_demand(self, data: pd.DataFrame) -> float:
        score = 50.0
        if "views" in data.columns:
            avg_views = data["views"].mean()
            score += min(avg_views / 100, 25)
        if "inquiries" in data.columns:
            avg_inq = data["inquiries"].mean()
            score += min(avg_inq * 5, 15)
        if "days_on_market" in data.columns:
            avg_dom = data["days_on_market"].mean()
            if avg_dom < 30:
                score += 10
            elif avg_dom > 90:
                score -= 10
        return min(max(score, 0), 100)

    def _score_supply(self, data: pd.DataFrame) -> float:
        score = 50.0
        total = len(data)
        score += min(total / 10, 30)
        if "listing_date" in data.columns:
            recent = data[data["listing_date"] >= pd.Timestamp.now() - pd.DateOffset(months=3)]
            new_listings_ratio = len(recent) / max(total, 1)
            score += new_listings_ratio * 20
        return min(max(score, 0), 100)

    def affordability_analysis(self, income_col: Optional[str] = None) -> Dict[str, Any]:
        avg_price = self.df["price_aed"].mean()
        median_price = self.df["price_aed"].median()
        studio_price = self.df[self.df["bedrooms"] == 0]["price_aed"].mean() if 0 in self.df["bedrooms"].values else avg_price
        one_bed_price = self.df[self.df["bedrooms"] == 1]["price_aed"].mean() if 1 in self.df["bedrooms"].values else avg_price
        return {
            "avg_price": float(avg_price),
            "median_price": float(median_price),
            "price_to_income_ratio": 0,
            "studio_avg_price": float(studio_price),
            "one_bed_avg_price": float(one_bed_price),
            "entry_level_price": float(min(self.df["price_aed"].quantile(0.1), avg_price)),
            "luxury_threshold": float(self.df["price_aed"].quantile(0.9)),
        }

    def absorption_analysis(self, date_col: str = "listing_date") -> Dict[str, Any]:
        df = self.df.copy()
        df["month"] = df[date_col].dt.to_period("M")
        monthly = df.groupby("month").agg(
            new_listings=("price_aed", "count"),
            sold=("sold_date", lambda x: x.notna().sum() if "sold_date" in df.columns else 0),
        )
        monthly["absorption_rate"] = (monthly["sold"] / monthly["new_listings"] * 100).replace([np.inf, -np.inf], 0)
        return {
            "overall_rate": float(monthly["absorption_rate"].mean()),
            "months_of_inventory": float(monthly["new_listings"].sum() / max(monthly["sold"].sum(), 1)),
            "monthly_trend": monthly["absorption_rate"].to_dict(),
        }
