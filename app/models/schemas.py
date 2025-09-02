"""
Pydantic Models and Schemas for NL2SQL Service
"""

from datetime import datetime
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, validator, Field
from enum import Enum


class DatabaseType(str, Enum):
    POSTGRESQL = "postgresql"
    MYSQL = "mysql"
    SQLITE = "sqlite"
    MSSQL = "mssql"
    ORACLE = "oracle"
    BIGQUERY = "bigquery"


class QueryRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=1000, description="Natural language question")
    database_url: str = Field(..., description="Database connection URL")
    database_type: Optional[DatabaseType] = DatabaseType.POSTGRESQL
    include_explanation: bool = Field(default=True, description="Include explanation in response")
    max_results: int = Field(default=100, ge=1, le=1000, description="Maximum number of results")
    schema_hint: Optional[Dict[str, Any]] = Field(default=None, description="Additional schema information")
    
    @validator('question')
    def validate_question(cls, v):
        if not v.strip():
            raise ValueError('Question cannot be empty')
        return v.strip()
    
    @validator('database_url')
    def validate_database_url(cls, v):
        if not v.strip():
            raise ValueError('Database URL cannot be empty')
        # Basic URL validation
        if not any(v.startswith(prefix) for prefix in ['postgresql://', 'mysql://', 'sqlite://', 'mssql://', 'oracle://', 'bigquery://']):
            raise ValueError('Invalid database URL format')
        return v.strip()


class QueryResponse(BaseModel):
    sql_query: str = Field(..., description="Generated SQL query")
    results: List[Dict[str, Any]] = Field(default=[], description="Query execution results")
    explanation: str = Field(default="", description="Human-readable explanation")
    execution_time: float = Field(..., description="Query execution time in seconds")
    row_count: int = Field(..., description="Number of rows returned")
    error: Optional[str] = Field(default=None, description="Error message if query failed")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Additional metadata")
    query_id: Optional[str] = Field(default=None, description="Unique query identifier")
    cache_hit: bool = Field(default=False, description="Whether result was served from cache")


class SchemaInfo(BaseModel):
    tables: Dict[str, Any] = Field(..., description="Database table information")
    relationships: List[Dict[str, str]] = Field(default=[], description="Table relationships")
    sample_data: Dict[str, List[Dict]] = Field(default={}, description="Sample data from tables")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Additional schema metadata")


class User(BaseModel):
    id: str = Field(..., description="User identifier")
    email: Optional[str] = Field(default=None, description="User email")
    name: Optional[str] = Field(default=None, description="User name")
    is_active: bool = Field(default=True, description="Whether user is active")
    permissions: List[str] = Field(default=[], description="User permissions")
    created_at: datetime = Field(default_factory=datetime.now, description="User creation timestamp")
    last_login: Optional[datetime] = Field(default=None, description="Last login timestamp")


class QueryHistory(BaseModel):
    id: str = Field(..., description="Query history identifier")
    user_id: str = Field(..., description="User identifier")
    question: str = Field(..., description="Original question")
    sql_query: str = Field(..., description="Generated SQL query")
    execution_time: float = Field(..., description="Execution time")
    row_count: int = Field(..., description="Number of rows returned")
    success: bool = Field(..., description="Whether query was successful")
    error_message: Optional[str] = Field(default=None, description="Error message if failed")
    created_at: datetime = Field(default_factory=datetime.now, description="Query timestamp")
    database_url: str = Field(..., description="Database URL (masked)")


class ValidationResult(BaseModel):
    is_valid: bool = Field(..., description="Whether SQL is valid")
    is_safe: bool = Field(..., description="Whether SQL is safe to execute")
    messages: List[str] = Field(default=[], description="Validation messages")
    suggestions: List[str] = Field(default=[], description="Improvement suggestions")
    sql_query: str = Field(..., description="Validated SQL query")


class DatabaseConnection(BaseModel):
    name: str = Field(..., description="Connection name")
    database_type: DatabaseType = Field(..., description="Database type")
    host: str = Field(..., description="Database host")
    port: int = Field(..., description="Database port")
    database: str = Field(..., description="Database name")
    username: str = Field(..., description="Username")
    password: str = Field(..., description="Password (encrypted)")
    ssl_enabled: bool = Field(default=False, description="Whether SSL is enabled")
    pool_size: int = Field(default=5, ge=1, le=50, description="Connection pool size")
    created_at: datetime = Field(default_factory=datetime.now, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.now, description="Last update timestamp")


class QueryMetrics(BaseModel):
    user_id: str = Field(..., description="User identifier")
    total_queries: int = Field(default=0, description="Total number of queries")
    successful_queries: int = Field(default=0, description="Number of successful queries")
    failed_queries: int = Field(default=0, description="Number of failed queries")
    avg_execution_time: float = Field(default=0.0, description="Average execution time")
    total_execution_time: float = Field(default=0.0, description="Total execution time")
    cache_hit_rate: float = Field(default=0.0, description="Cache hit rate percentage")
    last_query_at: Optional[datetime] = Field(default=None, description="Last query timestamp")
    period_start: datetime = Field(..., description="Metrics period start")
    period_end: datetime = Field(..., description="Metrics period end")


class ErrorLog(BaseModel):
    id: str = Field(..., description="Error log identifier")
    user_id: Optional[str] = Field(default=None, description="User identifier")
    error_type: str = Field(..., description="Type of error")
    error_message: str = Field(..., description="Error message")
    query_text: Optional[str] = Field(default=None, description="Query that caused error")
    stack_trace: Optional[str] = Field(default=None, description="Stack trace")
    request_data: Optional[Dict[str, Any]] = Field(default=None, description="Request data")
    created_at: datetime = Field(default_factory=datetime.now, description="Error timestamp")


class ApiUsage(BaseModel):
    api_key: str = Field(..., description="API key (masked)")
    requests_count: int = Field(default=0, description="Number of requests")
    successful_requests: int = Field(default=0, description="Number of successful requests")
    failed_requests: int = Field(default=0, description="Number of failed requests")
    last_request_at: Optional[datetime] = Field(default=None, description="Last request timestamp")
    rate_limit_exceeded: int = Field(default=0, description="Number of rate limit violations")
    daily_quota: int = Field(default=1000, description="Daily request quota")
    quota_used: int = Field(default=0, description="Quota used today")


# Response models for API endpoints
class HealthResponse(BaseModel):
    status: str = Field(..., description="Service status")
    timestamp: float = Field(..., description="Timestamp")
    version: str = Field(..., description="Service version")
    environment: str = Field(..., description="Environment")
    dependencies: Dict[str, str] = Field(default={}, description="Dependency status")


class LoginResponse(BaseModel):
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(..., description="Token expiration time in seconds")
    user: User = Field(..., description="User information")


class AdminStatsResponse(BaseModel):
    total_users: int = Field(..., description="Total number of users")
    active_users: int = Field(..., description="Number of active users")
    total_queries_today: int = Field(..., description="Total queries executed today")
    avg_response_time: float = Field(..., description="Average response time")
    error_rate: float = Field(..., description="Error rate percentage")
    cache_hit_rate: float = Field(..., description="Cache hit rate percentage")
    top_errors: List[Dict[str, Any]] = Field(default=[], description="Most common errors")
    
    
# Input validation schemas
class BulkQueryRequest(BaseModel):
    questions: List[str] = Field(..., min_items=1, max_items=10, description="List of questions")
    database_url: str = Field(..., description="Database connection URL")
    include_explanation: bool = Field(default=True, description="Include explanations")
    max_results: int = Field(default=100, ge=1, le=1000, description="Maximum results per query")
    
    @validator('questions')
    def validate_questions(cls, v):
        if not v:
            raise ValueError('At least one question is required')
        for i, question in enumerate(v):
            if not question.strip():
                raise ValueError(f'Question {i+1} cannot be empty')
        return [q.strip() for q in v]
