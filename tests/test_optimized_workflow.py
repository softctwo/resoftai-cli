"""Tests for optimized workflow orchestrator."""
import pytest
import asyncio
from pathlib import Path
from datetime import datetime

from resoftai.orchestration.optimized_workflow import (
    OptimizedWorkflowOrchestrator,
    OptimizedWorkflowConfig,
    WorkflowStage,
    ExecutionStrategy,
    RetryConfig,
    CacheConfig,
    CheckpointConfig,
    AgentResultCache,
    WorkflowCheckpoint
)
from resoftai.llm.base import LLMConfig, ModelProvider


@pytest.fixture
def llm_config():
    """Create test LLM configuration."""
    return LLMConfig(
        provider=ModelProvider.DEEPSEEK,
        api_key="test-key",
        model_name="deepseek-chat",
        max_tokens=4000,
        temperature=0.7
    )


@pytest.fixture
def workflow_config(llm_config, tmp_path):
    """Create test workflow configuration."""
    return OptimizedWorkflowConfig(
        project_id=1,
        requirements="Build a simple web application",
        llm_config=llm_config,
        output_directory=str(tmp_path),
        execution_strategy=ExecutionStrategy.SEQUENTIAL,
        max_iterations=1,
        cache_config=CacheConfig(
            enabled=True,
            cache_directory=tmp_path / "cache"
        ),
        checkpoint_config=CheckpointConfig(
            enabled=True,
            checkpoint_directory=tmp_path / "checkpoints"
        )
    )


class TestAgentResultCache:
    """Test agent result caching."""

    def test_cache_creation(self, tmp_path):
        """Test cache initialization."""
        config = CacheConfig(
            enabled=True,
            cache_directory=tmp_path / "cache"
        )
        cache = AgentResultCache(config)

        assert cache.config == config
        assert len(cache.cache) == 0

    def test_cache_set_and_get(self, tmp_path):
        """Test setting and getting cached results."""
        config = CacheConfig(enabled=True)
        cache = AgentResultCache(config)

        agent_role = "developer"
        context = {"task": "write code", "language": "python"}
        result = {"code": "print('hello')"}

        # Set cache
        cache.set(agent_role, context, result)

        # Get cache
        cached_result = cache.get(agent_role, context)
        assert cached_result == result

    def test_cache_miss(self, tmp_path):
        """Test cache miss."""
        config = CacheConfig(enabled=True)
        cache = AgentResultCache(config)

        result = cache.get("developer", {"task": "nonexistent"})
        assert result is None

    def test_cache_disabled(self, tmp_path):
        """Test cache when disabled."""
        config = CacheConfig(enabled=False)
        cache = AgentResultCache(config)

        cache.set("developer", {"task": "test"}, {"result": "test"})
        result = cache.get("developer", {"task": "test"})

        assert result is None

    def test_cache_max_size(self, tmp_path):
        """Test cache size limit."""
        config = CacheConfig(enabled=True, max_cache_size=2)
        cache = AgentResultCache(config)

        # Add 3 items
        for i in range(3):
            cache.set("agent", {"id": i}, {"result": i})

        # Cache should only have 2 items
        assert len(cache.cache) == 2


class TestWorkflowCheckpoint:
    """Test workflow checkpointing."""

    def test_checkpoint_creation(self, tmp_path):
        """Test checkpoint manager initialization."""
        config = CheckpointConfig(
            enabled=True,
            checkpoint_directory=tmp_path / "checkpoints"
        )
        checkpoint = WorkflowCheckpoint(config, project_id=1)

        assert checkpoint.config == config
        assert checkpoint.project_id == 1
        assert checkpoint.checkpoint_dir.exists()

    def test_save_and_load_checkpoint(self, tmp_path, workflow_config):
        """Test saving and loading checkpoints."""
        from resoftai.core.state import ProjectState

        config = CheckpointConfig(
            enabled=True,
            checkpoint_directory=tmp_path / "checkpoints"
        )
        checkpoint = WorkflowCheckpoint(config, project_id=1)

        # Create test state
        project_state = ProjectState(
            name="Test Project",
            description="Test",
            requirements={"raw_text": "test"}
        )

        # Save checkpoint
        success = checkpoint.save(
            current_stage=WorkflowStage.DEVELOPMENT,
            stage_history=[WorkflowStage.REQUIREMENT_ANALYSIS],
            project_state=project_state,
            metadata={"test": "data"}
        )

        assert success

        # Load checkpoint
        loaded = checkpoint.load_latest()
        assert loaded is not None
        assert loaded["current_stage"] == "development"
        assert loaded["project_id"] == 1

    def test_checkpoint_disabled(self, tmp_path):
        """Test checkpoint when disabled."""
        config = CheckpointConfig(enabled=False)
        checkpoint = WorkflowCheckpoint(config, project_id=1)

        from resoftai.core.state import ProjectState
        project_state = ProjectState(name="Test", description="Test")

        success = checkpoint.save(
            WorkflowStage.DEVELOPMENT,
            [],
            project_state,
            {}
        )

        assert not success


class TestOptimizedWorkflowOrchestrator:
    """Test optimized workflow orchestrator."""

    def test_orchestrator_initialization(self, workflow_config):
        """Test orchestrator initialization."""
        orchestrator = OptimizedWorkflowOrchestrator(workflow_config)

        assert orchestrator.config == workflow_config
        assert len(orchestrator.agents) == 7
        assert orchestrator.current_stage == WorkflowStage.INITIALIZATION
        assert isinstance(orchestrator.cache, AgentResultCache)
        assert isinstance(orchestrator.checkpoint, WorkflowCheckpoint)

    def test_get_progress(self, workflow_config):
        """Test progress tracking."""
        orchestrator = OptimizedWorkflowOrchestrator(workflow_config)

        progress = orchestrator.get_progress()

        assert "current_stage" in progress
        assert "progress_percentage" in progress
        assert "stage_history" in progress
        assert "total_tokens" in progress
        assert "cache_stats" in progress

    def test_get_artifacts(self, workflow_config):
        """Test artifact retrieval."""
        orchestrator = OptimizedWorkflowOrchestrator(workflow_config)

        artifacts = orchestrator.get_artifacts()

        assert "requirements_doc" in artifacts
        assert "architecture_doc" in artifacts
        assert "source_code" in artifacts

    @pytest.mark.asyncio
    async def test_cancel_workflow(self, workflow_config):
        """Test workflow cancellation."""
        orchestrator = OptimizedWorkflowOrchestrator(workflow_config)

        await orchestrator.cancel()

        assert orchestrator.current_stage == WorkflowStage.FAILED
        assert "canceled" in orchestrator.errors[0].lower()


class TestRetryLogic:
    """Test retry logic."""

    def test_retry_delay_calculation(self, workflow_config):
        """Test exponential backoff calculation."""
        orchestrator = OptimizedWorkflowOrchestrator(workflow_config)
        retry_config = RetryConfig(
            max_retries=3,
            initial_delay=1.0,
            max_delay=10.0,
            exponential_base=2.0
        )

        # Test delay calculation
        delay0 = orchestrator._calculate_retry_delay(0, retry_config)
        delay1 = orchestrator._calculate_retry_delay(1, retry_config)
        delay2 = orchestrator._calculate_retry_delay(2, retry_config)

        assert delay0 == 1.0  # 1.0 * 2^0
        assert delay1 == 2.0  # 1.0 * 2^1
        assert delay2 == 4.0  # 1.0 * 2^2

    def test_should_retry(self, workflow_config):
        """Test retry decision logic."""
        orchestrator = OptimizedWorkflowOrchestrator(workflow_config)
        retry_config = RetryConfig(
            retry_on_errors=["timeout", "rate_limit"]
        )

        # Should retry
        timeout_error = Exception("Request timeout")
        assert orchestrator._should_retry(timeout_error, retry_config)

        rate_limit_error = Exception("Rate limit exceeded")
        assert orchestrator._should_retry(rate_limit_error, retry_config)

        # Should not retry
        other_error = Exception("Some other error")
        assert not orchestrator._should_retry(other_error, retry_config)


class TestExecutionStrategies:
    """Test different execution strategies."""

    def test_sequential_strategy(self, workflow_config, llm_config, tmp_path):
        """Test sequential execution strategy."""
        config = OptimizedWorkflowConfig(
            project_id=1,
            requirements="Test",
            llm_config=llm_config,
            output_directory=str(tmp_path),
            execution_strategy=ExecutionStrategy.SEQUENTIAL
        )

        orchestrator = OptimizedWorkflowOrchestrator(config)
        assert orchestrator.config.execution_strategy == ExecutionStrategy.SEQUENTIAL

    def test_parallel_strategy(self, workflow_config, llm_config, tmp_path):
        """Test parallel execution strategy."""
        config = OptimizedWorkflowConfig(
            project_id=1,
            requirements="Test",
            llm_config=llm_config,
            output_directory=str(tmp_path),
            execution_strategy=ExecutionStrategy.PARALLEL
        )

        orchestrator = OptimizedWorkflowOrchestrator(config)
        assert orchestrator.config.execution_strategy == ExecutionStrategy.PARALLEL

    def test_adaptive_strategy(self, workflow_config, llm_config, tmp_path):
        """Test adaptive execution strategy."""
        config = OptimizedWorkflowConfig(
            project_id=1,
            requirements="Test",
            llm_config=llm_config,
            output_directory=str(tmp_path),
            execution_strategy=ExecutionStrategy.ADAPTIVE
        )

        orchestrator = OptimizedWorkflowOrchestrator(config)
        assert orchestrator.config.execution_strategy == ExecutionStrategy.ADAPTIVE


class TestWorkflowConfiguration:
    """Test workflow configuration options."""

    def test_skip_ui_design(self, llm_config, tmp_path):
        """Test skipping UI design stage."""
        config = OptimizedWorkflowConfig(
            project_id=1,
            requirements="Test",
            llm_config=llm_config,
            output_directory=str(tmp_path),
            skip_ui_design=True
        )

        assert config.skip_ui_design is True

    def test_timeout_configuration(self, llm_config, tmp_path):
        """Test timeout configuration."""
        config = OptimizedWorkflowConfig(
            project_id=1,
            requirements="Test",
            llm_config=llm_config,
            output_directory=str(tmp_path),
            timeout_per_stage=300
        )

        assert config.timeout_per_stage == 300

    def test_parallel_agents_limit(self, llm_config, tmp_path):
        """Test max parallel agents configuration."""
        config = OptimizedWorkflowConfig(
            project_id=1,
            requirements="Test",
            llm_config=llm_config,
            output_directory=str(tmp_path),
            max_parallel_agents=5
        )

        assert config.max_parallel_agents == 5
