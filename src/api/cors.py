"""CORS middleware configuration."""
from fastapi.middleware.cors import CORSMiddleware

def setup_cors(app, config: dict = None):
    """Configure CORS middleware for the FastAPI app."""
    config = config or {}
    app.add_middleware(
        CORSMiddleware,
        allow_origins=config.get("origins", ["*"]),
        allow_credentials=config.get("credentials", True),
        allow_methods=config.get("methods", ["*"]),
        allow_headers=config.get("headers", ["*"]),
        expose_headers=["X-Request-ID", "X-Response-Time"],
        max_age=600,
    )
