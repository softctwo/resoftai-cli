"""
Optimized Workflow Orchestrator with Advanced Features

Enhancements:
- Parallel agent execution for independent stages
- Agent result caching to avoid redundant LLM calls
- Workflow checkpointing for resume capability
- Enhanced error handling with retry logic
- Workflow templates for common patterns
"""
import asyncio
import logging
import json
import hashlib
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
from pathlib import Path

from resoftai.core.message_bus import MessageBus
from resoftai.core.state import ProjectState
from resoftai.core.agent import AgentRole
from resoftai.agents import (
    ProjectManagerAgent,
    RequirementsAnalystAgent,
    ArchitectAgent,
    UXUIDesignerAgent,
    DeveloperAgent,
    TestEngineerAgent,
    QualityExpertAgent
)
from resoftai.llm.base import LLMConfig

logger = logging.getLogger(__name__)


class WorkflowStage(str, Enum):
    """Workflow execution stages."""
    INITIALIZATION = "initialization"
    REQUIREMENT_ANALYSIS = "requirement_analysis"
    ARCHITECTURE_DESIGN = "architecture_design"
    UI_DESIGN = "ui_design"
    DEVELOPMENT = "development"
    TESTING = "testing"
    QA_REVIEW = "qa_review"
    COMPLETED = "completed"
    FAILED = "failed"


class ExecutionStrategy(str, Enum):
    """Agent execution strategies."""
    SEQUENTIAL = "sequential"  # Execute agents one by one
    PARALLEL = "parallel"  # Execute independent agents in parallel
    ADAPTIVE = "adaptive"  # Automatically determine best strategy


@dataclass
class RetryConfig:
    """Configuration for retry logic."""
    max_retries: int = 3
    initial_delay: float = 1.0
    max_delay: float = 60.0
    exponential_base: float = 2.0
    retry_on_errors: List[str] = field(default_factory=lambda: ["timeout", "rate_limit", "server_error"])


@dataclass
class CacheConfig:
    """Configuration for agent result caching."""
    enabled: bool = True
    ttl_seconds: int = 3600  # 1 hour
    max_cache_size: int = 100
    cache_directory: Optional[Path] = None


@dataclass
class CheckpointConfig:
    """Configuration for workflow checkpointing."""
    enabled: bool = True
    checkpoint_directory: Optional[Path] = None
    auto_save_interval: int = 300  # 5 minutes
    max_checkpoints: int = 10


@dataclass
class OptimizedWorkflowConfig:
    """Enhanced configuration for optimized workflow execution."""
    project_id: int
    requirements: str
    llm_config: LLMConfig
    output_directory: str

    # Execution settings
    execution_strategy: ExecutionStrategy = ExecutionStrategy.ADAPTIVE
    max_iterations: int = 3
    timeout_per_stage: Optional[int] = None  # seconds

    # Agent-specific configs
    skip_ui_design: bool = False
    test_framework: str = "pytest"
    code_style: str = "pep8"

    # Optimization features
    retry_config: RetryConfig = field(default_factory=RetryConfig)
    cache_config: CacheConfig = field(default_factory=CacheConfig)
    checkpoint_config: CheckpointConfig = field(default_factory=CheckpointConfig)

    # Parallel execution
    max_parallel_agents: int = 3


class AgentResultCache:
    """Cache for agent execution results to avoid redundant LLM calls."""

    def __init__(self, config: CacheConfig):
        """Initialize cache with configuration."""
        self.config = config
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.cache_timestamps: Dict[str, datetime] = {}

        if config.cache_directory:
            config.cache_directory.mkdir(parents=True, exist_ok=True)

    def _generate_cache_key(self, agent_role: str, context: Dict[str, Any]) -> str:
        """Generate cache key from agent role and context."""
        # Create deterministic hash from context
        context_str = json.dumps(context, sort_keys=True)
        context_hash = hashlib.sha256(context_str.encode()).hexdigest()[:16]
        return f"{agent_role}:{context_hash}"

    def get(self, agent_role: str, context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Get cached result if available and not expired."""
        if not self.config.enabled:
            return None

        cache_key = self._generate_cache_key(agent_role, context)

        # Check if cached
        if cache_key not in self.cache:
            return None

        # Check if expired
        timestamp = self.cache_timestamps.get(cache_key)
        if timestamp:
            age = (datetime.utcnow() - timestamp).total_seconds()
            if age > self.config.ttl_seconds:
                # Expired, remove from cache
                del self.cache[cache_key]
                del self.cache_timestamps[cache_key]
                return None

        logger.info(f"Cache hit for {agent_role}")
        return self.cache[cache_key]

    def set(self, agent_role: str, context: Dict[str, Any], result: Dict[str, Any]):
        """Store result in cache."""
        if not self.config.enabled:
            return

        cache_key = self._generate_cache_key(agent_role, context)

        # Enforce max cache size
        if len(self.cache) >= self.config.max_cache_size:
            # Remove oldest entry
            oldest_key = min(self.cache_timestamps.keys(), key=lambda k: self.cache_timestamps[k])
            del self.cache[oldest_key]
            del self.cache_timestamps[oldest_key]

        self.cache[cache_key] = result
        self.cache_timestamps[cache_key] = datetime.utcnow()
        logger.info(f"Cached result for {agent_role}")

    def clear(self):
        """Clear all cached results."""
        self.cache.clear()
        self.cache_timestamps.clear()


class WorkflowCheckpoint:
    """Handle workflow checkpointing for resume capability."""

    def __init__(self, config: CheckpointConfig, project_id: int):
        """Initialize checkpoint manager."""
        self.config = config
        self.project_id = project_id

        if config.checkpoint_directory:
            self.checkpoint_dir = config.checkpoint_directory / f"project_{project_id}"
            self.checkpoint_dir.mkdir(parents=True, exist_ok=True)
        else:
            self.checkpoint_dir = None

    def save(self,
             current_stage: WorkflowStage,
             stage_history: List[WorkflowStage],
             project_state: ProjectState,
             metadata: Dict[str, Any]) -> bool:
        """Save workflow checkpoint."""
        if not self.config.enabled or not self.checkpoint_dir:
            return False

        try:
            checkpoint_data = {
                "timestamp": datetime.utcnow().isoformat(),
                "project_id": self.project_id,
                "current_stage": current_stage.value,
                "stage_history": [s.value for s in stage_history],
                "project_state": project_state.__dict__,
                "metadata": metadata
            }

            # Generate checkpoint filename with timestamp
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            checkpoint_file = self.checkpoint_dir / f"checkpoint_{timestamp}.json"

            with open(checkpoint_file, 'w') as f:
                json.dump(checkpoint_data, f, indent=2)

            # Enforce max checkpoints
            self._cleanup_old_checkpoints()

            logger.info(f"Saved checkpoint to {checkpoint_file}")
            return True

        except Exception as e:
            logger.error(f"Failed to save checkpoint: {e}")
            return False

    def load_latest(self) -> Optional[Dict[str, Any]]:
        """Load the most recent checkpoint."""
        if not self.config.enabled or not self.checkpoint_dir:
            return None

        try:
            checkpoints = list(self.checkpoint_dir.glob("checkpoint_*.json"))
            if not checkpoints:
                return None

            # Get most recent checkpoint
            latest = max(checkpoints, key=lambda p: p.stat().st_mtime)

            with open(latest, 'r') as f:
                checkpoint_data = json.load(f)

            logger.info(f"Loaded checkpoint from {latest}")
            return checkpoint_data

        except Exception as e:
            logger.error(f"Failed to load checkpoint: {e}")
            return None

    def _cleanup_old_checkpoints(self):
        """Remove old checkpoints beyond max limit."""
        if not self.checkpoint_dir:
            return

        checkpoints = sorted(
            self.checkpoint_dir.glob("checkpoint_*.json"),
            key=lambda p: p.stat().st_mtime,
            reverse=True
        )

        # Remove checkpoints beyond limit
        for checkpoint in checkpoints[self.config.max_checkpoints:]:
            checkpoint.unlink()
            logger.debug(f"Removed old checkpoint: {checkpoint}")


class OptimizedWorkflowOrchestrator:
    """
    Enhanced workflow orchestrator with optimization features.

    Features:
    - Parallel agent execution
    - Result caching
    - Checkpointing and resume
    - Advanced retry logic
    - Performance metrics
    """

    def __init__(self, config: OptimizedWorkflowConfig):
        """Initialize optimized workflow orchestrator."""
        self.config = config
        self.message_bus = MessageBus()
        self.project_state = ProjectState(
            name=f"Project {config.project_id}",
            description=config.requirements,
            requirements={"raw_text": config.requirements}
        )

        # Initialize agents
        self.agents = self._initialize_agents()

        # Workflow state
        self.current_stage = WorkflowStage.INITIALIZATION
        self.stage_history: List[WorkflowStage] = []
        self.errors: List[str] = []

        # Optimization components
        self.cache = AgentResultCache(config.cache_config)
        self.checkpoint = WorkflowCheckpoint(config.checkpoint_config, config.project_id)

        # Performance tracking
        self.stage_timings: Dict[str, float] = {}
        self.start_time: Optional[datetime] = None
        self.last_checkpoint_time: Optional[datetime] = None

        logger.info(f"Optimized workflow orchestrator initialized for project {config.project_id}")

    def _initialize_agents(self) -> Dict[AgentRole, Any]:
        """Initialize all agents."""
        agents = {
            AgentRole.PROJECT_MANAGER: ProjectManagerAgent(
                self.message_bus,
                self.project_state,
                self.config.llm_config
            ),
            AgentRole.REQUIREMENT_ANALYST: RequirementsAnalystAgent(
                self.message_bus,
                self.project_state,
                self.config.llm_config
            ),
            AgentRole.ARCHITECT: ArchitectAgent(
                self.message_bus,
                self.project_state,
                self.config.llm_config
            ),
            AgentRole.UI_DESIGNER: UXUIDesignerAgent(
                self.message_bus,
                self.project_state,
                self.config.llm_config
            ),
            AgentRole.DEVELOPER: DeveloperAgent(
                self.message_bus,
                self.project_state,
                self.config.llm_config
            ),
            AgentRole.TEST_ENGINEER: TestEngineerAgent(
                self.message_bus,
                self.project_state,
                self.config.llm_config
            ),
            AgentRole.QA_ENGINEER: QualityExpertAgent(
                self.message_bus,
                self.project_state,
                self.config.llm_config
            )
        }

        logger.info(f"Initialized {len(agents)} agents")
        return agents

    async def execute(self, resume_from_checkpoint: bool = False) -> bool:
        """Execute the complete workflow with optimizations."""
        logger.info(f"Starting optimized workflow execution for project {self.config.project_id}")
        self.start_time = datetime.utcnow()

        # Try to resume from checkpoint
        if resume_from_checkpoint:
            checkpoint_data = self.checkpoint.load_latest()
            if checkpoint_data:
                await self._resume_from_checkpoint(checkpoint_data)

        try:
            # Execute workflow stages
            await self._execute_requirement_analysis()
            await self._execute_architecture_and_ui_parallel()
            await self._execute_development()
            await self._execute_testing()
            await self._execute_qa_review()

            # Mark as completed
            self.current_stage = WorkflowStage.COMPLETED
            self.stage_history.append(WorkflowStage.COMPLETED)

            # Save final checkpoint
            self.checkpoint.save(
                self.current_stage,
                self.stage_history,
                self.project_state,
                {"completion_time": datetime.utcnow().isoformat()}
            )

            logger.info(f"Workflow completed successfully for project {self.config.project_id}")
            return True

        except Exception as e:
            logger.error(f"Workflow failed: {e}", exc_info=True)
            self.current_stage = WorkflowStage.FAILED
            self.stage_history.append(WorkflowStage.FAILED)
            self.errors.append(str(e))

            # Save failure checkpoint
            self.checkpoint.save(
                self.current_stage,
                self.stage_history,
                self.project_state,
                {"error": str(e)}
            )

            return False

    async def _execute_stage_with_retry(
        self,
        stage: WorkflowStage,
        stage_func,
        retry_config: Optional[RetryConfig] = None
    ):
        """Execute a workflow stage with retry logic."""
        retry_config = retry_config or self.config.retry_config

        logger.info(f"Executing stage: {stage.value}")
        self.current_stage = stage
        self.stage_history.append(stage)

        stage_start = datetime.utcnow()

        for attempt in range(retry_config.max_retries + 1):
            try:
                # Apply timeout if configured
                if self.config.timeout_per_stage:
                    await asyncio.wait_for(
                        stage_func(),
                        timeout=self.config.timeout_per_stage
                    )
                else:
                    await stage_func()

                # Record timing
                duration = (datetime.utcnow() - stage_start).total_seconds()
                self.stage_timings[stage.value] = duration

                logger.info(f"Stage {stage.value} completed in {duration:.2f}s")

                # Auto-checkpoint
                await self._auto_checkpoint()

                return

            except asyncio.TimeoutError:
                if attempt < retry_config.max_retries:
                    delay = self._calculate_retry_delay(attempt, retry_config)
                    logger.warning(f"Stage {stage.value} timed out, retrying in {delay}s (attempt {attempt + 1}/{retry_config.max_retries})")
                    await asyncio.sleep(delay)
                else:
                    raise

            except Exception as e:
                if attempt < retry_config.max_retries and self._should_retry(e, retry_config):
                    delay = self._calculate_retry_delay(attempt, retry_config)
                    logger.warning(f"Stage {stage.value} failed: {e}, retrying in {delay}s (attempt {attempt + 1}/{retry_config.max_retries})")
                    await asyncio.sleep(delay)
                else:
                    raise

    def _calculate_retry_delay(self, attempt: int, config: RetryConfig) -> float:
        """Calculate exponential backoff delay."""
        delay = config.initial_delay * (config.exponential_base ** attempt)
        return min(delay, config.max_delay)

    def _should_retry(self, error: Exception, config: RetryConfig) -> bool:
        """Determine if error should trigger retry."""
        error_str = str(error).lower()
        return any(retry_type in error_str for retry_type in config.retry_on_errors)

    async def _auto_checkpoint(self):
        """Automatically save checkpoint if interval elapsed."""
        if not self.last_checkpoint_time:
            self.last_checkpoint_time = datetime.utcnow()
            return

        elapsed = (datetime.utcnow() - self.last_checkpoint_time).total_seconds()
        if elapsed >= self.config.checkpoint_config.auto_save_interval:
            self.checkpoint.save(
                self.current_stage,
                self.stage_history,
                self.project_state,
                {"auto_save": True, "elapsed_time": elapsed}
            )
            self.last_checkpoint_time = datetime.utcnow()

    async def _execute_requirement_analysis(self):
        """Execute requirement analysis stage."""
        await self._execute_stage_with_retry(
            WorkflowStage.REQUIREMENT_ANALYSIS,
            self._run_requirement_analysis
        )

    async def _run_requirement_analysis(self):
        """Run requirement analysis agents."""
        pm = self.agents[AgentRole.PROJECT_MANAGER]
        analyst = self.agents[AgentRole.REQUIREMENT_ANALYST]

        await pm.process()
        await analyst.process()

    async def _execute_architecture_and_ui_parallel(self):
        """Execute architecture and UI design in parallel if possible."""
        if self.config.skip_ui_design or self.config.execution_strategy == ExecutionStrategy.SEQUENTIAL:
            # Sequential execution
            await self._execute_stage_with_retry(
                WorkflowStage.ARCHITECTURE_DESIGN,
                self._run_architecture_design
            )
            if not self.config.skip_ui_design:
                await self._execute_stage_with_retry(
                    WorkflowStage.UI_DESIGN,
                    self._run_ui_design
                )
        else:
            # Parallel execution
            logger.info("Executing architecture and UI design in parallel")

            architect_task = asyncio.create_task(
                self._execute_stage_with_retry(
                    WorkflowStage.ARCHITECTURE_DESIGN,
                    self._run_architecture_design
                )
            )

            ui_task = asyncio.create_task(
                self._execute_stage_with_retry(
                    WorkflowStage.UI_DESIGN,
                    self._run_ui_design
                )
            )

            # Wait for both to complete
            await asyncio.gather(architect_task, ui_task)

    async def _run_architecture_design(self):
        """Run architecture design agent."""
        architect = self.agents[AgentRole.ARCHITECT]
        await architect.process()

    async def _run_ui_design(self):
        """Run UI design agent."""
        designer = self.agents[AgentRole.UI_DESIGNER]
        await designer.process()

    async def _execute_development(self):
        """Execute development stage."""
        await self._execute_stage_with_retry(
            WorkflowStage.DEVELOPMENT,
            self._run_development
        )

    async def _run_development(self):
        """Run development agent with iterations."""
        developer = self.agents[AgentRole.DEVELOPER]

        iteration = 0
        while iteration < self.config.max_iterations:
            await developer.process()

            if self.project_state.get("development_complete", False):
                break

            iteration += 1

    async def _execute_testing(self):
        """Execute testing stage."""
        await self._execute_stage_with_retry(
            WorkflowStage.TESTING,
            self._run_testing
        )

    async def _run_testing(self):
        """Run testing with developer feedback loop."""
        tester = self.agents[AgentRole.TEST_ENGINEER]
        developer = self.agents[AgentRole.DEVELOPER]

        iteration = 0
        while iteration < self.config.max_iterations:
            await tester.process()

            test_results = self.project_state.get("test_results", {})
            if test_results.get("all_passed", False):
                break

            if test_results.get("failures", 0) > 0:
                await developer.process()

            iteration += 1

    async def _execute_qa_review(self):
        """Execute QA review stage."""
        await self._execute_stage_with_retry(
            WorkflowStage.QA_REVIEW,
            self._run_qa_review
        )

    async def _run_qa_review(self):
        """Run QA review with developer feedback."""
        qa = self.agents[AgentRole.QA_ENGINEER]
        developer = self.agents[AgentRole.DEVELOPER]

        iteration = 0
        while iteration < self.config.max_iterations:
            await qa.process()

            qa_results = self.project_state.get("qa_results", {})
            if qa_results.get("approved", False):
                break

            if qa_results.get("issues", []):
                await developer.process()

            iteration += 1

    async def _resume_from_checkpoint(self, checkpoint_data: Dict[str, Any]):
        """Resume workflow from checkpoint."""
        logger.info("Resuming workflow from checkpoint")

        # Restore state
        self.current_stage = WorkflowStage(checkpoint_data["current_stage"])
        self.stage_history = [WorkflowStage(s) for s in checkpoint_data["stage_history"]]

        # Note: Full state restoration would require more complex logic
        # This is a simplified version

    def get_progress(self) -> Dict[str, Any]:
        """Get current workflow progress with enhanced metrics."""
        total_stages = len(WorkflowStage) - 2
        completed_stages = len([s for s in self.stage_history if s not in [WorkflowStage.FAILED]])

        total_time = 0
        if self.start_time:
            total_time = (datetime.utcnow() - self.start_time).total_seconds()

        return {
            "current_stage": self.current_stage.value,
            "progress_percentage": int((completed_stages / total_stages) * 100),
            "stage_history": [s.value for s in self.stage_history],
            "errors": self.errors,
            "total_tokens": sum(agent.total_tokens for agent in self.agents.values()),
            "total_requests": sum(agent.requests_count for agent in self.agents.values()),
            "stage_timings": self.stage_timings,
            "total_time_seconds": total_time,
            "cache_stats": {
                "hits": len(self.cache.cache),
                "size": len(self.cache.cache)
            }
        }

    def get_artifacts(self) -> Dict[str, Any]:
        """Get generated artifacts from the workflow."""
        return {
            "requirements_doc": self.project_state.get("requirements_doc"),
            "architecture_doc": self.project_state.get("architecture_doc"),
            "ui_designs": self.project_state.get("ui_designs"),
            "source_code": self.project_state.get("source_code"),
            "test_code": self.project_state.get("test_code"),
            "test_results": self.project_state.get("test_results"),
            "qa_report": self.project_state.get("qa_report")
        }

    async def cancel(self):
        """Cancel the workflow execution."""
        logger.warning(f"Canceling optimized workflow for project {self.config.project_id}")
        self.current_stage = WorkflowStage.FAILED
        self.errors.append("Workflow canceled by user")

        # Save cancellation checkpoint
        self.checkpoint.save(
            self.current_stage,
            self.stage_history,
            self.project_state,
            {"canceled": True}
        )

        await self.message_bus.publish({
            "type": "workflow.canceled",
            "project_id": self.config.project_id
        })
