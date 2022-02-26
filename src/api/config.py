"""API configuration with rate limiting, CORS, and security settings."""
import os
from typing import List, Optional
from pydantic import BaseSettings, Field

class APIConfig(BaseSettings):
    """API configuration loaded from environment variables."""

    app_name: str = "UAE Real Estate ML API"
    version: str = "1.0.0"
    debug: bool = False
    host: str = "0.0.0.0"
    port: int = 8000
    workers: int = 4
    reload: bool = False
    cors_origins: List[str] = Field(default=["*"])
    cors_methods: List[str] = Field(default=["GET", "POST", "PUT", "DELETE"])
    cors_headers: List[str] = Field(default=["*"])
    rate_limit_requests: int = 100
    rate_limit_window: int = 60
    api_key_header: str = "X-API-Key"
    api_keys: List[str] = Field(default=[])
    max_request_size: int = 10 * 1024 * 1024
    request_timeout: int = 30
    log_level: str = "INFO"
    db_url: str = "sqlite:///./uae_realestate.db"
    redis_url: str = "redis://localhost:6379/0"
    model_registry_path: str = "model_registry"
    enable_docs: bool = True
    enable_metrics: bool = True

    class Config:
        env_prefix = "UAE_"
        env_file = ".env"

    @property
    def docs_url(self) -> Optional[str]:
        return "/docs" if self.enable_docs else None

    @property
    def redoc_url(self) -> Optional[str]:
        return "/redoc" if self.enable_docs else None

    @property
    def openapi_url(self) -> Optional[str]:
        return "/openapi.json" if self.enable_docs else None

api_config = APIConfig()
