"""Market trend analysis with statistical significance testing."""
import numpy as np
import pandas as pd
from typing import Dict, List, Optional
from scipy import stats
import logging

logger = logging.getLogger(__name__)

class TrendAnalyzer:
    """Detect and analyze market trends with statistical rigor."""

    def __init__(self, significance_level: float = 0.05):
        self.alpha = significance_level

    def detect_trend(self, series: pd.Series) -> Dict:
        """Detect if a time series has a significant trend."""
        x = np.arange(len(series))
        slope, intercept, r_value, p_value, std_err = stats.linregress(x, series.values)
        return {
            "has_trend": p_value < self.alpha,
            "direction": "upward" if slope > 0 else "downward",
            "slope": round(float(slope), 4),
            "r_squared": round(float(r_value ** 2), 4),
            "p_value": round(float(p_value), 6),
            "std_error": round(float(std_err), 4),
        }

    def detect_structural_break(self, series: pd.Series, min_segment: int = 10) -> Dict:
        """Detect structural breaks using Chow test approximation."""
        n = len(series)
        if n < 2 * min_segment:
            return {"break_detected": False, "reason": "insufficient_data"}
        best_break = None
        best_f_stat = 0
        for i in range(min_segment, n - min_segment):
            seg1 = series.values[:i]
            seg2 = series.values[i:]
            ss_res_full = np.sum((series.values - series.mean()) ** 2)
            ss_res_1 = np.sum((seg1 - seg1.mean()) ** 2)
            ss_res_2 = np.sum((seg2 - seg2.mean()) ** 2)
            ss_res_parts = ss_res_1 + ss_res_2
            k = 2
            f_stat = ((ss_res_full - ss_res_parts) / k) / (ss_res_parts / (n - 2 * k))
            if f_stat > best_f_stat:
                best_f_stat = f_stat
                best_break = i
        p_value = 1 - stats.f.cdf(best_f_stat, 2, n - 4) if best_f_stat > 0 else 1
        return {
            "break_detected": p_value < self.alpha,
            "break_index": best_break,
            "f_statistic": round(float(best_f_stat), 4),
            "p_value": round(float(p_value), 6),
        }

    def seasonality_analysis(self, series: pd.Series, period: int = 12) -> Dict:
        """Analyze seasonal patterns in the data."""
        if len(series) < 2 * period:
            return {"seasonal": False, "reason": "insufficient_data"}
        values = series.values
        seasonal_means = [values[i::period].mean() for i in range(period)]
        overall_mean = values.mean()
        ss_total = np.sum((values - overall_mean) ** 2)
        ss_seasonal = sum(
            len(values[i::period]) * (m - overall_mean) ** 2
            for i, m in enumerate(seasonal_means)
        )
        seasonal_strength = ss_seasonal / ss_total if ss_total > 0 else 0
        return {
            "seasonal": seasonal_strength > 0.1,
            "seasonal_strength": round(float(seasonal_strength), 4),
            "seasonal_pattern": [round(float(m), 2) for m in seasonal_means],
        }

    def moving_average_crossover(self, series: pd.Series, short_window: int = 5,
                                 long_window: int = 20) -> Dict:
        """Detect moving average crossovers (buy/sell signals)."""
        short_ma = series.rolling(window=short_window).mean()
        long_ma = series.rolling(window=long_window).mean()
        signals = []
        for i in range(1, len(series)):
            if pd.notna(short_ma.iloc[i]) and pd.notna(long_ma.iloc[i]):
                if short_ma.iloc[i] > long_ma.iloc[i] and short_ma.iloc[i - 1] <= long_ma.iloc[i - 1]:
                    signals.append({"index": i, "signal": "buy", "price": float(series.iloc[i])})
                elif short_ma.iloc[i] < long_ma.iloc[i] and short_ma.iloc[i - 1] >= long_ma.iloc[i - 1]:
                    signals.append({"index": i, "signal": "sell", "price": float(series.iloc[i])})
        return {
            "short_window": short_window,
            "long_window": long_window,
            "signals": signals,
            "total_signals": len(signals),
        }

    def volatility_analysis(self, series: pd.Series, window: int = 20) -> Dict:
        """Analyze volatility using rolling standard deviation."""
        returns = series.pct_change().dropna()
        rolling_vol = returns.rolling(window=window).std() * np.sqrt(252)
        return {
            "annualized_volatility": round(float(returns.std() * np.sqrt(252)), 4),
            "current_volatility": round(float(rolling_vol.iloc[-1]) if len(rolling_vol) > 0 else 0, 4),
            "avg_volatility": round(float(rolling_vol.mean()), 4),
            "max_volatility": round(float(rolling_vol.max()), 4),
            "volatility_trend": "increasing" if rolling_vol.iloc[-1] > rolling_vol.mean() else "decreasing",
        }
