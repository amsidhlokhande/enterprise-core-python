"""
Enterprise exception handling module.
"""
from enterprise_core.exception.base_exception import BaseEnterpriseException
from enterprise_core.exception.error_handler import register_centralized_error_handlers

__all__ = ["BaseEnterpriseException", "register_centralized_error_handlers"]
