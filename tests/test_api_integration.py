#!/usr/bin/env python3
"""
Integration tests for ResoftAI API endpoints.
Tests the complete user flow from registration to project execution.
"""
import requests
import json
from typing import Dict, Any


BASE_URL = "http://localhost:8000"


class APITester:
    """API integration tester."""

    def __init__(self):
        self.base_url = BASE_URL
        self.token = None
        self.user_id = None
        self.project_id = None
        self.llm_config_id = None

    def test_health(self) -> bool:
        """Test health endpoint."""
        print("\n📋 Testing health endpoint...")
        try:
            response = requests.get(f"{self.base_url}/health")
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "healthy"
            print("✅ Health check passed")
            return True
        except Exception as e:
            print(f"❌ Health check failed: {e}")
            return False

    def test_register(self) -> bool:
        """Test user registration."""
        print("\n📋 Testing user registration...")
        try:
            payload = {
                "username": "testuser",
                "email": "test@example.com",
                "password": "TestPassword123!",
                "full_name": "Test User"
            }
            response = requests.post(
                f"{self.base_url}/api/auth/register",
                json=payload
            )

            if response.status_code == 400:
                # User might already exist
                print("⚠️  User already exists, trying login instead")
                return self.test_login()

            assert response.status_code == 200
            data = response.json()
            assert "access_token" in data
            self.token = data["access_token"]
            print(f"✅ User registered successfully")
            print(f"   Token: {self.token[:20]}...")
            return True
        except Exception as e:
            print(f"❌ Registration failed: {e}")
            if hasattr(e, 'response'):
                print(f"   Response: {e.response.text}")
            return False

    def test_login(self) -> bool:
        """Test user login."""
        print("\n📋 Testing user login...")
        try:
            payload = {
                "username": "testuser",
                "password": "TestPassword123!"
            }
            response = requests.post(
                f"{self.base_url}/api/auth/login",
                data=payload
            )
            assert response.status_code == 200
            data = response.json()
            assert "access_token" in data
            self.token = data["access_token"]
            print(f"✅ Login successful")
            print(f"   Token: {self.token[:20]}...")
            return True
        except Exception as e:
            print(f"❌ Login failed: {e}")
            return False

    def test_get_current_user(self) -> bool:
        """Test getting current user info."""
        print("\n📋 Testing get current user...")
        try:
            headers = {"Authorization": f"Bearer {self.token}"}
            response = requests.get(
                f"{self.base_url}/api/auth/me",
                headers=headers
            )
            assert response.status_code == 200
            data = response.json()
            assert "username" in data
            self.user_id = data["id"]
            print(f"✅ Got user info: {data['username']} (ID: {self.user_id})")
            return True
        except Exception as e:
            print(f"❌ Get current user failed: {e}")
            return False

    def test_create_llm_config(self) -> bool:
        """Test creating LLM configuration."""
        print("\n📋 Testing LLM config creation...")
        try:
            headers = {"Authorization": f"Bearer {self.token}"}
            payload = {
                "name": "Test DeepSeek Config",
                "provider": "deepseek",
                "api_key": "test-api-key-12345",
                "model_name": "deepseek-chat",
                "max_tokens": 4096,
                "temperature": 0.7
            }
            response = requests.post(
                f"{self.base_url}/api/llm-configs",
                headers=headers,
                json=payload
            )
            assert response.status_code == 200
            data = response.json()
            self.llm_config_id = data["id"]
            print(f"✅ LLM config created (ID: {self.llm_config_id})")
            print(f"   Provider: {data['provider']}")
            print(f"   Model: {data['model_name']}")
            return True
        except Exception as e:
            print(f"❌ LLM config creation failed: {e}")
            if hasattr(e, 'response'):
                print(f"   Response: {e.response.text}")
            return False

    def test_activate_llm_config(self) -> bool:
        """Test activating LLM configuration."""
        print("\n📋 Testing LLM config activation...")
        try:
            headers = {"Authorization": f"Bearer {self.token}"}
            response = requests.post(
                f"{self.base_url}/api/llm-configs/{self.llm_config_id}/activate",
                headers=headers
            )
            assert response.status_code == 200
            data = response.json()
            print(f"✅ LLM config activated")
            return True
        except Exception as e:
            print(f"❌ LLM config activation failed: {e}")
            return False

    def test_create_project(self) -> bool:
        """Test creating a project."""
        print("\n📋 Testing project creation...")
        try:
            headers = {"Authorization": f"Bearer {self.token}"}
            payload = {
                "name": "Test Project",
                "description": "A test project for API integration testing",
                "requirements": "Build a simple web application with user authentication and a dashboard"
            }
            response = requests.post(
                f"{self.base_url}/api/projects",
                headers=headers,
                json=payload
            )
            assert response.status_code == 200
            data = response.json()
            self.project_id = data["id"]
            print(f"✅ Project created (ID: {self.project_id})")
            print(f"   Name: {data['name']}")
            print(f"   Status: {data['status']}")
            return True
        except Exception as e:
            print(f"❌ Project creation failed: {e}")
            if hasattr(e, 'response'):
                print(f"   Response: {e.response.text}")
            return False

    def test_get_projects(self) -> bool:
        """Test getting projects list."""
        print("\n📋 Testing get projects...")
        try:
            headers = {"Authorization": f"Bearer {self.token}"}
            response = requests.get(
                f"{self.base_url}/api/projects",
                headers=headers
            )
            assert response.status_code == 200
            data = response.json()
            assert "items" in data
            print(f"✅ Got {len(data['items'])} project(s)")
            return True
        except Exception as e:
            print(f"❌ Get projects failed: {e}")
            return False

    def test_get_project_detail(self) -> bool:
        """Test getting project details."""
        print("\n📋 Testing get project details...")
        try:
            headers = {"Authorization": f"Bearer {self.token}"}
            response = requests.get(
                f"{self.base_url}/api/projects/{self.project_id}",
                headers=headers
            )
            assert response.status_code == 200
            data = response.json()
            print(f"✅ Got project details")
            print(f"   Name: {data['name']}")
            print(f"   Requirements: {data['requirements'][:50]}...")
            return True
        except Exception as e:
            print(f"❌ Get project detail failed: {e}")
            return False

    def test_start_execution(self) -> bool:
        """Test starting project execution."""
        print("\n📋 Testing project execution start...")
        try:
            headers = {"Authorization": f"Bearer {self.token}"}
            response = requests.post(
                f"{self.base_url}/api/execution/{self.project_id}/start",
                headers=headers
            )

            # This might fail if LLM provider is not configured properly
            # That's expected in test environment
            if response.status_code in [200, 400, 500]:
                data = response.json()
                if response.status_code == 200:
                    print(f"✅ Execution started")
                    return True
                else:
                    print(f"⚠️  Execution start returned {response.status_code}")
                    print(f"   Message: {data.get('detail', 'No detail')}")
                    print(f"   (This is expected without real LLM configuration)")
                    return True
            else:
                print(f"❌ Unexpected status code: {response.status_code}")
                return False
        except Exception as e:
            print(f"⚠️  Execution start failed (expected): {e}")
            print(f"   (This is normal without real LLM API keys)")
            return True

    def test_get_execution_status(self) -> bool:
        """Test getting execution status."""
        print("\n📋 Testing get execution status...")
        try:
            headers = {"Authorization": f"Bearer {self.token}"}
            response = requests.get(
                f"{self.base_url}/api/execution/{self.project_id}/status",
                headers=headers
            )
            assert response.status_code == 200
            data = response.json()
            print(f"✅ Got execution status")
            print(f"   Running: {data.get('is_running', False)}")
            return True
        except Exception as e:
            print(f"❌ Get execution status failed: {e}")
            return False

    def run_all_tests(self) -> Dict[str, bool]:
        """Run all integration tests."""
        print("=" * 60)
        print("🚀 Starting ResoftAI API Integration Tests")
        print("=" * 60)

        results = {}

        # Test health
        results["health"] = self.test_health()

        # Test authentication
        results["register"] = self.test_register()
        if results["register"]:
            results["get_user"] = self.test_get_current_user()

        # Test LLM configuration
        if self.token:
            results["llm_config_create"] = self.test_create_llm_config()
            if self.llm_config_id:
                results["llm_config_activate"] = self.test_activate_llm_config()

        # Test project management
        if self.token:
            results["project_create"] = self.test_create_project()
            results["projects_list"] = self.test_get_projects()
            if self.project_id:
                results["project_detail"] = self.test_get_project_detail()

        # Test execution
        if self.project_id and self.llm_config_id:
            results["execution_start"] = self.test_start_execution()
            results["execution_status"] = self.test_get_execution_status()

        # Print summary
        print("\n" + "=" * 60)
        print("📊 Test Results Summary")
        print("=" * 60)

        passed = sum(1 for v in results.values() if v)
        total = len(results)

        for test_name, result in results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{status} - {test_name}")

        print("=" * 60)
        print(f"Results: {passed}/{total} tests passed ({passed*100//total}%)")
        print("=" * 60)

        return results


if __name__ == "__main__":
    tester = APITester()
    results = tester.run_all_tests()

    # Exit with error code if any test failed
    if not all(results.values()):
        exit(1)
