import numpy as np
import pandas as pd
from typing import Dict, Any, List, Optional, Tuple
from scipy import signal


class TrendAnalyzer:
    def __init__(self, df: pd.DataFrame):
        self.df = df

    def detect_trends(
        self, date_col: str, value_col: str, group_col: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        if group_col:
            results = []
            for group, data in self.df.groupby(group_col):
                trend = self._analyze_single_series(data, date_col, value_col)
                trend["group"] = str(group)
                results.append(trend)
            return results
        return [self._analyze_single_series(self.df, date_col, value_col)]

    def _analyze_single_series(self, data: pd.DataFrame, date_col: str, value_col: str) -> Dict[str, Any]:
        ts = data.set_index(date_col).sort_index()[value_col]
        monthly = ts.resample("ME").mean().dropna()
        if len(monthly) < 3:
            return {"error": "Insufficient data points"}
        values = monthly.values
        n = len(values)
        x = np.arange(n)
        slope, intercept = np.polyfit(x, values, 1)
        trend_line = slope * x + intercept
        direction = "upward" if slope > 0 else "downward" if slope < 0 else "flat"
        strength = abs(slope) / np.std(values) * 100 if np.std(values) > 0 else 0
        seasonal, trend_component = self._decompose(values, period=self._best_period(values))
        volatility = np.std(values - trend_line) / np.mean(values) * 100
        momentum = self._calculate_momentum(values)
        return {
            "direction": direction,
            "slope": float(slope),
            "strength": float(min(strength, 100)),
            "intercept": float(intercept),
            "volatility_pct": float(volatility),
            "momentum": float(momentum),
            "seasonal_strength": float(seasonal),
            "trend_line": trend_line.tolist(),
            "data_points": int(n),
            "start_date": str(monthly.index[0].date()),
            "end_date": str(monthly.index[-1].date()),
            "avg_value": float(monthly.mean()),
            "min_value": float(monthly.min()),
            "max_value": float(monthly.max()),
        }

    def _best_period(self, values: np.ndarray) -> int:
        n = len(values)
        if n >= 24:
            return 12
        if n >= 12:
            return 6
        if n >= 6:
            return 3
        return max(2, n // 2)

    def _decompose(self, values: np.ndarray, period: int) -> Tuple[float, np.ndarray]:
        if len(values) < 2 * period:
            return 0.0, values
        try:
            decomposition = signal.seasonal_decompose(values, model="additive", period=period)
            seasonal_std = np.std(decomposition.seasonal)
            residual_std = np.std(decomposition.resid) if np.std(decomposition.resid) > 0 else 1
            seasonal_strength = float(min(seasonal_std / residual_std, 10))
            return seasonal_strength, decomposition.trend
        except Exception:
            return 0.0, values

    def _calculate_momentum(self, values: np.ndarray) -> float:
        if len(values) < 2:
            return 0.0
        short = np.mean(values[-3:]) if len(values) >= 3 else np.mean(values)
        long = np.mean(values[:3]) if len(values) >= 3 else np.mean(values)
        return float(((short - long) / long) * 100) if long != 0 else 0.0

    def find_inflection_points(self, date_col: str, value_col: str) -> List[Dict[str, Any]]:
        ts = self.df.set_index(date_col).sort_index()[value_col]
        values = ts.values
        peaks, _ = signal.find_peaks(values, distance=3)
        valleys, _ = signal.find_peaks(-values, distance=3)
        inflection_points = []
        for p in peaks:
            inflection_points.append({
                "type": "peak",
                "index": int(p),
                "date": str(ts.index[p].date()),
                "value": float(values[p]),
            })
        for v in valleys:
            inflection_points.append({
                "type": "valley",
                "index": int(v),
                "date": str(ts.index[v].date()),
                "value": float(values[v]),
            })
        return sorted(inflection_points, key=lambda x: x["index"])

    def moving_averages(
        self, date_col: str, value_col: str, windows: List[int] = None
    ) -> Dict[str, Any]:
        if windows is None:
            windows = [7, 30, 90]
        ts = self.df.set_index(date_col).sort_index()[value_col]
        result = {"original": ts.tolist(), "dates": [str(d.date()) for d in ts.index]}
        for w in windows:
            if len(ts) >= w:
                result[f"ma_{w}"] = ts.rolling(window=w).mean().dropna().tolist()
        return result
