"""End-to-end ML training pipeline with reproducibility."""
import os, json, hashlib, logging
import numpy as np
import pandas as pd
from typing import Dict, Optional, Any
from datetime import datetime
import hashlib

logger = logging.getLogger(__name__)

class PipelineTrainer:
    """Train ML models with full reproducibility tracking."""

    def __init__(self, experiment_name: str, output_dir: str = "training_output"):
        self.experiment_name = experiment_name
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        self.run_id = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        self.metadata: Dict[str, Any] = {
            "experiment": experiment_name,
            "run_id": self.run_id,
            "start_time": datetime.utcnow().isoformat(),
            "artifacts": [],
        }

    def train(self, model, X_train, y_train, X_val=None, y_val=None,
              config: Dict = None) -> Dict:
        """Train a model with full tracking."""
        self.metadata["config"] = config or {}
        self.metadata["train_samples"] = len(X_train)
        self.metadata["n_features"] = X_train.shape[1] if hasattr(X_train, "shape") else len(X_train[0])
        data_hash = hashlib.md5(pd.util.hash_pandas_object(X_train).values.tobytes()).hexdigest()
        self.metadata["data_hash"] = data_hash
        logger.info("Training %s on %d samples (data_hash=%s)",
                     type(model).__name__, len(X_train), data_hash[:8])
        model.fit(X_train, y_train)
        train_pred = model.predict(X_train)
        self.metadata["train_metrics"] = {
            "mae": round(float(np.mean(np.abs(y_train - train_pred))), 2),
            "r2": round(float(1 - np.sum((y_train - train_pred) ** 2) / np.sum((y_train - y_train.mean()) ** 2)), 4),
        }
        if X_val is not None and y_val is not None:
            val_pred = model.predict(X_val)
            self.metadata["val_metrics"] = {
                "mae": round(float(np.mean(np.abs(y_val - val_pred))), 2),
                "r2": round(float(1 - np.sum((y_val - val_pred) ** 2) / np.sum((y_val - y_val.mean()) ** 2)), 4),
            }
        self.metadata["end_time"] = datetime.utcnow().isoformat()
        self._save_metadata()
        return self.metadata

    def _save_metadata(self):
        """Save training metadata to disk."""
        path = os.path.join(self.output_dir, f"{self.experiment_name}_{self.run_id}_metadata.json")
        with open(path, "w") as f:
            json.dump(self.metadata, f, indent=2, default=str)
        self.metadata["artifacts"].append(path)

    def save_model(self, model, name: str = "model") -> str:
        """Save trained model to disk."""
        import joblib
        path = os.path.join(self.output_dir, f"{self.experiment_name}_{self.run_id}_{name}.pkl")
        joblib.dump(model, path)
        self.metadata["artifacts"].append(path)
        self._save_metadata()
        return path

    def save_report(self, report: Dict) -> str:
        """Save evaluation report."""
        path = os.path.join(self.output_dir, f"{self.experiment_name}_{self.run_id}_report.json")
        with open(path, "w") as f:
            json.dump(report, f, indent=2, default=str)
        return path
