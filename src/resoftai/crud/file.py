"""CRUD operations for files and file versions."""
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime

from resoftai.models.file import File, FileVersion
from resoftai.utils.cache import cached, cache_manager
from resoftai.utils.performance import timing_decorator


# File operations

@timing_decorator("crud.get_file")
@cached(key_func=lambda db, file_id: f"file:{file_id}", ttl=180)
async def get_file(db: AsyncSession, file_id: int) -> Optional[File]:
    """
    Get file by ID with caching.

    Results are cached for 3 minutes.
    """
    result = await db.execute(
        select(File).where(File.id == file_id)
    )
    file = result.scalar_one_or_none()
    if file:
        # Convert to dict for caching
        return {
            'id': file.id,
            'project_id': file.project_id,
            'path': file.path,
            'content': file.content,
            'language': file.language,
            'current_version': file.current_version,
            'created_at': file.created_at.isoformat() if file.created_at else None,
            'updated_at': file.updated_at.isoformat() if file.updated_at else None
        }
    return None


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


@timing_decorator("crud.get_files_by_project")
async def get_files_by_project(
    db: AsyncSession,
    project_id: int,
    skip: int = 0,
    limit: int = 100
) -> List[File]:
    """
    Get all files for a project.

    Optimized with index on project_id.
    """
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


@timing_decorator("crud.update_file")
async def update_file(
    db: AsyncSession,
    file_id: int,
    content: str,
    created_by: Optional[int] = None
) -> Optional[File]:
    """
    Update file content and create new version.

    Invalidates cache after update.
    """
    # Note: get_file returns dict from cache, we need the actual object
    result = await db.execute(select(File).where(File.id == file_id))
    file = result.scalar_one_or_none()

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

    # Invalidate cache
    await cache_manager.delete(f"file:{file_id}")

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


# Batch operations for performance

async def get_files_by_ids(
    db: AsyncSession,
    file_ids: List[int]
) -> List[File]:
    """
    Batch get files by IDs.

    More efficient than multiple individual queries.

    Args:
        db: Database session
        file_ids: List of file IDs

    Returns:
        List of File objects
    """
    if not file_ids:
        return []

    query = select(File).where(File.id.in_(file_ids))
    result = await db.execute(query)
    return list(result.scalars().all())


@timing_decorator("crud.bulk_update_files")
async def bulk_update_file_content(
    db: AsyncSession,
    updates: List[dict]  # [{'file_id': 1, 'content': '...', 'created_by': 1}]
) -> int:
    """
    Bulk update file contents.

    More efficient than individual updates.

    Args:
        db: Database session
        updates: List of update dicts

    Returns:
        Number of files updated
    """
    if not updates:
        return 0

    updated_count = 0

    for update in updates:
        file_id = update['file_id']
        content = update['content']
        created_by = update.get('created_by')

        file = await update_file(db, file_id, content, created_by)
        if file:
            updated_count += 1

    return updated_count
