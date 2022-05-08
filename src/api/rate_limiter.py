"""Rate limiter using token bucket algorithm."""
import time, threading, logging
from typing import Dict, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class TokenBucket:
    """Token bucket for rate limiting."""
    capacity: int
    refill_rate: float
    tokens: float = 0
    last_refill: float = 0

    def __post_init__(self):
        self.tokens = self.capacity
        self.last_refill = time.time()

    def consume(self, tokens: int = 1) -> bool:
        """Try to consume tokens."""
        now = time.time()
        elapsed = now - self.last_refill
        self.tokens = min(self.capacity, self.tokens + elapsed * self.refill_rate)
        self.last_refill = now
        if self.tokens >= tokens:
            self.tokens -= tokens
            return True
        return False

    @property
    def retry_after(self) -> float:
        """Seconds until next token is available."""
        if self.tokens >= 1:
            return 0
        return (1 - self.tokens) / self.refill_rate


class RateLimiter:
    """Per-client rate limiter."""

    def __init__(self, max_requests: int = 100, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._buckets: Dict[str, TokenBucket] = {}
        self._lock = threading.Lock()

    def _get_bucket(self, client_id: str) -> TokenBucket:
        """Get or create a token bucket for a client."""
        with self._lock:
            if client_id not in self._buckets:
                rate = self.max_requests / self.window_seconds
                self._buckets[client_id] = TokenBucket(
                    capacity=self.max_requests, refill_rate=rate,
                )
            return self._buckets[client_id]

    def is_allowed(self, client_id: str) -> Dict:
        """Check if a request is allowed."""
        bucket = self._get_bucket(client_id)
        allowed = bucket.consume()
        return {
            "allowed": allowed,
            "remaining": int(bucket.tokens),
            "retry_after": round(bucket.retry_after, 2) if not allowed else 0,
        }

    def reset(self, client_id: str = None):
        """Reset rate limiter state."""
        with self._lock:
            if client_id:
                self._buckets.pop(client_id, None)
            else:
                self._buckets.clear()
