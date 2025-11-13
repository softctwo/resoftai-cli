"""Performance monitoring and metrics collection."""
import time
import asyncio
from typing import Dict, Any, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import defaultdict, deque
import logging

logger = logging.getLogger(__name__)


@dataclass
class PerformanceMetrics:
    """Performance metrics data class."""
    request_count: int = 0
    error_count: int = 0
    average_response_time: float = 0.0
    p95_response_time: float = 0.0
    p99_response_time: float = 0.0
    active_agents: int = 0
    completed_workflows: int = 0
    failed_workflows: int = 0
    llm_requests: int = 0
    llm_tokens_used: int = 0
    file_operations: int = 0
    database_operations: int = 0


@dataclass
class AgentActivity:
    """Agent activity tracking."""
    agent_type: str
    start_time: datetime
    end_time: Optional[datetime] = None
    duration: Optional[float] = None
    success: bool = True
    error_message: Optional[str] = None
    tokens_used: int = 0
    files_processed: int = 0


class PerformanceMonitor:
    """Performance monitoring system."""
    
    def __init__(self, window_size: int = 1000):
        self.window_size = window_size
        self.metrics = PerformanceMetrics()
        self.response_times = deque(maxlen=window_size)
        self.agent_activities: Dict[str, AgentActivity] = {}
        self.workflow_stats = defaultdict(int)
        self.llm_stats = defaultdict(int)
        self.file_stats = defaultdict(int)
        self.db_stats = defaultdict(int)
        self._lock = asyncio.Lock()
    
    async def record_request(self, response_time: float, success: bool = True):
        """Record an API request."""
        async with self._lock:
            self.metrics.request_count += 1
            self.response_times.append(response_time)
            
            if not success:
                self.metrics.error_count += 1
            
            # Update response time statistics
            if self.response_times:
                sorted_times = sorted(self.response_times)
                self.metrics.average_response_time = sum(sorted_times) / len(sorted_times)
                self.metrics.p95_response_time = sorted_times[int(len(sorted_times) * 0.95)]
                self.metrics.p99_response_time = sorted_times[int(len(sorted_times) * 0.99)]
    
    async def start_agent_activity(self, agent_id: str, agent_type: str) -> None:
        """Start tracking an agent activity."""
        async with self._lock:
            self.agent_activities[agent_id] = AgentActivity(
                agent_type=agent_type,
                start_time=datetime.utcnow()
            )
            self.metrics.active_agents += 1
    
    async def end_agent_activity(
        self, 
        agent_id: str, 
        success: bool = True, 
        error_message: Optional[str] = None,
        tokens_used: int = 0,
        files_processed: int = 0
    ) -> None:
        """End tracking an agent activity."""
        async with self._lock:
            if agent_id in self.agent_activities:
                activity = self.agent_activities[agent_id]
                activity.end_time = datetime.utcnow()
                activity.duration = (activity.end_time - activity.start_time).total_seconds()
                activity.success = success
                activity.error_message = error_message
                activity.tokens_used = tokens_used
                activity.files_processed = files_processed
                
                self.metrics.active_agents -= 1
                
                # Log completed activity
                logger.info(
                    f"Agent {agent_id} ({activity.agent_type}) completed in "
                    f"{activity.duration:.2f}s, success: {success}, "
                    f"tokens: {tokens_used}, files: {files_processed}"
                )
    
    async def record_workflow_completion(self, success: bool = True):
        """Record workflow completion."""
        async with self._lock:
            if success:
                self.metrics.completed_workflows += 1
            else:
                self.metrics.failed_workflows += 1
    
    async def record_llm_request(self, tokens_used: int = 0):
        """Record LLM request."""
        async with self._lock:
            self.metrics.llm_requests += 1
            self.metrics.llm_tokens_used += tokens_used
    
    async def record_file_operation(self):
        """Record file operation."""
        async with self._lock:
            self.metrics.file_operations += 1
    
    async def record_database_operation(self):
        """Record database operation."""
        async with self._lock:
            self.metrics.database_operations += 1
    
    async def get_metrics(self) -> PerformanceMetrics:
        """Get current performance metrics."""
        async with self._lock:
            return self.metrics
    
    async def get_agent_activities(self) -> Dict[str, AgentActivity]:
        """Get current agent activities."""
        async with self._lock:
            return self.agent_activities.copy()
    
    async def reset_metrics(self):
        """Reset all metrics."""
        async with self._lock:
            self.metrics = PerformanceMetrics()
            self.response_times.clear()
            self.agent_activities.clear()
            self.workflow_stats.clear()
            self.llm_stats.clear()
            self.file_stats.clear()
            self.db_stats.clear()


# Global performance monitor instance
performance_monitor = PerformanceMonitor()


def monitor_request(func: Callable) -> Callable:
    """Decorator to monitor API request performance."""
    async def wrapper(*args, **kwargs):
        start_time = time.time()
        success = True
        
        try:
            result = await func(*args, **kwargs)
            return result
        except Exception as e:
            success = False
            raise e
        finally:
            response_time = time.time() - start_time
            await performance_monitor.record_request(response_time, success)
    
    return wrapper


def monitor_agent_activity(agent_type: str):
    """Decorator to monitor agent activity performance."""
    def decorator(func: Callable) -> Callable:
        async def wrapper(*args, **kwargs):
            # Generate agent ID from function name and timestamp
            agent_id = f"{func.__name__}_{int(time.time())}"
            
            await performance_monitor.start_agent_activity(agent_id, agent_type)
            
            success = True
            error_message = None
            tokens_used = 0
            files_processed = 0
            
            try:
                result = await func(*args, **kwargs)
                return result
            except Exception as e:
                success = False
                error_message = str(e)
                raise e
            finally:
                await performance_monitor.end_agent_activity(
                    agent_id, success, error_message, tokens_used, files_processed
                )
        
        return wrapper
    
    return decorator