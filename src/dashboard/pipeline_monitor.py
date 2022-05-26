"""Pipeline monitoring dashboard data provider."""
import logging
from typing import Dict, List
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class PipelineMonitor:
    """Monitor data pipeline health and performance."""

    def __init__(self):
        self.run_history: List[Dict] = []
        self.alerts: List[Dict] = []

    def record_run(self, pipeline_name: str, status: str, duration: float,
                   records_processed: int = 0, errors: int = 0):
        """Record a pipeline run."""
        entry = {
            "pipeline": pipeline_name,
            "status": status,
            "duration": round(duration, 2),
            "records": records_processed,
            "errors": errors,
            "timestamp": datetime.utcnow().isoformat(),
        }
        self.run_history.append(entry)
        if status == "failed" or errors > 0:
            self.alerts.append({**entry, "severity": "error" if status == "failed" else "warning"})

    def get_dashboard(self, hours: int = 24) -> Dict:
        """Get monitoring dashboard data."""
        cutoff = datetime.utcnow() - timedelta(hours=hours)
        recent = [r for r in self.run_history
                  if datetime.fromisoformat(r["timestamp"]) > cutoff]
        total_runs = len(recent)
        successful = sum(1 for r in recent if r["status"] == "success")
        total_records = sum(r["records"] for r in recent)
        total_errors = sum(r["errors"] for r in recent)
        avg_duration = sum(r["duration"] for r in recent) / max(total_runs, 1)
        return {
            "summary": {
                "total_runs": total_runs,
                "success_rate": round(successful / max(total_runs, 1) * 100, 1),
                "total_records": total_records,
                "total_errors": total_errors,
                "avg_duration": round(avg_duration, 2),
            },
            "recent_runs": recent[-20:],
            "recent_alerts": self.alerts[-10:],
            "period_hours": hours,
        }
