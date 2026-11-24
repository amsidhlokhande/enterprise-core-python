"""
Enterprise swagger documentation module.
"""
from enterprise_core.swagger.swagger_routes import (
    create_swagger_blueprint,
    ACTUATOR_OPENAPI_PATHS,
)

__all__ = ["create_swagger_blueprint", "ACTUATOR_OPENAPI_PATHS"]
