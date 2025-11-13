"""Authentication module."""
from resoftai.auth.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    create_refresh_token,
    verify_token,
    Token,
    TokenData,
)

# Import dependencies separately to avoid circular imports
# from resoftai.auth.dependencies import (
#     get_current_user,
#     get_current_active_user,
#     require_admin,
#     get_optional_user,
# )

__all__ = [
    "verify_password",
    "get_password_hash",
    "create_access_token",
    "create_refresh_token",
    "verify_token",
    "Token",
    "TokenData",
    # "get_current_user",
    # "get_current_active_user",
    # "require_admin",
    # "get_optional_user",
]
