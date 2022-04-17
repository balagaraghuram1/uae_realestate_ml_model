"""Hyperparameter tuning with Optuna and GridSearch."""
import logging
from typing import Dict, Callable, Optional, Any
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class TuningResult:
    """Results from hyperparameter tuning."""
    best_params: Dict[str, Any]
    best_score: float
    n_trials: int
    all_trials: list

class HyperparameterTuner:
    """Tune model hyperparameters using multiple strategies."""

    def __init__(self, objective_fn: Callable, direction: str = "maximize"):
        self.objective_fn = objective_fn
        self.direction = direction
        self.results: Optional[TuningResult] = None

    def tune_optuna(self, param_space: Dict, n_trials: int = 50,
                    timeout: int = 3600) -> TuningResult:
        """Tune using Optuna Bayesian optimization."""
        try:
            import optuna
            optuna.logging.set_verbosity(optuna.logging.WARNING)
            study = optuna.create_study(direction=self.direction)
            study.optimize(self.objective_fn, n_trials=n_trials, timeout=timeout)
            self.results = TuningResult(
                best_params=study.best_params,
                best_score=study.best_value,
                n_trials=len(study.trials),
                all_trials=[{"params": t.params, "value": t.value} for t in study.trials],
            )
            logger.info("Optuna tuning complete: best_score=%.4f", study.best_value)
            return self.results
        except ImportError:
            logger.warning("Optuna not installed, falling back to grid search")
            return self.tune_grid(param_space)

    def tune_grid(self, param_grid: Dict) -> TuningResult:
        """Tune using exhaustive grid search."""
        import itertools
        keys = list(param_grid.keys())
        values = list(param_grid.values())
        combos = list(itertools.product(*values))
        best_score = float("-inf") if self.direction == "maximize" else float("inf")
        best_params = {}
        all_trials = []
        for combo in combos:
            params = dict(zip(keys, combo))
            try:
                score = self.objective_fn(params)
                all_trials.append({"params": params, "value": score})
                if self.direction == "maximize" and score > best_score:
                    best_score = score
                    best_params = params
                elif self.direction == "minimize" and score < best_score:
                    best_score = score
                    best_params = params
            except Exception as e:
                logger.warning("Trial failed: %s", e)
        self.results = TuningResult(
            best_params=best_params, best_score=best_score,
            n_trials=len(all_trials), all_trials=all_trials,
        )
        return self.results

    def tune_random(self, param_space: Dict, n_iter: int = 100) -> TuningResult:
        """Tune using random search."""
        import random
        best_score = float("-inf") if self.direction == "maximize" else float("inf")
        best_params = {}
        all_trials = []
        for _ in range(n_iter):
            params = {k: random.choice(v) if isinstance(v, list) else v
                     for k, v in param_space.items()}
            try:
                score = self.objective_fn(params)
                all_trials.append({"params": params, "value": score})
                if self.direction == "maximize" and score > best_score:
                    best_score = score
                    best_params = params
                elif self.direction == "minimize" and score < best_score:
                    best_score = score
                    best_params = params
            except Exception as e:
                logger.warning("Trial failed: %s", e)
        self.results = TuningResult(
            best_params=best_params, best_score=best_score,
            n_trials=n_iter, all_trials=all_trials,
        )
        return self.results
