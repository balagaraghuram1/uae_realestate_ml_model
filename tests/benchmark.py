"""Performance benchmarking for ML models."""
import time, logging
import numpy as np
from typing import Dict, Callable

logger = logging.getLogger(__name__)

class BenchmarkSuite:
    """Benchmark ML model performance."""

    def __init__(self):
        self.results: Dict[str, Dict] = {}

    def benchmark_inference(self, model, X: np.ndarray, n_runs: int = 100) -> Dict:
        """Benchmark model inference speed."""
        latencies = []
        for _ in range(n_runs):
            start = time.perf_counter()
            model.predict(X[:1])
            latencies.append(time.perf_counter() - start)
        latencies = np.array(latencies) * 1000
        return {
            "mean_ms": round(float(latencies.mean()), 2),
            "std_ms": round(float(latencies.std()), 2),
            "p50_ms": round(float(np.percentile(latencies, 50)), 2),
            "p95_ms": round(float(np.percentile(latencies, 95)), 2),
            "p99_ms": round(float(np.percentile(latencies, 99)), 2),
            "throughput_per_sec": round(1000 / latencies.mean(), 0) if latencies.mean() > 0 else 0,
        }

    def benchmark_training(self, train_fn: Callable, *args, **kwargs) -> Dict:
        """Benchmark model training time."""
        start = time.perf_counter()
        model = train_fn(*args, **kwargs)
        duration = time.perf_counter() - start
        return {
            "training_time_seconds": round(duration, 2),
            "model_type": type(model).__name__,
        }

    def compare_models(self, models: Dict[str, object], X: np.ndarray) -> Dict:
        """Compare inference speed of multiple models."""
        results = {}
        for name, model in models.items():
            results[name] = self.benchmark_inference(model, X)
        return results
