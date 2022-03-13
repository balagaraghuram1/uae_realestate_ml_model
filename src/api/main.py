"""FastAPI application entry point for UAE Real Estate ML API."""
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.api.config import api_config
from src.api.middleware import (
    RequestLoggingMiddleware, ErrorHandlerMiddleware, SecurityHeadersMiddleware
)
from src.api.routes import properties, predictions, analytics

logging.basicConfig(
    level=getattr(logging, api_config.log_level),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title=api_config.app_name,
    version=api_config.version,
    docs_url=api_config.docs_url,
    redoc_url=api_config.redoc_url,
    openapi_url=api_config.openapi_url,
    description="Production ML platform for UAE real estate investment analytics",
)

app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(ErrorHandlerMiddleware)
app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=api_config.cors_origins,
    allow_methods=api_config.cors_methods,
    allow_headers=api_config.cors_headers,
)

app.include_router(properties.router)
app.include_router(predictions.router)
app.include_router(analytics.router)

@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": api_config.version, "service": "uae-realestate-ml"}

@app.get("/")
async def root():
    return {
        "service": api_config.app_name,
        "version": api_config.version,
        "docs": api_config.docs_url,
        "status": "/health",
    }
