"""
Example usage of ResoftAI multi-agent platform.
"""

import asyncio
from pathlib import Path

from resoftai.core.message_bus import MessageBus
from resoftai.core.state import ProjectState
from resoftai.core.workflow import ProjectWorkflow
from resoftai.agents import (
    ProjectManagerAgent,
    RequirementsAnalystAgent,
    ArchitectAgent,
)
from resoftai.generators import RequirementsDocGenerator


async def main():
    """Example: Create a simple project using the platform."""

    print("ResoftAI Multi-Agent Platform - Example Usage\n")
    print("=" * 60)

    # 1. Define requirements
    requirements = """
    Create a task management web application with the following features:
    - User authentication and authorization
    - Create, update, and delete tasks
    - Organize tasks into projects
    - Set task priorities and due dates
    - Assign tasks to team members
    - Track task completion status
    - Dashboard with task overview and statistics
    """

    print(f"\nRequirements:\n{requirements}\n")

    # 2. Initialize the platform
    print("Initializing platform components...")

    message_bus = MessageBus()
    project_state = ProjectState(
        name="Task Management Application",
        description=requirements
    )
    workflow = ProjectWorkflow(message_bus, project_state)

    # 3. Initialize agents
    print("Initializing AI agents...")

    from resoftai.core.agent import AgentRole

    agents = [
        ProjectManagerAgent(
            role=AgentRole.PROJECT_MANAGER,
            message_bus=message_bus,
            project_state=project_state
        ),
        RequirementsAnalystAgent(
            role=AgentRole.REQUIREMENTS_ANALYST,
            message_bus=message_bus,
            project_state=project_state
        ),
        ArchitectAgent(
            role=AgentRole.ARCHITECT,
            message_bus=message_bus,
            project_state=project_state
        ),
    ]

    for agent in agents:
        print(f"  - {agent.name} ({agent.role.value})")

    # 4. Start workflow
    print("\nStarting workflow...")
    await workflow.start(requirements)

    print(f"Current stage: {project_state.current_stage.value}")

    # 5. Process through a few stages (demo)
    print("\nProcessing workflow stages...")

    for stage in workflow.WORKFLOW_SEQUENCE[:3]:  # First 3 stages
        print(f"  Processing: {stage.value}...")
        await workflow.advance_to_stage(stage)
        await asyncio.sleep(0.5)  # Simulate processing

    # 6. Generate documentation
    print("\nGenerating requirements document...")

    output_dir = Path("./output")
    output_dir.mkdir(exist_ok=True)

    req_generator = RequirementsDocGenerator(project_state)
    doc_path = await req_generator.generate(output_dir)

    print(f"Document generated: {doc_path}")

    # 7. Display project summary
    print("\n" + "=" * 60)
    print("Project Summary:")
    print(f"  Name: {project_state.name}")
    print(f"  Stage: {project_state.current_stage.value}")
    print(f"  Total Tasks: {len(project_state.tasks)}")
    print(f"  Artifacts: {len(project_state.artifacts)}")

    print("\nExample completed successfully!")


if __name__ == "__main__":
    asyncio.run(main())
