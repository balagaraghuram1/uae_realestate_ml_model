"""Batch prediction processor for large-scale inference."""
import logging
import numpy as np
import pandas as pd
from typing import Dict, Optional, Callable
from concurrent.futures import ProcessPoolExecutor, as_completed

logger = logging.getLogger(__name__)

class BatchPredictor:
    """Process batch predictions with chunking and parallelism."""

    def __init__(self, model, chunk_size: int = 1000, n_workers: int = 4):
        self.model = model
        self.chunk_size = chunk_size
        self.n_workers = n_workers
        self._stats = {"total": 0, "processed": 0, "errors": 0}

    def predict_batch(self, df: pd.DataFrame, feature_cols: list,
                      output_col: str = "prediction") -> pd.DataFrame:
        """Run batch predictions on a DataFrame."""
        self._stats["total"] = len(df)
        chunks = [df[i:i + self.chunk_size] for i in range(0, len(df), self.chunk_size)]
        results = []
        for i, chunk in enumerate(chunks):
            try:
                X = chunk[feature_cols].values
                predictions = self.model.predict(X)
                chunk_result = chunk.copy()
                chunk_result[output_col] = predictions
                results.append(chunk_result)
                self._stats["processed"] += len(chunk)
                logger.debug("Processed chunk %d/%d (%d rows)", i + 1, len(chunks), len(chunk))
            except Exception as e:
                logger.error("Chunk %d failed: %s", i + 1, e)
                self._stats["errors"] += len(chunk)
        if results:
            return pd.concat(results, ignore_index=True)
        return df

    def predict_with_confidence(self, df: pd.DataFrame, feature_cols: list,
                                n_bootstraps: int = 100) -> pd.DataFrame:
        """Generate predictions with confidence intervals."""
        X = df[feature_cols].values
        predictions = []
        for _ in range(n_bootstraps):
            indices = np.random.choice(len(X), size=len(X), replace=True)
            preds = self.model.predict(X[indices])
            predictions.append(preds)
        predictions = np.array(predictions)
        df_result = df.copy()
        df_result["prediction_mean"] = predictions.mean(axis=0)
        df_result["prediction_std"] = predictions.std(axis=0)
        df_result["prediction_lower"] = np.percentile(predictions, 5, axis=0)
        df_result["prediction_upper"] = np.percentile(predictions, 95, axis=0)
        return df_result

    @property
    def stats(self) -> Dict:
        return self._stats.copy()
