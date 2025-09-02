"""
API Router for NL2SQL Service
"""

from fastapi import APIRouter
from app.api.v1.endpoints import query, admin, auth

api_router = APIRouter()

# Include endpoint routers
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(query.router, prefix="/query", tags=["query"])
api_router.include_router(admin.router, prefix="/admin", tags=["admin"])
