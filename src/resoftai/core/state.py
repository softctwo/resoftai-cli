"""
Project state management for tracking workflow progress.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import uuid4
import json
from pathlib import Path


class WorkflowStage(str, Enum):
    """Stages in the software development workflow."""

    INITIAL = "initial"
    REQUIREMENTS_GATHERING = "requirements_gathering"
    REQUIREMENTS_ANALYSIS = "requirements_analysis"
    ARCHITECTURE_DESIGN = "architecture_design"
    UI_UX_DESIGN = "ui_ux_design"
    PROTOTYPE_DEVELOPMENT = "prototype_development"
    CLIENT_REVIEW = "client_review"
    REQUIREMENTS_REFINEMENT = "requirements_refinement"
    DEVELOPMENT_PLANNING = "development_planning"
    IMPLEMENTATION = "implementation"
    TESTING = "testing"
    QUALITY_ASSURANCE = "quality_assurance"
    DOCUMENTATION = "documentation"
    DEPLOYMENT = "deployment"
    COMPLETED = "completed"


class TaskStatus(str, Enum):
    """Status of a task."""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    REVIEW = "review"
    COMPLETED = "completed"
    BLOCKED = "blocked"


@dataclass
class Task:
    """Represents a task in the workflow."""

    id: str = field(default_factory=lambda: str(uuid4()))
    title: str = ""
    description: str = ""
    assigned_to: Optional[str] = None
    status: TaskStatus = TaskStatus.PENDING
    stage: WorkflowStage = WorkflowStage.INITIAL
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    dependencies: List[str] = field(default_factory=list)
    artifacts: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert task to dictionary."""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "assigned_to": self.assigned_to,
            "status": self.status.value,
            "stage": self.stage.value,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "dependencies": self.dependencies,
            "artifacts": self.artifacts,
            "metadata": self.metadata,
        }


@dataclass
class ProjectState:
    """
    Central state management for a software project.
    Tracks workflow progress, tasks, artifacts, and metadata.
    """

    id: str = field(default_factory=lambda: str(uuid4()))
    name: str = ""
    description: str = ""
    current_stage: WorkflowStage = WorkflowStage.INITIAL
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    # Project content
    requirements: Dict[str, Any] = field(default_factory=dict)
    architecture: Dict[str, Any] = field(default_factory=dict)
    design: Dict[str, Any] = field(default_factory=dict)
    implementation_plan: Dict[str, Any] = field(default_factory=dict)

    # Tasks and artifacts
    tasks: Dict[str, Task] = field(default_factory=dict)
    artifacts: Dict[str, str] = field(default_factory=dict)  # artifact_type -> path

    # Communication history
    decisions: List[Dict[str, Any]] = field(default_factory=list)
    client_feedback: List[Dict[str, Any]] = field(default_factory=list)

    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)

    def add_task(self, task: Task) -> None:
        """Add a task to the project."""
        self.tasks[task.id] = task
        self.updated_at = datetime.now()

    def update_task(self, task_id: str, **updates) -> None:
        """Update a task."""
        if task_id in self.tasks:
            task = self.tasks[task_id]
            for key, value in updates.items():
                if hasattr(task, key):
                    setattr(task, key, value)
            task.updated_at = datetime.now()
            self.updated_at = datetime.now()

    def get_tasks_by_stage(self, stage: WorkflowStage) -> List[Task]:
        """Get all tasks for a specific stage."""
        return [task for task in self.tasks.values() if task.stage == stage]

    def get_tasks_by_status(self, status: TaskStatus) -> List[Task]:
        """Get all tasks with a specific status."""
        return [task for task in self.tasks.values() if task.status == status]

    def add_artifact(self, artifact_type: str, path: str) -> None:
        """Add an artifact to the project."""
        self.artifacts[artifact_type] = path
        self.updated_at = datetime.now()

    def add_decision(self, decision: str, made_by: str, rationale: str = "") -> None:
        """Record a project decision."""
        self.decisions.append({
            "decision": decision,
            "made_by": made_by,
            "rationale": rationale,
            "timestamp": datetime.now().isoformat(),
        })
        self.updated_at = datetime.now()

    def add_client_feedback(self, feedback: str, stage: WorkflowStage) -> None:
        """Record client feedback."""
        self.client_feedback.append({
            "feedback": feedback,
            "stage": stage.value,
            "timestamp": datetime.now().isoformat(),
        })
        self.updated_at = datetime.now()

    def advance_stage(self, new_stage: WorkflowStage) -> None:
        """Advance to a new workflow stage."""
        self.current_stage = new_stage
        self.updated_at = datetime.now()

    def to_dict(self) -> Dict[str, Any]:
        """Convert project state to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "current_stage": self.current_stage.value,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "requirements": self.requirements,
            "architecture": self.architecture,
            "design": self.design,
            "implementation_plan": self.implementation_plan,
            "tasks": {tid: task.to_dict() for tid, task in self.tasks.items()},
            "artifacts": self.artifacts,
            "decisions": self.decisions,
            "client_feedback": self.client_feedback,
            "metadata": self.metadata,
        }

    def save(self, path: Path) -> None:
        """Save project state to file."""
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)

    @classmethod
    def load(cls, path: Path) -> 'ProjectState':
        """Load project state from file."""
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        state = cls(
            id=data["id"],
            name=data["name"],
            description=data["description"],
            current_stage=WorkflowStage(data["current_stage"]),
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"]),
            requirements=data.get("requirements", {}),
            architecture=data.get("architecture", {}),
            design=data.get("design", {}),
            implementation_plan=data.get("implementation_plan", {}),
            artifacts=data.get("artifacts", {}),
            decisions=data.get("decisions", []),
            client_feedback=data.get("client_feedback", []),
            metadata=data.get("metadata", {}),
        )

        # Restore tasks
        for task_id, task_data in data.get("tasks", {}).items():
            task = Task(
                id=task_data["id"],
                title=task_data["title"],
                description=task_data["description"],
                assigned_to=task_data.get("assigned_to"),
                status=TaskStatus(task_data["status"]),
                stage=WorkflowStage(task_data["stage"]),
                created_at=datetime.fromisoformat(task_data["created_at"]),
                updated_at=datetime.fromisoformat(task_data["updated_at"]),
                completed_at=datetime.fromisoformat(task_data["completed_at"])
                    if task_data.get("completed_at") else None,
                dependencies=task_data.get("dependencies", []),
                artifacts=task_data.get("artifacts", []),
                metadata=task_data.get("metadata", {}),
            )
            state.tasks[task_id] = task

        return state
