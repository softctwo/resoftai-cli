"""
Tests for authentication security module.
"""
from datetime import timedelta, datetime
import pytest
from jose import jwt, JWTError
from resoftai.auth.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    create_refresh_token,
    verify_token,
    Token,
    TokenData,
)
from resoftai.config import Settings


def test_password_hashing():
    """Test password hashing and verification."""
    password = "test_password_123"
    hashed = get_password_hash(password)

    # Verify the password hash is different from plain password
    assert hashed != password
    # Verify the hash is not empty
    assert len(hashed) > 0
    # Verify password verification works
    assert verify_password(password, hashed) is True
    # Verify wrong password fails
    assert verify_password("wrong_password", hashed) is False


def test_password_hash_uniqueness():
    """Test that same password generates different hashes (due to salt)."""
    password = "test_password"
    hash1 = get_password_hash(password)
    hash2 = get_password_hash(password)

    # Hashes should be different due to random salt
    assert hash1 != hash2
    # But both should verify correctly
    assert verify_password(password, hash1) is True
    assert verify_password(password, hash2) is True


def test_create_access_token_default_expiration():
    """Test creating access token with default expiration."""
    data = {"sub": "testuser", "user_id": 123}
    token = create_access_token(data)

    # Verify token is not empty
    assert token
    assert isinstance(token, str)

    # Decode and verify
    settings = Settings()
    payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])

    assert payload["sub"] == "testuser"
    assert payload["user_id"] == 123
    assert payload["type"] == "access"
    assert "exp" in payload


def test_create_access_token_custom_expiration():
    """Test creating access token with custom expiration."""
    data = {"sub": "testuser", "user_id": 123}
    expires_delta = timedelta(minutes=60)
    token = create_access_token(data, expires_delta)

    # Verify token
    assert token
    settings = Settings()
    payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])

    # Verify expiration is approximately 60 minutes from now
    exp_time = datetime.fromtimestamp(payload["exp"])
    expected_exp = datetime.utcnow() + expires_delta
    # Allow 5 second tolerance
    assert abs((exp_time - expected_exp).total_seconds()) < 5


def test_create_refresh_token():
    """Test creating refresh token."""
    data = {"sub": "testuser", "user_id": 456}
    token = create_refresh_token(data)

    # Verify token
    assert token
    settings = Settings()
    payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])

    assert payload["sub"] == "testuser"
    assert payload["user_id"] == 456
    assert payload["type"] == "refresh"
    assert "exp" in payload


def test_verify_token_valid_access():
    """Test verifying a valid access token."""
    data = {"sub": "testuser", "user_id": 789}
    token = create_access_token(data)

    token_data = verify_token(token, token_type="access")

    assert token_data is not None
    assert token_data.username == "testuser"
    assert token_data.user_id == 789


def test_verify_token_valid_refresh():
    """Test verifying a valid refresh token."""
    data = {"sub": "refreshuser", "user_id": 999}
    token = create_refresh_token(data)

    token_data = verify_token(token, token_type="refresh")

    assert token_data is not None
    assert token_data.username == "refreshuser"
    assert token_data.user_id == 999


def test_verify_token_wrong_type():
    """Test that access token fails when verified as refresh token."""
    data = {"sub": "testuser", "user_id": 123}
    access_token = create_access_token(data)

    # Try to verify as refresh token - should fail
    token_data = verify_token(access_token, token_type="refresh")

    assert token_data is None


def test_verify_token_invalid():
    """Test verifying an invalid token."""
    invalid_token = "invalid.jwt.token"

    token_data = verify_token(invalid_token, token_type="access")

    assert token_data is None


def test_verify_token_expired():
    """Test verifying an expired token."""
    data = {"sub": "testuser", "user_id": 123}
    # Create token that expired 1 hour ago
    expires_delta = timedelta(hours=-1)
    token = create_access_token(data, expires_delta)

    token_data = verify_token(token, token_type="access")

    assert token_data is None


def test_verify_token_no_username():
    """Test token without username (sub claim)."""
    settings = Settings()
    # Create token without 'sub' claim
    data = {"user_id": 123, "type": "access"}
    expire = datetime.utcnow() + timedelta(minutes=30)
    data.update({"exp": expire})

    token = jwt.encode(data, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)

    token_data = verify_token(token, token_type="access")

    assert token_data is None


def test_token_model():
    """Test Token model."""
    token = Token(
        access_token="access_token_123",
        refresh_token="refresh_token_456"
    )

    assert token.access_token == "access_token_123"
    assert token.refresh_token == "refresh_token_456"
    assert token.token_type == "bearer"


def test_token_data_model():
    """Test TokenData model."""
    token_data = TokenData(username="testuser", user_id=123)

    assert token_data.username == "testuser"
    assert token_data.user_id == 123


def test_token_data_optional_fields():
    """Test TokenData with optional fields."""
    token_data = TokenData()

    assert token_data.username is None
    assert token_data.user_id is None
