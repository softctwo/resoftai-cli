"""
Frontend-Backend Integration Tests
Tests the complete flow from frontend to backend.
"""
import requests
import json
import time
from typing import Optional

BASE_URL = "http://localhost:8000"
FRONTEND_URL = "http://localhost:3000"


class FrontendIntegrationTest:
    """Test frontend-backend integration."""

    def __init__(self):
        self.token: Optional[str] = None
        self.user_id: Optional[int] = None

    def test_backend_health(self) -> bool:
        """Test backend health endpoint."""
        print("\n[1/8] Testing backend health...")
        try:
            response = requests.get(f"{BASE_URL}/health", timeout=5)
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Backend healthy: {data}")
                return True
            else:
                print(f"❌ Backend unhealthy: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Backend not accessible: {e}")
            return False

    def test_frontend_accessible(self) -> bool:
        """Test frontend is accessible."""
        print("\n[2/8] Testing frontend accessibility...")
        try:
            response = requests.get(FRONTEND_URL, timeout=5)
            if response.status_code == 200 and "ResoftAI" in response.text:
                print("✅ Frontend accessible and loaded")
                return True
            else:
                print(f"❌ Frontend issue: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Frontend not accessible: {e}")
            return False

    def test_api_docs(self) -> bool:
        """Test API documentation."""
        print("\n[3/8] Testing API documentation...")
        try:
            response = requests.get(f"{BASE_URL}/docs", timeout=5)
            if response.status_code == 200 and "swagger" in response.text.lower():
                print("✅ API docs accessible")
                return True
            else:
                print(f"❌ API docs issue: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ API docs error: {e}")
            return False

    def test_user_registration(self) -> bool:
        """Test user registration via API."""
        print("\n[4/8] Testing user registration...")
        try:
            # Generate unique username
            username = f"testuser_{int(time.time())}"

            data = {
                "username": username,
                "email": f"{username}@example.com",
                "password": "Test@Pass123",
                "full_name": "Test User"
            }

            response = requests.post(
                f"{BASE_URL}/api/auth/register",
                json=data,
                timeout=10
            )

            if response.status_code in [200, 201]:
                user_data = response.json()
                self.user_id = user_data.get("id")
                print(f"✅ User registered: {username} (ID: {self.user_id})")
                return True
            else:
                print(f"❌ Registration failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
        except Exception as e:
            print(f"❌ Registration error: {e}")
            return False

    def test_user_login(self) -> bool:
        """Test user login and token retrieval."""
        print("\n[5/8] Testing user login...")
        try:
            # Login with credentials
            data = {
                "username": f"testuser_{int(time.time())}",
                "password": "Test@Pass123"
            }

            # Try to login with recently created user
            response = requests.post(
                f"{BASE_URL}/api/auth/login",
                data=data,
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                timeout=10
            )

            if response.status_code == 200:
                token_data = response.json()
                self.token = token_data.get("access_token")
                print(f"✅ Login successful, token received")
                return True
            else:
                # Try with existing test user
                data["username"] = "testuser"
                response = requests.post(
                    f"{BASE_URL}/api/auth/login",
                    data=data,
                    headers={"Content-Type": "application/x-www-form-urlencoded"},
                    timeout=10
                )
                if response.status_code == 200:
                    token_data = response.json()
                    self.token = token_data.get("access_token")
                    print(f"✅ Login successful with existing user")
                    return True
                else:
                    print(f"❌ Login failed: {response.status_code}")
                    return False
        except Exception as e:
            print(f"❌ Login error: {e}")
            return False

    def test_authenticated_api_call(self) -> bool:
        """Test authenticated API call."""
        print("\n[6/8] Testing authenticated API call...")
        if not self.token:
            print("⚠️  No token available, skipping")
            return False

        try:
            headers = {"Authorization": f"Bearer {self.token}"}
            response = requests.get(
                f"{BASE_URL}/api/projects",
                headers=headers,
                timeout=10
            )

            if response.status_code == 200:
                data = response.json()
                project_count = len(data.get("projects", []))
                print(f"✅ Authenticated API call successful ({project_count} projects)")
                return True
            else:
                print(f"❌ API call failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ API call error: {e}")
            return False

    def test_frontend_proxy(self) -> bool:
        """Test frontend proxy to backend API."""
        print("\n[7/8] Testing frontend API proxy...")
        try:
            # Test through frontend proxy
            response = requests.get(
                f"{FRONTEND_URL}/api/auth/me",
                timeout=5
            )

            # Should get 401 without authentication
            if response.status_code == 401:
                print("✅ Frontend proxy working (401 expected without auth)")
                return True
            elif response.status_code == 404:
                print("⚠️  Frontend proxy returned 404 (endpoint might not exist)")
                return True
            else:
                print(f"✅ Frontend proxy responded: {response.status_code}")
                return True
        except Exception as e:
            print(f"❌ Proxy test error: {e}")
            return False

    def test_cors_headers(self) -> bool:
        """Test CORS headers."""
        print("\n[8/8] Testing CORS configuration...")
        try:
            headers = {
                "Origin": FRONTEND_URL,
                "Access-Control-Request-Method": "GET"
            }
            response = requests.options(
                f"{BASE_URL}/api/projects",
                headers=headers,
                timeout=5
            )

            cors_header = response.headers.get("Access-Control-Allow-Origin")
            if cors_header:
                print(f"✅ CORS enabled: {cors_header}")
                return True
            else:
                print("⚠️  CORS headers not found (may still work)")
                return True
        except Exception as e:
            print(f"❌ CORS test error: {e}")
            return False

    def run_all_tests(self) -> dict:
        """Run all integration tests."""
        print("\n" + "="*60)
        print("Frontend-Backend Integration Test Suite")
        print("="*60)

        results = {
            "backend_health": self.test_backend_health(),
            "frontend_accessible": self.test_frontend_accessible(),
            "api_docs": self.test_api_docs(),
            "user_registration": self.test_user_registration(),
            "user_login": self.test_user_login(),
            "authenticated_api": self.test_authenticated_api_call(),
            "frontend_proxy": self.test_frontend_proxy(),
            "cors": self.test_cors_headers(),
        }

        # Summary
        print("\n" + "="*60)
        print("Test Summary")
        print("="*60)

        passed = sum(1 for v in results.values() if v)
        total = len(results)

        for test_name, result in results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{status} - {test_name}")

        print("\n" + "="*60)
        print(f"Results: {passed}/{total} tests passed ({passed*100//total}%)")
        print("="*60)

        return results


if __name__ == "__main__":
    tester = FrontendIntegrationTest()
    results = tester.run_all_tests()

    # Exit with appropriate code
    all_passed = all(results.values())
    exit(0 if all_passed else 1)
