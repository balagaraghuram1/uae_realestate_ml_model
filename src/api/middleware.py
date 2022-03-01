"""API middleware for authentication, request logging, and error handling."""
import time, logging, uuid
from typing import Callable
from fastapi import Request, Response, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
import logging

logger = logging.getLogger(__name__)

class AuthMiddleware(BaseHTTPMiddleware):
    """API key authentication middleware."""

    SKIP_PATHS = {"/health", "/docs", "/redoc", "/openapi.json", "/favicon.ico"}

    def __init__(self, app, api_keys: list = None):
        super().__init__(app)
        self.api_keys = set(api_keys or [])

    async def dispatch(self, request: Request, call_next):
        if request.url.path in self.SKIP_PATHS:
            return await call_next(request)
        if self.api_keys:
            api_key = request.headers.get("X-API-Key")
            if not api_key or api_key not in self.api_keys:
                return JSONResponse(
                    status_code=401,
                    content={"error": "Invalid or missing API key"},
                )
        return await call_next(request)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Log all incoming requests with timing."""

    async def dispatch(self, request: Request, call_next):
        request_id = str(uuid.uuid4())[:8]
        start = time.time()
        logger.info("[%s] %s %s", request_id, request.method, request.url.path)
        try:
            response = await call_next(request)
            duration = time.time() - start
            logger.info("[%s] %s %s -> %d (%.3fs)",
                        request_id, request.method, request.url.path,
                        response.status_code, duration)
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Response-Time"] = f"{duration:.3f}s"
            return response
        except Exception as e:
            duration = time.time() - start
            logger.error("[%s] %s %s -> ERROR (%.3fs): %s",
                         request_id, request.method, request.url.path, duration, e)
            return JSONResponse(
                status_code=500,
                content={"error": "Internal server error", "request_id": request_id},
            )


class ErrorHandlerMiddleware(BaseHTTPMiddleware):
    """Global error handler middleware."""

    async def dispatch(self, request: Request, call_next):
        try:
            return await call_next(request)
        except HTTPException as e:
            return JSONResponse(
                status_code=e.status_code,
                content={"error": e.detail, "status_code": e.status_code},
            )
        except Exception as e:
            logger.exception("Unhandled exception")
            return JSONResponse(
                status_code=500,
                content={"error": "Internal server error", "detail": str(e)},
            )


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Add security headers to responses."""

    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "SAMEORIGIN"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
        return response
