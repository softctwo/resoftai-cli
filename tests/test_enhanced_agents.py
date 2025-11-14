"""Tests for enhanced agents: DevOps, Security, and Performance Engineers."""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from resoftai.core.agent import AgentRole
from resoftai.core.message_bus import MessageBus, Message, MessageType
from resoftai.core.state import ProjectState
from resoftai.llm.base import LLMConfig, ModelProvider
from resoftai.agents.devops_engineer import DevOpsEngineerAgent
from resoftai.agents.security_expert import SecurityExpertAgent
from resoftai.agents.performance_engineer import PerformanceEngineerAgent


@pytest.fixture
def message_bus():
    """Create message bus for testing."""
    return MessageBus()


@pytest.fixture
def project_state():
    """Create project state for testing."""
    return ProjectState(
        name="Test Project",
        description="Build a scalable web application"
    )


@pytest.fixture
def llm_config():
    """Create LLM config for testing."""
    return LLMConfig(
        provider=ModelProvider.DEEPSEEK,
        api_key="test-api-key",
        model_name="deepseek-chat"
    )


class TestDevOpsEngineerAgent:
    """Tests for DevOps Engineer Agent."""

    @pytest.fixture
    def agent(self, message_bus, project_state, llm_config):
        """Create DevOps Engineer agent."""
        agent = DevOpsEngineerAgent(
            role=AgentRole.DEVOPS_ENGINEER,
            message_bus=message_bus,
            project_state=project_state,
            llm_config=llm_config
        )
        # Mock LLM generate method
        agent.llm.generate = AsyncMock(return_value=type('obj', (object,), {
            'content': 'CI/CD pipeline configuration',
            'total_tokens': 100
        })())
        return agent

    def test_agent_initialization(self, agent):
        """Test agent initialization."""
        assert agent.name == "DevOps Engineer"
        assert agent.role == AgentRole.DEVOPS_ENGINEER
        assert len(agent.capabilities) == 4

    def test_agent_capabilities(self, agent):
        """Test agent has required capabilities."""
        capability_names = [cap.name for cap in agent.capabilities]
        assert "design_cicd_pipeline" in capability_names
        assert "infrastructure_as_code" in capability_names
        assert "containerization_strategy" in capability_names
        assert "monitoring_setup" in capability_names

    @pytest.mark.asyncio
    async def test_cicd_request_processing(self, agent):
        """Test CI/CD pipeline design request."""
        message = Message(
            type=MessageType.AGENT_REQUEST,
            sender=AgentRole.PROJECT_MANAGER.value,
            content="Design a CI/CD pipeline for our FastAPI application with automated testing and deployment to AWS"
        )

        response = await agent.process(message)

        assert response is not None
        assert response.type == MessageType.AGENT_RESPONSE
        assert response.sender == AgentRole.DEVOPS_ENGINEER
        assert "CI/CD pipeline configuration" in response.content
        assert response.metadata["capability"] == "cicd_pipeline_design"

    @pytest.mark.asyncio
    async def test_infrastructure_request_processing(self, agent):
        """Test infrastructure as code request."""
        message = Message(
            type=MessageType.AGENT_REQUEST,
            sender=AgentRole.PROJECT_MANAGER.value,
            content="Generate infrastructure code for deploying our application on AWS with load balancer, database, and caching"
        )

        response = await agent.process(message)

        assert response is not None
        assert response.type == MessageType.AGENT_RESPONSE
        assert response.metadata["capability"] == "infrastructure_as_code"

    @pytest.mark.asyncio
    async def test_monitoring_request_processing(self, agent):
        """Test monitoring setup request."""
        message = Message(
            type=MessageType.AGENT_REQUEST,
            sender=AgentRole.PROJECT_MANAGER.value,
            content="Configure monitoring and logging for production application"
        )

        response = await agent.process(message)

        assert response is not None
        assert response.metadata["capability"] == "monitoring_setup"


class TestSecurityExpertAgent:
    """Tests for Security Expert Agent."""

    @pytest.fixture
    def agent(self, message_bus, project_state, llm_config):
        """Create Security Expert agent."""
        agent = SecurityExpertAgent(
            role=AgentRole.SECURITY_EXPERT,
            message_bus=message_bus,
            project_state=project_state,
            llm_config=llm_config
        )
        # Mock LLM generate method
        agent.llm.generate = AsyncMock(return_value=type('obj', (object,), {
            'content': 'Security analysis report',
            'total_tokens': 100
        })())
        return agent

    def test_agent_initialization(self, agent):
        """Test agent initialization."""
        assert agent.name == "Security Expert"
        assert agent.role == AgentRole.SECURITY_EXPERT
        assert len(agent.capabilities) == 4

    def test_agent_capabilities(self, agent):
        """Test agent has required capabilities."""
        capability_names = [cap.name for cap in agent.capabilities]
        assert "security_code_review" in capability_names
        assert "threat_modeling" in capability_names
        assert "compliance_check" in capability_names
        assert "penetration_test_plan" in capability_names

    @pytest.mark.asyncio
    async def test_security_review_processing(self, agent):
        """Test security review request."""
        message = Message(
            type=MessageType.AGENT_REQUEST,
            sender=AgentRole.QUALITY_EXPERT.value,
            content="Perform a security review of the authentication and authorization implementation"
        )

        response = await agent.process(message)

        assert response is not None
        assert response.type == MessageType.AGENT_RESPONSE
        assert response.sender == AgentRole.SECURITY_EXPERT
        assert "Security analysis report" in response.content
        assert response.metadata["capability"] == "security_review"

    @pytest.mark.asyncio
    async def test_compliance_check_processing(self, agent):
        """Test compliance verification request."""
        message = Message(
            type=MessageType.AGENT_REQUEST,
            sender=AgentRole.PROJECT_MANAGER.value,
            content="Verify compliance with GDPR requirements for our application"
        )

        response = await agent.process(message)

        assert response is not None
        assert response.metadata["capability"] == "compliance_check"

    @pytest.mark.asyncio
    async def test_threat_modeling_processing(self, agent):
        """Test threat modeling request."""
        message = Message(
            type=MessageType.AGENT_REQUEST,
            sender=AgentRole.ARCHITECT.value,
            content="Perform threat modeling for our payment processing system"
        )

        response = await agent.process(message)

        assert response is not None
        assert response.metadata["capability"] == "threat_modeling"

    @pytest.mark.asyncio
    async def test_vulnerability_assessment(self, agent):
        """Test vulnerability assessment request."""
        message = Message(
            type=MessageType.AGENT_REQUEST,
            sender=AgentRole.DEVELOPER.value,
            content="Check for security vulnerabilities in the API endpoints"
        )

        response = await agent.process(message)

        assert response is not None
        assert response.sender == AgentRole.SECURITY_EXPERT


class TestPerformanceEngineerAgent:
    """Tests for Performance Engineer Agent."""

    @pytest.fixture
    def agent(self, message_bus, project_state, llm_config):
        """Create Performance Engineer agent."""
        agent = PerformanceEngineerAgent(
            role=AgentRole.PERFORMANCE_ENGINEER,
            message_bus=message_bus,
            project_state=project_state,
            llm_config=llm_config
        )
        # Mock LLM generate method
        agent.llm.generate = AsyncMock(return_value=type('obj', (object,), {
            'content': 'Performance optimization recommendations',
            'total_tokens': 100
        })())
        return agent

    def test_agent_initialization(self, agent):
        """Test agent initialization."""
        assert agent.name == "Performance Engineer"
        assert agent.role == AgentRole.PERFORMANCE_ENGINEER
        assert len(agent.capabilities) == 4

    def test_agent_capabilities(self, agent):
        """Test agent has required capabilities."""
        capability_names = [cap.name for cap in agent.capabilities]
        assert "performance_analysis" in capability_names
        assert "load_testing_plan" in capability_names
        assert "caching_strategy" in capability_names
        assert "database_optimization" in capability_names

    @pytest.mark.asyncio
    async def test_performance_analysis_processing(self, agent):
        """Test performance analysis request."""
        message = Message(
            type=MessageType.AGENT_REQUEST,
            sender=AgentRole.DEVELOPER.value,
            content="Analyze performance bottlenecks in our API endpoints with high response times"
        )

        response = await agent.process(message)

        assert response is not None
        assert response.type == MessageType.AGENT_RESPONSE
        assert response.sender == AgentRole.PERFORMANCE_ENGINEER
        assert "Performance optimization recommendations" in response.content
        assert response.metadata["capability"] == "performance_analysis"

    @pytest.mark.asyncio
    async def test_load_testing_processing(self, agent):
        """Test load testing strategy request."""
        message = Message(
            type=MessageType.AGENT_REQUEST,
            sender=AgentRole.TEST_ENGINEER.value,
            content="Design a load test plan for our e-commerce application handling 10,000 concurrent users"
        )

        response = await agent.process(message)

        assert response is not None
        assert response.metadata["capability"] == "load_testing"

    @pytest.mark.asyncio
    async def test_caching_strategy_processing(self, agent):
        """Test caching strategy request."""
        message = Message(
            type=MessageType.AGENT_REQUEST,
            sender=AgentRole.ARCHITECT.value,
            content="Design a multi-layered caching strategy for frequently accessed product data"
        )

        response = await agent.process(message)

        assert response is not None
        assert response.metadata["capability"] == "caching_strategy"

    @pytest.mark.asyncio
    async def test_database_optimization_processing(self, agent):
        """Test database optimization request."""
        message = Message(
            type=MessageType.AGENT_REQUEST,
            sender=AgentRole.DEVELOPER.value,
            content="Optimize slow database queries in the order processing system"
        )

        response = await agent.process(message)

        assert response is not None
        assert response.metadata["capability"] == "database_optimization"


class TestEnhancedAgentsIntegration:
    """Integration tests for enhanced agents working together."""

    @pytest.mark.asyncio
    async def test_all_agents_can_be_instantiated(self, message_bus, project_state, llm_config):
        """Test all enhanced agents can be instantiated together."""
        devops = DevOpsEngineerAgent(
            role=AgentRole.DEVOPS_ENGINEER,
            message_bus=message_bus,
            project_state=project_state,
            llm_config=llm_config
        )

        security = SecurityExpertAgent(
            role=AgentRole.SECURITY_EXPERT,
            message_bus=message_bus,
            project_state=project_state,
            llm_config=llm_config
        )

        performance = PerformanceEngineerAgent(
            role=AgentRole.PERFORMANCE_ENGINEER,
            message_bus=message_bus,
            project_state=project_state,
            llm_config=llm_config
        )

        assert devops.name == "DevOps Engineer"
        assert security.name == "Security Expert"
        assert performance.name == "Performance Engineer"

    def test_agent_roles_are_unique(self):
        """Test all agent roles are unique and properly defined."""
        assert AgentRole.DEVOPS_ENGINEER.value == "devops_engineer"
        assert AgentRole.SECURITY_EXPERT.value == "security_expert"
        assert AgentRole.PERFORMANCE_ENGINEER.value == "performance_engineer"

        # Test all roles are different
        roles = [
            AgentRole.DEVOPS_ENGINEER,
            AgentRole.SECURITY_EXPERT,
            AgentRole.PERFORMANCE_ENGINEER
        ]
        assert len(roles) == len(set(roles))
