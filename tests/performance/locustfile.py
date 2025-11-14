"""
Performance tests using Locust

Run with:
    locust -f tests/performance/locustfile.py --host=http://localhost:8000
"""
from locust import HttpUser, task, between
import random
import json


class ResoftAIUser(HttpUser):
    """
    Simulates a ResoftAI API user
    
    Tests common API endpoints under load.
    """
    wait_time = between(1, 3)  # Wait 1-3 seconds between requests
    
    def on_start(self):
        """Login and obtain JWT token"""
        response = self.client.post("/api/auth/login", json={
            "username": "testuser",
            "password": "testpass"
        })
        
        if response.status_code == 200:
            self.token = response.json().get("access_token")
            self.headers = {"Authorization": f"Bearer {self.token}"}
        else:
            self.token = None
            self.headers = {}
    
    @task(3)
    def list_projects(self):
        """List projects - weight 3 (most common)"""
        self.client.get("/api/projects", headers=self.headers)
    
    @task(2)
    def get_health(self):
        """Health check - weight 2"""
        self.client.get("/health")
    
    @task(1)
    def create_project(self):
        """Create project - weight 1 (less common)"""
        project_data = {
            "name": f"Test Project {random.randint(1, 10000)}",
            "requirements": "Build a simple REST API",
            "llm_provider": "deepseek"
        }
        self.client.post("/api/projects", json=project_data, headers=self.headers)
    
    @task(2)
    def browse_marketplace(self):
        """Browse plugin marketplace - weight 2"""
        self.client.get("/api/plugins/marketplace?limit=20")
    
    @task(1)
    def search_plugins(self):
        """Search plugins - weight 1"""
        search_terms = ["security", "quality", "integration", "llm"]
        term = random.choice(search_terms)
        self.client.get(f"/api/plugins/marketplace/search?q={term}")


class AdminUser(HttpUser):
    """
    Simulates an admin user with elevated privileges
    """
    wait_time = between(2, 5)
    
    def on_start(self):
        """Login as admin"""
        response = self.client.post("/api/auth/login", json={
            "username": "admin",
            "password": "adminpass"
        })
        
        if response.status_code == 200:
            self.token = response.json().get("access_token")
            self.headers = {"Authorization": f"Bearer {self.token}"}
        else:
            self.token = None
            self.headers = {}
    
    @task(2)
    def list_organizations(self):
        """List organizations"""
        self.client.get("/api/organizations", headers=self.headers)
    
    @task(1)
    def create_organization(self):
        """Create organization"""
        org_data = {
            "name": f"Test Org {random.randint(1, 1000)}",
            "slug": f"test-org-{random.randint(1, 1000)}",
            "tier": "free"
        }
        self.client.post("/api/organizations", json=org_data, headers=self.headers)
    
    @task(1)
    def list_teams(self):
        """List teams"""
        self.client.get("/api/teams", headers=self.headers)
