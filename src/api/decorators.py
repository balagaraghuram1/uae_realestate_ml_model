 """API decorators for caching, rate limiting, and logging."""
import time, functools, hashlib, json, logging
from typing import Callable, Optional

logger = logging.getLogger(__name__)

def cache_response(ttl: int = 300, key_prefix: str = ""):
    """Cache API response with TTL."""
    _cache = {}
    def decorator(func: Callable):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            cache_key = f"{key_prefix}:{hashlib.md5(json.dumps(kwargs, default=str).encode()).hexdigest()}"
            if cache_key in _cache:
                entry = _cache[cache_key]
                if time.time() - entry["time"] < ttl:
                    return entry["value"]
            result = await func(*args, **kwargs)
            _cache[cache_key] = {"value": result, "time": time.time()}
            return result
        wrapper.cache_clear = lambda: _cache.clear()
        return wrapper
    return decorator

def log_execution(func: Callable):
    """Log function execution time."""
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        start = time.time()
        try:
            result = await func(*args, **kwargs)
            duration = time.time() - start
            logger.info("%s executed in %.3fs", func.__name__, duration)
            return result
        except Exception as e:
            duration = time.time() - start
            logger.error("%s failed after %.3fs: %s", func.__name__, duration, e)
            raise
    return wrapper
