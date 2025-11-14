"""Tests for Architect Agent."""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from resoftai.agents.architect import ArchitectAgent
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
    return ProjectState(
        name="Test Project",
        description="Test project for agent testing",
        requirements={"initial_input": "Build a web application"}
    )


@pytest.fixture
def message_bus():
    """Create test message bus."""
    return MessageBus()


@pytest.fixture
@patch('resoftai.llm.factory.LLMFactory.create')
def architect_agent(mock_llm_factory, message_bus, project_state, mock_llm_config):
    """Create architect agent with mocked LLM."""
    mock_llm = MagicMock()
    mock_llm.generate = AsyncMock(return_value=MagicMock(
        content="Generated architecture",
        usage={"total_tokens": 100}
    ))
    mock_llm_factory.return_value = mock_llm

    agent = ArchitectAgent(
        role=AgentRole.ARCHITECT,
        message_bus=message_bus,
        project_state=project_state,
        llm_config=mock_llm_config
    )
    return agent


def test_architect_agent_initialization(architect_agent):
    """Test architect agent initialization."""
    assert architect_agent.role == AgentRole.ARCHITECT
    assert architect_agent.name == "Software Architect"
    assert len(architect_agent.capabilities) > 0
    assert WorkflowStage.ARCHITECTURE_DESIGN in architect_agent.responsible_stages


def test_architect_agent_capabilities(architect_agent):
    """Test architect agent has proper capabilities."""
    capability_names = [cap.name for cap in architect_agent.capabilities]

    assert "architecture_design" in capability_names
    assert "database_design" in capability_names


def test_architect_system_prompt(architect_agent):
    """Test architect has a proper system prompt."""
    prompt = architect_agent.system_prompt

    assert len(prompt) > 0
    assert "architect" in prompt.lower() or "architecture" in prompt.lower()
    assert "design" in prompt.lower()


@pytest.mark.asyncio
@patch('resoftai.llm.factory.LLMFactory.create')
async def test_handle_task_assignment_architecture(mock_llm_factory, message_bus, project_state, mock_llm_config):
    """Test handling architecture design task."""
    mock_llm = MagicMock()
    mock_llm.generate = AsyncMock(return_value=MagicMock(
        content="# System Architecture\n\nDesigned architecture...",
        usage={"total_tokens": 500}
    ))
    mock_llm_factory.return_value = mock_llm

    agent = ArchitectAgent(
        role=AgentRole.ARCHITECT,
        message_bus=message_bus,
        project_state=project_state,
        llm_config=mock_llm_config
    )

    # Create task
    task_id = "task-1"
    task = {
        "title": "Design system architecture",
        "description": "Create overall system architecture"
    }

    message = Message(
        type=MessageType.TASK_ASSIGNED,
        sender="workflow",
        receiver=agent.role.value,
        content={"task_id": task_id, "task": task}
    )

    await agent.handle_task_assignment(message)

    # Verify LLM was called
    assert mock_llm.generate.called


@pytest.mark.asyncio
@patch('resoftai.llm.factory.LLMFactory.create')
async def test_handle_task_assignment_database(mock_llm_factory, message_bus, project_state, mock_llm_config):
    """Test handling database design task."""
    mock_llm = MagicMock()
    mock_llm.generate = AsyncMock(return_value=MagicMock(
        content="# Database Schema\n\nDesigned schema...",
        usage={"total_tokens": 300}
    ))
    mock_llm_factory.return_value = mock_llm

    agent = ArchitectAgent(
        role=AgentRole.ARCHITECT,
        message_bus=message_bus,
        project_state=project_state,
        llm_config=mock_llm_config
    )

    task_id = "task-2"
    task = {
        "title": "Design database schema",
        "description": "Create database design"
    }

    message = Message(
        type=MessageType.TASK_ASSIGNED,
        sender="workflow",
        receiver=agent.role.value,
        content={"task_id": task_id, "task": task}
    )

    await agent.handle_task_assignment(message)

    # Verify LLM was called
    assert mock_llm.generate.called


@pytest.mark.asyncio
@patch('resoftai.llm.factory.LLMFactory.create')
async def test_process_request(mock_llm_factory, architect_agent):
    """Test processing architecture design request."""
    message = Message(
        type=MessageType.AGENT_REQUEST,
        sender="user",
        receiver=architect_agent.role.value,
        content={"request_type": "design_architecture"}
    )

    # Should not raise an exception
    await architect_agent.process_request(message)


def test_context_from_state(architect_agent):
    """Test getting context from project state."""
    context = architect_agent.get_context_from_state()

    assert isinstance(context, str)
    assert len(context) > 0


@pytest.mark.asyncio
@patch('resoftai.llm.factory.LLMFactory.create')
async def test_send_message(mock_llm_factory, message_bus, project_state, mock_llm_config):
    """Test agent can send messages."""
    mock_llm = MagicMock()
    mock_llm_factory.return_value = mock_llm

    agent = ArchitectAgent(
        role=AgentRole.ARCHITECT,
        message_bus=message_bus,
        project_state=project_state,
        llm_config=mock_llm_config
    )

    # Send a message
    await agent.send_message(
        MessageType.AGENT_RESPONSE,
        "workflow",
        {"status": "completed"}
    )

    # Message should be in the bus (depending on implementation)
