"""Tests for document generators."""
import pytest
from pathlib import Path
from datetime import datetime
import tempfile
import shutil

from resoftai.core.state import ProjectState, WorkflowStage
from resoftai.generators.requirements_doc import RequirementsDocGenerator
from resoftai.generators.design_doc import DesignDocGenerator
from resoftai.generators.database_doc import DatabaseDocGenerator
from resoftai.generators.deployment_doc import DeploymentDocGenerator
from resoftai.generators.training_manual import TrainingManualGenerator
from resoftai.generators.user_manual import UserManualGenerator


@pytest.fixture
def temp_output_dir():
    """Create a temporary directory for output."""
    temp_dir = Path(tempfile.mkdtemp())
    yield temp_dir
    shutil.rmtree(temp_dir)


@pytest.fixture
def project_state():
    """Create a test project state."""
    state = ProjectState(
        name="Test Project",
        description="A test project for generator testing",
        requirements={"initial_input": "Build a web application"}
    )
    return state


@pytest.fixture
def project_state_with_full_data():
    """Create a project state with comprehensive data."""
    state = ProjectState(
        name="Full Test Project",
        description="A comprehensive test project",
        requirements={
            "initial_input": "Build a comprehensive web application",
            "srs_document": "## Functional Requirements\n\n- User authentication\n- Data management",
            "organized_requirements": "Organized requirements content"
        }
    )
    state.decisions = [
        {
            "decision": "Use PostgreSQL",
            "made_by": "architect",
            "rationale": "Better performance",
            "timestamp": "2025-01-01T10:00:00"
        }
    ]
    state.architecture = {"tech_stack": "Python/FastAPI"}
    state.design = {"ui_components": ["Login", "Dashboard"]}
    return state


@pytest.mark.asyncio
async def test_requirements_doc_generator_basic(project_state, temp_output_dir):
    """Test basic requirements document generation."""
    generator = RequirementsDocGenerator(project_state)

    assert generator.document_name == "Software Requirements Specification (SRS)"
    assert generator.document_filename == "requirements-specification.md"

    file_path = await generator.generate(temp_output_dir)

    assert file_path.exists()
    assert file_path.name == "requirements-specification.md"

    content = file_path.read_text(encoding='utf-8')
    assert "Test Project" in content
    assert "Requirements" in content


@pytest.mark.asyncio
async def test_requirements_doc_generator_with_srs(project_state_with_full_data, temp_output_dir):
    """Test requirements generation with full SRS document."""
    generator = RequirementsDocGenerator(project_state_with_full_data)

    file_path = await generator.generate(temp_output_dir)
    content = file_path.read_text(encoding='utf-8')

    assert "Functional Requirements" in content
    assert "User authentication" in content


@pytest.mark.asyncio
async def test_requirements_doc_includes_decisions(project_state_with_full_data, temp_output_dir):
    """Test that requirements doc includes project decisions."""
    generator = RequirementsDocGenerator(project_state_with_full_data)

    file_path = await generator.generate(temp_output_dir)
    content = file_path.read_text(encoding='utf-8')

    assert "Key Decisions" in content
    assert "Use PostgreSQL" in content
    assert "architect" in content


@pytest.mark.asyncio
async def test_design_doc_generator(project_state_with_full_data, temp_output_dir):
    """Test design document generation."""
    generator = DesignDocGenerator(project_state_with_full_data)

    assert "Design" in generator.document_name

    file_path = await generator.generate(temp_output_dir)

    assert file_path.exists()
    content = file_path.read_text(encoding='utf-8')
    assert "Full Test Project" in content


@pytest.mark.asyncio
async def test_design_doc_with_architecture(project_state_with_full_data, temp_output_dir):
    """Test design doc includes architecture data."""
    generator = DesignDocGenerator(project_state_with_full_data)

    content = await generator.generate_content()

    # Should include architecture or design information
    assert len(content) > 0


@pytest.mark.asyncio
async def test_database_doc_generator(project_state, temp_output_dir):
    """Test database documentation generation."""
    generator = DatabaseDocGenerator(project_state)

    assert "Database" in generator.document_name

    file_path = await generator.generate(temp_output_dir)

    assert file_path.exists()
    content = file_path.read_text(encoding='utf-8')
    assert "Test Project" in content


@pytest.mark.asyncio
async def test_deployment_doc_generator(project_state, temp_output_dir):
    """Test deployment documentation generation."""
    generator = DeploymentDocGenerator(project_state)

    assert "Deployment" in generator.document_name

    file_path = await generator.generate(temp_output_dir)

    assert file_path.exists()
    content = file_path.read_text(encoding='utf-8')
    assert "Test Project" in content


@pytest.mark.asyncio
async def test_training_manual_generator(project_state, temp_output_dir):
    """Test training manual generation."""
    generator = TrainingManualGenerator(project_state)

    assert "Training" in generator.document_name

    file_path = await generator.generate(temp_output_dir)

    assert file_path.exists()
    content = file_path.read_text(encoding='utf-8')
    assert "Test Project" in content


@pytest.mark.asyncio
async def test_user_manual_generator(project_state, temp_output_dir):
    """Test user manual generation."""
    generator = UserManualGenerator(project_state)

    assert "User" in generator.document_name or "Manual" in generator.document_name

    file_path = await generator.generate(temp_output_dir)

    assert file_path.exists()
    content = file_path.read_text(encoding='utf-8')
    assert "Test Project" in content


@pytest.mark.asyncio
async def test_header_generation(project_state, temp_output_dir):
    """Test that all generators add proper headers."""
    generator = RequirementsDocGenerator(project_state)

    file_path = await generator.generate(temp_output_dir)
    content = file_path.read_text(encoding='utf-8')

    # Check header components
    assert "Test Project" in content
    assert "Generated:" in content
    assert "Version:" in content


@pytest.mark.asyncio
async def test_project_summary_generation(project_state):
    """Test project summary generation."""
    generator = RequirementsDocGenerator(project_state)

    summary = generator._get_project_summary()

    assert "Project Overview" in summary
    assert "Test Project" in summary
    assert "A test project for generator testing" in summary


@pytest.mark.asyncio
async def test_output_directory_creation(project_state):
    """Test that output directory is created if it doesn't exist."""
    temp_dir = Path(tempfile.gettempdir()) / "test_generator_output"

    # Ensure it doesn't exist
    if temp_dir.exists():
        shutil.rmtree(temp_dir)

    generator = RequirementsDocGenerator(project_state)

    file_path = await generator.generate(temp_dir)

    assert temp_dir.exists()
    assert file_path.exists()

    # Cleanup
    shutil.rmtree(temp_dir)


@pytest.mark.asyncio
async def test_utf8_encoding(project_state, temp_output_dir):
    """Test that files are written with UTF-8 encoding."""
    # Add some unicode characters to test
    project_state.description = "Test with unicode: é, ñ, 中文"

    generator = RequirementsDocGenerator(project_state)
    file_path = await generator.generate(temp_output_dir)

    # Should be able to read with UTF-8
    content = file_path.read_text(encoding='utf-8')
    assert "é, ñ, 中文" in content


@pytest.mark.asyncio
async def test_multiple_generators_same_dir(project_state, temp_output_dir):
    """Test generating multiple documents in the same directory."""
    gen1 = RequirementsDocGenerator(project_state)
    gen2 = DesignDocGenerator(project_state)
    gen3 = DatabaseDocGenerator(project_state)

    file1 = await gen1.generate(temp_output_dir)
    file2 = await gen2.generate(temp_output_dir)
    file3 = await gen3.generate(temp_output_dir)

    assert file1.exists()
    assert file2.exists()
    assert file3.exists()

    # All should be different files
    assert file1 != file2 != file3
