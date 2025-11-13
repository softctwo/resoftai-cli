"""Tests for agent implementations."""
import pytest
from unittest.mock import Mock, AsyncMock, patch

from resoftai.agents.base import Agent, AgentRole, AgentMessage
from resoftai.llm.base import LLMConfig, ModelProvider


@pytest.fixture
def sample_llm_config():
    """Sample LLM configuration."""
    return LLMConfig(
        provider=ModelProvider.DEEPSEEK,
        api_key="test-api-key",
        model_name="deepseek-chat",
        max_tokens=4096,
        temperature=0.7
    )


class TestAgentBase:
    """Test base agent functionality."""

    def test_agent_role_enum(self):
        """Test agent role enumeration."""
        roles = [
            AgentRole.REQUIREMENT_ANALYST,
            AgentRole.ARCHITECT,
            AgentRole.UI_DESIGNER,
            AgentRole.DEVELOPER,
            AgentRole.TESTER,
            AgentRole.QA_REVIEWER
        ]

        assert len(roles) == 6
        assert AgentRole.REQUIREMENT_ANALYST.value == "requirement_analyst"
        assert AgentRole.DEVELOPER.value == "developer"

    def test_agent_message_creation(self):
        """Test agent message creation."""
        message = AgentMessage(
            role="user",
            content="Test message",
            agent_role=AgentRole.REQUIREMENT_ANALYST
        )

        assert message.role == "user"
        assert message.content == "Test message"
        assert message.agent_role == AgentRole.REQUIREMENT_ANALYST
        assert isinstance(message.timestamp, float)

    def test_agent_message_to_dict(self):
        """Test agent message serialization."""
        message = AgentMessage(
            role="assistant",
            content="Response",
            agent_role=AgentRole.ARCHITECT
        )

        message_dict = message.to_dict()

        assert message_dict["role"] == "assistant"
        assert message_dict["content"] == "Response"
        assert message_dict["agent_role"] == AgentRole.ARCHITECT.value
        assert "timestamp" in message_dict


@pytest.mark.asyncio
class TestRequirementAnalyst:
    """Test requirement analyst agent."""

    async def test_requirement_analyst_initialization(self, sample_llm_config):
        """Test requirement analyst initialization."""
        from resoftai.agents.requirement_analyst import RequirementAnalyst

        analyst = RequirementAnalyst(sample_llm_config)

        assert analyst.role == AgentRole.REQUIREMENT_ANALYST
        assert analyst.llm_config == sample_llm_config

    async def test_analyze_requirements_mock(self, sample_llm_config):
        """Test requirement analysis with mocked LLM."""
        from resoftai.agents.requirement_analyst import RequirementAnalyst

        analyst = RequirementAnalyst(sample_llm_config)

        # Mock the LLM generate method
        mock_response = {
            "content": "# Requirements Document\n\n## Functional Requirements\n- User authentication",
            "usage": {"total_tokens": 150}
        }

        with patch.object(analyst.llm, 'generate', new_callable=AsyncMock, return_value=mock_response):
            result = await analyst.analyze("Build a web app with user authentication")

        assert "requirements_doc" in result
        assert "functional_requirements" in result.get("requirements_doc", "").lower()

    async def test_refine_requirements(self, sample_llm_config):
        """Test requirement refinement."""
        from resoftai.agents.requirement_analyst import RequirementAnalyst

        analyst = RequirementAnalyst(sample_llm_config)

        # Mock refinement
        mock_response = {
            "content": "# Refined Requirements\n\nMore detailed requirements...",
            "usage": {"total_tokens": 200}
        }

        with patch.object(analyst.llm, 'generate', new_callable=AsyncMock, return_value=mock_response):
            feedback = "Add more details about authentication"
            result = await analyst.refine("Original requirements", feedback)

        assert "refined" in result.get("requirements_doc", "").lower() or "requirements" in result.get("requirements_doc", "").lower()


@pytest.mark.asyncio
class TestArchitect:
    """Test architect agent."""

    async def test_architect_initialization(self, sample_llm_config):
        """Test architect initialization."""
        from resoftai.agents.architect import Architect

        architect = Architect(sample_llm_config)

        assert architect.role == AgentRole.ARCHITECT
        assert architect.llm_config == sample_llm_config

    async def test_design_architecture_mock(self, sample_llm_config):
        """Test architecture design with mocked LLM."""
        from resoftai.agents.architect import Architect

        architect = Architect(sample_llm_config)

        mock_response = {
            "content": "# Architecture Document\n\n## System Design\n- Frontend: React\n- Backend: FastAPI",
            "usage": {"total_tokens": 250}
        }

        with patch.object(architect.llm, 'generate', new_callable=AsyncMock, return_value=mock_response):
            requirements = "User authentication, data storage"
            result = await architect.design(requirements)

        assert "architecture_doc" in result
        assert "system" in result.get("architecture_doc", "").lower() or "design" in result.get("architecture_doc", "").lower()


@pytest.mark.asyncio
class TestDeveloper:
    """Test developer agent."""

    async def test_developer_initialization(self, sample_llm_config):
        """Test developer initialization."""
        from resoftai.agents.developer import Developer

        developer = Developer(sample_llm_config)

        assert developer.role == AgentRole.DEVELOPER
        assert developer.llm_config == sample_llm_config

    async def test_generate_code_mock(self, sample_llm_config):
        """Test code generation with mocked LLM."""
        from resoftai.agents.developer import Developer

        developer = Developer(sample_llm_config)

        mock_response = {
            "content": "```python\ndef authenticate_user():\n    pass\n```",
            "usage": {"total_tokens": 300}
        }

        with patch.object(developer.llm, 'generate', new_callable=AsyncMock, return_value=mock_response):
            architecture = "FastAPI backend with JWT auth"
            result = await developer.implement(architecture)

        assert "code_files" in result or "implementation" in result


@pytest.mark.asyncio
class TestTester:
    """Test tester agent."""

    async def test_tester_initialization(self, sample_llm_config):
        """Test tester initialization."""
        from resoftai.agents.tester import Tester

        tester = Tester(sample_llm_config)

        assert tester.role == AgentRole.TESTER
        assert tester.llm_config == sample_llm_config

    async def test_generate_tests_mock(self, sample_llm_config):
        """Test test generation with mocked LLM."""
        from resoftai.agents.tester import Tester

        tester = Tester(sample_llm_config)

        mock_response = {
            "content": "```python\ndef test_authenticate_user():\n    assert True\n```",
            "usage": {"total_tokens": 200}
        }

        with patch.object(tester.llm, 'generate', new_callable=AsyncMock, return_value=mock_response):
            code = "def authenticate_user(): pass"
            result = await tester.create_tests(code)

        assert "test_files" in result or "tests" in result


@pytest.mark.asyncio
class TestQAReviewer:
    """Test QA reviewer agent."""

    async def test_qa_reviewer_initialization(self, sample_llm_config):
        """Test QA reviewer initialization."""
        from resoftai.agents.qa_reviewer import QAReviewer

        qa = QAReviewer(sample_llm_config)

        assert qa.role == AgentRole.QA_REVIEWER
        assert qa.llm_config == sample_llm_config

    async def test_review_project_mock(self, sample_llm_config):
        """Test project review with mocked LLM."""
        from resoftai.agents.qa_reviewer import QAReviewer

        qa = QAReviewer(sample_llm_config)

        mock_response = {
            "content": "# QA Review\n\n## Findings\n- Code quality: Good\n- Test coverage: 80%",
            "usage": {"total_tokens": 250}
        }

        with patch.object(qa.llm, 'generate', new_callable=AsyncMock, return_value=mock_response):
            artifacts = {"code": "...", "tests": "..."}
            result = await qa.review(artifacts)

        assert "review_report" in result or "findings" in result


class TestAgentCommunication:
    """Test inter-agent communication."""

    def test_agent_message_bus_broadcast(self):
        """Test message broadcasting to all agents."""
        # Placeholder for message bus testing
        pass

    def test_agent_message_routing(self):
        """Test routing messages to specific agents."""
        # Placeholder for message routing testing
        pass

    def test_agent_collaboration(self):
        """Test agents collaborating on a task."""
        # Placeholder for collaboration testing
        pass
