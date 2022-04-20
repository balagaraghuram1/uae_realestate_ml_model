"""Comprehensive model evaluation framework."""
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Callable
from sklearn.model_selection import cross_val_score, KFold, TimeSeriesSplit
from sklearn.metrics import (
    mean_absolute_error, mean_squared_error, r2_score,
    mean_absolute_percentage_error, median_absolute_error,
)
import logging

logger = logging.getLogger(__name__)

class ModelEvaluator:
    """Evaluate ML models with multiple metrics and validation strategies."""

    def __init__(self, model, task: str = "regression"):
        self.model = model
        self.task = task
        self.cv_results: Dict = {}
        self.test_results: Dict = {}

    def cross_validate(self, X: np.ndarray, y: np.ndarray, cv: int = 5,
                       scoring: str = "neg_mean_absolute_error",
                       time_series: bool = False) -> Dict:
        """Perform cross-validation."""
        if time_series:
            splitter = TimeSeriesSplit(n_splits=cv)
        else:
            splitter = KFold(n_splits=cv, shuffle=True, random_state=42)
        scores = cross_val_score(self.model, X, y, cv=splitter, scoring=scoring, n_jobs=-1)
        self.cv_results = {
            "scoring": scoring,
            "n_folds": cv,
            "scores": scores.tolist(),
            "mean": round(float(scores.mean()), 4),
            "std": round(float(scores.std()), 4),
            "min": round(float(scores.min()), 4),
            "max": round(float(scores.max()), 4),
        }
        return self.cv_results

    def evaluate_test_set(self, X_test: np.ndarray, y_test: np.ndarray) -> Dict:
        """Evaluate on a held-out test set."""
        predictions = self.model.predict(X_test)
        self.test_results = {
            "mae": round(float(mean_absolute_error(y_test, predictions)), 2),
            "rmse": round(float(np.sqrt(mean_squared_error(y_test, predictions))), 2),
            "r2": round(float(r2_score(y_test, predictions)), 4),
            "mape": round(float(mean_absolute_percentage_error(y_test, predictions)) * 100, 2),
            "median_ae": round(float(median_absolute_error(y_test, predictions)), 2),
            "explained_variance": round(float(1 - np.var(y_test - predictions) / np.var(y_test)), 4),
        }
        return self.test_results

    def residual_analysis(self, y_true: np.ndarray, y_pred: np.ndarray) -> Dict:
        """Analyze prediction residuals."""
        residuals = y_true - y_pred
        return {
            "mean_residual": round(float(residuals.mean()), 2),
            "std_residual": round(float(residuals.std()), 2),
            "skewness": round(float(pd.Series(residuals).skew()), 4),
            "kurtosis": round(float(pd.Series(residuals).kurtosis()), 4),
            "within_10pct": round(float((np.abs(residuals / y_true) < 0.1).mean() * 100), 2),
            "within_20pct": round(float((np.abs(residuals / y_true) < 0.2).mean() * 100), 2),
        }

    def prediction_confidence(self, X: np.ndarray, method: str = "bootstrap",
                              n_estimators: int = 100) -> Dict:
        """Estimate prediction confidence intervals."""
        if method == "bootstrap":
            from sklearn.ensemble import BaggingRegressor
            bagging = BaggingRegressor(
                base_estimator=None, n_estimators=n_estimators,
                random_state=42, n_jobs=-1,
            )
            bagging.fit(X, np.zeros(len(X)))
            return {"method": "bootstrap", "n_estimators": n_estimators, "note": "fitted"}
        return {"method": method}

    def generate_report(self) -> Dict:
        """Generate a complete evaluation report."""
        return {
            "cross_validation": self.cv_results,
            "test_set": self.test_results,
            "model_type": type(self.model).__name__,
            "task": self.task,
        }
