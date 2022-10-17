 """Prediction confidence calibration for reliable uncertainty estimates."""
import numpy as np
from typing import Dict, Tuple

class ConfidenceCalibrator:
    """Calibrate prediction confidence intervals."""

    def calibrate(self, predictions: np.ndarray, actuals: np.ndarray,
                  confidence_levels: list = [0.5, 0.8, 0.9, 0.95]) -> Dict:
        """Compute calibration metrics at different confidence levels."""
        errors = np.abs(predictions - actuals)
        results = {}
        for level in confidence_levels:
            quantile = np.percentile(errors, level * 100)
            coverage = np.mean(errors <= quantile)
            results[f"{int(level*100)}%"] = {
                "target_coverage": level,
                "actual_coverage": round(float(coverage), 4),
                "threshold": round(float(quantile), 2),
                "miscalibration": round(float(abs(coverage - level)), 4),
            }
        return {
            "calibration": results,
            "mean_error": round(float(errors.mean()), 2),
            "median_error": round(float(np.median(errors)), 2),
        }

    def prediction_intervals(self, predictions: np.ndarray, residuals: np.ndarray,
                             confidence: float = 0.9) -> Tuple[np.ndarray, np.ndarray]:
        """Generate prediction intervals from residuals."""
        alpha = 1 - confidence
        lower_percentile = alpha / 2 * 100
        upper_percentile = (1 - alpha / 2) * 100
        lower_margin = np.percentile(np.abs(residuals), lower_percentile)
        upper_margin = np.percentile(np.abs(residuals), upper_percentile)
        return predictions - lower_margin, predictions + upper_margin
