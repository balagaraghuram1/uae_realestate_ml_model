"""Risk assessment model for real estate investments."""
import numpy as np
import pandas as pd
from typing import Dict, Optional, List
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.calibration import CalibratedClassifierCV
from sklearn.metrics import classification_report, roc_auc_score
import logging

logger = logging.getLogger(__name__)

class RiskAssessor:
    """Assess investment risk for UAE real estate properties."""

    RISK_LEVELS = {0: "Low", 1: "Medium", 2: "High", 3: "Very High"}

    def __init__(self):
        base_model = RandomForestClassifier(
            n_estimators=200, max_depth=10, random_state=42, n_jobs=-1
        )
        self.model = CalibratedClassifierCV(base_model, cv=3, method="isotonic")
        self.feature_names: list = []
        self.risk_factors: Dict[str, float] = {}

    def train(self, X: pd.DataFrame, y: pd.Series) -> Dict:
        """Train the risk assessment model."""
        self.feature_names = X.columns.tolist()
        self.model.fit(X, y)
        train_pred = self.model.predict(X)
        report = classification_report(y, train_pred, output_dict=True)
        self.risk_factors = dict(zip(
            self.feature_names,
            self.model.calibrated_classifiers_[0].base_estimator.feature_importances_
        ))
        self.risk_factors = dict(sorted(self.risk_factors.items(), key=lambda x: x[1], reverse=True))
        metrics = {
            "accuracy": round(float(report["accuracy"]), 4),
            "macro_f1": round(float(report["macro avg"]["f1-score"]), 4),
        }
        logger.info("Risk model trained: %s", metrics)
        return metrics

    def assess_risk(self, X: pd.DataFrame) -> Dict:
        """Assess risk for a property."""
        probabilities = self.model.predict_proba(X)[0]
        risk_level = int(np.argmax(probabilities))
        return {
            "risk_level": self.RISK_LEVELS[risk_level],
            "risk_score": round(float(probabilities[risk_level]) * 100, 1),
            "probabilities": {
                self.RISK_LEVELS[i]: round(float(p) * 100, 1)
                for i, p in enumerate(probabilities)
            },
            "top_risk_factors": dict(list(self.risk_factors.items())[:5]),
        }

    def evaluate(self, X: pd.DataFrame, y: pd.Series) -> Dict:
        """Evaluate model performance."""
        pred = self.model.predict(X)
        proba = self.model.predict_proba(X)
        report = classification_report(y, pred, output_dict=True)
        metrics = {
            "accuracy": round(float(report["accuracy"]), 4),
            "macro_f1": round(float(report["macro avg"]["f1-score"]), 4),
            "weighted_f1": round(float(report["weighted avg"]["f1-score"]), 4),
        }
        try:
            metrics["auc_roc"] = round(float(roc_auc_score(y, proba, multi_class="ovr")), 4)
        except Exception:
            pass
        return metrics
