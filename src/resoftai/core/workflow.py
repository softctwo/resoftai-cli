"""
Project workflow orchestration and management.
"""

from typing import Dict, List, Optional, Callable
import logging
import asyncio

from resoftai.core.message_bus import Message, MessageBus, MessageType
from resoftai.core.state import ProjectState, WorkflowStage, Task, TaskStatus
from resoftai.core.agent import AgentRole

logger = logging.getLogger(__name__)


class ProjectWorkflow:
    """
    Orchestrates the entire software development workflow.

    Manages:
    - Stage transitions
    - Agent coordination
    - Task distribution
    - Progress tracking
    """

    # Define the workflow stages in order
    WORKFLOW_SEQUENCE = [
        WorkflowStage.REQUIREMENTS_GATHERING,
        WorkflowStage.REQUIREMENTS_ANALYSIS,
        WorkflowStage.ARCHITECTURE_DESIGN,
        WorkflowStage.UI_UX_DESIGN,
        WorkflowStage.PROTOTYPE_DEVELOPMENT,
        WorkflowStage.CLIENT_REVIEW,
        WorkflowStage.REQUIREMENTS_REFINEMENT,
        WorkflowStage.DEVELOPMENT_PLANNING,
        WorkflowStage.IMPLEMENTATION,
        WorkflowStage.TESTING,
        WorkflowStage.QUALITY_ASSURANCE,
        WorkflowStage.DOCUMENTATION,
        WorkflowStage.DEPLOYMENT,
        WorkflowStage.COMPLETED,
    ]

    # Map stages to responsible agents
    STAGE_AGENTS: Dict[WorkflowStage, List[AgentRole]] = {
        WorkflowStage.REQUIREMENTS_GATHERING: [
            AgentRole.PROJECT_MANAGER,
            AgentRole.REQUIREMENTS_ANALYST,
        ],
        WorkflowStage.REQUIREMENTS_ANALYSIS: [
            AgentRole.REQUIREMENTS_ANALYST,
        ],
        WorkflowStage.ARCHITECTURE_DESIGN: [
            AgentRole.ARCHITECT,
        ],
        WorkflowStage.UI_UX_DESIGN: [
            AgentRole.UXUI_DESIGNER,
        ],
        WorkflowStage.PROTOTYPE_DEVELOPMENT: [
            AgentRole.ARCHITECT,
            AgentRole.UXUI_DESIGNER,
            AgentRole.DEVELOPER,
        ],
        WorkflowStage.CLIENT_REVIEW: [
            AgentRole.PROJECT_MANAGER,
        ],
        WorkflowStage.REQUIREMENTS_REFINEMENT: [
            AgentRole.REQUIREMENTS_ANALYST,
            AgentRole.ARCHITECT,
        ],
        WorkflowStage.DEVELOPMENT_PLANNING: [
            AgentRole.PROJECT_MANAGER,
            AgentRole.ARCHITECT,
        ],
        WorkflowStage.IMPLEMENTATION: [
            AgentRole.DEVELOPER,
        ],
        WorkflowStage.TESTING: [
            AgentRole.TEST_ENGINEER,
            AgentRole.DEVELOPER,
        ],
        WorkflowStage.QUALITY_ASSURANCE: [
            AgentRole.QUALITY_EXPERT,
        ],
        WorkflowStage.DOCUMENTATION: [
            AgentRole.PROJECT_MANAGER,
            AgentRole.REQUIREMENTS_ANALYST,
            AgentRole.ARCHITECT,
            AgentRole.DEVELOPER,
        ],
        WorkflowStage.DEPLOYMENT: [
            AgentRole.PROJECT_MANAGER,
            AgentRole.DEVELOPER,
        ],
    }

    def __init__(self, message_bus: MessageBus, project_state: ProjectState):
        """
        Initialize the workflow engine.

        Args:
            message_bus: Message bus for communication
            project_state: Project state to manage
        """
        self.message_bus = message_bus
        self.project_state = project_state
        self._stage_completion_callbacks: Dict[WorkflowStage, List[Callable]] = {}

    async def start(self, user_requirements: str) -> None:
        """
        Start the workflow with initial user requirements.

        Args:
            user_requirements: Initial requirements from the user
        """
        logger.info("Starting project workflow")

        # Initialize project state with user requirements
        self.project_state.description = user_requirements
        self.project_state.requirements["initial_input"] = user_requirements

        # Publish workflow start message
        await self.message_bus.publish(
            Message(
                type=MessageType.WORKFLOW_START,
                sender="workflow",
                content={
                    "project_id": self.project_state.id,
                    "requirements": user_requirements,
                }
            )
        )

        # Start first stage
        await self.advance_to_stage(WorkflowStage.REQUIREMENTS_GATHERING)

    async def advance_to_stage(self, stage: WorkflowStage) -> None:
        """
        Advance the workflow to a new stage.

        Args:
            stage: The stage to advance to
        """
        logger.info(f"Advancing to stage: {stage.value}")

        # Update project state
        self.project_state.advance_stage(stage)

        # Notify agents about stage start
        await self.message_bus.publish(
            Message(
                type=MessageType.STAGE_START,
                sender="workflow",
                content={
                    "stage": stage.value,
                    "project_id": self.project_state.id,
                }
            )
        )

        # Assign initial tasks for this stage
        await self._create_stage_tasks(stage)

    async def complete_stage(self, stage: WorkflowStage) -> None:
        """
        Mark a stage as complete and advance to next stage.

        Args:
            stage: The stage that is completing
        """
        logger.info(f"Completing stage: {stage.value}")

        # Publish stage completion message
        await self.message_bus.publish(
            Message(
                type=MessageType.STAGE_COMPLETE,
                sender="workflow",
                content={
                    "stage": stage.value,
                    "project_id": self.project_state.id,
                }
            )
        )

        # Call completion callbacks
        if stage in self._stage_completion_callbacks:
            for callback in self._stage_completion_callbacks[stage]:
                await callback(self.project_state)

        # Advance to next stage
        next_stage = self._get_next_stage(stage)
        if next_stage:
            await self.advance_to_stage(next_stage)
        else:
            await self._complete_workflow()

    def _get_next_stage(self, current_stage: WorkflowStage) -> Optional[WorkflowStage]:
        """Get the next stage in the workflow sequence."""
        try:
            current_index = self.WORKFLOW_SEQUENCE.index(current_stage)
            if current_index < len(self.WORKFLOW_SEQUENCE) - 1:
                return self.WORKFLOW_SEQUENCE[current_index + 1]
        except ValueError:
            pass
        return None

    async def _complete_workflow(self) -> None:
        """Complete the entire workflow."""
        logger.info("Workflow completed")

        self.project_state.advance_stage(WorkflowStage.COMPLETED)

        await self.message_bus.publish(
            Message(
                type=MessageType.WORKFLOW_COMPLETE,
                sender="workflow",
                content={
                    "project_id": self.project_state.id,
                    "artifacts": self.project_state.artifacts,
                }
            )
        )

    async def _create_stage_tasks(self, stage: WorkflowStage) -> None:
        """
        Create initial tasks for a workflow stage.

        Args:
            stage: The stage to create tasks for
        """
        agents = self.STAGE_AGENTS.get(stage, [])

        # Create tasks based on stage
        tasks = self._get_default_tasks_for_stage(stage)

        for task_info in tasks:
            task = Task(
                title=task_info["title"],
                description=task_info["description"],
                assigned_to=task_info.get("assigned_to"),
                status=TaskStatus.PENDING,
                stage=stage,
            )

            self.project_state.add_task(task)

            # Notify assigned agent
            if task.assigned_to:
                await self.message_bus.publish(
                    Message(
                        type=MessageType.TASK_ASSIGNED,
                        sender="workflow",
                        receiver=task.assigned_to,
                        content={
                            "task_id": task.id,
                            "task": task.to_dict(),
                        }
                    )
                )

    def _get_default_tasks_for_stage(self, stage: WorkflowStage) -> List[Dict]:
        """Get default tasks for each stage."""
        task_templates = {
            WorkflowStage.REQUIREMENTS_GATHERING: [
                {
                    "title": "Gather initial requirements",
                    "description": "Interview client and gather initial software requirements",
                    "assigned_to": AgentRole.PROJECT_MANAGER.value,
                },
                {
                    "title": "Document user needs",
                    "description": "Document all user needs and expectations",
                    "assigned_to": AgentRole.REQUIREMENTS_ANALYST.value,
                },
            ],
            WorkflowStage.REQUIREMENTS_ANALYSIS: [
                {
                    "title": "Analyze requirements",
                    "description": "Analyze and structure the gathered requirements",
                    "assigned_to": AgentRole.REQUIREMENTS_ANALYST.value,
                },
                {
                    "title": "Create requirements document",
                    "description": "Create detailed requirements specification",
                    "assigned_to": AgentRole.REQUIREMENTS_ANALYST.value,
                },
            ],
            WorkflowStage.ARCHITECTURE_DESIGN: [
                {
                    "title": "Design system architecture",
                    "description": "Design the overall system architecture and components",
                    "assigned_to": AgentRole.ARCHITECT.value,
                },
                {
                    "title": "Design database schema",
                    "description": "Design the database structure and relationships",
                    "assigned_to": AgentRole.ARCHITECT.value,
                },
            ],
            WorkflowStage.UI_UX_DESIGN: [
                {
                    "title": "Design user interface",
                    "description": "Create UI mockups and design system",
                    "assigned_to": AgentRole.UXUI_DESIGNER.value,
                },
                {
                    "title": "Design user experience flow",
                    "description": "Design the user journey and interaction patterns",
                    "assigned_to": AgentRole.UXUI_DESIGNER.value,
                },
            ],
            WorkflowStage.PROTOTYPE_DEVELOPMENT: [
                {
                    "title": "Develop prototype",
                    "description": "Create a working prototype of key features",
                    "assigned_to": AgentRole.DEVELOPER.value,
                },
            ],
            WorkflowStage.DEVELOPMENT_PLANNING: [
                {
                    "title": "Create development plan",
                    "description": "Break down work into sprints and tasks",
                    "assigned_to": AgentRole.PROJECT_MANAGER.value,
                },
            ],
            WorkflowStage.IMPLEMENTATION: [
                {
                    "title": "Implement features",
                    "description": "Develop all planned features",
                    "assigned_to": AgentRole.DEVELOPER.value,
                },
            ],
            WorkflowStage.TESTING: [
                {
                    "title": "Create test plan",
                    "description": "Design comprehensive test strategy",
                    "assigned_to": AgentRole.TEST_ENGINEER.value,
                },
                {
                    "title": "Execute tests",
                    "description": "Run all tests and document results",
                    "assigned_to": AgentRole.TEST_ENGINEER.value,
                },
            ],
            WorkflowStage.QUALITY_ASSURANCE: [
                {
                    "title": "Quality review",
                    "description": "Comprehensive quality assessment",
                    "assigned_to": AgentRole.QUALITY_EXPERT.value,
                },
            ],
            WorkflowStage.DOCUMENTATION: [
                {
                    "title": "Generate all documentation",
                    "description": "Create complete documentation package",
                    "assigned_to": AgentRole.PROJECT_MANAGER.value,
                },
            ],
            WorkflowStage.DEPLOYMENT: [
                {
                    "title": "Deploy software",
                    "description": "Deploy and deliver the software",
                    "assigned_to": AgentRole.PROJECT_MANAGER.value,
                },
            ],
        }

        return task_templates.get(stage, [])

    def register_stage_completion_callback(
        self,
        stage: WorkflowStage,
        callback: Callable
    ) -> None:
        """Register a callback to be called when a stage completes."""
        if stage not in self._stage_completion_callbacks:
            self._stage_completion_callbacks[stage] = []
        self._stage_completion_callbacks[stage].append(callback)

    def get_workflow_progress(self) -> Dict:
        """Get current workflow progress summary."""
        total_stages = len(self.WORKFLOW_SEQUENCE)
        try:
            current_index = self.WORKFLOW_SEQUENCE.index(self.project_state.current_stage)
            progress_percentage = (current_index / total_stages) * 100
        except ValueError:
            progress_percentage = 0

        all_tasks = list(self.project_state.tasks.values())
        completed_tasks = [t for t in all_tasks if t.status == TaskStatus.COMPLETED]

        return {
            "current_stage": self.project_state.current_stage.value,
            "progress_percentage": progress_percentage,
            "total_tasks": len(all_tasks),
            "completed_tasks": len(completed_tasks),
            "pending_tasks": len([t for t in all_tasks if t.status == TaskStatus.PENDING]),
            "in_progress_tasks": len([t for t in all_tasks if t.status == TaskStatus.IN_PROGRESS]),
        }
