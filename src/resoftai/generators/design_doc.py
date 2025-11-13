"""Design specification document generator."""

from resoftai.generators.base import DocumentGenerator


class DesignDocGenerator(DocumentGenerator):
    """Generates comprehensive design specification document."""

    @property
    def document_name(self) -> str:
        return "System Design Specification"

    @property
    def document_filename(self) -> str:
        return "design-specification.md"

    async def generate_content(self) -> str:
        """Generate design specification content."""
        content = self._get_project_summary()

        # Architecture Design
        if self.project_state.architecture:
            content += "## Architecture Design\n\n"
            if "system_architecture" in self.project_state.architecture:
                content += self.project_state.architecture["system_architecture"]
                content += "\n\n"

        # UI/UX Design
        if self.project_state.design:
            if "ux_design" in self.project_state.design:
                content += "## User Experience Design\n\n"
                content += self.project_state.design["ux_design"]
                content += "\n\n"

            if "ui_design" in self.project_state.design:
                content += "## User Interface Design\n\n"
                content += self.project_state.design["ui_design"]
                content += "\n\n"

        return content
