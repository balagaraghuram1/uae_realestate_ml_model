"""A/B testing framework for model comparison."""
import numpy as np
import pandas as pd
from typing import Dict, List, Optional
from scipy import stats
import logging

logger = logging.getLogger(__name__)

class ABTestFramework:
    """A/B test framework for comparing ML model performance."""

    def __init__(self, significance_level: float = 0.05):
        self.alpha = significance_level
        self.experiments: List[Dict] = []

    def create_experiment(self, name: str, model_a, model_b,
                          test_data: pd.DataFrame) -> Dict:
        """Create a new A/B experiment."""
        predictions_a = model_a.predict(test_data)
        predictions_b = model_b.predict(test_data)
        experiment = {
            "name": name,
            "model_a": type(model_a).__name__,
            "model_b": type(model_b).__name__,
            "n_samples": len(test_data),
            "predictions_a": predictions_a,
            "predictions_b": predictions_b,
        }
        self.experiments.append(experiment)
        return experiment

    def analyze_results(self, experiment: Dict, actual: np.ndarray) -> Dict:
        """Analyze A/B test results."""
        pred_a = experiment["predictions_a"]
        pred_b = experiment["predictions_b"]
        errors_a = np.abs(actual - pred_a)
        errors_b = np.abs(actual - pred_b)
        t_stat, p_value = stats.ttest_rel(errors_a, errors_b)
        return {
            "experiment": experiment["name"],
            "model_a_mae": round(float(errors_a.mean()), 2),
            "model_b_mae": round(float(errors_b.mean()), 2),
            "improvement_pct": round(float((errors_a.mean() - errors_b.mean()) / errors_a.mean() * 100), 2),
            "t_statistic": round(float(t_stat), 4),
            "p_value": round(float(p_value), 6),
            "significant": p_value < self.alpha,
            "winner": experiment["model_b"] if p_value < self.alpha and errors_b.mean() < errors_a.mean() else experiment["model_a"],
        }
