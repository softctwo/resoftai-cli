"""Load testing for ResoftAI WebSocket collaborative editing.

Run with:
    locust -f tests/load/locustfile.py --host=http://localhost:8000
"""
import json
import random
from locust import HttpUser, task, between, events
from locust.contrib.fasthttp import FastHttpUser
import socketio


class WebSocketClient:
    """WebSocket client for load testing."""

    def __init__(self, base_url: str):
        """Initialize WebSocket client."""
        self.base_url = base_url.replace('http://', 'ws://').replace('https://', 'wss://')
        self.sio = socketio.Client()
        self.connected = False
        self.setup_handlers()

    def setup_handlers(self):
        """Setup Socket.IO event handlers."""
        @self.sio.event
        def connect():
            self.connected = True

        @self.sio.event
        def disconnect():
            self.connected = False

        @self.sio.on('file.joined')
        def on_file_joined(data):
            pass

        @self.sio.on('file.edit')
        def on_file_edit(data):
            pass

        @self.sio.on('cursor.position')
        def on_cursor_position(data):
            pass

    def connect(self):
        """Connect to WebSocket server."""
        try:
            self.sio.connect(self.base_url, transports=['websocket'])
            return True
        except Exception as e:
            print(f"Connection error: {e}")
            return False

    def disconnect(self):
        """Disconnect from WebSocket server."""
        if self.connected:
            self.sio.disconnect()

    def join_file_session(self, file_id: int, project_id: int, user_id: int, username: str):
        """Join file editing session."""
        self.sio.emit('join_file_session', {
            'file_id': file_id,
            'project_id': project_id,
            'user_id': user_id,
            'username': username
        })

    def send_file_edit(self, file_id: int, changes: dict):
        """Send file edit."""
        self.sio.emit('file_edit', {
            'file_id': file_id,
            'changes': changes
        })

    def send_cursor_position(self, file_id: int, position: dict, selection: dict = None):
        """Send cursor position."""
        self.sio.emit('cursor_position', {
            'file_id': file_id,
            'position': position,
            'selection': selection
        })


class ResoftAIUser(FastHttpUser):
    """Simulated user for load testing."""

    wait_time = between(1, 3)  # Wait 1-3 seconds between tasks

    def on_start(self):
        """Initialize on user start."""
        # Login (you may need to adjust this based on your auth)
        self.user_id = random.randint(1, 1000)
        self.username = f"LoadTestUser{self.user_id}"
        self.project_id = 1
        self.file_id = random.randint(1, 10)

        # Connect WebSocket
        self.ws_client = WebSocketClient(self.host)
        self.ws_connected = self.ws_client.connect()

        if self.ws_connected:
            self.ws_client.join_file_session(
                self.file_id,
                self.project_id,
                self.user_id,
                self.username
            )

    def on_stop(self):
        """Cleanup on user stop."""
        if hasattr(self, 'ws_client'):
            self.ws_client.disconnect()

    @task(3)
    def send_edit(self):
        """Simulate file editing."""
        if not self.ws_connected:
            return

        changes = {
            'range': {
                'startLineNumber': random.randint(1, 100),
                'startColumn': 1,
                'endLineNumber': random.randint(1, 100),
                'endColumn': 10
            },
            'text': f'Sample code from {self.username}'
        }

        self.ws_client.send_file_edit(self.file_id, changes)

    @task(5)
    def send_cursor_update(self):
        """Simulate cursor movement."""
        if not self.ws_connected:
            return

        position = {
            'lineNumber': random.randint(1, 100),
            'column': random.randint(1, 80)
        }

        self.ws_client.send_cursor_position(self.file_id, position)

    @task(1)
    def get_performance_metrics(self):
        """Get performance metrics via API."""
        with self.client.get(
            "/api/performance/metrics",
            catch_response=True,
            name="/api/performance/metrics"
        ) as response:
            if response.status_code == 200:
                response.success()
            elif response.status_code == 401:
                # Expected if not authenticated
                response.success()
            else:
                response.failure(f"Got status code {response.status_code}")

    @task(1)
    def get_websocket_metrics(self):
        """Get WebSocket metrics via API."""
        with self.client.get(
            "/api/performance/websocket",
            catch_response=True,
            name="/api/performance/websocket"
        ) as response:
            if response.status_code in [200, 401]:
                response.success()
            else:
                response.failure(f"Got status code {response.status_code}")


class APIOnlyUser(FastHttpUser):
    """User that only tests HTTP API endpoints."""

    wait_time = between(0.5, 2)

    @task(5)
    def health_check(self):
        """Test health endpoint."""
        self.client.get("/health", name="/health")

    @task(3)
    def get_metrics(self):
        """Test performance metrics endpoint."""
        with self.client.get(
            "/api/performance/health",
            catch_response=True,
            name="/api/performance/health"
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Got status code {response.status_code}")

    @task(2)
    def root_endpoint(self):
        """Test root endpoint."""
        self.client.get("/", name="/")


# Event handlers for custom statistics
@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    """Called when test starts."""
    print("Load test starting...")


@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    """Called when test stops."""
    print("Load test completed!")
    print(f"Total requests: {environment.stats.total.num_requests}")
    print(f"Total failures: {environment.stats.total.num_failures}")
    print(f"Average response time: {environment.stats.total.avg_response_time:.2f}ms")
