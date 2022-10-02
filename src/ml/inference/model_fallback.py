 """Model fallback chain for high availability predictions."""
import logging
from typing import List, Optional, Any

logger = logging.getLogger(__name__)

class ModelFallbackChain:
    """Try multiple models in order until one succeeds."""

    def __init__(self):
        self.models: List[dict] = []

    def add_model(self, name: str, model: Any, priority: int = 0):
        """Add a model to the fallback chain."""
        self.models.append({"name": name, "model": model, "priority": priority})
        self.models.sort(key=lambda m: m["priority"])

    def predict(self, X, **kwargs) -> dict:
        """Try models in priority order."""
        for entry in self.models:
            try:
                prediction = entry["model"].predict(X, **kwargs)
                return {
                    "prediction": prediction,
                    "model_used": entry["name"],
                    "fallback": False,
                }
            except Exception as e:
                logger.warning("Model %s failed: %s, trying next", entry["name"], e)
        return {"prediction": None, "model_used": None, "fallback": True, "error": "All models failed"}
