import numpy as np
from typing import Dict, Any, List, Optional, Tuple
from sklearn.metrics import (
    mean_absolute_error, mean_squared_error, r2_score,
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, confusion_matrix, classification_report,
    silhouette_score, davies_bouldin_score, calinski_harabasz_score,
)


class MetricsCalculator:
    @staticmethod
    def regression_metrics(y_true: np.ndarray, y_pred: np.ndarray) -> Dict[str, float]:
        y_true, y_pred = np.array(y_true), np.array(y_pred)
        mae = mean_absolute_error(y_true, y_pred)
        mse = mean_squared_error(y_true, y_pred)
        rmse = np.sqrt(mse)
        mape = np.mean(np.abs((y_true - y_pred) / np.maximum(np.abs(y_true), 1e-10))) * 100
        return {
            "mae": float(mae),
            "mse": float(mse),
            "rmse": float(rmse),
            "mape_pct": float(mape),
            "r2_score": float(r2_score(y_true, y_pred)),
            "adj_r2_score": 0.0,
            "mean_abs_pct_error": float(mape),
        }

    @staticmethod
    def classification_metrics(y_true: np.ndarray, y_pred: np.ndarray,
                               y_prob: Optional[np.ndarray] = None,
                               average: str = "weighted") -> Dict[str, Any]:
        y_true, y_pred = np.array(y_true), np.array(y_pred)
        metrics = {
            "accuracy": float(accuracy_score(y_true, y_pred)),
            "precision": float(precision_score(y_true, y_pred, average=average, zero_division=0)),
            "recall": float(recall_score(y_true, y_pred, average=average, zero_division=0)),
            "f1_score": float(f1_score(y_true, y_pred, average=average, zero_division=0)),
        }
        if y_prob is not None and len(np.unique(y_true)) == 2:
            try:
                metrics["roc_auc"] = float(roc_auc_score(y_true, y_prob[:, 1] if y_prob.ndim > 1 else y_prob))
            except Exception:
                metrics["roc_auc"] = 0.0
        try:
            cm = confusion_matrix(y_true, y_pred).tolist()
            metrics["confusion_matrix"] = cm
            tp = cm[0][0] if len(cm) > 0 and len(cm[0]) > 0 else 0
            fp = cm[0][1] if len(cm) > 0 and len(cm[0]) > 1 else 0
            fn = cm[1][0] if len(cm) > 1 and len(cm[0]) > 0 else 0
            tn = cm[1][1] if len(cm) > 1 and len(cm[0]) > 1 else 0
            metrics["true_positives"] = tp
            metrics["false_positives"] = fp
            metrics["false_negatives"] = fn
            metrics["true_negatives"] = tn
            sensitivity = tp / (tp + fn) if (tp + fn) > 0 else 0
            specificity = tn / (tn + fp) if (tn + fp) > 0 else 0
            metrics["sensitivity"] = float(sensitivity)
            metrics["specificity"] = float(specificity)
        except Exception:
            pass
        return metrics

    @staticmethod
    def clustering_metrics(X: np.ndarray, labels: np.ndarray) -> Dict[str, float]:
        n_labels = len(set(labels))
        if n_labels < 2 or n_labels >= len(labels):
            return {"silhouette_score": 0.0, "davies_bouldin_score": 0.0, "calinski_harabasz_score": 0.0}
        return {
            "silhouette_score": float(silhouette_score(X, labels)),
            "davies_bouldin_score": float(davies_bouldin_score(X, labels)),
            "calinski_harabasz_score": float(calinski_harabasz_score(X, labels)),
        }

    @staticmethod
    def time_series_metrics(y_true: np.ndarray, y_pred: np.ndarray) -> Dict[str, float]:
        y_true, y_pred = np.array(y_true), np.array(y_pred)
        residuals = y_true - y_pred
        mae = mean_absolute_error(y_true, y_pred)
        rmse = np.sqrt(mean_squared_error(y_true, y_pred))
        mape = np.mean(np.abs(residuals / np.maximum(np.abs(y_true), 1e-10))) * 100
        return {
            "mae": float(mae),
            "rmse": float(rmse),
            "mape_pct": float(mape),
            "mean_residual": float(np.mean(residuals)),
            "std_residual": float(np.std(residuals)),
            "max_error": float(np.max(np.abs(residuals))),
            "theil_u": float(np.sqrt(np.mean(residuals ** 2)) / (np.sqrt(np.mean(y_true ** 2)) + np.sqrt(np.mean(y_pred ** 2)))),
        }

    @staticmethod
    def cross_validation_scores(scores: List[float]) -> Dict[str, float]:
        scores = np.array(scores)
        return {
            "mean_score": float(np.mean(scores)),
            "std_score": float(np.std(scores)),
            "min_score": float(np.min(scores)),
            "max_score": float(np.max(scores)),
            "score_range": float(np.ptp(scores)),
            "cv_coefficient": float(np.std(scores) / np.mean(scores)) if np.mean(scores) != 0 else 0,
        }
