import uuid
import json
from typing import Dict, Any, Optional, List
from datetime import datetime
from dataclasses import dataclass, field


@dataclass
class ExperimentRun:
    run_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    experiment_name: str = ""
    status: str = "running"
    params: Dict[str, Any] = field(default_factory=dict)
    metrics: Dict[str, float] = field(default_factory=dict)
    artifacts: List[str] = field(default_factory=list)
    tags: Dict[str, str] = field(default_factory=dict)
    start_time: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    end_time: Optional[str] = None
    model_id: Optional[str] = None


class ExperimentTracker:
    def __init__(self, storage_path: str = "experiments"):
        self.storage_path = storage_path
        self._runs: Dict[str, ExperimentRun] = {}

    def create_run(self, experiment_name: str,
                   params: Optional[Dict[str, Any]] = None,
                   tags: Optional[Dict[str, str]] = None) -> ExperimentRun:
        run = ExperimentRun(
            experiment_name=experiment_name,
            params=params or {},
            tags=tags or {},
        )
        self._runs[run.run_id] = run
        return run

    def log_params(self, run_id: str, params: Dict[str, Any]) -> bool:
        run = self._runs.get(run_id)
        if not run:
            return False
        run.params.update(params)
        return True

    def log_metrics(self, run_id: str, metrics: Dict[str, float], step: Optional[int] = None) -> bool:
        run = self._runs.get(run_id)
        if not run:
            return False
        prefixed = {f"{k}_step_{step}" if step is not None else k: v for k, v in metrics.items()}
        run.metrics.update(prefixed)
        return True

    def log_artifact(self, run_id: str, artifact_path: str) -> bool:
        run = self._runs.get(run_id)
        if not run:
            return False
        run.artifacts.append(artifact_path)
        return True

    def set_tags(self, run_id: str, tags: Dict[str, str]) -> bool:
        run = self._runs.get(run_id)
        if not run:
            return False
        run.tags.update(tags)
        return True

    def finish_run(self, run_id: str, status: str = "completed") -> bool:
        run = self._runs.get(run_id)
        if not run:
            return False
        run.status = status
        run.end_time = datetime.utcnow().isoformat()
        return True

    def get_run(self, run_id: str) -> Optional[ExperimentRun]:
        return self._runs.get(run_id)

    def list_runs(self, experiment_name: Optional[str] = None,
                  status: Optional[str] = None) -> List[ExperimentRun]:
        results = list(self._runs.values())
        if experiment_name:
            results = [r for r in results if r.experiment_name == experiment_name]
        if status:
            results = [r for r in results if r.status == status]
        return sorted(results, key=lambda r: r.start_time, reverse=True)

    def compare_runs(self, run_ids: List[str]) -> Dict[str, Any]:
        runs = [self._runs[rid] for rid in run_ids if rid in self._runs]
        if not runs:
            return {}
        all_metrics = set()
        for run in runs:
            all_metrics.update(run.metrics.keys())
        comparison = {"runs": [], "metrics": {}}
        for run in runs:
            run_data = {"run_id": run.run_id, "experiment": run.experiment_name, "params": run.params, "metrics": run.metrics}
            comparison["runs"].append(run_data)
        for metric in sorted(all_metrics):
            values = [run.metrics.get(metric) for run in runs if metric in run.metrics]
            if values:
                comparison["metrics"][metric] = {
                    "min": min(values), "max": max(values),
                    "mean": sum(values) / len(values),
                    "values": {run.run_id: run.metrics.get(metric) for run in runs if metric in run.metrics},
                }
        return comparison
