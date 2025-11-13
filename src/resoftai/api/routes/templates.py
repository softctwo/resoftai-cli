"""Templates API routes."""
from typing import List, Optional, Dict, Any
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException, status, Query, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field
import asyncio

from resoftai.db import get_db
from resoftai.models.user import User
from resoftai.auth.dependencies import get_current_active_user
from resoftai.templates.manager import TemplateManager
from resoftai.templates.registry import get_builtin_templates
from resoftai.websocket import sio

router = APIRouter(prefix="/templates", tags=["templates"])

# Initialize template manager
template_manager = TemplateManager()

# Register built-in templates on module load
for template in get_builtin_templates():
    template_manager.register_template(template)


# Request/Response Models
class VariableResponse(BaseModel):
    """Template variable response."""
    name: str
    description: str
    default: Any
    required: bool
    type: str
    choices: Optional[List[str]] = None


class TemplateListItem(BaseModel):
    """Template list item (minimal info)."""
    id: str
    name: str
    description: str
    category: str
    author: str
    version: str
    tags: List[str]
    file_count: int
    directory_count: int


class TemplateDetailResponse(BaseModel):
    """Template detail response (full info)."""
    id: str
    name: str
    description: str
    category: str
    author: str
    version: str
    variables: List[VariableResponse]
    requirements: Dict[str, Any]
    dependencies: List[str]
    tags: List[str]
    file_count: int
    directory_count: int


class TemplatePreviewResponse(BaseModel):
    """Template preview response."""
    id: str
    name: str
    description: str
    category: str
    variables: List[VariableResponse]
    files: List[Dict[str, Any]]
    directories: List[str]
    setup_commands: List[str]


class ApplyTemplateRequest(BaseModel):
    """Apply template request."""
    project_id: int = Field(..., description="Target project ID")
    variables: Dict[str, Any] = Field(..., description="Template variable values")
    overwrite: bool = Field(default=False, description="Overwrite existing files")


class ApplyTemplateResponse(BaseModel):
    """Apply template response."""
    success: bool
    message: str
    project_id: int
    files_created: int
    directories_created: int


# API Endpoints

@router.get("", response_model=List[TemplateListItem])
async def list_templates(
    category: Optional[str] = Query(None, description="Filter by category"),
    tags: Optional[str] = Query(None, description="Filter by tags (comma-separated)"),
    current_user: User = Depends(get_current_active_user)
):
    """
    List all available templates.

    Supports filtering by category and tags.

    Args:
        category: Optional category filter
        tags: Optional comma-separated tags filter
        current_user: Current authenticated user

    Returns:
        List of templates matching filters
    """
    # Parse tags
    tag_list = None
    if tags:
        tag_list = [tag.strip() for tag in tags.split(",")]

    # Get filtered templates
    templates = template_manager.list_templates(
        category=category,
        tags=tag_list
    )

    # Convert to response model
    return [
        TemplateListItem(**template.to_dict())
        for template in templates
    ]


@router.get("/{template_id}", response_model=TemplateDetailResponse)
async def get_template(
    template_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """
    Get template details by ID.

    Args:
        template_id: Template identifier
        current_user: Current authenticated user

    Returns:
        Template details

    Raises:
        HTTPException: If template not found
    """
    template = template_manager.get_template(template_id)
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Template '{template_id}' not found"
        )

    template_dict = template.to_dict()

    # Convert to response model
    return TemplateDetailResponse(
        id=template_dict["id"],
        name=template_dict["name"],
        description=template_dict["description"],
        category=template_dict["category"],
        author=template_dict["author"],
        version=template_dict["version"],
        variables=[VariableResponse(**var) for var in template_dict["variables"]],
        requirements=template_dict["requirements"],
        dependencies=template_dict["dependencies"],
        tags=template_dict["tags"],
        file_count=template_dict["file_count"],
        directory_count=template_dict["directory_count"]
    )


@router.get("/{template_id}/preview", response_model=TemplatePreviewResponse)
async def preview_template(
    template_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """
    Get template preview (structure without content).

    Args:
        template_id: Template identifier
        current_user: Current authenticated user

    Returns:
        Template preview data

    Raises:
        HTTPException: If template not found
    """
    preview = template_manager.get_template_preview(template_id)
    if not preview:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Template '{template_id}' not found"
        )

    return TemplatePreviewResponse(
        id=preview["id"],
        name=preview["name"],
        description=preview["description"],
        category=preview["category"],
        variables=[VariableResponse(**var) for var in preview["variables"]],
        files=preview["files"],
        directories=preview["directories"],
        setup_commands=preview["setup_commands"]
    )


async def apply_template_background(
    template_id: str,
    project_id: int,
    variables: Dict[str, Any],
    overwrite: bool,
    user_id: int
):
    """
    Background task to apply template with WebSocket progress updates.

    Args:
        template_id: Template to apply
        project_id: Target project ID
        variables: Variable values
        overwrite: Overwrite existing files
        user_id: User ID for WebSocket notifications
    """
    try:
        # Send start notification
        await sio.emit('template:apply:start', {
            'project_id': project_id,
            'template_id': template_id,
            'status': 'started'
        }, room=f'user_{user_id}')

        # Get template
        template = template_manager.get_template(template_id)
        if not template:
            await sio.emit('template:apply:error', {
                'project_id': project_id,
                'error': f"Template '{template_id}' not found"
            }, room=f'user_{user_id}')
            return

        # Validate variables
        await sio.emit('template:apply:progress', {
            'project_id': project_id,
            'step': 'validating',
            'message': 'Validating template variables...',
            'progress': 10
        }, room=f'user_{user_id}')

        is_valid, errors = template.validate_variables(variables)
        if not is_valid:
            await sio.emit('template:apply:error', {
                'project_id': project_id,
                'error': f"Variable validation failed: {', '.join(errors)}"
            }, room=f'user_{user_id}')
            return

        # Create output directory
        await sio.emit('template:apply:progress', {
            'project_id': project_id,
            'step': 'creating_structure',
            'message': 'Creating project structure...',
            'progress': 30
        }, room=f'user_{user_id}')

        # For now, we'll use a temporary directory
        # In production, this would integrate with the project file system
        output_dir = Path(f"/tmp/resoftai_project_{project_id}")

        # Create directories
        for i, dir_path in enumerate(template.directories):
            progress = 30 + int((i / len(template.directories)) * 30)
            await sio.emit('template:apply:progress', {
                'project_id': project_id,
                'step': 'creating_directories',
                'message': f'Creating directory: {dir_path}',
                'progress': progress
            }, room=f'user_{user_id}')
            await asyncio.sleep(0.1)  # Small delay for UI feedback

        # Create files
        for i, file in enumerate(template.files):
            progress = 60 + int((i / len(template.files)) * 30)
            await sio.emit('template:apply:progress', {
                'project_id': project_id,
                'step': 'creating_files',
                'message': f'Creating file: {file.path}',
                'progress': progress
            }, room=f'user_{user_id}')
            await asyncio.sleep(0.1)  # Small delay for UI feedback

        # Apply template
        success = template_manager.apply_template(
            template_id=template_id,
            output_dir=output_dir,
            variables=variables,
            overwrite=overwrite
        )

        if success:
            await sio.emit('template:apply:complete', {
                'project_id': project_id,
                'template_id': template_id,
                'status': 'completed',
                'files_created': len(template.files),
                'directories_created': len(template.directories),
                'output_path': str(output_dir),
                'progress': 100
            }, room=f'user_{user_id}')
        else:
            await sio.emit('template:apply:error', {
                'project_id': project_id,
                'error': 'Failed to apply template'
            }, room=f'user_{user_id}')

    except Exception as e:
        await sio.emit('template:apply:error', {
            'project_id': project_id,
            'error': str(e)
        }, room=f'user_{user_id}')


@router.post("/{template_id}/apply", response_model=ApplyTemplateResponse)
async def apply_template(
    template_id: str,
    request: ApplyTemplateRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Apply template to a project.

    This endpoint starts the template application process in the background
    and sends real-time progress updates via WebSocket.

    Args:
        template_id: Template to apply
        request: Application request with project ID and variables
        background_tasks: FastAPI background tasks
        current_user: Current authenticated user
        db: Database session

    Returns:
        Application status

    Raises:
        HTTPException: If template not found or validation fails
    """
    # Verify template exists
    template = template_manager.get_template(template_id)
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Template '{template_id}' not found"
        )

    # Quick validation (detailed validation in background task)
    is_valid, errors = template.validate_variables(request.variables)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Variable validation failed: {', '.join(errors)}"
        )

    # Start background task
    background_tasks.add_task(
        apply_template_background,
        template_id=template_id,
        project_id=request.project_id,
        variables=request.variables,
        overwrite=request.overwrite,
        user_id=current_user.id
    )

    return ApplyTemplateResponse(
        success=True,
        message=f"Template '{template_id}' application started. Monitor progress via WebSocket.",
        project_id=request.project_id,
        files_created=0,  # Will be updated in background
        directories_created=0  # Will be updated in background
    )


@router.get("/categories/list", response_model=List[str])
async def list_categories(
    current_user: User = Depends(get_current_active_user)
):
    """
    List all available template categories.

    Args:
        current_user: Current authenticated user

    Returns:
        List of category names
    """
    from resoftai.templates.base import TemplateCategory
    return [category.value for category in TemplateCategory]
