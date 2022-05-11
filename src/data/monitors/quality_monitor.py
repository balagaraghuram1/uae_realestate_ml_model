"""Real-time data quality monitoring."""
import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)

@dataclass
class QualityCheck:
    """Single quality check definition."""
    name: str
    check_type: str
    threshold: float
    severity: str = "warning"
    last_run: Optional[datetime] = None
    last_result: Optional[bool] = None
    failure_count: int = 0

class DataQualityMonitor:
    """Monitor data quality across the pipeline."""

    def __init__(self):
        self.checks: List[QualityCheck] = []
        self.alerts: List[Dict] = []
        self.metrics: Dict[str, List] = {}

    def add_check(self, name: str, check_type: str, threshold: float,
                  severity: str = "warning"):
        """Add a quality check."""
        self.checks.append(QualityCheck(
            name=name, check_type=check_type,
            threshold=threshold, severity=severity,
        ))

    def run_checks(self, data_stats: Dict) -> Dict:
        """Run all quality checks against current data stats."""
        results = []
        for check in self.checks:
            value = data_stats.get(check.check_type, 0)
            passed = value >= check.threshold if check.severity == "warning" else value <= check.threshold
            check.last_run = datetime.utcnow()
            check.last_result = passed
            if not passed:
                check.failure_count += 1
                self._create_alert(check, value)
            results.append({
                "check": check.name,
                "type": check.check_type,
                "value": value,
                "threshold": check.threshold,
                "passed": passed,
                "severity": check.severity,
            })
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "total_checks": len(results),
            "passed": sum(1 for r in results if r["passed"]),
            "failed": sum(1 for r in results if not r["passed"]),
            "results": results,
        }

    def _create_alert(self, check: QualityCheck, actual_value: float):
        """Create an alert for a failed quality check."""
        alert = {
            "timestamp": datetime.utcnow().isoformat(),
            "check": check.name,
            "severity": check.severity,
            "message": f"Quality check '{check.name}' failed: {actual_value} vs threshold {check.threshold}",
            "failure_count": check.failure_count,
        }
        self.alerts.append(alert)
        logger.warning("Quality alert: %s", alert["message"])

    def get_dashboard(self) -> Dict:
        """Get quality metrics dashboard."""
        return {
            "total_checks": len(self.checks),
            "checks_passing": sum(1 for c in self.checks if c.last_result is True),
            "checks_failing": sum(1 for c in self.checks if c.last_result is False),
            "recent_alerts": self.alerts[-10:],
        }
