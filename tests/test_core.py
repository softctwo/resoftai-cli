"""
Tests for core components.
"""

import pytest
from resoftai.core.message_bus import MessageBus, Message, MessageType
from resoftai.core.state import ProjectState, WorkflowStage, Task, TaskStatus


class TestMessageBus:
    """Tests for MessageBus."""

    @pytest.mark.asyncio
    async def test_publish_subscribe(self):
        """Test basic publish/subscribe functionality."""
        bus = MessageBus()
        received_messages = []

        def callback(msg: Message):
            received_messages.append(msg)

        bus.subscribe("type:system", callback)

        message = Message(type=MessageType.SYSTEM, sender="test")
        await bus.publish(message)

        assert len(received_messages) == 1
        assert received_messages[0].sender == "test"

    def test_message_history(self):
        """Test message history retrieval."""
        bus = MessageBus()

        # Clear any existing history
        bus.clear_history()

        # Publish messages synchronously for testing
        import asyncio
        asyncio.run(bus.publish(Message(type=MessageType.SYSTEM, sender="agent1")))
        asyncio.run(bus.publish(Message(type=MessageType.SYSTEM, sender="agent2")))

        history = bus.get_message_history()
        assert len(history) == 2

        # Filter by sender
        agent1_messages = bus.get_message_history(sender="agent1")
        assert len(agent1_messages) == 1
        assert agent1_messages[0].sender == "agent1"


class TestProjectState:
    """Tests for ProjectState."""

    def test_create_project_state(self):
        """Test creating a project state."""
        state = ProjectState(
            name="Test Project",
            description="Test description"
        )

        assert state.name == "Test Project"
        assert state.description == "Test description"
        assert state.current_stage == WorkflowStage.INITIAL

    def test_add_task(self):
        """Test adding tasks to project."""
        state = ProjectState(name="Test Project")

        task = Task(
            title="Test Task",
            description="Test description",
            status=TaskStatus.PENDING
        )

        state.add_task(task)

        assert task.id in state.tasks
        assert state.tasks[task.id] == task

    def test_update_task(self):
        """Test updating task status."""
        state = ProjectState(name="Test Project")

        task = Task(title="Test Task")
        state.add_task(task)

        state.update_task(task.id, status=TaskStatus.COMPLETED)

        assert state.tasks[task.id].status == TaskStatus.COMPLETED

    def test_get_tasks_by_stage(self):
        """Test filtering tasks by stage."""
        state = ProjectState(name="Test Project")

        task1 = Task(title="Task 1", stage=WorkflowStage.REQUIREMENTS_GATHERING)
        task2 = Task(title="Task 2", stage=WorkflowStage.ARCHITECTURE_DESIGN)

        state.add_task(task1)
        state.add_task(task2)

        req_tasks = state.get_tasks_by_stage(WorkflowStage.REQUIREMENTS_GATHERING)
        assert len(req_tasks) == 1
        assert req_tasks[0].title == "Task 1"

    def test_add_decision(self):
        """Test adding project decisions."""
        state = ProjectState(name="Test Project")

        state.add_decision(
            decision="Use Python for backend",
            made_by="architect",
            rationale="Team expertise"
        )

        assert len(state.decisions) == 1
        assert state.decisions[0]["decision"] == "Use Python for backend"

    def test_advance_stage(self):
        """Test advancing workflow stage."""
        state = ProjectState(name="Test Project")

        state.advance_stage(WorkflowStage.REQUIREMENTS_GATHERING)

        assert state.current_stage == WorkflowStage.REQUIREMENTS_GATHERING
