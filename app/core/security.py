"""
Security and Authentication for NL2SQL Service
"""

import jwt
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError
from datetime import datetime, timedelta
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from passlib.context import CryptContext
import structlog

from app.config import settings
from app.models.schemas import User
from app.core.exceptions import AuthenticationError

logger = structlog.get_logger(__name__)

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Security scheme
security = HTTPBearer()


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt


def verify_token(token: str) -> dict:
    """Verify JWT token and return payload"""
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        return payload
    except ExpiredSignatureError:
        raise AuthenticationError("Token has expired")
    except InvalidTokenError:
        raise AuthenticationError("Invalid token")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash password"""
    return pwd_context.hash(password)


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Optional[User]:
    """Get current authenticated user from JWT token"""
    try:
        # Verify token
        payload = verify_token(credentials.credentials)
        user_id = payload.get("sub")
        
        if user_id is None:
            raise AuthenticationError("Invalid token payload")
        
        # In a real implementation, you would fetch user from database
        # For now, return a mock user
        user = User(
            id=user_id,
            email=payload.get("email"),
            name=payload.get("name"),
            is_active=True,
            permissions=payload.get("permissions", [])
        )
        
        return user
        
    except AuthenticationError:
        raise
    except Exception as e:
        logger.error("Authentication failed", error=str(e))
        raise AuthenticationError("Authentication failed")


async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """Get current active user"""
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


async def require_api_key(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    """Require valid API key for public endpoints"""
    try:
        api_key = credentials.credentials
        
        # Simple API key validation (in production, use a database)
        if api_key != settings.API_KEY:
            raise AuthenticationError("Invalid API key")
        
        return api_key
        
    except Exception as e:
        logger.error("API key validation failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
            headers={"WWW-Authenticate": "Bearer"},
        )


def require_permissions(required_permissions: list[str]):
    """Decorator to require specific permissions"""
    def permission_checker(current_user: User = Depends(get_current_user)) -> User:
        if not current_user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required"
            )
        
        user_permissions = set(current_user.permissions)
        required_permissions_set = set(required_permissions)
        
        if not required_permissions_set.issubset(user_permissions):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )
        
        return current_user
    
    return permission_checker


def require_admin(current_user: User = Depends(get_current_user)) -> User:
    """Require admin privileges"""
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )
    
    if "admin" not in current_user.permissions:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )
    
    return current_user


class APIKeyManager:
    """Manage API keys"""
    
    def __init__(self):
        # In production, store this in a database
        self.api_keys = {
            settings.API_KEY: {
                "name": "default",
                "created_at": datetime.utcnow(),
                "last_used": None,
                "is_active": True,
                "permissions": ["query:execute", "query:validate"],
                "rate_limit": 1000
            }
        }
    
    def validate_api_key(self, api_key: str) -> dict:
        """Validate API key and return its information"""
        key_info = self.api_keys.get(api_key)
        
        if not key_info:
            raise AuthenticationError("Invalid API key")
        
        if not key_info["is_active"]:
            raise AuthenticationError("API key is disabled")
        
        # Update last used timestamp
        key_info["last_used"] = datetime.utcnow()
        
        return key_info
    
    def create_api_key(self, name: str, permissions: list[str]) -> str:
        """Create new API key"""
        import secrets
        api_key = f"nl2sql_{secrets.token_urlsafe(32)}"
        
        self.api_keys[api_key] = {
            "name": name,
            "created_at": datetime.utcnow(),
            "last_used": None,
            "is_active": True,
            "permissions": permissions,
            "rate_limit": 1000
        }
        
        return api_key
    
    def revoke_api_key(self, api_key: str) -> bool:
        """Revoke API key"""
        if api_key in self.api_keys:
            self.api_keys[api_key]["is_active"] = False
            return True
        return False


# Global API key manager instance
api_key_manager = APIKeyManager()
