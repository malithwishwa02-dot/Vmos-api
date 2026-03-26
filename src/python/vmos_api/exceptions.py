"""
VMOS API Exceptions

This module defines custom exceptions for the VMOS API SDK.
"""

from typing import Optional, Dict, Any


class VMOSError(Exception):
    """Base exception for all VMOS API errors."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        self.message = message
        self.details = details or {}
        super().__init__(self.message)

    def __str__(self) -> str:
        if self.details:
            return f"{self.message} - Details: {self.details}"
        return self.message


class VMOSConnectionError(VMOSError):
    """Raised when connection to VMOS API fails."""

    def __init__(
        self,
        message: str = "Failed to connect to VMOS API",
        host: Optional[str] = None,
        port: Optional[int] = None,
    ):
        details = {}
        if host:
            details["host"] = host
        if port:
            details["port"] = port
        super().__init__(message, details)


class VMOSAuthenticationError(VMOSError):
    """Raised when authentication fails."""

    def __init__(
        self,
        message: str = "Authentication failed",
        status_code: Optional[int] = None,
    ):
        details = {}
        if status_code:
            details["status_code"] = status_code
        super().__init__(message, details)


class VMOSAPIError(VMOSError):
    """Raised when API returns an error response."""

    def __init__(
        self,
        message: str,
        code: Optional[int] = None,
        request_id: Optional[str] = None,
        endpoint: Optional[str] = None,
    ):
        details = {}
        if code is not None:
            details["code"] = code
        if request_id:
            details["request_id"] = request_id
        if endpoint:
            details["endpoint"] = endpoint
        super().__init__(message, details)
        self.code = code
        self.request_id = request_id
        self.endpoint = endpoint


class VMOSTimeoutError(VMOSError):
    """Raised when API request times out."""

    def __init__(
        self,
        message: str = "Request timed out",
        timeout: Optional[float] = None,
        endpoint: Optional[str] = None,
    ):
        details = {}
        if timeout:
            details["timeout"] = timeout
        if endpoint:
            details["endpoint"] = endpoint
        super().__init__(message, details)


class VMOSValidationError(VMOSError):
    """Raised when input validation fails."""

    def __init__(
        self,
        message: str,
        field: Optional[str] = None,
        value: Optional[Any] = None,
    ):
        details = {}
        if field:
            details["field"] = field
        if value is not None:
            details["value"] = value
        super().__init__(message, details)


class VMOSInstanceNotFoundError(VMOSError):
    """Raised when a requested instance is not found."""

    def __init__(self, db_id: str):
        super().__init__(f"Instance not found: {db_id}", {"db_id": db_id})
        self.db_id = db_id


class VMOSInstanceNotReadyError(VMOSError):
    """Raised when an instance is not in the expected state."""

    def __init__(self, db_id: str, current_status: str, expected_status: str):
        super().__init__(
            f"Instance {db_id} is not ready. Current: {current_status}, Expected: {expected_status}",
            {
                "db_id": db_id,
                "current_status": current_status,
                "expected_status": expected_status,
            },
        )
        self.db_id = db_id
        self.current_status = current_status
        self.expected_status = expected_status
