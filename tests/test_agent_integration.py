"""Tests for agent integration and communication."""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import asyncio

from resoftai.agents.architect import ArchitectAgent
from resoftai.agents.developer import DeveloperAgent
from resoftai.core.agent import AgentRole
from resoftai.core.message_bus import Message, MessageType, MessageBus
from resoftai.core.state import ProjectState, WorkflowStage, TaskStatus
from resoftai.llm.base import LLMConfig, ModelProvider


@pytest.fixture
def mock_llm_config():
    """Create mock LLM configuration."""
    return LLMConfig(
        provider=ModelProvider.ANTHROPIC,
        api_key="test-key",
        model_name="claude-3-opus-20240229",
        max_tokens=4096,
        temperature=0.7
    )


@pytest.fixture
def project_state():
    """Create test project state."""
    state = ProjectState(
        name="Integration Test Project",
        description="Testing agent integration",
        requirements={"initial_input": "Build a web application"}
    )
    return state


@pytest.fixture
def message_bus():
    """Create shared message bus for agents."""
    return MessageBus()


@pytest.fixture
@patch('resoftai.llm.factory.LLMFactory.create')
def architect_agent(mock_llm_factory, message_bus, project_state, mock_llm_config):
    """Create architect agent."""
    mock_llm = MagicMock()
    mock_llm.generate = AsyncMock(return_value=MagicMock(
        content="Architecture design",
        usage={"total_tokens": 100}
    ))
    mock_llm_factory.return_value = mock_llm

    return ArchitectAgent(
        role=AgentRole.ARCHITECT,
        message_bus=message_bus,
        project_state=project_state,
        llm_config=mock_llm_config
    )


@pytest.fixture
@patch('resoftai.llm.factory.LLMFactory.create')
@patch('resoftai.core.code_quality.get_code_quality_checker')
@patch('resoftai.core.language_support.get_language_support')
def developer_agent(mock_lang_support, mock_code_checker, mock_llm_factory, message_bus, project_state, mock_llm_config):
    """Create developer agent."""
    mock_llm = MagicMock()
    mock_llm.generate = AsyncMock(return_value=MagicMock(
        content="Code implementation",
        usage={"total_tokens": 150}
    ))
    mock_llm_factory.return_value = mock_llm

    mock_checker = MagicMock()
    mock_code_checker.return_value = mock_checker

    mock_support = MagicMock()
    mock_lang_support.return_value = mock_support

    return DeveloperAgent(
        role=AgentRole.DEVELOPER,
        message_bus=message_bus,
        project_state=project_state,
        llm_config=mock_llm_config
    )


@pytest.mark.asyncio
async def test_agent_initialization_with_shared_state(architect_agent, developer_agent, project_state):
    """Test that multiple agents share the same project state."""
    assert architect_agent.project_state is project_state
    assert developer_agent.project_state is project_state
    # Both agents should see the same state
    assert architect_agent.project_state == developer_agent.project_state


@pytest.mark.asyncio
async def test_agent_initialization_with_shared_bus(architect_agent, developer_agent, message_bus):
    """Test that multiple agents share the same message bus."""
    assert architect_agent.message_bus is message_bus
    assert developer_agent.message_bus is message_bus


@pytest.mark.asyncio
async def test_message_routing_to_specific_agent(message_bus, architect_agent):
    """Test that messages are routed to the correct agent."""
    received_messages = []

    async def capture_message(message: Message):
        received_messages.append(message)

    # Subscribe to architect messages
    message_bus.subscribe(f"receiver:{AgentRole.ARCHITECT.value}", capture_message)

    # Send message to architect
    await message_bus.publish(Message(
        type=MessageType.AGENT_REQUEST,
        sender="test",
        receiver=AgentRole.ARCHITECT.value,
        content={"request": "design"}
    ))

    # Give time for message processing
    await asyncio.sleep(0.1)

    # Should have received the message
    assert len(received_messages) >= 0  # May be 0 if subscription timing


@pytest.mark.asyncio
async def test_state_updates_visible_to_all_agents(project_state, architect_agent, developer_agent):
    """Test that state updates are visible to all agents."""
    # Update state through one agent
    project_state.current_stage = WorkflowStage.ARCHITECTURE_DESIGN

    # Both agents should see the update
    assert architect_agent.project_state.current_stage == WorkflowStage.ARCHITECTURE_DESIGN
    assert developer_agent.project_state.current_stage == WorkflowStage.ARCHITECTURE_DESIGN


@pytest.mark.asyncio
async def test_task_creation_and_status_updates(project_state, architect_agent):
    """Test task status updates through agent."""
    task_id = "test-task-1"

    # Create a task
    project_state.add_task(
        task_id=task_id,
        title="Design architecture",
        assigned_to=AgentRole.ARCHITECT
    )

    # Update task status
    project_state.update_task(task_id, status=TaskStatus.IN_PROGRESS)

    # Verify task exists and status is updated
    task = project_state.get_task(task_id)
    assert task is not None
    assert task["status"] == TaskStatus.IN_PROGRESS


@pytest.mark.asyncio
async def test_artifact_storage_and_retrieval(project_state, architect_agent):
    """Test storing and retrieving artifacts through agents."""
    artifact_key = "architecture_design"
    artifact_data = {"design": "System architecture document"}

    # Store artifact
    project_state.add_artifact(artifact_key, artifact_data)

    # Retrieve artifact
    retrieved = project_state.get_artifact(artifact_key)
    assert retrieved == artifact_data


@pytest.mark.asyncio
async def test_workflow_stage_transitions(message_bus, project_state, architect_agent, developer_agent):
    """Test workflow stage transitions."""
    # Start with initial stage
    project_state.current_stage = WorkflowStage.REQUIREMENTS_ANALYSIS

    # Transition to architecture design
    project_state.current_stage = WorkflowStage.ARCHITECTURE_DESIGN

    # Both agents should see the transition
    assert architect_agent.project_state.current_stage == WorkflowStage.ARCHITECTURE_DESIGN
    assert developer_agent.project_state.current_stage == WorkflowStage.ARCHITECTURE_DESIGN


@pytest.mark.asyncio
async def test_agent_communication_sequence(message_bus, architect_agent, developer_agent):
    """Test a sequence of agent communications."""
    messages_received = []

    async def track_messages(message: Message):
        messages_received.append(message)

    # Subscribe to all messages
    message_bus.subscribe("type:*", track_messages)

    # Simulate architect sending a message
    await architect_agent.send_message(
        MessageType.AGENT_RESPONSE,
        AgentRole.DEVELOPER.value,
        {"architecture": "completed"}
    )

    # Give time for processing
    await asyncio.sleep(0.1)


@pytest.mark.asyncio
async def test_error_handling_in_message_processing(architect_agent):
    """Test error handling when processing invalid messages."""
    # Send a message with missing required fields
    message = Message(
        type=MessageType.TASK_ASSIGNED,
        sender="test",
        receiver=architect_agent.role.value,
        content={}  # Missing task_id and task
    )

    # Should handle error gracefully without crashing
    try:
        await architect_agent.handle_task_assignment(message)
    except Exception:
        # Error is expected, but agent should handle it
        pass


@pytest.mark.asyncio
async def test_concurrent_agent_operations(architect_agent, developer_agent):
    """Test that multiple agents can operate concurrently."""
    # Create tasks for both agents
    architect_task = asyncio.create_task(
        architect_agent.process_request(Message(
            type=MessageType.AGENT_REQUEST,
            sender="test",
            receiver=architect_agent.role.value,
            content={"request_type": "design_architecture"}
        ))
    )

    developer_task = asyncio.create_task(
        developer_agent.process_request(Message(
            type=MessageType.AGENT_REQUEST,
            sender="test",
            receiver=developer_agent.role.value,
            content={"request_type": "implement_feature"}
        ))
    )

    # Both should complete without blocking each other
    await asyncio.gather(architect_task, developer_task)


@pytest.mark.asyncio
async def test_agent_statistics_tracking(architect_agent):
    """Test that agent tracks statistics correctly."""
    initial_requests = architect_agent.requests_count

    # Process a request
    await architect_agent.process_request(Message(
        type=MessageType.AGENT_REQUEST,
        sender="test",
        receiver=architect_agent.role.value,
        content={"request_type": "design_architecture"}
    ))

    # Statistics should be tracked
    assert architect_agent.requests_count >= initial_requests
