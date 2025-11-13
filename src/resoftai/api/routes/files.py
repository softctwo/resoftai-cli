"""API routes for file management."""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from resoftai.db import get_db
from resoftai.auth.dependencies import get_current_active_user
from resoftai.models.user import User
from resoftai.models.file import File, FileVersion
from resoftai.crud import file as crud_file
from resoftai.crud.project import get_project_by_id as get_project
from resoftai.api.errors import (
    NotFoundError, PermissionError, ConflictError, FileOperationError,
    handle_resoftai_error
)
from resoftai.monitoring.performance import monitor_request


router = APIRouter(prefix="/files", tags=["files"])


# Pydantic schemas

class FileCreate(BaseModel):
    """Schema for creating file."""
    project_id: int
    path: str
    content: str
    language: Optional[str] = None


class FileUpdate(BaseModel):
    """Schema for updating file."""
    content: str


class FileVersionResponse(BaseModel):
    """Schema for file version response."""
    id: int
    file_id: int
    version: int
    content: str
    created_at: str
    created_by: Optional[int]

    class Config:
        from_attributes = True

    @classmethod
    def from_orm(cls, version: FileVersion):
        return cls(
            id=version.id,
            file_id=version.file_id,
            version=version.version,
            content=version.content,
            created_at=version.created_at.isoformat(),
            created_by=version.created_by
        )


class FileResponse(BaseModel):
    """Schema for file response."""
    id: int
    project_id: int
    path: str
    content: Optional[str]
    language: Optional[str]
    current_version: int
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True

    @classmethod
    def from_orm(cls, file: File):
        return cls(
            id=file.id,
            project_id=file.project_id,
            path=file.path,
            content=file.content,
            language=file.language,
            current_version=file.current_version,
            created_at=file.created_at.isoformat(),
            updated_at=file.updated_at.isoformat()
        )


class FileListResponse(BaseModel):
    """Schema for file list response."""
    files: List[FileResponse]
    total: int
    skip: int
    limit: int


# File endpoints

@router.get("", response_model=FileListResponse)
@monitor_request
async def list_files(
    project_id: int = Query(..., description="Project ID"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """List files in a project."""
    # Verify user has access to the project
    project = await get_project(db, project_id)
    if not project:
        raise handle_resoftai_error(
            NotFoundError("Project", project_id)
        )

    if project.user_id != current_user.id and current_user.role != "admin":
        raise handle_resoftai_error(
            PermissionError("access", f"project {project_id}")
        )

    # Get files
    files = await crud_file.get_files_by_project(
        db,
        project_id=project_id,
        skip=skip,
        limit=limit
    )

    # Count total
    total = await crud_file.count_project_files(db, project_id)

    return FileListResponse(
        files=[FileResponse.from_orm(f) for f in files],
        total=total,
        skip=skip,
        limit=limit
    )


@monitor_request
@router.get("/{file_id}", response_model=FileResponse)
async def get_file(
    file_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get file by ID."""
    file = await crud_file.get_file(db, file_id)

    if not file:
        raise handle_resoftai_error(
            NotFoundError("File", file_id)
        )

    # Verify user has access
    project = await get_project(db, file.project_id)
    if project.user_id != current_user.id and current_user.role != "admin":
        raise handle_resoftai_error(
            PermissionError("access", f"file {file_id}")
        )

    return FileResponse.from_orm(file)


@router.post("", response_model=FileResponse, status_code=201)
async def create_file(
    file_data: FileCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new file."""
    # Verify user has access to the project
    project = await get_project(db, file_data.project_id)
    if not project:
        raise handle_resoftai_error(
            NotFoundError("Project", file_data.project_id)
        )

    if project.user_id != current_user.id and current_user.role != "admin":
        raise handle_resoftai_error(
            PermissionError("modify", f"project {file_data.project_id}")
        )

    # Check if file already exists
    existing = await crud_file.get_file_by_path(
        db,
        project_id=file_data.project_id,
        path=file_data.path
    )

    if existing:
        raise handle_resoftai_error(
            ConflictError("File", f"path already exists: {file_data.path}")
        )

    # Create file
    file = await crud_file.create_file(
        db,
        project_id=file_data.project_id,
        path=file_data.path,
        content=file_data.content,
        language=file_data.language,
        created_by=current_user.id
    )

    await db.commit()

    return FileResponse.from_orm(file)


@router.put("/{file_id}", response_model=FileResponse)
async def update_file(
    file_id: int,
    file_data: FileUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Update file content (creates new version)."""
    file = await crud_file.get_file(db, file_id)

    if not file:
        raise handle_resoftai_error(
            NotFoundError("File", file_id)
        )

    # Verify user has access
    project = await get_project(db, file.project_id)
    if project.user_id != current_user.id and current_user.role != "admin":
        raise handle_resoftai_error(
            PermissionError("modify", f"file {file_id}")
        )

    # Update file
    file = await crud_file.update_file(
        db,
        file_id=file_id,
        content=file_data.content,
        created_by=current_user.id
    )

    await db.commit()

    return FileResponse.from_orm(file)


@router.delete("/{file_id}", status_code=204)
async def delete_file(
    file_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete file."""
    file = await crud_file.get_file(db, file_id)

    if not file:
        raise handle_resoftai_error(
            NotFoundError("File", file_id)
        )

    # Verify user has access
    project = await get_project(db, file.project_id)
    if project.user_id != current_user.id and current_user.role != "admin":
        raise handle_resoftai_error(
            PermissionError("delete", f"file {file_id}")
        )

    await crud_file.delete_file(db, file_id)
    await db.commit()

    return None


# File version endpoints

@router.get("/{file_id}/versions", response_model=List[FileVersionResponse])
async def list_file_versions(
    file_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """List all versions of a file."""
    file = await crud_file.get_file(db, file_id)

    if not file:
        raise HTTPException(status_code=404, detail="File not found")

    # Verify user has access
    project = await get_project(db, file.project_id)
    if project.user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=403,
            detail="Not authorized to access this file"
        )

    # Get versions
    versions = await crud_file.get_file_versions(
        db,
        file_id=file_id,
        skip=skip,
        limit=limit
    )

    return [FileVersionResponse.from_orm(v) for v in versions]


@router.get("/{file_id}/versions/{version}", response_model=FileVersionResponse)
async def get_file_version(
    file_id: int,
    version: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get specific version of a file."""
    file = await crud_file.get_file(db, file_id)

    if not file:
        raise HTTPException(status_code=404, detail="File not found")

    # Verify user has access
    project = await get_project(db, file.project_id)
    if project.user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=403,
            detail="Not authorized to access this file"
        )

    # Get version
    version_obj = await crud_file.get_file_version_by_number(
        db,
        file_id=file_id,
        version=version
    )

    if not version_obj:
        raise HTTPException(
            status_code=404,
            detail=f"Version {version} not found"
        )

    return FileVersionResponse.from_orm(version_obj)


@router.post("/{file_id}/restore/{version}", response_model=FileResponse)
async def restore_file_version(
    file_id: int,
    version: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Restore file to a specific version."""
    file = await crud_file.get_file(db, file_id)

    if not file:
        raise HTTPException(status_code=404, detail="File not found")

    # Verify user has access
    project = await get_project(db, file.project_id)
    if project.user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=403,
            detail="Not authorized to modify this file"
        )

    # Restore version
    file = await crud_file.restore_file_version(
        db,
        file_id=file_id,
        version=version,
        created_by=current_user.id
    )

    if not file:
        raise HTTPException(
            status_code=404,
            detail=f"Version {version} not found"
        )

    await db.commit()

    return FileResponse.from_orm(file)
