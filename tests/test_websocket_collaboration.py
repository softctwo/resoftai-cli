"""Tests for WebSocket collaboration features."""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch


@pytest.mark.asyncio
async def test_join_file_editing():
    """Test joining a file editing session."""
    from resoftai.websocket.collaboration import active_editors

    # Clear active editors
    active_editors.clear()

    # Mock socket.io operations
    with patch('resoftai.websocket.collaboration.sio') as mock_sio:
        mock_sio.enter_room = AsyncMock()
        mock_sio.emit = AsyncMock()

        from resoftai.websocket.collaboration import join_file_editing

        # Simulate join event
        sid = "test_sid_123"
        data = {
            "file_id": 1,
            "user_id": 100,
            "project_id": 1,
            "username": "Test User"
        }

        await join_file_editing(sid, data)

        # Verify user was added to active editors
        assert 1 in active_editors
        assert 100 in active_editors[1]
        assert active_editors[1][100]["username"] == "Test User"

        # Verify socket.io room operations were called
        mock_sio.enter_room.assert_called_once()
        assert mock_sio.emit.call_count >= 1


@pytest.mark.asyncio
async def test_leave_file_editing():
    """Test leaving a file editing session."""
    from resoftai.websocket.collaboration import active_editors

    # Setup initial state
    active_editors.clear()
    active_editors[1] = {
        100: {
            "sid": "test_sid",
            "username": "Test User",
            "cursor_position": None
        }
    }

    with patch('resoftai.websocket.collaboration.sio') as mock_sio:
        mock_sio.leave_room = AsyncMock()
        mock_sio.emit = AsyncMock()

        from resoftai.websocket.collaboration import leave_file_editing

        sid = "test_sid"
        data = {"file_id": 1, "user_id": 100}

        await leave_file_editing(sid, data)

        # Verify user was removed
        assert 1 not in active_editors or 100 not in active_editors.get(1, {})


@pytest.mark.asyncio
async def test_file_content_change():
    """Test file content change broadcasting."""
    from resoftai.websocket.collaboration import file_operations

    file_operations.clear()

    with patch('resoftai.websocket.collaboration.sio') as mock_sio:
        mock_sio.emit = AsyncMock()

        from resoftai.websocket.collaboration import file_content_change

        sid = "test_sid"
        data = {
            "file_id": 1,
            "user_id": 100,
            "changes": [
                {
                    "type": "insert",
                    "position": {"line": 10, "column": 5},
                    "content": "new code"
                }
            ],
            "version": 1
        }

        await file_content_change(sid, data)

        # Verify operation was stored
        assert 1 in file_operations
        assert len(file_operations[1]) > 0

        # Verify broadcast was sent
        mock_sio.emit.assert_called_once()


@pytest.mark.asyncio
async def test_cursor_position_change():
    """Test cursor position change broadcasting."""
    from resoftai.websocket.collaboration import active_editors

    # Setup
    active_editors.clear()
    active_editors[1] = {
        100: {
            "sid": "test_sid",
            "username": "Test User",
            "cursor_position": None,
            "selection": None
        }
    }

    with patch('resoftai.websocket.collaboration.sio') as mock_sio:
        mock_sio.emit = AsyncMock()

        from resoftai.websocket.collaboration import cursor_position_change

        sid = "test_sid"
        data = {
            "file_id": 1,
            "user_id": 100,
            "position": {"line": 10, "column": 5}
        }

        await cursor_position_change(sid, data)

        # Verify cursor was updated
        assert active_editors[1][100]["cursor_position"] == {"line": 10, "column": 5}

        # Verify broadcast was sent
        mock_sio.emit.assert_called_once()


@pytest.mark.asyncio
async def test_get_active_editors():
    """Test getting list of active editors."""
    from resoftai.websocket.collaboration import active_editors, get_active_editors

    active_editors.clear()
    active_editors[1] = {
        100: {
            "sid": "sid1",
            "username": "User1",
            "cursor_position": {"line": 1, "column": 1},
            "selection": None,
            "joined_at": "2025-01-01T00:00:00"
        },
        200: {
            "sid": "sid2",
            "username": "User2",
            "cursor_position": {"line": 2, "column": 2},
            "selection": None,
            "joined_at": "2025-01-01T00:01:00"
        }
    }

    editors = await get_active_editors(1)

    assert len(editors) == 2
    assert any(e["user_id"] == 100 for e in editors)
    assert any(e["user_id"] == 200 for e in editors)


@pytest.mark.asyncio
async def test_file_save_notification():
    """Test file save notification."""
    with patch('resoftai.websocket.collaboration.sio') as mock_sio:
        mock_sio.emit = AsyncMock()

        from resoftai.websocket.collaboration import file_save_notification

        sid = "test_sid"
        data = {
            "file_id": 1,
            "user_id": 100,
            "version": 2,
            "content_hash": "abc123"
        }

        await file_save_notification(sid, data)

        # Verify save notification was broadcasted
        mock_sio.emit.assert_called_once()
        call_args = mock_sio.emit.call_args
        assert call_args[0][0] == "file_saved"
        assert call_args[0][1]["file_id"] == 1
        assert call_args[0][1]["version"] == 2
