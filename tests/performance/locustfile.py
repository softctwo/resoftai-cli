"""
ResoftAI API Performance Testing with Locust

This file contains performance tests for the ResoftAI API endpoints.
Run with: locust -f locustfile.py --host=http://localhost:8000
"""

import random
import json
from locust import HttpUser, task, between, events
from locust.exception import RescheduleTask


class ResoftAIUser(HttpUser):
    """Simulates a ResoftAI user performing various API operations."""

    # Wait time between tasks (1-3 seconds)
    wait_time = between(1, 3)

    # Store tokens and user data
    token = None
    user_id = None
    project_ids = []
    llm_config_id = None

    def on_start(self):
        """Called when a simulated user starts."""
        # Register and login
        self.register_and_login()

    def register_and_login(self):
        """Register a new user and login to get token."""
        # Generate unique username
        username = f"loadtest_user_{random.randint(10000, 99999)}"
        email = f"{username}@test.com"
        password = "TestPassword123!"

        # Register
        register_response = self.client.post("/api/auth/register", json={
            "username": username,
            "email": email,
            "password": password,
            "full_name": "Load Test User"
        }, name="/api/auth/register")

        if register_response.status_code == 201:
            # Login
            login_response = self.client.post("/api/auth/login", data={
                "username": username,
                "password": password
            }, name="/api/auth/login")

            if login_response.status_code == 200:
                data = login_response.json()
                self.token = data.get("access_token")
                self.user_id = data.get("user", {}).get("id")
                # Update headers for all subsequent requests
                self.client.headers.update({
                    "Authorization": f"Bearer {self.token}"
                })
            else:
                print(f"Login failed: {login_response.status_code}")
                raise RescheduleTask()
        else:
            print(f"Registration failed: {register_response.status_code}")
            raise RescheduleTask()

    def on_stop(self):
        """Called when a simulated user stops."""
        # Logout
        if self.token:
            self.client.post("/api/auth/logout", name="/api/auth/logout")

    # ===== Health Check Tasks =====

    @task(10)
    def health_check(self):
        """Test health check endpoint (high frequency)."""
        self.client.get("/health", name="/health")

    # ===== Authentication Tasks =====

    @task(5)
    def get_current_user(self):
        """Test getting current user info."""
        if not self.token:
            return
        self.client.get("/api/auth/me", name="/api/auth/me")

    @task(2)
    def refresh_token(self):
        """Test token refresh."""
        if not self.token:
            return
        self.client.post("/api/auth/refresh", name="/api/auth/refresh")

    # ===== Project Tasks =====

    @task(8)
    def list_projects(self):
        """Test listing projects."""
        if not self.token:
            return
        self.client.get("/api/projects", name="/api/projects (list)")

    @task(5)
    def create_project(self):
        """Test creating a new project."""
        if not self.token:
            return

        project_data = {
            "name": f"Test Project {random.randint(1000, 9999)}",
            "description": "Performance test project",
            "requirements": "Test requirements for load testing"
        }

        response = self.client.post(
            "/api/projects",
            json=project_data,
            name="/api/projects (create)"
        )

        if response.status_code == 201:
            project_id = response.json().get("id")
            if project_id:
                self.project_ids.append(project_id)

    @task(6)
    def get_project_detail(self):
        """Test getting project details."""
        if not self.token or not self.project_ids:
            return

        project_id = random.choice(self.project_ids)
        self.client.get(
            f"/api/projects/{project_id}",
            name="/api/projects/{id} (get)"
        )

    @task(3)
    def update_project(self):
        """Test updating a project."""
        if not self.token or not self.project_ids:
            return

        project_id = random.choice(self.project_ids)
        update_data = {
            "description": f"Updated at {random.randint(1000, 9999)}",
            "status": random.choice(["planning", "in_progress", "completed"])
        }

        self.client.put(
            f"/api/projects/{project_id}",
            json=update_data,
            name="/api/projects/{id} (update)"
        )

    # ===== LLM Config Tasks =====

    @task(4)
    def list_llm_configs(self):
        """Test listing LLM configurations."""
        if not self.token:
            return
        self.client.get("/api/llm-configs", name="/api/llm-configs (list)")

    @task(2)
    def create_llm_config(self):
        """Test creating LLM configuration."""
        if not self.token:
            return

        config_data = {
            "name": f"Test Config {random.randint(1000, 9999)}",
            "provider": random.choice(["deepseek", "anthropic", "openai"]),
            "api_key": "test-api-key-for-load-testing",
            "model_name": "test-model",
            "max_tokens": 4096,
            "temperature": 0.7
        }

        response = self.client.post(
            "/api/llm-configs",
            json=config_data,
            name="/api/llm-configs (create)"
        )

        if response.status_code == 201:
            config_id = response.json().get("id")
            if config_id:
                self.llm_config_id = config_id

    @task(2)
    def get_active_llm_config(self):
        """Test getting active LLM configuration."""
        if not self.token:
            return
        self.client.get(
            "/api/llm-configs/active",
            name="/api/llm-configs/active"
        )

    # ===== File Management Tasks =====

    @task(4)
    def list_files(self):
        """Test listing files."""
        if not self.token or not self.project_ids:
            return

        project_id = random.choice(self.project_ids)
        self.client.get(
            f"/api/files?project_id={project_id}",
            name="/api/files (list)"
        )

    @task(2)
    def create_file(self):
        """Test creating a file."""
        if not self.token or not self.project_ids:
            return

        project_id = random.choice(self.project_ids)
        file_data = {
            "project_id": project_id,
            "filename": f"test_{random.randint(1000, 9999)}.py",
            "file_path": f"/test/file_{random.randint(1000, 9999)}.py",
            "content": "# Test file content\nprint('Hello World')\n",
            "file_type": "python"
        }

        self.client.post(
            "/api/files",
            json=file_data,
            name="/api/files (create)"
        )

    # ===== Agent Activity Tasks =====

    @task(3)
    def list_agent_activities(self):
        """Test listing agent activities."""
        if not self.token:
            return
        self.client.get(
            "/api/agent-activities",
            name="/api/agent-activities (list)"
        )

    @task(2)
    def list_active_agents(self):
        """Test listing active agents."""
        if not self.token:
            return
        self.client.get(
            "/api/agent-activities/active",
            name="/api/agent-activities/active"
        )

    # ===== Code Quality Tasks =====

    @task(3)
    def check_code_quality(self):
        """Test code quality check endpoint."""
        if not self.token:
            return

        code_sample = """
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

print(fibonacci(10))
"""

        quality_data = {
            "code": code_sample,
            "language": "python",
            "filename": "test.py"
        }

        self.client.post(
            "/api/code-quality/check",
            json=quality_data,
            name="/api/code-quality/check"
        )

    @task(2)
    def get_supported_linters(self):
        """Test getting supported linters."""
        if not self.token:
            return
        self.client.get(
            "/api/code-quality/linters",
            name="/api/code-quality/linters"
        )

    @task(1)
    def get_code_quality_health(self):
        """Test code quality health check."""
        if not self.token:
            return
        self.client.get(
            "/api/code-quality/health",
            name="/api/code-quality/health"
        )

    # ===== Template Tasks =====

    @task(4)
    def list_templates(self):
        """Test listing templates."""
        if not self.token:
            return
        self.client.get(
            "/api/v1/templates",
            name="/api/v1/templates (list)"
        )

    @task(2)
    def get_template_detail(self):
        """Test getting template details."""
        if not self.token:
            return

        # Test with known template IDs
        template_ids = [
            "fastapi-rest-api",
            "microservice-architecture",
            "data-pipeline-airflow",
            "ml-project"
        ]

        template_id = random.choice(template_ids)
        self.client.get(
            f"/api/v1/templates/{template_id}",
            name="/api/v1/templates/{id} (get)"
        )

    @task(1)
    def get_template_preview(self):
        """Test getting template preview."""
        if not self.token:
            return

        template_ids = ["fastapi-rest-api", "microservice-architecture"]
        template_id = random.choice(template_ids)

        self.client.get(
            f"/api/v1/templates/{template_id}/preview",
            name="/api/v1/templates/{id}/preview"
        )


# ===== Event Handlers for Metrics =====

@events.init.add_listener
def on_locust_init(environment, **kwargs):
    """Called when Locust is initialized."""
    print("=" * 60)
    print("ResoftAI Performance Testing")
    print("=" * 60)


@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    """Called when the load test starts."""
    print(f"\n🚀 Starting load test against: {environment.host}")
    print(f"📊 Target metrics:")
    print(f"   - API P50 < 100ms")
    print(f"   - API P95 < 500ms")
    print(f"   - API P99 < 1000ms")
    print(f"   - Error rate < 1%")
    print()


@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    """Called when the load test stops."""
    print("\n" + "=" * 60)
    print("✅ Load test completed!")
    print("=" * 60)
    print("\n📈 Review results in Locust web UI or reports")
