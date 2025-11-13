"""Tests for file CRUD operations."""
import pytest
from unittest.mock import Mock, AsyncMock
from datetime import datetime

from resoftai.crud import file as crud_file
from resoftai.models.file import File, FileVersion


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
def mock_file():
    """Create mock file."""
    file = File(
        id=1,
        project_id=1,
        path="test.py",
        content="print('Hello, World!')",
        language="python",
        current_version=1,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    return file


@pytest.fixture
def mock_file_version():
    """Create mock file version."""
    version = FileVersion(
        id=1,
        file_id=1,
        version=1,
        content="print('Hello, World!')",
        created_by=1,
        created_at=datetime.utcnow()
    )
    return version


class TestFileCRUD:
    """Test file CRUD operations."""

    @pytest.mark.asyncio
    async def test_create_file(self, mock_db, mock_file):
        """Test creating a file."""
        # Mock the database operations
        mock_result = Mock()
        mock_result.scalar_one_or_none = Mock(return_value=None)  # File doesn't exist yet
        mock_db.execute = AsyncMock(return_value=mock_result)
        
        # Mock the refresh operation
        mock_db.refresh = AsyncMock()
        
        # Call the function
        file = await crud_file.create_file(
            mock_db,
            project_id=1,
            path="test.py",
            content="print('Hello, World!')",
            language="python",
            created_by=1
        )
        
        # Verify the file was created with correct attributes
        assert file is not None
        assert file.project_id == 1
        assert file.path == "test.py"
        assert file.content == "print('Hello, World!')"
        assert file.language == "python"
        assert file.current_version == 1
        
        # Verify database operations were called
        mock_db.add.assert_called()
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_file(self, mock_db, mock_file):
        """Test updating a file and creating new version."""
        # Mock getting existing file
        mock_result = Mock()
        mock_result.scalar_one_or_none = Mock(return_value=mock_file)
        mock_db.execute = AsyncMock(return_value=mock_result)
        
        # Call the function
        updated_file = await crud_file.update_file(
            mock_db,
            file_id=1,
            content="updated content",
            created_by=1
        )
        
        # Verify the file was updated
        assert updated_file is not None
        assert updated_file.current_version == 2
        assert updated_file.content == "updated content"
        
        # Verify database operations were called
        mock_db.execute.assert_called()
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once()

    @pytest.mark.asyncio
    async def test_restore_file_version(self, db: AsyncSession):
        """Test restoring a file to a previous version."""
        # Create test user and project
        test_user = User(
            username="test_restore_user",
            email="test_restore@example.com",
            password_hash="test_hash",
            role="user"
        )
        db.add(test_user)
        await db.flush()

        project = await create_project(
            db,
            name="Test Restore Project",
            requirements="Test project for file restoration",
            user_id=test_user.id
        )
        await db.commit()

        # Create file with multiple versions
        file = await crud_file.create_file(
            db,
            project_id=project.id,
            path="restore_test.py",
            content="version 1",
            language="python",
            created_by=test_user.id
        )
        await db.commit()

        await crud_file.update_file(
            db,
            file_id=file.id,
            content="version 2",
            created_by=test_user.id
        )
        await db.commit()

        await crud_file.update_file(
            db,
            file_id=file.id,
            content="version 3",
            created_by=test_user.id
        )
        await db.commit()

        # Restore to version 1
        restored_file = await crud_file.restore_file_version(
            db,
            file_id=file.id,
            version=1,
            created_by=test_user.id
        )
        await db.commit()

        assert restored_file.current_version == 4  # New version created
        assert restored_file.content == "version 1"

        # Verify we have 4 versions now
        versions = await crud_file.get_file_versions(db, file.id)
        assert len(versions) == 4
        assert versions[0].version == 4
        assert versions[0].content == "version 1"

    @pytest.mark.asyncio
    async def test_get_file_by_path(self, db: AsyncSession):
        """Test getting a file by project and path."""
        # Create test user and project
        test_user = User(
            username="test_path_user",
            email="test_path@example.com",
            password_hash="test_hash",
            role="user"
        )
        db.add(test_user)
        await db.flush()

        project = await create_project(
            db,
            name="Test Path Project",
            requirements="Test project for file path lookup",
            user_id=test_user.id
        )
        await db.commit()

        # Create file
        file = await crud_file.create_file(
            db,
            project_id=project.id,
            path="path_test.py",
            content="path test content",
            language="python",
            created_by=test_user.id
        )
        await db.commit()

        # Get file by path
        found_file = await crud_file.get_file_by_path(
            db,
            project_id=project.id,
            path="path_test.py"
        )

        assert found_file is not None
        assert found_file.id == file.id
        assert found_file.path == "path_test.py"

    @pytest.mark.asyncio
    async def test_list_project_files(self, db: AsyncSession):
        """Test listing files for a project."""
        # Create test user and project
        test_user = User(
            username="test_list_user",
            email="test_list@example.com",
            password_hash="test_hash",
            role="user"
        )
        db.add(test_user)
        await db.flush()

        project = await create_project(
            db,
            name="Test List Project",
            requirements="Test project for file listing",
            user_id=test_user.id
        )
        await db.commit()

        # Create multiple files
        files_data = [
            ("file1.py", "content1"),
            ("file2.py", "content2"),
            ("subdir/file3.py", "content3"),
        ]

        for path, content in files_data:
            await crud_file.create_file(
                db,
                project_id=project.id,
                path=path,
                content=content,
                language="python",
                created_by=test_user.id
            )
        await db.commit()

        # List files
        files = await crud_file.get_files_by_project(db, project.id)
        assert len(files) == 3

        # Check file paths
        paths = [f.path for f in files]
        assert "file1.py" in paths
        assert "file2.py" in paths
        assert "subdir/file3.py" in paths

        # Test count
        count = await crud_file.count_project_files(db, project.id)
        assert count == 3

    @pytest.mark.asyncio
    async def test_delete_file(self, db: AsyncSession):
        """Test deleting a file and its versions."""
        # Create test user and project
        test_user = User(
            username="test_delete_user",
            email="test_delete@example.com",
            password_hash="test_hash",
            role="user"
        )
        db.add(test_user)
        await db.flush()

        project = await create_project(
            db,
            name="Test Delete Project",
            requirements="Test project for file deletion",
            user_id=test_user.id
        )
        await db.commit()

        # Create file with versions
        file = await crud_file.create_file(
            db,
            project_id=project.id,
            path="delete_test.py",
            content="initial",
            language="python",
            created_by=test_user.id
        )
        await db.commit()

        await crud_file.update_file(
            db,
            file_id=file.id,
            content="updated",
            created_by=test_user.id
        )
        await db.commit()

        # Delete file
        result = await crud_file.delete_file(db, file.id)
        await db.commit()

        assert result is True

        # Verify file is gone
        deleted_file = await crud_file.get_file(db, file.id)
        assert deleted_file is None

        # Verify versions are gone
        versions = await crud_file.get_file_versions(db, file.id)
        assert len(versions) == 0