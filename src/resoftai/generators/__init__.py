"""Document generators for creating comprehensive project documentation."""

from resoftai.generators.base import DocumentGenerator
from resoftai.generators.requirements_doc import RequirementsDocGenerator
from resoftai.generators.design_doc import DesignDocGenerator
from resoftai.generators.database_doc import DatabaseDocGenerator
from resoftai.generators.deployment_doc import DeploymentDocGenerator
from resoftai.generators.user_manual import UserManualGenerator
from resoftai.generators.training_manual import TrainingManualGenerator

__all__ = [
    "DocumentGenerator",
    "RequirementsDocGenerator",
    "DesignDocGenerator",
    "DatabaseDocGenerator",
    "DeploymentDocGenerator",
    "UserManualGenerator",
    "TrainingManualGenerator",
]
