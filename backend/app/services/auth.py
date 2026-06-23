from datetime import timedelta
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    get_password_hash,
    verify_password,
)
from app.models.user import User
from app.redis_client import get_redis
from app.schemas.user import Token


async def authenticate_user(db: AsyncSession, username: str, password: str) -> Optional[User]:
    """Authenticate a user by username/email and password."""
    # Try to find by username first
    result = await db.execute(select(User).where(User.username == username))
    user = result.scalar_one_or_none()

    # Try by email if not found
    if user is None:
        result = await db.execute(select(User).where(User.email == username))
        user = result.scalar_one_or_none()

    if user is None:
        return None

    if not verify_password(password, user.hashed_password):
        return None

    return user


async def create_tokens(user: User) -> Token:
    """Create access and refresh tokens for a user."""
    access_token = create_access_token(
        subject=user.id,
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    refresh_token = create_refresh_token(subject=user.id)

    # Store refresh token in Redis
    redis_conn = await get_redis()
    await redis_conn.setex(
        f"refresh_token:{user.id}:{refresh_token}",
        settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
        "valid",
    )

    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
    )


async def refresh_access_token(refresh_token_str: str) -> Optional[Token]:
    """Refresh access token using refresh token."""
    payload = decode_token(refresh_token_str)
    if payload is None:
        return None

    if payload.get("type") != "refresh":
        return None

    user_id = payload.get("sub")
    if user_id is None:
        return None

    # Check if refresh token exists in Redis
    redis_conn = await get_redis()
    token_key = f"refresh_token:{user_id}:{refresh_token_str}"
    exists = await redis_conn.get(token_key)
    if not exists:
        return None

    # Delete old refresh token
    await redis_conn.delete(token_key)

    # Create new tokens
    from app.database import async_session_factory
    from app.models.user import User
    from sqlalchemy import select

    async with async_session_factory() as db:
        result = await db.execute(select(User).where(User.id == int(user_id)))
        user = result.scalar_one_or_none()
        if user is None or not user.is_active:
            return None

        return await create_tokens(user)


async def logout_user(user_id: int, access_token: str, refresh_token: str):
    """Logout user by blacklisting tokens in Redis."""
    redis_conn = await get_redis()

    # Blacklist access token (until it expires)
    payload = decode_token(access_token)
    if payload:
        exp = payload.get("exp", 0)
        from datetime import datetime, timezone
        ttl = max(0, exp - int(datetime.now(timezone.utc).timestamp()))
        if ttl > 0:
            await redis_conn.setex(f"blacklist:{access_token}", ttl, "1")

    # Remove refresh token
    await redis_conn.delete(f"refresh_token:{user_id}:{refresh_token}")


async def create_user(db: AsyncSession, username: str, email: str, password: str, full_name: str = "", is_superuser: bool = False) -> User:
    """Create a new user."""
    user = User(
        username=username,
        email=email,
        hashed_password=get_password_hash(password),
        full_name=full_name,
        is_superuser=is_superuser,
        is_active=True,
    )
    db.add(user)
    await db.flush()
    await db.refresh(user)
    return user
