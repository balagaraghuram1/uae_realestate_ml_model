import os
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class APIConfig:
    host: str = os.getenv("API_HOST", "0.0.0.0")
    port: int = int(os.getenv("API_PORT", "8000"))
    debug: bool = os.getenv("API_DEBUG", "false").lower() == "true"
    allowed_origins: List[str] = field(default_factory=lambda: ["*"])
    api_prefix: str = "/api/v1"
    rate_limit: int = int(os.getenv("API_RATE_LIMIT", "100"))
    rate_limit_window: int = int(os.getenv("API_RATE_LIMIT_WINDOW", "60"))
    jwt_secret: str = os.getenv("JWT_SECRET", "change-this-in-production")
    jwt_algorithm: str = "HS256"
    jwt_expiry_minutes: int = int(os.getenv("JWT_EXPIRY_MINUTES", "1440"))
    max_page_size: int = 100
    default_page_size: int = 20
    enable_docs: bool = True
    enable_cors: bool = True
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    cache_ttl_seconds: int = int(os.getenv("CACHE_TTL_SECONDS", "300"))
    redis_url: Optional[str] = os.getenv("REDIS_URL")
    database_url: str = os.getenv(
        "DATABASE_URL", "sqlite:///./data/realestate.db"
    )


config = APIConfig()
