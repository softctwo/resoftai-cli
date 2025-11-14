"""WebSocket connection manager."""
import socketio
import logging
from typing import Dict, Set, Any
from resoftai.utils.performance import (
    timing_decorator,
    websocket_metrics,
    performance_monitor,
    message_batcher
)

logger = logging.getLogger(__name__)

# Create Socket.IO server
sio = socketio.AsyncServer(
    async_mode='asgi',
    cors_allowed_origins='*',  # Configure properly in production
    logger=False,
    engineio_logger=False
)


class ConnectionManager:
    """Manages WebSocket connections and rooms."""

    def __init__(self):
        """Initialize connection manager."""
        self.active_connections: Dict[str, Set[str]] = {}  # project_id -> set of session_ids
        self.user_connections: Dict[int, Set[str]] = {}  # user_id -> set of session_ids
        self.file_sessions: Dict[int, Dict[str, Any]] = {}  # file_id -> {sid: user_info}
        self.session_user_info: Dict[str, Dict[str, Any]] = {}  # sid -> {user_id, username}
        self.file_versions: Dict[int, int] = {}  # file_id -> current_version

    @timing_decorator("manager.connect")
    async def connect(self, sid: str, project_id: str, user_id: int = None):
        """
        Add connection to project room.

        Args:
            sid: Session ID
            project_id: Project ID to join
            user_id: Optional user ID
        """
        # Add to project room
        if project_id not in self.active_connections:
            self.active_connections[project_id] = set()
        self.active_connections[project_id].add(sid)
        await sio.enter_room(sid, f"project:{project_id}")

        # Add to user tracking
        if user_id:
            if user_id not in self.user_connections:
                self.user_connections[user_id] = set()
            self.user_connections[user_id].add(sid)

        # Track metrics
        websocket_metrics.connection_opened()

        logger.info(f"Client {sid} connected to project {project_id}")

    @timing_decorator("manager.disconnect")
    async def disconnect(self, sid: str):
        """
        Remove connection from all rooms.

        Args:
            sid: Session ID
        """
        # Remove from project rooms
        for project_id, sids in list(self.active_connections.items()):
            if sid in sids:
                sids.remove(sid)
                await sio.leave_room(sid, f"project:{project_id}")
                if not sids:
                    del self.active_connections[project_id]

        # Remove from user tracking
        for user_id, sids in list(self.user_connections.items()):
            if sid in sids:
                sids.remove(sid)
                if not sids:
                    del self.user_connections[user_id]

        # Track metrics
        websocket_metrics.connection_closed()

        logger.info(f"Client {sid} disconnected")

    @timing_decorator("manager.broadcast_to_project")
    async def broadcast_to_project(self, project_id: int, event: str, data: Any):
        """
        Broadcast message to all clients in a project room.

        Args:
            project_id: Project ID
            event: Event name
            data: Event data
        """
        import json
        room = f"project:{project_id}"
        await sio.emit(event, data, room=room)

        # Track message metrics
        message_size = len(json.dumps(data).encode('utf-8'))
        websocket_metrics.message_sent(message_size)

        logger.debug(f"Broadcasted {event} to project {project_id}")

    async def broadcast_to_user(self, user_id: int, event: str, data: Any):
        """
        Broadcast message to all sessions of a specific user.

        Args:
            user_id: User ID
            event: Event name
            data: Event data
        """
        if user_id in self.user_connections:
            for sid in self.user_connections[user_id]:
                await sio.emit(event, data, room=sid)
            logger.debug(f"Broadcasted {event} to user {user_id}")

    async def send_to_client(self, sid: str, event: str, data: Any):
        """
        Send message to a specific client.

        Args:
            sid: Session ID
            event: Event name
            data: Event data
        """
        await sio.emit(event, data, room=sid)

    def get_project_connection_count(self, project_id: str) -> int:
        """Get number of connections for a project."""
        return len(self.active_connections.get(project_id, set()))

    def get_user_connection_count(self, user_id: int) -> int:
        """Get number of connections for a user."""
        return len(self.user_connections.get(user_id, set()))

    async def join_file(self, sid: str, file_id: int, project_id: int, user_id: int, username: str):
        """
        Add user to file editing session.

        Args:
            sid: Session ID
            file_id: File ID
            project_id: Project ID
            user_id: User ID
            username: Username
        """
        if file_id not in self.file_sessions:
            self.file_sessions[file_id] = {}
            self.file_versions[file_id] = 0

        self.file_sessions[file_id][sid] = {
            'user_id': user_id,
            'username': username,
            'project_id': project_id
        }

        self.session_user_info[sid] = {
            'user_id': user_id,
            'username': username,
            'file_id': file_id,
            'project_id': project_id
        }

        await sio.enter_room(sid, f"file:{file_id}")
        logger.info(f"User {username} (sid: {sid}) joined file {file_id}")

    async def leave_file(self, sid: str, file_id: int):
        """
        Remove user from file editing session.

        Args:
            sid: Session ID
            file_id: File ID
        """
        if file_id in self.file_sessions and sid in self.file_sessions[file_id]:
            del self.file_sessions[file_id][sid]
            if not self.file_sessions[file_id]:
                del self.file_sessions[file_id]
                if file_id in self.file_versions:
                    del self.file_versions[file_id]

        if sid in self.session_user_info:
            del self.session_user_info[sid]

        await sio.leave_room(sid, f"file:{file_id}")
        logger.info(f"Client {sid} left file {file_id}")

    def get_file_active_users(self, file_id: int) -> list:
        """Get list of active users editing a file."""
        if file_id not in self.file_sessions:
            return []

        return [
            {
                'user_id': info['user_id'],
                'username': info['username']
            }
            for info in self.file_sessions[file_id].values()
        ]

    def increment_file_version(self, file_id: int) -> int:
        """Increment and return file version."""
        if file_id not in self.file_versions:
            self.file_versions[file_id] = 0
        self.file_versions[file_id] += 1
        return self.file_versions[file_id]

    def get_file_version(self, file_id: int) -> int:
        """Get current file version."""
        return self.file_versions.get(file_id, 0)

    @timing_decorator("manager.broadcast_to_file")
    async def broadcast_to_file(self, file_id: int, event: str, data: Any, exclude_sid: str = None):
        """
        Broadcast message to all users editing a file.

        Args:
            file_id: File ID
            event: Event name
            data: Event data
            exclude_sid: Optional session ID to exclude from broadcast
        """
        import json
        room = f"file:{file_id}"
        message_size = len(json.dumps(data).encode('utf-8'))

        if exclude_sid:
            # Send to all in room except the sender
            if file_id in self.file_sessions:
                for sid in self.file_sessions[file_id].keys():
                    if sid != exclude_sid:
                        await sio.emit(event, data, room=sid)
                        websocket_metrics.message_sent(message_size)
        else:
            await sio.emit(event, data, room=room)
            websocket_metrics.message_sent(message_size)

        logger.debug(f"Broadcasted {event} to file {file_id}")


# Global connection manager instance
manager = ConnectionManager()


# Socket.IO Event Handlers
@sio.event
async def connect(sid, environ):
    """Handle client connection."""
    logger.info(f"Client connected: {sid}")
    await sio.emit('connected', {'sid': sid}, room=sid)


@sio.event
async def disconnect(sid):
    """Handle client disconnection."""
    logger.info(f"Client disconnected: {sid}")
    await manager.disconnect(sid)


@sio.event
async def join_project(sid, data):
    """
    Handle join project room request.

    Expected data:
        {
            "project_id": "123",
            "user_id": 456  # optional
        }
    """
    project_id = str(data.get('project_id'))
    user_id = data.get('user_id')

    if not project_id:
        await sio.emit('error', {'message': 'project_id is required'}, room=sid)
        return

    await manager.connect(sid, project_id, user_id)
    await sio.emit('joined', {
        'project_id': project_id,
        'message': f'Successfully joined project {project_id}'
    }, room=sid)


@sio.event
async def leave_project(sid, data):
    """
    Handle leave project room request.

    Expected data:
        {
            "project_id": "123"
        }
    """
    project_id = str(data.get('project_id'))

    if not project_id:
        await sio.emit('error', {'message': 'project_id is required'}, room=sid)
        return

    await sio.leave_room(sid, f"project:{project_id}")
    await sio.emit('left', {
        'project_id': project_id,
        'message': f'Left project {project_id}'
    }, room=sid)


@sio.event
async def ping(sid, data):
    """Handle ping for keepalive."""
    await sio.emit('pong', data, room=sid)


@sio.event
async def join_file_session(sid, data):
    """
    Handle join file editing session request.

    Expected data:
        {
            "file_id": 123,
            "project_id": 456,
            "user_id": 789,
            "username": "John Doe"
        }
    """
    file_id = data.get('file_id')
    project_id = data.get('project_id')
    user_id = data.get('user_id')
    username = data.get('username')

    if not all([file_id, project_id, user_id, username]):
        await sio.emit('error', {
            'message': 'file_id, project_id, user_id, and username are required'
        }, room=sid)
        return

    await manager.join_file(sid, file_id, project_id, user_id, username)

    # Get active users after joining
    active_users = manager.get_file_active_users(file_id)

    # Notify the user who joined
    await sio.emit('file.joined', {
        'file_id': file_id,
        'active_users': active_users,
        'version': manager.get_file_version(file_id)
    }, room=sid)

    # Notify other users in the file
    from resoftai.websocket.events import FileJoinEvent
    event = FileJoinEvent(
        file_id=file_id,
        project_id=project_id,
        user_id=user_id,
        username=username,
        active_users=active_users
    )
    await manager.broadcast_to_file(file_id, "file.join", event.dict(), exclude_sid=sid)


@sio.event
async def leave_file_session(sid, data):
    """
    Handle leave file editing session request.

    Expected data:
        {
            "file_id": 123
        }
    """
    file_id = data.get('file_id')

    if not file_id:
        await sio.emit('error', {'message': 'file_id is required'}, room=sid)
        return

    # Get user info before leaving
    user_info = manager.session_user_info.get(sid)
    if not user_info:
        return

    await manager.leave_file(sid, file_id)

    # Get remaining active users
    active_users = manager.get_file_active_users(file_id)

    # Notify other users
    from resoftai.websocket.events import FileLeaveEvent
    event = FileLeaveEvent(
        file_id=file_id,
        project_id=user_info['project_id'],
        user_id=user_info['user_id'],
        username=user_info['username'],
        active_users=active_users
    )
    await manager.broadcast_to_file(file_id, "file.leave", event.dict())


@sio.event
async def file_edit(sid, data):
    """
    Handle file content edit event.

    Expected data:
        {
            "file_id": 123,
            "changes": {...},  # Monaco editor change object
        }
    """
    file_id = data.get('file_id')
    changes = data.get('changes')

    if not file_id or not changes:
        await sio.emit('error', {'message': 'file_id and changes are required'}, room=sid)
        return

    # Get user info
    user_info = manager.session_user_info.get(sid)
    if not user_info:
        await sio.emit('error', {'message': 'Not in a file session'}, room=sid)
        return

    # Increment version
    version = manager.increment_file_version(file_id)

    # Broadcast edit to other users
    from resoftai.websocket.events import FileEditEvent
    event = FileEditEvent(
        file_id=file_id,
        project_id=user_info['project_id'],
        user_id=user_info['user_id'],
        username=user_info['username'],
        changes=changes,
        version=version
    )
    await manager.broadcast_to_file(file_id, "file.edit", event.dict(), exclude_sid=sid)


@sio.event
async def cursor_position(sid, data):
    """
    Handle cursor position update.

    Expected data:
        {
            "file_id": 123,
            "position": {"lineNumber": 10, "column": 5},
            "selection": {...}  # optional
        }
    """
    file_id = data.get('file_id')
    position = data.get('position')

    if not file_id or not position:
        await sio.emit('error', {'message': 'file_id and position are required'}, room=sid)
        return

    # Get user info
    user_info = manager.session_user_info.get(sid)
    if not user_info:
        return

    # Broadcast cursor position to other users
    from resoftai.websocket.events import CursorPositionEvent
    event = CursorPositionEvent(
        file_id=file_id,
        project_id=user_info['project_id'],
        user_id=user_info['user_id'],
        username=user_info['username'],
        position=position,
        selection=data.get('selection')
    )
    await manager.broadcast_to_file(file_id, "cursor.position", event.dict(), exclude_sid=sid)


# Helper functions for emitting events
async def emit_project_progress(project_id: int, percentage: int, stage: str, message: str):
    """Emit project progress event."""
    from resoftai.websocket.events import ProjectProgressEvent

    event = ProjectProgressEvent(
        project_id=project_id,
        percentage=percentage,
        stage=stage,
        message=message
    )
    await manager.broadcast_to_project(project_id, "project.progress", event.dict())


async def emit_agent_status(
    project_id: int,
    agent_role: str,
    status: str,
    current_task: str = None,
    tokens_used: int = 0
):
    """Emit agent status event."""
    from resoftai.websocket.events import AgentStatusEvent

    event = AgentStatusEvent(
        project_id=project_id,
        agent_role=agent_role,
        status=status,
        current_task=current_task,
        tokens_used=tokens_used
    )
    await manager.broadcast_to_project(project_id, "agent.status", event.dict())


async def emit_log(project_id: int, level: str, message: str, source: str = None):
    """Emit log event."""
    from resoftai.websocket.events import LogEvent

    event = LogEvent(
        project_id=project_id,
        level=level,
        message=message,
        source=source
    )
    await manager.broadcast_to_project(project_id, "log.new", event.dict())


async def emit_task_complete(
    project_id: int,
    task_id: int,
    stage: str,
    status: str,
    result: str = None
):
    """Emit task complete event."""
    from resoftai.websocket.events import TaskCompleteEvent

    event = TaskCompleteEvent(
        project_id=project_id,
        task_id=task_id,
        stage=stage,
        status=status,
        result=result
    )
    await manager.broadcast_to_project(project_id, "task.complete", event.dict())


async def emit_project_status(project_id: int, status: str, message: str = None):
    """Emit project status change event."""
    from resoftai.websocket.events import ProjectStatusEvent

    event = ProjectStatusEvent(
        project_id=project_id,
        status=status,
        message=message
    )
    await manager.broadcast_to_project(project_id, "project.status", event.dict())
