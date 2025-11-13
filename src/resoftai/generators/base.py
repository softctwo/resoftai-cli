"""
Base document generator class.
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, Any
import logging
from datetime import datetime

from resoftai.core.state import ProjectState
from resoftai.config.settings import get_settings

logger = logging.getLogger(__name__)


class DocumentGenerator(ABC):
    """
    Base class for all document generators.
    """

    def __init__(self, project_state: ProjectState):
        """
        Initialize the document generator.

        Args:
            project_state: Project state containing all project information
        """
        self.project_state = project_state
        self.settings = get_settings()

    @property
    @abstractmethod
    def document_name(self) -> str:
        """Name of the document."""
        pass

    @property
    @abstractmethod
    def document_filename(self) -> str:
        """Filename for the document."""
        pass

    @abstractmethod
    async def generate_content(self) -> str:
        """
        Generate the document content.

        Returns:
            The generated document content
        """
        pass

    async def generate(self, output_dir: Path) -> Path:
        """
        Generate the document and save to file.

        Args:
            output_dir: Directory to save the document

        Returns:
            Path to the generated document
        """
        logger.info(f"Generating {self.document_name}...")

        # Ensure output directory exists
        output_dir.mkdir(parents=True, exist_ok=True)

        # Generate content
        content = await self.generate_content()

        # Add header
        full_content = self._add_header(content)

        # Save to file
        file_path = output_dir / self.document_filename
        file_path.write_text(full_content, encoding='utf-8')

        logger.info(f"Generated {self.document_name} at {file_path}")

        return file_path

    def _add_header(self, content: str) -> str:
        """Add a standard header to the document."""
        header = f"""# {self.document_name}

**Project:** {self.project_state.name}
**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Version:** 1.0

---

"""
        return header + content

    def _get_project_summary(self) -> str:
        """Get a summary of the project."""
        return f"""## Project Overview

**Project Name:** {self.project_state.name}

**Description:** {self.project_state.description}

**Current Stage:** {self.project_state.current_stage.value}

**Created:** {self.project_state.created_at.strftime('%Y-%m-%d')}

"""
