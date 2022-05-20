"""Automated model retraining scheduler."""
import logging, time
from typing import Dict, Callable, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class RetrainJob:
    """Model retraining job definition."""
    model_name: str
    train_fn: Callable
    eval_fn: Callable
    threshold: float = 0.05
    interval_hours: int = 24
    last_run: Optional[datetime] = None
    last_score: Optional[float] = None
    enabled: bool = True

class RetrainScheduler:
    """Schedule automatic model retraining based on performance drift."""

    def __init__(self):
        self.jobs: Dict[str, RetrainJob] = {}
        self.history: list = []

    def register_job(self, model_name: str, train_fn: Callable,
                     eval_fn: Callable, threshold: float = 0.05,
                     interval_hours: int = 24):
        """Register a model for automatic retraining."""
        self.jobs[model_name] = RetrainJob(
            model_name=model_name, train_fn=train_fn,
            eval_fn=eval_fn, threshold=threshold,
            interval_hours=interval_hours,
        )
        logger.info("Registered retrain job: %s (interval=%dh)", model_name, interval_hours)

    def check_and_retrain(self) -> Dict:
        """Check all models and retrain if needed."""
        results = {}
        for name, job in self.jobs.items():
            if not job.enabled:
                continue
            should_retrain = False
            if job.last_run is None:
                should_retrain = True
            elif datetime.utcnow() - job.last_run > timedelta(hours=job.interval_hours):
                should_retrain = True
            if should_retrain:
                result = self._run_retrain(job)
                results[name] = result
        return results

    def _run_retrain(self, job: RetrainJob) -> Dict:
        """Execute a retraining job."""
        start = time.time()
        try:
            model = job.train_fn()
            score = job.eval_fn(model)
            duration = time.time() - start
            improved = job.last_score is None or score > job.last_score * (1 + job.threshold)
            job.last_run = datetime.utcnow()
            job.last_score = score
            entry = {
                "model": job.model_name,
                "score": score,
                "previous_score": job.last_score,
                "improved": improved,
                "duration": round(duration, 2),
                "timestamp": datetime.utcnow().isoformat(),
            }
            self.history.append(entry)
            if improved:
                logger.info("Model %s retrained: score=%.4f (improved)", job.model_name, score)
            else:
                logger.info("Model %s retrained: score=%.4f (no improvement)", job.model_name, score)
            return entry
        except Exception as e:
            duration = time.time() - start
            logger.error("Retrain failed for %s: %s", job.model_name, e)
            return {"model": job.model_name, "error": str(e), "duration": round(duration, 2)}

    def get_status(self) -> Dict:
        """Get status of all retraining jobs."""
        return {
            name: {
                "enabled": job.enabled,
                "interval_hours": job.interval_hours,
                "last_run": job.last_run.isoformat() if job.last_run else None,
                "last_score": job.last_score,
            }
            for name, job in self.jobs.items()
        }
