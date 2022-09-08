 """Time series decomposition for market analysis."""
import numpy as np
import pandas as pd
from typing import Dict

def decompose(series: pd.Series, period: int = 12) -> Dict:
    """Decompose a time series into trend, seasonal, and residual components."""
    values = series.values.astype(float)
    n = len(values)
    if n < 2 * period:
        return {"error": "Insufficient data for decomposition"}
    trend = pd.Series(values).rolling(window=period, center=True).mean().values
    detrended = values - trend
    seasonal = np.zeros(n)
    for i in range(period):
        indices = list(range(i, n, period))
        season_mean = np.nanmean(detrended[indices])
        for idx in indices:
            seasonal[idx] = season_mean
    residual = values - trend - seasonal
    trend_strength = 1 - np.nanvar(residual) / np.nanvar(values - seasonal) if np.nanvar(values - seasonal) > 0 else 0
    seasonal_strength = 1 - np.nanvar(residual) / np.nanvar(values - trend) if np.nanvar(values - trend) > 0 else 0
    return {
        "trend": np.nan_to_num(trend).tolist(),
        "seasonal": seasonal.tolist(),
        "residual": np.nan_to_num(residual).tolist(),
        "trend_strength": round(float(trend_strength), 4),
        "seasonal_strength": round(float(seasonal_strength), 4),
    }
