"""Model interpretability using SHAP values."""
import numpy as np
import pandas as pd
from typing import Dict, Optional, List
import logging

logger = logging.getLogger(__name__)

class ModelInterpreter:
    """Interpret ML model predictions using SHAP."""

    def __init__(self, model, feature_names: List[str]):
        self.model = model
        self.feature_names = feature_names
        self._explainer = None

    def _get_explainer(self):
        """Initialize SHAP explainer."""
        if self._explainer is None:
            try:
                import shap
                self._explainer = shap.TreeExplainer(self.model)
            except Exception:
                logger.warning("SHAP not available, using permutation importance")
                self._explainer = "permutation"
        return self._explainer

    def explain_prediction(self, X: np.ndarray, index: int = 0) -> Dict:
        """Explain a single prediction."""
        explainer = self._get_explainer()
        if explainer == "permutation":
            return self._permutation_importance(X)
        shap_values = explainer.shap_values(X[index:index + 1])
        feature_importance = list(zip(
            self.feature_names,
            shap_values[0] if isinstance(shap_values, list) else shap_values[0],
        ))
        feature_importance.sort(key=lambda x: abs(x[1]), reverse=True)
        return {
            "prediction_index": index,
            "top_features": [
                {"feature": f, "shap_value": round(float(v), 4)}
                for f, v in feature_importance[:10]
            ],
            "base_value": round(float(explainer.expected_value[0] if isinstance(explainer.expected_value, list) else explainer.expected_value), 4),
        }

    def global_feature_importance(self, X: np.ndarray) -> Dict:
        """Compute global feature importance."""
        explainer = self._get_explainer()
        if explainer == "permutation":
            return self._permutation_importance(X)
        shap_values = explainer.shap_values(X[:min(100, len(X))])
        if isinstance(shap_values, list):
            shap_values = shap_values[0]
        mean_abs_shap = np.abs(shap_values).mean(axis=0)
        importance = dict(zip(self.feature_names, mean_abs_shap))
        importance = dict(sorted(importance.items(), key=lambda x: x[1], reverse=True))
        return {
            "feature_importance": {k: round(float(v), 4) for k, v in importance.items()},
            "n_samples": min(100, len(X)),
        }

    def _permutation_importance(self, X: np.ndarray, n_repeats: int = 10) -> Dict:
        """Fallback permutation importance."""
        baseline_pred = self.model.predict(X)
        importances = {}
        for i, name in enumerate(self.feature_names):
            scores = []
            for _ in range(n_repeats):
                X_perm = X.copy()
                X_perm[:, i] = np.random.permutation(X_perm[:, i])
                perm_pred = self.model.predict(X_perm)
                scores.append(np.mean(np.abs(baseline_pred - perm_pred)))
            importances[name] = round(float(np.mean(scores)), 4)
        importances = dict(sorted(importances.items(), key=lambda x: x[1], reverse=True))
        return {"feature_importance": importances, "method": "permutation"}
