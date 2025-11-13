"""
Template manager for loading and applying templates.
"""

import re
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Any
import logging

from resoftai.templates.base import Template, TemplateFile, TemplateVariable

logger = logging.getLogger(__name__)


class TemplateManager:
    """
    Manages project templates: loading, listing, and applying.
    """

    def __init__(self, template_dir: Optional[Path] = None):
        """
        Initialize template manager.

        Args:
            template_dir: Directory containing template files
        """
        self.template_dir = template_dir or Path(__file__).parent / "builtin"
        self._templates: Dict[str, Template] = {}

    def register_template(self, template: Template) -> None:
        """
        Register a template.

        Args:
            template: Template to register
        """
        self._templates[template.id] = template
        logger.info(f"Registered template: {template.id}")

    def get_template(self, template_id: str) -> Optional[Template]:
        """
        Get template by ID.

        Args:
            template_id: Template identifier

        Returns:
            Template or None if not found
        """
        return self._templates.get(template_id)

    def list_templates(
        self,
        category: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> List[Template]:
        """
        List available templates with optional filtering.

        Args:
            category: Filter by category
            tags: Filter by tags (any match)

        Returns:
            List of matching templates
        """
        templates = list(self._templates.values())

        if category:
            templates = [t for t in templates if t.category.value == category]

        if tags:
            templates = [
                t for t in templates
                if any(tag in t.tags for tag in tags)
            ]

        return templates

    def apply_template(
        self,
        template_id: str,
        output_dir: Path,
        variables: Dict[str, Any],
        overwrite: bool = False
    ) -> bool:
        """
        Apply template to create project structure.

        Args:
            template_id: Template to apply
            output_dir: Output directory
            variables: Variable values
            overwrite: Whether to overwrite existing files

        Returns:
            True if successful

        Raises:
            ValueError: If template not found or validation fails
            FileExistsError: If output directory exists and overwrite is False
        """
        template = self.get_template(template_id)
        if not template:
            raise ValueError(f"Template not found: {template_id}")

        # Validate variables
        is_valid, errors = template.validate_variables(variables)
        if not is_valid:
            raise ValueError(f"Variable validation failed: {', '.join(errors)}")

        # Check output directory
        if output_dir.exists() and not overwrite:
            if any(output_dir.iterdir()):
                raise FileExistsError(
                    f"Output directory is not empty: {output_dir}. "
                    "Use overwrite=True to force."
                )

        # Create output directory
        output_dir.mkdir(parents=True, exist_ok=True)

        # Create directories
        for dir_path in template.directories:
            # Substitute variables in directory path
            resolved_path = self._substitute_variables(dir_path, variables)
            (output_dir / resolved_path).mkdir(parents=True, exist_ok=True)

        # Create files
        for file in template.files:
            # Substitute variables in file path
            resolved_file_path = self._substitute_variables(file.path, variables)
            file_path = output_dir / resolved_file_path
            file_path.parent.mkdir(parents=True, exist_ok=True)

            if file.is_template:
                # Apply variable substitution to content
                content = self._substitute_variables(file.content, variables)
                file_path.write_text(content, encoding='utf-8')
            elif file.is_binary:
                # Copy binary file as-is (if exists in template dir)
                source = self.template_dir / template.id / file.path
                if source.exists():
                    shutil.copy2(source, file_path)
            else:
                # Write content as-is
                file_path.write_text(file.content, encoding='utf-8')

            if file.executable:
                file_path.chmod(0o755)

        logger.info(f"Applied template '{template_id}' to {output_dir}")
        return True

    def _substitute_variables(self, content: str, variables: Dict[str, Any]) -> str:
        """
        Substitute template variables in content.

        Supports:
        - {{variable_name}} - simple substitution
        - {{variable_name|upper}} - with filter
        - {{variable_name|default:value}} - with default

        Args:
            content: Template content
            variables: Variable values

        Returns:
            Content with substituted variables
        """
        def replace_var(match):
            var_expr = match.group(1).strip()

            # Parse variable name and filters
            if '|' in var_expr:
                var_name, filters = var_expr.split('|', 1)
                var_name = var_name.strip()
                filters = filters.strip()
            else:
                var_name = var_expr
                filters = None

            # Get variable value
            value = variables.get(var_name, "")

            # Apply filters
            if filters:
                value = self._apply_filter(str(value), filters)

            return str(value)

        # Replace {{variable}} patterns
        pattern = r'\{\{([^}]+)\}\}'
        return re.sub(pattern, replace_var, content)

    def _apply_filter(self, value: str, filter_expr: str) -> str:
        """
        Apply filter to value.

        Supported filters:
        - upper: Convert to uppercase
        - lower: Convert to lowercase
        - title: Convert to title case
        - capitalize: Capitalize first letter
        - snake_case: Convert to snake_case
        - kebab-case: Convert to kebab-case
        - camelCase: Convert to camelCase
        - PascalCase: Convert to PascalCase
        - default:value: Use default if empty

        Args:
            value: Input value
            filter_expr: Filter expression

        Returns:
            Filtered value
        """
        if filter_expr == "upper":
            return value.upper()
        elif filter_expr == "lower":
            return value.lower()
        elif filter_expr == "title":
            return value.title()
        elif filter_expr == "capitalize":
            return value.capitalize()
        elif filter_expr == "snake_case":
            # Convert to snake_case
            s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', value)
            return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()
        elif filter_expr == "kebab-case":
            # Convert to kebab-case
            s1 = re.sub('(.)([A-Z][a-z]+)', r'\1-\2', value)
            return re.sub('([a-z0-9])([A-Z])', r'\1-\2', s1).lower()
        elif filter_expr == "camelCase":
            # Convert to camelCase
            words = re.split(r'[\s_-]+', value)
            if not words:
                return value
            return words[0].lower() + ''.join(w.capitalize() for w in words[1:])
        elif filter_expr == "PascalCase":
            # Convert to PascalCase
            words = re.split(r'[\s_-]+', value)
            return ''.join(w.capitalize() for w in words)
        elif filter_expr.startswith("default:"):
            # Use default if value is empty
            default = filter_expr.split(":", 1)[1]
            return value if value else default
        else:
            return value

    def get_template_preview(self, template_id: str) -> Optional[Dict[str, Any]]:
        """
        Get template preview information.

        Args:
            template_id: Template identifier

        Returns:
            Template preview data or None
        """
        template = self.get_template(template_id)
        if not template:
            return None

        return {
            **template.to_dict(),
            "files": [
                {"path": f.path, "is_template": f.is_template}
                for f in template.files
            ],
            "directories": template.directories,
            "setup_commands": template.setup_commands,
        }
