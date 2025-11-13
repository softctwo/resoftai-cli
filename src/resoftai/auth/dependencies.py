"""Authentication dependencies for FastAPI."""
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from resoftai.db import get_db
from resoftai.models.user import User
from resoftai.crud.user import get_user_by_username, get_user_by_id
from resoftai.auth.security import verify_token

# OAuth2 scheme for token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
) -> User:
    """
    Get current authenticated user from JWT token.

    Args:
        token: JWT access token
        db: Database session

    Returns:
        Current User object

    Raises:
        HTTPException: If token is invalid or user not found
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    token_data = verify_token(token, token_type="access")
    if token_data is None:
        raise credentials_exception

    # Try to get user by ID first, fallback to username
    user: Optional[User] = None
    if token_data.user_id:
        user = await get_user_by_id(db, user_id=token_data.user_id)
    elif token_data.username:
        user = await get_user_by_username(db, username=token_data.username)

    if user is None:
        raise credentials_exception

    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Get current active user (not deactivated).

    Args:
        current_user: Current user from token

    Returns:
        Current active User object

    Raises:
        HTTPException: If user is inactive
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return current_user


async def require_admin(
    current_user: User = Depends(get_current_active_user)
) -> User:
    """
    Require admin role.

    Args:
        current_user: Current active user

    Returns:
        Current admin User object

    Raises:
        HTTPException: If user is not admin
    """
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions. Admin role required."
        )
    return current_user


async def get_optional_user(
    token: Optional[str] = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
) -> Optional[User]:
    """
    Get current user if token is provided, otherwise return None.
    Useful for endpoints that work both with and without authentication.

    Args:
        token: Optional JWT access token
        db: Database session

    Returns:
        User object if authenticated, None otherwise
    """
    if not token:
        return None

    token_data = verify_token(token, token_type="access")
    if token_data is None:
        return None

    if token_data.user_id:
        return await get_user_by_id(db, user_id=token_data.user_id)
    elif token_data.username:
        return await get_user_by_username(db, username=token_data.username)

    return None
