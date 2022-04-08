"""Orchestrate multiple data collectors with scheduling."""
import logging, time
from typing import Dict, List, Callable
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

logger = logging.getLogger(__name__)

class CollectorOrchestrator:
    """Manage and schedule multiple data collection tasks."""

    def __init__(self, max_workers: int = 4):
        self.collectors: Dict[str, Dict] = {}
        self.max_workers = max_workers
        self._results: Dict[str, Dict] = {}

    def register_collector(self, name: str, func: Callable, schedule: str = "daily",
                           priority: int = 0, enabled: bool = True):
        """Register a data collector."""
        self.collectors[name] = {
            "func": func, "schedule": schedule,
            "priority": priority, "enabled": enabled,
            "last_run": None, "run_count": 0, "error_count": 0,
        }
        logger.info("Registered collector: %s (schedule=%s, priority=%d)", name, schedule, priority)

    def run_collector(self, name: str) -> Dict:
        """Run a single collector."""
        collector = self.collectors.get(name)
        if not collector:
            return {"error": f"Collector '{name}' not found"}
        start = time.time()
        try:
            result = collector["func"]()
            duration = time.time() - start
            collector["last_run"] = datetime.utcnow().isoformat()
            collector["run_count"] += 1
            self._results[name] = {
                "status": "success", "duration": round(duration, 2),
                "records": result if isinstance(result, int) else len(result) if hasattr(result, "__len__") else 0,
            }
            logger.info("Collector %s completed in %.2fs", name, duration)
            return self._results[name]
        except Exception as e:
            duration = time.time() - start
            collector["error_count"] += 1
            self._results[name] = {"status": "failed", "error": str(e), "duration": round(duration, 2)}
            logger.error("Collector %s failed: %s", name, e)
            return self._results[name]

    def run_all(self, schedule_filter: str = None) -> Dict:
        """Run all enabled collectors, optionally filtered by schedule."""
        to_run = []
        for name, config in self.collectors.items():
            if not config["enabled"]:
                continue
            if schedule_filter and config["schedule"] != schedule_filter:
                continue
            to_run.append((config["priority"], name))
        to_run.sort(reverse=True)
        results = {}
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {executor.submit(self.run_collector, name): name for _, name in to_run}
            for future in as_completed(futures):
                name = futures[future]
                try:
                    results[name] = future.result()
                except Exception as e:
                    results[name] = {"status": "error", "error": str(e)}
        return results

    def get_status(self) -> Dict:
        """Get status of all collectors."""
        return {
            name: {
                "enabled": config["enabled"],
                "schedule": config["schedule"],
                "last_run": config["last_run"],
                "run_count": config["run_count"],
                "error_count": config["error_count"],
            }
            for name, config in self.collectors.items()
        }
