"""CRUD operations for User model."""
from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime

from resoftai.models.user import User
from resoftai.auth.security import get_password_hash


async def get_user_by_id(db: AsyncSession, user_id: int) -> Optional[User]:
    """Get user by ID."""
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()


async def get_user_by_username(db: AsyncSession, username: str) -> Optional[User]:
    """Get user by username."""
    result = await db.execute(select(User).where(User.username == username))
    return result.scalar_one_or_none()


async def get_user_by_email(db: AsyncSession, email: str) -> Optional[User]:
    """Get user by email."""
    result = await db.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()


async def create_user(
    db: AsyncSession,
    username: str,
    email: str,
    password: str,
    role: str = "user"
) -> User:
    """
    Create a new user.

    Args:
        db: Database session
        username: Username
        email: Email address
        password: Plain text password (will be hashed)
        role: User role (default: 'user')

    Returns:
        Created User object
    """
    password_hash = get_password_hash(password)

    user = User(
        username=username,
        email=email,
        password_hash=password_hash,
        role=role,
        is_active=True,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )

    db.add(user)
    await db.commit()
    await db.refresh(user)

    return user


async def update_user_last_login(db: AsyncSession, user_id: int) -> None:
    """Update user's last login timestamp."""
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if user:
        user.last_login = datetime.utcnow()
        await db.commit()


async def update_user(
    db: AsyncSession,
    user_id: int,
    **kwargs
) -> Optional[User]:
    """
    Update user fields.

    Args:
        db: Database session
        user_id: User ID
        **kwargs: Fields to update

    Returns:
        Updated User object or None
    """
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        return None

    for key, value in kwargs.items():
        if hasattr(user, key):
            setattr(user, key, value)

    user.updated_at = datetime.utcnow()
    await db.commit()
    await db.refresh(user)

    return user


async def deactivate_user(db: AsyncSession, user_id: int) -> Optional[User]:
    """Deactivate a user (soft delete)."""
    return await update_user(db, user_id, is_active=False)
