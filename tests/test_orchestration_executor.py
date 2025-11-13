"""
Comprehensive tests for project executor.
"""
import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from datetime import datetime
from pathlib import Path

from resoftai.orchestration.executor import ProjectExecutor
from resoftai.models.project import Project
from resoftai.models.llm_config import LLMConfigModel


@pytest.fixture
def mock_project():
    """Create mock project."""
    project = Mock(spec=Project)
    project.id = 1
    project.name = "Test Project"
    project.requirements = "Build a test application"
    project.status = "pending"
    project.progress = 0
    project.user_id = 1
    project.created_at = datetime.now()
    return project


@pytest.fixture
def mock_llm_config():
    """Create mock LLM config."""
    config = Mock(spec=LLMConfigModel)
    config.id = 1
    config.provider = "deepseek"
    config.model = "deepseek-chat"
    config.api_key = "test-api-key"
    config.api_base = None
    config.max_tokens = 4096
    config.temperature = 0.7
    config.top_p = 0.9
    config.is_default = True
    return config


@pytest.fixture
def mock_db():
    """Create mock database session."""
    db = AsyncMock()
    db.commit = AsyncMock()
    db.refresh = AsyncMock()
    return db


class TestProjectExecutor:
    """Test ProjectExecutor class."""

    def test_executor_initialization(self, mock_project, mock_llm_config, mock_db):
        """Test project executor initialization."""
        executor = ProjectExecutor(mock_project, mock_llm_config, mock_db)

        assert executor.project == mock_project
        assert executor.llm_config_model == mock_llm_config
        assert executor.db == mock_db
        assert executor.llm_config is not None
        assert executor.workflow_config is not None
        assert executor.orchestrator is None
        assert executor.execution_task is None
        assert executor.is_running is False
        assert executor.start_time is None
        assert executor.end_time is None

    def test_llm_config_conversion(self, mock_project, mock_llm_config, mock_db):
        """Test LLM config model conversion."""
        executor = ProjectExecutor(mock_project, mock_llm_config, mock_db)

        assert executor.llm_config.api_key == "test-api-key"
        assert executor.llm_config.model_name == "deepseek-chat"
        assert executor.llm_config.max_tokens == 4096
        assert executor.llm_config.temperature == 0.7
        assert executor.llm_config.top_p == 0.9

    def test_workflow_config_creation(self, mock_project, mock_llm_config, mock_db):
        """Test workflow config is created correctly."""
        executor = ProjectExecutor(mock_project, mock_llm_config, mock_db)

        assert executor.workflow_config.project_id == 1
        assert executor.workflow_config.requirements == "Build a test application"
        assert executor.workflow_config.llm_config == executor.llm_config
        assert "project_1" in executor.workflow_config.output_directory

    def test_output_directory_creation(self, mock_project, mock_llm_config, mock_db, tmp_path):
        """Test output directory is created."""
        with patch('resoftai.orchestration.executor.settings') as mock_settings:
            mock_settings.workspace_dir = str(tmp_path)

            executor = ProjectExecutor(mock_project, mock_llm_config, mock_db)

            output_path = Path(executor.workflow_config.output_directory)
            assert output_path.exists()
            assert output_path.is_dir()
            assert output_path.name == "project_1"

    @pytest.mark.asyncio
    async def test_start_execution(self, mock_project, mock_llm_config, mock_db):
        """Test starting project execution."""
        with patch('resoftai.orchestration.executor.get_active_llm_config', new_callable=AsyncMock) as mock_get_config:
            mock_get_config.return_value = mock_llm_config

            with patch('resoftai.orchestration.executor.update_project', new_callable=AsyncMock):
                with patch('resoftai.orchestration.executor.WorkflowOrchestrator._initialize_agents', return_value={}):
                    with patch.object(ProjectExecutor, '_execute_workflow', new_callable=AsyncMock):
                        executor = await ProjectExecutor.start_execution(mock_project, mock_db)

                        assert executor is not None
                        assert executor.project == mock_project
                        assert executor.is_running is True
                        assert ProjectExecutor._running_executors.get(1) is not None

    @pytest.mark.asyncio
    async def test_start_execution_already_running(self, mock_project, mock_llm_config, mock_db):
        """Test error when project is already running."""
        # Clear any existing executors
        ProjectExecutor._running_executors.clear()

        with patch('resoftai.orchestration.executor.get_active_llm_config', new_callable=AsyncMock) as mock_get_config:
            mock_get_config.return_value = mock_llm_config

            with patch('resoftai.orchestration.executor.update_project', new_callable=AsyncMock):
                with patch('resoftai.orchestration.executor.WorkflowOrchestrator._initialize_agents', return_value={}):
                    with patch.object(ProjectExecutor, '_execute_workflow', new_callable=AsyncMock):
                        # Start first execution
                        executor1 = await ProjectExecutor.start_execution(mock_project, mock_db)
                        assert executor1 is not None

                        # Try to start again - should raise error
                        with pytest.raises(ValueError, match="already running"):
                            await ProjectExecutor.start_execution(mock_project, mock_db)

                        # Cleanup
                        ProjectExecutor._running_executors.clear()

    @pytest.mark.asyncio
    async def test_stop_execution(self, mock_project, mock_llm_config, mock_db):
        """Test stopping project execution."""
        executor = ProjectExecutor(mock_project, mock_llm_config, mock_db)
        executor.is_running = True
        executor.start_time = datetime.now()

        # Mock execution task
        mock_task = Mock(spec=asyncio.Task)
        mock_task.cancel = Mock()
        mock_task.cancelled = Mock(return_value=True)

        # Make awaiting the task raise CancelledError
        async def mock_await():
            raise asyncio.CancelledError()
        mock_task.__await__ = lambda self: mock_await().__await__()

        executor.execution_task = mock_task

        # Mock orchestrator
        mock_orchestrator = Mock()
        mock_orchestrator.cancel = AsyncMock()
        executor.orchestrator = mock_orchestrator

        # Add to running executors
        ProjectExecutor._running_executors[1] = executor

        with patch('resoftai.orchestration.executor.update_project', new_callable=AsyncMock):
            with patch('resoftai.orchestration.executor.emit_project_progress', new_callable=AsyncMock):
                await executor.stop()

                assert executor.is_running is False
                assert executor.end_time is not None
                mock_task.cancel.assert_called_once()

                # Cleanup
                ProjectExecutor._running_executors.clear()

    @pytest.mark.asyncio
    async def test_get_progress(self, mock_project, mock_llm_config, mock_db):
        """Test getting execution progress."""
        executor = ProjectExecutor(mock_project, mock_llm_config, mock_db)
        executor.is_running = True
        executor.start_time = datetime.now()

        progress = executor.get_progress()

        assert progress is not None
        assert "percentage" in progress or isinstance(progress, dict)

    @pytest.mark.asyncio
    async def test_get_executor(self, mock_project, mock_llm_config, mock_db):
        """Test getting running executor."""
        # Clear executors
        ProjectExecutor._running_executors.clear()

        executor = ProjectExecutor(mock_project, mock_llm_config, mock_db)
        ProjectExecutor._running_executors[1] = executor

        result = ProjectExecutor.get_executor(1)
        assert result == executor

        result_none = ProjectExecutor.get_executor(999)
        assert result_none is None

        # Cleanup
        ProjectExecutor._running_executors.clear()

    @pytest.mark.asyncio
    async def test_execute_workflow_success(self, mock_project, mock_llm_config, mock_db):
        """Test successful workflow execution."""
        executor = ProjectExecutor(mock_project, mock_llm_config, mock_db)

        # Mock orchestrator
        mock_orchestrator = Mock()
        mock_orchestrator.execute = AsyncMock(return_value=True)

        with patch('resoftai.orchestration.executor.WorkflowOrchestrator', return_value=mock_orchestrator):
            with patch('resoftai.orchestration.executor.update_project', new_callable=AsyncMock):
                with patch('resoftai.orchestration.executor.emit_project_progress', new_callable=AsyncMock):
                    await executor._execute_workflow()

                    assert executor.orchestrator == mock_orchestrator
                    mock_orchestrator.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_execute_workflow_failure(self, mock_project, mock_llm_config, mock_db):
        """Test workflow execution failure."""
        executor = ProjectExecutor(mock_project, mock_llm_config, mock_db)

        # Mock orchestrator that fails
        mock_orchestrator = Mock()
        mock_orchestrator.execute = AsyncMock(return_value=False)
        mock_orchestrator.errors = ["Test error"]

        with patch('resoftai.orchestration.executor.WorkflowOrchestrator', return_value=mock_orchestrator):
            with patch('resoftai.orchestration.executor.update_project', new_callable=AsyncMock):
                with patch('resoftai.orchestration.executor.emit_project_progress', new_callable=AsyncMock):
                    await executor._execute_workflow()

                    mock_orchestrator.execute.assert_called_once()

    def test_class_level_executor_registry(self):
        """Test class-level executor registry."""
        # Clear registry
        ProjectExecutor._running_executors.clear()

        assert len(ProjectExecutor._running_executors) == 0
        assert ProjectExecutor.get_executor(1) is None

    @pytest.mark.asyncio
    async def test_multiple_executors(self, mock_llm_config, mock_db):
        """Test multiple project executors."""
        # Clear registry
        ProjectExecutor._running_executors.clear()

        # Create multiple projects
        project1 = Mock(spec=Project)
        project1.id = 1
        project1.requirements = "Project 1"

        project2 = Mock(spec=Project)
        project2.id = 2
        project2.requirements = "Project 2"

        executor1 = ProjectExecutor(project1, mock_llm_config, mock_db)
        executor2 = ProjectExecutor(project2, mock_llm_config, mock_db)

        ProjectExecutor._running_executors[1] = executor1
        ProjectExecutor._running_executors[2] = executor2

        assert len(ProjectExecutor._running_executors) == 2
        assert ProjectExecutor.get_executor(1) == executor1
        assert ProjectExecutor.get_executor(2) == executor2

        # Cleanup
        ProjectExecutor._running_executors.clear()

    def test_execution_timing(self, mock_project, mock_llm_config, mock_db):
        """Test execution timing tracking."""
        executor = ProjectExecutor(mock_project, mock_llm_config, mock_db)

        assert executor.start_time is None
        assert executor.end_time is None

        # Simulate start
        executor.start_time = datetime.now()
        assert executor.start_time is not None

        # Simulate end
        executor.end_time = datetime.now()
        assert executor.end_time is not None
        assert executor.end_time >= executor.start_time


class TestProjectExecutorIntegration:
    """Integration tests for project executor."""

    @pytest.mark.asyncio
    async def test_full_execution_flow(self, mock_project, mock_llm_config, mock_db, tmp_path):
        """Test full execution flow."""
        with patch('resoftai.orchestration.executor.settings') as mock_settings:
            mock_settings.workspace_dir = str(tmp_path)

            with patch('resoftai.orchestration.executor.get_active_llm_config', new_callable=AsyncMock) as mock_get_config:
                mock_get_config.return_value = mock_llm_config

                with patch('resoftai.orchestration.executor.update_project', new_callable=AsyncMock):
                    with patch('resoftai.orchestration.executor.WorkflowOrchestrator') as mock_workflow_class:
                        mock_orchestrator = Mock()
                        mock_orchestrator.execute = AsyncMock(return_value=True)
                        mock_workflow_class.return_value = mock_orchestrator

                        with patch('resoftai.orchestration.executor.emit_project_progress', new_callable=AsyncMock):
                            # Start execution
                            executor = await ProjectExecutor.start_execution(mock_project, mock_db)

                            assert executor.is_running is True
                            assert executor.project.id in ProjectExecutor._running_executors

                            # Wait a bit for async task
                            await asyncio.sleep(0.1)

                            # Cleanup
                            ProjectExecutor._running_executors.clear()

    @pytest.mark.asyncio
    async def test_execution_with_real_paths(self, mock_project, mock_llm_config, mock_db, tmp_path):
        """Test execution creates real directory structure."""
        with patch('resoftai.orchestration.executor.settings') as mock_settings:
            mock_settings.workspace_dir = str(tmp_path)

            executor = ProjectExecutor(mock_project, mock_llm_config, mock_db)

            # Check directory was created
            output_path = Path(executor.workflow_config.output_directory)
            assert output_path.exists()
            assert output_path.is_dir()
            assert output_path.parent == tmp_path
