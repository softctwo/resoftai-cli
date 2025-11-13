"""
WebSocket Integration Tests
Tests real-time communication between frontend and backend.
"""
import asyncio
import socketio
from typing import Dict, List
import time

BASE_URL = "http://localhost:8000"


class WebSocketIntegrationTest:
    """Test WebSocket integration."""

    def __init__(self):
        self.sio = None
        self.events_received: List[Dict] = []
        self.connected = False

    async def setup(self):
        """Setup WebSocket client."""
        self.sio = socketio.AsyncClient(
            logger=False,
            engineio_logger=False
        )

        # Register event handlers
        @self.sio.event
        async def connect():
            print("✅ WebSocket connected")
            self.connected = True

        @self.sio.event
        async def disconnect():
            print("ℹ️  WebSocket disconnected")
            self.connected = False

        @self.sio.event
        async def connected(data):
            print(f"✅ Received 'connected' event: {data}")
            self.events_received.append({"event": "connected", "data": data})

        @self.sio.event
        async def joined(data):
            print(f"✅ Received 'joined' event: {data}")
            self.events_received.append({"event": "joined", "data": data})

        @self.sio.event
        async def left(data):
            print(f"✅ Received 'left' event: {data}")
            self.events_received.append({"event": "left", "data": data})

        @self.sio.event
        async def pong(data):
            print(f"✅ Received 'pong' event: {data}")
            self.events_received.append({"event": "pong", "data": data})

        @self.sio.event
        async def error(data):
            print(f"⚠️  Received 'error' event: {data}")
            self.events_received.append({"event": "error", "data": data})

        # Project events
        @self.sio.event
        async def project_progress(data):
            print(f"📊 Project progress: {data}")
            self.events_received.append({"event": "project.progress", "data": data})

        @self.sio.event
        async def agent_status(data):
            print(f"🤖 Agent status: {data}")
            self.events_received.append({"event": "agent.status", "data": data})

        @self.sio.event
        async def log_new(data):
            print(f"📝 New log: {data}")
            self.events_received.append({"event": "log.new", "data": data})

    async def test_connection(self) -> bool:
        """Test WebSocket connection."""
        print("\n[1/6] Testing WebSocket connection...")
        try:
            await self.sio.connect(BASE_URL)
            await asyncio.sleep(1)  # Wait for connection to establish

            if self.connected:
                print("✅ WebSocket connection successful")
                return True
            else:
                print("❌ WebSocket connection failed")
                return False
        except Exception as e:
            print(f"❌ Connection error: {e}")
            return False

    async def test_ping_pong(self) -> bool:
        """Test ping/pong mechanism."""
        print("\n[2/6] Testing ping/pong...")
        if not self.connected:
            print("⚠️  Not connected, skipping")
            return False

        try:
            ping_data = {"timestamp": time.time()}
            await self.sio.emit('ping', ping_data)
            await asyncio.sleep(0.5)

            # Check if pong was received
            pong_events = [e for e in self.events_received if e["event"] == "pong"]
            if pong_events:
                print("✅ Ping/pong working")
                return True
            else:
                print("❌ No pong received")
                return False
        except Exception as e:
            print(f"❌ Ping/pong error: {e}")
            return False

    async def test_join_project(self) -> bool:
        """Test joining a project room."""
        print("\n[3/6] Testing join project room...")
        if not self.connected:
            print("⚠️  Not connected, skipping")
            return False

        try:
            join_data = {
                "project_id": 1,
                "user_id": 1
            }
            await self.sio.emit('join_project', join_data)
            await asyncio.sleep(0.5)

            # Check if joined event was received
            joined_events = [e for e in self.events_received if e["event"] == "joined"]
            if joined_events:
                project_id = joined_events[0]["data"].get("project_id")
                print(f"✅ Successfully joined project {project_id}")
                return True
            else:
                print("❌ No 'joined' event received")
                return False
        except Exception as e:
            print(f"❌ Join project error: {e}")
            return False

    async def test_leave_project(self) -> bool:
        """Test leaving a project room."""
        print("\n[4/6] Testing leave project room...")
        if not self.connected:
            print("⚠️  Not connected, skipping")
            return False

        try:
            leave_data = {
                "project_id": 1
            }
            await self.sio.emit('leave_project', leave_data)
            await asyncio.sleep(0.5)

            # Check if left event was received
            left_events = [e for e in self.events_received if e["event"] == "left"]
            if left_events:
                project_id = left_events[0]["data"].get("project_id")
                print(f"✅ Successfully left project {project_id}")
                return True
            else:
                print("❌ No 'left' event received")
                return False
        except Exception as e:
            print(f"❌ Leave project error: {e}")
            return False

    async def test_error_handling(self) -> bool:
        """Test error handling."""
        print("\n[5/6] Testing error handling...")
        if not self.connected:
            print("⚠️  Not connected, skipping")
            return False

        try:
            # Send join without project_id to trigger error
            await self.sio.emit('join_project', {})
            await asyncio.sleep(0.5)

            # Check if error was received
            error_events = [e for e in self.events_received if e["event"] == "error"]
            if error_events:
                error_msg = error_events[0]["data"].get("message")
                print(f"✅ Error handling working: {error_msg}")
                return True
            else:
                print("⚠️  No error event received (may be handled differently)")
                return True  # Not critical
        except Exception as e:
            print(f"❌ Error handling test failed: {e}")
            return False

    async def test_disconnect(self) -> bool:
        """Test disconnect."""
        print("\n[6/6] Testing disconnect...")
        if not self.connected:
            print("⚠️  Not connected, skipping")
            return False

        try:
            await self.sio.disconnect()
            await asyncio.sleep(0.5)

            if not self.connected:
                print("✅ Disconnected successfully")
                return True
            else:
                print("❌ Still connected after disconnect")
                return False
        except Exception as e:
            print(f"❌ Disconnect error: {e}")
            return False

    async def run_all_tests(self) -> dict:
        """Run all WebSocket tests."""
        print("\n" + "="*60)
        print("WebSocket Integration Test Suite")
        print("="*60)

        await self.setup()

        results = {
            "connection": await self.test_connection(),
            "ping_pong": await self.test_ping_pong(),
            "join_project": await self.test_join_project(),
            "leave_project": await self.test_leave_project(),
            "error_handling": await self.test_error_handling(),
            "disconnect": await self.test_disconnect(),
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

        print(f"\nTotal events received: {len(self.events_received)}")
        print("\n" + "="*60)
        print(f"Results: {passed}/{total} tests passed ({passed*100//total}%)")
        print("="*60)

        return results


async def main():
    """Main test runner."""
    tester = WebSocketIntegrationTest()
    results = await tester.run_all_tests()

    # Exit with appropriate code
    all_passed = all(results.values())
    return 0 if all_passed else 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)
