"""
Comprehensive tests for CRUD user operations.
"""
import pytest
from unittest.mock import Mock, AsyncMock, MagicMock, patch
from datetime import datetime

from resoftai.crud.user import (
    get_user_by_id,
    get_user_by_username,
    get_user_by_email,
    create_user,
    update_user_last_login,
    update_user,
    deactivate_user
)
from resoftai.models.user import User


@pytest.fixture
def mock_db():
    """Create mock database session."""
    db = AsyncMock()
    db.commit = AsyncMock()
    db.refresh = AsyncMock()
    db.add = Mock()
    return db


@pytest.fixture
def mock_user():
    """Create mock user."""
    user = User(
        id=1,
        username="testuser",
        email="test@example.com",
        password_hash="hashed_password",
        role="user",
        is_active=True,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    return user


class TestGetUser:
    """Test get user functions."""

    @pytest.mark.asyncio
    async def test_get_user_by_id_found(self, mock_db, mock_user):
        """Test getting user by ID when user exists."""
        # Mock database result
        mock_result = Mock()
        mock_result.scalar_one_or_none = Mock(return_value=mock_user)
        mock_db.execute = AsyncMock(return_value=mock_result)

        user = await get_user_by_id(mock_db, 1)

        assert user is not None
        assert user.id == 1
        assert user.username == "testuser"
        mock_db.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_user_by_id_not_found(self, mock_db):
        """Test getting user by ID when user doesn't exist."""
        mock_result = Mock()
        mock_result.scalar_one_or_none = Mock(return_value=None)
        mock_db.execute = AsyncMock(return_value=mock_result)

        user = await get_user_by_id(mock_db, 999)

        assert user is None
        mock_db.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_user_by_username_found(self, mock_db, mock_user):
        """Test getting user by username when user exists."""
        mock_result = Mock()
        mock_result.scalar_one_or_none = Mock(return_value=mock_user)
        mock_db.execute = AsyncMock(return_value=mock_result)

        user = await get_user_by_username(mock_db, "testuser")

        assert user is not None
        assert user.username == "testuser"
        mock_db.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_user_by_username_not_found(self, mock_db):
        """Test getting user by username when user doesn't exist."""
        mock_result = Mock()
        mock_result.scalar_one_or_none = Mock(return_value=None)
        mock_db.execute = AsyncMock(return_value=mock_result)

        user = await get_user_by_username(mock_db, "nonexistent")

        assert user is None
        mock_db.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_user_by_email_found(self, mock_db, mock_user):
        """Test getting user by email when user exists."""
        mock_result = Mock()
        mock_result.scalar_one_or_none = Mock(return_value=mock_user)
        mock_db.execute = AsyncMock(return_value=mock_result)

        user = await get_user_by_email(mock_db, "test@example.com")

        assert user is not None
        assert user.email == "test@example.com"
        mock_db.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_user_by_email_not_found(self, mock_db):
        """Test getting user by email when user doesn't exist."""
        mock_result = Mock()
        mock_result.scalar_one_or_none = Mock(return_value=None)
        mock_db.execute = AsyncMock(return_value=mock_result)

        user = await get_user_by_email(mock_db, "nonexistent@example.com")

        assert user is None
        mock_db.execute.assert_called_once()


class TestCreateUser:
    """Test create user function."""

    @pytest.mark.asyncio
    async def test_create_user_success(self, mock_db):
        """Test successful user creation."""
        with patch('resoftai.crud.user.get_password_hash', return_value="hashed_password"):
            # Create a mock user that will be returned after refresh
            created_user = User(
                id=1,
                username="newuser",
                email="new@example.com",
                password_hash="hashed_password",
                role="user",
                is_active=True,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )

            # Mock the refresh to populate the user
            async def mock_refresh(user):
                user.id = 1

            mock_db.refresh = mock_refresh

            user = await create_user(
                mock_db,
                username="newuser",
                email="new@example.com",
                password="plainpassword"
            )

            assert user.username == "newuser"
            assert user.email == "new@example.com"
            assert user.password_hash == "hashed_password"
            assert user.role == "user"
            assert user.is_active is True
            mock_db.add.assert_called_once()
            mock_db.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_user_with_custom_role(self, mock_db):
        """Test creating user with custom role."""
        with patch('resoftai.crud.user.get_password_hash', return_value="hashed_password"):
            async def mock_refresh(user):
                user.id = 1

            mock_db.refresh = mock_refresh

            user = await create_user(
                mock_db,
                username="admin",
                email="admin@example.com",
                password="adminpass",
                role="admin"
            )

            assert user.role == "admin"
            mock_db.add.assert_called_once()
            mock_db.commit.assert_called_once()


class TestUpdateUser:
    """Test update user functions."""

    @pytest.mark.asyncio
    async def test_update_user_last_login_success(self, mock_db, mock_user):
        """Test updating user's last login."""
        mock_result = Mock()
        mock_result.scalar_one_or_none = Mock(return_value=mock_user)
        mock_db.execute = AsyncMock(return_value=mock_result)

        await update_user_last_login(mock_db, 1)

        assert mock_user.last_login is not None
        mock_db.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_user_last_login_not_found(self, mock_db):
        """Test updating last login for non-existent user."""
        mock_result = Mock()
        mock_result.scalar_one_or_none = Mock(return_value=None)
        mock_db.execute = AsyncMock(return_value=mock_result)

        await update_user_last_login(mock_db, 999)

        # Should not commit if user not found
        mock_db.commit.assert_not_called()

    @pytest.mark.asyncio
    async def test_update_user_success(self, mock_db, mock_user):
        """Test successful user update."""
        mock_result = Mock()
        mock_result.scalar_one_or_none = Mock(return_value=mock_user)
        mock_db.execute = AsyncMock(return_value=mock_result)

        updated_user = await update_user(
            mock_db,
            user_id=1,
            email="newemail@example.com",
            role="admin"
        )

        assert updated_user is not None
        assert updated_user.email == "newemail@example.com"
        assert updated_user.role == "admin"
        assert updated_user.updated_at is not None
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_user_not_found(self, mock_db):
        """Test updating non-existent user."""
        mock_result = Mock()
        mock_result.scalar_one_or_none = Mock(return_value=None)
        mock_db.execute = AsyncMock(return_value=mock_result)

        updated_user = await update_user(
            mock_db,
            user_id=999,
            email="test@example.com"
        )

        assert updated_user is None
        mock_db.commit.assert_not_called()

    @pytest.mark.asyncio
    async def test_update_user_invalid_field(self, mock_db, mock_user):
        """Test updating user with invalid field."""
        mock_result = Mock()
        mock_result.scalar_one_or_none = Mock(return_value=mock_user)
        mock_db.execute = AsyncMock(return_value=mock_result)

        original_username = mock_user.username

        # Try to update with invalid field
        updated_user = await update_user(
            mock_db,
            user_id=1,
            invalid_field="value"
        )

        # Invalid field should be ignored
        assert updated_user is not None
        assert updated_user.username == original_username
        assert not hasattr(updated_user, 'invalid_field')


class TestDeactivateUser:
    """Test deactivate user function."""

    @pytest.mark.asyncio
    async def test_deactivate_user_success(self, mock_db, mock_user):
        """Test successful user deactivation."""
        mock_result = Mock()
        mock_result.scalar_one_or_none = Mock(return_value=mock_user)
        mock_db.execute = AsyncMock(return_value=mock_result)

        deactivated_user = await deactivate_user(mock_db, 1)

        assert deactivated_user is not None
        assert deactivated_user.is_active is False
        mock_db.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_deactivate_user_not_found(self, mock_db):
        """Test deactivating non-existent user."""
        mock_result = Mock()
        mock_result.scalar_one_or_none = Mock(return_value=None)
        mock_db.execute = AsyncMock(return_value=mock_result)

        deactivated_user = await deactivate_user(mock_db, 999)

        assert deactivated_user is None
        mock_db.commit.assert_not_called()


class TestUserIntegration:
    """Integration tests for user CRUD operations."""

    @pytest.mark.asyncio
    async def test_create_and_get_user_flow(self, mock_db):
        """Test complete user creation and retrieval flow."""
        with patch('resoftai.crud.user.get_password_hash', return_value="hashed"):
            # Create user
            async def mock_refresh(user):
                user.id = 1

            mock_db.refresh = mock_refresh

            created_user = await create_user(
                mock_db,
                username="flowtest",
                email="flow@example.com",
                password="testpass"
            )

            assert created_user.id == 1
            assert created_user.username == "flowtest"

            # Mock get operation
            mock_result = Mock()
            mock_result.scalar_one_or_none = Mock(return_value=created_user)
            mock_db.execute = AsyncMock(return_value=mock_result)

            # Get user by ID
            retrieved_user = await get_user_by_id(mock_db, 1)
            assert retrieved_user.id == 1
            assert retrieved_user.username == "flowtest"

    @pytest.mark.asyncio
    async def test_create_update_deactivate_flow(self, mock_db):
        """Test full user lifecycle."""
        with patch('resoftai.crud.user.get_password_hash', return_value="hashed"):
            # Create
            user = User(
                id=1,
                username="lifecycle",
                email="lifecycle@example.com",
                password_hash="hashed",
                role="user",
                is_active=True,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )

            mock_result = Mock()
            mock_result.scalar_one_or_none = Mock(return_value=user)
            mock_db.execute = AsyncMock(return_value=mock_result)

            # Update
            updated = await update_user(mock_db, 1, role="admin")
            assert updated.role == "admin"

            # Deactivate
            deactivated = await deactivate_user(mock_db, 1)
            assert deactivated.is_active is False
