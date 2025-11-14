"""
Plugin Hook System - Event-based Extension Points

Provides an event-driven hook system that allows plugins to extend
platform functionality at specific extension points.

Hook Types:
- Action hooks: Execute code at specific points (no return value expected)
- Filter hooks: Transform data (return modified value)
"""
from typing import Callable, Dict, List, Any, Optional
from collections import defaultdict
import logging
import asyncio
from functools import wraps

logger = logging.getLogger(__name__)


class HookManager:
    """
    Manages hooks and their execution

    Hooks are extension points where plugins can inject custom behavior.
    """

    def __init__(self):
        # Action hooks: hook_name -> List[callback]
        self._action_hooks: Dict[str, List[Callable]] = defaultdict(list)

        # Filter hooks: hook_name -> List[callback]
        self._filter_hooks: Dict[str, List[Callable]] = defaultdict(list)

        # Hook priorities: (hook_name, callback) -> priority
        self._priorities: Dict[tuple, int] = {}

    def register_action(self, hook_name: str, callback: Callable, priority: int = 10):
        """
        Register an action hook

        Action hooks execute callbacks without expecting a return value.
        Used for triggering side effects at specific points.

        Args:
            hook_name: Name of the hook
            callback: Function to call
            priority: Priority (lower runs first)
        """
        self._action_hooks[hook_name].append(callback)
        self._priorities[(hook_name, callback)] = priority

        # Sort by priority
        self._action_hooks[hook_name].sort(
            key=lambda cb: self._priorities.get((hook_name, cb), 10)
        )

        logger.debug(f"Registered action hook: {hook_name} -> {callback.__name__}")

    def register_filter(self, hook_name: str, callback: Callable, priority: int = 10):
        """
        Register a filter hook

        Filter hooks transform data by passing it through callbacks.
        Each callback receives the current value and returns a modified value.

        Args:
            hook_name: Name of the hook
            callback: Function to call (must return modified value)
            priority: Priority (lower runs first)
        """
        self._filter_hooks[hook_name].append(callback)
        self._priorities[(hook_name, callback)] = priority

        # Sort by priority
        self._filter_hooks[hook_name].sort(
            key=lambda cb: self._priorities.get((hook_name, cb), 10)
        )

        logger.debug(f"Registered filter hook: {hook_name} -> {callback.__name__}")

    def unregister_action(self, hook_name: str, callback: Callable):
        """
        Unregister an action hook

        Args:
            hook_name: Name of the hook
            callback: Callback to remove
        """
        if hook_name in self._action_hooks and callback in self._action_hooks[hook_name]:
            self._action_hooks[hook_name].remove(callback)
            del self._priorities[(hook_name, callback)]
            logger.debug(f"Unregistered action hook: {hook_name} -> {callback.__name__}")

    def unregister_filter(self, hook_name: str, callback: Callable):
        """
        Unregister a filter hook

        Args:
            hook_name: Name of the hook
            callback: Callback to remove
        """
        if hook_name in self._filter_hooks and callback in self._filter_hooks[hook_name]:
            self._filter_hooks[hook_name].remove(callback)
            del self._priorities[(hook_name, callback)]
            logger.debug(f"Unregistered filter hook: {hook_name} -> {callback.__name__}")

    def do_action(self, hook_name: str, *args, **kwargs):
        """
        Execute action hooks

        Calls all registered callbacks for the action hook.

        Args:
            hook_name: Name of the hook
            *args: Positional arguments to pass to callbacks
            **kwargs: Keyword arguments to pass to callbacks
        """
        if hook_name not in self._action_hooks:
            return

        logger.debug(f"Executing action hook: {hook_name}")

        for callback in self._action_hooks[hook_name]:
            try:
                callback(*args, **kwargs)
            except Exception as e:
                logger.error(f"Error in action hook {hook_name} -> {callback.__name__}: {e}")

    async def do_action_async(self, hook_name: str, *args, **kwargs):
        """
        Execute async action hooks

        Calls all registered async callbacks for the action hook.

        Args:
            hook_name: Name of the hook
            *args: Positional arguments to pass to callbacks
            **kwargs: Keyword arguments to pass to callbacks
        """
        if hook_name not in self._action_hooks:
            return

        logger.debug(f"Executing async action hook: {hook_name}")

        tasks = []
        for callback in self._action_hooks[hook_name]:
            try:
                if asyncio.iscoroutinefunction(callback):
                    tasks.append(callback(*args, **kwargs))
                else:
                    # Run sync function in executor
                    tasks.append(asyncio.get_event_loop().run_in_executor(None, callback, *args, **kwargs))
            except Exception as e:
                logger.error(f"Error in async action hook {hook_name} -> {callback.__name__}: {e}")

        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)

    def apply_filters(self, hook_name: str, value: Any, *args, **kwargs) -> Any:
        """
        Apply filter hooks

        Passes the value through all registered filter callbacks.
        Each callback receives the current value and returns a modified value.

        Args:
            hook_name: Name of the hook
            value: Initial value to filter
            *args: Additional positional arguments to pass to callbacks
            **kwargs: Additional keyword arguments to pass to callbacks

        Returns:
            Filtered value after all callbacks
        """
        if hook_name not in self._filter_hooks:
            return value

        logger.debug(f"Applying filter hook: {hook_name}")

        current_value = value
        for callback in self._filter_hooks[hook_name]:
            try:
                current_value = callback(current_value, *args, **kwargs)
            except Exception as e:
                logger.error(f"Error in filter hook {hook_name} -> {callback.__name__}: {e}")

        return current_value

    async def apply_filters_async(self, hook_name: str, value: Any, *args, **kwargs) -> Any:
        """
        Apply async filter hooks

        Args:
            hook_name: Name of the hook
            value: Initial value to filter
            *args: Additional positional arguments
            **kwargs: Additional keyword arguments

        Returns:
            Filtered value
        """
        if hook_name not in self._filter_hooks:
            return value

        logger.debug(f"Applying async filter hook: {hook_name}")

        current_value = value
        for callback in self._filter_hooks[hook_name]:
            try:
                if asyncio.iscoroutinefunction(callback):
                    current_value = await callback(current_value, *args, **kwargs)
                else:
                    current_value = callback(current_value, *args, **kwargs)
            except Exception as e:
                logger.error(f"Error in async filter hook {hook_name} -> {callback.__name__}: {e}")

        return current_value

    def has_hook(self, hook_name: str) -> bool:
        """
        Check if a hook has any registered callbacks

        Args:
            hook_name: Name of the hook

        Returns:
            True if hook has callbacks
        """
        return (
            hook_name in self._action_hooks and len(self._action_hooks[hook_name]) > 0
        ) or (
            hook_name in self._filter_hooks and len(self._filter_hooks[hook_name]) > 0
        )

    def list_hooks(self) -> Dict[str, Dict[str, int]]:
        """
        List all registered hooks

        Returns:
            Dict with hook names and callback counts
        """
        return {
            "actions": {name: len(callbacks) for name, callbacks in self._action_hooks.items()},
            "filters": {name: len(callbacks) for name, callbacks in self._filter_hooks.items()},
        }


# =============================================================================
# Decorator-based Hook Registration
# =============================================================================

def action_hook(hook_name: str, priority: int = 10):
    """
    Decorator to register a function as an action hook

    Usage:
        @action_hook("project.created")
        def on_project_created(project):
            print(f"Project created: {project.name}")

    Args:
        hook_name: Name of the hook
        priority: Priority (lower runs first)
    """
    def decorator(func: Callable) -> Callable:
        # Note: Actual registration happens in plugin.activate()
        func._hook_type = "action"
        func._hook_name = hook_name
        func._hook_priority = priority
        return func
    return decorator


def filter_hook(hook_name: str, priority: int = 10):
    """
    Decorator to register a function as a filter hook

    Usage:
        @filter_hook("project.requirements")
        def enhance_requirements(requirements):
            return requirements + "\\n- Additional requirement"

    Args:
        hook_name: Name of the hook
        priority: Priority (lower runs first)
    """
    def decorator(func: Callable) -> Callable:
        func._hook_type = "filter"
        func._hook_name = hook_name
        func._hook_priority = priority
        return func
    return decorator


# =============================================================================
# Standard Platform Hooks
# =============================================================================

class Hooks:
    """
    Standard hook names available in ResoftAI

    This class documents all available hooks in the platform.
    """

    # Project lifecycle hooks
    PROJECT_CREATE_BEFORE = "project.create.before"
    PROJECT_CREATE_AFTER = "project.create.after"
    PROJECT_UPDATE_BEFORE = "project.update.before"
    PROJECT_UPDATE_AFTER = "project.update.after"
    PROJECT_DELETE_BEFORE = "project.delete.before"
    PROJECT_DELETE_AFTER = "project.delete.after"
    PROJECT_EXECUTE_START = "project.execute.start"
    PROJECT_EXECUTE_COMPLETE = "project.execute.complete"

    # File hooks
    FILE_CREATE_BEFORE = "file.create.before"
    FILE_CREATE_AFTER = "file.create.after"
    FILE_UPDATE_BEFORE = "file.update.before"
    FILE_UPDATE_AFTER = "file.update.after"
    FILE_DELETE_BEFORE = "file.delete.before"
    FILE_DELETE_AFTER = "file.delete.after"

    # Agent hooks
    AGENT_START = "agent.start"
    AGENT_COMPLETE = "agent.complete"
    AGENT_ERROR = "agent.error"

    # Code quality hooks
    CODE_ANALYZE = "code.analyze"
    CODE_FORMAT = "code.format"
    CODE_LINT = "code.lint"

    # LLM hooks
    LLM_REQUEST_BEFORE = "llm.request.before"
    LLM_REQUEST_AFTER = "llm.request.after"
    LLM_ERROR = "llm.error"

    # User hooks
    USER_LOGIN = "user.login"
    USER_LOGOUT = "user.logout"
    USER_REGISTER = "user.register"

    # Filter hooks (transform data)
    FILTER_PROJECT_REQUIREMENTS = "filter.project.requirements"
    FILTER_CODE_CONTENT = "filter.code.content"
    FILTER_LLM_PROMPT = "filter.llm.prompt"
    FILTER_LLM_RESPONSE = "filter.llm.response"
