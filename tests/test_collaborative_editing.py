"""Tests for collaborative editing WebSocket functionality."""
import pytest
from unittest.mock import AsyncMock, patch
import socketio
from resoftai.websocket.manager import manager, sio
from resoftai.websocket.events import (
    FileEditEvent,
    CursorPositionEvent,
    FileJoinEvent,
    FileLeaveEvent,
    UserOnlineEvent,
    UserOfflineEvent
)


class TestCollaborativeEditingEvents:
    """Test collaborative editing event models."""

    def test_file_edit_event_creation(self):
        """Test creating file edit event."""
        event = FileEditEvent(
            file_id=1,
            project_id=100,
            user_id=10,
            username="testuser",
            changes={"range": {"startLine": 1, "endLine": 1}, "text": "new code"},
            version=5
        )

        assert event.type == "file.edit"
        assert event.file_id == 1
        assert event.project_id == 100
        assert event.user_id == 10
        assert event.username == "testuser"
        assert event.version == 5
        assert event.timestamp is not None

    def test_cursor_position_event_creation(self):
        """Test creating cursor position event."""
        event = CursorPositionEvent(
            file_id=1,
            project_id=100,
            user_id=10,
            username="testuser",
            position={"lineNumber": 10, "column": 5},
            selection={"startLine": 10, "endLine": 12}
        )

        assert event.type == "cursor.position"
        assert event.file_id == 1
        assert event.position["lineNumber"] == 10
        assert event.position["column"] == 5
        assert event.selection is not None

    def test_file_join_event_creation(self):
        """Test creating file join event."""
        active_users = [
            {"user_id": 10, "username": "user1"},
            {"user_id": 20, "username": "user2"}
        ]

        event = FileJoinEvent(
            file_id=1,
            project_id=100,
            user_id=10,
            username="user1",
            active_users=active_users
        )

        assert event.type == "file.join"
        assert event.file_id == 1
        assert len(event.active_users) == 2

    def test_file_leave_event_creation(self):
        """Test creating file leave event."""
        active_users = [{"user_id": 20, "username": "user2"}]

        event = FileLeaveEvent(
            file_id=1,
            project_id=100,
            user_id=10,
            username="user1",
            active_users=active_users
        )

        assert event.type == "file.leave"
        assert event.user_id == 10
        assert len(event.active_users) == 1

    def test_user_online_event_creation(self):
        """Test creating user online event."""
        event = UserOnlineEvent(
            user_id=10,
            username="testuser",
            project_id=100,
            file_id=1
        )

        assert event.type == "user.online"
        assert event.user_id == 10
        assert event.file_id == 1

    def test_user_offline_event_creation(self):
        """Test creating user offline event."""
        event = UserOfflineEvent(
            user_id=10,
            username="testuser",
            project_id=100,
            file_id=1
        )

        assert event.type == "user.offline"
        assert event.user_id == 10


class TestConnectionManagerCollaborativeFeatures:
    """Test ConnectionManager collaborative editing features."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup for each test."""
        # Clear manager state before each test
        manager.file_sessions.clear()
        manager.session_user_info.clear()
        manager.file_versions.clear()
        yield
        # Cleanup after each test
        manager.file_sessions.clear()
        manager.session_user_info.clear()
        manager.file_versions.clear()

    @pytest.mark.asyncio
    async def test_join_file_session(self):
        """Test joining a file editing session."""
        sid = "test_session_1"
        file_id = 1
        project_id = 100
        user_id = 10
        username = "testuser"

        # Mock the sio.enter_room call
        with patch.object(sio, 'enter_room', new_callable=AsyncMock):
            await manager.join_file(sid, file_id, project_id, user_id, username)

        # Verify file session was created
        assert file_id in manager.file_sessions
        assert sid in manager.file_sessions[file_id]

        # Verify user info stored correctly
        assert sid in manager.session_user_info
        user_info = manager.session_user_info[sid]
        assert user_info['user_id'] == user_id
        assert user_info['username'] == username
        assert user_info['file_id'] == file_id

        # Verify version initialized
        assert manager.get_file_version(file_id) == 0

    @pytest.mark.asyncio
    async def test_leave_file_session(self):
        """Test leaving a file editing session."""
        sid = "test_session_1"
        file_id = 1

        # First join
        with patch.object(sio, 'enter_room', new_callable=AsyncMock):
            await manager.join_file(sid, file_id, 100, 10, "testuser")

        # Then leave
        with patch.object(sio, 'leave_room', new_callable=AsyncMock):
            await manager.leave_file(sid, file_id)

        # Verify cleanup
        assert file_id not in manager.file_sessions
        assert sid not in manager.session_user_info

    @pytest.mark.asyncio
    async def test_multiple_users_in_file(self):
        """Test multiple users joining the same file."""
        file_id = 1
        project_id = 100

        # Mock sio.enter_room for all join operations
        with patch.object(sio, 'enter_room', new_callable=AsyncMock):
            # User 1 joins
            await manager.join_file("sid1", file_id, project_id, 10, "user1")
            # User 2 joins
            await manager.join_file("sid2", file_id, project_id, 20, "user2")
            # User 3 joins
            await manager.join_file("sid3", file_id, project_id, 30, "user3")

        # Get active users
        active_users = manager.get_file_active_users(file_id)

        assert len(active_users) == 3
        usernames = [u['username'] for u in active_users]
        assert "user1" in usernames
        assert "user2" in usernames
        assert "user3" in usernames

    @pytest.mark.asyncio
    async def test_file_version_increment(self):
        """Test file version incrementing."""
        file_id = 1

        # Initialize version
        manager.file_versions[file_id] = 0

        # Increment multiple times
        v1 = manager.increment_file_version(file_id)
        v2 = manager.increment_file_version(file_id)
        v3 = manager.increment_file_version(file_id)

        assert v1 == 1
        assert v2 == 2
        assert v3 == 3
        assert manager.get_file_version(file_id) == 3

    @pytest.mark.asyncio
    async def test_get_file_active_users_empty(self):
        """Test getting active users for file with no users."""
        active_users = manager.get_file_active_users(999)
        assert active_users == []

    @pytest.mark.asyncio
    async def test_user_leaving_updates_active_users(self):
        """Test that leaving updates active users list."""
        file_id = 1

        # Multiple users join
        with patch.object(sio, 'enter_room', new_callable=AsyncMock):
            await manager.join_file("sid1", file_id, 100, 10, "user1")
            await manager.join_file("sid2", file_id, 100, 20, "user2")

        assert len(manager.get_file_active_users(file_id)) == 2

        # One user leaves
        with patch.object(sio, 'leave_room', new_callable=AsyncMock):
            await manager.leave_file("sid1", file_id)

        active_users = manager.get_file_active_users(file_id)
        assert len(active_users) == 1
        assert active_users[0]['username'] == "user2"

    @pytest.mark.asyncio
    async def test_file_session_cleanup_when_last_user_leaves(self):
        """Test file session is cleaned up when last user leaves."""
        file_id = 1

        # User joins
        with patch.object(sio, 'enter_room', new_callable=AsyncMock):
            await manager.join_file("sid1", file_id, 100, 10, "user1")
        assert file_id in manager.file_sessions
        assert file_id in manager.file_versions

        # User leaves (last user)
        with patch.object(sio, 'leave_room', new_callable=AsyncMock):
            await manager.leave_file("sid1", file_id)

        # Session should be cleaned up
        assert file_id not in manager.file_sessions
        assert file_id not in manager.file_versions


class TestCollaborativeEditingIntegration:
    """Integration tests for collaborative editing."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup for each test."""
        manager.file_sessions.clear()
        manager.session_user_info.clear()
        manager.file_versions.clear()
        yield
        manager.file_sessions.clear()
        manager.session_user_info.clear()
        manager.file_versions.clear()

    @pytest.mark.asyncio
    async def test_collaborative_editing_workflow(self):
        """Test complete collaborative editing workflow."""
        file_id = 1
        project_id = 100

        # Mock sio operations
        with patch.object(sio, 'enter_room', new_callable=AsyncMock), \
             patch.object(sio, 'leave_room', new_callable=AsyncMock):

            # Step 1: User 1 joins
            await manager.join_file("sid1", file_id, project_id, 10, "alice")
            assert manager.get_file_version(file_id) == 0

            # Step 2: User 2 joins
            await manager.join_file("sid2", file_id, project_id, 20, "bob")
            active_users = manager.get_file_active_users(file_id)
            assert len(active_users) == 2

            # Step 3: User 1 makes edit
            version1 = manager.increment_file_version(file_id)
            assert version1 == 1

            # Step 4: User 2 makes edit
            version2 = manager.increment_file_version(file_id)
            assert version2 == 2

            # Step 5: User 1 leaves
            await manager.leave_file("sid1", file_id)
            active_users = manager.get_file_active_users(file_id)
            assert len(active_users) == 1
            assert active_users[0]['username'] == "bob"

            # Step 6: User 2 leaves
            await manager.leave_file("sid2", file_id)
            assert file_id not in manager.file_sessions

    @pytest.mark.asyncio
    async def test_concurrent_users_different_files(self):
        """Test users editing different files concurrently."""
        # Mock sio operations
        with patch.object(sio, 'enter_room', new_callable=AsyncMock):
            # User 1 in file 1
            await manager.join_file("sid1", 1, 100, 10, "alice")

            # User 2 in file 2
            await manager.join_file("sid2", 2, 100, 20, "bob")

            # User 3 in file 1
            await manager.join_file("sid3", 1, 100, 30, "charlie")

        # Check file 1 has 2 users
        assert len(manager.get_file_active_users(1)) == 2

        # Check file 2 has 1 user
        assert len(manager.get_file_active_users(2)) == 1

        # Each file has independent version
        manager.increment_file_version(1)
        manager.increment_file_version(1)
        manager.increment_file_version(2)

        assert manager.get_file_version(1) == 2
        assert manager.get_file_version(2) == 1
