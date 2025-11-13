"""WebSocket module for real-time communication."""
from resoftai.websocket.manager import (
    sio,
    manager,
    emit_project_progress,
    emit_agent_status,
    emit_log,
    emit_task_complete,
    emit_project_status,
)
from resoftai.websocket.events import (
    WebSocketEvent,
    ProjectProgressEvent,
    AgentStatusEvent,
    LogEvent,
    TaskCompleteEvent,
    ProjectStatusEvent,
    DashboardUpdateEvent,
)

__all__ = [
    "sio",
    "manager",
    "emit_project_progress",
    "emit_agent_status",
    "emit_log",
    "emit_task_complete",
    "emit_project_status",
    "WebSocketEvent",
    "ProjectProgressEvent",
    "AgentStatusEvent",
    "LogEvent",
    "TaskCompleteEvent",
    "ProjectStatusEvent",
    "DashboardUpdateEvent",
]
