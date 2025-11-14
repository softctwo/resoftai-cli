"""Tests for Developer Agent."""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

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
        name="Test Project",
        description="Test project for developer agent testing",
        requirements={"initial_input": "Build a REST API"}
    )
    state.architecture = {"tech_stack": "Python/FastAPI"}
    return state


@pytest.fixture
def message_bus():
    """Create test message bus."""
    return MessageBus()


@pytest.fixture
@patch('resoftai.llm.factory.LLMFactory.create')
@patch('resoftai.core.code_quality.get_code_quality_checker')
@patch('resoftai.core.language_support.get_language_support')
def developer_agent(mock_lang_support, mock_code_checker, mock_llm_factory, message_bus, project_state, mock_llm_config):
    """Create developer agent with mocked dependencies."""
    mock_llm = MagicMock()
    mock_llm.generate = AsyncMock(return_value=MagicMock(
        content="Generated code implementation",
        usage={"total_tokens": 200}
    ))
    mock_llm_factory.return_value = mock_llm

    # Mock code quality checker
    mock_checker = MagicMock()
    mock_checker.check_quality = MagicMock(return_value={
        "score": 85,
        "issues": []
    })
    mock_code_checker.return_value = mock_checker

    # Mock language support
    mock_support = MagicMock()
    mock_lang_support.return_value = mock_support

    agent = DeveloperAgent(
        role=AgentRole.DEVELOPER,
        message_bus=message_bus,
        project_state=project_state,
        llm_config=mock_llm_config
    )
    return agent


def test_developer_agent_initialization(developer_agent):
    """Test developer agent initialization."""
    assert developer_agent.role == AgentRole.DEVELOPER
    assert developer_agent.name == "Software Developer"
    assert len(developer_agent.capabilities) > 0
    assert WorkflowStage.IMPLEMENTATION in developer_agent.responsible_stages


def test_developer_agent_capabilities(developer_agent):
    """Test developer agent has proper capabilities."""
    capability_names = [cap.name for cap in developer_agent.capabilities]

    assert "feature_implementation" in capability_names
    assert "code_review" in capability_names
    assert "code_quality_check" in capability_names


def test_developer_system_prompt(developer_agent):
    """Test developer has a comprehensive system prompt."""
    prompt = developer_agent.system_prompt

    assert len(prompt) > 0
    assert "developer" in prompt.lower() or "implement" in prompt.lower()
    assert "code" in prompt.lower()
    assert "quality" in prompt.lower()


@pytest.mark.asyncio
@patch('resoftai.llm.factory.LLMFactory.create')
@patch('resoftai.core.code_quality.get_code_quality_checker')
@patch('resoftai.core.language_support.get_language_support')
async def test_handle_task_assignment_feature(mock_lang_support, mock_code_checker, mock_llm_factory, message_bus, project_state, mock_llm_config):
    """Test handling feature implementation task."""
    mock_llm = MagicMock()
    mock_llm.generate = AsyncMock(return_value=MagicMock(
        content="def feature():\n    pass",
        usage={"total_tokens": 150}
    ))
    mock_llm_factory.return_value = mock_llm

    mock_checker = MagicMock()
    mock_code_checker.return_value = mock_checker

    mock_support = MagicMock()
    mock_lang_support.return_value = mock_support

    agent = DeveloperAgent(
        role=AgentRole.DEVELOPER,
        message_bus=message_bus,
        project_state=project_state,
        llm_config=mock_llm_config
    )

    task_id = "task-1"
    task = {
        "title": "Implement user authentication",
        "description": "Create login and registration endpoints"
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
@patch('resoftai.core.code_quality.get_code_quality_checker')
@patch('resoftai.core.language_support.get_language_support')
async def test_check_code_quality(mock_lang_support, mock_code_checker, mock_llm_factory, developer_agent):
    """Test code quality check functionality."""
    code = """
def hello_world():
    print("Hello, World!")
    """

    # Mock code checker response
    developer_agent.code_checker.check_quality = MagicMock(return_value={
        "score": 90,
        "issues": [],
        "suggestions": []
    })

    result = developer_agent.check_code_quality(code, "test.py")

    assert "score" in result
    assert result["score"] == 90
    assert developer_agent.code_checker.check_quality.called


@pytest.mark.asyncio
@patch('resoftai.llm.factory.LLMFactory.create')
@patch('resoftai.core.code_quality.get_code_quality_checker')
@patch('resoftai.core.language_support.get_language_support')
async def test_process_request(mock_lang_support, mock_code_checker, mock_llm_factory, developer_agent):
    """Test processing implementation request."""
    message = Message(
        type=MessageType.AGENT_REQUEST,
        sender="user",
        receiver=developer_agent.role.value,
        content={
            "request_type": "implement_feature",
            "specification": "Create a user registration function"
        }
    )

    # Should not raise an exception
    await developer_agent.process_request(message)


def test_context_from_state(developer_agent):
    """Test getting context from project state."""
    context = developer_agent.get_context_from_state()

    assert isinstance(context, str)
    assert len(context) > 0


@pytest.mark.asyncio
@patch('resoftai.llm.factory.LLMFactory.create')
@patch('resoftai.core.code_quality.get_code_quality_checker')
@patch('resoftai.core.language_support.get_language_support')
async def test_language_detection(mock_lang_support, mock_code_checker, mock_llm_factory, developer_agent):
    """Test language detection from project state."""
    # Agent should detect language from architecture
    lang = developer_agent._detect_target_language()

    # Should return a language (Python in this case based on architecture)
    assert lang is not None
    assert isinstance(lang, str)


@pytest.mark.asyncio
@patch('resoftai.llm.factory.LLMFactory.create')
@patch('resoftai.core.code_quality.get_code_quality_checker')
@patch('resoftai.core.language_support.get_language_support')
async def test_multiple_language_support(mock_lang_support, mock_code_checker, mock_llm_factory, developer_agent):
    """Test that developer agent supports multiple languages."""
    prompt = developer_agent.system_prompt

    # Should mention multiple languages
    assert "Python" in prompt
    assert "JavaScript" in prompt or "TypeScript" in prompt
    assert "Java" in prompt or "Go" in prompt


@pytest.mark.asyncio
@patch('resoftai.llm.factory.LLMFactory.create')
@patch('resoftai.core.code_quality.get_code_quality_checker')
@patch('resoftai.core.language_support.get_language_support')
async def test_code_quality_integration(mock_lang_support, mock_code_checker, mock_llm_factory, developer_agent):
    """Test integration with code quality checker."""
    assert developer_agent.code_checker is not None
    assert developer_agent.language_support is not None
