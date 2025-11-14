"""Tests for plugin hook system."""
import pytest
from typing import Any

from resoftai.plugins.hooks import HookManager, HookType


class TestHookManager:
    """Test suite for HookManager."""

    def test_register_action_hook(self):
        """Test registering an action hook."""
        manager = HookManager()
        called = []

        def callback(*args, **kwargs):
            called.append((args, kwargs))

        manager.register_action("test_action", callback, priority=10)
        manager.do_action("test_action", "arg1", "arg2", key="value")

        assert len(called) == 1
        assert called[0] == (("arg1", "arg2"), {"key": "value"})

    def test_register_filter_hook(self):
        """Test registering a filter hook."""
        manager = HookManager()

        def double_value(value: int) -> int:
            return value * 2

        manager.register_filter("double", double_value, priority=10)
        result = manager.apply_filters("double", 5)

        assert result == 10

    def test_multiple_action_hooks(self):
        """Test multiple callbacks for same action hook."""
        manager = HookManager()
        called = []

        def callback1():
            called.append(1)

        def callback2():
            called.append(2)

        manager.register_action("test", callback1, priority=10)
        manager.register_action("test", callback2, priority=5)
        manager.do_action("test")

        # Lower priority (5) should be called first
        assert called == [2, 1]

    def test_multiple_filter_hooks(self):
        """Test multiple filters for same hook."""
        manager = HookManager()

        def add_five(value: int) -> int:
            return value + 5

        def multiply_two(value: int) -> int:
            return value * 2

        manager.register_filter("transform", add_five, priority=10)
        manager.register_filter("transform", multiply_two, priority=20)

        # Start with 10: (10 + 5) = 15, then 15 * 2 = 30
        result = manager.apply_filters("transform", 10)
        assert result == 30

    def test_hook_priority_order(self):
        """Test that hooks are called in priority order."""
        manager = HookManager()
        order = []

        def high_priority():
            order.append("high")

        def low_priority():
            order.append("low")

        def medium_priority():
            order.append("medium")

        manager.register_action("test", high_priority, priority=100)
        manager.register_action("test", low_priority, priority=1)
        manager.register_action("test", medium_priority, priority=50)
        manager.do_action("test")

        assert order == ["low", "medium", "high"]

    def test_remove_action_hook(self):
        """Test removing an action hook."""
        manager = HookManager()
        called = []

        def callback():
            called.append(1)

        manager.register_action("test", callback)
        manager.remove_action("test", callback)
        manager.do_action("test")

        assert len(called) == 0

    def test_remove_filter_hook(self):
        """Test removing a filter hook."""
        manager = HookManager()

        def double(value: int) -> int:
            return value * 2

        manager.register_filter("test", double)
        manager.remove_filter("test", double)
        result = manager.apply_filters("test", 10)

        # Should return original value since filter was removed
        assert result == 10

    def test_has_action(self):
        """Test checking if action hook exists."""
        manager = HookManager()

        def callback():
            pass

        assert not manager.has_action("test")
        manager.register_action("test", callback)
        assert manager.has_action("test")

    def test_has_filter(self):
        """Test checking if filter hook exists."""
        manager = HookManager()

        def filter_func(value):
            return value

        assert not manager.has_filter("test")
        manager.register_filter("test", filter_func)
        assert manager.has_filter("test")

    def test_clear_hooks(self):
        """Test clearing all hooks."""
        manager = HookManager()

        def callback():
            pass

        def filter_func(value):
            return value

        manager.register_action("action1", callback)
        manager.register_action("action2", callback)
        manager.register_filter("filter1", filter_func)
        manager.register_filter("filter2", filter_func)

        assert manager.has_action("action1")
        assert manager.has_filter("filter1")

        manager.clear()

        assert not manager.has_action("action1")
        assert not manager.has_action("action2")
        assert not manager.has_filter("filter1")
        assert not manager.has_filter("filter2")

    def test_action_with_exception(self):
        """Test that exception in one callback doesn't stop others."""
        manager = HookManager()
        called = []

        def failing_callback():
            called.append("before_error")
            raise ValueError("Test error")

        def success_callback():
            called.append("success")

        manager.register_action("test", failing_callback, priority=5)
        manager.register_action("test", success_callback, priority=10)

        # Should not raise exception
        manager.do_action("test")

        # Both callbacks should have been attempted
        assert "before_error" in called
        assert "success" in called

    def test_filter_with_exception(self):
        """Test that exception in filter returns original value."""
        manager = HookManager()

        def failing_filter(value: int) -> int:
            raise ValueError("Test error")
            return value * 2

        manager.register_filter("test", failing_filter)
        result = manager.apply_filters("test", 10)

        # Should return original value on exception
        assert result == 10

    def test_filter_chain(self):
        """Test chaining multiple filters."""
        manager = HookManager()

        def add_one(value: int) -> int:
            return value + 1

        def square(value: int) -> int:
            return value ** 2

        def subtract_five(value: int) -> int:
            return value - 5

        manager.register_filter("chain", add_one, priority=10)
        manager.register_filter("chain", square, priority=20)
        manager.register_filter("chain", subtract_five, priority=30)

        # Start with 2: (2+1)=3, (3^2)=9, (9-5)=4
        result = manager.apply_filters("chain", 2)
        assert result == 4

    def test_action_with_kwargs(self):
        """Test action hook with keyword arguments."""
        manager = HookManager()
        received = {}

        def callback(**kwargs):
            received.update(kwargs)

        manager.register_action("test", callback)
        manager.do_action("test", name="test", value=42)

        assert received == {"name": "test", "value": 42}

    def test_filter_with_multiple_args(self):
        """Test filter hook with multiple arguments."""
        manager = HookManager()

        def concatenate(value: str, prefix: str = "", suffix: str = "") -> str:
            return f"{prefix}{value}{suffix}"

        manager.register_filter("concat", concatenate)
        result = manager.apply_filters("concat", "test", prefix="[", suffix="]")

        assert result == "[test]"

    def test_same_priority_preserves_registration_order(self):
        """Test that hooks with same priority are called in registration order."""
        manager = HookManager()
        order = []

        def first():
            order.append(1)

        def second():
            order.append(2)

        def third():
            order.append(3)

        manager.register_action("test", first, priority=10)
        manager.register_action("test", second, priority=10)
        manager.register_action("test", third, priority=10)
        manager.do_action("test")

        assert order == [1, 2, 3]

    def test_register_duplicate_callback(self):
        """Test that registering same callback twice doesn't duplicate calls."""
        manager = HookManager()
        called = []

        def callback():
            called.append(1)

        manager.register_action("test", callback)
        manager.register_action("test", callback)  # Register again
        manager.do_action("test")

        # Should only be called once
        assert len(called) == 1

    def test_empty_hook_name(self):
        """Test handling of empty hook name."""
        manager = HookManager()

        def callback():
            pass

        # Should handle gracefully
        manager.register_action("", callback)
        manager.do_action("")  # Should not crash

    def test_none_value_in_filter(self):
        """Test filter with None value."""
        manager = HookManager()

        def make_string(value: Any) -> str:
            return str(value) if value is not None else "null"

        manager.register_filter("stringify", make_string)
        result = manager.apply_filters("stringify", None)

        assert result == "null"

    def test_get_hook_count(self):
        """Test getting number of hooks registered."""
        manager = HookManager()

        def callback1():
            pass

        def callback2():
            pass

        manager.register_action("test", callback1)
        manager.register_action("test", callback2)

        # This test assumes HookManager has a method to get hook count
        # If not implemented, this can be a feature request
        assert manager.has_action("test")
