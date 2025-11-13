"""
FastAPI web server for ResoftAI platform.
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from pathlib import Path
import logging
from datetime import datetime

from resoftai import __version__
from resoftai.config.settings import get_settings
from resoftai.core.message_bus import MessageBus
from resoftai.core.state import ProjectState, WorkflowStage, TaskStatus
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

logger = logging.getLogger(__name__)

app = FastAPI(
    title="ResoftAI Multi-Agent Platform API",
    description="AI-powered custom software development service",
    version=__version__
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage for projects (in production, use a database)
projects: Dict[str, ProjectState] = {}


# Request/Response Models
class CreateProjectRequest(BaseModel):
    name: str
    requirements: str


class CreateProjectResponse(BaseModel):
    project_id: str
    name: str
    status: str
    message: str


class ProjectStatusResponse(BaseModel):
    project_id: str
    name: str
    current_stage: str
    progress_percentage: float
    total_tasks: int
    completed_tasks: int
    created_at: str
    updated_at: str


class TaskResponse(BaseModel):
    id: str
    title: str
    description: str
    assigned_to: Optional[str]
    status: str
    stage: str


# Routes
@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "name": "ResoftAI Multi-Agent Platform API",
        "version": __version__,
        "description": "AI-powered custom software development service",
        "endpoints": {
            "/projects": "Create and manage projects",
            "/projects/{project_id}": "Get project details",
            "/projects/{project_id}/status": "Get project status",
            "/health": "Health check"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": __version__
    }


@app.post("/projects", response_model=CreateProjectResponse)
async def create_project(
    request: CreateProjectRequest,
    background_tasks: BackgroundTasks
):
    """
    Create a new software development project.

    This endpoint initializes a new project with AI agents and starts
    the development workflow.
    """
    try:
        # Initialize project
        project_state = ProjectState(
            name=request.name,
            description=request.requirements
        )

        # Store project
        projects[project_state.id] = project_state

        # Schedule background workflow execution
        background_tasks.add_task(
            execute_project_workflow,
            project_state.id,
            request.requirements
        )

        logger.info(f"Created project: {project_state.id} - {request.name}")

        return CreateProjectResponse(
            project_id=project_state.id,
            name=request.name,
            status="started",
            message="Project created and workflow initiated"
        )

    except Exception as e:
        logger.error(f"Error creating project: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/projects/{project_id}", response_model=Dict[str, Any])
async def get_project(project_id: str):
    """Get detailed project information."""
    if project_id not in projects:
        raise HTTPException(status_code=404, detail="Project not found")

    project = projects[project_id]
    return project.to_dict()


@app.get("/projects/{project_id}/status", response_model=ProjectStatusResponse)
async def get_project_status(project_id: str):
    """Get project status and progress."""
    if project_id not in projects:
        raise HTTPException(status_code=404, detail="Project not found")

    project = projects[project_id]

    # Calculate progress
    workflow = ProjectWorkflow(MessageBus(), project)
    progress = workflow.get_workflow_progress()

    return ProjectStatusResponse(
        project_id=project.id,
        name=project.name,
        current_stage=project.current_stage.value,
        progress_percentage=progress["progress_percentage"],
        total_tasks=progress["total_tasks"],
        completed_tasks=progress["completed_tasks"],
        created_at=project.created_at.isoformat(),
        updated_at=project.updated_at.isoformat()
    )


@app.get("/projects/{project_id}/tasks", response_model=List[TaskResponse])
async def get_project_tasks(project_id: str):
    """Get all tasks for a project."""
    if project_id not in projects:
        raise HTTPException(status_code=404, detail="Project not found")

    project = projects[project_id]

    tasks = [
        TaskResponse(
            id=task.id,
            title=task.title,
            description=task.description,
            assigned_to=task.assigned_to,
            status=task.status.value,
            stage=task.stage.value
        )
        for task in project.tasks.values()
    ]

    return tasks


@app.get("/projects/{project_id}/artifacts")
async def get_project_artifacts(project_id: str):
    """Get generated artifacts for a project."""
    if project_id not in projects:
        raise HTTPException(status_code=404, detail="Project not found")

    project = projects[project_id]
    return {"artifacts": project.artifacts}


async def execute_project_workflow(project_id: str, requirements: str):
    """
    Execute the project workflow in the background.

    This is a simplified version for the API. In production, you would
    use a task queue like Celery or similar.
    """
    try:
        project = projects[project_id]

        # Initialize components
        message_bus = MessageBus()
        workflow = ProjectWorkflow(message_bus, project)

        # Initialize agents
        agents = [
            ProjectManagerAgent(message_bus=message_bus, project_state=project),
            RequirementsAnalystAgent(message_bus=message_bus, project_state=project),
            ArchitectAgent(message_bus=message_bus, project_state=project),
            UXUIDesignerAgent(message_bus=message_bus, project_state=project),
            DeveloperAgent(message_bus=message_bus, project_state=project),
            TestEngineerAgent(message_bus=message_bus, project_state=project),
            QualityExpertAgent(message_bus=message_bus, project_state=project),
        ]

        # Start workflow
        await workflow.start(requirements)

        # Process through stages (simplified)
        for stage in workflow.WORKFLOW_SEQUENCE[:-1]:
            await workflow.complete_stage(stage)

        logger.info(f"Completed workflow for project: {project_id}")

    except Exception as e:
        logger.error(f"Error executing workflow for project {project_id}: {e}", exc_info=True)
        # In production, update project status to 'failed'


if __name__ == "__main__":
    import uvicorn

    settings = get_settings()
    uvicorn.run(
        "resoftai.api.server:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.api_reload
    )
