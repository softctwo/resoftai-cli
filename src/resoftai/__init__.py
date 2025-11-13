"""
ResoftAI - Multi-Agent Software Development Platform

An AI-powered platform for custom software development using collaborative AI agents.
"""

__version__ = "0.1.0"
__author__ = "softctwo"
__email__ = "softctwo@aliyun.com"

from resoftai.core.agent import Agent, AgentRole
from resoftai.core.workflow import ProjectWorkflow, WorkflowStage
from resoftai.core.state import ProjectState

__all__ = [
    "Agent",
    "AgentRole",
    "ProjectWorkflow",
    "WorkflowStage",
    "ProjectState",
]
