"""Tests for performance monitoring utilities."""
import pytest
import asyncio
import time
from resoftai.utils.performance import (
    PerformanceMonitor,
    WebSocketMetrics,
    MessageBatcher,
    timing_decorator,
    get_performance_report
)


class TestPerformanceMonitor:
    """Test PerformanceMonitor class."""

    def test_record_timing(self):
        """Test recording timing metrics."""
        monitor = PerformanceMonitor(max_samples=100)

        # Record some timings
        monitor.record_timing("test_operation", 0.1)
        monitor.record_timing("test_operation", 0.2)
        monitor.record_timing("test_operation", 0.15)

        stats = monitor.get_stats("test_operation")
        assert stats['count'] == 3
        assert stats['min'] == 0.1
        assert stats['max'] == 0.2
        assert stats['avg'] == pytest.approx(0.15, rel=0.01)
        assert stats['total'] == pytest.approx(0.45, rel=0.01)

    def test_increment_counter(self):
        """Test incrementing counters."""
        monitor = PerformanceMonitor()

        monitor.increment_counter("api_calls")
        monitor.increment_counter("api_calls")
        monitor.increment_counter("api_calls", 3)

        stats = monitor.get_all_stats()
        assert stats['counters']['counter.api_calls'] == 5

    def test_get_stats_empty(self):
        """Test getting stats for non-existent metric."""
        monitor = PerformanceMonitor()

        stats = monitor.get_stats("nonexistent")
        assert stats == {}

    def test_reset(self):
        """Test resetting all metrics."""
        monitor = PerformanceMonitor()

        monitor.record_timing("test", 0.1)
        monitor.increment_counter("count")

        monitor.reset()

        stats = monitor.get_all_stats()
        assert len(stats['counters']) == 0

    def test_max_samples(self):
        """Test max samples limit."""
        monitor = PerformanceMonitor(max_samples=5)

        for i in range(10):
            monitor.record_timing("test", i * 0.1)

        stats = monitor.get_stats("test")
        assert stats['count'] == 5  # Should keep only last 5


class TestWebSocketMetrics:
    """Test WebSocketMetrics class."""

    def test_connection_lifecycle(self):
        """Test connection open and close."""
        metrics = WebSocketMetrics()

        metrics.connection_opened()
        metrics.connection_opened()

        assert metrics.active_connections == 2
        assert metrics.total_connections == 2

        metrics.connection_closed()

        assert metrics.active_connections == 1
        assert metrics.total_disconnections == 1

    def test_message_tracking(self):
        """Test message and byte tracking."""
        metrics = WebSocketMetrics()

        metrics.message_sent(100)
        metrics.message_sent(200)
        metrics.message_received(150)

        assert metrics.messages_sent == 2
        assert metrics.bytes_sent == 300
        assert metrics.messages_received == 1
        assert metrics.bytes_received == 150

    def test_error_tracking(self):
        """Test error counting."""
        metrics = WebSocketMetrics()

        metrics.error_occurred()
        metrics.error_occurred()

        assert metrics.errors == 2

    def test_reconnection_tracking(self):
        """Test reconnection counting."""
        metrics = WebSocketMetrics()

        metrics.reconnection_occurred()

        assert metrics.reconnections == 1

    def test_get_stats(self):
        """Test getting comprehensive stats."""
        metrics = WebSocketMetrics()

        metrics.connection_opened()
        metrics.message_sent(100)
        metrics.message_sent(200)
        metrics.message_received(300)

        stats = metrics.get_stats()

        assert stats['active_connections'] == 1
        assert stats['messages_sent'] == 2
        assert stats['bytes_sent'] == 300
        assert stats['avg_message_size_sent'] == 150.0
        assert stats['avg_message_size_received'] == 300.0


class TestMessageBatcher:
    """Test MessageBatcher class."""

    @pytest.mark.asyncio
    async def test_batch_flush_on_size(self):
        """Test batch flushes when size limit reached."""
        batcher = MessageBatcher(batch_size=3, flush_interval=1.0)
        flushed_batches = []

        async def flush_callback(messages):
            flushed_batches.append(messages)

        # Add messages
        await batcher.add_message("test_key", "msg1", flush_callback)
        await batcher.add_message("test_key", "msg2", flush_callback)
        await batcher.add_message("test_key", "msg3", flush_callback)

        # Should have flushed immediately after 3rd message
        await asyncio.sleep(0.1)
        assert len(flushed_batches) == 1
        assert flushed_batches[0] == ["msg1", "msg2", "msg3"]

    @pytest.mark.asyncio
    async def test_batch_flush_on_timer(self):
        """Test batch flushes after timeout."""
        batcher = MessageBatcher(batch_size=10, flush_interval=0.2)
        flushed_batches = []

        async def flush_callback(messages):
            flushed_batches.append(messages)

        # Add messages (less than batch_size)
        await batcher.add_message("test_key", "msg1", flush_callback)
        await batcher.add_message("test_key", "msg2", flush_callback)

        # Should not flush immediately
        assert len(flushed_batches) == 0

        # Wait for timer
        await asyncio.sleep(0.3)

        # Should have flushed after timer
        assert len(flushed_batches) == 1
        assert flushed_batches[0] == ["msg1", "msg2"]

    @pytest.mark.asyncio
    async def test_multiple_batch_keys(self):
        """Test batching with different keys."""
        batcher = MessageBatcher(batch_size=2, flush_interval=1.0)
        flushed_batches = {}

        async def make_flush_callback(key):
            async def flush_callback(messages):
                flushed_batches[key] = messages
            return flush_callback

        # Add messages to different keys
        cb1 = await make_flush_callback("key1")
        cb2 = await make_flush_callback("key2")

        await batcher.add_message("key1", "msg1a", cb1)
        await batcher.add_message("key2", "msg2a", cb2)
        await batcher.add_message("key1", "msg1b", cb1)

        # key1 should flush (reached batch_size)
        await asyncio.sleep(0.1)
        assert "key1" in flushed_batches
        assert flushed_batches["key1"] == ["msg1a", "msg1b"]


class TestTimingDecorator:
    """Test timing_decorator functionality."""

    @pytest.mark.asyncio
    async def test_async_function_timing(self):
        """Test timing decorator on async function."""
        monitor = PerformanceMonitor()

        @timing_decorator("test_async")
        async def async_operation():
            await asyncio.sleep(0.1)
            return "result"

        # Patch global monitor
        import resoftai.utils.performance as perf_module
        original_monitor = perf_module.performance_monitor
        perf_module.performance_monitor = monitor

        try:
            result = await async_operation()
            assert result == "result"

            stats = monitor.get_stats("test_async")
            assert stats['count'] == 1
            assert stats['avg'] >= 0.1
        finally:
            perf_module.performance_monitor = original_monitor

    def test_sync_function_timing(self):
        """Test timing decorator on sync function."""
        monitor = PerformanceMonitor()

        @timing_decorator("test_sync")
        def sync_operation():
            time.sleep(0.1)
            return "result"

        # Patch global monitor
        import resoftai.utils.performance as perf_module
        original_monitor = perf_module.performance_monitor
        perf_module.performance_monitor = monitor

        try:
            result = sync_operation()
            assert result == "result"

            stats = monitor.get_stats("test_sync")
            assert stats['count'] == 1
            assert stats['avg'] >= 0.1
        finally:
            perf_module.performance_monitor = original_monitor

    @pytest.mark.asyncio
    async def test_custom_metric_name(self):
        """Test timing decorator with custom metric name."""
        monitor = PerformanceMonitor()

        @timing_decorator("custom_name")
        async def operation():
            return "done"

        import resoftai.utils.performance as perf_module
        original_monitor = perf_module.performance_monitor
        perf_module.performance_monitor = monitor

        try:
            await operation()
            stats = monitor.get_stats("custom_name")
            assert stats['count'] == 1
        finally:
            perf_module.performance_monitor = original_monitor


class TestPerformanceReport:
    """Test get_performance_report function."""

    def test_performance_report_structure(self):
        """Test performance report contains expected fields."""
        report = get_performance_report()

        assert 'timestamp' in report
        assert 'performance_metrics' in report
        assert 'websocket_metrics' in report

        # Check websocket metrics structure
        ws_metrics = report['websocket_metrics']
        assert 'active_connections' in ws_metrics
        assert 'total_connections' in ws_metrics
        assert 'messages_sent' in ws_metrics
        assert 'bytes_sent' in ws_metrics


# Integration tests
@pytest.mark.asyncio
async def test_integration_performance_tracking():
    """Integration test for performance tracking."""
    monitor = PerformanceMonitor()

    # Simulate operations
    monitor.record_timing("api.create_project", 0.123)
    monitor.record_timing("api.create_project", 0.145)
    monitor.increment_counter("api.requests")
    monitor.increment_counter("api.requests")

    stats = monitor.get_all_stats()

    assert 'create_project' in stats
    assert stats['create_project']['count'] == 2
    assert stats['counters']['counter.api.requests'] == 2
