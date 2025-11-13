"""
Comprehensive tests for core state management.
"""
import pytest
import json
from datetime import datetime
from pathlib import Path

from resoftai.core.state import (
    WorkflowStage,
    TaskStatus,
    Task,
    ProjectState
)


class TestWorkflowStage:
    """Test WorkflowStage enum."""

    def test_workflow_stages_exist(self):
        """Test all workflow stages are defined."""
        assert WorkflowStage.INITIAL == "initial"
        assert WorkflowStage.REQUIREMENTS_GATHERING == "requirements_gathering"
        assert WorkflowStage.REQUIREMENTS_ANALYSIS == "requirements_analysis"
        assert WorkflowStage.ARCHITECTURE_DESIGN == "architecture_design"
        assert WorkflowStage.UI_UX_DESIGN == "ui_ux_design"
        assert WorkflowStage.PROTOTYPE_DEVELOPMENT == "prototype_development"
        assert WorkflowStage.CLIENT_REVIEW == "client_review"
        assert WorkflowStage.REQUIREMENTS_REFINEMENT == "requirements_refinement"
        assert WorkflowStage.DEVELOPMENT_PLANNING == "development_planning"
        assert WorkflowStage.IMPLEMENTATION == "implementation"
        assert WorkflowStage.TESTING == "testing"
        assert WorkflowStage.QUALITY_ASSURANCE == "quality_assurance"
        assert WorkflowStage.DOCUMENTATION == "documentation"
        assert WorkflowStage.DEPLOYMENT == "deployment"
        assert WorkflowStage.COMPLETED == "completed"

    def test_workflow_stage_count(self):
        """Test correct number of workflow stages."""
        stages = list(WorkflowStage)
        assert len(stages) == 15


class TestTaskStatus:
    """Test TaskStatus enum."""

    def test_task_statuses_exist(self):
        """Test all task statuses are defined."""
        assert TaskStatus.PENDING == "pending"
        assert TaskStatus.IN_PROGRESS == "in_progress"
        assert TaskStatus.REVIEW == "review"
        assert TaskStatus.COMPLETED == "completed"
        assert TaskStatus.BLOCKED == "blocked"

    def test_task_status_count(self):
        """Test correct number of task statuses."""
        statuses = list(TaskStatus)
        assert len(statuses) == 5


class TestTask:
    """Test Task dataclass."""

    def test_task_creation_defaults(self):
        """Test task creation with defaults."""
        task = Task()

        assert task.id is not None
        assert len(task.id) > 0
        assert task.title == ""
        assert task.description == ""
        assert task.assigned_to is None
        assert task.status == TaskStatus.PENDING
        assert task.stage == WorkflowStage.INITIAL
        assert isinstance(task.created_at, datetime)
        assert isinstance(task.updated_at, datetime)
        assert task.completed_at is None
        assert task.dependencies == []
        assert task.artifacts == []
        assert task.metadata == {}

    def test_task_creation_with_params(self):
        """Test task creation with parameters."""
        task = Task(
            title="Test Task",
            description="Test description",
            assigned_to="agent1",
            status=TaskStatus.IN_PROGRESS,
            stage=WorkflowStage.IMPLEMENTATION,
            dependencies=["dep1", "dep2"],
            artifacts=["artifact1"],
            metadata={"key": "value"}
        )

        assert task.title == "Test Task"
        assert task.description == "Test description"
        assert task.assigned_to == "agent1"
        assert task.status == TaskStatus.IN_PROGRESS
        assert task.stage == WorkflowStage.IMPLEMENTATION
        assert task.dependencies == ["dep1", "dep2"]
        assert task.artifacts == ["artifact1"]
        assert task.metadata == {"key": "value"}

    def test_task_unique_ids(self):
        """Test that each task gets unique ID."""
        task1 = Task()
        task2 = Task()

        assert task1.id != task2.id

    def test_task_to_dict(self):
        """Test converting task to dictionary."""
        completed_time = datetime.now()
        task = Task(
            title="Test Task",
            description="Description",
            assigned_to="agent1",
            status=TaskStatus.COMPLETED,
            stage=WorkflowStage.TESTING,
            completed_at=completed_time,
            dependencies=["dep1"],
            artifacts=["art1"],
            metadata={"priority": "high"}
        )

        task_dict = task.to_dict()

        assert task_dict["id"] == task.id
        assert task_dict["title"] == "Test Task"
        assert task_dict["description"] == "Description"
        assert task_dict["assigned_to"] == "agent1"
        assert task_dict["status"] == "completed"
        assert task_dict["stage"] == "testing"
        assert isinstance(task_dict["created_at"], str)
        assert isinstance(task_dict["updated_at"], str)
        assert task_dict["completed_at"] == completed_time.isoformat()
        assert task_dict["dependencies"] == ["dep1"]
        assert task_dict["artifacts"] == ["art1"]
        assert task_dict["metadata"] == {"priority": "high"}

    def test_task_to_dict_no_completed_at(self):
        """Test task to_dict with no completion time."""
        task = Task(title="Test")
        task_dict = task.to_dict()

        assert task_dict["completed_at"] is None


class TestProjectStateBasic:
    """Test basic ProjectState functionality."""

    def test_project_state_creation_defaults(self):
        """Test project state creation with defaults."""
        state = ProjectState()

        assert state.id is not None
        assert len(state.id) > 0
        assert state.name == ""
        assert state.description == ""
        assert state.current_stage == WorkflowStage.INITIAL
        assert isinstance(state.created_at, datetime)
        assert isinstance(state.updated_at, datetime)
        assert state.requirements == {}
        assert state.architecture == {}
        assert state.design == {}
        assert state.implementation_plan == {}
        assert state.tasks == {}
        assert state.artifacts == {}
        assert state.decisions == []
        assert state.client_feedback == []
        assert state.metadata == {}

    def test_project_state_creation_with_params(self):
        """Test project state creation with parameters."""
        state = ProjectState(
            name="Test Project",
            description="Test description",
            current_stage=WorkflowStage.IMPLEMENTATION,
            requirements={"req1": "value1"},
            metadata={"key": "value"}
        )

        assert state.name == "Test Project"
        assert state.description == "Test description"
        assert state.current_stage == WorkflowStage.IMPLEMENTATION
        assert state.requirements == {"req1": "value1"}
        assert state.metadata == {"key": "value"}

    def test_project_state_unique_ids(self):
        """Test that each project state gets unique ID."""
        state1 = ProjectState()
        state2 = ProjectState()

        assert state1.id != state2.id


class TestProjectStateTasks:
    """Test ProjectState task management."""

    def test_add_task(self):
        """Test adding task to project."""
        state = ProjectState()
        task = Task(title="Test Task", assigned_to="agent1")

        initial_updated_at = state.updated_at
        state.add_task(task)

        assert task.id in state.tasks
        assert state.tasks[task.id] == task
        assert state.updated_at > initial_updated_at

    def test_add_multiple_tasks(self):
        """Test adding multiple tasks."""
        state = ProjectState()
        task1 = Task(title="Task 1")
        task2 = Task(title="Task 2")
        task3 = Task(title="Task 3")

        state.add_task(task1)
        state.add_task(task2)
        state.add_task(task3)

        assert len(state.tasks) == 3
        assert task1.id in state.tasks
        assert task2.id in state.tasks
        assert task3.id in state.tasks

    def test_update_task(self):
        """Test updating task fields."""
        state = ProjectState()
        task = Task(title="Original Title", status=TaskStatus.PENDING)
        state.add_task(task)

        state.update_task(
            task.id,
            title="Updated Title",
            status=TaskStatus.IN_PROGRESS,
            assigned_to="agent1"
        )

        updated_task = state.tasks[task.id]
        assert updated_task.title == "Updated Title"
        assert updated_task.status == TaskStatus.IN_PROGRESS
        assert updated_task.assigned_to == "agent1"

    def test_update_task_not_found(self):
        """Test updating non-existent task."""
        state = ProjectState()

        # Should not raise exception
        state.update_task("nonexistent-id", title="New Title")

        assert len(state.tasks) == 0

    def test_update_task_invalid_field(self):
        """Test updating task with invalid field."""
        state = ProjectState()
        task = Task(title="Test Task")
        state.add_task(task)

        # Invalid field should be ignored
        state.update_task(task.id, invalid_field="value")

        assert not hasattr(state.tasks[task.id], "invalid_field")

    def test_get_tasks_by_stage(self):
        """Test filtering tasks by stage."""
        state = ProjectState()
        task1 = Task(title="Task 1", stage=WorkflowStage.IMPLEMENTATION)
        task2 = Task(title="Task 2", stage=WorkflowStage.TESTING)
        task3 = Task(title="Task 3", stage=WorkflowStage.IMPLEMENTATION)

        state.add_task(task1)
        state.add_task(task2)
        state.add_task(task3)

        impl_tasks = state.get_tasks_by_stage(WorkflowStage.IMPLEMENTATION)
        test_tasks = state.get_tasks_by_stage(WorkflowStage.TESTING)

        assert len(impl_tasks) == 2
        assert len(test_tasks) == 1
        assert task1 in impl_tasks
        assert task3 in impl_tasks
        assert task2 in test_tasks

    def test_get_tasks_by_status(self):
        """Test filtering tasks by status."""
        state = ProjectState()
        task1 = Task(title="Task 1", status=TaskStatus.PENDING)
        task2 = Task(title="Task 2", status=TaskStatus.IN_PROGRESS)
        task3 = Task(title="Task 3", status=TaskStatus.IN_PROGRESS)
        task4 = Task(title="Task 4", status=TaskStatus.COMPLETED)

        state.add_task(task1)
        state.add_task(task2)
        state.add_task(task3)
        state.add_task(task4)

        pending_tasks = state.get_tasks_by_status(TaskStatus.PENDING)
        in_progress_tasks = state.get_tasks_by_status(TaskStatus.IN_PROGRESS)
        completed_tasks = state.get_tasks_by_status(TaskStatus.COMPLETED)

        assert len(pending_tasks) == 1
        assert len(in_progress_tasks) == 2
        assert len(completed_tasks) == 1


class TestProjectStateArtifacts:
    """Test ProjectState artifact management."""

    def test_add_artifact(self):
        """Test adding artifact."""
        state = ProjectState()

        initial_updated_at = state.updated_at
        state.add_artifact("design_doc", "/path/to/design.md")

        assert "design_doc" in state.artifacts
        assert state.artifacts["design_doc"] == "/path/to/design.md"
        assert state.updated_at > initial_updated_at

    def test_add_multiple_artifacts(self):
        """Test adding multiple artifacts."""
        state = ProjectState()

        state.add_artifact("requirements", "/path/to/requirements.md")
        state.add_artifact("architecture", "/path/to/architecture.md")
        state.add_artifact("design", "/path/to/design.md")

        assert len(state.artifacts) == 3
        assert state.artifacts["requirements"] == "/path/to/requirements.md"
        assert state.artifacts["architecture"] == "/path/to/architecture.md"
        assert state.artifacts["design"] == "/path/to/design.md"


class TestProjectStateDecisionsAndFeedback:
    """Test ProjectState decisions and feedback."""

    def test_add_decision(self):
        """Test recording project decision."""
        state = ProjectState()

        initial_updated_at = state.updated_at
        state.add_decision(
            decision="Use React for frontend",
            made_by="architect",
            rationale="Team expertise and ecosystem"
        )

        assert len(state.decisions) == 1
        decision = state.decisions[0]
        assert decision["decision"] == "Use React for frontend"
        assert decision["made_by"] == "architect"
        assert decision["rationale"] == "Team expertise and ecosystem"
        assert "timestamp" in decision
        assert state.updated_at > initial_updated_at

    def test_add_decision_without_rationale(self):
        """Test adding decision without rationale."""
        state = ProjectState()

        state.add_decision(
            decision="Deploy to AWS",
            made_by="project_manager"
        )

        decision = state.decisions[0]
        assert decision["rationale"] == ""

    def test_add_multiple_decisions(self):
        """Test adding multiple decisions."""
        state = ProjectState()

        state.add_decision("Decision 1", "agent1")
        state.add_decision("Decision 2", "agent2")
        state.add_decision("Decision 3", "agent3")

        assert len(state.decisions) == 3

    def test_add_client_feedback(self):
        """Test recording client feedback."""
        state = ProjectState()

        initial_updated_at = state.updated_at
        state.add_client_feedback(
            feedback="UI looks great, needs dark mode",
            stage=WorkflowStage.UI_UX_DESIGN
        )

        assert len(state.client_feedback) == 1
        feedback = state.client_feedback[0]
        assert feedback["feedback"] == "UI looks great, needs dark mode"
        assert feedback["stage"] == "ui_ux_design"
        assert "timestamp" in feedback
        assert state.updated_at > initial_updated_at

    def test_add_multiple_feedback(self):
        """Test adding multiple feedback items."""
        state = ProjectState()

        state.add_client_feedback("Feedback 1", WorkflowStage.REQUIREMENTS_GATHERING)
        state.add_client_feedback("Feedback 2", WorkflowStage.CLIENT_REVIEW)

        assert len(state.client_feedback) == 2


class TestProjectStateWorkflow:
    """Test ProjectState workflow progression."""

    def test_advance_stage(self):
        """Test advancing workflow stage."""
        state = ProjectState()
        assert state.current_stage == WorkflowStage.INITIAL

        initial_updated_at = state.updated_at
        state.advance_stage(WorkflowStage.REQUIREMENTS_GATHERING)

        assert state.current_stage == WorkflowStage.REQUIREMENTS_GATHERING
        assert state.updated_at > initial_updated_at

    def test_advance_through_multiple_stages(self):
        """Test progressing through multiple stages."""
        state = ProjectState()

        state.advance_stage(WorkflowStage.REQUIREMENTS_GATHERING)
        assert state.current_stage == WorkflowStage.REQUIREMENTS_GATHERING

        state.advance_stage(WorkflowStage.ARCHITECTURE_DESIGN)
        assert state.current_stage == WorkflowStage.ARCHITECTURE_DESIGN

        state.advance_stage(WorkflowStage.IMPLEMENTATION)
        assert state.current_stage == WorkflowStage.IMPLEMENTATION

        state.advance_stage(WorkflowStage.COMPLETED)
        assert state.current_stage == WorkflowStage.COMPLETED


class TestProjectStateSerialization:
    """Test ProjectState serialization/deserialization."""

    def test_to_dict_empty_state(self):
        """Test converting empty state to dictionary."""
        state = ProjectState(name="Test Project", description="Test desc")
        state_dict = state.to_dict()

        assert state_dict["id"] == state.id
        assert state_dict["name"] == "Test Project"
        assert state_dict["description"] == "Test desc"
        assert state_dict["current_stage"] == "initial"
        assert isinstance(state_dict["created_at"], str)
        assert isinstance(state_dict["updated_at"], str)
        assert state_dict["tasks"] == {}
        assert state_dict["artifacts"] == {}
        assert state_dict["decisions"] == []
        assert state_dict["client_feedback"] == []

    def test_to_dict_with_tasks(self):
        """Test to_dict with tasks."""
        state = ProjectState()
        task = Task(title="Test Task", status=TaskStatus.IN_PROGRESS)
        state.add_task(task)

        state_dict = state.to_dict()

        assert len(state_dict["tasks"]) == 1
        assert task.id in state_dict["tasks"]
        assert state_dict["tasks"][task.id]["title"] == "Test Task"

    def test_to_dict_complete_state(self):
        """Test to_dict with complete state."""
        state = ProjectState(
            name="Complete Project",
            requirements={"req1": "value1"},
            architecture={"arch1": "value1"}
        )

        task = Task(title="Task 1")
        state.add_task(task)
        state.add_artifact("doc", "/path/to/doc")
        state.add_decision("Decision 1", "agent1", "Reason")
        state.add_client_feedback("Feedback 1", WorkflowStage.CLIENT_REVIEW)

        state_dict = state.to_dict()

        assert state_dict["name"] == "Complete Project"
        assert state_dict["requirements"] == {"req1": "value1"}
        assert state_dict["architecture"] == {"arch1": "value1"}
        assert len(state_dict["tasks"]) == 1
        assert len(state_dict["artifacts"]) == 1
        assert len(state_dict["decisions"]) == 1
        assert len(state_dict["client_feedback"]) == 1

    def test_save_and_load(self, tmp_path):
        """Test saving and loading project state."""
        # Create state
        original_state = ProjectState(
            name="Saved Project",
            description="Test save/load",
            current_stage=WorkflowStage.IMPLEMENTATION,
            requirements={"req1": "value1"},
            architecture={"arch1": "value1"}
        )

        task1 = Task(title="Task 1", status=TaskStatus.IN_PROGRESS)
        task2 = Task(title="Task 2", status=TaskStatus.COMPLETED, completed_at=datetime.now())
        original_state.add_task(task1)
        original_state.add_task(task2)

        original_state.add_artifact("design", "/path/to/design.md")
        original_state.add_decision("Use PostgreSQL", "architect", "Reliable and scalable")
        original_state.add_client_feedback("Looks good", WorkflowStage.CLIENT_REVIEW)

        # Save to file
        state_file = tmp_path / "project_state.json"
        original_state.save(state_file)

        # Load from file
        loaded_state = ProjectState.load(state_file)

        # Verify
        assert loaded_state.id == original_state.id
        assert loaded_state.name == original_state.name
        assert loaded_state.description == original_state.description
        assert loaded_state.current_stage == original_state.current_stage
        assert loaded_state.requirements == original_state.requirements
        assert loaded_state.architecture == original_state.architecture
        assert len(loaded_state.tasks) == 2
        assert loaded_state.artifacts == original_state.artifacts
        assert len(loaded_state.decisions) == 1
        assert len(loaded_state.client_feedback) == 1

    def test_load_preserves_task_data(self, tmp_path):
        """Test loading preserves all task data."""
        original_state = ProjectState()
        task = Task(
            title="Complex Task",
            description="Test description",
            assigned_to="agent1",
            status=TaskStatus.IN_PROGRESS,
            stage=WorkflowStage.TESTING,
            dependencies=["dep1", "dep2"],
            artifacts=["art1"],
            metadata={"key": "value"}
        )
        original_state.add_task(task)

        state_file = tmp_path / "state.json"
        original_state.save(state_file)

        loaded_state = ProjectState.load(state_file)
        loaded_task = loaded_state.tasks[task.id]

        assert loaded_task.title == task.title
        assert loaded_task.description == task.description
        assert loaded_task.assigned_to == task.assigned_to
        assert loaded_task.status == task.status
        assert loaded_task.stage == task.stage
        assert loaded_task.dependencies == task.dependencies
        assert loaded_task.artifacts == task.artifacts
        assert loaded_task.metadata == task.metadata


class TestProjectStateIntegration:
    """Integration tests for ProjectState."""

    def test_complete_workflow_simulation(self):
        """Test simulating complete project workflow."""
        # Initialize project
        state = ProjectState(
            name="Complete Workflow Test",
            description="Simulating full workflow"
        )

        # Requirements gathering
        state.advance_stage(WorkflowStage.REQUIREMENTS_GATHERING)
        req_task = Task(
            title="Gather requirements",
            stage=WorkflowStage.REQUIREMENTS_GATHERING,
            assigned_to="requirements_analyst"
        )
        state.add_task(req_task)
        state.update_task(req_task.id, status=TaskStatus.COMPLETED)
        state.add_artifact("requirements", "/docs/requirements.md")

        # Architecture design
        state.advance_stage(WorkflowStage.ARCHITECTURE_DESIGN)
        arch_task = Task(
            title="Design architecture",
            stage=WorkflowStage.ARCHITECTURE_DESIGN,
            assigned_to="architect"
        )
        state.add_task(arch_task)
        state.add_decision("Use microservices", "architect", "Scalability")

        # Client review
        state.advance_stage(WorkflowStage.CLIENT_REVIEW)
        state.add_client_feedback("Approve architecture", WorkflowStage.CLIENT_REVIEW)

        # Implementation
        state.advance_stage(WorkflowStage.IMPLEMENTATION)
        impl_task = Task(
            title="Implement API",
            stage=WorkflowStage.IMPLEMENTATION,
            assigned_to="developer"
        )
        state.add_task(impl_task)

        # Verify state
        assert state.current_stage == WorkflowStage.IMPLEMENTATION
        assert len(state.tasks) == 3
        assert len(state.artifacts) == 1
        assert len(state.decisions) == 1
        assert len(state.client_feedback) == 1

        # Verify task filtering
        impl_tasks = state.get_tasks_by_stage(WorkflowStage.IMPLEMENTATION)
        assert len(impl_tasks) == 1

        completed_tasks = state.get_tasks_by_status(TaskStatus.COMPLETED)
        assert len(completed_tasks) == 1
