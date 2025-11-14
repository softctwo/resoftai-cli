"""Real-time collaboration features for code editing."""
import logging
from typing import Dict, List, Any
from datetime import datetime
import json

from resoftai.websocket.manager import sio, manager

logger = logging.getLogger(__name__)

# Track active editors per file
# Structure: {file_id: {user_id: {sid, cursor_position, selection}}}
active_editors: Dict[int, Dict[int, Dict[str, Any]]] = {}

# Track file change operations (Operational Transformation-like)
file_operations: Dict[int, List[Dict[str, Any]]] = {}


@sio.event
async def join_file_editing(sid, data):
    """
    Join a file editing session.

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
    Handle file content changes and broadcast to other editors.

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
    Update cursor position for an editor.

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
