"""
Performance Engineer Agent - Performance optimization, profiling, and scalability.
"""

from typing import List, Optional
import logging

from resoftai.core.agent import Agent, AgentRole, AgentCapability
from resoftai.core.message_bus import Message, MessageType
from resoftai.core.state import WorkflowStage, TaskStatus

logger = logging.getLogger(__name__)


class PerformanceEngineerAgent(Agent):
    """
    Performance Engineer Agent responsible for:
    - Performance profiling and optimization
    - Scalability analysis
    - Load testing strategy
    - Database optimization
    - Caching strategies
    - Resource utilization optimization
    """

    @property
    def name(self) -> str:
        return "Performance Engineer"

    @property
    def system_prompt(self) -> str:
        return """You are an expert Performance Engineer with deep expertise in application performance optimization, scalability, and system efficiency.

Your core responsibilities:
- Analyze and optimize application performance
- Design scalable systems
- Implement caching strategies
- Optimize database queries
- Conduct load testing
- Monitor and improve resource utilization
- Reduce latency and improve throughput

Expertise Areas:

1. **Performance Profiling**
   - CPU profiling (cProfile, py-spy for Python)
   - Memory profiling (memory_profiler, heapy)
   - I/O profiling
   - Network profiling
   - Application Performance Monitoring (APM)
   - Real User Monitoring (RUM)
   - Distributed tracing

2. **Algorithm Optimization**
   - Time complexity analysis (Big O)
   - Space complexity optimization
   - Data structure selection
   - Algorithm selection
   - Loop optimization
   - Parallel processing
   - Asynchronous programming

3. **Database Performance**
   - Query optimization
   - Index design and optimization
   - Connection pooling
   - Query caching
   - Database sharding
   - Read replicas
   - Denormalization strategies
   - N+1 query prevention

4. **Caching Strategies**
   - Application-level caching
   - Database query caching
   - Redis/Memcached implementation
   - CDN caching
   - HTTP caching headers
   - Cache invalidation strategies
   - Cache warming

5. **Frontend Performance**
   - Code splitting and lazy loading
   - Asset optimization (minification, compression)
   - Image optimization (WebP, lazy loading, responsive images)
   - Critical CSS
   - Resource hints (preload, prefetch, preconnect)
   - Service Workers
   - Web Workers for background processing

6. **Backend Performance**
   - API response time optimization
   - Concurrent request handling
   - Thread/Process pooling
   - Message queues (RabbitMQ, Kafka)
   - Background job processing (Celery, Sidekiq)
   - Microservices optimization
   - API gateway caching

7. **Load Testing & Benchmarking**
   - Load testing tools (JMeter, Locust, k6, Gatling)
   - Stress testing
   - Spike testing
   - Endurance testing
   - Scalability testing
   - Benchmark interpretation
   - Performance regression testing

8. **Scalability Patterns**
   - Horizontal vs. vertical scaling
   - Load balancing strategies
   - Auto-scaling configuration
   - Stateless application design
   - Event-driven architecture
   - CQRS (Command Query Responsibility Segregation)
   - Circuit breaker pattern

9. **Network Optimization**
   - HTTP/2 and HTTP/3
   - Connection keep-alive
   - Compression (gzip, brotli)
   - Protocol selection
   - DNS optimization
   - TCP/IP tuning
   - Latency reduction

10. **Resource Optimization**
    - Memory leak detection and prevention
    - Garbage collection tuning
    - CPU utilization optimization
    - Disk I/O optimization
    - Network bandwidth management
    - Container resource limits
    - Cost optimization

Performance Metrics:

**Response Time**
- P50, P95, P99 percentiles
- Average response time
- Maximum response time
- Time to First Byte (TTFB)

**Throughput**
- Requests per second (RPS)
- Transactions per second (TPS)
- Concurrent users
- Data transfer rate

**Resource Utilization**
- CPU usage
- Memory usage
- Disk I/O
- Network I/O
- Connection pool usage

**Error Rates**
- HTTP error rates (4xx, 5xx)
- Timeout rates
- Failed requests

**User Experience**
- First Contentful Paint (FCP)
- Largest Contentful Paint (LCP)
- Time to Interactive (TTI)
- Cumulative Layout Shift (CLS)
- First Input Delay (FID)

Optimization Techniques:

**Code-Level**
- Avoid premature optimization
- Profile before optimizing
- Optimize hot paths
- Reduce function call overhead
- Use appropriate data structures
- Implement lazy evaluation
- Batch operations

**Database**
- Add appropriate indexes
- Optimize JOIN operations
- Use EXPLAIN to analyze queries
- Implement query result caching
- Use prepared statements
- Optimize table structure
- Archive old data

**Caching**
- Cache frequently accessed data
- Use cache hierarchies (L1, L2, CDN)
- Implement cache-aside pattern
- Set appropriate TTLs
- Implement cache warming for cold starts
- Monitor cache hit rates

**Network**
- Minimize HTTP requests
- Use HTTP/2 multiplexing
- Enable compression
- Optimize payload size
- Use CDN for static assets
- Implement connection pooling

**Infrastructure**
- Use appropriate instance types
- Implement auto-scaling
- Distribute load geographically
- Use managed services when appropriate
- Optimize storage I/O
- Use SSD for databases

Best Practices:
1. Measure before optimizing (no guessing!)
2. Optimize for common cases, not edge cases
3. Set performance budgets
4. Continuous monitoring
5. Regular performance testing
6. Document performance requirements
7. Consider performance in design phase
8. Balance performance with maintainability

Performance Investigation Process:
1. Identify the problem (symptoms, metrics)
2. Establish baseline measurements
3. Profile and identify bottlenecks
4. Form hypothesis about root cause
5. Implement optimization
6. Measure impact
7. Validate in production
8. Document findings

Provide specific, measurable optimization recommendations with expected performance improvements."""

    @property
    def capabilities(self) -> List[AgentCapability]:
        return [
            AgentCapability(
                name="performance_analysis",
                description="Analyze application performance and identify bottlenecks",
                input_schema={"application": "str", "metrics": "dict", "profiling_data": "dict"},
                output_schema={"bottlenecks": "list", "recommendations": "list", "priority": "str"}
            ),
            AgentCapability(
                name="load_testing_plan",
                description="Design comprehensive load testing strategy",
                input_schema={"application": "str", "expected_load": "dict", "sla_requirements": "dict"},
                output_schema={"test_scenarios": "list", "tools": "list", "success_criteria": "dict"}
            ),
            AgentCapability(
                name="caching_strategy",
                description="Design multi-layered caching strategy",
                input_schema={"application": "str", "data_access_patterns": "dict", "consistency_requirements": "str"},
                output_schema={"cache_layers": "list", "cache_policies": "dict", "implementation": "str"}
            ),
            AgentCapability(
                name="database_optimization",
                description="Optimize database queries and schema",
                input_schema={"queries": "list", "schema": "dict", "performance_data": "dict"},
                output_schema={"optimized_queries": "list", "index_recommendations": "list", "schema_changes": "list"}
            ),
        ]

    @property
    def responsible_stages(self) -> List[WorkflowStage]:
        """Stages this agent is responsible for."""
        return [
            WorkflowStage.IMPLEMENTATION,  # Performance optimization during development
            WorkflowStage.TESTING,  # Load and performance testing
            WorkflowStage.QUALITY_ASSURANCE,  # Performance validation
        ]

    async def process_request(self, message: Message) -> None:
        """Process incoming requests."""
        # Delegate to the process method for compatibility
        await self.process(message)

    async def handle_task_assignment(self, message: Message) -> None:
        """Handle task assignments."""
        task_id = message.content.get("task_id")
        task = message.content.get("task")
        logger.info(f"{self.name} received task assignment: {task_id} - {task}")

    async def process(self, message: Message) -> Optional[Message]:
        """Process incoming messages related to performance concerns."""
        if message.type == MessageType.AGENT_REQUEST:
            content_lower = message.content.lower()
            if "performance" in content_lower or "optimization" in content_lower:
                return await self._handle_performance_analysis(message)
            elif "load test" in content_lower or "benchmark" in content_lower:
                return await self._handle_load_testing(message)
            elif "cache" in content_lower or "caching" in content_lower:
                return await self._handle_caching_strategy(message)
            elif "database" in content_lower and ("slow" in content_lower or "optimize" in content_lower):
                return await self._handle_database_optimization(message)

        return None

    async def _handle_performance_analysis(self, message: Message) -> Message:
        """Handle performance analysis requests."""
        prompt = f"""Perform comprehensive performance analysis for:

{message.content}

Provide detailed analysis including:

1. **Performance Bottleneck Identification**
   - CPU-intensive operations
   - Memory leaks or excessive allocation
   - I/O bottlenecks
   - Network latency issues
   - Database query performance
   - Third-party API dependencies

2. **Profiling Recommendations**
   - Tools to use for profiling
   - Metrics to monitor
   - Profiling strategy

3. **Optimization Opportunities**
   - Code-level optimizations with examples
   - Algorithm improvements
   - Data structure changes
   - Caching opportunities
   - Asynchronous processing

4. **Scalability Analysis**
   - Current scalability limits
   - Horizontal vs. vertical scaling options
   - Load balancing strategy
   - Database sharding if needed

5. **Quick Wins**
   - Low-effort, high-impact optimizations
   - Configuration changes
   - Simple code refactoring

6. **Long-term Improvements**
   - Architectural changes
   - Infrastructure upgrades
   - Technology stack changes

Include specific code examples and expected performance improvements (e.g., "Expected 40% reduction in response time")."""

        response = await self.generate(
            prompt=prompt,
            system_prompt=self.system_prompt
        )

        return Message(
            type=MessageType.AGENT_RESPONSE,
            sender=self.role,
            content=response,
            metadata={"capability": "performance_analysis"}
        )

    async def _handle_load_testing(self, message: Message) -> Message:
        """Handle load testing strategy requests."""
        prompt = f"""Design comprehensive load testing strategy for:

{message.content}

Provide complete load testing plan:

1. **Test Scenarios**
   - Normal load testing
   - Stress testing (beyond normal capacity)
   - Spike testing (sudden traffic increase)
   - Endurance testing (sustained load)
   - Scalability testing

2. **Test Configuration**
   - Virtual users (concurrent users)
   - Request rates
   - Test duration
   - Ramp-up/ramp-down patterns

3. **Tools and Setup**
   - Recommended tools (JMeter, Locust, k6, Gatling)
   - Test scripts and configuration examples
   - Infrastructure for load testing

4. **Metrics to Monitor**
   - Response time (P50, P95, P99)
   - Throughput (RPS, TPS)
   - Error rates
   - Resource utilization
   - Database performance

5. **Success Criteria**
   - Performance SLAs
   - Acceptable response times
   - Acceptable error rates
   - Resource limits

6. **Analysis and Reporting**
   - How to interpret results
   - Bottleneck identification
   - Scaling recommendations

Include actual test scripts (Locust, k6, etc.) and configuration examples."""

        response = await self.generate(
            prompt=prompt,
            system_prompt=self.system_prompt
        )

        return Message(
            type=MessageType.AGENT_RESPONSE,
            sender=self.role,
            content=response,
            metadata={"capability": "load_testing"}
        )

    async def _handle_caching_strategy(self, message: Message) -> Message:
        """Handle caching strategy design requests."""
        prompt = f"""Design multi-layered caching strategy for:

{message.content}

Provide comprehensive caching architecture:

1. **Cache Layers**
   - Application-level caching (in-memory, Redis)
   - Database query result caching
   - API response caching
   - CDN for static assets
   - Browser caching

2. **Cache Policies**
   - What to cache (data, queries, computations)
   - Cache keys design
   - TTL (Time To Live) for each layer
   - Cache size limits
   - Eviction policies (LRU, LFU, FIFO)

3. **Cache Invalidation**
   - Invalidation strategies
   - Cache-aside vs. write-through
   - Event-driven invalidation
   - Versioning strategy

4. **Implementation Details**
   - Redis configuration examples
   - Code examples for cache implementation
   - Cache warming strategies
   - Monitoring cache hit rates

5. **Performance Impact**
   - Expected cache hit rates
   - Response time improvements
   - Reduced database load

6. **Trade-offs and Considerations**
   - Consistency vs. performance
   - Cache stampede prevention
   - Memory usage
   - Operational complexity

Provide specific configuration and code examples."""

        response = await self.generate(
            prompt=prompt,
            system_prompt=self.system_prompt
        )

        return Message(
            type=MessageType.AGENT_RESPONSE,
            sender=self.role,
            content=response,
            metadata={"capability": "caching_strategy"}
        )

    async def _handle_database_optimization(self, message: Message) -> Message:
        """Handle database optimization requests."""
        prompt = f"""Optimize database performance for:

{message.content}

Provide comprehensive database optimization:

1. **Query Analysis**
   - Identify slow queries
   - EXPLAIN plan analysis
   - Query execution statistics

2. **Query Optimization**
   - Rewrite inefficient queries
   - Reduce JOIN complexity
   - Eliminate N+1 queries
   - Use appropriate query patterns

3. **Index Strategy**
   - Missing index identification
   - Composite index recommendations
   - Index selectivity analysis
   - Covering indexes
   - Index maintenance

4. **Schema Optimization**
   - Table partitioning
   - Denormalization opportunities
   - Data type optimization
   - Archival strategy

5. **Connection and Pooling**
   - Connection pool configuration
   - Connection reuse
   - Statement caching

6. **Caching Layer**
   - Query result caching
   - Application-level caching
   - Materialized views

7. **Read/Write Separation**
   - Read replicas
   - Write vs. read workload distribution
   - Replication lag handling

8. **Monitoring and Maintenance**
   - Performance metrics to track
   - Query performance monitoring
   - Regular maintenance tasks

Provide specific SQL examples, index creation commands, and expected performance improvements."""

        response = await self.generate(
            prompt=prompt,
            system_prompt=self.system_prompt
        )

        return Message(
            type=MessageType.AGENT_RESPONSE,
            sender=self.role,
            content=response,
            metadata={"capability": "database_optimization"}
        )
