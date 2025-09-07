"""
Enterprise NL2SQL Main Application

Main FastAPI application with security, monitoring, and enterprise features.
"""
import time
import structlog
import sentry_sdk
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration

from app.config import settings
from app.core.middleware import (
    LoggingMiddleware,
    MetricsMiddleware,
    RateLimitMiddleware
)
from app.core.exceptions import (
    NL2SQLException,
    nl2sql_exception_handler,
    validation_exception_handler
)
from app.api.v1.router import api_router
from app.core.logging import setup_logging

# Setup logging
setup_logging()
logger = structlog.get_logger(__name__)

# Initialize Sentry for error tracking (disabled - no DSN configured)
# if settings.SENTRY_DSN and settings.SENTRY_DSN.strip():
#     sentry_sdk.init(
#         dsn=settings.SENTRY_DSN,
#         integrations=[
#             FastApiIntegration(),
#             SqlalchemyIntegration(),
#         ],
#         traces_sample_rate=0.1,
#         environment=settings.ENVIRONMENT
#     )

def create_application() -> FastAPI:
    """Create FastAPI application with all configurations"""
    
    app = FastAPI(
        title=settings.API_TITLE,
        version=settings.API_VERSION,
        description="Enterprise-grade Natural Language to SQL conversion service",
        docs_url="/docs" if settings.DEBUG else None,
        redoc_url="/redoc" if settings.DEBUG else None,
        openapi_url="/openapi.json" if settings.DEBUG else None,
    )
    
    # Security middleware
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["*"] if settings.DEBUG else ["yourdomain.com", "localhost"]
    )
    
    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
        allow_methods=["GET", "POST", "PUT", "DELETE"],
        allow_headers=["*"],
    )
    
    # Custom middleware
    app.add_middleware(LoggingMiddleware)
    if settings.ENABLE_METRICS:
        app.add_middleware(MetricsMiddleware)
    app.add_middleware(RateLimitMiddleware)
    
    # Exception handlers
    app.add_exception_handler(NL2SQLException, nl2sql_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    
    # Include API router
    app.include_router(api_router, prefix="/api/v1")
    
    @app.get("/")
    async def root():
        return {
            "service": settings.API_TITLE,
            "version": settings.API_VERSION,
            "status": "running",
            "docs": "/docs" if settings.DEBUG else "disabled"
        }
    
    @app.get("/health")
    async def health_check():
        return {
            "status": "healthy",
            "timestamp": time.time(),
            "version": settings.API_VERSION,
            "environment": settings.ENVIRONMENT
        }
    
    @app.on_event("startup")
    async def startup_event():
        logger.info(
            "Starting NL2SQL service",
            version=settings.API_VERSION,
            environment=settings.ENVIRONMENT
        )
    
    @app.on_event("shutdown")
    async def shutdown_event():
        logger.info("Shutting down NL2SQL service")
    
    return app

# Create the application instance
app = create_application()

if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower(),
        access_log=True,
    )
