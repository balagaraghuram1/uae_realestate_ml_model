"""Rental yield prediction model for investment analysis."""
import numpy as np
import pandas as pd
from typing import Dict, Optional
from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
from sklearn.model_selection import cross_val_score
from sklearn.metrics import mean_absolute_error, r2_score, mean_absolute_percentage_error
import logging

logger = logging.getLogger(__name__)

class YieldPredictor:
    """Predict rental yield for UAE properties."""

    def __init__(self):
        self.model = GradientBoostingRegressor(
            n_estimators=200, max_depth=5, learning_rate=0.08,
            subsample=0.8, random_state=42,
        )
        self.feature_names: list = []
        self.metrics: Dict = {}

    def train(self, X: pd.DataFrame, y: pd.Series) -> Dict:
        """Train the yield prediction model."""
        self.feature_names = X.columns.tolist()
        self.model.fit(X, y)
        train_pred = self.model.predict(X)
        cv_scores = cross_val_score(self.model, X, y, cv=5, scoring="r2")
        self.metrics = {
            "train_r2": round(float(r2_score(y, train_pred)), 4),
            "train_mae": round(float(mean_absolute_error(y, train_pred)), 4),
            "cv_r2_mean": round(float(cv_scores.mean()), 4),
            "cv_r2_std": round(float(cv_scores.std()), 4),
        }
        logger.info("Yield model trained: %s", self.metrics)
        return self.metrics

    def predict(self, X: pd.DataFrame) -> np.ndarray:
        """Predict rental yield percentage."""
        return self.model.predict(X)

    def evaluate(self, X: pd.DataFrame, y: pd.Series) -> Dict:
        """Evaluate on test set."""
        pred = self.predict(X)
        return {
            "r2": round(float(r2_score(y, pred)), 4),
            "mae": round(float(mean_absolute_error(y, pred)), 4),
            "mape": round(float(mean_absolute_percentage_error(y, pred)) * 100, 2),
        }

    def feature_importance(self) -> Dict[str, float]:
        """Get feature importances."""
        return dict(sorted(
            zip(self.feature_names, self.model.feature_importances_),
            key=lambda x: x[1], reverse=True
        ))
