"""
Main CLI application for ResoftAI multi-agent platform.
"""

import click
import asyncio
import logging
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table
from rich import print as rprint

from resoftai import __version__
from resoftai.config.settings import get_settings
from resoftai.core.message_bus import MessageBus
from resoftai.core.state import ProjectState, WorkflowStage
from resoftai.core.workflow import ProjectWorkflow
from resoftai.agents import (
    ProjectManagerAgent,
    RequirementsAnalystAgent,
    ArchitectAgent,
    UXUIDesignerAgent,
    DeveloperAgent,
    TestEngineerAgent,
    QualityExpertAgent,
)
from resoftai.generators import (
    RequirementsDocGenerator,
    DesignDocGenerator,
    DatabaseDocGenerator,
    DeploymentDocGenerator,
    UserManualGenerator,
    TrainingManualGenerator,
)

console = Console()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@click.group()
@click.version_option(version=__version__)
def cli():
    """
    ResoftAI - Multi-Agent Software Development Platform

    AI-powered custom software development service using collaborative AI agents.
    """
    pass


@cli.command()
@click.argument('requirements', type=str)
@click.option('--name', '-n', default='New Project', help='Project name')
@click.option('--output', '-o', type=click.Path(), help='Output directory for deliverables')
@click.option('--interactive', '-i', is_flag=True, help='Interactive mode with user feedback')
def create(requirements: str, name: str, output: str, interactive: bool):
    """
    Create a new software project from requirements.

    REQUIREMENTS: Initial software requirements (text description)
    """
    asyncio.run(_create_project(requirements, name, output, interactive))


async def _create_project(requirements: str, name: str, output: str, interactive: bool):
    """Create a new project asynchronously."""

    console.print(Panel.fit(
        f"[bold green]ResoftAI Multi-Agent Platform v{__version__}[/bold green]\n"
        f"Creating project: [cyan]{name}[/cyan]",
        border_style="green"
    ))

    # Initialize settings
    settings = get_settings()

    # Determine output directory
    if output:
        output_dir = Path(output)
    else:
        output_dir = settings.workspace_dir / name.replace(' ', '_').lower()

    output_dir.mkdir(parents=True, exist_ok=True)

    console.print(f"[yellow]Output directory:[/yellow] {output_dir}")
    console.print(f"[yellow]Requirements:[/yellow] {requirements}\n")

    # Initialize core components
    message_bus = MessageBus()
    project_state = ProjectState(name=name, description=requirements)
    workflow = ProjectWorkflow(message_bus, project_state)

    # Initialize agents
    console.print("[bold]Initializing AI agents...[/bold]")
    agents = [
        ProjectManagerAgent(message_bus=message_bus, project_state=project_state),
        RequirementsAnalystAgent(message_bus=message_bus, project_state=project_state),
        ArchitectAgent(message_bus=message_bus, project_state=project_state),
        UXUIDesignerAgent(message_bus=message_bus, project_state=project_state),
        DeveloperAgent(message_bus=message_bus, project_state=project_state),
        TestEngineerAgent(message_bus=message_bus, project_state=project_state),
        QualityExpertAgent(message_bus=message_bus, project_state=project_state),
    ]

    # Display agent table
    agent_table = Table(title="Active Agents")
    agent_table.add_column("Agent", style="cyan")
    agent_table.add_column("Role", style="magenta")
    for agent in agents:
        agent_table.add_row(agent.name, agent.role.value)
    console.print(agent_table)
    console.print()

    # Start workflow
    console.print("[bold green]Starting project workflow...[/bold green]\n")

    try:
        # Start the workflow
        await workflow.start(requirements)

        # Process through workflow stages
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:

            for stage in workflow.WORKFLOW_SEQUENCE[:-1]:  # Exclude COMPLETED
                task = progress.add_task(
                    f"[cyan]Processing {stage.value}...",
                    total=None
                )

                # Simulate stage processing (in real implementation, wait for stage completion)
                await asyncio.sleep(0.5)  # Placeholder for actual processing

                # Complete the stage
                await workflow.complete_stage(stage)

                progress.update(task, completed=True)
                console.print(f"[green]✓[/green] Completed: {stage.value}")

                # Show progress
                progress_info = workflow.get_workflow_progress()
                console.print(
                    f"  Progress: {progress_info['progress_percentage']:.1f}% "
                    f"({progress_info['completed_tasks']}/{progress_info['total_tasks']} tasks)"
                )

        console.print("\n[bold green]Workflow completed![/bold green]\n")

        # Generate documentation
        console.print("[bold]Generating project documentation...[/bold]")
        docs_dir = output_dir / "documentation"
        docs_dir.mkdir(exist_ok=True)

        generators = [
            RequirementsDocGenerator(project_state),
            DesignDocGenerator(project_state),
            DatabaseDocGenerator(project_state),
            DeploymentDocGenerator(project_state),
            UserManualGenerator(project_state),
            TrainingManualGenerator(project_state),
        ]

        for generator in generators:
            doc_path = await generator.generate(docs_dir)
            console.print(f"[green]✓[/green] Generated: {doc_path.name}")

        # Save project state
        state_file = output_dir / "project_state.json"
        project_state.save(state_file)
        console.print(f"\n[green]✓[/green] Saved project state: {state_file}")

        # Display summary
        console.print("\n" + "="*70)
        console.print(Panel.fit(
            f"[bold green]Project Creation Complete![/bold green]\n\n"
            f"Project: [cyan]{name}[/cyan]\n"
            f"Output: [yellow]{output_dir}[/yellow]\n"
            f"Documentation: [yellow]{docs_dir}[/yellow]\n"
            f"State File: [yellow]{state_file}[/yellow]\n\n"
            f"Generated Documents:\n"
            f"  • Requirements Specification\n"
            f"  • Design Specification\n"
            f"  • Database Design\n"
            f"  • Deployment Guide\n"
            f"  • User Manual\n"
            f"  • Training Manual",
            border_style="green"
        ))

    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        logger.error(f"Error creating project: {e}", exc_info=True)
        raise click.Abort()


@cli.command()
@click.argument('state_file', type=click.Path(exists=True))
def status(state_file: str):
    """
    Show status of an existing project.

    STATE_FILE: Path to project state file
    """
    try:
        state = ProjectState.load(Path(state_file))

        console.print(Panel.fit(
            f"[bold]Project Status[/bold]\n\n"
            f"Name: [cyan]{state.name}[/cyan]\n"
            f"Stage: [yellow]{state.current_stage.value}[/yellow]\n"
            f"Created: {state.created_at.strftime('%Y-%m-%d %H:%M')}\n"
            f"Updated: {state.updated_at.strftime('%Y-%m-%d %H:%M')}",
            border_style="blue"
        ))

        # Tasks summary
        task_table = Table(title="Tasks Summary")
        task_table.add_column("Status", style="cyan")
        task_table.add_column("Count", style="magenta")

        from resoftai.core.state import TaskStatus
        for status_type in TaskStatus:
            count = len(state.get_tasks_by_status(status_type))
            task_table.add_row(status_type.value, str(count))

        console.print(task_table)

        # Artifacts
        if state.artifacts:
            console.print("\n[bold]Generated Artifacts:[/bold]")
            for artifact_type, path in state.artifacts.items():
                console.print(f"  • {artifact_type}: {path}")

    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        raise click.Abort()


@cli.command()
def info():
    """Display platform information and configuration."""
    settings = get_settings()

    info_table = Table(title="ResoftAI Platform Configuration")
    info_table.add_column("Setting", style="cyan")
    info_table.add_column("Value", style="yellow")

    info_table.add_row("Version", __version__)
    info_table.add_row("Claude Model", settings.claude_model)
    info_table.add_row("Workspace", str(settings.workspace_dir))
    info_table.add_row("Log Level", settings.log_level)

    console.print(info_table)


if __name__ == '__main__':
    cli()
