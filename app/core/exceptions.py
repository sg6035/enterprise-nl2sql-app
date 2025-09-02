"""
Custom Exceptions for NL2SQL Service
"""

from typing import Any, Dict, Optional
from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
import structlog

logger = structlog.get_logger(__name__)


class NL2SQLException(Exception):
    """Base exception for NL2SQL service"""
    
    def __init__(
        self,
        message: str,
        error_code: str = "NL2SQL_ERROR",
        details: Optional[Dict[str, Any]] = None,
        status_code: int = 500
    ):
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        self.status_code = status_code
        super().__init__(self.message)


class SchemaExtractionError(NL2SQLException):
    """Raised when schema extraction fails"""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code="SCHEMA_EXTRACTION_ERROR",
            details=details,
            status_code=422
        )


class SQLGenerationError(NL2SQLException):
    """Raised when SQL generation fails"""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code="SQL_GENERATION_ERROR",
            details=details,
            status_code=422
        )


class SQLExecutionError(NL2SQLException):
    """Raised when SQL execution fails"""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code="SQL_EXECUTION_ERROR",
            details=details,
            status_code=400
        )


class SecurityValidationError(NL2SQLException):
    """Raised when SQL security validation fails"""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code="SECURITY_VALIDATION_ERROR",
            details=details,
            status_code=403
        )


class RateLimitExceededError(NL2SQLException):
    """Raised when rate limit is exceeded"""
    
    def __init__(self, message: str = "Rate limit exceeded", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code="RATE_LIMIT_EXCEEDED",
            details=details,
            status_code=429
        )


class AuthenticationError(NL2SQLException):
    """Raised when authentication fails"""
    
    def __init__(self, message: str = "Authentication failed", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code="AUTHENTICATION_ERROR",
            details=details,
            status_code=401
        )


async def nl2sql_exception_handler(request: Request, exc: NL2SQLException) -> JSONResponse:
    """Handle NL2SQL custom exceptions"""
    logger.error(
        "NL2SQL Exception occurred",
        error_code=exc.error_code,
        message=exc.message,
        details=exc.details,
        path=request.url.path,
        method=request.method
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": exc.error_code,
                "message": exc.message,
                "details": exc.details
            },
            "path": request.url.path,
            "method": request.method
        }
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Handle validation exceptions"""
    logger.warning(
        "Validation error",
        errors=exc.errors(),
        path=request.url.path,
        method=request.method
    )
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Request validation failed",
                "details": {
                    "validation_errors": exc.errors()
                }
            },
            "path": request.url.path,
            "method": request.method
        }
    )
