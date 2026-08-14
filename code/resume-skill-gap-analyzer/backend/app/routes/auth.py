"""
Authentication Routes
==================
Login, Register, Logout with JWT and password hashing.
"""

from datetime import timedelta
from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.models import User
from app.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_access_token,
    generate_token_id
)

router = APIRouter()
security = HTTPBearer()


# Request models
class RegisterRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=100)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: Optional[str] = None
    token_type: str = "bearer"
    expires_in: int = 60  # days


class UserResponse(BaseModel):
    id: str
    name: str
    email: str


class RefreshTokenRequest(BaseModel):
    refresh_token: str


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> dict:
    """Get current authenticated user"""
    token = credentials.credentials
    payload = decode_access_token(token)
    
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )
    
    user_id = payload.get("sub")
    user_email = payload.get("email")
    
    if not user_id or not user_email:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
        )
    
    # Find user by email
    user = db.query(User).filter(User.email == user_email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )
    
    return {
        "id": user.id, "name": user.name, "email": user.email,
    }

@router.post("/register", response_model=TokenResponse)
async def register(request: RegisterRequest, db: Session = Depends(get_db)):
    """Register new user with hashed password"""
    # Check if email exists
    db_user = db.query(User).filter(User.email == request.email).first()
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )
    
    # Generate user ID
    user_id = generate_token_id(16)
    
    # Hash password before storing
    hashed_pw = hash_password(request.password)
    
    # Store user with hashed password
    new_user = User(
        id=user_id,
        name=request.name,
        email=request.email,
        password_hash=hashed_pw
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # Create tokens (60 days expiry)
    access_token = create_access_token(
        data={"sub": user_id, "email": request.email},
        expires_delta=timedelta(days=60)
    )
    refresh_token = create_refresh_token(
        data={"sub": user_id, "email": request.email}
    )
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=60
    )


@router.post("/login", response_model=TokenResponse)
async def login(request: LoginRequest, db: Session = Depends(get_db)):
    """Login user with password verification"""
    # Find user
    user = db.query(User).filter(User.email == request.email).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )
    
    # Verify password against hash
    if not verify_password(request.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )
    
    # Create tokens (60 days expiry)
    access_token = create_access_token(
        data={"sub": user.id, "email": request.email},
        expires_delta=timedelta(days=60)
    )
    refresh_token = create_refresh_token(
        data={"sub": user.id, "email": request.email}
    )
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=60
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(request: RefreshTokenRequest, db: Session = Depends(get_db)):
    """Refresh access token using refresh token"""
    payload = decode_access_token(request.refresh_token)
    
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
        )
    
    # Check if it's a refresh token
    if payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type",
        )
    
    user_id = payload.get("sub")
    user_email = payload.get("email")
    
    if not user_id or not user_email:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
        )
    
    # Verify user still exists
    user = db.query(User).filter(User.email == user_email).first()
    if not user or user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )
    
    # Generate new tokens
    access_token = create_access_token(
        data={"sub": user_id, "email": user_email},
        expires_delta=timedelta(days=60)
    )
    new_refresh_token = create_refresh_token(
        data={"sub": user_id, "email": user_email}
    )
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=new_refresh_token,
        token_type="bearer",
        expires_in=60
    )


@router.post("/logout")
async def logout():
    """Logout user"""
    # In production: add token to blacklist
    return {"message": "Logged out successfully"}


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """Get current user info (protected route)"""
    return UserResponse(
        id=current_user["id"],
        name=current_user["name"],
        email=current_user["email"],
    )


@router.delete("/delete-account")
async def delete_account(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete user account"""
    # Remove user from database
    user_email = current_user["email"]
    user = db.query(User).filter(User.email == user_email).first()
    if user:
        db.delete(user)
        db.commit()
        return {"message": "Account deleted successfully"}
    
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="User not found",
    )