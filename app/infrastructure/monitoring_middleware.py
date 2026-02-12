"""
Performance Monitoring Middleware

Adds request/response timing and memory usage tracking to the FastAPI app.
"""

import time
import psutil
import os
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware


class PerformanceMonitoringMiddleware(BaseHTTPMiddleware):
    """
    Middleware that tracks request timing and memory usage.

    Adds timing headers to responses and logs performance metrics.
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Get process info for memory tracking
        process = psutil.Process(os.getpid())

        # Record start time and memory
        start_time = time.time()
        start_memory = process.memory_info().rss / 1024 / 1024  # MB

        # Process the request
        response = await call_next(request)

        # Record end time and memory
        end_time = time.time()
        end_memory = process.memory_info().rss / 1024 / 1024  # MB

        # Calculate metrics
        duration_ms = (end_time - start_time) * 1000
        memory_delta_mb = end_memory - start_memory

        # Add headers to response
        response.headers["X-Response-Time-Ms"] = f"{duration_ms:.2f}"
        response.headers["X-Memory-Usage-Mb"] = f"{end_memory:.2f}"
        response.headers["X-Memory-Delta-Mb"] = f"{memory_delta_mb:+.2f}"

        # Log detailed metrics for text-to-speech endpoint
        if request.url.path == "/text-to-speech":
            print(
                f"[TTS] Duration: {duration_ms:.2f}ms | "
                f"Memory: {end_memory:.2f}MB (Δ{memory_delta_mb:+.2f}MB)"
            )

        return response


def get_current_memory_usage() -> dict:
    """
    Get current memory usage statistics.

    Returns:
        dict with memory usage in MB
    """
    process = psutil.Process(os.getpid())
    memory_info = process.memory_info()

    return {
        "rss_mb": memory_info.rss / 1024 / 1024,
        "vms_mb": memory_info.vms / 1024 / 1024,
        "percent": process.memory_percent(),
    }
