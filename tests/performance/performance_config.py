"""
Performance Testing Configuration

Defines test scenarios, load patterns, and performance thresholds.
"""

# ===== Performance Thresholds =====

PERFORMANCE_THRESHOLDS = {
    "api": {
        "p50_response_time": 100,  # ms
        "p95_response_time": 500,  # ms
        "p99_response_time": 1000,  # ms
        "max_error_rate": 1.0,  # %
        "min_throughput": 100,  # requests per second
    },
    "websocket": {
        "max_connection_time": 1000,  # ms
        "mean_message_latency": 50,  # ms
        "p99_message_latency": 200,  # ms
        "max_error_rate": 1.0,  # %
    },
    "database": {
        "max_query_time": 100,  # ms for simple queries
        "max_complex_query_time": 500,  # ms for complex queries
        "max_connection_time": 50,  # ms
    }
}

# ===== Load Test Scenarios =====

LOAD_SCENARIOS = {
    "smoke": {
        "description": "Minimal load to verify system is working",
        "users": 1,
        "spawn_rate": 1,
        "duration": "1m",
    },
    "baseline": {
        "description": "Establish performance baseline",
        "users": 10,
        "spawn_rate": 2,
        "duration": "5m",
    },
    "normal": {
        "description": "Normal expected load",
        "users": 50,
        "spawn_rate": 5,
        "duration": "10m",
    },
    "stress": {
        "description": "High load to find breaking point",
        "users": 100,
        "spawn_rate": 10,
        "duration": "15m",
    },
    "spike": {
        "description": "Sudden traffic spike",
        "users": 200,
        "spawn_rate": 50,
        "duration": "5m",
    },
    "endurance": {
        "description": "Extended duration test",
        "users": 50,
        "spawn_rate": 5,
        "duration": "60m",
    },
}

# ===== API Endpoint Weights =====

# Weight distribution for different API endpoints
# Higher weight = more frequent testing
ENDPOINT_WEIGHTS = {
    "health_check": 10,
    "authentication": 5,
    "projects": 8,
    "files": 6,
    "llm_configs": 4,
    "agent_activities": 3,
    "code_quality": 3,
    "templates": 4,
}

# ===== Test Data Configuration =====

TEST_DATA = {
    "users": {
        "count": 100,
        "username_prefix": "loadtest_user_",
        "email_domain": "test.com",
        "default_password": "TestPassword123!",
    },
    "projects": {
        "count_per_user": 5,
        "name_prefix": "Test Project",
    },
    "files": {
        "count_per_project": 10,
        "types": ["python", "javascript", "typescript", "json", "yaml"],
    },
}

# ===== Report Configuration =====

REPORT_CONFIG = {
    "output_dir": "tests/performance/reports",
    "html_report": True,
    "csv_report": True,
    "json_report": True,
    "charts": True,
}

# ===== Monitoring Configuration =====

MONITORING = {
    "enabled": True,
    "metrics": [
        "response_time",
        "throughput",
        "error_rate",
        "active_users",
        "requests_per_second",
    ],
    "sample_interval": 10,  # seconds
}
