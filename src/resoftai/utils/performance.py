"""Performance monitoring and optimization utilities."""
import time
import logging
import functools
from typing import Dict, Any, Callable, Optional
from datetime import datetime
from collections import defaultdict, deque
import asyncio

logger = logging.getLogger(__name__)


class PerformanceMonitor:
    """Monitor and collect performance metrics."""

    def __init__(self, max_samples: int = 1000):
        """
        Initialize performance monitor.

        Args:
            max_samples: Maximum number of samples to keep per metric
        """
        self.metrics: Dict[str, deque] = defaultdict(lambda: deque(maxlen=max_samples))
        self.counters: Dict[str, int] = defaultdict(int)
        self.start_time = time.time()

    def record_timing(self, name: str, duration: float):
        """
        Record timing metric.

        Args:
            name: Metric name
            duration: Duration in seconds
        """
        self.metrics[f"timing.{name}"].append({
            'duration': duration,
            'timestamp': datetime.utcnow().isoformat()
        })

    def increment_counter(self, name: str, value: int = 1):
        """
        Increment counter metric.

        Args:
            name: Counter name
            value: Increment value
        """
        self.counters[f"counter.{name}"] += value

    def get_stats(self, name: str) -> Dict[str, Any]:
        """
        Get statistics for a metric.

        Args:
            name: Metric name

        Returns:
            Dictionary with min, max, avg, count
        """
        metric_name = f"timing.{name}"
        if metric_name not in self.metrics or not self.metrics[metric_name]:
            return {}

        durations = [m['duration'] for m in self.metrics[metric_name]]
        return {
            'min': min(durations),
            'max': max(durations),
            'avg': sum(durations) / len(durations),
            'count': len(durations),
            'total': sum(durations)
        }

    def get_all_stats(self) -> Dict[str, Any]:
        """Get all metrics statistics."""
        stats = {}

        # Timing metrics
        for name in self.metrics.keys():
            if name.startswith('timing.'):
                metric_name = name.replace('timing.', '')
                stats[metric_name] = self.get_stats(metric_name)

        # Counter metrics
        stats['counters'] = dict(self.counters)

        # Uptime
        stats['uptime_seconds'] = time.time() - self.start_time

        return stats

    def reset(self):
        """Reset all metrics."""
        self.metrics.clear()
        self.counters.clear()
        self.start_time = time.time()


# Global performance monitor instance
performance_monitor = PerformanceMonitor()


def timing_decorator(name: Optional[str] = None):
    """
    Decorator to measure function execution time.

    Args:
        name: Optional metric name (defaults to function name)

    Example:
        @timing_decorator("api.create_project")
        async def create_project():
            ...
    """
    def decorator(func: Callable):
        metric_name = name or func.__name__

        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                return result
            finally:
                duration = time.time() - start_time
                performance_monitor.record_timing(metric_name, duration)
                if duration > 1.0:  # Log slow operations
                    logger.warning(f"Slow operation: {metric_name} took {duration:.2f}s")

        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                return result
            finally:
                duration = time.time() - start_time
                performance_monitor.record_timing(metric_name, duration)
                if duration > 1.0:
                    logger.warning(f"Slow operation: {metric_name} took {duration:.2f}s")

        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper

    return decorator


class WebSocketMetrics:
    """Track WebSocket-specific metrics."""

    def __init__(self):
        """Initialize WebSocket metrics."""
        self.active_connections = 0
        self.total_connections = 0
        self.total_disconnections = 0
        self.messages_sent = 0
        self.messages_received = 0
        self.bytes_sent = 0
        self.bytes_received = 0
        self.errors = 0
        self.reconnections = 0

    def connection_opened(self):
        """Record connection opened."""
        self.active_connections += 1
        self.total_connections += 1
        performance_monitor.increment_counter('websocket.connections.total')
        performance_monitor.increment_counter('websocket.connections.active')

    def connection_closed(self):
        """Record connection closed."""
        self.active_connections = max(0, self.active_connections - 1)
        self.total_disconnections += 1
        performance_monitor.increment_counter('websocket.disconnections')
        performance_monitor.counters['counter.websocket.connections.active'] -= 1

    def message_sent(self, size_bytes: int):
        """
        Record message sent.

        Args:
            size_bytes: Message size in bytes
        """
        self.messages_sent += 1
        self.bytes_sent += size_bytes
        performance_monitor.increment_counter('websocket.messages.sent')
        performance_monitor.increment_counter('websocket.bytes.sent', size_bytes)

    def message_received(self, size_bytes: int):
        """
        Record message received.

        Args:
            size_bytes: Message size in bytes
        """
        self.messages_received += 1
        self.bytes_received += size_bytes
        performance_monitor.increment_counter('websocket.messages.received')
        performance_monitor.increment_counter('websocket.bytes.received', size_bytes)

    def error_occurred(self):
        """Record error."""
        self.errors += 1
        performance_monitor.increment_counter('websocket.errors')

    def reconnection_occurred(self):
        """Record reconnection."""
        self.reconnections += 1
        performance_monitor.increment_counter('websocket.reconnections')

    def get_stats(self) -> Dict[str, Any]:
        """Get WebSocket statistics."""
        return {
            'active_connections': self.active_connections,
            'total_connections': self.total_connections,
            'total_disconnections': self.total_disconnections,
            'messages_sent': self.messages_sent,
            'messages_received': self.messages_received,
            'bytes_sent': self.bytes_sent,
            'bytes_received': self.bytes_received,
            'errors': self.errors,
            'reconnections': self.reconnections,
            'avg_message_size_sent': (
                self.bytes_sent / self.messages_sent if self.messages_sent > 0 else 0
            ),
            'avg_message_size_received': (
                self.bytes_received / self.messages_received if self.messages_received > 0 else 0
            )
        }


# Global WebSocket metrics instance
websocket_metrics = WebSocketMetrics()


class MessageBatcher:
    """Batch multiple messages for efficient transmission."""

    def __init__(self, batch_size: int = 10, flush_interval: float = 0.1):
        """
        Initialize message batcher.

        Args:
            batch_size: Maximum messages per batch
            flush_interval: Interval to flush batches (seconds)
        """
        self.batch_size = batch_size
        self.flush_interval = flush_interval
        self.batches: Dict[str, list] = defaultdict(list)
        self.timers: Dict[str, asyncio.Task] = {}

    async def add_message(self, key: str, message: Any, flush_callback: Callable):
        """
        Add message to batch.

        Args:
            key: Batch key (e.g., user_id or room)
            message: Message to batch
            flush_callback: Callback to flush batch
        """
        self.batches[key].append(message)

        # Flush if batch is full
        if len(self.batches[key]) >= self.batch_size:
            await self._flush_batch(key, flush_callback)
        else:
            # Schedule flush timer
            if key not in self.timers:
                self.timers[key] = asyncio.create_task(
                    self._schedule_flush(key, flush_callback)
                )

    async def _schedule_flush(self, key: str, flush_callback: Callable):
        """Schedule delayed flush."""
        await asyncio.sleep(self.flush_interval)
        await self._flush_batch(key, flush_callback)

    async def _flush_batch(self, key: str, flush_callback: Callable):
        """Flush batch."""
        if key in self.batches and self.batches[key]:
            messages = self.batches[key]
            self.batches[key] = []

            # Cancel timer
            if key in self.timers:
                if not self.timers[key].done():
                    self.timers[key].cancel()
                del self.timers[key]

            # Call flush callback
            await flush_callback(messages)

            performance_monitor.increment_counter('message_batcher.batches_flushed')
            performance_monitor.increment_counter('message_batcher.messages_batched', len(messages))


# Global message batcher instance
message_batcher = MessageBatcher()


def get_performance_report() -> Dict[str, Any]:
    """
    Get comprehensive performance report.

    Returns:
        Dictionary with all performance metrics
    """
    return {
        'timestamp': datetime.utcnow().isoformat(),
        'performance_metrics': performance_monitor.get_all_stats(),
        'websocket_metrics': websocket_metrics.get_stats()
    }
