"""
Message Bus for inter-agent communication.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Callable
from uuid import uuid4
import asyncio
import logging

logger = logging.getLogger(__name__)


class MessageType(str, Enum):
    """Types of messages in the system."""

    # System messages
    SYSTEM = "system"

    # Agent communication
    AGENT_REQUEST = "agent_request"
    AGENT_RESPONSE = "agent_response"
    AGENT_NOTIFICATION = "agent_notification"

    # Workflow control
    WORKFLOW_START = "workflow_start"
    WORKFLOW_COMPLETE = "workflow_complete"
    STAGE_START = "stage_start"
    STAGE_COMPLETE = "stage_complete"
    TASK_ASSIGNED = "task_assigned"
    TASK_COMPLETE = "task_complete"

    # User interaction
    USER_INPUT = "user_input"
    USER_FEEDBACK = "user_feedback"

    # Documentation
    DOCUMENT_GENERATED = "document_generated"


@dataclass
class Message:
    """Message exchanged between agents and system components."""

    id: str = field(default_factory=lambda: str(uuid4()))
    type: MessageType = MessageType.SYSTEM
    sender: str = "system"
    receiver: Optional[str] = None
    content: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    correlation_id: Optional[str] = None  # For tracking related messages
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert message to dictionary."""
        return {
            "id": self.id,
            "type": self.type.value,
            "sender": self.sender,
            "receiver": self.receiver,
            "content": self.content,
            "timestamp": self.timestamp.isoformat(),
            "correlation_id": self.correlation_id,
            "metadata": self.metadata,
        }


class MessageBus:
    """
    Central message bus for agent communication.
    Implements publish-subscribe pattern with topic-based routing.
    """

    def __init__(self):
        self._subscribers: Dict[str, List[Callable]] = {}
        self._message_history: List[Message] = []
        self._lock = asyncio.Lock()

    async def publish(self, message: Message) -> None:
        """
        Publish a message to all subscribers.

        Args:
            message: Message to publish
        """
        async with self._lock:
            self._message_history.append(message)
            logger.debug(
                f"Publishing message {message.id} from {message.sender} "
                f"type={message.type.value}"
            )

        # Notify subscribers
        topics = self._get_topics_for_message(message)
        for topic in topics:
            if topic in self._subscribers:
                for callback in self._subscribers[topic]:
                    try:
                        if asyncio.iscoroutinefunction(callback):
                            await callback(message)
                        else:
                            callback(message)
                    except Exception as e:
                        logger.error(f"Error in subscriber callback: {e}", exc_info=True)

    def subscribe(self, topic: str, callback: Callable) -> None:
        """
        Subscribe to messages on a topic.

        Args:
            topic: Topic to subscribe to (message type, sender, or receiver)
            callback: Callback function to invoke when message arrives
        """
        if topic not in self._subscribers:
            self._subscribers[topic] = []
        self._subscribers[topic].append(callback)
        logger.debug(f"Subscribed to topic: {topic}")

    def unsubscribe(self, topic: str, callback: Callable) -> None:
        """
        Unsubscribe from a topic.

        Args:
            topic: Topic to unsubscribe from
            callback: Callback function to remove
        """
        if topic in self._subscribers:
            self._subscribers[topic].remove(callback)
            if not self._subscribers[topic]:
                del self._subscribers[topic]

    def get_message_history(
        self,
        sender: Optional[str] = None,
        receiver: Optional[str] = None,
        message_type: Optional[MessageType] = None,
        limit: Optional[int] = None,
    ) -> List[Message]:
        """
        Get message history with optional filters.

        Args:
            sender: Filter by sender
            receiver: Filter by receiver
            message_type: Filter by message type
            limit: Maximum number of messages to return

        Returns:
            List of messages matching filters
        """
        messages = self._message_history

        if sender:
            messages = [m for m in messages if m.sender == sender]
        if receiver:
            messages = [m for m in messages if m.receiver == receiver]
        if message_type:
            messages = [m for m in messages if m.type == message_type]

        if limit:
            messages = messages[-limit:]

        return messages

    def _get_topics_for_message(self, message: Message) -> List[str]:
        """Get all topics that match this message."""
        topics = [
            f"type:{message.type.value}",
            f"sender:{message.sender}",
        ]

        if message.receiver:
            topics.append(f"receiver:{message.receiver}")

        # Global topic for all messages
        topics.append("*")

        return topics

    def clear_history(self) -> None:
        """Clear message history."""
        self._message_history.clear()
