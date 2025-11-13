"""
Project template system for quick project scaffolding.
"""

from resoftai.templates.base import Template, TemplateVariable, TemplateCategory
from resoftai.templates.manager import TemplateManager
from resoftai.templates.registry import get_builtin_templates

__all__ = [
    "Template",
    "TemplateVariable",
    "TemplateCategory",
    "TemplateManager",
    "get_builtin_templates",
]
