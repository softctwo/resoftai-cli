"""
Comprehensive tests for project template system.
"""
import pytest
from pathlib import Path

from resoftai.templates.base import (
    Template,
    TemplateVariable,
    TemplateFile,
    TemplateCategory
)
from resoftai.templates.manager import TemplateManager
from resoftai.templates.registry import (
    get_builtin_templates,
    create_rest_api_template,
    create_web_app_template,
    create_cli_tool_template,
)


class TestTemplateVariable:
    """Test TemplateVariable class."""

    def test_variable_creation(self):
        """Test creating template variable."""
        var = TemplateVariable(
            name="project_name",
            description="Project name",
            default="myproject",
            required=True,
            type="string"
        )

        assert var.name == "project_name"
        assert var.description == "Project name"
        assert var.default == "myproject"
        assert var.required is True
        assert var.type == "string"

    def test_validate_string(self):
        """Test validating string variable."""
        var = TemplateVariable(name="test", description="Test", type="string", required=True)

        assert var.validate("value") is True
        assert var.validate("") is False
        assert var.validate(None) is False

    def test_validate_integer(self):
        """Test validating integer variable."""
        var = TemplateVariable(name="port", description="Port", type="integer", required=True)

        assert var.validate(8000) is True
        assert var.validate("8000") is True
        assert var.validate("abc") is False

    def test_validate_boolean(self):
        """Test validating boolean variable."""
        var = TemplateVariable(name="enabled", description="Enabled", type="boolean")

        assert var.validate(True) is True
        assert var.validate(False) is True
        assert var.validate("true") is True
        assert var.validate("false") is True
        assert var.validate("yes") is False

    def test_validate_choice(self):
        """Test validating choice variable."""
        var = TemplateVariable(
            name="language",
            description="Language",
            type="choice",
            choices=["python", "javascript", "go"]
        )

        assert var.validate("python") is True
        assert var.validate("javascript") is True
        assert var.validate("ruby") is False

    def test_validate_optional(self):
        """Test validating optional variable."""
        var = TemplateVariable(name="test", description="Test", required=False)

        assert var.validate("") is True
        assert var.validate(None) is True


class TestTemplateFile:
    """Test TemplateFile class."""

    def test_file_creation(self):
        """Test creating template file."""
        file = TemplateFile(
            path="README.md",
            content="# Project",
            is_template=True,
            executable=False
        )

        assert file.path == "README.md"
        assert file.content == "# Project"
        assert file.is_template is True
        assert file.is_binary is False
        assert file.executable is False


class TestTemplate:
    """Test Template class."""

    def test_template_creation(self):
        """Test creating template."""
        template = Template(
            id="test-template",
            name="Test Template",
            description="A test template",
            category=TemplateCategory.REST_API,
            author="Test Author",
            version="1.0.0"
        )

        assert template.id == "test-template"
        assert template.name == "Test Template"
        assert template.category == TemplateCategory.REST_API
        assert template.author == "Test Author"

    def test_get_variable(self):
        """Test getting variable by name."""
        var1 = TemplateVariable(name="var1", description="Var 1")
        var2 = TemplateVariable(name="var2", description="Var 2")

        template = Template(
            id="test",
            name="Test",
            description="Test",
            category=TemplateCategory.CLI_TOOL,
            variables=[var1, var2]
        )

        assert template.get_variable("var1") == var1
        assert template.get_variable("var2") == var2
        assert template.get_variable("nonexistent") is None

    def test_validate_variables_success(self):
        """Test successful variable validation."""
        template = Template(
            id="test",
            name="Test",
            description="Test",
            category=TemplateCategory.WEB_APP,
            variables=[
                TemplateVariable(name="name", description="Name", required=True),
                TemplateVariable(name="port", description="Port", type="integer", required=False),
            ]
        )

        is_valid, errors = template.validate_variables({"name": "myproject", "port": 8000})

        assert is_valid is True
        assert len(errors) == 0

    def test_validate_variables_missing_required(self):
        """Test validation fails for missing required variable."""
        template = Template(
            id="test",
            name="Test",
            description="Test",
            category=TemplateCategory.REST_API,
            variables=[
                TemplateVariable(name="name", description="Name", required=True),
            ]
        )

        is_valid, errors = template.validate_variables({})

        assert is_valid is False
        assert len(errors) == 1
        assert "Required variable 'name' is missing" in errors[0]

    def test_validate_variables_invalid_type(self):
        """Test validation fails for invalid type."""
        template = Template(
            id="test",
            name="Test",
            description="Test",
            category=TemplateCategory.CLI_TOOL,
            variables=[
                TemplateVariable(name="port", description="Port", type="integer", required=True),
            ]
        )

        is_valid, errors = template.validate_variables({"port": "invalid"})

        assert is_valid is False
        assert len(errors) == 1
        assert "Invalid value for variable 'port'" in errors[0]

    def test_to_dict(self):
        """Test converting template to dictionary."""
        template = Template(
            id="test",
            name="Test Template",
            description="Test description",
            category=TemplateCategory.MICROSERVICE,
            variables=[
                TemplateVariable(name="name", description="Name"),
            ],
            tags=["python", "test"]
        )

        result = template.to_dict()

        assert result["id"] == "test"
        assert result["name"] == "Test Template"
        assert result["category"] == "microservice"
        assert len(result["variables"]) == 1
        assert result["tags"] == ["python", "test"]


class TestTemplateManager:
    """Test TemplateManager class."""

    @pytest.fixture
    def manager(self):
        """Create template manager."""
        return TemplateManager()

    @pytest.fixture
    def sample_template(self):
        """Create sample template."""
        return Template(
            id="sample",
            name="Sample Template",
            description="A sample",
            category=TemplateCategory.REST_API,
            variables=[
                TemplateVariable(name="project_name", description="Project name", required=True),
            ],
            directories=["src", "tests"],
            files=[
                TemplateFile(
                    path="README.md",
                    content="# {{project_name}}\n\nProject: {{project_name|upper}}",
                    is_template=True
                ),
                TemplateFile(
                    path="src/main.py",
                    content='print("{{project_name}}")',
                    is_template=True
                ),
            ]
        )

    def test_register_template(self, manager, sample_template):
        """Test registering template."""
        manager.register_template(sample_template)

        assert "sample" in manager._templates
        assert manager._templates["sample"] == sample_template

    def test_get_template(self, manager, sample_template):
        """Test getting template."""
        manager.register_template(sample_template)

        result = manager.get_template("sample")
        assert result == sample_template

        assert manager.get_template("nonexistent") is None

    def test_list_templates_all(self, manager):
        """Test listing all templates."""
        t1 = Template(id="t1", name="T1", description="T1", category=TemplateCategory.REST_API)
        t2 = Template(id="t2", name="T2", description="T2", category=TemplateCategory.WEB_APP)

        manager.register_template(t1)
        manager.register_template(t2)

        templates = manager.list_templates()
        assert len(templates) == 2

    def test_list_templates_by_category(self, manager):
        """Test listing templates by category."""
        t1 = Template(id="t1", name="T1", description="T1", category=TemplateCategory.REST_API)
        t2 = Template(id="t2", name="T2", description="T2", category=TemplateCategory.WEB_APP)
        t3 = Template(id="t3", name="T3", description="T3", category=TemplateCategory.REST_API)

        manager.register_template(t1)
        manager.register_template(t2)
        manager.register_template(t3)

        templates = manager.list_templates(category="rest_api")
        assert len(templates) == 2
        assert all(t.category == TemplateCategory.REST_API for t in templates)

    def test_list_templates_by_tags(self, manager):
        """Test listing templates by tags."""
        t1 = Template(id="t1", name="T1", description="T1",
                     category=TemplateCategory.CLI_TOOL, tags=["python", "cli"])
        t2 = Template(id="t2", name="T2", description="T2",
                     category=TemplateCategory.WEB_APP, tags=["javascript", "web"])
        t3 = Template(id="t3", name="T3", description="T3",
                     category=TemplateCategory.REST_API, tags=["python", "api"])

        manager.register_template(t1)
        manager.register_template(t2)
        manager.register_template(t3)

        templates = manager.list_templates(tags=["python"])
        assert len(templates) == 2

    def test_apply_template_simple(self, manager, sample_template, tmp_path):
        """Test applying template."""
        manager.register_template(sample_template)

        output_dir = tmp_path / "myproject"
        variables = {"project_name": "MyProject"}

        success = manager.apply_template("sample", output_dir, variables)

        assert success is True
        assert output_dir.exists()
        assert (output_dir / "src").exists()
        assert (output_dir / "tests").exists()
        assert (output_dir / "README.md").exists()
        assert (output_dir / "src" / "main.py").exists()

    def test_apply_template_variable_substitution(self, manager, sample_template, tmp_path):
        """Test variable substitution in templates."""
        manager.register_template(sample_template)

        output_dir = tmp_path / "test"
        variables = {"project_name": "TestProject"}

        manager.apply_template("sample", output_dir, variables)

        readme_content = (output_dir / "README.md").read_text()
        assert "# TestProject" in readme_content
        assert "Project: TESTPROJECT" in readme_content

        main_content = (output_dir / "src" / "main.py").read_text()
        assert 'print("TestProject")' in main_content

    def test_apply_template_not_found(self, manager, tmp_path):
        """Test applying non-existent template."""
        with pytest.raises(ValueError, match="Template not found"):
            manager.apply_template("nonexistent", tmp_path, {})

    def test_apply_template_validation_error(self, manager, sample_template, tmp_path):
        """Test template application with validation error."""
        manager.register_template(sample_template)

        with pytest.raises(ValueError, match="Variable validation failed"):
            manager.apply_template("sample", tmp_path, {})  # Missing required variable

    def test_apply_template_overwrite_false(self, manager, sample_template, tmp_path):
        """Test template application fails when directory exists."""
        manager.register_template(sample_template)

        output_dir = tmp_path / "existing"
        output_dir.mkdir()
        (output_dir / "file.txt").write_text("existing")

        with pytest.raises(FileExistsError, match="not empty"):
            manager.apply_template("sample", output_dir, {"project_name": "Test"},
                                 overwrite=False)

    def test_apply_template_overwrite_true(self, manager, sample_template, tmp_path):
        """Test template application overwrites when allowed."""
        manager.register_template(sample_template)

        output_dir = tmp_path / "existing"
        output_dir.mkdir()
        (output_dir / "file.txt").write_text("existing")

        success = manager.apply_template("sample", output_dir, {"project_name": "Test"},
                                        overwrite=True)

        assert success is True

    def test_get_template_preview(self, manager, sample_template):
        """Test getting template preview."""
        manager.register_template(sample_template)

        preview = manager.get_template_preview("sample")

        assert preview is not None
        assert preview["id"] == "sample"
        assert preview["name"] == "Sample Template"
        assert "files" in preview
        assert "directories" in preview
        assert len(preview["files"]) == 2
        assert len(preview["directories"]) == 2


class TestTemplateManagerFilters:
    """Test TemplateManager variable filters."""

    @pytest.fixture
    def manager(self):
        return TemplateManager()

    def test_substitute_variables_simple(self, manager):
        """Test simple variable substitution."""
        content = "Hello {{name}}"
        result = manager._substitute_variables(content, {"name": "World"})
        assert result == "Hello World"

    def test_substitute_variables_multiple(self, manager):
        """Test multiple variable substitution."""
        content = "{{greeting}} {{name}}!"
        result = manager._substitute_variables(content, {"greeting": "Hello", "name": "World"})
        assert result == "Hello World!"

    def test_filter_upper(self, manager):
        """Test upper filter."""
        content = "{{name|upper}}"
        result = manager._substitute_variables(content, {"name": "hello"})
        assert result == "HELLO"

    def test_filter_lower(self, manager):
        """Test lower filter."""
        content = "{{name|lower}}"
        result = manager._substitute_variables(content, {"name": "HELLO"})
        assert result == "hello"

    def test_filter_title(self, manager):
        """Test title filter."""
        content = "{{name|title}}"
        result = manager._substitute_variables(content, {"name": "hello world"})
        assert result == "Hello World"

    def test_filter_capitalize(self, manager):
        """Test capitalize filter."""
        content = "{{name|capitalize}}"
        result = manager._substitute_variables(content, {"name": "hello world"})
        assert result == "Hello world"

    def test_filter_snake_case(self, manager):
        """Test snake_case filter."""
        content = "{{name|snake_case}}"
        result = manager._substitute_variables(content, {"name": "MyProjectName"})
        assert result == "my_project_name"

    def test_filter_kebab_case(self, manager):
        """Test kebab-case filter."""
        content = "{{name|kebab-case}}"
        result = manager._substitute_variables(content, {"name": "MyProjectName"})
        assert result == "my-project-name"

    def test_filter_camel_case(self, manager):
        """Test camelCase filter."""
        content = "{{name|camelCase}}"
        result = manager._substitute_variables(content, {"name": "my_project_name"})
        assert result == "myProjectName"

    def test_filter_pascal_case(self, manager):
        """Test PascalCase filter."""
        content = "{{name|PascalCase}}"
        result = manager._substitute_variables(content, {"name": "my_project_name"})
        assert result == "MyProjectName"

    def test_filter_default(self, manager):
        """Test default filter."""
        content = "{{name|default:Anonymous}}"
        result = manager._substitute_variables(content, {"name": ""})
        assert result == "Anonymous"

        result2 = manager._substitute_variables(content, {"name": "John"})
        assert result2 == "John"


class TestBuiltinTemplates:
    """Test built-in templates."""

    def test_get_builtin_templates(self):
        """Test getting all built-in templates."""
        templates = get_builtin_templates()

        assert len(templates) >= 3
        assert all(isinstance(t, Template) for t in templates)

    def test_rest_api_template(self):
        """Test FastAPI REST API template."""
        template = create_rest_api_template()

        assert template.id == "fastapi-rest-api"
        assert template.category == TemplateCategory.REST_API
        assert len(template.variables) > 0
        assert len(template.files) > 0
        assert "python" in template.tags

        # Check variables
        assert template.get_variable("project_name") is not None
        assert template.get_variable("use_database") is not None
        assert template.get_variable("use_auth") is not None

    def test_web_app_template(self):
        """Test React + FastAPI web app template."""
        template = create_web_app_template()

        assert template.id == "react-fastapi-webapp"
        assert template.category == TemplateCategory.WEB_APP
        assert "react" in template.tags
        assert "fastapi" in template.tags

    def test_cli_tool_template(self):
        """Test Python CLI tool template."""
        template = create_cli_tool_template()

        assert template.id == "python-cli-tool"
        assert template.category == TemplateCategory.CLI_TOOL
        assert "cli" in template.tags
        assert template.get_variable("command_name") is not None


class TestTemplateIntegration:
    """Integration tests for template system."""

    def test_full_template_workflow(self, tmp_path):
        """Test complete template workflow."""
        # Create manager and register template
        manager = TemplateManager()
        template = create_rest_api_template()
        manager.register_template(template)

        # Apply template
        output_dir = tmp_path / "myapi"
        variables = {
            "project_name": "MyAPI",
            "description": "My REST API",
            "author": "Test Author",
            "python_version": "3.11",
            "use_database": "true",
            "use_auth": "true",
        }

        success = manager.apply_template(template.id, output_dir, variables)

        assert success is True

        # Verify structure
        assert (output_dir / "my_api").exists()
        assert (output_dir / "my_api" / "main.py").exists()
        assert (output_dir / "tests").exists()
        assert (output_dir / "README.md").exists()
        assert (output_dir / "requirements.txt").exists()
        assert (output_dir / "Dockerfile").exists()

        # Verify content substitution
        readme = (output_dir / "README.md").read_text()
        assert "MyAPI" in readme
        assert "My REST API" in readme

        main_py = (output_dir / "my_api" / "main.py").read_text()
        assert "my_api" in main_py

    def test_template_list_and_preview(self):
        """Test listing templates and getting previews."""
        manager = TemplateManager()

        # Register built-in templates
        for template in get_builtin_templates():
            manager.register_template(template)

        # List all templates
        all_templates = manager.list_templates()
        assert len(all_templates) >= 3

        # List by category
        rest_api_templates = manager.list_templates(category="rest_api")
        assert len(rest_api_templates) >= 1

        # Get preview
        preview = manager.get_template_preview("fastapi-rest-api")
        assert preview is not None
        assert "files" in preview
        assert "setup_commands" in preview
