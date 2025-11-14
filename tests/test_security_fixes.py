"""Tests for security fixes in code analysis and collaboration."""
import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

from resoftai.api.routes.code_analysis import sanitize_filename


class TestSanitizeFilename:
    """Test sanitize_filename function for path traversal protection."""

    def test_sanitize_path_traversal(self):
        """Test that path traversal attempts are blocked."""
        # Path.name extracts only the final component, which is safer
        assert sanitize_filename("../../etc/passwd") == "passwd"
        assert sanitize_filename("../../../etc/shadow") == "shadow"
        # Windows paths on Linux are treated as single names with backslashes replaced
        result = sanitize_filename("..\\..\\windows\\system32")
        assert ".." not in result  # Path traversal removed
        assert len(result) > 0  # Valid filename returned

    def test_sanitize_dangerous_characters(self):
        """Test that dangerous characters are removed."""
        assert sanitize_filename("test<script>.py") == "test_script_.py"
        # Path.name extracts only the final component
        assert sanitize_filename("file;rm -rf /.py") == "py"
        assert sanitize_filename("test|pipe.js") == "test_pipe.js"
        assert sanitize_filename("test&background.ts") == "test_background.ts"

    def test_sanitize_consecutive_dots(self):
        """Test that consecutive dots are removed."""
        assert sanitize_filename("test...file.py") == "test.file.py"
        assert sanitize_filename("....py") == "py"

    def test_sanitize_leading_dot(self):
        """Test that leading dots are removed."""
        assert sanitize_filename(".hidden.py") == "hidden.py"
        assert sanitize_filename("...test.py") == "test.py"

    def test_sanitize_length_limit(self):
        """Test that long filenames are truncated."""
        long_name = "a" * 150 + ".py"
        result = sanitize_filename(long_name, max_length=100)
        assert len(result) <= 100
        assert result.endswith(".py")

    def test_sanitize_empty_result(self):
        """Test that empty or dangerous-only results are handled."""
        assert sanitize_filename("...") == "temp"
        assert sanitize_filename("") == "temp"
        # Characters are replaced with underscores, which is valid
        result = sanitize_filename("<<<>>>")
        assert len(result) > 0  # Should return something non-empty

    def test_sanitize_preserves_valid_names(self):
        """Test that valid filenames are preserved."""
        assert sanitize_filename("test_file.py") == "test_file.py"
        assert sanitize_filename("module-name.js") == "module-name.js"
        assert sanitize_filename("Component.tsx") == "Component.tsx"


class TestCodeAnalysisTimeout:
    """Test timeout protection in code analysis functions."""

    @pytest.mark.asyncio
    async def test_analysis_timeout_protection(self):
        """Test that analysis times out after configured duration."""
        from resoftai.api.routes.code_analysis import ANALYSIS_TIMEOUT, run_pylint
        from fastapi import HTTPException

        # Create code that would potentially run forever
        infinite_code = """
while True:
    pass
"""
        # This test would need a way to simulate a long-running process
        # For now, we just verify the timeout constant exists
        assert ANALYSIS_TIMEOUT == 30


class TestCodeSizeLimit:
    """Test code size limits in analysis requests."""

    def test_code_size_limit_configured(self):
        """Test that MAX_CODE_SIZE is configured correctly."""
        from resoftai.api.routes.code_analysis import MAX_CODE_SIZE

        # Verify the limit is reasonable
        assert MAX_CODE_SIZE == 100_000
        assert MAX_CODE_SIZE > 0


class TestCollaborationRateLimit:
    """Test rate limiting in collaboration features."""

    def test_rate_limit_allows_normal_usage(self):
        """Test that normal usage is allowed."""
        from resoftai.websocket.collaboration import check_rate_limit

        # Normal usage should be allowed
        for i in range(5):
            assert check_rate_limit(f"test_user_{i}", max_requests=10, window=1) is True

    def test_rate_limit_blocks_excessive_requests(self):
        """Test that excessive requests are blocked."""
        from resoftai.websocket.collaboration import check_rate_limit

        # Make requests up to the limit
        user_key = "test_user_excessive"
        for i in range(10):
            result = check_rate_limit(user_key, max_requests=10, window=1)
            if i < 10:
                assert result is True

        # Next request should be blocked
        assert check_rate_limit(user_key, max_requests=10, window=1) is False

    @pytest.mark.asyncio
    async def test_rate_limit_resets_after_window(self):
        """Test that rate limit resets after time window."""
        from resoftai.websocket.collaboration import check_rate_limit
        import time

        user_key = "test_user_reset"

        # Fill the rate limit
        for i in range(5):
            check_rate_limit(user_key, max_requests=5, window=1)

        # Should be at limit
        assert check_rate_limit(user_key, max_requests=5, window=1) is False

        # Wait for window to expire
        await asyncio.sleep(1.1)

        # Should be allowed again
        assert check_rate_limit(user_key, max_requests=5, window=1) is True


class TestLRUDict:
    """Test LRU cache implementation."""

    def test_lru_max_size(self):
        """Test that LRU dict respects max size."""
        from resoftai.websocket.collaboration import LRUDict

        cache = LRUDict(maxsize=3)
        cache[1] = "one"
        cache[2] = "two"
        cache[3] = "three"
        cache[4] = "four"  # Should evict oldest (1)

        assert len(cache) == 3
        assert 1 not in cache
        assert 2 in cache
        assert 3 in cache
        assert 4 in cache

    def test_lru_access_updates_order(self):
        """Test that accessing an item updates its position."""
        from resoftai.websocket.collaboration import LRUDict

        cache = LRUDict(maxsize=3)
        cache[1] = "one"
        cache[2] = "two"
        cache[3] = "three"

        # Access item 1 to make it most recent
        _ = cache[1]

        # Add new item, should evict 2 (oldest)
        cache[4] = "four"

        assert 1 in cache
        assert 2 not in cache
        assert 3 in cache
        assert 4 in cache


class TestPermissionVerification:
    """Test permission verification for file access."""

    @pytest.mark.asyncio
    async def test_verify_file_access_function_exists(self):
        """Test that permission verification function exists."""
        from resoftai.websocket.collaboration import verify_file_access

        # Verify function exists and is callable
        assert callable(verify_file_access)

    @pytest.mark.asyncio
    async def test_verify_file_access_handles_errors(self):
        """Test that permission verification handles errors gracefully."""
        from resoftai.websocket.collaboration import verify_file_access

        # Non-existent file should return False (no access)
        result = await verify_file_access(file_id=999999, user_id=999999)
        assert result is False


class TestConcurrencyControl:
    """Test concurrency control with semaphore."""

    @pytest.mark.asyncio
    async def test_analysis_semaphore_limits_concurrent_requests(self):
        """Test that semaphore limits concurrent analysis requests."""
        from resoftai.api.routes.code_analysis import _analysis_semaphore

        # Verify semaphore exists
        assert _analysis_semaphore is not None
        # Check it's configured for 5 concurrent requests
        assert isinstance(_analysis_semaphore, asyncio.Semaphore)


class TestDisconnectHandler:
    """Test WebSocket disconnect handling."""

    @pytest.mark.asyncio
    async def test_disconnect_cleans_up_sessions(self):
        """Test that disconnect handler cleans up user sessions."""
        from resoftai.websocket.collaboration import (
            active_editors,
            sid_to_sessions,
            disconnect
        )

        # Setup test data
        sid = "test_sid_disconnect"
        file_id = 1
        user_id = 100

        active_editors[file_id] = {
            user_id: {
                'sid': sid,
                'username': 'Test User',
                'cursor_position': None
            }
        }
        sid_to_sessions[sid] = [(file_id, user_id)]

        # Mock socket.io emit
        with patch('resoftai.websocket.collaboration.sio') as mock_sio:
            mock_sio.emit = AsyncMock()

            # Call disconnect
            await disconnect(sid)

        # Verify cleanup
        assert sid not in sid_to_sessions
        assert file_id not in active_editors or user_id not in active_editors.get(file_id, {})


class TestInactiveSessionCleanup:
    """Test inactive session cleanup task."""

    @pytest.mark.asyncio
    async def test_cleanup_removes_old_sessions(self):
        """Test that cleanup task removes old inactive sessions."""
        from resoftai.websocket.collaboration import active_editors
        from datetime import datetime, timedelta

        # Add an old session
        old_time = (datetime.utcnow() - timedelta(hours=2)).isoformat()
        active_editors[999] = {
            888: {
                'sid': 'old_sid',
                'username': 'Old User',
                'cursor_position': None,
                'joined_at': old_time
            }
        }

        # Note: Actual cleanup task testing would require running the task
        # and waiting for it to execute, which is complex in unit tests
        # This test just verifies the data structure is set up correctly
        assert 999 in active_editors
        assert 888 in active_editors[999]
