"""API response caching with Redis backend."""
import json, hashlib, logging
from typing import Optional, Any, Callable
from functools import wraps
import time

logger = logging.getLogger(__name__)

class ResponseCache:
    """Cache API responses to reduce computation."""

    def __init__(self, redis_url: str = None, default_ttl: int = 300):
        self.default_ttl = default_ttl
        self._redis = None
        self._local_cache = {}
        if redis_url:
            try:
                import redis
                self._redis = redis.from_url(redis_url)
            except Exception:
                logger.warning("Redis not available, using in-memory cache")

    def _make_key(self, prefix: str, params: dict) -> str:
        """Generate cache key from parameters."""
        param_str = json.dumps(params, sort_keys=True, default=str)
        param_hash = hashlib.md5(param_str.encode()).hexdigest()
        return f"{prefix}:{param_hash}"

    def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        if self._redis:
            try:
                data = self._redis.get(key)
                if data:
                    return json.loads(data)
            except Exception:
                pass
        return self._local_cache.get(key, {}).get("value")

    def set(self, key: str, value: Any, ttl: int = None):
        """Set value in cache."""
        ttl = ttl or self.default_ttl
        if self._redis:
            try:
                self._redis.setex(key, ttl, json.dumps(value, default=str))
                return
            except Exception:
                pass
        self._local_cache[key] = {"value": value, "expires": time.time() + ttl}

    def invalidate(self, pattern: str = None):
        """Invalidate cache entries."""
        if self._redis and pattern:
            try:
                keys = self._redis.keys(pattern)
                if keys:
                    self._redis.delete(*keys)
            except Exception:
                pass
        if not pattern:
            self._local_cache.clear()

    def cached(self, prefix: str, ttl: int = None):
        """Decorator to cache function results."""
        def decorator(func: Callable):
            @wraps(func)
            def wrapper(*args, **kwargs):
                cache_key = self._make_key(prefix, {"args": str(args), "kwargs": str(kwargs)})
                result = self.get(cache_key)
                if result is not None:
                    return result
                result = func(*args, **kwargs)
                self.set(cache_key, result, ttl)
                return result
            return wrapper
        return decorator
