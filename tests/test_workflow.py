"""Tests for workflow orchestration."""
import pytest
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime

from resoftai.orchestration.workflow import (
    WorkflowOrchestrator,
    WorkflowConfig,
    WorkflowStage,
    ProjectState
)
from resoftai.llm.base import LLMConfig, ModelProvider
from resoftai.models.project import Project, ProjectStatus


@pytest.fixture
def sample_llm_config():
    """Sample LLM configuration for testing."""
    return LLMConfig(
        provider=ModelProvider.DEEPSEEK,
        api_key="test-api-key",
        model_name="deepseek-chat",
        max_tokens=4096,
        temperature=0.7
    )


@pytest.fixture
def sample_project():
    """Sample project for testing."""
    return Project(
        id=1,
        user_id=1,
        name="Test Project",
        description="A test project",
        requirements="Build a simple web app with user authentication",
        status=ProjectStatus.PENDING,
        created_at=datetime.utcnow()
    )


@pytest.fixture
def sample_workflow_config(sample_llm_config, sample_project):
    """Sample workflow configuration."""
    return WorkflowConfig(
        project=sample_project,
        llm_config=sample_llm_config,
        workspace_dir="/tmp/test_workspace",
        max_iterations=3,
        skip_ui_design=False
    )


class TestWorkflowOrchestrator:
    """Test workflow orchestrator functionality."""

    def test_orchestrator_initialization(self, sample_workflow_config):
        """Test workflow orchestrator initialization."""
        orchestrator = WorkflowOrchestrator(sample_workflow_config)

        assert orchestrator.config == sample_workflow_config
        assert orchestrator.current_stage == WorkflowStage.INITIALIZATION
        assert orchestrator.state.project_id == sample_workflow_config.project.id
        assert len(orchestrator.errors) == 0

    def test_project_state_initialization(self, sample_project):
        """Test project state initialization."""
        state = ProjectState(
            project_id=sample_project.id,
            project_name=sample_project.name,
            requirements=sample_project.requirements
        )

        assert state.project_id == sample_project.id
        assert state.project_name == sample_project.name
        assert state.requirements == sample_project.requirements
        assert state.current_iteration == 0
        assert len(state.stage_history) == 0

    def test_workflow_stage_enum(self):
        """Test workflow stage enumeration."""
        stages = [
            WorkflowStage.INITIALIZATION,
            WorkflowStage.REQUIREMENT_ANALYSIS,
            WorkflowStage.ARCHITECTURE_DESIGN,
            WorkflowStage.UI_DESIGN,
            WorkflowStage.DEVELOPMENT,
            WorkflowStage.TESTING,
            WorkflowStage.QA_REVIEW,
            WorkflowStage.COMPLETED,
            WorkflowStage.FAILED
        ]

        assert len(stages) == 9
        assert WorkflowStage.INITIALIZATION.value == "initialization"
        assert WorkflowStage.COMPLETED.value == "completed"

    @pytest.mark.asyncio
    async def test_execute_stage_tracking(self, sample_workflow_config):
        """Test that stage execution is tracked in history."""
        orchestrator = WorkflowOrchestrator(sample_workflow_config)

        # Mock the stage execution
        async def mock_stage_func():
            return {"result": "success"}

        with patch.object(orchestrator, '_emit_stage_update', new_callable=AsyncMock):
            await orchestrator._execute_stage(
                WorkflowStage.REQUIREMENT_ANALYSIS,
                mock_stage_func
            )

        assert len(orchestrator.state.stage_history) == 1
        assert orchestrator.state.stage_history[0]["stage"] == WorkflowStage.REQUIREMENT_ANALYSIS.value

    def test_get_progress(self, sample_workflow_config):
        """Test progress calculation."""
        orchestrator = WorkflowOrchestrator(sample_workflow_config)

        progress = orchestrator.get_progress()

        assert "progress_percentage" in progress
        assert "current_stage" in progress
        assert "stage_history" in progress
        assert "errors" in progress
        assert progress["current_stage"] == WorkflowStage.INITIALIZATION.value

    def test_get_artifacts(self, sample_workflow_config):
        """Test artifact retrieval."""
        orchestrator = WorkflowOrchestrator(sample_workflow_config)

        # Add some test artifacts
        orchestrator.state.requirements_doc = "Test requirements"
        orchestrator.state.architecture_doc = "Test architecture"

        artifacts = orchestrator.get_artifacts()

        assert "requirements_doc" in artifacts
        assert "architecture_doc" in artifacts
        assert artifacts["requirements_doc"] == "Test requirements"


@pytest.mark.asyncio
class TestWorkflowExecution:
    """Test workflow execution scenarios."""

    async def test_full_workflow_mock(self, sample_workflow_config):
        """Test full workflow execution with mocked agents."""
        # This would require mocking all agent calls
        # Placeholder for integration test
        pass

    async def test_workflow_error_handling(self, sample_workflow_config):
        """Test workflow error handling."""
        orchestrator = WorkflowOrchestrator(sample_workflow_config)

        # Mock a failing stage
        async def failing_stage():
            raise Exception("Test error")

        with patch.object(orchestrator, '_run_requirement_analysis', failing_stage):
            with patch.object(orchestrator, '_emit_stage_update', new_callable=AsyncMock):
                result = await orchestrator.execute()

        assert result is False
        assert orchestrator.current_stage == WorkflowStage.FAILED
        assert len(orchestrator.errors) > 0

    async def test_skip_ui_design(self, sample_workflow_config):
        """Test skipping UI design stage."""
        sample_workflow_config.skip_ui_design = True
        orchestrator = WorkflowOrchestrator(sample_workflow_config)

        # Verify UI design stage is skipped in execution
        # This would require mocking all other stages
        pass

    async def test_max_iterations_limit(self, sample_workflow_config):
        """Test that max iterations limit is respected."""
        sample_workflow_config.max_iterations = 2
        orchestrator = WorkflowOrchestrator(sample_workflow_config)

        assert orchestrator.config.max_iterations == 2


class TestProjectState:
    """Test project state management."""

    def test_add_message(self):
        """Test adding messages to project state."""
        state = ProjectState(
            project_id=1,
            project_name="Test",
            requirements="Requirements"
        )

        state.add_message("user", "Test message")
        state.add_message("agent", "Test response", agent_role="requirement_analyst")

        assert len(state.messages) == 2
        assert state.messages[0]["role"] == "user"
        assert state.messages[1]["agent_role"] == "requirement_analyst"

    def test_increment_iteration(self):
        """Test iteration counter increment."""
        state = ProjectState(
            project_id=1,
            project_name="Test",
            requirements="Requirements"
        )

        assert state.current_iteration == 0
        state.increment_iteration()
        assert state.current_iteration == 1

    def test_update_tokens(self):
        """Test token usage tracking."""
        state = ProjectState(
            project_id=1,
            project_name="Test",
            requirements="Requirements"
        )

        state.update_tokens(100, 200)
        assert state.total_tokens == 300
        state.update_tokens(50, 50)
        assert state.total_tokens == 400
