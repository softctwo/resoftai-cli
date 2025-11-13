"""Custom error classes and error handling utilities."""
from fastapi import HTTPException, status
from typing import Optional, Dict, Any


class ResoftAIError(Exception):
    """Base exception class for ResoftAI platform."""
    
    def __init__(
        self, 
        message: str, 
        error_code: str = "internal_error",
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.error_code = error_code
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)


class NotFoundError(ResoftAIError):
    """Resource not found error."""
    
    def __init__(self, resource_type: str, resource_id: Any, details: Optional[Dict[str, Any]] = None):
        message = f"{resource_type} not found: {resource_id}"
        super().__init__(
            message=message,
            error_code="not_found",
            status_code=status.HTTP_404_NOT_FOUND,
            details=details
        )


class PermissionError(ResoftAIError):
    """Permission denied error."""
    
    def __init__(self, action: str, resource: str, details: Optional[Dict[str, Any]] = None):
        message = f"Permission denied: Cannot {action} {resource}"
        super().__init__(
            message=message,
            error_code="permission_denied",
            status_code=status.HTTP_403_FORBIDDEN,
            details=details
        )


class ValidationError(ResoftAIError):
    """Validation error."""
    
    def __init__(self, field: str, message: str, details: Optional[Dict[str, Any]] = None):
        full_message = f"Validation error for field '{field}': {message}"
        super().__init__(
            message=full_message,
            error_code="validation_error",
            status_code=status.HTTP_400_BAD_REQUEST,
            details=details
        )


class ConflictError(ResoftAIError):
    """Resource conflict error."""
    
    def __init__(self, resource: str, conflict_details: str, details: Optional[Dict[str, Any]] = None):
        message = f"{resource} conflict: {conflict_details}"
        super().__init__(
            message=message,
            error_code="conflict",
            status_code=status.HTTP_409_CONFLICT,
            details=details
        )


class FileOperationError(ResoftAIError):
    """File operation error."""
    
    def __init__(self, operation: str, file_path: str, error: str, details: Optional[Dict[str, Any]] = None):
        message = f"File operation failed: {operation} on '{file_path}' - {error}"
        super().__init__(
            message=message,
            error_code="file_operation_error",
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            details=details
        )


class DatabaseError(ResoftAIError):
    """Database operation error."""
    
    def __init__(self, operation: str, error: str, details: Optional[Dict[str, Any]] = None):
        message = f"Database operation failed: {operation} - {error}"
        super().__init__(
            message=message,
            error_code="database_error",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details=details
        )


class LLMError(ResoftAIError):
    """LLM operation error."""
    
    def __init__(self, provider: str, operation: str, error: str, details: Optional[Dict[str, Any]] = None):
        message = f"LLM operation failed: {operation} with {provider} - {error}"
        super().__init__(
            message=message,
            error_code="llm_error",
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            details=details
        )


def handle_resoftai_error(error: ResoftAIError) -> HTTPException:
    """Convert ResoftAIError to HTTPException with structured error response."""
    error_response = {
        "error": {
            "code": error.error_code,
            "message": error.message,
            "details": error.details
        }
    }
    
    return HTTPException(
        status_code=error.status_code,
        detail=error_response
    )


def create_error_response(
    error_code: str,
    message: str,
    status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
    details: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Create a standardized error response."""
    return {
        "error": {
            "code": error_code,
            "message": message,
            "details": details or {}
        }
    }