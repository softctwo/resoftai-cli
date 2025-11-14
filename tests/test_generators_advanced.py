"""Advanced tests for document generators."""
import pytest
from pathlib import Path
import tempfile
import shutil

from resoftai.core.state import ProjectState, WorkflowStage
from resoftai.generators.design_doc import DesignDocGenerator
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
def complex_project_state():
    """Create a complex project state for testing."""
    state = ProjectState(
        name="Complex Project",
        description="A comprehensive test project with multiple features",
        requirements={
            "initial_input": "Build a comprehensive e-commerce platform",
            "srs_document": "## Functional Requirements\n\n- User Management\n- Product Catalog\n- Shopping Cart\n- Payment Processing\n- Order Management",
            "organized_requirements": "Detailed requirements content"
        }
    )
    state.architecture = {
        "tech_stack": "Python/FastAPI + React",
        "components": ["API Server", "Web Client", "Database"],
        "deployment": "Docker + Kubernetes"
    }
    state.design = {
        "ui_components": ["Header", "ProductList", "ShoppingCart", "Checkout"],
        "api_endpoints": ["/api/products", "/api/cart", "/api/orders"]
    }
    state.decisions = [
        {
            "decision": "Use PostgreSQL for primary database",
            "made_by": "architect",
            "rationale": "Better performance for complex queries",
            "timestamp": "2025-01-01T10:00:00"
        },
        {
            "decision": "Use Redis for caching",
            "made_by": "architect",
            "rationale": "Improve response times",
            "timestamp": "2025-01-01T11:00:00"
        }
    ]
    return state


@pytest.mark.asyncio
async def test_design_doc_with_full_architecture(complex_project_state, temp_output_dir):
    """Test design doc generation with complete architecture."""
    generator = DesignDocGenerator(complex_project_state)

    file_path = await generator.generate(temp_output_dir)

    assert file_path.exists()
    content = file_path.read_text(encoding='utf-8')

    # Should include architecture details
    assert "Complex Project" in content
    assert "Architecture" in content or "Design" in content


@pytest.mark.asyncio
async def test_deployment_doc_includes_tech_stack(complex_project_state, temp_output_dir):
    """Test deployment doc includes technology stack."""
    generator = DeploymentDocGenerator(complex_project_state)

    file_path = await generator.generate(temp_output_dir)

    assert file_path.exists()
    content = file_path.read_text(encoding='utf-8')

    assert "Deployment" in content
    assert "Complex Project" in content


@pytest.mark.asyncio
async def test_training_manual_structure(complex_project_state, temp_output_dir):
    """Test training manual has proper structure."""
    generator = TrainingManualGenerator(complex_project_state)

    file_path = await generator.generate(temp_output_dir)

    assert file_path.exists()
    content = file_path.read_text(encoding='utf-8')

    # Should have training-related content
    assert "Training" in content or "Manual" in content
    assert "Complex Project" in content


@pytest.mark.asyncio
async def test_user_manual_structure(complex_project_state, temp_output_dir):
    """Test user manual has proper structure."""
    generator = UserManualGenerator(complex_project_state)

    file_path = await generator.generate(temp_output_dir)

    assert file_path.exists()
    content = file_path.read_text(encoding='utf-8')

    # Should have user manual content
    assert "User" in content or "Manual" in content
    assert "Complex Project" in content


@pytest.mark.asyncio
async def test_generator_handles_missing_optional_data(temp_output_dir):
    """Test generators handle missing optional data gracefully."""
    minimal_state = ProjectState(
        name="Minimal Project",
        description="Minimal test",
        requirements={"initial_input": "Simple app"}
    )

    # Should not raise exceptions
    generators = [
        DesignDocGenerator(minimal_state),
        DeploymentDocGenerator(minimal_state),
        TrainingManualGenerator(minimal_state),
        UserManualGenerator(minimal_state)
    ]

    for generator in generators:
        file_path = await generator.generate(temp_output_dir)
        assert file_path.exists()
        assert file_path.stat().st_size > 0


@pytest.mark.asyncio
async def test_concurrent_generator_execution(complex_project_state, temp_output_dir):
    """Test multiple generators running concurrently."""
    import asyncio

    generators = [
        DesignDocGenerator(complex_project_state),
        DeploymentDocGenerator(complex_project_state),
        TrainingManualGenerator(complex_project_state),
        UserManualGenerator(complex_project_state)
    ]

    # Run all generators concurrently
    tasks = [gen.generate(temp_output_dir) for gen in generators]
    file_paths = await asyncio.gather(*tasks)

    # All should complete successfully
    assert len(file_paths) == 4
    for path in file_paths:
        assert path.exists()
        assert path.stat().st_size > 0


@pytest.mark.asyncio
async def test_generator_creates_nested_directories(complex_project_state):
    """Test generator creates nested output directories if needed."""
    with tempfile.TemporaryDirectory() as tmpdir:
        nested_path = Path(tmpdir) / "docs" / "generated" / "output"

        generator = DesignDocGenerator(complex_project_state)
        file_path = await generator.generate(nested_path)

        assert file_path.exists()
        assert file_path.parent == nested_path


@pytest.mark.asyncio
async def test_generator_overwrites_existing_file(complex_project_state, temp_output_dir):
    """Test generator overwrites existing file."""
    generator = DesignDocGenerator(complex_project_state)

    # Generate once
    file_path1 = await generator.generate(temp_output_dir)
    content1 = file_path1.read_text()
    mtime1 = file_path1.stat().st_mtime

    # Wait a moment
    import time
    time.sleep(0.1)

    # Generate again
    file_path2 = await generator.generate(temp_output_dir)
    mtime2 = file_path2.stat().st_mtime

    assert file_path1 == file_path2
    assert mtime2 >= mtime1  # File was modified


@pytest.mark.asyncio
async def test_generator_preserves_unicode_content(temp_output_dir):
    """Test generator preserves unicode characters."""
    state = ProjectState(
        name="国际化项目",  # Chinese characters
        description="Support for émojis 🎉 and spëcial çharactërs",
        requirements={"initial_input": "Internationalization support"}
    )

    generator = DesignDocGenerator(state)
    file_path = await generator.generate(temp_output_dir)

    content = file_path.read_text(encoding='utf-8')

    assert "国际化项目" in content
    assert "émojis" in content
    assert "🎉" in content
