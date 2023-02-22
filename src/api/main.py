from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.config import config
from src.api.routes.properties import router as properties_router
from src.api.routes.analytics import router as analytics_router
from src.api.routes.predictions import router as predictions_router
from src.api.middleware import LoggingMiddleware, RateLimitMiddleware

app = FastAPI(
    title="UAE Real Estate ML API",
    description="API for real estate ML model predictions and analytics",
    version="1.0.0",
    docs_url="/docs" if config.enable_docs else None,
    redoc_url="/redoc" if config.enable_docs else None,
)

if config.enable_cors:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=config.allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.add_middleware(LoggingMiddleware)
app.add_middleware(RateLimitMiddleware)

app.include_router(properties_router, prefix=f"{config.api_prefix}/properties", tags=["properties"])
app.include_router(analytics_router, prefix=f"{config.api_prefix}/analytics", tags=["analytics"])
app.include_router(predictions_router, prefix=f"{config.api_prefix}/predictions", tags=["predictions"])


@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": "1.0.0"}
