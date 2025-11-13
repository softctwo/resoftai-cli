"""
Comprehensive tests for CRUD project operations.
"""
import pytest
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime

from resoftai.crud.project import (
    get_project_by_id,
    get_projects_by_user,
    count_user_projects,
    create_project,
    update_project,
    delete_project,
    update_project_progress
)
from resoftai.models.project import Project


@pytest.fixture
def mock_db():
    """Create mock database session."""
    db = AsyncMock()
    db.commit = AsyncMock()
    db.refresh = AsyncMock()
    db.delete = AsyncMock()
    db.add = Mock()
    return db


@pytest.fixture
def mock_project():
    """Create mock project."""
    project = Project(
        id=1,
        user_id=1,
        name="Test Project",
        requirements="Build a test app",
        status="pending",
        progress=0,
        llm_provider="deepseek",
        llm_model="deepseek-chat",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    return project


class TestGetProject:
    """Test get project functions."""

    @pytest.mark.asyncio
    async def test_get_project_by_id_found(self, mock_db, mock_project):
        """Test getting project by ID when exists."""
        mock_result = Mock()
        mock_result.scalar_one_or_none = Mock(return_value=mock_project)
        mock_db.execute = AsyncMock(return_value=mock_result)

        project = await get_project_by_id(mock_db, 1)

        assert project is not None
        assert project.id == 1
        assert project.name == "Test Project"
        mock_db.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_project_by_id_not_found(self, mock_db):
        """Test getting project by ID when doesn't exist."""
        mock_result = Mock()
        mock_result.scalar_one_or_none = Mock(return_value=None)
        mock_db.execute = AsyncMock(return_value=mock_result)

        project = await get_project_by_id(mock_db, 999)

        assert project is None
        mock_db.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_projects_by_user(self, mock_db):
        """Test getting projects by user."""
        # Create multiple mock projects
        projects = [
            Project(id=i, user_id=1, name=f"Project {i}", requirements="Req",
                   status="pending", progress=0, created_at=datetime.utcnow(),
                   updated_at=datetime.utcnow())
            for i in range(1, 4)
        ]

        mock_result = Mock()
        mock_scalars = Mock()
        mock_scalars.all = Mock(return_value=projects)
        mock_result.scalars = Mock(return_value=mock_scalars)
        mock_db.execute = AsyncMock(return_value=mock_result)

        result = await get_projects_by_user(mock_db, user_id=1)

        assert len(result) == 3
        assert all(p.user_id == 1 for p in result)
        mock_db.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_projects_by_user_with_status_filter(self, mock_db):
        """Test getting projects with status filter."""
        completed_projects = [
            Project(id=1, user_id=1, name="Project 1", requirements="Req",
                   status="completed", progress=100, created_at=datetime.utcnow(),
                   updated_at=datetime.utcnow())
        ]

        mock_result = Mock()
        mock_scalars = Mock()
        mock_scalars.all = Mock(return_value=completed_projects)
        mock_result.scalars = Mock(return_value=mock_scalars)
        mock_db.execute = AsyncMock(return_value=mock_result)

        result = await get_projects_by_user(mock_db, user_id=1, status="completed")

        assert len(result) == 1
        assert result[0].status == "completed"


class TestCreateProject:
    """Test create project function."""

    @pytest.mark.asyncio
    async def test_create_project_basic(self, mock_db):
        """Test basic project creation."""
        async def mock_refresh(project):
            project.id = 1

        mock_db.refresh = mock_refresh

        project = await create_project(
            mock_db,
            user_id=1,
            name="New Project",
            requirements="Build something"
        )

        assert project.id == 1
        assert project.user_id == 1
        assert project.name == "New Project"
        assert project.requirements == "Build something"
        assert project.status == "pending"
        assert project.progress == 0
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()


class TestUpdateProject:
    """Test update project function."""

    @pytest.mark.asyncio
    async def test_update_project_success(self, mock_db, mock_project):
        """Test successful project update."""
        mock_result = Mock()
        mock_result.scalar_one_or_none = Mock(return_value=mock_project)
        mock_db.execute = AsyncMock(return_value=mock_result)

        updated = await update_project(
            mock_db,
            project_id=1,
            name="Updated Name",
            status="in_progress"
        )

        assert updated is not None
        assert updated.name == "Updated Name"
        assert updated.status == "in_progress"
        assert updated.updated_at is not None
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_project_not_found(self, mock_db):
        """Test updating non-existent project."""
        mock_result = Mock()
        mock_result.scalar_one_or_none = Mock(return_value=None)
        mock_db.execute = AsyncMock(return_value=mock_result)

        updated = await update_project(mock_db, project_id=999, name="Test")

        assert updated is None
        mock_db.commit.assert_not_called()


class TestDeleteProject:
    """Test delete project function."""

    @pytest.mark.asyncio
    async def test_delete_project_success(self, mock_db, mock_project):
        """Test successful project deletion."""
        mock_result = Mock()
        mock_result.scalar_one_or_none = Mock(return_value=mock_project)
        mock_db.execute = AsyncMock(return_value=mock_result)

        result = await delete_project(mock_db, 1)

        assert result is True
        mock_db.delete.assert_called_once_with(mock_project)
        mock_db.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_delete_project_not_found(self, mock_db):
        """Test deleting non-existent project."""
        mock_result = Mock()
        mock_result.scalar_one_or_none = Mock(return_value=None)
        mock_db.execute = AsyncMock(return_value=mock_result)

        result = await delete_project(mock_db, 999)

        assert result is False
        mock_db.delete.assert_not_called()
        mock_db.commit.assert_not_called()
