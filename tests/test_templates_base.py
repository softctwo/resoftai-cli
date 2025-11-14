"""Tests for template base classes."""
import pytest
from resoftai.templates.base import (
    TemplateCategory,
    TemplateVariable,
    TemplateFile,
    Template
)


class TestTemplateCategory:
    """Test TemplateCategory enum."""

    def test_category_values(self):
        """Test that all category values are available."""
        assert TemplateCategory.WEB_APP == "web_app"
        assert TemplateCategory.REST_API == "rest_api"
        assert TemplateCategory.CLI_TOOL == "cli_tool"
        assert TemplateCategory.MICROSERVICE == "microservice"
        assert TemplateCategory.DATA_PIPELINE == "data_pipeline"
        assert TemplateCategory.ML_PROJECT == "ml_project"
        assert TemplateCategory.MOBILE_APP == "mobile_app"
        assert TemplateCategory.DESKTOP_APP == "desktop_app"

    def test_category_is_string_enum(self):
        """Test that category inherits from str."""
        assert isinstance(TemplateCategory.WEB_APP, str)
        assert isinstance(TemplateCategory.REST_API.value, str)


class TestTemplateVariable:
    """Test TemplateVariable class."""

    def test_create_required_variable(self):
        """Test creating a required variable."""
        var = TemplateVariable(
            name="project_name",
            description="Name of the project",
            required=True
        )
        assert var.name == "project_name"
        assert var.description == "Name of the project"
        assert var.required is True
        assert var.type == "string"
        assert var.default == ""

    def test_create_optional_variable(self):
        """Test creating an optional variable with default."""
        var = TemplateVariable(
            name="port",
            description="Server port",
            default=8000,
            required=False,
            type="integer"
        )
        assert var.name == "port"
        assert var.default == 8000
        assert var.required is False
        assert var.type == "integer"

    def test_validate_required_string_valid(self):
        """Test validating required string with value."""
        var = TemplateVariable(
            name="name",
            description="Name",
            required=True,
            type="string"
        )
        assert var.validate("my-project") is True
        assert var.validate("test") is True

    def test_validate_required_string_invalid(self):
        """Test validating required string without value."""
        var = TemplateVariable(
            name="name",
            description="Name",
            required=True,
            type="string"
        )
        assert var.validate(None) is False
        assert var.validate("") is False

    def test_validate_optional_string(self):
        """Test validating optional string."""
        var = TemplateVariable(
            name="description",
            description="Description",
            required=False,
            type="string"
        )
        assert var.validate("some text") is True
        assert var.validate("") is True
        assert var.validate(None) is True

    def test_validate_integer_type(self):
        """Test validating integer type."""
        var = TemplateVariable(
            name="port",
            description="Port number",
            type="integer"
        )
        assert var.validate(8000) is True
        assert var.validate(80) is True
        assert var.validate("8000") is True
        assert var.validate("not a number") is False

    def test_validate_boolean_type(self):
        """Test validating boolean type."""
        var = TemplateVariable(
            name="enabled",
            description="Enable feature",
            type="boolean"
        )
        assert var.validate(True) is True
        assert var.validate(False) is True
        assert var.validate("true") is True
        assert var.validate("false") is True
        assert var.validate("True") is True
        assert var.validate("False") is True
        assert var.validate("yes") is False
        assert var.validate(1) is False

    def test_validate_choice_type(self):
        """Test validating choice type."""
        var = TemplateVariable(
            name="database",
            description="Database type",
            type="choice",
            choices=["postgresql", "mysql", "sqlite"]
        )
        assert var.validate("postgresql") is True
        assert var.validate("mysql") is True
        assert var.validate("sqlite") is True
        assert var.validate("mongodb") is False
        assert var.validate("") is False

    def test_validate_required_false_value(self):
        """Test that False as a boolean value is valid for required field."""
        var = TemplateVariable(
            name="feature",
            description="Feature flag",
            required=True,
            type="boolean"
        )
        # False should be valid for boolean even if required
        assert var.validate(False) is True


class TestTemplateFile:
    """Test TemplateFile class."""

    def test_create_template_file(self):
        """Test creating a template file."""
        file = TemplateFile(
            path="src/main.py",
            content="print('Hello World')",
            is_template=True
        )
        assert file.path == "src/main.py"
        assert file.content == "print('Hello World')"
        assert file.is_template is True
        assert file.is_binary is False
        assert file.executable is False

    def test_create_binary_file(self):
        """Test creating a binary file."""
        file = TemplateFile(
            path="assets/logo.png",
            content="",
            is_template=False,
            is_binary=True
        )
        assert file.path == "assets/logo.png"
        assert file.is_binary is True
        assert file.is_template is False

    def test_create_executable_file(self):
        """Test creating an executable file."""
        file = TemplateFile(
            path="scripts/run.sh",
            content="#!/bin/bash\necho 'Running...'",
            is_template=True,
            executable=True
        )
        assert file.path == "scripts/run.sh"
        assert file.executable is True

    def test_default_values(self):
        """Test default values for TemplateFile."""
        file = TemplateFile(path="test.txt")
        assert file.content == ""
        assert file.is_template is True
        assert file.is_binary is False
        assert file.executable is False


class TestTemplate:
    """Test Template class."""

    def test_create_template(self):
        """Test creating a template."""
        template = Template(
            id="web-app-python",
            name="Python Web Application",
            description="Full-stack Python web app with FastAPI",
            category=TemplateCategory.WEB_APP
        )
        assert template.id == "web-app-python"
        assert template.name == "Python Web Application"
        assert template.description == "Full-stack Python web app with FastAPI"
        assert template.category == TemplateCategory.WEB_APP
        assert template.author == "ResoftAI"
        assert template.version == "1.0.0"

    def test_template_with_custom_author(self):
        """Test template with custom author and version."""
        template = Template(
            id="custom-template",
            name="Custom Template",
            description="A custom template",
            category=TemplateCategory.CLI_TOOL,
            author="Custom Author",
            version="2.0.0"
        )
        assert template.author == "Custom Author"
        assert template.version == "2.0.0"

    def test_template_categories(self):
        """Test templates with different categories."""
        categories = [
            TemplateCategory.WEB_APP,
            TemplateCategory.REST_API,
            TemplateCategory.MICROSERVICE,
            TemplateCategory.ML_PROJECT
        ]

        for category in categories:
            template = Template(
                id=f"test-{category.value}",
                name=f"Test {category.value}",
                description="Test template",
                category=category
            )
            assert template.category == category


class TestTemplateIntegration:
    """Integration tests for template components."""

    def test_template_with_variables_and_files(self):
        """Test creating a complete template with variables and files."""
        variables = [
            TemplateVariable(
                name="project_name",
                description="Project name",
                required=True
            ),
            TemplateVariable(
                name="author",
                description="Project author",
                default="Anonymous",
                required=False
            ),
            TemplateVariable(
                name="port",
                description="Server port",
                default=8000,
                type="integer",
                required=False
            )
        ]

        files = [
            TemplateFile(
                path="README.md",
                content="# {{project_name}}\nBy {{author}}",
                is_template=True
            ),
            TemplateFile(
                path="src/main.py",
                content="PORT = {{port}}\nprint('Starting on port', PORT)",
                is_template=True
            ),
            TemplateFile(
                path=".gitignore",
                content="__pycache__/\n*.pyc",
                is_template=False
            )
        ]

        template = Template(
            id="test-template",
            name="Test Template",
            description="A test template",
            category=TemplateCategory.WEB_APP
        )

        # Verify all components are created correctly
        assert len(variables) == 3
        assert len(files) == 3
        assert template.category == TemplateCategory.WEB_APP

        # Test variable validation
        assert variables[0].validate("my-project") is True
        assert variables[1].validate("John Doe") is True
        assert variables[2].validate(3000) is True

    def test_validate_all_variables(self):
        """Test validating multiple variables."""
        variables = [
            TemplateVariable(name="name", description="Name", required=True),
            TemplateVariable(name="port", description="Port", type="integer", default=8000),
            TemplateVariable(name="debug", description="Debug mode", type="boolean", default=False),
        ]

        # Valid values
        values = {
            "name": "my-app",
            "port": 3000,
            "debug": True
        }

        for var in variables:
            value = values.get(var.name, var.default)
            assert var.validate(value) is True

        # Invalid values
        invalid_values = {
            "name": "",  # Required but empty
            "port": "not-a-number",  # Should be integer
            "debug": "maybe"  # Should be boolean
        }

        validation_results = []
        for var in variables:
            value = invalid_values.get(var.name)
            if value is not None:
                validation_results.append(var.validate(value))

        # At least some validations should fail
        assert False in validation_results
