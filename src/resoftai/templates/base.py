"""
Base classes for project templates.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Any, Optional
from pathlib import Path


class TemplateCategory(str, Enum):
    """Template categories."""

    WEB_APP = "web_app"
    REST_API = "rest_api"
    CLI_TOOL = "cli_tool"
    MICROSERVICE = "microservice"
    DATA_PIPELINE = "data_pipeline"
    ML_PROJECT = "ml_project"
    MOBILE_APP = "mobile_app"
    DESKTOP_APP = "desktop_app"


@dataclass
class TemplateVariable:
    """
    Variable that can be customized when applying template.
    """

    name: str
    description: str
    default: Any = ""
    required: bool = True
    type: str = "string"  # string, integer, boolean, choice
    choices: Optional[List[str]] = None

    def validate(self, value: Any) -> bool:
        """Validate variable value."""
        # Check if required value is missing (None or empty string, but not False)
        if self.required and value is None:
            return False
        if self.required and value == "" and not isinstance(value, bool):
            return False

        if self.type == "integer":
            return isinstance(value, int) or (isinstance(value, str) and value.isdigit())
        elif self.type == "boolean":
            return isinstance(value, bool) or value in ["true", "false", "True", "False"]
        elif self.type == "choice":
            return self.choices and value in self.choices

        return True


@dataclass
class TemplateFile:
    """
    File in a template with optional content transformation.
    """

    path: str  # Relative path in template
    content: str = ""
    is_template: bool = True  # If True, apply variable substitution
    is_binary: bool = False
    executable: bool = False


@dataclass
class Template:
    """
    Project template definition.
    """

    id: str
    name: str
    description: str
    category: TemplateCategory
    author: str = "ResoftAI"
    version: str = "1.0.0"

    # Template content
    variables: List[TemplateVariable] = field(default_factory=list)
    files: List[TemplateFile] = field(default_factory=list)
    directories: List[str] = field(default_factory=list)

    # Requirements
    requirements: Dict[str, Any] = field(default_factory=dict)  # e.g., {"python": ">=3.8"}
    dependencies: List[str] = field(default_factory=list)  # Package dependencies

    # Post-creation instructions
    setup_commands: List[str] = field(default_factory=list)
    readme_content: str = ""

    # Metadata
    tags: List[str] = field(default_factory=list)
    icon: Optional[str] = None
    screenshot: Optional[str] = None

    def get_variable(self, name: str) -> Optional[TemplateVariable]:
        """Get variable by name."""
        for var in self.variables:
            if var.name == name:
                return var
        return None

    def validate_variables(self, values: Dict[str, Any]) -> tuple[bool, List[str]]:
        """
        Validate provided variable values.

        Returns:
            (is_valid, error_messages)
        """
        errors = []

        for var in self.variables:
            if var.required and var.name not in values:
                errors.append(f"Required variable '{var.name}' is missing")
                continue

            if var.name in values:
                if not var.validate(values[var.name]):
                    errors.append(
                        f"Invalid value for variable '{var.name}': "
                        f"expected {var.type}, got {type(values[var.name]).__name__}"
                    )

        return len(errors) == 0, errors

    def to_dict(self) -> Dict[str, Any]:
        """Convert template to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "category": self.category.value,
            "author": self.author,
            "version": self.version,
            "variables": [
                {
                    "name": var.name,
                    "description": var.description,
                    "default": var.default,
                    "required": var.required,
                    "type": var.type,
                    "choices": var.choices,
                }
                for var in self.variables
            ],
            "requirements": self.requirements,
            "dependencies": self.dependencies,
            "tags": self.tags,
            "file_count": len(self.files),
            "directory_count": len(self.directories),
        }
