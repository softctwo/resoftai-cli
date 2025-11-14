"""Tests for WebSocket connection manager."""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from resoftai.websocket.manager import ConnectionManager


class TestConnectionManager:
    """Test ConnectionManager class."""

    @pytest.fixture
    def manager(self):
        """Create a connection manager instance."""
        return ConnectionManager()

    @pytest.mark.asyncio
    async def test_initialization(self, manager):
        """Test manager initialization."""
        assert isinstance(manager.active_connections, dict)
        assert isinstance(manager.user_connections, dict)
        assert isinstance(manager.file_sessions, dict)
        assert isinstance(manager.session_user_info, dict)
        assert isinstance(manager.file_versions, dict)
        assert len(manager.active_connections) == 0
        assert len(manager.user_connections) == 0

    @pytest.mark.asyncio
    async def test_connect_to_project(self, manager):
        """Test connecting to a project."""
        with patch('resoftai.websocket.manager.sio') as mock_sio:
            mock_sio.enter_room = AsyncMock()

            await manager.connect(sid="test_sid", project_id="1", user_id=100)

            # Verify project tracking
            assert "1" in manager.active_connections
            assert "test_sid" in manager.active_connections["1"]

            # Verify user tracking
            assert 100 in manager.user_connections
            assert "test_sid" in manager.user_connections[100]

            # Verify room joining
            mock_sio.enter_room.assert_called_once_with("test_sid", "project:1")

    @pytest.mark.asyncio
    async def test_connect_multiple_users_to_project(self, manager):
        """Test multiple users connecting to the same project."""
        with patch('resoftai.websocket.manager.sio') as mock_sio:
            mock_sio.enter_room = AsyncMock()

            await manager.connect(sid="sid1", project_id="1", user_id=100)
            await manager.connect(sid="sid2", project_id="1", user_id=200)
            await manager.connect(sid="sid3", project_id="1", user_id=100)

            # Verify multiple users in same project
            assert len(manager.active_connections["1"]) == 3
            assert "sid1" in manager.active_connections["1"]
            assert "sid2" in manager.active_connections["1"]
            assert "sid3" in manager.active_connections["1"]

            # Verify user 100 has 2 sessions
            assert len(manager.user_connections[100]) == 2
            assert "sid1" in manager.user_connections[100]
            assert "sid3" in manager.user_connections[100]

            # Verify user 200 has 1 session
            assert len(manager.user_connections[200]) == 1
            assert "sid2" in manager.user_connections[200]

    @pytest.mark.asyncio
    async def test_connect_without_user_id(self, manager):
        """Test connecting without user ID."""
        with patch('resoftai.websocket.manager.sio') as mock_sio:
            mock_sio.enter_room = AsyncMock()

            await manager.connect(sid="test_sid", project_id="1", user_id=None)

            # Verify project tracking
            assert "1" in manager.active_connections
            assert "test_sid" in manager.active_connections["1"]

            # Verify user tracking is empty (no user_id)
            assert len(manager.user_connections) == 0

    @pytest.mark.asyncio
    async def test_disconnect(self, manager):
        """Test disconnecting a session."""
        with patch('resoftai.websocket.manager.sio') as mock_sio:
            mock_sio.enter_room = AsyncMock()
            mock_sio.leave_room = AsyncMock()

            # Connect first
            await manager.connect(sid="test_sid", project_id="1", user_id=100)

            # Verify connected
            assert "test_sid" in manager.active_connections["1"]
            assert "test_sid" in manager.user_connections[100]

            # Disconnect
            await manager.disconnect(sid="test_sid")

            # Verify disconnected and cleaned up
            assert "1" not in manager.active_connections
            assert 100 not in manager.user_connections
            mock_sio.leave_room.assert_called_once_with("test_sid", "project:1")

    @pytest.mark.asyncio
    async def test_disconnect_one_of_multiple_sessions(self, manager):
        """Test disconnecting one session while others remain."""
        with patch('resoftai.websocket.manager.sio') as mock_sio:
            mock_sio.enter_room = AsyncMock()
            mock_sio.leave_room = AsyncMock()

            # Connect multiple sessions
            await manager.connect(sid="sid1", project_id="1", user_id=100)
            await manager.connect(sid="sid2", project_id="1", user_id=100)

            # Disconnect one
            await manager.disconnect(sid="sid1")

            # Verify project still has one session
            assert "1" in manager.active_connections
            assert "sid2" in manager.active_connections["1"]
            assert "sid1" not in manager.active_connections["1"]

            # Verify user still has one session
            assert 100 in manager.user_connections
            assert "sid2" in manager.user_connections[100]
            assert "sid1" not in manager.user_connections[100]

    @pytest.mark.asyncio
    async def test_disconnect_nonexistent_session(self, manager):
        """Test disconnecting a session that doesn't exist."""
        with patch('resoftai.websocket.manager.sio') as mock_sio:
            mock_sio.leave_room = AsyncMock()

            # Should not raise an error
            await manager.disconnect(sid="nonexistent_sid")

            # Should not have called leave_room
            assert mock_sio.leave_room.call_count == 0

    @pytest.mark.asyncio
    async def test_broadcast_to_project(self, manager):
        """Test broadcasting to a project room."""
        with patch('resoftai.websocket.manager.sio') as mock_sio:
            mock_sio.emit = AsyncMock()

            await manager.broadcast_to_project(
                project_id=1,
                event="test_event",
                data={"message": "Hello"}
            )

            mock_sio.emit.assert_called_once_with(
                "test_event",
                {"message": "Hello"},
                room="project:1"
            )

    @pytest.mark.asyncio
    async def test_broadcast_to_user(self, manager):
        """Test broadcasting to a user's sessions."""
        with patch('resoftai.websocket.manager.sio') as mock_sio:
            mock_sio.enter_room = AsyncMock()
            mock_sio.emit = AsyncMock()

            # Connect user with 2 sessions
            await manager.connect(sid="sid1", project_id="1", user_id=100)
            await manager.connect(sid="sid2", project_id="1", user_id=100)

            # Broadcast to user
            await manager.broadcast_to_user(
                user_id=100,
                event="notification",
                data={"message": "Test"}
            )

            # Should emit to both sessions
            assert mock_sio.emit.call_count == 2
            calls = mock_sio.emit.call_args_list
            assert calls[0][0][0] == "notification"
            assert calls[0][0][1] == {"message": "Test"}

    @pytest.mark.asyncio
    async def test_broadcast_to_nonexistent_user(self, manager):
        """Test broadcasting to a user that doesn't exist."""
        with patch('resoftai.websocket.manager.sio') as mock_sio:
            mock_sio.emit = AsyncMock()

            # Broadcast to nonexistent user
            await manager.broadcast_to_user(
                user_id=999,
                event="test_event",
                data={}
            )

            # Should not emit
            assert mock_sio.emit.call_count == 0

    @pytest.mark.asyncio
    async def test_get_connection_count(self, manager):
        """Test getting connection counts."""
        with patch('resoftai.websocket.manager.sio') as mock_sio:
            mock_sio.enter_room = AsyncMock()

            # Connect multiple sessions
            await manager.connect(sid="sid1", project_id="1", user_id=100)
            await manager.connect(sid="sid2", project_id="1", user_id=200)
            await manager.connect(sid="sid3", project_id="2", user_id=100)

            # Check counts
            assert len(manager.active_connections) == 2  # 2 projects
            assert len(manager.active_connections["1"]) == 2  # 2 sessions in project 1
            assert len(manager.active_connections["2"]) == 1  # 1 session in project 2
            assert len(manager.user_connections) == 2  # 2 users
            assert len(manager.user_connections[100]) == 2  # user 100 has 2 sessions
            assert len(manager.user_connections[200]) == 1  # user 200 has 1 session

    @pytest.mark.asyncio
    async def test_file_versions_tracking(self, manager):
        """Test file version tracking."""
        # Set file versions
        manager.file_versions[1] = 10
        manager.file_versions[2] = 5

        assert manager.file_versions[1] == 10
        assert manager.file_versions[2] == 5
        assert len(manager.file_versions) == 2

        # Update version
        manager.file_versions[1] = 11
        assert manager.file_versions[1] == 11

    @pytest.mark.asyncio
    async def test_file_sessions_tracking(self, manager):
        """Test file editing sessions tracking."""
        # Add file sessions
        manager.file_sessions[1] = {
            "sid1": {"user_id": 100, "username": "user1"},
            "sid2": {"user_id": 200, "username": "user2"}
        }

        assert 1 in manager.file_sessions
        assert len(manager.file_sessions[1]) == 2
        assert manager.file_sessions[1]["sid1"]["user_id"] == 100
        assert manager.file_sessions[1]["sid2"]["username"] == "user2"

    @pytest.mark.asyncio
    async def test_session_user_info_tracking(self, manager):
        """Test session user info tracking."""
        # Set session info
        manager.session_user_info["sid1"] = {
            "user_id": 100,
            "username": "testuser"
        }

        assert "sid1" in manager.session_user_info
        assert manager.session_user_info["sid1"]["user_id"] == 100
        assert manager.session_user_info["sid1"]["username"] == "testuser"


class TestConnectionManagerIntegration:
    """Integration tests for ConnectionManager."""

    @pytest.mark.asyncio
    async def test_full_connection_lifecycle(self):
        """Test complete connection lifecycle."""
        manager = ConnectionManager()

        with patch('resoftai.websocket.manager.sio') as mock_sio:
            mock_sio.enter_room = AsyncMock()
            mock_sio.leave_room = AsyncMock()
            mock_sio.emit = AsyncMock()

            # 1. Connect
            await manager.connect(sid="sid1", project_id="1", user_id=100)
            assert "sid1" in manager.active_connections["1"]

            # 2. Broadcast to project
            await manager.broadcast_to_project(1, "update", {"data": "test"})
            assert mock_sio.emit.called

            # 3. Broadcast to user
            await manager.broadcast_to_user(100, "notification", {"msg": "hi"})
            assert mock_sio.emit.call_count >= 2

            # 4. Disconnect
            await manager.disconnect("sid1")
            assert "1" not in manager.active_connections
            assert 100 not in manager.user_connections

    @pytest.mark.asyncio
    async def test_multiple_projects_and_users(self):
        """Test complex scenario with multiple projects and users."""
        manager = ConnectionManager()

        with patch('resoftai.websocket.manager.sio') as mock_sio:
            mock_sio.enter_room = AsyncMock()
            mock_sio.leave_room = AsyncMock()
            mock_sio.emit = AsyncMock()

            # User 100 connects to project 1 and 2
            await manager.connect(sid="u100_p1", project_id="1", user_id=100)
            await manager.connect(sid="u100_p2", project_id="2", user_id=100)

            # User 200 connects to project 1
            await manager.connect(sid="u200_p1", project_id="1", user_id=200)

            # User 300 connects to project 2 (two sessions)
            await manager.connect(sid="u300_p2_s1", project_id="2", user_id=300)
            await manager.connect(sid="u300_p2_s2", project_id="2", user_id=300)

            # Verify state
            assert len(manager.active_connections) == 2
            assert len(manager.active_connections["1"]) == 2  # u100, u200
            assert len(manager.active_connections["2"]) == 3  # u100, u300x2

            assert len(manager.user_connections) == 3
            assert len(manager.user_connections[100]) == 2  # 2 projects
            assert len(manager.user_connections[200]) == 1  # 1 project
            assert len(manager.user_connections[300]) == 2  # 2 sessions

            # Broadcast to project 1
            mock_sio.emit.reset_mock()
            await manager.broadcast_to_project(1, "event1", {})
            assert mock_sio.emit.call_count == 1

            # Broadcast to user 300 (should hit 2 sessions)
            mock_sio.emit.reset_mock()
            await manager.broadcast_to_user(300, "event2", {})
            assert mock_sio.emit.call_count == 2

            # Disconnect one session of user 300
            await manager.disconnect("u300_p2_s1")
            assert len(manager.user_connections[300]) == 1
            assert len(manager.active_connections["2"]) == 2  # u100, u300 (1 session left)

            # Disconnect last session of user 300
            await manager.disconnect("u300_p2_s2")
            assert 300 not in manager.user_connections
            assert len(manager.active_connections["2"]) == 1  # only u100 left
