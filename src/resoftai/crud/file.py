"""CRUD operations for files and file versions."""
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime

from resoftai.models.file import File, FileVersion


# File operations

async def get_file(db: AsyncSession, file_id: int) -> Optional[File]:
    """Get file by ID."""
    result = await db.execute(
        select(File).where(File.id == file_id)
    )
    return result.scalar_one_or_none()


async def get_file_by_path(
    db: AsyncSession,
    project_id: int,
    path: str
) -> Optional[File]:
    """Get file by project and path."""
    result = await db.execute(
        select(File).where(
            File.project_id == project_id,
            File.path == path
        )
    )
    return result.scalar_one_or_none()


async def get_files_by_project(
    db: AsyncSession,
    project_id: int,
    skip: int = 0,
    limit: int = 100
) -> List[File]:
    """Get all files for a project."""
    result = await db.execute(
        select(File)
        .where(File.project_id == project_id)
        .order_by(File.path)
        .offset(skip)
        .limit(limit)
    )
    return list(result.scalars().all())


async def create_file(
    db: AsyncSession,
    project_id: int,
    path: str,
    content: str,
    language: Optional[str] = None,
    created_by: Optional[int] = None
) -> File:
    """Create a new file."""
    # Create file
    file = File(
        project_id=project_id,
        path=path,
        content=content,
        language=language,
        current_version=1
    )

    db.add(file)
    await db.flush()
    await db.refresh(file)

    # Create initial version
    version = FileVersion(
        file_id=file.id,
        version=1,
        content=content,
        created_by=created_by
    )

    db.add(version)
    await db.flush()

    return file


async def update_file(
    db: AsyncSession,
    file_id: int,
    content: str,
    created_by: Optional[int] = None
) -> Optional[File]:
    """Update file content and create new version."""
    file = await get_file(db, file_id)

    if not file:
        return None

    # Update file content
    file.content = content
    file.current_version += 1
    file.updated_at = datetime.utcnow()

    # Create new version
    version = FileVersion(
        file_id=file.id,
        version=file.current_version,
        content=content,
        created_by=created_by
    )

    db.add(version)
    await db.flush()
    await db.refresh(file)

    return file


async def delete_file(db: AsyncSession, file_id: int) -> bool:
    """Delete file and all its versions."""
    file = await get_file(db, file_id)

    if not file:
        return False

    # Delete all versions first (due to foreign key)
    await db.execute(
        select(FileVersion).where(FileVersion.file_id == file_id)
    )

    await db.delete(file)
    await db.flush()

    return True


async def count_project_files(db: AsyncSession, project_id: int) -> int:
    """Count files in a project."""
    from sqlalchemy import func

    result = await db.execute(
        select(func.count(File.id)).where(File.project_id == project_id)
    )
    return result.scalar_one()


# File version operations

async def get_file_version(
    db: AsyncSession,
    version_id: int
) -> Optional[FileVersion]:
    """Get file version by ID."""
    result = await db.execute(
        select(FileVersion).where(FileVersion.id == version_id)
    )
    return result.scalar_one_or_none()


async def get_file_versions(
    db: AsyncSession,
    file_id: int,
    skip: int = 0,
    limit: int = 50
) -> List[FileVersion]:
    """Get all versions of a file."""
    result = await db.execute(
        select(FileVersion)
        .where(FileVersion.file_id == file_id)
        .order_by(FileVersion.version.desc())
        .offset(skip)
        .limit(limit)
    )
    return list(result.scalars().all())


async def get_file_version_by_number(
    db: AsyncSession,
    file_id: int,
    version: int
) -> Optional[FileVersion]:
    """Get specific version of a file."""
    result = await db.execute(
        select(FileVersion).where(
            FileVersion.file_id == file_id,
            FileVersion.version == version
        )
    )
    return result.scalar_one_or_none()


async def restore_file_version(
    db: AsyncSession,
    file_id: int,
    version: int,
    created_by: Optional[int] = None
) -> Optional[File]:
    """Restore file to a specific version."""
    # Get the version to restore
    version_obj = await get_file_version_by_number(db, file_id, version)

    if not version_obj:
        return None

    # Update file with the version's content
    return await update_file(
        db,
        file_id=file_id,
        content=version_obj.content,
        created_by=created_by
    )


async def count_file_versions(db: AsyncSession, file_id: int) -> int:
    """Count versions of a file."""
    from sqlalchemy import func

    result = await db.execute(
        select(func.count(FileVersion.id)).where(FileVersion.file_id == file_id)
    )
    return result.scalar_one()
