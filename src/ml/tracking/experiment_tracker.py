"""Experiment tracking system for ML runs."""
import os, json, time, uuid, logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)

@dataclass
class ExperimentRun:
    """Single experiment run."""
    run_id: str
    experiment_name: str
    status: str = "running"
    metrics: Dict[str, float] = field(default_factory=dict)
    parameters: Dict[str, Any] = field(default_factory=dict)
    artifacts: List[str] = field(default_factory=list)
    tags: Dict[str, str] = field(default_factory=dict)
    start_time: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    end_time: Optional[str] = None
    duration_seconds: Optional[float] = None

    def log_metric(self, name: str, value: float):
        self.metrics[name] = value

    def log_params(self, params: Dict[str, Any]):
        self.parameters.update(params)

    def log_artifact(self, path: str):
        self.artifacts.append(path)

class ExperimentTracker:
    """Track and log ML experiments with runs, metrics, and parameters."""

    def __init__(self, tracking_dir: str = "experiments"):
        self.tracking_dir = Path(tracking_dir)
        self.tracking_dir.mkdir(parents=True, exist_ok=True)
        self._runs: Dict[str, ExperimentRun] = {}
        self._active_run: Optional[ExperimentRun] = None

    def create_experiment(self, name: str) -> str:
        """Create a new experiment."""
        exp_dir = self.tracking_dir / name
        exp_dir.mkdir(parents=True, exist_ok=True)
        logger.info("Created experiment: %s", name)
        return str(exp_dir)

    def start_run(self, experiment_name: str, run_name: Optional[str] = None) -> str:
        """Start a new run within an experiment."""
        run_id = run_name or f"run_{uuid.uuid4().hex[:8]}"
        run = ExperimentRun(run_id=run_id, experiment_name=experiment_name)
        self._runs[run_id] = run
        self._active_run = run
        logger.info("Started run %s in experiment %s", run_id, experiment_name)
        return run_id

    def log_metric(self, name: str, value: float, step: Optional[int] = None):
        """Log a metric to the active run."""
        if self._active_run:
            self._active_run.log_metric(name, value)

    def log_metrics(self, metrics: Dict[str, float]):
        """Log multiple metrics at once."""
        if self._active_run:
            self._active_run.metrics.update(metrics)

    def log_params(self, params: Dict[str, Any]):
        """Log parameters to the active run."""
        if self._active_run:
            self._active_run.log_params(params)

    def log_artifact(self, local_path: str):
        """Log an artifact file path."""
        if self._active_run:
            self._active_run.log_artifact(local_path)

    def end_run(self, status: str = "completed"):
        """End the active run."""
        if self._active_run:
            self._active_run.end_time = datetime.utcnow().isoformat()
            self._active_run.status = status
            start = datetime.fromisoformat(self._active_run.start_time)
            end = datetime.fromisoformat(self._active_run.end_time)
            self._active_run.duration_seconds = (end - start).total_seconds()
            self._save_run(self._active_run)
            logger.info("Ended run %s (%s, %.2fs)",
                        self._active_run.run_id, status, self._active_run.duration_seconds)
            self._active_run = None

    def _save_run(self, run: ExperimentRun):
        """Persist run data to disk."""
        exp_dir = self.tracking_dir / run.experiment_name
        exp_dir.mkdir(parents=True, exist_ok=True)
        run_file = exp_dir / f"{run.run_id}.json"
        with open(run_file, "w") as f:
            json.dump(run.__dict__, f, indent=2, default=str)

    def get_run(self, run_id: str) -> Optional[ExperimentRun]:
        """Retrieve a run by ID."""
        return self._runs.get(run_id)

    def search_runs(self, experiment_name: str, metric_filter: Optional[Dict] = None) -> List:
        """Search runs by experiment and optional metric filters."""
        runs = [r for r in self._runs.values() if r.experiment_name == experiment_name]
        if metric_filter:
            for metric_name, threshold in metric_filter.items():
                runs = [r for r in runs if r.metrics.get(metric_name, 0) >= threshold]
        return sorted(runs, key=lambda r: r.start_time, reverse=True)

    def compare_runs(self, run_ids: List[str]) -> Dict:
        """Compare multiple runs side by side."""
        comparison = {"runs": {}, "best": {}}
        for rid in run_ids:
            run = self._runs.get(rid)
            if run:
                comparison["runs"][rid] = {
                    "metrics": run.metrics,
                    "parameters": run.parameters,
                    "duration": run.duration_seconds,
                }
        if comparison["runs"]:
            best_metric = {}
            for rid, data in comparison["runs"].items():
                for m, v in data["metrics"].items():
                    if m not in best_metric or v > best_metric[m][1]:
                        best_metric[m] = (rid, v)
            comparison["best"] = {k: {"run_id": v[0], "value": v[1]} for k, v in best_metric.items()}
        return comparison
