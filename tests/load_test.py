"""Load testing configuration for API endpoints."""
import time, logging
from typing import Dict
from concurrent.futures import ThreadPoolExecutor
import requests

logger = logging.getLogger(__name__)

class LoadTester:
    """Simple load testing framework."""

    def __init__(self, base_url: str, n_workers: int = 10, n_requests: int = 100):
        self.base_url = base_url
        self.n_workers = n_workers
        self.n_requests = n_requests
        self.results: list = []

    def _make_request(self, endpoint: str) -> Dict:
        """Make a single HTTP request."""
        start = time.time()
        try:
            resp = requests.get(f"{self.base_url}{endpoint}", timeout=30)
            return {
                "status": resp.status_code,
                "latency": round(time.time() - start, 4),
                "success": resp.status_code == 200,
            }
        except Exception as e:
            return {
                "status": 0, "latency": round(time.time() - start, 4),
                "success": False, "error": str(e),
            }

    def run_test(self, endpoint: str) -> Dict:
        """Run load test against an endpoint."""
        self.results = []
        with ThreadPoolExecutor(max_workers=self.n_workers) as executor:
            futures = [executor.submit(self._make_request, endpoint) for _ in range(self.n_requests)]
            self.results = [f.result() for f in futures]
        latencies = [r["latency"] for r in self.results]
        successes = sum(1 for r in self.results if r["success"])
        return {
            "endpoint": endpoint,
            "total_requests": self.n_requests,
            "successful": successes,
            "failed": self.n_requests - successes,
            "success_rate": round(successes / self.n_requests * 100, 2),
            "avg_latency": round(sum(latencies) / len(latencies), 4),
            "p50_latency": round(sorted(latencies)[len(latencies) // 2], 4),
            "p95_latency": round(sorted(latencies)[int(len(latencies) * 0.95)], 4),
            "p99_latency": round(sorted(latencies)[int(len(latencies) * 0.99)], 4),
        }
