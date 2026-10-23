"""
Sentinel SOS - Centralized Error and Exception Handling.

Defines custom domain exceptions and FastAPI exception handlers to ensure
predictable, secure, and standardized JSON error payloads.
"""

from typing import Any, Dict, Optional
from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from app.core.logging import logger


class SentinelException(Exception):
    """Base exception for all Sentinel SOS domain errors."""
    def __init__(
        self,
        message: str,
        status_code: int = status.HTTP_400_BAD_REQUEST,
        code: str = "ERROR",
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.code = code
        self.details = details or {}


class EntityNotFoundException(SentinelException):
    """Raised when a requested resource (user, incident, responder) is not found."""
    def __init__(self, entity_name: str, identifier: Any):
        super().__init__(
            message=f"{entity_name} with identifier '{identifier}' was not found.",
            status_code=status.HTTP_404_NOT_FOUND,
            code="ENTITY_NOT_FOUND",
            details={"entity": entity_name, "id": str(identifier)},
        )


class UnauthorizedException(SentinelException):
    """Raised when authentication credentials are invalid or missing."""
    def __init__(self, message: str = "Authentication credentials were invalid or missing."):
        super().__init__(
            message=message,
            status_code=status.HTTP_401_UNAUTHORIZED,
            code="UNAUTHORIZED",
        )


class ForbiddenException(SentinelException):
    """Raised when user lacks permission to access an incident or endpoint."""
    def __init__(self, message: str = "You do not have permission to perform this action."):
        super().__init__(
            message=message,
            status_code=status.HTTP_403_FORBIDDEN,
            code="FORBIDDEN",
        )


class IncidentStateException(SentinelException):
    """Raised when an invalid state transition is attempted on an incident."""
    def __init__(self, message: str, current_state: str, attempted_state: str):
        super().__init__(
            message=message,
            status_code=status.HTTP_409_CONFLICT,
            code="INVALID_STATE_TRANSITION",
            details={"current_state": current_state, "attempted_state": attempted_state},
        )


class DuplicateRequestException(SentinelException):
    """Raised when an idempotent or duplicate client request is detected."""
    def __init__(self, message: str = "Duplicate emergency submission detected."):
        super().__init__(
            message=message,
            status_code=status.HTTP_409_CONFLICT,
            code="DUPLICATE_REQUEST",
        )


class ExternalIntegrationException(SentinelException):
    """Raised when an upstream external API fails."""
    def __init__(self, provider: str, message: str):
        super().__init__(
            message=f"External provider failure ({provider}): {message}",
            status_code=status.HTTP_502_BAD_GATEWAY,
            code="EXTERNAL_PROVIDER_ERROR",
            details={"provider": provider},
        )


def register_exception_handlers(app: FastAPI) -> None:
    """Registers centralized exception handlers into the FastAPI instance."""

    @app.exception_handler(SentinelException)
    async def sentinel_exception_handler(request: Request, exc: SentinelException):
        logger.warning(f"Domain error [{exc.code}] at {request.url.path}: {exc.message}")
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": {
                    "code": exc.code,
                    "message": exc.message,
                    "details": exc.details,
                }
            },
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        logger.info(f"Validation failure at {request.url.path}: {exc.errors()}")
        errors = []
        for err in exc.errors():
            loc = " -> ".join([str(x) for x in err.get("loc", [])])
            errors.append({
                "field": loc,
                "message": err.get("msg", "Invalid value"),
                "type": err.get("type", "value_error"),
            })
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": "Input validation failed. Please check the supplied fields.",
                    "details": {"validation_errors": errors},
                }
            },
        )

    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        logger.error(f"Unhandled error at {request.url.path}: {exc}", exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": {
                    "code": "INTERNAL_SERVER_ERROR",
                    "message": "An unexpected server error occurred. Please contact system support.",
                    "details": {},
                }
            },
        )
