"""Database design document generator."""

from resoftai.generators.base import DocumentGenerator


class DatabaseDocGenerator(DocumentGenerator):
    """Generates comprehensive database design document."""

    @property
    def document_name(self) -> str:
        return "Database Design Document"

    @property
    def document_filename(self) -> str:
        return "database-design.md"

    async def generate_content(self) -> str:
        """Generate database design content."""
        content = self._get_project_summary()

        if "database_design" in self.project_state.architecture:
            content += "## Database Design\n\n"
            content += self.project_state.architecture["database_design"]
        else:
            content += "## Database Design\n\n"
            content += "Database design not yet available.\n"

        return content
