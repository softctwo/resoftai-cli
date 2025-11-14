#!/usr/bin/env python3
"""
Real-time performance monitoring dashboard for ResoftAI.

Usage:
    python scripts/monitor_performance.py
    python scripts/monitor_performance.py --url http://localhost:8000
    python scripts/monitor_performance.py --interval 2
"""

import requests
import time
import argparse
import sys
from datetime import datetime
from typing import Dict, Any


def clear_screen():
    """Clear terminal screen."""
    print('\033[2J\033[H', end='')


def format_size(bytes: int) -> str:
    """Format bytes to human readable string."""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes < 1024.0:
            return f"{bytes:.2f} {unit}"
        bytes /= 1024.0
    return f"{bytes:.2f} TB"


def format_duration(seconds: float) -> str:
    """Format seconds to human readable string."""
    if seconds < 0.001:
        return f"{seconds * 1000000:.0f} μs"
    elif seconds < 1:
        return f"{seconds * 1000:.2f} ms"
    else:
        return f"{seconds:.2f} s"


def colorize(text: str, color: str) -> str:
    """Colorize text for terminal output."""
    colors = {
        'red': '\033[91m',
        'green': '\033[92m',
        'yellow': '\033[93m',
        'blue': '\033[94m',
        'magenta': '\033[95m',
        'cyan': '\033[96m',
        'white': '\033[97m',
        'bold': '\033[1m',
        'end': '\033[0m'
    }
    return f"{colors.get(color, '')}{text}{colors['end']}"


def get_metrics(base_url: str) -> Dict[str, Any]:
    """Fetch performance metrics from API."""
    try:
        response = requests.get(f"{base_url}/api/performance/metrics", timeout=5)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(colorize(f"Error fetching metrics: {e}", 'red'))
        return {}


def get_websocket_metrics(base_url: str) -> Dict[str, Any]:
    """Fetch WebSocket metrics from API."""
    try:
        response = requests.get(f"{base_url}/api/performance/websocket", timeout=5)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return {}


def print_header(base_url: str):
    """Print dashboard header."""
    print(colorize("=" * 80, 'cyan'))
    print(colorize("ResoftAI Performance Monitor".center(80), 'bold'))
    print(colorize("=" * 80, 'cyan'))
    print(f"Server: {colorize(base_url, 'blue')}")
    print(f"Time: {colorize(datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 'green')}")
    print(colorize("-" * 80, 'cyan'))


def print_timing_metrics(metrics: Dict[str, Any]):
    """Print timing metrics section."""
    print(colorize("\n📊 Timing Metrics", 'bold'))
    print(colorize("-" * 80, 'cyan'))

    perf_metrics = metrics.get('performance_metrics', {})

    # Filter timing metrics
    timing_metrics = {k: v for k, v in perf_metrics.items()
                      if isinstance(v, dict) and 'avg' in v}

    if not timing_metrics:
        print(colorize("  No timing data available", 'yellow'))
        return

    # Print header
    print(f"{'Operation':<40} {'Count':>8} {'Avg':>12} {'Min':>12} {'Max':>12}")
    print(colorize("-" * 80, 'white'))

    # Sort by average time (slowest first)
    sorted_metrics = sorted(timing_metrics.items(),
                           key=lambda x: x[1].get('avg', 0),
                           reverse=True)

    for name, stats in sorted_metrics[:10]:  # Show top 10
        avg_time = stats.get('avg', 0)
        min_time = stats.get('min', 0)
        max_time = stats.get('max', 0)
        count = stats.get('count', 0)

        # Color code based on performance
        if avg_time > 0.5:
            color = 'red'
        elif avg_time > 0.1:
            color = 'yellow'
        else:
            color = 'green'

        operation = name[:38]
        print(f"{operation:<40} {count:>8} "
              f"{colorize(format_duration(avg_time), color):>20} "
              f"{format_duration(min_time):>12} "
              f"{format_duration(max_time):>12}")


def print_websocket_metrics(ws_metrics: Dict[str, Any]):
    """Print WebSocket metrics section."""
    print(colorize("\n🔌 WebSocket Metrics", 'bold'))
    print(colorize("-" * 80, 'cyan'))

    if not ws_metrics:
        print(colorize("  No WebSocket data available", 'yellow'))
        return

    # Connections
    active = ws_metrics.get('active_connections', 0)
    total = ws_metrics.get('total_connections', 0)
    disconnects = ws_metrics.get('total_disconnections', 0)

    print(f"  Active Connections:  {colorize(str(active), 'green')}")
    print(f"  Total Connections:   {total}")
    print(f"  Total Disconnects:   {disconnects}")

    # Messages
    msg_sent = ws_metrics.get('messages_sent', 0)
    msg_recv = ws_metrics.get('messages_received', 0)
    bytes_sent = ws_metrics.get('bytes_sent', 0)
    bytes_recv = ws_metrics.get('bytes_received', 0)

    print(f"\n  Messages Sent:       {msg_sent:,}")
    print(f"  Messages Received:   {msg_recv:,}")
    print(f"  Bytes Sent:          {format_size(bytes_sent)}")
    print(f"  Bytes Received:      {format_size(bytes_recv)}")

    # Average message sizes
    avg_size_sent = ws_metrics.get('avg_message_size_sent', 0)
    avg_size_recv = ws_metrics.get('avg_message_size_received', 0)

    print(f"\n  Avg Message Size (Sent):     {format_size(avg_size_sent)}")
    print(f"  Avg Message Size (Received): {format_size(avg_size_recv)}")

    # Errors
    errors = ws_metrics.get('errors', 0)
    reconnections = ws_metrics.get('reconnections', 0)

    if errors > 0:
        print(f"\n  Errors:          {colorize(str(errors), 'red')}")
    else:
        print(f"\n  Errors:          {colorize(str(errors), 'green')}")

    print(f"  Reconnections:   {reconnections}")


def print_counters(metrics: Dict[str, Any]):
    """Print counter metrics section."""
    print(colorize("\n📈 Counters", 'bold'))
    print(colorize("-" * 80, 'cyan'))

    perf_metrics = metrics.get('performance_metrics', {})
    counters = perf_metrics.get('counters', {})

    if not counters:
        print(colorize("  No counter data available", 'yellow'))
        return

    # Sort by value (highest first)
    sorted_counters = sorted(counters.items(), key=lambda x: x[1], reverse=True)

    for name, value in sorted_counters[:15]:  # Show top 15
        # Remove 'counter.' prefix if present
        display_name = name.replace('counter.', '')
        print(f"  {display_name:<50} {value:>15,}")


def print_system_info(metrics: Dict[str, Any]):
    """Print system information."""
    print(colorize("\n⚙️  System Info", 'bold'))
    print(colorize("-" * 80, 'cyan'))

    perf_metrics = metrics.get('performance_metrics', {})
    uptime = perf_metrics.get('uptime_seconds', 0)

    hours = int(uptime // 3600)
    minutes = int((uptime % 3600) // 60)
    seconds = int(uptime % 60)

    print(f"  Uptime: {hours}h {minutes}m {seconds}s")


def print_footer():
    """Print dashboard footer."""
    print(colorize("\n" + "=" * 80, 'cyan'))
    print(colorize("Press Ctrl+C to exit".center(80), 'white'))


def monitor(base_url: str, interval: int = 5):
    """Main monitoring loop."""
    print(colorize("\nStarting performance monitor...\n", 'green'))
    print(f"Refresh interval: {interval} seconds")
    print("Press Ctrl+C to stop\n")

    try:
        while True:
            clear_screen()

            # Fetch data
            metrics = get_metrics(base_url)
            ws_metrics = get_websocket_metrics(base_url)

            # Display dashboard
            print_header(base_url)
            print_timing_metrics(metrics)
            print_websocket_metrics(ws_metrics)
            print_counters(metrics)
            print_system_info(metrics)
            print_footer()

            # Wait for next refresh
            time.sleep(interval)

    except KeyboardInterrupt:
        print(colorize("\n\nMonitoring stopped.", 'yellow'))
        sys.exit(0)
    except Exception as e:
        print(colorize(f"\n\nError: {e}", 'red'))
        sys.exit(1)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Real-time performance monitoring for ResoftAI'
    )
    parser.add_argument(
        '--url',
        default='http://localhost:8000',
        help='Base URL of the API server (default: http://localhost:8000)'
    )
    parser.add_argument(
        '--interval',
        type=int,
        default=5,
        help='Refresh interval in seconds (default: 5)'
    )
    parser.add_argument(
        '--once',
        action='store_true',
        help='Display metrics once and exit'
    )

    args = parser.parse_args()

    if args.once:
        # Display once and exit
        metrics = get_metrics(args.url)
        ws_metrics = get_websocket_metrics(args.url)

        print_header(args.url)
        print_timing_metrics(metrics)
        print_websocket_metrics(ws_metrics)
        print_counters(metrics)
        print_system_info(metrics)
    else:
        # Start monitoring loop
        monitor(args.url, args.interval)


if __name__ == '__main__':
    main()
