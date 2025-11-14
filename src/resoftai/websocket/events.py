"""WebSocket event types and utilities."""
from typing import Dict, Any, Literal
from datetime import datetime
from pydantic import BaseModel


class WebSocketEvent(BaseModel):
    """Base WebSocket event model."""
    type: str
    timestamp: str = None

    def __init__(self, **data):
        if "timestamp" not in data:
            data["timestamp"] = datetime.utcnow().isoformat()
        super().__init__(**data)


class ProjectProgressEvent(WebSocketEvent):
    """Project progress update event."""
    type: Literal["project.progress"] = "project.progress"
    project_id: int
    percentage: int
    stage: str
    message: str


class AgentStatusEvent(WebSocketEvent):
    """Agent status update event."""
    type: Literal["agent.status"] = "agent.status"
    project_id: int
    agent_role: str
    status: str
    current_task: str = None
    tokens_used: int = 0


class LogEvent(WebSocketEvent):
    """New log event."""
    type: Literal["log.new"] = "log.new"
    project_id: int
    level: str
    message: str
    source: str = None


class TaskCompleteEvent(WebSocketEvent):
    """Task completion event."""
    type: Literal["task.complete"] = "task.complete"
    project_id: int
    task_id: int
    stage: str
    status: str
    result: str = None


class ProjectStatusEvent(WebSocketEvent):
    """Project status change event."""
    type: Literal["project.status"] = "project.status"
    project_id: int
    status: str
    message: str = None


class DashboardUpdateEvent(WebSocketEvent):
    """Dashboard data update event."""
    type: Literal["dashboard.update"] = "dashboard.update"
    data: Dict[str, Any]


class FileEditEvent(WebSocketEvent):
    """File content edit event for collaborative editing."""
    type: Literal["file.edit"] = "file.edit"
    file_id: int
    project_id: int
    user_id: int
    username: str
    changes: Dict[str, Any]  # Monaco editor change object
    version: int  # Document version for conflict resolution


class CursorPositionEvent(WebSocketEvent):
    """Cursor position update event for collaborative editing."""
    type: Literal["cursor.position"] = "cursor.position"
    file_id: int
    project_id: int
    user_id: int
    username: str
    position: Dict[str, int]  # {lineNumber: int, column: int}
    selection: Dict[str, Any] = None  # Selection range if any


class UserOnlineEvent(WebSocketEvent):
    """User online status event."""
    type: Literal["user.online"] = "user.online"
    user_id: int
    username: str
    project_id: int
    file_id: int = None  # Specific file being edited


class UserOfflineEvent(WebSocketEvent):
    """User offline status event."""
    type: Literal["user.offline"] = "user.offline"
    user_id: int
    username: str
    project_id: int
    file_id: int = None


class FileJoinEvent(WebSocketEvent):
    """User joined file editing session."""
    type: Literal["file.join"] = "file.join"
    file_id: int
    project_id: int
    user_id: int
    username: str
    active_users: list  # List of currently active users in this file


class FileLeaveEvent(WebSocketEvent):
    """User left file editing session."""
    type: Literal["file.leave"] = "file.leave"
    file_id: int
    project_id: int
    user_id: int
    username: str
    active_users: list  # Remaining active users


# Event type mapping for serialization
EVENT_TYPE_MAP = {
    "project.progress": ProjectProgressEvent,
    "agent.status": AgentStatusEvent,
    "log.new": LogEvent,
    "task.complete": TaskCompleteEvent,
    "project.status": ProjectStatusEvent,
    "dashboard.update": DashboardUpdateEvent,
    "file.edit": FileEditEvent,
    "cursor.position": CursorPositionEvent,
    "user.online": UserOnlineEvent,
    "user.offline": UserOfflineEvent,
    "file.join": FileJoinEvent,
    "file.leave": FileLeaveEvent,
}
