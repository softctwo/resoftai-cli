"""
Plugin Base Classes and Interfaces

Defines the core interfaces and base classes that all plugins must implement.
Provides a contract for plugin developers to extend ResoftAI functionality.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List, Type
from dataclasses import dataclass, field
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


@dataclass
class PluginMetadata:
    """
    Plugin metadata describing the plugin's capabilities and requirements
    """
    # Basic info
    name: str
    slug: str  # Unique identifier
    version: str
    description: str
    author: str

    # Requirements
    min_platform_version: Optional[str] = None
    max_platform_version: Optional[str] = None
    dependencies: List[str] = field(default_factory=list)  # Other plugin slugs

    # Categorization
    category: str = "utility"
    tags: List[str] = field(default_factory=list)

    # URLs
    homepage: Optional[str] = None
    documentation: Optional[str] = None
    repository: Optional[str] = None

    # License
    license: str = "MIT"

    # Internal
    entry_point: Optional[str] = None  # Class path to plugin class

    def to_dict(self) -> Dict[str, Any]:
        """Convert metadata to dictionary"""
        return {
            "name": self.name,
            "slug": self.slug,
            "version": self.version,
            "description": self.description,
            "author": self.author,
            "min_platform_version": self.min_platform_version,
            "max_platform_version": self.max_platform_version,
            "dependencies": self.dependencies,
            "category": self.category,
            "tags": self.tags,
            "homepage": self.homepage,
            "documentation": self.documentation,
            "repository": self.repository,
            "license": self.license,
        }


@dataclass
class PluginConfig:
    """
    Plugin configuration provided by the user
    """
    enabled: bool = True
    config: Dict[str, Any] = field(default_factory=dict)
    auto_update: bool = False

    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value"""
        return self.config.get(key, default)

    def set(self, key: str, value: Any):
        """Set configuration value"""
        self.config[key] = value


class PluginContext:
    """
    Context object passed to plugins providing access to platform APIs

    This is the main interface through which plugins interact with ResoftAI.
    """

    def __init__(self, db_session=None, settings=None, logger=None):
        self.db_session = db_session
        self.settings = settings
        self.logger = logger or logging.getLogger("resoftai.plugins")
        self._data = {}  # Plugin-specific data storage

    def get_data(self, key: str, default: Any = None) -> Any:
        """Get plugin-specific data"""
        return self._data.get(key, default)

    def set_data(self, key: str, value: Any):
        """Set plugin-specific data"""
        self._data[key] = value

    def log_info(self, message: str):
        """Log info message"""
        self.logger.info(message)

    def log_error(self, message: str):
        """Log error message"""
        self.logger.error(message)

    def log_warning(self, message: str):
        """Log warning message"""
        self.logger.warning(message)


class Plugin(ABC):
    """
    Abstract base class for all plugins

    All plugins must inherit from this class and implement the required methods.

    Lifecycle:
    1. __init__() - Plugin instantiation
    2. load() - Plugin initialization
    3. activate() - Plugin activation
    4. (Plugin is now active and receiving hooks)
    5. deactivate() - Plugin deactivation
    6. unload() - Plugin cleanup
    """

    def __init__(self, metadata: PluginMetadata, config: PluginConfig):
        self.metadata = metadata
        self.config = config
        self.context: Optional[PluginContext] = None
        self._loaded = False
        self._active = False
        self._load_time: Optional[datetime] = None
        self.logger = logging.getLogger(f"resoftai.plugins.{metadata.slug}")

    @abstractmethod
    def load(self, context: PluginContext) -> bool:
        """
        Initialize the plugin

        Called when the plugin is first loaded. Use this to set up any
        resources, validate configuration, etc.

        Args:
            context: Plugin context with platform APIs

        Returns:
            True if load successful, False otherwise
        """
        pass

    @abstractmethod
    def activate(self) -> bool:
        """
        Activate the plugin

        Called after load() to activate the plugin. The plugin should
        start listening to hooks and providing its functionality.

        Returns:
            True if activation successful, False otherwise
        """
        pass

    @abstractmethod
    def deactivate(self) -> bool:
        """
        Deactivate the plugin

        Called to temporarily deactivate the plugin. The plugin should
        stop processing hooks but keep its resources.

        Returns:
            True if deactivation successful, False otherwise
        """
        pass

    @abstractmethod
    def unload(self) -> bool:
        """
        Unload and cleanup the plugin

        Called when the plugin is being unloaded. Clean up all resources,
        close connections, etc.

        Returns:
            True if unload successful, False otherwise
        """
        pass

    def get_config_schema(self) -> Optional[Dict[str, Any]]:
        """
        Return JSON Schema for plugin configuration

        Override this method to provide a configuration schema that
        will be used for validation and UI generation.

        Returns:
            JSON Schema dict or None
        """
        return None

    def validate_config(self, config: Dict[str, Any]) -> bool:
        """
        Validate plugin configuration

        Override this method to provide custom configuration validation.

        Args:
            config: Configuration to validate

        Returns:
            True if valid, False otherwise
        """
        return True

    @property
    def is_loaded(self) -> bool:
        """Check if plugin is loaded"""
        return self._loaded

    @property
    def is_active(self) -> bool:
        """Check if plugin is active"""
        return self._active

    @property
    def load_time(self) -> Optional[datetime]:
        """Get plugin load time"""
        return self._load_time

    def __repr__(self):
        return f"<{self.__class__.__name__}(slug='{self.metadata.slug}', version='{self.metadata.version}')>"


# =============================================================================
# Specialized Plugin Types
# =============================================================================

class AgentPlugin(Plugin):
    """
    Base class for custom agent plugins

    Agent plugins can add new agent types to the platform.
    """

    @abstractmethod
    def get_agent_class(self) -> Type:
        """
        Return the agent class

        Returns:
            Agent class that inherits from resoftai.core.agent.Agent
        """
        pass

    @abstractmethod
    def get_agent_role(self) -> str:
        """
        Return the agent role identifier

        Returns:
            Role string (e.g., "security_analyst", "api_designer")
        """
        pass


class LLMProviderPlugin(Plugin):
    """
    Base class for LLM provider plugins

    Allows adding support for additional LLM providers.
    """

    @abstractmethod
    def get_provider_class(self) -> Type:
        """
        Return the LLM provider class

        Returns:
            Provider class that inherits from resoftai.llm.base.LLMProvider
        """
        pass

    @abstractmethod
    def get_provider_name(self) -> str:
        """
        Return the provider name

        Returns:
            Provider identifier (e.g., "openai", "cohere")
        """
        pass


class IntegrationPlugin(Plugin):
    """
    Base class for integration plugins

    Integration plugins connect ResoftAI with external services.
    """

    @abstractmethod
    def get_integration_name(self) -> str:
        """
        Return the integration name

        Returns:
            Integration identifier (e.g., "jira", "slack")
        """
        pass

    @abstractmethod
    async def send_notification(self, event: str, data: Dict[str, Any]) -> bool:
        """
        Send notification to external service

        Args:
            event: Event type
            data: Event data

        Returns:
            True if sent successfully
        """
        pass


class WorkflowPlugin(Plugin):
    """
    Base class for workflow plugins

    Workflow plugins can add custom project workflows.
    """

    @abstractmethod
    def get_workflow_name(self) -> str:
        """
        Return the workflow name

        Returns:
            Workflow identifier
        """
        pass

    @abstractmethod
    def get_workflow_stages(self) -> List[str]:
        """
        Return the workflow stages

        Returns:
            List of stage names in order
        """
        pass


class CodeQualityPlugin(Plugin):
    """
    Base class for code quality plugins

    Adds custom linters, formatters, or code analysis tools.
    """

    @abstractmethod
    def get_tool_name(self) -> str:
        """
        Return the tool name

        Returns:
            Tool identifier
        """
        pass

    @abstractmethod
    async def analyze_code(self, code: str, language: str) -> Dict[str, Any]:
        """
        Analyze code and return issues

        Args:
            code: Source code to analyze
            language: Programming language

        Returns:
            Analysis results with issues
        """
        pass


class TemplatePlugin(Plugin):
    """
    Base class for project template plugins

    Adds custom project templates.
    """

    @abstractmethod
    def get_template_name(self) -> str:
        """
        Return the template name

        Returns:
            Template identifier
        """
        pass

    @abstractmethod
    def get_template_files(self) -> Dict[str, str]:
        """
        Return template files

        Returns:
            Dict mapping file paths to content
        """
        pass


# =============================================================================
# Plugin Exceptions
# =============================================================================

class PluginError(Exception):
    """Base exception for plugin errors"""
    pass


class PluginLoadError(PluginError):
    """Error loading a plugin"""
    pass


class PluginValidationError(PluginError):
    """Plugin validation failed"""
    pass


class PluginDependencyError(PluginError):
    """Plugin dependency not satisfied"""
    pass


class PluginVersionError(PluginError):
    """Plugin version incompatible"""
    pass
