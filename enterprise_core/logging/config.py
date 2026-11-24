"""
Logging bootstrap utility for enterprise microservices.
"""
import sys
import logging
from enterprise_core.logging.pii_filter import PIIMaskingFilter
from enterprise_core.logging.formatter import JsonLogFormatter

def setup_enterprise_logging(service_name: str, log_level: str = "INFO"):
    """
    Configures root logger with:
    1. Standard output StreamHandler
    2. JsonLogFormatter tagging service_name and correlation_id
    3. PIIMaskingFilter scrubbing sensitive data
    """
    root_logger = logging.getLogger()
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)
    root_logger.setLevel(numeric_level)

    # Clear existing handlers to prevent duplicate lines
    for h in root_logger.handlers[:]:
        root_logger.removeHandler(h)

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(numeric_level)
    handler.setFormatter(JsonLogFormatter(service_name=service_name))
    handler.addFilter(PIIMaskingFilter())

    root_logger.addHandler(handler)
    logging.getLogger("werkzeug").setLevel(logging.WARNING)
