"""
Request and Response Filters/Interceptors for Latency Tracking and Correlation Traceability.
"""
import time
import uuid
import logging
from flask import Flask, request, g, Response

logger = logging.getLogger("access_audit")

def register_latency_interceptors(app: Flask):
    """
    Registers request and response filters/interceptors for end-to-end traceability
    and millisecond latency logging.
    Injects and propagates X-Correlation-ID and X-Response-Time-Ms.
    """
    @app.before_request
    def interceptor_before_request():
        correlation_id = request.headers.get("X-Correlation-ID")
        if not correlation_id:
            correlation_id = str(uuid.uuid4())
        
        g.correlation_id = correlation_id
        g.start_time = time.perf_counter()

    @app.after_request
    def interceptor_after_request(response: Response):
        start_time = getattr(g, "start_time", None)
        if start_time is not None:
            duration_ms = round((time.perf_counter() - start_time) * 1000, 2)
        else:
            duration_ms = 0.0

        correlation_id = getattr(g, "correlation_id", "UNKNOWN")

        response.headers["X-Correlation-ID"] = correlation_id
        response.headers["X-Response-Time-Ms"] = str(duration_ms)

        extra_data = {
            "correlation_id": correlation_id,
            "method": request.method,
            "path": request.path,
            "status_code": response.status_code,
            "duration_ms": duration_ms
        }
        logger.info(
            f"Request completed: {request.method} {request.path} -> {response.status_code} in {duration_ms}ms",
            extra=extra_data
        )

        return response
