"""
Admin Endpoints for NL2SQL Service
"""

from typing import Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from datetime import datetime, timedelta
import structlog

from app.core.security import require_admin, get_current_user
from app.models.schemas import User, AdminStatsResponse
from app.services.nl2sql_service import get_nl2sql_service

logger = structlog.get_logger(__name__)
router = APIRouter()


class SystemInfo(BaseModel):
    version: str
    uptime: str
    environment: str
    database_status: str
    cache_status: str
    llm_status: str


class UserManagement(BaseModel):
    user_id: str
    action: str  # activate, deactivate, delete
    reason: Optional[str] = None


@router.get("/stats", response_model=AdminStatsResponse)
async def get_admin_stats(admin_user: User = Depends(require_admin)):
    """
    Get administrative statistics and metrics
    """
    try:
        # In production, these would come from database queries
        stats = AdminStatsResponse(
            total_users=100,
            active_users=85,
            total_queries_today=450,
            avg_response_time=1.2,
            error_rate=2.5,
            cache_hit_rate=78.3,
            top_errors=[
                {"error": "SQL Generation Error", "count": 15},
                {"error": "Database Connection Error", "count": 8},
                {"error": "Security Validation Error", "count": 5}
            ]
        )
        
        logger.info("Admin stats retrieved", admin_user_id=admin_user.id)
        return stats
        
    except Exception as e:
        logger.error("Failed to get admin stats", error=str(e), admin_user_id=admin_user.id)
        raise HTTPException(status_code=500, detail=f"Failed to get stats: {str(e)}")


@router.get("/system-info", response_model=SystemInfo)
async def get_system_info(admin_user: User = Depends(require_admin)):
    """
    Get system information and health status
    """
    try:
        from app.config import settings
        import time
        
        # Calculate uptime (mock value)
        uptime = "5 days, 3 hours, 22 minutes"
        
        system_info = SystemInfo(
            version=settings.API_VERSION,
            uptime=uptime,
            environment=settings.ENVIRONMENT,
            database_status="healthy",
            cache_status="healthy" if settings.REDIS_URL else "unavailable",
            llm_status="healthy" if settings.OPENAI_API_KEY else "unavailable"
        )
        
        logger.info("System info retrieved", admin_user_id=admin_user.id)
        return system_info
        
    except Exception as e:
        logger.error("Failed to get system info", error=str(e), admin_user_id=admin_user.id)
        raise HTTPException(status_code=500, detail=f"Failed to get system info: {str(e)}")


@router.get("/users")
async def list_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    admin_user: User = Depends(require_admin)
):
    """
    List all users with pagination
    """
    try:
        # In production, fetch from database
        # Mock data for demonstration
        users = [
            {
                "id": "user-1",
                "email": "admin@example.com",
                "name": "Admin User",
                "is_active": True,
                "permissions": ["admin", "query:execute"],
                "created_at": "2024-01-01T00:00:00",
                "last_login": "2024-01-15T10:30:00"
            },
            {
                "id": "user-2", 
                "email": "user@example.com",
                "name": "Regular User",
                "is_active": True,
                "permissions": ["query:execute"],
                "created_at": "2024-01-05T00:00:00",
                "last_login": "2024-01-14T15:45:00"
            }
        ]
        
        # Apply pagination
        paginated_users = users[skip:skip + limit]
        
        logger.info("Users listed", admin_user_id=admin_user.id, count=len(paginated_users))
        
        return {
            "users": paginated_users,
            "total": len(users),
            "skip": skip,
            "limit": limit
        }
        
    except Exception as e:
        logger.error("Failed to list users", error=str(e), admin_user_id=admin_user.id)
        raise HTTPException(status_code=500, detail=f"Failed to list users: {str(e)}")


@router.post("/users/manage")
async def manage_user(
    user_action: UserManagement,
    admin_user: User = Depends(require_admin)
):
    """
    Manage user account (activate, deactivate, delete)
    """
    try:
        logger.info(
            "User management action",
            admin_user_id=admin_user.id,
            target_user_id=user_action.user_id,
            action=user_action.action,
            reason=user_action.reason
        )
        
        # In production, perform the actual user management action
        if user_action.action == "activate":
            message = f"User {user_action.user_id} activated"
        elif user_action.action == "deactivate":
            message = f"User {user_action.user_id} deactivated"
        elif user_action.action == "delete":
            message = f"User {user_action.user_id} deleted"
        else:
            raise HTTPException(status_code=400, detail="Invalid action")
        
        return {"message": message, "action": user_action.action}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("User management failed", error=str(e), admin_user_id=admin_user.id)
        raise HTTPException(status_code=500, detail=f"User management failed: {str(e)}")


@router.get("/queries/recent")
async def get_recent_queries(
    limit: int = Query(50, ge=1, le=100),
    include_errors: bool = Query(True),
    admin_user: User = Depends(require_admin)
):
    """
    Get recent queries across all users
    """
    try:
        # In production, fetch from database
        recent_queries = [
            {
                "id": "query-1",
                "user_id": "user-1",
                "question": "How many customers do we have?",
                "sql_query": "SELECT COUNT(*) FROM customers",
                "execution_time": 0.15,
                "row_count": 1,
                "success": True,
                "created_at": "2024-01-15T10:30:00"
            },
            {
                "id": "query-2",
                "user_id": "user-2", 
                "question": "Show me sales by product",
                "sql_query": "SELECT p.name, SUM(s.amount) FROM products p JOIN sales s...",
                "execution_time": 2.3,
                "row_count": 25,
                "success": True,
                "created_at": "2024-01-15T10:25:00"
            }
        ]
        
        if include_errors:
            recent_queries.append({
                "id": "query-3",
                "user_id": "user-2",
                "question": "Invalid query test",
                "sql_query": "",
                "execution_time": 0.0,
                "row_count": 0,
                "success": False,
                "error": "SQL generation failed",
                "created_at": "2024-01-15T10:20:00"
            })
        
        # Apply limit
        limited_queries = recent_queries[:limit]
        
        logger.info("Recent queries retrieved", admin_user_id=admin_user.id, count=len(limited_queries))
        
        return {
            "queries": limited_queries,
            "count": len(limited_queries),
            "include_errors": include_errors
        }
        
    except Exception as e:
        logger.error("Failed to get recent queries", error=str(e), admin_user_id=admin_user.id)
        raise HTTPException(status_code=500, detail=f"Failed to get recent queries: {str(e)}")


@router.get("/errors/analysis")
async def get_error_analysis(
    days: int = Query(7, ge=1, le=30),
    admin_user: User = Depends(require_admin)
):
    """
    Get error analysis and trends
    """
    try:
        # In production, analyze error logs from database
        error_analysis = {
            "period_days": days,
            "total_errors": 125,
            "error_rate": 2.8,
            "trending_up": False,
            "error_categories": [
                {"category": "SQL Generation", "count": 45, "percentage": 36.0},
                {"category": "Database Connection", "count": 30, "percentage": 24.0},
                {"category": "Security Validation", "count": 25, "percentage": 20.0},
                {"category": "Schema Extraction", "count": 15, "percentage": 12.0},
                {"category": "Other", "count": 10, "percentage": 8.0}
            ],
            "daily_errors": [
                {"date": "2024-01-15", "count": 18},
                {"date": "2024-01-14", "count": 22},
                {"date": "2024-01-13", "count": 15},
                {"date": "2024-01-12", "count": 20},
                {"date": "2024-01-11", "count": 17},
                {"date": "2024-01-10", "count": 19},
                {"date": "2024-01-09", "count": 14}
            ]
        }
        
        logger.info("Error analysis retrieved", admin_user_id=admin_user.id, days=days)
        
        return error_analysis
        
    except Exception as e:
        logger.error("Failed to get error analysis", error=str(e), admin_user_id=admin_user.id)
        raise HTTPException(status_code=500, detail=f"Failed to get error analysis: {str(e)}")


@router.get("/performance/metrics")
async def get_performance_metrics(
    hours: int = Query(24, ge=1, le=168),  # Max 1 week
    admin_user: User = Depends(require_admin)
):
    """
    Get system performance metrics
    """
    try:
        # In production, calculate from monitoring data
        performance_metrics = {
            "period_hours": hours,
            "avg_response_time": 1.23,
            "p95_response_time": 3.45,
            "p99_response_time": 8.12,
            "requests_per_hour": 187,
            "cache_hit_rate": 78.5,
            "memory_usage": 65.2,
            "cpu_usage": 42.1,
            "db_connection_pool": {
                "active": 8,
                "idle": 12,
                "total": 20
            },
            "hourly_metrics": [
                {"hour": "2024-01-15T10:00:00", "requests": 45, "avg_response": 1.1},
                {"hour": "2024-01-15T09:00:00", "requests": 52, "avg_response": 1.3},
                {"hour": "2024-01-15T08:00:00", "requests": 38, "avg_response": 0.9}
            ]
        }
        
        logger.info("Performance metrics retrieved", admin_user_id=admin_user.id, hours=hours)
        
        return performance_metrics
        
    except Exception as e:
        logger.error("Failed to get performance metrics", error=str(e), admin_user_id=admin_user.id)
        raise HTTPException(status_code=500, detail=f"Failed to get performance metrics: {str(e)}")


@router.post("/cache/clear")
async def clear_cache(
    cache_type: str = Query("all", regex="^(all|schema|query|user)$"),
    admin_user: User = Depends(require_admin)
):
    """
    Clear various caches
    """
    try:
        # In production, clear the specified cache
        cleared_items = 0
        
        if cache_type == "all":
            cleared_items = 150  # Mock value
            message = "All caches cleared"
        elif cache_type == "schema":
            cleared_items = 25
            message = "Schema cache cleared"
        elif cache_type == "query":
            cleared_items = 100
            message = "Query cache cleared"
        elif cache_type == "user":
            cleared_items = 25
            message = "User cache cleared"
        
        logger.info(
            "Cache cleared",
            admin_user_id=admin_user.id,
            cache_type=cache_type,
            cleared_items=cleared_items
        )
        
        return {
            "message": message,
            "cache_type": cache_type,
            "cleared_items": cleared_items
        }
        
    except Exception as e:
        logger.error("Failed to clear cache", error=str(e), admin_user_id=admin_user.id)
        raise HTTPException(status_code=500, detail=f"Failed to clear cache: {str(e)}")


@router.get("/audit/logs")
async def get_audit_logs(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    user_id: Optional[str] = Query(None),
    action: Optional[str] = Query(None),
    admin_user: User = Depends(require_admin)
):
    """
    Get audit logs with filtering
    """
    try:
        # In production, fetch from audit log database
        audit_logs = [
            {
                "id": "audit-1",
                "user_id": "user-1",
                "action": "query_executed",
                "resource": "customers table",
                "ip_address": "192.168.1.100",
                "user_agent": "Mozilla/5.0...",
                "timestamp": "2024-01-15T10:30:00",
                "details": {"question": "How many customers?", "execution_time": 0.15}
            },
            {
                "id": "audit-2",
                "user_id": "admin-user",
                "action": "user_created",
                "resource": "user-2",
                "ip_address": "192.168.1.101",
                "user_agent": "Mozilla/5.0...",
                "timestamp": "2024-01-15T09:15:00",
                "details": {"created_user_email": "newuser@example.com"}
            }
        ]
        
        # Apply filters
        if user_id:
            audit_logs = [log for log in audit_logs if log["user_id"] == user_id]
        if action:
            audit_logs = [log for log in audit_logs if log["action"] == action]
        
        # Apply pagination
        paginated_logs = audit_logs[skip:skip + limit]
        
        logger.info(
            "Audit logs retrieved",
            admin_user_id=admin_user.id,
            count=len(paginated_logs),
            filters={"user_id": user_id, "action": action}
        )
        
        return {
            "logs": paginated_logs,
            "total": len(audit_logs),
            "skip": skip,
            "limit": limit
        }
        
    except Exception as e:
        logger.error("Failed to get audit logs", error=str(e), admin_user_id=admin_user.id)
        raise HTTPException(status_code=500, detail=f"Failed to get audit logs: {str(e)}")
