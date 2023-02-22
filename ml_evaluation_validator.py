import numpy as np
from typing import Dict, Any, List, Optional, Callable, Tuple
from sklearn.model_selection import (
    KFold, StratifiedKFold, TimeSeriesSplit,
    cross_val_score, cross_validate, GridSearchCV,
    RandomizedSearchCV, learning_curve,
)
from dataclasses import dataclass, field


@dataclass
class CVResult:
    scores: List[float]
    mean_score: float
    std_score: float
    fit_times: List[float]
    score_times: List[float]
    train_scores: Optional[List[List[float]]] = None
    test_scores: Optional[List[List[float]]] = None


class CrossValidator:
    def __init__(self, n_folds: int = 5, shuffle: bool = True, random_state: int = 42):
        self.n_folds = n_folds
        self.shuffle = shuffle
        self.random_state = random_state

    def kfold_cv(self, model, X: np.ndarray, y: np.ndarray,
                 scoring: str = "r2", return_train_score: bool = False) -> CVResult:
        cv = KFold(n_splits=self.n_folds, shuffle=self.shuffle, random_state=self.random_state)
        return self._run_cv(model, X, y, cv, scoring, return_train_score)

    def stratified_kfold_cv(self, model, X: np.ndarray, y: np.ndarray,
                            scoring: str = "accuracy",
                            return_train_score: bool = False) -> CVResult:
        cv = StratifiedKFold(n_splits=self.n_folds, shuffle=self.shuffle, random_state=self.random_state)
        return self._run_cv(model, X, y, cv, scoring, return_train_score)

    def time_series_cv(self, model, X: np.ndarray, y: np.ndarray,
                       scoring: str = "neg_mean_squared_error",
                       return_train_score: bool = False) -> CVResult:
        cv = TimeSeriesSplit(n_splits=self.n_folds)
        return self._run_cv(model, X, y, cv, scoring, return_train_score)

    def _run_cv(self, model, X: np.ndarray, y: np.ndarray,
                cv, scoring: str, return_train_score: bool) -> CVResult:
        cv_results = cross_validate(
            model, X, y, cv=cv, scoring=scoring,
            return_train_score=return_train_score,
            return_estimator=True,
        )
        return CVResult(
            scores=cv_results["test_score"].tolist(),
            mean_score=float(np.mean(cv_results["test_score"])),
            std_score=float(np.std(cv_results["test_score"])),
            fit_times=cv_results["fit_time"].tolist(),
            score_times=cv_results["score_time"].tolist(),
            train_scores=cv_results.get("train_score", [None]),
            test_scores=None,
        )


class HyperparameterTuner:
    def __init__(self, cv_folds: int = 5, random_state: int = 42):
        self.cv_folds = cv_folds
        self.random_state = random_state
        self.best_params_ = None
        self.best_score_ = None
        self.cv_results_ = None

    def grid_search(self, model, param_grid: Dict[str, List[Any]],
                    X: np.ndarray, y: np.ndarray, scoring: str = "r2",
                    verbose: int = 0, n_jobs: int = -1) -> Dict[str, Any]:
        search = GridSearchCV(
            model, param_grid, cv=self.cv_folds, scoring=scoring,
            verbose=verbose, n_jobs=n_jobs, return_train_score=True,
        )
        search.fit(X, y)
        self.best_params_ = search.best_params_
        self.best_score_ = search.best_score_
        self.cv_results_ = search.cv_results_
        return {
            "best_params": search.best_params_,
            "best_score": float(search.best_score_),
            "best_estimator": search.best_estimator_,
            "all_results": [
                {
                    "params": p,
                    "mean_test_score": float(s),
                    "std_test_score": float(std),
                }
                for p, s, std in zip(
                    search.cv_results_["params"],
                    search.cv_results_["mean_test_score"],
                    search.cv_results_["std_test_score"],
                )
            ],
        }

    def random_search(self, model, param_distributions: Dict[str, Any],
                      X: np.ndarray, y: np.ndarray, n_iter: int = 100,
                      scoring: str = "r2", verbose: int = 0,
                      n_jobs: int = -1) -> Dict[str, Any]:
        search = RandomizedSearchCV(
            model, param_distributions, n_iter=n_iter, cv=self.cv_folds,
            scoring=scoring, verbose=verbose, n_jobs=n_jobs,
            random_state=self.random_state, return_train_score=True,
        )
        search.fit(X, y)
        self.best_params_ = search.best_params_
        self.best_score_ = search.best_score_
        return {
            "best_params": search.best_params_,
            "best_score": float(search.best_score_),
            "best_estimator": search.best_estimator_,
        }
