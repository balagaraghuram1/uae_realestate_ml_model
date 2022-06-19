"""API health check and system monitoring endpoints."""
from fastapi import APIRouter
from typing import Dict
import time, os, psutil

router = APIRouter(tags=["health"])

_start_time = time.time()

@router.get("/health")
async def health_check():
    """Basic health check endpoint."""
    return {
        "status": "healthy",
        "uptime_seconds": round(time.time() - _start_time, 2),
        "timestamp": time.time(),
    }

@router.get("/health/detailed")
async def detailed_health():
    """Detailed system health check."""
    process = psutil.Process(os.getpid())
    return {
        "status": "healthy",
        "uptime_seconds": round(time.time() - _start_time, 2),
        "memory": {
            "rss_mb": round(process.memory_info().rss / 1024 / 1024, 2),
            "vms_mb": round(process.memory_info().vms / 1024 / 1024, 2),
        },
        "cpu_percent": process.cpu_percent(),
        "threads": process.num_threads(),
    }

@router.get("/ready")
async def readiness_check():
    """Readiness probe for Kubernetes."""
    return {"ready": True, "message": "Service is ready to accept traffic"}
