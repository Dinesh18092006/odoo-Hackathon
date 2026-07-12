"""Custom HTTP exception classes for meaningful error responses."""
from fastapi import HTTPException, status


class AssetFlowException(HTTPException):
    """Base exception for all AssetFlow errors."""

    def __init__(self, status_code: int, message: str, error_code: str = "ERROR"):
        super().__init__(status_code=status_code, detail={"message": message, "error_code": error_code})


class NotFoundException(AssetFlowException):
    """Raised when a requested resource is not found."""

    def __init__(self, resource: str = "Resource", identifier: str = ""):
        msg = f"{resource} not found" + (f": {identifier}" if identifier else "")
        super().__init__(status.HTTP_404_NOT_FOUND, msg, "NOT_FOUND")


class AlreadyExistsException(AssetFlowException):
    """Raised when trying to create a duplicate resource."""

    def __init__(self, resource: str = "Resource", field: str = ""):
        msg = f"{resource} already exists" + (f" with this {field}" if field else "")
        super().__init__(status.HTTP_409_CONFLICT, msg, "ALREADY_EXISTS")


class InvalidTransitionException(AssetFlowException):
    """Raised when an invalid asset state transition is attempted."""

    def __init__(self, from_status: str, to_status: str):
        super().__init__(
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            f"Cannot transition asset from '{from_status}' to '{to_status}'",
            "INVALID_STATE_TRANSITION",
        )


class ConflictException(AssetFlowException):
    """Raised when a business rule conflict is detected (double allocation, booking overlap)."""

    def __init__(self, message: str):
        super().__init__(status.HTTP_409_CONFLICT, message, "CONFLICT")


class PermissionDeniedException(AssetFlowException):
    """Raised when a user lacks permission to perform an action."""

    def __init__(self, message: str = "You do not have permission to perform this action"):
        super().__init__(status.HTTP_403_FORBIDDEN, message, "PERMISSION_DENIED")


class UnauthorizedException(AssetFlowException):
    """Raised when authentication is required but not provided."""

    def __init__(self, message: str = "Authentication required"):
        super().__init__(status.HTTP_401_UNAUTHORIZED, message, "UNAUTHORIZED")


class ValidationException(AssetFlowException):
    """Raised on business-level validation failures (not schema validation)."""

    def __init__(self, message: str):
        super().__init__(status.HTTP_400_BAD_REQUEST, message, "VALIDATION_ERROR")


class FileTooLargeException(AssetFlowException):
    """Raised when an uploaded file exceeds the size limit."""

    def __init__(self, max_mb: int = 10):
        super().__init__(
            status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            f"File size exceeds maximum allowed size of {max_mb}MB",
            "FILE_TOO_LARGE",
        )


class InvalidFileTypeException(AssetFlowException):
    """Raised when an uploaded file has an unsupported type."""

    def __init__(self, allowed_types: str = ""):
        msg = "File type not allowed" + (f". Allowed: {allowed_types}" if allowed_types else "")
        super().__init__(status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, msg, "INVALID_FILE_TYPE")
