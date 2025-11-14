"""
WebSocket Performance Testing for ResoftAI

Tests WebSocket connection stability, message latency, and concurrent connections.
Run with: python websocket_test.py --url ws://localhost:8000 --connections 100
"""

import asyncio
import time
import statistics
import argparse
from typing import List, Dict
import socketio
from datetime import datetime


class WebSocketLoadTester:
    """WebSocket load testing utility."""

    def __init__(self, url: str, num_connections: int = 100):
        """
        Initialize WebSocket load tester.

        Args:
            url: WebSocket server URL
            num_connections: Number of concurrent connections to establish
        """
        self.url = url
        self.num_connections = num_connections
        self.clients: List[socketio.AsyncClient] = []
        self.connection_times: List[float] = []
        self.message_latencies: List[float] = []
        self.errors: List[Dict] = []
        self.messages_sent = 0
        self.messages_received = 0

    async def create_client(self, client_id: int) -> socketio.AsyncClient:
        """
        Create and connect a Socket.IO client.

        Args:
            client_id: Unique identifier for the client

        Returns:
            Connected Socket.IO client
        """
        sio = socketio.AsyncClient()

        @sio.event
        async def connect():
            """Handle connection event."""
            print(f"✅ Client {client_id} connected")

        @sio.event
        async def disconnect():
            """Handle disconnection event."""
            print(f"❌ Client {client_id} disconnected")

        @sio.event
        async def pong(data):
            """Handle pong response."""
            send_time = data.get('timestamp')
            if send_time:
                latency = (time.time() - send_time) * 1000  # Convert to ms
                self.message_latencies.append(latency)
                self.messages_received += 1

        @sio.event
        async def error(data):
            """Handle error event."""
            self.errors.append({
                'client_id': client_id,
                'error': str(data),
                'timestamp': datetime.now().isoformat()
            })

        try:
            start_time = time.time()
            await sio.connect(self.url, transports=['websocket'])
            connection_time = (time.time() - start_time) * 1000
            self.connection_times.append(connection_time)
            return sio
        except Exception as e:
            self.errors.append({
                'client_id': client_id,
                'error': f"Connection failed: {str(e)}",
                'timestamp': datetime.now().isoformat()
            })
            raise

    async def establish_connections(self):
        """Establish all WebSocket connections."""
        print(f"\n🔌 Establishing {self.num_connections} WebSocket connections...")

        tasks = []
        for i in range(self.num_connections):
            task = self.create_client(i)
            tasks.append(task)

        # Connect all clients concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Filter out failed connections
        self.clients = [r for r in results if isinstance(r, socketio.AsyncClient)]

        success_rate = len(self.clients) / self.num_connections * 100
        print(f"\n📊 Connection Results:")
        print(f"   - Successful: {len(self.clients)}/{self.num_connections}")
        print(f"   - Success Rate: {success_rate:.1f}%")
        print(f"   - Errors: {len(self.errors)}")

    async def send_ping_messages(self, duration_seconds: int = 60):
        """
        Send ping messages from all clients.

        Args:
            duration_seconds: Duration to send messages
        """
        print(f"\n📤 Sending ping messages for {duration_seconds} seconds...")

        start_time = time.time()
        tasks = []

        async def send_pings(client: socketio.AsyncClient, client_id: int):
            """Send periodic pings from a single client."""
            while time.time() - start_time < duration_seconds:
                try:
                    await client.emit('ping', {
                        'timestamp': time.time(),
                        'client_id': client_id
                    })
                    self.messages_sent += 1
                    await asyncio.sleep(1)  # Send ping every second
                except Exception as e:
                    self.errors.append({
                        'client_id': client_id,
                        'error': f"Send failed: {str(e)}",
                        'timestamp': datetime.now().isoformat()
                    })

        # Create send tasks for all clients
        for idx, client in enumerate(self.clients):
            task = send_pings(client, idx)
            tasks.append(task)

        # Run all send tasks concurrently
        await asyncio.gather(*tasks, return_exceptions=True)

        print(f"\n✅ Message sending completed")
        print(f"   - Messages sent: {self.messages_sent}")
        print(f"   - Messages received: {self.messages_received}")

    async def disconnect_all(self):
        """Disconnect all clients."""
        print(f"\n🔌 Disconnecting {len(self.clients)} clients...")

        tasks = []
        for client in self.clients:
            task = client.disconnect()
            tasks.append(task)

        await asyncio.gather(*tasks, return_exceptions=True)
        print("✅ All clients disconnected")

    def print_statistics(self):
        """Print performance statistics."""
        print("\n" + "=" * 70)
        print("📊 WebSocket Performance Test Results")
        print("=" * 70)

        # Connection Statistics
        if self.connection_times:
            print("\n🔌 Connection Performance:")
            print(f"   - Mean connection time: {statistics.mean(self.connection_times):.2f}ms")
            print(f"   - Median connection time: {statistics.median(self.connection_times):.2f}ms")
            print(f"   - Min connection time: {min(self.connection_times):.2f}ms")
            print(f"   - Max connection time: {max(self.connection_times):.2f}ms")

        # Message Latency Statistics
        if self.message_latencies:
            sorted_latencies = sorted(self.message_latencies)
            p50_idx = int(len(sorted_latencies) * 0.50)
            p95_idx = int(len(sorted_latencies) * 0.95)
            p99_idx = int(len(sorted_latencies) * 0.99)

            print("\n📨 Message Latency:")
            print(f"   - Mean latency: {statistics.mean(self.message_latencies):.2f}ms")
            print(f"   - P50 latency: {sorted_latencies[p50_idx]:.2f}ms")
            print(f"   - P95 latency: {sorted_latencies[p95_idx]:.2f}ms")
            print(f"   - P99 latency: {sorted_latencies[p99_idx]:.2f}ms")
            print(f"   - Min latency: {min(self.message_latencies):.2f}ms")
            print(f"   - Max latency: {max(self.message_latencies):.2f}ms")

        # Message Statistics
        print("\n📊 Message Statistics:")
        print(f"   - Total messages sent: {self.messages_sent}")
        print(f"   - Total messages received: {self.messages_received}")
        if self.messages_sent > 0:
            delivery_rate = self.messages_received / self.messages_sent * 100
            print(f"   - Delivery rate: {delivery_rate:.1f}%")

        # Error Statistics
        print("\n❌ Error Statistics:")
        print(f"   - Total errors: {len(self.errors)}")
        if self.errors:
            print("\n   Recent errors:")
            for error in self.errors[:5]:
                print(f"   - Client {error.get('client_id', 'N/A')}: {error.get('error', 'Unknown')}")

        # Performance Assessment
        print("\n🎯 Performance Assessment:")
        if self.message_latencies:
            avg_latency = statistics.mean(self.message_latencies)
            if avg_latency < 50:
                print("   ✅ EXCELLENT - Average latency < 50ms")
            elif avg_latency < 100:
                print("   ✅ GOOD - Average latency < 100ms")
            elif avg_latency < 200:
                print("   ⚠️  ACCEPTABLE - Average latency < 200ms")
            else:
                print("   ❌ POOR - Average latency > 200ms")

        if self.errors:
            error_rate = len(self.errors) / (self.messages_sent + len(self.errors)) * 100
            if error_rate < 1:
                print("   ✅ EXCELLENT - Error rate < 1%")
            elif error_rate < 5:
                print("   ⚠️  ACCEPTABLE - Error rate < 5%")
            else:
                print("   ❌ POOR - Error rate > 5%")

        print("\n" + "=" * 70)

    async def run_test(self, duration_seconds: int = 60):
        """
        Run the complete WebSocket load test.

        Args:
            duration_seconds: Duration to run the test
        """
        try:
            # Establish connections
            await self.establish_connections()

            if not self.clients:
                print("❌ No clients connected. Aborting test.")
                return

            # Send messages
            await self.send_ping_messages(duration_seconds)

            # Wait a bit for pending messages
            await asyncio.sleep(2)

            # Disconnect
            await self.disconnect_all()

            # Print statistics
            self.print_statistics()

        except Exception as e:
            print(f"\n❌ Test failed: {str(e)}")
            raise


async def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="WebSocket Performance Testing for ResoftAI"
    )
    parser.add_argument(
        "--url",
        default="http://localhost:8000",
        help="WebSocket server URL (default: http://localhost:8000)"
    )
    parser.add_argument(
        "--connections",
        type=int,
        default=100,
        help="Number of concurrent connections (default: 100)"
    )
    parser.add_argument(
        "--duration",
        type=int,
        default=60,
        help="Test duration in seconds (default: 60)"
    )

    args = parser.parse_args()

    print("=" * 70)
    print("🚀 ResoftAI WebSocket Performance Test")
    print("=" * 70)
    print(f"\nConfiguration:")
    print(f"   - Server URL: {args.url}")
    print(f"   - Concurrent connections: {args.connections}")
    print(f"   - Test duration: {args.duration}s")

    # Run test
    tester = WebSocketLoadTester(args.url, args.connections)
    await tester.run_test(args.duration)


if __name__ == "__main__":
    asyncio.run(main())
