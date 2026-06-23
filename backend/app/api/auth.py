from fastapi import APIRouter, Depends, HTTPException, status, Header
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.database import get_db
from app.core.deps import get_current_user
from app.config import settings
from app.models.user import User
from app.schemas.user import (
    Token,
    TokenRefresh,
    Message,
    UserCreate,
    UserResponse,
    ChangePasswordRequest,
)
from app.services import auth as auth_service
from app.services import user as user_service
from app.redis_client import get_redis

router = APIRouter(prefix=f"{settings.API_V1_STR}/auth", tags=["auth"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    *,
    db: AsyncSession = Depends(get_db),
    user_in: UserCreate,
):
    """Register a new user."""
    # Check if username already exists
    existing_user = await user_service.get_user_by_username(db, user_in.username)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username already registered",
        )

    # Check if email already exists
    existing_email = await user_service.get_user_by_email(db, user_in.email)
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered",
        )

    user = await user_service.create_user(db, user_in)
    return user


@router.post("/login", response_model=Token)
async def login(
    db: AsyncSession = Depends(get_db),
    form_data: OAuth2PasswordRequestForm = Depends(),
):
    """Login with username/email and password."""
    user = await auth_service.authenticate_user(
        db, form_data.username, form_data.password
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username/email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user account",
        )

    tokens = await auth_service.create_tokens(user)
    return tokens


@router.post("/refresh", response_model=Token)
async def refresh_token(
    *,
    refresh_in: TokenRefresh,
):
    """Refresh access token using refresh token."""
    tokens = await auth_service.refresh_access_token(refresh_in.refresh_token)
    if tokens is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
        )
    return tokens


@router.post("/logout", response_model=Message)
async def logout(
    *,
    current_user: User = Depends(get_current_user),
    refresh_in: TokenRefresh,
    authorization: Optional[str] = Header(None),
):
    """Logout user and invalidate tokens."""
    redis = await get_redis()

    # Extract access token from Authorization header
    access_token = None
    if authorization and authorization.startswith("Bearer "):
        access_token = authorization[7:]

    # Blacklist the access token
    if access_token:
        from app.core.security import decode_token
        from datetime import datetime, timezone

        payload = decode_token(access_token)
        if payload:
            exp = payload.get("exp", 0)
            ttl = max(0, exp - int(datetime.now(timezone.utc).timestamp()))
            if ttl > 0:
                await redis.setex(f"blacklist:{access_token}", ttl, "1")

    # Remove refresh token from Redis
    await redis.delete(f"refresh_token:{current_user.id}:{refresh_in.refresh_token}")

    return Message(message="Successfully logged out")


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user),
):
    """Get current user information."""
    return current_user


@router.put("/change-password", response_model=Message)
async def change_password(
    *,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    password_in: ChangePasswordRequest,
):
    """Change current user's password."""
    from app.core.security import verify_password, get_password_hash

    if not verify_password(password_in.old_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect old password",
        )

    current_user.hashed_password = get_password_hash(password_in.new_password)
    await db.flush()

    return Message(message="Password changed successfully")
