"""
Authentication Endpoints
"""

from datetime import timedelta
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr
import structlog

from app.core.security import (
    create_access_token, verify_password, get_password_hash,
    get_current_user, get_current_active_user
)
from app.models.schemas import User, LoginResponse
from app.config import settings

logger = structlog.get_logger(__name__)
router = APIRouter()


class UserCreate(BaseModel):
    email: EmailStr
    name: str
    password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int


# Mock user database (in production, use a real database)
fake_users_db = {
    "admin@example.com": {
        "id": "admin-user-id",
        "email": "admin@example.com",
        "name": "Admin User",
        "hashed_password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",  # "admin123"
        "is_active": True,
        "permissions": ["admin", "query:execute", "query:validate", "user:manage"]
    },
    "user@example.com": {
        "id": "regular-user-id", 
        "email": "user@example.com",
        "name": "Regular User",
        "hashed_password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",  # "user123"
        "is_active": True,
        "permissions": ["query:execute", "query:validate"]
    }
}


def authenticate_user(email: str, password: str) -> Optional[dict]:
    """Authenticate user credentials"""
    user = fake_users_db.get(email)
    if not user:
        return None
    if not verify_password(password, user["hashed_password"]):
        return None
    return user


@router.post("/login", response_model=LoginResponse)
async def login(user_credentials: UserLogin):
    """
    Authenticate user and return access token
    """
    try:
        # Authenticate user
        user_data = authenticate_user(user_credentials.email, user_credentials.password)
        if not user_data:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Create access token
        access_token_expires = timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={
                "sub": user_data["id"],
                "email": user_data["email"],
                "name": user_data["name"],
                "permissions": user_data["permissions"]
            },
            expires_delta=access_token_expires
        )
        
        user = User(
            id=user_data["id"],
            email=user_data["email"],
            name=user_data["name"],
            is_active=user_data["is_active"],
            permissions=user_data["permissions"]
        )
        
        logger.info("User logged in successfully", user_id=user_data["id"], email=user_data["email"])
        
        return LoginResponse(
            access_token=access_token,
            token_type="bearer",
            expires_in=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user=user
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Login failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed"
        )


@router.post("/register", response_model=User)
async def register(user_data: UserCreate):
    """
    Register a new user
    """
    try:
        # Check if user already exists
        if user_data.email in fake_users_db:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Create new user
        user_id = f"user-{len(fake_users_db) + 1}"
        hashed_password = get_password_hash(user_data.password)
        
        new_user = {
            "id": user_id,
            "email": user_data.email,
            "name": user_data.name,
            "hashed_password": hashed_password,
            "is_active": True,
            "permissions": ["query:execute", "query:validate"]
        }
        
        fake_users_db[user_data.email] = new_user
        
        user = User(
            id=new_user["id"],
            email=new_user["email"],
            name=new_user["name"],
            is_active=new_user["is_active"],
            permissions=new_user["permissions"]
        )
        
        logger.info("User registered successfully", user_id=user_id, email=user_data.email)
        
        return user
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Registration failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed"
        )


@router.get("/me", response_model=User)
async def get_current_user_info(current_user: User = Depends(get_current_active_user)):
    """
    Get current user information
    """
    return current_user


@router.post("/refresh")
async def refresh_token(current_user: User = Depends(get_current_user)):
    """
    Refresh access token
    """
    try:
        # Create new access token
        access_token_expires = timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={
                "sub": current_user.id,
                "email": current_user.email,
                "name": current_user.name,
                "permissions": current_user.permissions
            },
            expires_delta=access_token_expires
        )
        
        return TokenResponse(
            access_token=access_token,
            expires_in=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )
        
    except Exception as e:
        logger.error("Token refresh failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Token refresh failed"
        )


@router.post("/logout")
async def logout(current_user: User = Depends(get_current_user)):
    """
    Logout user (in a real implementation, you would invalidate the token)
    """
    logger.info("User logged out", user_id=current_user.id)
    return {"message": "Successfully logged out"}


@router.post("/change-password")
async def change_password(
    current_password: str,
    new_password: str,
    current_user: User = Depends(get_current_active_user)
):
    """
    Change user password
    """
    try:
        # Find user in fake database
        user_data = None
        for email, data in fake_users_db.items():
            if data["id"] == current_user.id:
                user_data = data
                break
        
        if not user_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Verify current password
        if not verify_password(current_password, user_data["hashed_password"]):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Incorrect current password"
            )
        
        # Update password
        user_data["hashed_password"] = get_password_hash(new_password)
        
        logger.info("Password changed successfully", user_id=current_user.id)
        
        return {"message": "Password changed successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Password change failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Password change failed"
        )
