"""
Enterprise Core Python Library.
Shared foundation for Python / Flask microservices:
- Centralized Exception Handling & Generic Error Envelope
- JSON Logging with Automatic PII Masking
- End-to-End Latency Tracking & Correlation Interceptors
- Spring Boot-style Actuators (/health, /liveness, /readiness, /info, /metrics)
- OpenAPI 3.0 & Swagger UI Blueprint Factory
"""

from enterprise_core.exception.base_exception import BaseEnterpriseException
from enterprise_core.exception.error_handler import register_centralized_error_handlers
from enterprise_core.logging.config import setup_enterprise_logging
from enterprise_core.logging.pii_filter import PIIMaskingFilter
from enterprise_core.logging.formatter import JsonLogFormatter
from enterprise_core.interceptor.latency_interceptor import register_latency_interceptors
from enterprise_core.actuator.actuator_routes import create_actuators_blueprint
from enterprise_core.swagger.swagger_routes import (
    create_swagger_blueprint,
    ACTUATOR_OPENAPI_PATHS,
)

__all__ = [
    "BaseEnterpriseException",
    "register_centralized_error_handlers",
    "setup_enterprise_logging",
    "PIIMaskingFilter",
    "JsonLogFormatter",
    "register_latency_interceptors",
    "create_actuators_blueprint",
    "create_swagger_blueprint",
    "ACTUATOR_OPENAPI_PATHS",
]

__version__ = "1.0.0"
