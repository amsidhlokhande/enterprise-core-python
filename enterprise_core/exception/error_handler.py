"""
Centralized Error Handler for Enterprise Flask Microservices.
Provides a unified point of exception handling returning the standard enterprise error response template.
"""
import logging
from datetime import datetime, timezone
from typing import Optional
from flask import Flask, jsonify, request, g
from werkzeug.exceptions import HTTPException
from enterprise_core.exception.base_exception import BaseEnterpriseException

logger = logging.getLogger(__name__)

def register_centralized_error_handlers(
    app: Flask,
    default_internal_error_code: str = "ENTERPRISE_500",
    default_internal_error_msg: str = "An internal processing error occurred in the service."
):
    """
    Registers a single centralized error handler on the Flask application instance.
    Guarantees every error returns the common generic error response template.
    """
    @app.errorhandler(Exception)
    def handle_centralized_exception(e: Exception):
        correlation_id = getattr(g, "correlation_id", request.headers.get("X-Correlation-ID", "UNKNOWN"))
        path = request.path
        timestamp = datetime.now(timezone.utc).isoformat()

        # 1. Custom Enterprise Domain Exceptions
        if isinstance(e, BaseEnterpriseException):
            status_code = e.status_code
            error_code = e.error_code
            error_message = e.error_message
            error_detail_message = e.error_detail_message
            details = e.details
            logger.warning(
                f"Domain Exception [{error_code}]: {error_message} | Detail: {error_detail_message}",
                extra={"correlation_id": correlation_id, "path": path, "status_code": status_code}
            )

        # 2. Standard Werkzeug HTTP Exceptions (e.g. 404 Not Found, 405 Method Not Allowed)
        elif isinstance(e, HTTPException):
            status_code = e.code or 500
            error_code = f"HTTP_{status_code}"
            error_message = e.description
            error_detail_message = f"HTTP error {status_code}: {e.name}"
            details = [str(e)]
            logger.warning(
                f"HTTP Exception [{error_code}]: {error_message}",
                extra={"correlation_id": correlation_id, "path": path, "status_code": status_code}
            )

        # 3. Unhandled Generic / System Exceptions (Catch-All)
        else:
            status_code = 500
            error_code = default_internal_error_code
            error_message = default_internal_error_msg
            error_detail_message = f"Unhandled Exception type '{type(e).__name__}': {str(e)}"
            details = [str(e)]
            logger.error(
                f"Unhandled Exception [{error_code}]: {str(e)}",
                exc_info=True,
                extra={"correlation_id": correlation_id, "path": path, "status_code": 500}
            )

        # Unified Enterprise Error Response Template
        error_payload = {
            "timestamp": timestamp,
            "status": status_code,
            "errorCode": error_code,
            "errorMessage": error_message,
            "errorDetailMessage": error_detail_message,
            "path": path,
            "correlationId": correlation_id,
            "details": details
        }

        response = jsonify(error_payload)
        response.status_code = status_code
        response.headers["X-Correlation-ID"] = correlation_id
        return response
