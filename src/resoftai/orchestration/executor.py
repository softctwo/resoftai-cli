"""Project execution service."""
import asyncio
import logging
from typing import Dict, Optional
from datetime import datetime
from pathlib import Path

from sqlalchemy.ext.asyncio import AsyncSession

from resoftai.orchestration.workflow import WorkflowOrchestrator, WorkflowConfig, WorkflowStage
from resoftai.models.project import Project
from resoftai.models.llm_config import LLMConfigModel
from resoftai.crud.project import update_project
from resoftai.crud.llm_config import get_active_llm_config
from resoftai.llm.base import LLMConfig, ModelProvider
from resoftai.websocket.manager import emit_project_progress, emit_agent_status
from resoftai.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class ProjectExecutor:
    """Manages project execution with workflow orchestration."""

    # Class-level registry of running executors
    _running_executors: Dict[int, 'ProjectExecutor'] = {}

    def __init__(
        self,
        project: Project,
        llm_config_model: LLMConfigModel,
        db: AsyncSession
    ):
        """Initialize project executor.

        Args:
            project: Project model instance
            llm_config_model: LLM configuration model
            db: Database session
        """
        self.project = project
        self.llm_config_model = llm_config_model
        self.db = db

        # Convert LLMConfigModel to LLMConfig
        self.llm_config = LLMConfig(
            provider=ModelProvider(llm_config_model.provider),
            api_key=llm_config_model.api_key,
            model_name=llm_config_model.model,
            api_base=llm_config_model.api_base,
            max_tokens=llm_config_model.max_tokens,
            temperature=llm_config_model.temperature,
            top_p=llm_config_model.top_p
        )

        # Create workflow config
        output_dir = Path(settings.resoftai_workspace) / f"project_{project.id}"
        output_dir.mkdir(parents=True, exist_ok=True)

        self.workflow_config = WorkflowConfig(
            project_id=project.id,
            requirements=project.requirements,
            llm_config=self.llm_config,
            output_directory=str(output_dir)
        )

        # Create orchestrator
        self.orchestrator: Optional[WorkflowOrchestrator] = None
        self.execution_task: Optional[asyncio.Task] = None

        # Status
        self.is_running = False
        self.start_time: Optional[datetime] = None
        self.end_time: Optional[datetime] = None

        logger.info(f"ProjectExecutor initialized for project {project.id}")

    @classmethod
    async def start_execution(
        cls,
        project: Project,
        db: AsyncSession
    ) -> 'ProjectExecutor':
        """Start project execution.

        Args:
            project: Project to execute
            db: Database session

        Returns:
            ProjectExecutor instance

        Raises:
            ValueError: If project is already running or LLM config not found
        """
        # Check if already running
        if project.id in cls._running_executors:
            raise ValueError(f"Project {project.id} is already running")

        # Get active LLM config
        llm_config = await get_active_llm_config(db, project.user_id)
        if not llm_config:
            raise ValueError(f"No active LLM configuration found for user {project.user_id}")

        # Create executor
        executor = cls(project, llm_config, db)

        # Register executor
        cls._running_executors[project.id] = executor

        # Start execution in background
        await executor.start()

        return executor

    @classmethod
    def get_executor(cls, project_id: int) -> Optional['ProjectExecutor']:
        """Get running executor for a project.

        Args:
            project_id: Project ID

        Returns:
            ProjectExecutor if running, None otherwise
        """
        return cls._running_executors.get(project_id)

    @classmethod
    async def stop_execution(cls, project_id: int) -> bool:
        """Stop project execution.

        Args:
            project_id: Project ID

        Returns:
            True if stopped, False if not running
        """
        executor = cls._running_executors.get(project_id)
        if not executor:
            return False

        await executor.stop()
        return True

    async def start(self):
        """Start the workflow execution."""
        if self.is_running:
            raise RuntimeError("Execution already started")

        logger.info(f"Starting execution for project {self.project.id}")

        self.is_running = True
        self.start_time = datetime.utcnow()

        # Update project status
        await update_project(
            self.db,
            self.project.id,
            status="planning",
            progress=0
        )
        await self.db.commit()

        # Emit progress event
        await emit_project_progress(
            self.project.id,
            percentage=0,
            stage="planning",
            message="Starting project execution..."
        )

        # Create orchestrator
        self.orchestrator = WorkflowOrchestrator(self.workflow_config)

        # Start execution task
        self.execution_task = asyncio.create_task(self._execute_workflow())

    async def _execute_workflow(self):
        """Execute the workflow and update status."""
        try:
            # Execute workflow
            success = await self.orchestrator.execute()

            if success:
                # Update project to completed
                await update_project(
                    self.db,
                    self.project.id,
                    status="completed",
                    progress=100
                )
                await self.db.commit()

                await emit_project_progress(
                    self.project.id,
                    percentage=100,
                    stage="completed",
                    message="Project completed successfully!"
                )

                logger.info(f"Project {self.project.id} completed successfully")
            else:
                # Update project to failed
                await update_project(
                    self.db,
                    self.project.id,
                    status="failed",
                    progress=self.orchestrator.get_progress()["progress_percentage"]
                )
                await self.db.commit()

                await emit_project_progress(
                    self.project.id,
                    percentage=self.orchestrator.get_progress()["progress_percentage"],
                    stage="failed",
                    message=f"Project failed: {self.orchestrator.errors[-1] if self.orchestrator.errors else 'Unknown error'}"
                )

                logger.error(f"Project {self.project.id} failed")

        except Exception as e:
            logger.error(f"Workflow execution error: {e}", exc_info=True)

            # Update project to failed
            await update_project(
                self.db,
                self.project.id,
                status="failed"
            )
            await self.db.commit()

            await emit_project_progress(
                self.project.id,
                percentage=0,
                stage="failed",
                message=f"Execution error: {str(e)}"
            )

        finally:
            self.is_running = False
            self.end_time = datetime.utcnow()

            # Unregister executor
            if self.project.id in self._running_executors:
                del self._running_executors[self.project.id]

    async def stop(self):
        """Stop the workflow execution."""
        if not self.is_running:
            return

        logger.info(f"Stopping execution for project {self.project.id}")

        # Cancel orchestrator
        if self.orchestrator:
            await self.orchestrator.cancel()

        # Cancel task
        if self.execution_task:
            self.execution_task.cancel()
            try:
                await self.execution_task
            except asyncio.CancelledError:
                pass

        # Update project status
        await update_project(
            self.db,
            self.project.id,
            status="canceled"
        )
        await self.db.commit()

        await emit_project_progress(
            self.project.id,
            percentage=self.get_progress()["progress_percentage"],
            stage="canceled",
            message="Project execution canceled by user"
        )

        self.is_running = False
        self.end_time = datetime.utcnow()

        # Unregister
        if self.project.id in self._running_executors:
            del self._running_executors[self.project.id]

    def get_progress(self) -> Dict:
        """Get current execution progress.

        Returns:
            Progress dictionary
        """
        if not self.orchestrator:
            return {
                "progress_percentage": 0,
                "current_stage": "not_started",
                "stage_history": [],
                "errors": [],
                "total_tokens": 0,
                "total_requests": 0
            }

        return self.orchestrator.get_progress()

    def get_artifacts(self) -> Dict:
        """Get generated artifacts.

        Returns:
            Artifacts dictionary
        """
        if not self.orchestrator:
            return {}

        return self.orchestrator.get_artifacts()

    def get_execution_time(self) -> Optional[float]:
        """Get execution time in seconds.

        Returns:
            Execution time or None if not started
        """
        if not self.start_time:
            return None

        end = self.end_time or datetime.utcnow()
        return (end - self.start_time).total_seconds()
