"""
Base Enterprise Exception definition.
Enforces standard error codes, functional error messages, technical details, and HTTP status codes.
"""
from typing import List, Optional

class BaseEnterpriseException(Exception):
    """
    Base application exception for all enterprise Python microservices.
    Guarantees consistent error taxonomy and envelope structure across the organization.
    """
    def __init__(
        self,
        error_code: str,
        error_message: str,
        error_detail_message: str,
        status_code: int = 500,
        details: Optional[List[str]] = None
    ):
        super().__init__(error_message)
        self.error_code = error_code
        self.error_message = error_message
        self.error_detail_message = error_detail_message
        self.status_code = status_code
        self.details = details or []
