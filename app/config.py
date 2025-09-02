"""
Enterprise NL2SQL Configuration Management
"""

import os
from typing import List, Optional
from pydantic import BaseSettings, validator
import secrets


class Settings(BaseSettings):
    # API Configuration
    API_TITLE: str = "Enterprise NL2SQL Service"
    API_VERSION: str = "1.0.0"
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    DEBUG: bool = False
    ENVIRONMENT: str = "development"
    
    # Security
    SECRET_KEY: str = secrets.token_urlsafe(32)
    API_KEY: str = "change-this-in-production"
    JWT_SECRET_KEY: str = secrets.token_urlsafe(32)
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Database
    DATABASE_URL: str = "sqlite:///./nl2sql.db"
    DATABASE_POOL_SIZE: int = 10
    DATABASE_MAX_OVERFLOW: int = 20
    DATABASE_POOL_TIMEOUT: int = 30
    
    # LLM Configuration
    OPENAI_API_KEY: Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None
    LLM_MODEL: str = "gpt-4"
    LLM_TEMPERATURE: float = 0.0
    MAX_TOKENS: int = 2000
    LLM_TIMEOUT: int = 60
    
    # Cache Configuration
    REDIS_URL: str = "redis://localhost:6379"
    CACHE_TTL: int = 3600
    SCHEMA_CACHE_TTL: int = 86400
    
    # Query Configuration
    MAX_QUERY_TIME: int = 30
    MAX_RESULTS_DEFAULT: int = 100
    MAX_RESULTS_LIMIT: int = 1000
    
    # Monitoring
    SENTRY_DSN: Optional[str] = None
    LOG_LEVEL: str = "INFO"
    ENABLE_METRICS: bool = True
    
    # Rate Limiting
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_WINDOW: int = 3600
    
    # CORS
    CORS_ORIGINS: List[str] = ["*"]
    CORS_ALLOW_CREDENTIALS: bool = True
    
    # File Upload
    MAX_UPLOAD_SIZE: int = 10485760  # 10MB
    
    # Security Keywords
    ALLOWED_KEYWORDS: List[str] = [
        "SELECT", "WITH", "ORDER", "GROUP", "HAVING", "LIMIT", "OFFSET",
        "JOIN", "LEFT", "RIGHT", "INNER", "OUTER", "UNION", "DISTINCT",
        "WHERE", "AND", "OR", "NOT", "IN", "EXISTS", "BETWEEN", "LIKE",
        "COUNT", "SUM", "AVG", "MAX", "MIN", "EXTRACT", "DATE_TRUNC"
    ]
    
    DANGEROUS_KEYWORDS: List[str] = [
        "DROP", "DELETE", "UPDATE", "INSERT", "ALTER", "TRUNCATE",
        "CREATE", "GRANT", "REVOKE", "EXEC", "EXECUTE", "MERGE"
    ]
    
    @validator('CORS_ORIGINS', pre=True)
    def parse_cors_origins(cls, v):
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(',')]
        return v
    
    @validator('OPENAI_API_KEY')
    def validate_openai_key(cls, v):
        if not v and os.getenv('ENVIRONMENT') != 'test':
            raise ValueError('OPENAI_API_KEY is required for non-test environments')
        return v
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Create global settings instance
settings = Settings()

# Database URL for SQLAlchemy
DATABASE_URL = settings.DATABASE_URL

# Export commonly used settings
__all__ = ['settings', 'DATABASE_URL']
