"""
Comprehensive tests for core message bus.
"""
import pytest
import asyncio
from datetime import datetime
from unittest.mock import Mock, AsyncMock

from resoftai.core.message_bus import MessageBus, Message, MessageType


@pytest.fixture
def message_bus():
    """Create message bus instance."""
    return MessageBus()


@pytest.fixture
def sample_message():
    """Create sample message."""
    return Message(
        type=MessageType.AGENT_REQUEST,
        sender="agent1",
        receiver="agent2",
        content={"task": "Test task"},
        metadata={"priority": "high"}
    )


class TestMessage:
    """Test Message dataclass."""

    def test_message_creation_defaults(self):
        """Test message creation with defaults."""
        message = Message()

        assert message.id is not None
        assert len(message.id) > 0
        assert message.type == MessageType.SYSTEM
        assert message.sender == "system"
        assert message.receiver is None
        assert message.content == {}
        assert isinstance(message.timestamp, datetime)
        assert message.correlation_id is None
        assert message.metadata == {}

    def test_message_creation_with_params(self):
        """Test message creation with parameters."""
        message = Message(
            type=MessageType.AGENT_RESPONSE,
            sender="agent1",
            receiver="agent2",
            content={"result": "success"},
            correlation_id="corr-123",
            metadata={"key": "value"}
        )

        assert message.type == MessageType.AGENT_RESPONSE
        assert message.sender == "agent1"
        assert message.receiver == "agent2"
        assert message.content == {"result": "success"}
        assert message.correlation_id == "corr-123"
        assert message.metadata == {"key": "value"}

    def test_message_to_dict(self):
        """Test converting message to dictionary."""
        message = Message(
            type=MessageType.WORKFLOW_START,
            sender="orchestrator",
            receiver="agent1",
            content={"project_id": 1},
            correlation_id="workflow-1"
        )

        message_dict = message.to_dict()

        assert message_dict["id"] == message.id
        assert message_dict["type"] == "workflow_start"
        assert message_dict["sender"] == "orchestrator"
        assert message_dict["receiver"] == "agent1"
        assert message_dict["content"] == {"project_id": 1}
        assert message_dict["correlation_id"] == "workflow-1"
        assert isinstance(message_dict["timestamp"], str)

    def test_message_unique_ids(self):
        """Test that each message gets unique ID."""
        msg1 = Message()
        msg2 = Message()

        assert msg1.id != msg2.id


class TestMessageBusSubscription:
    """Test message bus subscription."""

    def test_subscribe_single_topic(self, message_bus):
        """Test subscribing to a single topic."""
        callback = Mock()
        message_bus.subscribe("type:agent_request", callback)

        assert "type:agent_request" in message_bus._subscribers
        assert callback in message_bus._subscribers["type:agent_request"]

    def test_subscribe_multiple_callbacks(self, message_bus):
        """Test subscribing multiple callbacks to same topic."""
        callback1 = Mock()
        callback2 = Mock()

        message_bus.subscribe("type:system", callback1)
        message_bus.subscribe("type:system", callback2)

        assert len(message_bus._subscribers["type:system"]) == 2
        assert callback1 in message_bus._subscribers["type:system"]
        assert callback2 in message_bus._subscribers["type:system"]

    def test_unsubscribe(self, message_bus):
        """Test unsubscribing from topic."""
        callback = Mock()
        message_bus.subscribe("sender:agent1", callback)

        message_bus.unsubscribe("sender:agent1", callback)

        assert "sender:agent1" not in message_bus._subscribers

    def test_unsubscribe_with_multiple_callbacks(self, message_bus):
        """Test unsubscribing one callback when multiple exist."""
        callback1 = Mock()
        callback2 = Mock()

        message_bus.subscribe("topic", callback1)
        message_bus.subscribe("topic", callback2)

        message_bus.unsubscribe("topic", callback1)

        assert "topic" in message_bus._subscribers
        assert callback1 not in message_bus._subscribers["topic"]
        assert callback2 in message_bus._subscribers["topic"]


class TestMessageBusPublish:
    """Test message bus publishing."""

    @pytest.mark.asyncio
    async def test_publish_to_type_topic(self, message_bus):
        """Test publishing message to type topic subscribers."""
        callback = Mock()
        message_bus.subscribe("type:agent_request", callback)

        message = Message(
            type=MessageType.AGENT_REQUEST,
            sender="agent1",
            content={"data": "test"}
        )

        await message_bus.publish(message)

        callback.assert_called_once_with(message)

    @pytest.mark.asyncio
    async def test_publish_to_sender_topic(self, message_bus):
        """Test publishing message to sender topic subscribers."""
        callback = Mock()
        message_bus.subscribe("sender:agent1", callback)

        message = Message(
            type=MessageType.AGENT_NOTIFICATION,
            sender="agent1",
            content={"notification": "test"}
        )

        await message_bus.publish(message)

        callback.assert_called_once_with(message)

    @pytest.mark.asyncio
    async def test_publish_to_receiver_topic(self, message_bus):
        """Test publishing message to receiver topic subscribers."""
        callback = Mock()
        message_bus.subscribe("receiver:agent2", callback)

        message = Message(
            type=MessageType.AGENT_REQUEST,
            sender="agent1",
            receiver="agent2",
            content={"request": "test"}
        )

        await message_bus.publish(message)

        callback.assert_called_once_with(message)

    @pytest.mark.asyncio
    async def test_publish_to_wildcard_topic(self, message_bus):
        """Test publishing to wildcard topic."""
        callback = Mock()
        message_bus.subscribe("*", callback)

        message = Message(
            type=MessageType.SYSTEM,
            sender="system"
        )

        await message_bus.publish(message)

        callback.assert_called_once_with(message)

    @pytest.mark.asyncio
    async def test_publish_to_multiple_topics(self, message_bus):
        """Test message published to all matching topics."""
        type_callback = Mock()
        sender_callback = Mock()
        wildcard_callback = Mock()

        message_bus.subscribe("type:workflow_start", type_callback)
        message_bus.subscribe("sender:orchestrator", sender_callback)
        message_bus.subscribe("*", wildcard_callback)

        message = Message(
            type=MessageType.WORKFLOW_START,
            sender="orchestrator",
            content={"project": "test"}
        )

        await message_bus.publish(message)

        type_callback.assert_called_once_with(message)
        sender_callback.assert_called_once_with(message)
        wildcard_callback.assert_called_once_with(message)

    @pytest.mark.asyncio
    async def test_publish_async_callback(self, message_bus):
        """Test publishing with async callback."""
        async_callback = AsyncMock()
        message_bus.subscribe("type:task_complete", async_callback)

        message = Message(
            type=MessageType.TASK_COMPLETE,
            sender="agent1",
            content={"status": "done"}
        )

        await message_bus.publish(message)

        async_callback.assert_called_once_with(message)

    @pytest.mark.asyncio
    async def test_publish_callback_error_handling(self, message_bus):
        """Test error handling in subscriber callbacks."""
        def failing_callback(msg):
            raise ValueError("Test error")

        working_callback = Mock()

        message_bus.subscribe("type:system", failing_callback)
        message_bus.subscribe("type:system", working_callback)

        message = Message(type=MessageType.SYSTEM)

        # Should not raise exception
        await message_bus.publish(message)

        # Working callback should still be called
        working_callback.assert_called_once_with(message)

    @pytest.mark.asyncio
    async def test_publish_stores_in_history(self, message_bus):
        """Test published messages are stored in history."""
        message1 = Message(type=MessageType.AGENT_REQUEST)
        message2 = Message(type=MessageType.AGENT_RESPONSE)

        await message_bus.publish(message1)
        await message_bus.publish(message2)

        assert len(message_bus._message_history) == 2
        assert message_bus._message_history[0] == message1
        assert message_bus._message_history[1] == message2


class TestMessageBusHistory:
    """Test message bus history functionality."""

    @pytest.mark.asyncio
    async def test_get_message_history_all(self, message_bus):
        """Test getting all message history."""
        msg1 = Message(sender="agent1")
        msg2 = Message(sender="agent2")
        msg3 = Message(sender="agent1")

        await message_bus.publish(msg1)
        await message_bus.publish(msg2)
        await message_bus.publish(msg3)

        history = message_bus.get_message_history()

        assert len(history) == 3
        assert history[0] == msg1
        assert history[1] == msg2
        assert history[2] == msg3

    @pytest.mark.asyncio
    async def test_get_message_history_filter_sender(self, message_bus):
        """Test filtering history by sender."""
        msg1 = Message(sender="agent1", type=MessageType.AGENT_REQUEST)
        msg2 = Message(sender="agent2", type=MessageType.AGENT_RESPONSE)
        msg3 = Message(sender="agent1", type=MessageType.AGENT_NOTIFICATION)

        await message_bus.publish(msg1)
        await message_bus.publish(msg2)
        await message_bus.publish(msg3)

        history = message_bus.get_message_history(sender="agent1")

        assert len(history) == 2
        assert history[0] == msg1
        assert history[1] == msg3

    @pytest.mark.asyncio
    async def test_get_message_history_filter_receiver(self, message_bus):
        """Test filtering history by receiver."""
        msg1 = Message(receiver="agent1")
        msg2 = Message(receiver="agent2")
        msg3 = Message(receiver="agent1")

        await message_bus.publish(msg1)
        await message_bus.publish(msg2)
        await message_bus.publish(msg3)

        history = message_bus.get_message_history(receiver="agent1")

        assert len(history) == 2
        assert history[0] == msg1
        assert history[1] == msg3

    @pytest.mark.asyncio
    async def test_get_message_history_filter_type(self, message_bus):
        """Test filtering history by message type."""
        msg1 = Message(type=MessageType.WORKFLOW_START)
        msg2 = Message(type=MessageType.TASK_ASSIGNED)
        msg3 = Message(type=MessageType.WORKFLOW_START)

        await message_bus.publish(msg1)
        await message_bus.publish(msg2)
        await message_bus.publish(msg3)

        history = message_bus.get_message_history(message_type=MessageType.WORKFLOW_START)

        assert len(history) == 2
        assert history[0] == msg1
        assert history[1] == msg3

    @pytest.mark.asyncio
    async def test_get_message_history_with_limit(self, message_bus):
        """Test limiting number of history messages returned."""
        for i in range(10):
            await message_bus.publish(Message(sender=f"agent{i}"))

        history = message_bus.get_message_history(limit=5)

        assert len(history) == 5
        # Should return last 5 messages
        assert history[0].sender == "agent5"
        assert history[4].sender == "agent9"

    @pytest.mark.asyncio
    async def test_get_message_history_combined_filters(self, message_bus):
        """Test using multiple filters together."""
        msg1 = Message(sender="agent1", receiver="agent2", type=MessageType.AGENT_REQUEST)
        msg2 = Message(sender="agent1", receiver="agent3", type=MessageType.AGENT_REQUEST)
        msg3 = Message(sender="agent2", receiver="agent2", type=MessageType.AGENT_RESPONSE)
        msg4 = Message(sender="agent1", receiver="agent2", type=MessageType.AGENT_REQUEST)

        await message_bus.publish(msg1)
        await message_bus.publish(msg2)
        await message_bus.publish(msg3)
        await message_bus.publish(msg4)

        history = message_bus.get_message_history(
            sender="agent1",
            receiver="agent2",
            message_type=MessageType.AGENT_REQUEST
        )

        assert len(history) == 2
        assert history[0] == msg1
        assert history[1] == msg4

    def test_clear_history(self, message_bus):
        """Test clearing message history."""
        message_bus._message_history = [
            Message(), Message(), Message()
        ]

        message_bus.clear_history()

        assert len(message_bus._message_history) == 0


class TestMessageBusIntegration:
    """Integration tests for message bus."""

    @pytest.mark.asyncio
    async def test_multiple_subscribers_workflow(self, message_bus):
        """Test complete workflow with multiple subscribers."""
        # Set up subscribers
        workflow_messages = []
        task_messages = []

        def workflow_handler(msg):
            workflow_messages.append(msg)

        def task_handler(msg):
            task_messages.append(msg)

        message_bus.subscribe("type:workflow_start", workflow_handler)
        message_bus.subscribe("type:workflow_complete", workflow_handler)
        message_bus.subscribe("type:task_assigned", task_handler)
        message_bus.subscribe("type:task_complete", task_handler)

        # Publish messages
        msg1 = Message(type=MessageType.WORKFLOW_START, sender="orchestrator")
        msg2 = Message(type=MessageType.TASK_ASSIGNED, sender="orchestrator", receiver="agent1")
        msg3 = Message(type=MessageType.TASK_COMPLETE, sender="agent1")
        msg4 = Message(type=MessageType.WORKFLOW_COMPLETE, sender="orchestrator")

        await message_bus.publish(msg1)
        await message_bus.publish(msg2)
        await message_bus.publish(msg3)
        await message_bus.publish(msg4)

        # Verify
        assert len(workflow_messages) == 2
        assert len(task_messages) == 2
        assert workflow_messages[0] == msg1
        assert workflow_messages[1] == msg4
        assert task_messages[0] == msg2
        assert task_messages[1] == msg3

    @pytest.mark.asyncio
    async def test_concurrent_publishing(self, message_bus):
        """Test concurrent message publishing."""
        callback = Mock()
        message_bus.subscribe("*", callback)

        # Publish multiple messages concurrently
        messages = [Message(sender=f"agent{i}") for i in range(20)]

        await asyncio.gather(*[message_bus.publish(msg) for msg in messages])

        assert len(message_bus._message_history) == 20
        assert callback.call_count == 20

    @pytest.mark.asyncio
    async def test_subscribe_unsubscribe_during_publishing(self, message_bus):
        """Test subscription changes during message flow."""
        callback1 = Mock()
        callback2 = Mock()

        message_bus.subscribe("type:system", callback1)

        # Publish first message
        msg1 = Message(type=MessageType.SYSTEM)
        await message_bus.publish(msg1)

        # Add another subscriber
        message_bus.subscribe("type:system", callback2)

        # Publish second message
        msg2 = Message(type=MessageType.SYSTEM)
        await message_bus.publish(msg2)

        # Remove first subscriber
        message_bus.unsubscribe("type:system", callback1)

        # Publish third message
        msg3 = Message(type=MessageType.SYSTEM)
        await message_bus.publish(msg3)

        # Verify call counts
        assert callback1.call_count == 2  # msg1, msg2
        assert callback2.call_count == 2  # msg2, msg3


class TestMessageBusTopics:
    """Test message bus topic routing."""

    def test_get_topics_for_message_basic(self, message_bus):
        """Test getting topics for basic message."""
        message = Message(
            type=MessageType.AGENT_REQUEST,
            sender="agent1"
        )

        topics = message_bus._get_topics_for_message(message)

        assert "type:agent_request" in topics
        assert "sender:agent1" in topics
        assert "*" in topics
        assert len(topics) == 3

    def test_get_topics_for_message_with_receiver(self, message_bus):
        """Test getting topics for message with receiver."""
        message = Message(
            type=MessageType.AGENT_RESPONSE,
            sender="agent1",
            receiver="agent2"
        )

        topics = message_bus._get_topics_for_message(message)

        assert "type:agent_response" in topics
        assert "sender:agent1" in topics
        assert "receiver:agent2" in topics
        assert "*" in topics
        assert len(topics) == 4
