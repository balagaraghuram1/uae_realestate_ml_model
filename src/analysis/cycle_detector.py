"""Real estate market cycle detection and phase analysis."""
import numpy as np
import pandas as pd
from typing import Dict, Optional, List
from scipy.signal import argrelextrema
import logging

logger = logging.getLogger(__name__)

class MarketCycleDetector:
    """Detect and analyze real estate market cycles."""

    PHASES = ["recovery", "expansion", "hyper_supply", "recession"]

    def __init__(self, order: int = 5):
        self.order = order
        self.cycles: List[Dict] = []

    def detect_cycles(self, price_series: pd.Series) -> Dict:
        """Detect market cycles from price data."""
        values = price_series.values
        peaks = argrelextrema(values, np.greater, order=self.order)[0]
        troughs = argrelextrema(values, np.less, order=self.order)[0]
        self.cycles = []
        for i in range(len(troughs) - 1):
            start_idx = troughs[i]
            end_idx = troughs[i + 1]
            peak_in_cycle = peaks[(peaks > start_idx) & (peaks < end_idx)]
            peak_idx = peak_in_cycle[0] if len(peak_in_cycle) > 0 else start_idx
            recovery_end = peak_idx
            expansion_end = peak_idx
            self.cycles.append({
                "start": int(start_idx),
                "trough_price": float(values[start_idx]),
                "peak": int(peak_idx),
                "peak_price": float(values[peak_idx]),
                "recovery_gain": float(values[peak_idx] - values[start_idx]),
                "recovery_pct": round(float((values[peak_idx] - values[start_idx]) / values[start_idx] * 100), 2),
            })
        current_phase = self._detect_current_phase(values, peaks, troughs)
        return {
            "total_cycles": len(self.cycles),
            "cycles": self.cycles,
            "current_phase": current_phase,
            "avg_cycle_length": round(float(np.mean([c["peak"] - c["start"] for c in self.cycles])), 0) if self.cycles else 0,
        }

    def _detect_current_phase(self, values: np.ndarray, peaks: np.ndarray,
                               troughs: np.ndarray) -> str:
        """Detect the current market phase."""
        recent = values[-10:]
        trend = np.polyfit(range(len(recent)), recent, 1)[0]
        if trend > 0:
            if values[-1] > np.percentile(values, 80):
                return "expansion"
            return "recovery"
        else:
            if values[-1] < np.percentile(values, 20):
                return "recession"
            return "hyper_supply"
