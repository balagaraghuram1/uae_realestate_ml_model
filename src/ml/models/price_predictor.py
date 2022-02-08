"""Ensemble price prediction model using XGBoost, LightGBM, and Ridge."""
import numpy as np
import pandas as pd
from typing import Dict, Optional, Tuple
from sklearn.model_selection import cross_val_score, KFold
from sklearn.linear_model import Ridge, Lasso, ElasticNet
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor, StackingRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score, mean_absolute_percentage_error
import logging

logger = logging.getLogger(__name__)

try:
    import xgboost as xgb
    HAS_XGB = True
except ImportError:
    HAS_XGB = False

try:
    import lightgbm as lgb
    HAS_LGB = True
except ImportError:
    HAS_LGB = False


class PricePredictor:
    """Ensemble model for UAE real estate price prediction."""

    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.model = None
        self.feature_names: list = []
        self.training_metrics: Dict = {}
        self._build_model()

    def _build_model(self):
        """Build the stacking ensemble model."""
        estimators = []
        estimators.append(("ridge", Ridge(alpha=1.0)))
        estimators.append(("lasso", Lasso(alpha=0.1)))
        estimators.append(("elastic", ElasticNet(alpha=0.1, l1_ratio=0.5)))
        estimators.append(("rf", RandomForestRegressor(
            n_estimators=200, max_depth=15, min_samples_split=5,
            min_samples_leaf=2, random_state=42, n_jobs=-1
        )))
        estimators.append(("gbr", GradientBoostingRegressor(
            n_estimators=200, max_depth=6, learning_rate=0.1,
            subsample=0.8, random_state=42
        )))
        if HAS_XGB:
            estimators.append(("xgb", xgb.XGBRegressor(
                n_estimators=300, max_depth=7, learning_rate=0.05,
                subsample=0.8, colsample_bytree=0.8, random_state=42,
                tree_method="hist", verbosity=0
            )))
        if HAS_LGB:
            estimators.append(("lgb", lgb.LGBMRegressor(
                n_estimators=300, max_depth=7, learning_rate=0.05,
                subsample=0.8, colsample_bytree=0.8, random_state=42,
                verbose=-1
            )))
        self.model = StackingRegressor(
            estimators=estimators,
            final_estimator=Ridge(alpha=0.5),
            cv=5, n_jobs=-1,
        )
        logger.info("Built stacking ensemble with %d base estimators", len(estimators))

    def train(self, X: pd.DataFrame, y: pd.Series, eval_set: Optional[Tuple] = None) -> Dict:
        """Train the ensemble model."""
        self.feature_names = X.columns.tolist()
        logger.info("Training on %d samples with %d features", len(X), len(self.feature_names))
        self.model.fit(X, y)
        train_pred = self.model.predict(X)
        self.training_metrics = {
            "train_mae": round(float(mean_absolute_error(y, train_pred)), 2),
            "train_rmse": round(float(np.sqrt(mean_squared_error(y, train_pred))), 2),
            "train_r2": round(float(r2_score(y, train_pred)), 4),
            "train_mape": round(float(mean_absolute_percentage_error(y, train_pred)) * 100, 2),
        }
        cv_scores = cross_val_score(
            self.model, X, y, cv=5, scoring="neg_mean_absolute_error", n_jobs=-1
        )
        self.training_metrics["cv_mae_mean"] = round(float(-cv_scores.mean()), 2)
        self.training_metrics["cv_mae_std"] = round(float(cv_scores.std()), 2)
        logger.info("Training metrics: %s", self.training_metrics)
        return self.training_metrics

    def predict(self, X: pd.DataFrame) -> np.ndarray:
        """Generate price predictions."""
        if self.model is None:
            raise RuntimeError("Model not trained")
        return self.model.predict(X)

    def evaluate(self, X: pd.DataFrame, y: pd.Series) -> Dict:
        """Evaluate model on test data."""
        predictions = self.predict(X)
        metrics = {
            "mae": round(float(mean_absolute_error(y, predictions)), 2),
            "rmse": round(float(np.sqrt(mean_squared_error(y, predictions))), 2),
            "r2": round(float(r2_score(y, predictions)), 4),
            "mape": round(float(mean_absolute_percentage_error(y, predictions)) * 100, 2),
            "median_ae": round(float(np.median(np.abs(y - predictions))), 2),
        }
        return metrics

    def feature_importance(self) -> Dict[str, float]:
        """Get feature importance from the ensemble."""
        importances = {}
        for name, est in self.model.named_estimators_.items():
            if hasattr(est, "feature_importances_"):
                for feat, imp in zip(self.feature_names, est.feature_importances_):
                    importances[feat] = importances.get(feat, 0) + imp
        if importances:
            total = sum(importances.values())
            if total > 0:
                importances = {k: round(v / total, 4) for k, v in importances.items()}
        return dict(sorted(importances.items(), key=lambda x: x[1], reverse=True))

    def save(self, path: str):
        """Save model to disk."""
        import joblib
        joblib.dump({
            "model": self.model,
            "feature_names": self.feature_names,
            "metrics": self.training_metrics,
            "config": self.config,
        }, path)
        logger.info("Model saved to %s", path)

    @classmethod
    def load(cls, path: str) -> "PricePredictor":
        """Load a saved model."""
        import joblib
        data = joblib.load(path)
        instance = cls(config=data.get("config", {}))
        instance.model = data["model"]
        instance.feature_names = data["feature_names"]
        instance.training_metrics = data.get("metrics", {})
        return instance
