"""Workflow orchestration for multi-agent software development."""
import asyncio
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum

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


from resoftai.core.state import WorkflowStage

# Use the existing WorkflowStage from core.state
# This ensures consistency across the system


@dataclass
class WorkflowConfig:
    """Configuration for workflow execution."""
    project_id: int
    requirements: str
    llm_config: LLMConfig
    output_directory: str
    max_iterations: int = 3
    enable_parallel_execution: bool = False

    # Agent-specific configs
    skip_ui_design: bool = False
    test_framework: str = "pytest"
    code_style: str = "pep8"


class WorkflowOrchestrator:
    """Orchestrates multi-agent workflow for software development."""

    def __init__(self, config: WorkflowConfig):
        """Initialize workflow orchestrator.

        Args:
            config: Workflow configuration
        """
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
        self.current_stage = WorkflowStage.INITIAL
        self.stage_history: List[WorkflowStage] = []
        self.errors: List[str] = []

        logger.info(f"Workflow orchestrator initialized for project {config.project_id}")

    def _initialize_agents(self) -> Dict[AgentRole, Any]:
        """Initialize all agents.

        Returns:
            Dictionary mapping agent roles to agent instances
        """
        agents = {
            AgentRole.PROJECT_MANAGER: ProjectManagerAgent(
                AgentRole.PROJECT_MANAGER,
                self.message_bus,
                self.project_state,
                self.config.llm_config
            ),
            AgentRole.REQUIREMENTS_ANALYST: RequirementsAnalystAgent(
                AgentRole.REQUIREMENTS_ANALYST,
                self.message_bus,
                self.project_state,
                self.config.llm_config
            ),
            AgentRole.ARCHITECT: ArchitectAgent(
                AgentRole.ARCHITECT,
                self.message_bus,
                self.project_state,
                self.config.llm_config
            ),
            AgentRole.UXUI_DESIGNER: UXUIDesignerAgent(
                AgentRole.UXUI_DESIGNER,
                self.message_bus,
                self.project_state,
                self.config.llm_config
            ),
            AgentRole.DEVELOPER: DeveloperAgent(
                AgentRole.DEVELOPER,
                self.message_bus,
                self.project_state,
                self.config.llm_config
            ),
            AgentRole.TEST_ENGINEER: TestEngineerAgent(
                AgentRole.TEST_ENGINEER,
                self.message_bus,
                self.project_state,
                self.config.llm_config
            ),
            AgentRole.QUALITY_EXPERT: QualityExpertAgent(
                AgentRole.QUALITY_EXPERT,
                self.message_bus,
                self.project_state,
                self.config.llm_config
            )
        }

        logger.info(f"Initialized {len(agents)} agents")
        return agents

    async def execute(self) -> bool:
        """Execute the complete workflow.

        Returns:
            True if workflow completed successfully, False otherwise
        """
        logger.info(f"Starting workflow execution for project {self.config.project_id}")

        try:
            # Stage 1: Requirement Analysis
            await self._execute_stage(
                WorkflowStage.REQUIREMENTS_ANALYSIS,
                self._run_requirement_analysis
            )

            # Stage 2: Architecture Design
            await self._execute_stage(
                WorkflowStage.ARCHITECTURE_DESIGN,
                self._run_architecture_design
            )

            # Stage 3: UI Design (optional)
            if not self.config.skip_ui_design:
                await self._execute_stage(
                    WorkflowStage.UI_UX_DESIGN,
                    self._run_ui_design
                )

            # Stage 4: Development
            await self._execute_stage(
                WorkflowStage.IMPLEMENTATION,
                self._run_development
            )

            # Stage 5: Testing
            await self._execute_stage(
                WorkflowStage.TESTING,
                self._run_testing
            )

            # Stage 6: QA Review
            await self._execute_stage(
                WorkflowStage.QUALITY_ASSURANCE,
                self._run_qa_review
            )

            # Mark as completed
            self.current_stage = WorkflowStage.COMPLETED
            self.stage_history.append(WorkflowStage.COMPLETED)

            logger.info(f"Workflow completed successfully for project {self.config.project_id}")
            return True

        except Exception as e:
            logger.error(f"Workflow failed: {e}", exc_info=True)
            self.current_stage = WorkflowStage.FAILED
            self.stage_history.append(WorkflowStage.FAILED)
            self.errors.append(str(e))
            return False

    async def _execute_stage(self, stage: WorkflowStage, stage_func):
        """Execute a workflow stage.

        Args:
            stage: Stage to execute
            stage_func: Async function to run for this stage
        """
        logger.info(f"Executing stage: {stage.value}")
        self.current_stage = stage
        self.stage_history.append(stage)

        try:
            await stage_func()
            logger.info(f"Stage {stage.value} completed successfully")
        except Exception as e:
            logger.error(f"Stage {stage.value} failed: {e}")
            raise

    async def _run_requirement_analysis(self):
        """Run requirement analysis stage."""
        pm = self.agents[AgentRole.PROJECT_MANAGER]
        analyst = self.agents[AgentRole.REQUIREMENTS_ANALYST]

        # PM initializes project
        await pm.process()

        # Analyst analyzes requirements
        await analyst.process()

        logger.info("Requirement analysis completed")

    async def _run_architecture_design(self):
        """Run architecture design stage."""
        architect = self.agents[AgentRole.ARCHITECT]

        # Architect designs system architecture
        await architect.process()

        logger.info("Architecture design completed")

    async def _run_ui_design(self):
        """Run UI design stage."""
        designer = self.agents[AgentRole.UXUI_DESIGNER]

        # Designer creates UI/UX designs
        await designer.process()

        logger.info("UI design completed")

    async def _run_development(self):
        """Run development stage."""
        developer = self.agents[AgentRole.DEVELOPER]

        # Developer implements code
        iteration = 0
        while iteration < self.config.max_iterations:
            await developer.process()

            # Check if development is complete
            if self.project_state.get("development_complete", False):
                break

            iteration += 1
            logger.info(f"Development iteration {iteration + 1} completed")

        logger.info("Development completed")

    async def _run_testing(self):
        """Run testing stage."""
        tester = self.agents[AgentRole.TEST_ENGINEER]
        developer = self.agents[AgentRole.DEVELOPER]

        # Tester creates and runs tests
        iteration = 0
        while iteration < self.config.max_iterations:
            await tester.process()

            # Check test results
            test_results = self.project_state.get("test_results", {})
            if test_results.get("all_passed", False):
                break

            # If tests failed, developer fixes issues
            if test_results.get("failures", 0) > 0:
                logger.info(f"Tests failed, developer fixing issues...")
                await developer.process()

            iteration += 1
            logger.info(f"Testing iteration {iteration + 1} completed")

        logger.info("Testing completed")

    async def _run_qa_review(self):
        """Run QA review stage."""
        qa = self.agents[AgentRole.QUALITY_EXPERT]
        developer = self.agents[AgentRole.DEVELOPER]

        # QA reviews the project
        iteration = 0
        while iteration < self.config.max_iterations:
            await qa.process()

            # Check QA results
            qa_results = self.project_state.get("qa_results", {})
            if qa_results.get("approved", False):
                break

            # If QA found issues, developer fixes them
            if qa_results.get("issues", []):
                logger.info(f"QA found issues, developer fixing...")
                await developer.process()

            iteration += 1
            logger.info(f"QA review iteration {iteration + 1} completed")

        logger.info("QA review completed")

    def get_progress(self) -> Dict[str, Any]:
        """Get current workflow progress.

        Returns:
            Dictionary with progress information
        """
        total_stages = len(WorkflowStage) - 2  # Exclude COMPLETED and FAILED
        completed_stages = len([s for s in self.stage_history if s not in [WorkflowStage.FAILED]])

        return {
            "current_stage": self.current_stage.value,
            "progress_percentage": int((completed_stages / total_stages) * 100),
            "stage_history": [s.value for s in self.stage_history],
            "errors": self.errors,
            "total_tokens": sum(agent.total_tokens for agent in self.agents.values()),
            "total_requests": sum(agent.requests_count for agent in self.agents.values())
        }

    def get_artifacts(self) -> Dict[str, Any]:
        """Get generated artifacts from the workflow.

        Returns:
            Dictionary with all generated artifacts
        """
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
        logger.warning(f"Canceling workflow for project {self.config.project_id}")
        self.current_stage = WorkflowStage.FAILED
        self.errors.append("Workflow canceled by user")

        # Notify all agents
        await self.message_bus.publish({
            "type": "workflow.canceled",
            "project_id": self.config.project_id
        })
