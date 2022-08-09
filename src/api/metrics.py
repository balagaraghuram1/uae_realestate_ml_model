"""Prometheus metrics collection for API monitoring."""
import time, logging
from typing import Dict
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)

@dataclass
class Counter:
    """Simple counter metric."""
    name: str
    help_text: str = ""
    value: int = 0
    labels: Dict[str, str] = field(default_factory=dict)

    def inc(self, amount: int = 1):
        self.value += amount

@dataclass
class Histogram:
    """Simple histogram metric."""
    name: str
    help_text: str = ""
    buckets: list = field(default_factory=list)
    _values: list = field(default_factory=list)

    def observe(self, value: float):
        self._values.append(value)

    @property
    def count(self) -> int:
        return len(self._values)

    @property
    def mean(self) -> float:
        return sum(self._values) / len(self._values) if self._values else 0

class MetricsCollector:
    """Collect and expose Prometheus-compatible metrics."""

    def __init__(self):
        self.request_count = Counter("http_requests_total", "Total HTTP requests")
        self.request_duration = Histogram("http_request_duration_seconds", "Request duration")
        self.prediction_count = Counter("ml_predictions_total", "Total predictions")
        self.prediction_duration = Histogram("ml_prediction_duration_seconds", "Prediction duration")
        self.model_errors = Counter("ml_errors_total", "Total ML errors")
        self._start_time = time.time()

    def record_request(self, method: str, path: str, status: int, duration: float):
        """Record an HTTP request."""
        self.request_count.inc()
        self.request_duration.observe(duration)

    def record_prediction(self, model: str, duration: float, success: bool):
        """Record an ML prediction."""
        self.prediction_count.inc()
        self.prediction_duration.observe(duration)
        if not success:
            self.model_errors.inc()

    def export_prometheus(self) -> str:
        """Export metrics in Prometheus text format."""
        lines = []
        lines.append(f"# HELP {self.request_count.name} {self.request_count.help_text}")
        lines.append(f"# TYPE {self.request_count.name} counter")
        lines.append(f"{self.request_count.name} {self.request_count.value}")
        lines.append(f"# HELP {self.prediction_duration.name} {self.prediction_duration.help_text}")
        lines.append(f"# TYPE {self.prediction_duration.name} histogram")
        lines.append(f"{self.prediction_duration.name}_count {self.prediction_duration.count}")
        lines.append(f"{self.prediction_duration.name}_sum {sum(self.prediction_duration._values):.4f}")
        return "\n".join(lines)

metrics = MetricsCollector()
