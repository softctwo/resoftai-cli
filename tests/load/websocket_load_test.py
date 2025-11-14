"""Simple WebSocket load testing script.

This script creates multiple concurrent WebSocket connections
to test collaborative editing under load.

Usage:
    python tests/load/websocket_load_test.py --url ws://localhost:8000 --users 50 --duration 60
"""
import asyncio
import socketio
import time
import argparse
import statistics
from datetime import datetime
from typing import List, Dict
import random


class WebSocketLoadTester:
    """WebSocket load testing client."""

    def __init__(self, base_url: str, user_id: int):
        """
        Initialize load tester.

        Args:
            base_url: WebSocket server URL
            user_id: Unique user ID
        """
        self.base_url = base_url
        self.user_id = user_id
        self.username = f"LoadUser{user_id}"
        self.sio = socketio.AsyncClient()
        self.connected = False
        self.messages_sent = 0
        self.messages_received = 0
        self.latencies: List[float] = []
        self.errors = 0
        self.file_id = random.randint(1, 5)  # Distribute across 5 files
        self.project_id = 1

        # Setup handlers
        self.setup_handlers()

    def setup_handlers(self):
        """Setup Socket.IO event handlers."""
        @self.sio.event
        async def connect():
            self.connected = True
            print(f"User {self.user_id} connected")

        @self.sio.event
        async def disconnect():
            self.connected = False
            print(f"User {self.user_id} disconnected")

        @self.sio.on('file.joined')
        async def on_file_joined(data):
            self.messages_received += 1

        @self.sio.on('file.edit')
        async def on_file_edit(data):
            self.messages_received += 1

        @self.sio.on('cursor.position')
        async def on_cursor_position(data):
            self.messages_received += 1

        @self.sio.on('error')
        async def on_error(data):
            self.errors += 1
            print(f"User {self.user_id} error: {data}")

    async def connect(self):
        """Connect to WebSocket server."""
        try:
            await self.sio.connect(
                self.base_url,
                transports=['websocket'],
                wait_timeout=10
            )
            return True
        except Exception as e:
            print(f"User {self.user_id} connection failed: {e}")
            self.errors += 1
            return False

    async def disconnect(self):
        """Disconnect from server."""
        if self.connected:
            await self.sio.disconnect()

    async def join_file_session(self):
        """Join file editing session."""
        try:
            await self.sio.emit('join_file_session', {
                'file_id': self.file_id,
                'project_id': self.project_id,
                'user_id': self.user_id,
                'username': self.username
            })
            self.messages_sent += 1
        except Exception as e:
            print(f"User {self.user_id} join failed: {e}")
            self.errors += 1

    async def send_edit(self):
        """Send file edit."""
        if not self.connected:
            return

        try:
            start_time = time.time()

            changes = {
                'range': {
                    'startLineNumber': random.randint(1, 100),
                    'startColumn': 1,
                    'endLineNumber': random.randint(1, 100),
                    'endColumn': 10
                },
                'text': f'Code from {self.username} at {datetime.now()}'
            }

            await self.sio.emit('file_edit', {
                'file_id': self.file_id,
                'changes': changes
            })

            latency = (time.time() - start_time) * 1000  # Convert to ms
            self.latencies.append(latency)
            self.messages_sent += 1

        except Exception as e:
            print(f"User {self.user_id} edit failed: {e}")
            self.errors += 1

    async def send_cursor_position(self):
        """Send cursor position."""
        if not self.connected:
            return

        try:
            start_time = time.time()

            position = {
                'lineNumber': random.randint(1, 100),
                'column': random.randint(1, 80)
            }

            await self.sio.emit('cursor_position', {
                'file_id': self.file_id,
                'position': position
            })

            latency = (time.time() - start_time) * 1000
            self.latencies.append(latency)
            self.messages_sent += 1

        except Exception as e:
            print(f"User {self.user_id} cursor update failed: {e}")
            self.errors += 1

    async def run_simulation(self, duration: int):
        """
        Run simulation for specified duration.

        Args:
            duration: Test duration in seconds
        """
        # Connect
        connected = await self.connect()
        if not connected:
            return

        # Join file session
        await asyncio.sleep(0.5)
        await self.join_file_session()
        await asyncio.sleep(0.5)

        # Simulate activity
        end_time = time.time() + duration

        while time.time() < end_time:
            # Randomly choose action
            action = random.choices(
                ['edit', 'cursor', 'idle'],
                weights=[3, 5, 2]  # More cursor updates than edits
            )[0]

            if action == 'edit':
                await self.send_edit()
                await asyncio.sleep(random.uniform(2, 5))
            elif action == 'cursor':
                await self.send_cursor_position()
                await asyncio.sleep(random.uniform(0.5, 2))
            else:
                await asyncio.sleep(random.uniform(1, 3))

        # Disconnect
        await self.disconnect()

    def get_stats(self) -> Dict:
        """Get statistics for this user."""
        return {
            'user_id': self.user_id,
            'messages_sent': self.messages_sent,
            'messages_received': self.messages_received,
            'errors': self.errors,
            'avg_latency_ms': statistics.mean(self.latencies) if self.latencies else 0,
            'min_latency_ms': min(self.latencies) if self.latencies else 0,
            'max_latency_ms': max(self.latencies) if self.latencies else 0,
            'p95_latency_ms': statistics.quantiles(self.latencies, n=20)[18] if len(self.latencies) > 20 else 0,
            'p99_latency_ms': statistics.quantiles(self.latencies, n=100)[98] if len(self.latencies) > 100 else 0,
        }


async def run_load_test(url: str, num_users: int, duration: int):
    """
    Run load test with multiple concurrent users.

    Args:
        url: WebSocket server URL
        num_users: Number of concurrent users
        duration: Test duration in seconds
    """
    print(f"\n{'='*60}")
    print(f"WebSocket Load Test")
    print(f"{'='*60}")
    print(f"Server: {url}")
    print(f"Users: {num_users}")
    print(f"Duration: {duration}s")
    print(f"{'='*60}\n")

    # Create testers
    testers = [WebSocketLoadTester(url, i) for i in range(num_users)]

    # Run simulations concurrently
    start_time = time.time()
    tasks = [tester.run_simulation(duration) for tester in testers]

    try:
        await asyncio.gather(*tasks)
    except KeyboardInterrupt:
        print("\nTest interrupted by user")

    elapsed_time = time.time() - start_time

    # Collect statistics
    print(f"\n{'='*60}")
    print(f"Test Results")
    print(f"{'='*60}")
    print(f"Elapsed time: {elapsed_time:.2f}s")

    total_sent = sum(t.messages_sent for t in testers)
    total_received = sum(t.messages_received for t in testers)
    total_errors = sum(t.errors for t in testers)
    all_latencies = [lat for t in testers for lat in t.latencies]

    print(f"Total messages sent: {total_sent}")
    print(f"Total messages received: {total_received}")
    print(f"Total errors: {total_errors}")
    print(f"Messages per second: {total_sent / elapsed_time:.2f}")

    if all_latencies:
        print(f"\nLatency Statistics:")
        print(f"  Average: {statistics.mean(all_latencies):.2f}ms")
        print(f"  Median: {statistics.median(all_latencies):.2f}ms")
        print(f"  Min: {min(all_latencies):.2f}ms")
        print(f"  Max: {max(all_latencies):.2f}ms")
        if len(all_latencies) > 20:
            print(f"  P95: {statistics.quantiles(all_latencies, n=20)[18]:.2f}ms")
        if len(all_latencies) > 100:
            print(f"  P99: {statistics.quantiles(all_latencies, n=100)[98]:.2f}ms")

    # Individual user stats (only show first 5)
    print(f"\nIndividual User Stats (first 5):")
    for tester in testers[:5]:
        stats = tester.get_stats()
        print(f"  User {stats['user_id']}: "
              f"Sent={stats['messages_sent']}, "
              f"Received={stats['messages_received']}, "
              f"Errors={stats['errors']}, "
              f"AvgLatency={stats['avg_latency_ms']:.2f}ms")

    print(f"{'='*60}\n")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='WebSocket Load Testing')
    parser.add_argument(
        '--url',
        default='ws://localhost:8000',
        help='WebSocket server URL (default: ws://localhost:8000)'
    )
    parser.add_argument(
        '--users',
        type=int,
        default=10,
        help='Number of concurrent users (default: 10)'
    )
    parser.add_argument(
        '--duration',
        type=int,
        default=30,
        help='Test duration in seconds (default: 30)'
    )

    args = parser.parse_args()

    # Run load test
    asyncio.run(run_load_test(args.url, args.users, args.duration))


if __name__ == '__main__':
    main()
