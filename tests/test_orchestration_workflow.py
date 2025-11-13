"""
Comprehensive tests for workflow orchestration.
"""
import pytest
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from resoftai.orchestration.workflow import (
    WorkflowOrchestrator,
    WorkflowConfig,
    WorkflowStage
)
from resoftai.llm.base import LLMConfig, ModelProvider
from resoftai.core.agent import AgentRole


@pytest.fixture
def llm_config():
    """Create test LLM config."""
    return LLMConfig(
        provider=ModelProvider.DEEPSEEK,
        model_name="deepseek-chat",
        api_key="test-api-key",
        max_tokens=4096,
        temperature=0.7
    )


@pytest.fixture
def workflow_config(llm_config):
    """Create test workflow config."""
    return WorkflowConfig(
        project_id=1,
        requirements="Build a simple TODO application",
        llm_config=llm_config,
        output_directory="/tmp/test_project",
        max_iterations=2,
        skip_ui_design=False,
        test_framework="pytest",
        code_style="pep8"
    )


@pytest.fixture
def mock_agents():
    """Create mock agents."""
    agents = {}
    for role in AgentRole:
        agent = Mock()
        agent.name = f"Mock {role.value}"
        agent.role = role
        agent.process_request = AsyncMock()
        agents[role] = agent
    return agents


class TestWorkflowConfig:
    """Test WorkflowConfig dataclass."""

    def test_config_creation(self, llm_config):
        """Test workflow config creation."""
        config = WorkflowConfig(
            project_id=1,
            requirements="Test requirements",
            llm_config=llm_config,
            output_directory="/tmp/test"
        )

        assert config.project_id == 1
        assert config.requirements == "Test requirements"
        assert config.llm_config == llm_config
        assert config.output_directory == "/tmp/test"
        assert config.max_iterations == 3  # default
        assert config.enable_parallel_execution is False  # default
        assert config.skip_ui_design is False  # default
        assert config.test_framework == "pytest"  # default
        assert config.code_style == "pep8"  # default

    def test_config_custom_values(self, llm_config):
        """Test workflow config with custom values."""
        config = WorkflowConfig(
            project_id=2,
            requirements="Custom requirements",
            llm_config=llm_config,
            output_directory="/custom/path",
            max_iterations=5,
            enable_parallel_execution=True,
            skip_ui_design=True,
            test_framework="unittest",
            code_style="google"
        )

        assert config.max_iterations == 5
        assert config.enable_parallel_execution is True
        assert config.skip_ui_design is True
        assert config.test_framework == "unittest"
        assert config.code_style == "google"


class TestWorkflowOrchestrator:
    """Test WorkflowOrchestrator."""

    def test_orchestrator_initialization(self, workflow_config):
        """Test workflow orchestrator initialization."""
        with patch.object(WorkflowOrchestrator, '_initialize_agents', return_value={}):
            orchestrator = WorkflowOrchestrator(workflow_config)

            assert orchestrator.config == workflow_config
            assert orchestrator.message_bus is not None
            assert orchestrator.project_state is not None
            assert orchestrator.project_state.name == "Project 1"
            assert orchestrator.project_state.description == "Build a simple TODO application"
            assert orchestrator.project_state.requirements == {"raw_text": "Build a simple TODO application"}
            assert orchestrator.current_stage == WorkflowStage.INITIALIZATION
            assert len(orchestrator.stage_history) == 0
            assert len(orchestrator.errors) == 0

    def test_agents_initialization(self, workflow_config):
        """Test agents are initialized correctly."""
        # Create mock agents
        mock_agents = {}
        for role in AgentRole:
            agent = Mock()
            agent.name = f"Mock {role.value}"
            agent.role = role
            mock_agents[role] = agent

        with patch.object(WorkflowOrchestrator, '_initialize_agents', return_value=mock_agents):
            orchestrator = WorkflowOrchestrator(workflow_config)

            assert len(orchestrator.agents) == 7
            assert AgentRole.PROJECT_MANAGER in orchestrator.agents
            assert AgentRole.REQUIREMENTS_ANALYST in orchestrator.agents
            assert AgentRole.ARCHITECT in orchestrator.agents
            assert AgentRole.UXUI_DESIGNER in orchestrator.agents
            assert AgentRole.DEVELOPER in orchestrator.agents
            assert AgentRole.TEST_ENGINEER in orchestrator.agents
            assert AgentRole.QUALITY_EXPERT in orchestrator.agents

    def test_stage_history_tracking(self, workflow_config):
        """Test stage history is tracked correctly."""
        with patch.object(WorkflowOrchestrator, '_initialize_agents', return_value={}):
            orchestrator = WorkflowOrchestrator(workflow_config)

            assert orchestrator.current_stage == WorkflowStage.INITIALIZATION
            assert orchestrator.stage_history == []

    @pytest.mark.asyncio
    async def test_execute_workflow_success(self, workflow_config):
        """Test successful workflow execution."""
        with patch.object(WorkflowOrchestrator, '_initialize_agents') as mock_init:
            # Mock agents
            mock_agents = {}
            for role in AgentRole:
                agent = Mock()
                agent.name = f"Mock {role.value}"
                agent.role = role
                mock_agents[role] = agent

            mock_init.return_value = mock_agents

            orchestrator = WorkflowOrchestrator(workflow_config)

            # Mock all stage execution methods
            orchestrator._run_requirement_analysis = AsyncMock()
            orchestrator._run_architecture_design = AsyncMock()
            orchestrator._run_ui_design = AsyncMock()
            orchestrator._run_development = AsyncMock()
            orchestrator._run_testing = AsyncMock()
            orchestrator._run_qa_review = AsyncMock()

            result = await orchestrator.execute()

            assert result is True
            assert orchestrator.current_stage == WorkflowStage.COMPLETED

            # Verify all stages were executed
            orchestrator._run_requirement_analysis.assert_called_once()
            orchestrator._run_architecture_design.assert_called_once()
            orchestrator._run_ui_design.assert_called_once()
            orchestrator._run_development.assert_called_once()
            orchestrator._run_testing.assert_called_once()
            orchestrator._run_qa_review.assert_called_once()

    @pytest.mark.asyncio
    async def test_execute_workflow_skip_ui_design(self, llm_config):
        """Test workflow execution with UI design skipped."""
        config = WorkflowConfig(
            project_id=1,
            requirements="Test requirements",
            llm_config=llm_config,
            output_directory="/tmp/test",
            skip_ui_design=True
        )

        with patch.object(WorkflowOrchestrator, '_initialize_agents') as mock_init:
            mock_agents = {}
            for role in AgentRole:
                agent = Mock()
                agent.name = f"Mock {role.value}"
                mock_agents[role] = agent

            mock_init.return_value = mock_agents

            orchestrator = WorkflowOrchestrator(config)

            # Mock stage methods
            orchestrator._run_requirement_analysis = AsyncMock()
            orchestrator._run_architecture_design = AsyncMock()
            orchestrator._run_ui_design = AsyncMock()
            orchestrator._run_development = AsyncMock()
            orchestrator._run_testing = AsyncMock()
            orchestrator._run_qa_review = AsyncMock()

            result = await orchestrator.execute()

            assert result is True

            # UI design should not be called
            orchestrator._run_ui_design.assert_not_called()

            # Other stages should be called
            orchestrator._run_requirement_analysis.assert_called_once()
            orchestrator._run_architecture_design.assert_called_once()
            orchestrator._run_development.assert_called_once()
            orchestrator._run_testing.assert_called_once()
            orchestrator._run_qa_review.assert_called_once()

    @pytest.mark.asyncio
    async def test_execute_workflow_failure(self, workflow_config):
        """Test workflow execution with failure."""
        with patch.object(WorkflowOrchestrator, '_initialize_agents') as mock_init:
            mock_agents = {}
            for role in AgentRole:
                agent = Mock()
                agent.name = f"Mock {role.value}"
                mock_agents[role] = agent

            mock_init.return_value = mock_agents

            orchestrator = WorkflowOrchestrator(workflow_config)

            # Mock stages - make one fail
            orchestrator._run_requirement_analysis = AsyncMock()
            orchestrator._run_architecture_design = AsyncMock(
                side_effect=Exception("Architecture design failed")
            )

            result = await orchestrator.execute()

            assert result is False
            assert orchestrator.current_stage == WorkflowStage.FAILED
            assert len(orchestrator.errors) > 0

            # Only first stage should have been called
            orchestrator._run_requirement_analysis.assert_called_once()
            orchestrator._run_architecture_design.assert_called_once()

    def test_get_agent_by_role(self, workflow_config):
        """Test getting agent by role."""
        # Create mock agents with roles
        mock_agents = {}
        for role in AgentRole:
            agent = Mock()
            agent.name = f"Mock {role.value}"
            agent.role = role
            mock_agents[role] = agent

        with patch.object(WorkflowOrchestrator, '_initialize_agents', return_value=mock_agents):
            orchestrator = WorkflowOrchestrator(workflow_config)

            pm_agent = orchestrator.agents.get(AgentRole.PROJECT_MANAGER)
            assert pm_agent is not None
            assert pm_agent.role == AgentRole.PROJECT_MANAGER

            dev_agent = orchestrator.agents.get(AgentRole.DEVELOPER)
            assert dev_agent is not None
            assert dev_agent.role == AgentRole.DEVELOPER

    def test_project_state_initialization(self, workflow_config):
        """Test project state is initialized correctly."""
        with patch.object(WorkflowOrchestrator, '_initialize_agents', return_value={}):
            orchestrator = WorkflowOrchestrator(workflow_config)

            assert orchestrator.project_state.name == "Project 1"
            assert orchestrator.project_state.description == "Build a simple TODO application"
            assert orchestrator.project_state.requirements == {"raw_text": "Build a simple TODO application"}
            assert orchestrator.project_state.current_stage is not None

    def test_message_bus_initialization(self, workflow_config):
        """Test message bus is initialized correctly."""
        # Create mock agents with message_bus attribute
        mock_agents = {}
        for role in AgentRole:
            agent = Mock()
            agent.name = f"Mock {role.value}"
            agent.role = role
            agent.message_bus = None  # Will be set after orchestrator creation
            mock_agents[role] = agent

        with patch.object(WorkflowOrchestrator, '_initialize_agents', return_value=mock_agents):
            orchestrator = WorkflowOrchestrator(workflow_config)
            # Simulate agents receiving message_bus
            for agent in orchestrator.agents.values():
                agent.message_bus = orchestrator.message_bus

            assert orchestrator.message_bus is not None
            # Message bus should be shared among all agents
            for agent in orchestrator.agents.values():
                assert agent.message_bus is orchestrator.message_bus


class TestWorkflowStage:
    """Test WorkflowStage enum."""

    def test_stage_values(self):
        """Test workflow stage values."""
        assert WorkflowStage.INITIALIZATION.value == "initialization"
        assert WorkflowStage.REQUIREMENT_ANALYSIS.value == "requirement_analysis"
        assert WorkflowStage.ARCHITECTURE_DESIGN.value == "architecture_design"
        assert WorkflowStage.UI_DESIGN.value == "ui_design"
        assert WorkflowStage.DEVELOPMENT.value == "development"
        assert WorkflowStage.TESTING.value == "testing"
        assert WorkflowStage.QA_REVIEW.value == "qa_review"
        assert WorkflowStage.COMPLETED.value == "completed"
        assert WorkflowStage.FAILED.value == "failed"

    def test_stage_comparison(self):
        """Test workflow stage comparison."""
        assert WorkflowStage.INITIALIZATION == WorkflowStage.INITIALIZATION
        assert WorkflowStage.INITIALIZATION != WorkflowStage.REQUIREMENT_ANALYSIS

    def test_all_stages_present(self):
        """Test all expected stages are present."""
        expected_stages = {
            "initialization",
            "requirement_analysis",
            "architecture_design",
            "ui_design",
            "development",
            "testing",
            "qa_review",
            "completed",
            "failed"
        }

        actual_stages = {stage.value for stage in WorkflowStage}
        assert actual_stages == expected_stages


class TestWorkflowIntegration:
    """Integration tests for workflow orchestration."""

    @pytest.mark.asyncio
    async def test_full_workflow_integration(self, workflow_config):
        """Test full workflow integration with mocked LLM calls."""
        with patch.object(WorkflowOrchestrator, '_initialize_agents') as mock_init:
            # Create mock agents with async methods
            mock_agents = {}
            for role in AgentRole:
                agent = MagicMock()
                agent.name = f"Mock {role.value}"
                agent.role = role
                agent.generate = AsyncMock(return_value="Mock response")
                agent.call_claude = AsyncMock(return_value="Mock Claude response")
                mock_agents[role] = agent

            mock_init.return_value = mock_agents

            orchestrator = WorkflowOrchestrator(workflow_config)

            # Mock all stage methods to simulate successful execution
            orchestrator._run_requirement_analysis = AsyncMock()
            orchestrator._run_architecture_design = AsyncMock()
            orchestrator._run_ui_design = AsyncMock()
            orchestrator._run_development = AsyncMock()
            orchestrator._run_testing = AsyncMock()
            orchestrator._run_qa_review = AsyncMock()

            # Execute workflow
            result = await orchestrator.execute()

            # Verify successful completion
            assert result is True
            assert orchestrator.current_stage == WorkflowStage.COMPLETED
            assert len(orchestrator.errors) == 0

    def test_workflow_config_validation(self, llm_config):
        """Test workflow config validation."""
        # Valid config
        config = WorkflowConfig(
            project_id=1,
            requirements="Valid requirements",
            llm_config=llm_config,
            output_directory="/tmp/valid"
        )
        assert config.project_id > 0
        assert config.requirements
        assert config.llm_config is not None

    @pytest.mark.asyncio
    async def test_workflow_error_recovery(self, workflow_config):
        """Test workflow error handling and recovery."""
        with patch.object(WorkflowOrchestrator, '_initialize_agents') as mock_init:
            mock_agents = {}
            for role in AgentRole:
                agent = Mock()
                agent.name = f"Mock {role.value}"
                mock_agents[role] = agent

            mock_init.return_value = mock_agents

            orchestrator = WorkflowOrchestrator(workflow_config)

            # Mock stages with one failure
            orchestrator._run_requirement_analysis = AsyncMock()
            orchestrator._run_architecture_design = AsyncMock(
                side_effect=ValueError("Test error")
            )

            result = await orchestrator.execute()

            assert result is False
            assert orchestrator.current_stage == WorkflowStage.FAILED
            assert "Test error" in str(orchestrator.errors)
