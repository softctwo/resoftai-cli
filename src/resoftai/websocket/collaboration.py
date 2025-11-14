"""Real-time collaboration features for code editing."""
import asyncio
import logging
from typing import Dict, List, Any
from datetime import datetime, timedelta
from collections import OrderedDict, defaultdict
from time import time

from resoftai.websocket.manager import sio, manager

logger = logging.getLogger(__name__)


class LRUDict(OrderedDict):
    """
    LRU (Least Recently Used) cache with max size.
    Automatically removes oldest items when max size is exceeded.
    """
    def __init__(self, maxsize=1000):
        self.maxsize = maxsize
        super().__init__()

    def __setitem__(self, key, value):
        if key in self:
            # Move to end
            del self[key]
        super().__setitem__(key, value)
        if len(self) > self.maxsize:
            # Remove oldest
            self.popitem(last=False)

    def __getitem__(self, key):
        # Move to end on access
        value = super().__getitem__(key)
        del self[key]
        super().__setitem__(key, value)
        return value


async def verify_file_access(file_id: int, user_id: int) -> bool:
    """
    Verify if user has access to the file.

    Args:
        file_id: File ID to check
        user_id: User ID requesting access

    Returns:
        True if access granted, False otherwise
    """
    try:
        from resoftai.db import get_async_session
        from resoftai.crud.file import get_file
        from resoftai.crud.project import get_project_by_id

        async for db in get_async_session():
            # Get file
            file = await get_file(db, file_id)
            if not file:
                return False

            # Get project
            project = await get_project_by_id(db, file.project_id)
            if not project:
                return False

            # Check ownership
            if project.user_id == user_id:
                return True

            # TODO: Check collaborator permissions from project members table
            # For now, only owner has access
            return False

    except Exception as e:
        logger.error(f"Error verifying file access: {e}")
        return False


# Rate limit tracking
_rate_limits: Dict[str, List[float]] = defaultdict(list)


def check_rate_limit(
    key: str,
    max_requests: int = 10,
    window: int = 1
) -> bool:
    """
    Check if request exceeds rate limit.

    Args:
        key: Identifier (e.g., user_id or sid)
        max_requests: Maximum requests allowed
        window: Time window in seconds

    Returns:
        True if within limit, False if exceeded
    """
    now = time()

    # Clean old timestamps
    _rate_limits[key] = [
        t for t in _rate_limits[key]
        if now - t < window
    ]

    # Check limit
    if len(_rate_limits[key]) >= max_requests:
        return False

    # Record request
    _rate_limits[key].append(now)
    return True


# Track active editors per file using LRU cache
# Structure: {file_id: {user_id: {sid, cursor_position, selection}}}
active_editors = LRUDict(maxsize=1000)  # Max 1000 active files

# Track file change operations (Operational Transformation-like)
file_operations = LRUDict(maxsize=500)  # Max 500 file histories

# Session tracking for fast cleanup
sid_to_sessions: Dict[str, List[tuple]] = {}


@sio.event
async def join_file_editing(sid, data):
    """
    Join a file editing session with permission check.

    Expected data:
        {
            "file_id": 123,
            "user_id": 456,
            "project_id": 789,
            "username": "John Doe"
        }
    """
    file_id = data.get('file_id')
    user_id = data.get('user_id')
    project_id = data.get('project_id')
    username = data.get('username', f'User {user_id}')

    if not file_id or not user_id:
        await sio.emit('error', {
            'message': 'Missing file_id or user_id'
        }, room=sid)
        return

    # SECURITY: Verify access permission
    has_access = await verify_file_access(file_id, user_id)
    if not has_access:
        await sio.emit('error', {
            'message': 'Permission denied - you do not have access to this file'
        }, room=sid)
        logger.warning(f"User {user_id} attempted unauthorized access to file {file_id}")
        return

    # Track active editor
    if file_id not in active_editors:
        active_editors[file_id] = {}

    active_editors[file_id][user_id] = {
        'sid': sid,
        'username': username,
        'cursor_position': None,
        'selection': None,
        'joined_at': datetime.utcnow().isoformat()
    }

    # Track session for fast cleanup on disconnect
    if sid not in sid_to_sessions:
        sid_to_sessions[sid] = []
    sid_to_sessions[sid].append((file_id, user_id))

    # Join file room
    room = f"file:{file_id}"
    await sio.enter_room(sid, room)

    # Notify other editors
    await sio.emit('user_joined_file', {
        'file_id': file_id,
        'user_id': user_id,
        'username': username,
        'active_users': len(active_editors[file_id])
    }, room=room, skip_sid=sid)

    # Send current active users to the new joiner
    await sio.emit('file_editors_list', {
        'file_id': file_id,
        'editors': [
            {
                'user_id': uid,
                'username': info['username'],
                'cursor_position': info.get('cursor_position'),
                'selection': info.get('selection')
            }
            for uid, info in active_editors[file_id].items()
            if uid != user_id
        ]
    }, room=sid)

    logger.info(f"User {user_id} joined file {file_id} editing")


@sio.event
async def leave_file_editing(sid, data):
    """
    Leave a file editing session.

    Expected data:
        {
            "file_id": 123,
            "user_id": 456
        }
    """
    file_id = data.get('file_id')
    user_id = data.get('user_id')

    if not file_id or not user_id:
        return

    # Remove from active editors
    if file_id in active_editors and user_id in active_editors[file_id]:
        username = active_editors[file_id][user_id].get('username', 'Unknown')
        del active_editors[file_id][user_id]

        # Clean up empty file entries
        if not active_editors[file_id]:
            del active_editors[file_id]

        # Leave room
        room = f"file:{file_id}"
        await sio.leave_room(sid, room)

        # Notify other editors
        await sio.emit('user_left_file', {
            'file_id': file_id,
            'user_id': user_id,
            'username': username,
            'active_users': len(active_editors.get(file_id, {}))
        }, room=room)

        logger.info(f"User {user_id} left file {file_id} editing")


@sio.event
async def file_content_change(sid, data):
    """
    Handle file content changes and broadcast to other editors with rate limiting.

    Expected data:
        {
            "file_id": 123,
            "user_id": 456,
            "changes": [
                {
                    "type": "insert" | "delete" | "replace",
                    "position": {"line": 10, "column": 5},
                    "content": "new text",
                    "length": 8  # for delete operations
                }
            ],
            "version": 42  # file version for conflict resolution
        }
    """
    # Rate limit: 10 changes per second
    if not check_rate_limit(sid, max_requests=10, window=1):
        await sio.emit('error', {
            'message': 'Rate limit exceeded - too many requests'
        }, room=sid)
        return

    file_id = data.get('file_id')
    user_id = data.get('user_id')
    changes = data.get('changes', [])
    version = data.get('version', 0)

    if not file_id or not user_id:
        return

    # Store operation for potential conflict resolution
    if file_id not in file_operations:
        file_operations[file_id] = []

    operation = {
        'user_id': user_id,
        'changes': changes,
        'version': version,
        'timestamp': datetime.utcnow().isoformat()
    }
    file_operations[file_id].append(operation)

    # Keep only last 100 operations per file
    if len(file_operations[file_id]) > 100:
        file_operations[file_id] = file_operations[file_id][-100:]

    # Broadcast changes to other editors in the same file
    room = f"file:{file_id}"
    await sio.emit('file_content_changed', {
        'file_id': file_id,
        'user_id': user_id,
        'changes': changes,
        'version': version,
        'timestamp': operation['timestamp']
    }, room=room, skip_sid=sid)

    logger.debug(f"File {file_id} content changed by user {user_id}")


@sio.event
async def cursor_position_change(sid, data):
    """
    Update cursor position for an editor with rate limiting.

    Expected data:
        {
            "file_id": 123,
            "user_id": 456,
            "position": {"line": 10, "column": 5},
            "selection": {
                "start": {"line": 10, "column": 5},
                "end": {"line": 10, "column": 15}
            }  # optional
        }
    """
    # Rate limit: 30 requests per second
    if not check_rate_limit(sid, max_requests=30, window=1):
        # Silently drop - too many cursor updates
        return

    file_id = data.get('file_id')
    user_id = data.get('user_id')
    position = data.get('position')
    selection = data.get('selection')

    if not file_id or not user_id or not position:
        return

    # Update cursor position
    if file_id in active_editors and user_id in active_editors[file_id]:
        active_editors[file_id][user_id]['cursor_position'] = position
        active_editors[file_id][user_id]['selection'] = selection

        # Broadcast cursor position to other editors
        room = f"file:{file_id}"
        await sio.emit('cursor_position_changed', {
            'file_id': file_id,
            'user_id': user_id,
            'username': active_editors[file_id][user_id].get('username'),
            'position': position,
            'selection': selection
        }, room=room, skip_sid=sid)


@sio.event
async def file_save_notification(sid, data):
    """
    Notify all editors that file has been saved.

    Expected data:
        {
            "file_id": 123,
            "user_id": 456,
            "version": 43,
            "content_hash": "abc123..."  # optional
        }
    """
    file_id = data.get('file_id')
    user_id = data.get('user_id')
    version = data.get('version')
    content_hash = data.get('content_hash')

    if not file_id or not user_id:
        return

    room = f"file:{file_id}"
    await sio.emit('file_saved', {
        'file_id': file_id,
        'user_id': user_id,
        'version': version,
        'content_hash': content_hash,
        'timestamp': datetime.utcnow().isoformat()
    }, room=room)

    logger.info(f"File {file_id} saved by user {user_id}, version {version}")


@sio.event
async def request_file_lock(sid, data):
    """
    Request exclusive lock on a file (for operations that need atomicity).

    Expected data:
        {
            "file_id": 123,
            "user_id": 456,
            "duration": 30  # seconds
        }
    """
    file_id = data.get('file_id')
    user_id = data.get('user_id')
    duration = data.get('duration', 30)

    # Simple lock implementation (can be enhanced with Redis for production)
    # For now, just broadcast the lock request
    room = f"file:{file_id}"
    await sio.emit('file_lock_requested', {
        'file_id': file_id,
        'user_id': user_id,
        'duration': duration
    }, room=room, skip_sid=sid)


@sio.event
async def release_file_lock(sid, data):
    """
    Release file lock.

    Expected data:
        {
            "file_id": 123,
            "user_id": 456
        }
    """
    file_id = data.get('file_id')
    user_id = data.get('user_id')

    room = f"file:{file_id}"
    await sio.emit('file_lock_released', {
        'file_id': file_id,
        'user_id': user_id
    }, room=room, skip_sid=sid)


async def get_active_editors(file_id: int) -> List[Dict[str, Any]]:
    """Get list of active editors for a file."""
    if file_id not in active_editors:
        return []

    return [
        {
            'user_id': user_id,
            'username': info['username'],
            'cursor_position': info.get('cursor_position'),
            'selection': info.get('selection'),
            'joined_at': info.get('joined_at')
        }
        for user_id, info in active_editors[file_id].items()
    ]


async def get_file_operations(file_id: int, since_version: int = None) -> List[Dict[str, Any]]:
    """
    Get file operations, optionally since a specific version.

    Useful for syncing clients that temporarily disconnected.
    """
    if file_id not in file_operations:
        return []

    operations = file_operations[file_id]

    if since_version is not None:
        operations = [op for op in operations if op['version'] > since_version]

    return operations


async def cleanup_inactive_sessions():
    """
    Background task to clean up inactive editing sessions.

    Runs every hour to remove sessions inactive for > 1 hour.
    """
    while True:
        try:
            await asyncio.sleep(3600)  # Every hour

            now = datetime.utcnow()
            cleaned_files = 0
            cleaned_users = 0

            for file_id in list(active_editors.keys()):
                for user_id in list(active_editors[file_id].keys()):
                    try:
                        joined_at_str = active_editors[file_id][user_id].get('joined_at')
                        if not joined_at_str:
                            continue

                        joined_at = datetime.fromisoformat(joined_at_str)
                        inactive_duration = now - joined_at

                        # Clean up if inactive for > 1 hour
                        if inactive_duration > timedelta(hours=1):
                            del active_editors[file_id][user_id]
                            cleaned_users += 1

                    except Exception as e:
                        logger.warning(f"Error cleaning user session: {e}")
                        continue

                # Clean empty file entries
                if file_id in active_editors and not active_editors[file_id]:
                    del active_editors[file_id]
                    cleaned_files += 1

            if cleaned_files > 0 or cleaned_users > 0:
                logger.info(
                    f"Cleaned up {cleaned_users} inactive users from {cleaned_files} files"
                )

        except Exception as e:
            logger.error(f"Error in cleanup task: {e}", exc_info=True)


@sio.event
async def disconnect(sid):
    """
    Handle client disconnection with optimized cleanup.
    """
    logger.info(f"Client disconnected: {sid}")

    # Fast lookup using sid_to_sessions
    if sid in sid_to_sessions:
        for file_id, user_id in sid_to_sessions[sid]:
            try:
                if file_id in active_editors and user_id in active_editors[file_id]:
                    username = active_editors[file_id][user_id].get('username', 'Unknown')
                    del active_editors[file_id][user_id]

                    # Clean empty file entries
                    if not active_editors[file_id]:
                        del active_editors[file_id]

                    # Notify other users
                    room = f"file:{file_id}"
                    await sio.emit('user_left_file', {
                        'file_id': file_id,
                        'user_id': user_id,
                        'username': username,
                        'active_users': len(active_editors.get(file_id, {}))
                    }, room=room)

            except Exception as e:
                logger.warning(f"Error cleaning session for file {file_id}: {e}")

        del sid_to_sessions[sid]


# Start cleanup task
try:
    cleanup_task = asyncio.create_task(cleanup_inactive_sessions())
    logger.info("Started inactive session cleanup task")
except Exception as e:
    logger.warning(f"Could not start cleanup task: {e}")
