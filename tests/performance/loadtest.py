"""
ResoftAI Load Testing Suite using Locust

This script performs comprehensive load testing of the ResoftAI platform.

Usage:
    # Run with web UI
    locust -f tests/performance/loadtest.py --host=https://yourdomain.com

    # Run headless
    locust -f tests/performance/loadtest.py --host=https://yourdomain.com \\
           --users 100 --spawn-rate 10 --run-time 10m --headless

    # Run with specific test class
    locust -f tests/performance/loadtest.py APILoadTest --host=https://yourdomain.com

Requirements:
    pip install locust faker
"""

import json
import random
from locust import HttpUser, task, between, TaskSet
from faker import Faker

fake = Faker()


class AuthTasks(TaskSet):
    """Authentication related tasks"""

    def on_start(self):
        """Called when a user starts - login"""
        self.login()

    def login(self):
        """Login and get access token"""
        response = self.client.post("/api/v1/auth/login", json={
            "username": "testuser",
            "password": "testpass123"
        })

        if response.status_code == 200:
            data = response.json()
            self.user.token = data.get("access_token")
            self.user.headers = {"Authorization": f"Bearer {self.user.token}"}
        else:
            # Create test user if login fails
            self.register()
            self.login()

    def register(self):
        """Register a new user"""
        username = fake.user_name()
        self.client.post("/api/v1/auth/register", json={
            "username": username,
            "email": fake.email(),
            "password": "testpass123"
        })

    @task(2)
    def get_current_user(self):
        """Get current user information"""
        self.client.get("/api/v1/auth/me", headers=self.user.headers)

    @task(1)
    def refresh_token(self):
        """Refresh access token"""
        if hasattr(self.user, 'token'):
            self.client.post("/api/v1/auth/refresh", json={
                "refresh_token": self.user.token
            })


class ProjectTasks(TaskSet):
    """Project management tasks"""

    def on_start(self):
        """Setup - ensure user is authenticated"""
        if not hasattr(self.user, 'headers'):
            self.user.headers = {"Authorization": "Bearer test-token"}
        self.project_ids = []

    @task(5)
    def list_projects(self):
        """List all projects"""
        response = self.client.get("/api/v1/projects", headers=self.user.headers)
        if response.status_code == 200:
            projects = response.json()
            if projects:
                self.project_ids = [p['id'] for p in projects[:10]]

    @task(3)
    def create_project(self):
        """Create a new project"""
        response = self.client.post("/api/v1/projects", headers=self.user.headers, json={
            "name": f"LoadTest {fake.company()}",
            "description": fake.text(max_nb_chars=200),
            "requirements": fake.text(max_nb_chars=500),
            "language": random.choice(["python", "javascript", "java", "go"]),
            "framework": random.choice(["fastapi", "express", "spring", "gin"])
        })

        if response.status_code == 201:
            project = response.json()
            self.project_ids.append(project['id'])

    @task(4)
    def get_project(self):
        """Get project details"""
        if self.project_ids:
            project_id = random.choice(self.project_ids)
            self.client.get(f"/api/v1/projects/{project_id}", headers=self.user.headers)

    @task(2)
    def update_project(self):
        """Update project"""
        if self.project_ids:
            project_id = random.choice(self.project_ids)
            self.client.put(f"/api/v1/projects/{project_id}", headers=self.user.headers, json={
                "description": fake.text(max_nb_chars=200)
            })

    @task(1)
    def delete_project(self):
        """Delete project"""
        if len(self.project_ids) > 5:  # Keep at least 5 projects
            project_id = self.project_ids.pop()
            self.client.delete(f"/api/v1/projects/{project_id}", headers=self.user.headers)


class PluginTasks(TaskSet):
    """Plugin marketplace tasks"""

    def on_start(self):
        if not hasattr(self.user, 'headers'):
            self.user.headers = {"Authorization": "Bearer test-token"}

    @task(10)
    def list_plugins(self):
        """List available plugins"""
        self.client.get("/api/v1/plugins/marketplace", headers=self.user.headers)

    @task(5)
    def search_plugins(self):
        """Search plugins"""
        query = random.choice(["test", "code", "quality", "security", "deploy"])
        self.client.get(f"/api/v1/plugins/marketplace/search?q={query}", headers=self.user.headers)

    @task(3)
    def get_plugin_details(self):
        """Get plugin details"""
        slug = random.choice(["pytest-plugin", "eslint-plugin", "security-scanner"])
        self.client.get(f"/api/v1/plugins/marketplace/{slug}", headers=self.user.headers)

    @task(2)
    def get_installed_plugins(self):
        """Get installed plugins"""
        self.client.get("/api/v1/plugins/installed", headers=self.user.headers)


class OrganizationTasks(TaskSet):
    """Enterprise organization tasks"""

    def on_start(self):
        if not hasattr(self.user, 'headers'):
            self.user.headers = {"Authorization": "Bearer test-token"}
        self.org_ids = []

    @task(5)
    def list_organizations(self):
        """List organizations"""
        response = self.client.get("/api/v1/organizations", headers=self.user.headers)
        if response.status_code == 200:
            orgs = response.json()
            if orgs:
                self.org_ids = [o['id'] for o in orgs[:5]]

    @task(2)
    def create_organization(self):
        """Create organization"""
        response = self.client.post("/api/v1/organizations", headers=self.user.headers, json={
            "name": fake.company(),
            "description": fake.text(max_nb_chars=200),
            "tier": random.choice(["FREE", "STARTER", "PROFESSIONAL"])
        })

        if response.status_code == 201:
            org = response.json()
            self.org_ids.append(org['id'])

    @task(3)
    def get_organization(self):
        """Get organization details"""
        if self.org_ids:
            org_id = random.choice(self.org_ids)
            self.client.get(f"/api/v1/organizations/{org_id}", headers=self.user.headers)

    @task(2)
    def get_org_quotas(self):
        """Get organization quotas"""
        if self.org_ids:
            org_id = random.choice(self.org_ids)
            self.client.get(f"/api/v1/organizations/{org_id}/quotas", headers=self.user.headers)


class PerformanceMonitoringTasks(TaskSet):
    """Performance monitoring tasks"""

    def on_start(self):
        if not hasattr(self.user, 'headers'):
            self.user.headers = {"Authorization": "Bearer test-token"}

    @task(5)
    def get_system_metrics(self):
        """Get system performance metrics"""
        self.client.get("/api/v1/performance/metrics", headers=self.user.headers)

    @task(3)
    def get_agent_performance(self):
        """Get agent performance metrics"""
        self.client.get("/api/v1/performance/agents", headers=self.user.headers)

    @task(2)
    def get_llm_performance(self):
        """Get LLM performance metrics"""
        self.client.get("/api/v1/performance/llm", headers=self.user.headers)


class ResoftAIUser(HttpUser):
    """Base user class for ResoftAI load testing"""

    wait_time = between(1, 3)  # Wait 1-3 seconds between tasks
    tasks = [
        ProjectTasks,
        PluginTasks,
        OrganizationTasks,
        PerformanceMonitoringTasks
    ]

    def on_start(self):
        """Called when a user starts"""
        self.token = None
        self.headers = {}
        self.login()

    def login(self):
        """Authenticate user"""
        response = self.client.post("/api/v1/auth/login", json={
            "username": "loadtest",
            "password": "loadtest123"
        })

        if response.status_code == 200:
            data = response.json()
            self.token = data.get("access_token")
            self.headers = {"Authorization": f"Bearer {self.token}"}


class APILoadTest(HttpUser):
    """Focused API endpoint load testing"""

    wait_time = between(0.5, 2)

    def on_start(self):
        self.token = "test-token"
        self.headers = {"Authorization": f"Bearer {self.token}"}

    @task(10)
    def health_check(self):
        """Health check endpoint"""
        self.client.get("/api/v1/health")

    @task(8)
    def list_projects(self):
        """List projects"""
        self.client.get("/api/v1/projects", headers=self.headers)

    @task(6)
    def list_plugins(self):
        """List plugins"""
        self.client.get("/api/v1/plugins/marketplace", headers=self.headers)

    @task(4)
    def get_metrics(self):
        """Get performance metrics"""
        self.client.get("/api/v1/performance/metrics", headers=self.headers)

    @task(2)
    def search_plugins(self):
        """Search plugins"""
        query = random.choice(["test", "code", "deploy", "quality"])
        self.client.get(f"/api/v1/plugins/marketplace/search?q={query}", headers=self.headers)


class StressTest(HttpUser):
    """Stress testing with high concurrency"""

    wait_time = between(0.1, 0.5)  # Very short wait time

    def on_start(self):
        self.headers = {"Authorization": "Bearer test-token"}

    @task(20)
    def rapid_list_requests(self):
        """Rapid fire list requests"""
        endpoint = random.choice([
            "/api/v1/projects",
            "/api/v1/plugins/marketplace",
            "/api/v1/organizations"
        ])
        self.client.get(endpoint, headers=self.headers)

    @task(10)
    def rapid_search_requests(self):
        """Rapid search requests"""
        query = random.choice(["test", "code", "api", "plugin"])
        self.client.get(f"/api/v1/plugins/marketplace/search?q={query}", headers=self.headers)

    @task(5)
    def rapid_detail_requests(self):
        """Rapid detail requests"""
        self.client.get("/api/v1/performance/metrics", headers=self.headers)


class RealisticUserBehavior(HttpUser):
    """Simulates realistic user behavior patterns"""

    wait_time = between(2, 10)  # More realistic wait times

    def on_start(self):
        self.login()

    def login(self):
        """Login"""
        response = self.client.post("/api/v1/auth/login", json={
            "username": "realistic_user",
            "password": "password123"
        })
        if response.status_code == 200:
            data = response.json()
            self.headers = {"Authorization": f"Bearer {data.get('access_token')}"}
        else:
            self.headers = {"Authorization": "Bearer test-token"}

    @task
    def browse_dashboard(self):
        """User browses dashboard"""
        self.client.get("/api/v1/projects", headers=self.headers)
        self.wait()
        self.client.get("/api/v1/performance/metrics", headers=self.headers)

    @task
    def explore_plugins(self):
        """User explores plugin marketplace"""
        # List plugins
        self.client.get("/api/v1/plugins/marketplace", headers=self.headers)
        self.wait()

        # Search for specific plugin
        query = random.choice(["test", "deploy", "quality"])
        self.client.get(f"/api/v1/plugins/marketplace/search?q={query}", headers=self.headers)
        self.wait()

        # View plugin details
        slug = random.choice(["pytest-plugin", "eslint-plugin"])
        self.client.get(f"/api/v1/plugins/marketplace/{slug}", headers=self.headers)

    @task
    def manage_project(self):
        """User manages a project"""
        # Create project
        response = self.client.post("/api/v1/projects", headers=self.headers, json={
            "name": f"Project {fake.word()}",
            "description": fake.text(max_nb_chars=200),
            "requirements": fake.text(max_nb_chars=500)
        })

        if response.status_code == 201:
            project = response.json()
            project_id = project['id']

            self.wait()

            # View project
            self.client.get(f"/api/v1/projects/{project_id}", headers=self.headers)

            self.wait()

            # Update project
            self.client.put(f"/api/v1/projects/{project_id}", headers=self.headers, json={
                "description": fake.text(max_nb_chars=150)
            })

    def wait(self):
        """Custom wait function for realistic pauses"""
        import time
        time.sleep(random.uniform(1, 3))


# Custom event handlers for reporting

from locust import events

@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    """Called when test starts"""
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("  ResoftAI Load Testing Started")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")


@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    """Called when test stops"""
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("  ResoftAI Load Testing Completed")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
