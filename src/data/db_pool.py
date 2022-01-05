"""Database connection pool manager with retry logic and health checks."""
import os, time, logging, threading
from contextlib import contextmanager
from typing import Optional, Generator
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)

@dataclass
class PoolConfig:
    host: str = "localhost"
    port: int = 5432
    database: str = "uae_realestate"
    user: str = ""
    password: str = ""
    min_connections: int = 2
    max_connections: int = 20
    timeout: int = 30
    retry_attempts: int = 3
    retry_delay: float = 1.0
    ssl_mode: str = "prefer"

    @classmethod
    def from_env(cls) -> "PoolConfig":
        return cls(
            host=os.getenv("DB_HOST", "localhost"),
            port=int(os.getenv("DB_PORT", "5432")),
            database=os.getenv("DB_NAME", "uae_realestate"),
            user=os.getenv("DB_USER", ""),
            password=os.getenv("DB_PASSWORD", ""),
            min_connections=int(os.getenv("DB_MIN_CONN", "2")),
            max_connections=int(os.getenv("DB_MAX_CONN", "20")),
        )


class ConnectionPool:
    """Thread-safe database connection pool with automatic reconnection."""

    def __init__(self, config: Optional[PoolConfig] = None):
        self.config = config or PoolConfig.from_env()
        self._pool = []
        self._lock = threading.Lock()
        self._active_count = 0
        self._total_created = 0
        self._closed = False
        self._stats = {"acquired": 0, "released": 0, "errors": 0, "reconnects": 0}
        logger.info("ConnectionPool initialized: %s@%s:%d/%s (min=%d, max=%d)",
                     self.config.user, self.config.host, self.config.port,
                     self.config.database, self.config.min_connections,
                     self.config.max_connections)

    def _create_connection(self):
        """Create a new database connection with retry logic."""
        for attempt in range(self.config.retry_attempts):
            try:
                import psycopg2
                conn = psycopg2.connect(
                    host=self.config.host, port=self.config.port,
                    database=self.config.database, user=self.config.user,
                    password=self.config.password, sslmode=self.config.ssl_mode,
                    connect_timeout=self.config.timeout,
                )
                conn.autocommit = False
                self._total_created += 1
                logger.debug("Created connection #%d", self._total_created)
                return conn
            except Exception as e:
                logger.warning("Connection attempt %d/%d failed: %s",
                               attempt + 1, self.config.retry_attempts, e)
                time.sleep(self.config.retry_delay * (attempt + 1))
        self._stats["errors"] += 1
        raise ConnectionError("Failed to create database connection after retries")

    def acquire(self):
        """Acquire a connection from the pool."""
        with self._lock:
            if self._closed:
                raise RuntimeError("Pool is closed")
            while self._pool:
                conn = self._pool.pop()
                try:
                    if conn.closed:
                        self._active_count -= 1
                        continue
                    conn.rollback()
                    self._stats["acquired"] += 1
                    return conn
                except Exception:
                    self._active_count -= 1
            if self._active_count >= self.config.max_connections:
                raise ConnectionError("Connection pool exhausted")
            self._active_count += 1
        conn = self._create_connection()
        self._stats["acquired"] += 1
        return conn

    def release(self, conn):
        """Release a connection back to the pool."""
        if conn is None:
            return
        with self._lock:
            if self._closed:
                try:
                    conn.close()
                except Exception:
                    pass
                self._active_count -= 1
                return
            if len(self._pool) < self.config.max_connections:
                try:
                    if not conn.closed:
                        self._pool.append(conn)
                        self._stats["released"] += 1
                        return
                except Exception:
                    pass
            try:
                conn.close()
            except Exception:
                pass
            self._active_count -= 1
            self._stats["released"] += 1

    @contextmanager
    def connection(self) -> Generator:
        """Context manager that acquires and automatically releases a connection."""
        conn = self.acquire()
        try:
            yield conn
        except Exception:
            try:
                conn.rollback()
            except Exception:
                pass
            raise
        finally:
            self.release(conn)

    @contextmanager
    def cursor(self, cursor_factory=None):
        """Context manager that yields a cursor with automatic cleanup."""
        with self.connection() as conn:
            cur = conn.cursor(cursor_factory=cursor_factory) if cursor_factory else conn.cursor()
            try:
                yield cur
            finally:
                cur.close()

    @property
    def stats(self) -> dict:
        """Return pool statistics."""
        with self._lock:
            return {
                **self._stats,
                "active": self._active_count,
                "idle": len(self._pool),
                "total_created": self._total_created,
            }

    def close_all(self):
        """Close all connections in the pool."""
        with self._lock:
            self._closed = True
            for conn in self._pool:
                try:
                    conn.close()
                except Exception:
                    pass
            self._pool.clear()
            self._active_count = 0
            logger.info("All connections closed")

    def health_check(self) -> bool:
        """Verify pool connectivity."""
        try:
            with self.connection() as conn:
                cur = conn.cursor()
                cur.execute("SELECT 1")
                result = cur.fetchone()
                cur.close()
                return result[0] == 1
        except Exception as e:
            logger.error("Health check failed: %s", e)
            return False
