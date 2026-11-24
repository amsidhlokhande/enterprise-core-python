"""
Structured JSON Log Formatter for Enterprise Observability.
"""
import logging
import json
from datetime import datetime, timezone
from flask import g, has_request_context

class JsonLogFormatter(logging.Formatter):
    """
    Structured JSON log formatter outputting machine-readable JSON logs
    with ISO timestamps, trace/correlation IDs, and service metadata.
    """
    def __init__(self, service_name: str = "enterprise-service"):
        super().__init__()
        self.service_name = service_name

    def format(self, record: logging.LogRecord) -> str:
        correlation_id = getattr(record, "correlation_id", None)
        if not correlation_id and has_request_context():
            correlation_id = getattr(g, "correlation_id", "NO_CORRELATION_ID")

        log_data = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "service": self.service_name,
            "correlationId": correlation_id or "SYSTEM",
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "lineno": record.lineno,
        }

        # Include custom extra metadata if passed
        for key in ("path", "method", "status_code", "duration_ms", "trace_id"):
            if hasattr(record, key):
                log_data[key] = getattr(record, key)

        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_data)
