"""Requirements specification document generator."""

from resoftai.generators.base import DocumentGenerator


class RequirementsDocGenerator(DocumentGenerator):
    """Generates comprehensive requirements specification document."""

    @property
    def document_name(self) -> str:
        return "Software Requirements Specification (SRS)"

    @property
    def document_filename(self) -> str:
        return "requirements-specification.md"

    async def generate_content(self) -> str:
        """Generate requirements specification content."""
        content = self._get_project_summary()

        # Add requirements sections
        if "srs_document" in self.project_state.requirements:
            content += self.project_state.requirements["srs_document"]
        elif "detailed_requirements" in self.project_state.requirements:
            content += self.project_state.requirements["detailed_requirements"]
        elif "organized_requirements" in self.project_state.requirements:
            content += "## Requirements\n\n"
            content += self.project_state.requirements["organized_requirements"]
        else:
            content += "## Requirements\n\n"
            content += self.project_state.requirements.get("initial_input", "No requirements available")

        # Add decisions
        if self.project_state.decisions:
            content += "\n\n## Key Decisions\n\n"
            for decision in self.project_state.decisions:
                content += f"### {decision['decision']}\n\n"
                content += f"- **Made by:** {decision['made_by']}\n"
                content += f"- **Rationale:** {decision.get('rationale', 'N/A')}\n"
                content += f"- **Date:** {decision['timestamp']}\n\n"

        return content
