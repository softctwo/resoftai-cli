"""WebSocket connection manager."""
import socketio
import logging
from typing import Dict, Set, Any

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

        logger.info(f"Client {sid} connected to project {project_id}")

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

        logger.info(f"Client {sid} disconnected")

    async def broadcast_to_project(self, project_id: int, event: str, data: Any):
        """
        Broadcast message to all clients in a project room.

        Args:
            project_id: Project ID
            event: Event name
            data: Event data
        """
        room = f"project:{project_id}"
        await sio.emit(event, data, room=room)
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
