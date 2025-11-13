"""Tests for file CRUD operations using mocks."""
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
        mock_db.flush.assert_called()
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
        mock_db.flush.assert_called()
        mock_db.refresh.assert_called_once()

    @pytest.mark.asyncio
    async def test_restore_file_version(self, mock_db, mock_file, mock_file_version):
        """Test restoring a file to a previous version."""
        # Mock getting file version
        mock_version_result = Mock()
        mock_version_result.scalar_one_or_none = Mock(return_value=mock_file_version)
        
        # Mock getting file
        mock_file_result = Mock()
        mock_file_result.scalar_one_or_none = Mock(return_value=mock_file)
        
        # Set up execute to return different results for different calls
        mock_db.execute = AsyncMock(side_effect=[mock_version_result, mock_file_result])
        
        # Call the function
        restored_file = await crud_file.restore_file_version(
            mock_db,
            file_id=1,
            version=1,
            created_by=1
        )
        
        # Verify the file was restored
        assert restored_file is not None
        assert restored_file.current_version == 2  # New version created
        assert restored_file.content == "print('Hello, World!')"
        
        # Verify database operations were called
        assert mock_db.execute.call_count == 2
        mock_db.flush.assert_called()
        mock_db.refresh.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_file_by_path(self, mock_db, mock_file):
        """Test getting a file by project and path."""
        # Mock the database operation
        mock_result = Mock()
        mock_result.scalar_one_or_none = Mock(return_value=mock_file)
        mock_db.execute = AsyncMock(return_value=mock_result)
        
        # Call the function
        found_file = await crud_file.get_file_by_path(
            mock_db,
            project_id=1,
            path="test.py"
        )
        
        # Verify the file was found
        assert found_file is not None
        assert found_file.id == 1
        assert found_file.path == "test.py"
        
        # Verify database operation was called
        mock_db.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_list_project_files(self, mock_db, mock_file):
        """Test listing files for a project."""
        # Mock the database operation
        mock_result = Mock()
        mock_scalars = Mock()
        mock_scalars.all = Mock(return_value=[mock_file])
        mock_result.scalars = Mock(return_value=mock_scalars)
        mock_db.execute = AsyncMock(return_value=mock_result)
        
        # Call the function
        files = await crud_file.get_files_by_project(mock_db, project_id=1)
        
        # Verify files were returned
        assert len(files) == 1
        assert files[0].id == 1
        assert files[0].path == "test.py"
        
        # Verify database operation was called
        mock_db.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_delete_file(self, mock_db, mock_file):
        """Test deleting a file and its versions."""
        # Mock getting existing file
        mock_result = Mock()
        mock_result.scalar_one_or_none = Mock(return_value=mock_file)
        mock_db.execute = AsyncMock(return_value=mock_result)
        
        # Call the function
        result = await crud_file.delete_file(mock_db, file_id=1)
        
        # Verify the file was deleted
        assert result is True
        
        # Verify database operations were called
        mock_db.execute.assert_called()
        mock_db.delete.assert_called()
        mock_db.flush.assert_called()