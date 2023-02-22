import numpy as np
import pandas as pd
from typing import Dict, Any, Optional, List, Tuple, Callable
from dataclasses import dataclass, field


@dataclass
class TrainingConfig:
    model_type: str
    hyperparameters: Dict[str, Any] = field(default_factory=dict)
    test_size: float = 0.2
    validation_size: float = 0.1
    random_state: int = 42
    cv_folds: int = 5
    scoring: str = "r2"
    early_stopping: bool = False
    early_stopping_rounds: int = 10
    feature_selection: bool = False
    feature_selection_k: Optional[int] = None
    handle_imbalance: bool = False
    scale_features: bool = True
    save_model: bool = True
    experiment_name: Optional[str] = None


@dataclass
class TrainingResult:
    model: Any = None
    metrics: Dict[str, float] = field(default_factory=dict)
    cv_scores: List[float] = field(default_factory=list)
    feature_importance: Optional[Dict[str, float]] = None
    train_score: float = 0.0
    test_score: float = 0.0
    training_time: float = 0.0
    config: Optional[TrainingConfig] = None


class TrainingPipeline:
    def __init__(self, config: TrainingConfig):
        self.config = config
        self.steps: List[Callable] = []

    def add_step(self, step: Callable) -> None:
        self.steps.append(step)

    def run(self, X: np.ndarray, y: np.ndarray) -> TrainingResult:
        data = {"X": X, "y": y, "config": self.config}
        for step in self.steps:
            data = step(data)
        return TrainingResult(
            model=data.get("model"),
            metrics=data.get("metrics", {}),
            cv_scores=data.get("cv_scores", []),
            feature_importance=data.get("feature_importance"),
            train_score=data.get("train_score", 0),
            test_score=data.get("test_score", 0),
            training_time=data.get("training_time", 0),
            config=self.config,
        )


class InferencePipeline:
    def __init__(self, model, preprocessors: Optional[List[Callable]] = None):
        self.model = model
        self.preprocessors = preprocessors or []

    def predict(self, features: np.ndarray) -> np.ndarray:
        data = features
        for preprocessor in self.preprocessors:
            data = preprocessor(data)
        return self.model.predict(data)

    def predict_proba(self, features: np.ndarray) -> np.ndarray:
        data = features
        for preprocessor in self.preprocessors:
            data = preprocessor(data)
        if hasattr(self.model, "predict_proba"):
            return self.model.predict_proba(data)
        return self.model.predict(data)

    def explain_prediction(self, features: np.ndarray) -> Dict[str, Any]:
        pred = self.predict(features)
        return {
            "prediction": pred.tolist() if hasattr(pred, "tolist") else pred,
            "features_used": len(features) if hasattr(features, "__len__") else 0,
        }


class FeaturePipeline:
    def __init__(self):
        self.transformers: List[Tuple[str, Callable]] = []

    def add_transformer(self, name: str, transformer: Callable) -> None:
        self.transformers.append((name, transformer))

    def fit_transform(self, X: pd.DataFrame) -> np.ndarray:
        data = X.copy()
        for name, transformer in self.transformers:
            data = transformer.fit_transform(data) if hasattr(transformer, "fit_transform") else transformer(data)
        return np.array(data)

    def transform(self, X: pd.DataFrame) -> np.ndarray:
        data = X.copy()
        for name, transformer in self.transformers:
            data = transformer.transform(data) if hasattr(transformer, "transform") else transformer(data)
        return np.array(data)
