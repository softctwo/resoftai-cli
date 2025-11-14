"""
Performance Test Results Analyzer

Analyzes Locust CSV reports and generates performance insights.
Usage: python analyze_results.py <csv_stats_file>
"""

import sys
import csv
from pathlib import Path
from typing import List, Dict
from dataclasses import dataclass


@dataclass
class EndpointStats:
    """Statistics for a single endpoint."""
    name: str
    method: str
    requests: int
    failures: int
    median_ms: float
    average_ms: float
    min_ms: float
    max_ms: float
    p95_ms: float
    p99_ms: float
    rps: float
    failure_rate: float


class PerformanceAnalyzer:
    """Analyzes performance test results."""

    def __init__(self, stats_file: Path):
        """
        Initialize analyzer with stats file.

        Args:
            stats_file: Path to Locust stats CSV file
        """
        self.stats_file = stats_file
        self.endpoints: List[EndpointStats] = []
        self.thresholds = {
            "p50": 100,  # ms
            "p95": 500,  # ms
            "p99": 1000,  # ms
            "error_rate": 1.0,  # %
        }

    def load_stats(self):
        """Load statistics from CSV file."""
        with open(self.stats_file, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Skip aggregate rows
                if row['Type'] == 'Aggregated':
                    continue

                try:
                    stats = EndpointStats(
                        name=row['Name'],
                        method=row['Type'],
                        requests=int(row['Request Count']),
                        failures=int(row['Failure Count']),
                        median_ms=float(row['Median Response Time']),
                        average_ms=float(row['Average Response Time']),
                        min_ms=float(row['Min Response Time']),
                        max_ms=float(row['Max Response Time']),
                        p95_ms=float(row.get('95%', row.get('95th percentile', 0))),
                        p99_ms=float(row.get('99%', row.get('99th percentile', 0))),
                        rps=float(row.get('Requests/s', row.get('RPS', 0))),
                        failure_rate=(int(row['Failure Count']) / int(row['Request Count']) * 100)
                        if int(row['Request Count']) > 0 else 0
                    )
                    self.endpoints.append(stats)
                except (KeyError, ValueError) as e:
                    print(f"Warning: Skipping row due to error: {e}")
                    continue

    def analyze(self):
        """Analyze performance metrics and generate report."""
        print("=" * 80)
        print("📊 Performance Test Results Analysis")
        print("=" * 80)
        print()

        if not self.endpoints:
            print("❌ No endpoint data found")
            return

        # Overall Statistics
        self._print_overall_stats()

        # Performance Assessment
        self._print_performance_assessment()

        # Top Slowest Endpoints
        self._print_slowest_endpoints()

        # Endpoints with Failures
        self._print_failed_endpoints()

        # Recommendations
        self._print_recommendations()

    def _print_overall_stats(self):
        """Print overall statistics."""
        total_requests = sum(e.requests for e in self.endpoints)
        total_failures = sum(e.failures for e in self.endpoints)
        overall_failure_rate = (total_failures / total_requests * 100) if total_requests > 0 else 0

        avg_median = sum(e.median_ms for e in self.endpoints) / len(self.endpoints)
        avg_p95 = sum(e.p95_ms for e in self.endpoints) / len(self.endpoints)
        avg_p99 = sum(e.p99_ms for e in self.endpoints) / len(self.endpoints)

        print("📈 Overall Statistics:")
        print(f"   - Total Endpoints Tested: {len(self.endpoints)}")
        print(f"   - Total Requests: {total_requests:,}")
        print(f"   - Total Failures: {total_failures:,}")
        print(f"   - Overall Failure Rate: {overall_failure_rate:.2f}%")
        print(f"   - Average Median Response Time: {avg_median:.2f}ms")
        print(f"   - Average P95 Response Time: {avg_p95:.2f}ms")
        print(f"   - Average P99 Response Time: {avg_p99:.2f}ms")
        print()

    def _print_performance_assessment(self):
        """Assess performance against thresholds."""
        print("🎯 Performance Assessment:")
        print()

        # P50 Assessment
        p50_compliant = sum(1 for e in self.endpoints if e.median_ms < self.thresholds["p50"])
        p50_rate = p50_compliant / len(self.endpoints) * 100
        print(f"   P50 < {self.thresholds['p50']}ms:")
        print(f"   {'✅' if p50_rate > 90 else '⚠️' if p50_rate > 70 else '❌'} {p50_compliant}/{len(self.endpoints)} endpoints ({p50_rate:.1f}%)")

        # P95 Assessment
        p95_compliant = sum(1 for e in self.endpoints if e.p95_ms < self.thresholds["p95"])
        p95_rate = p95_compliant / len(self.endpoints) * 100
        print(f"   P95 < {self.thresholds['p95']}ms:")
        print(f"   {'✅' if p95_rate > 90 else '⚠️' if p95_rate > 70 else '❌'} {p95_compliant}/{len(self.endpoints)} endpoints ({p95_rate:.1f}%)")

        # P99 Assessment
        p99_compliant = sum(1 for e in self.endpoints if e.p99_ms < self.thresholds["p99"])
        p99_rate = p99_compliant / len(self.endpoints) * 100
        print(f"   P99 < {self.thresholds['p99']}ms:")
        print(f"   {'✅' if p99_rate > 90 else '⚠️' if p99_rate > 70 else '❌'} {p99_compliant}/{len(self.endpoints)} endpoints ({p99_rate:.1f}%)")

        # Error Rate Assessment
        error_compliant = sum(1 for e in self.endpoints if e.failure_rate < self.thresholds["error_rate"])
        error_rate = error_compliant / len(self.endpoints) * 100
        print(f"   Error Rate < {self.thresholds['error_rate']}%:")
        print(f"   {'✅' if error_rate > 95 else '⚠️' if error_rate > 80 else '❌'} {error_compliant}/{len(self.endpoints)} endpoints ({error_rate:.1f}%)")
        print()

    def _print_slowest_endpoints(self, top_n: int = 5):
        """Print top N slowest endpoints."""
        sorted_by_p95 = sorted(self.endpoints, key=lambda e: e.p95_ms, reverse=True)[:top_n]

        print(f"🐌 Top {top_n} Slowest Endpoints (by P95):")
        print()
        print(f"{'Endpoint':<50} {'Method':<8} {'P50':<10} {'P95':<10} {'P99':<10}")
        print("-" * 88)
        for endpoint in sorted_by_p95:
            print(f"{endpoint.name:<50} {endpoint.method:<8} {endpoint.median_ms:<10.1f} {endpoint.p95_ms:<10.1f} {endpoint.p99_ms:<10.1f}")
        print()

    def _print_failed_endpoints(self):
        """Print endpoints with failures."""
        failed = [e for e in self.endpoints if e.failures > 0]

        if not failed:
            print("✅ No Failed Requests")
            print()
            return

        sorted_by_failures = sorted(failed, key=lambda e: e.failure_rate, reverse=True)

        print(f"❌ Endpoints with Failures:")
        print()
        print(f"{'Endpoint':<50} {'Requests':<12} {'Failures':<12} {'Rate':<10}")
        print("-" * 84)
        for endpoint in sorted_by_failures:
            print(f"{endpoint.name:<50} {endpoint.requests:<12} {endpoint.failures:<12} {endpoint.failure_rate:<10.2f}%")
        print()

    def _print_recommendations(self):
        """Generate optimization recommendations."""
        print("💡 Optimization Recommendations:")
        print()

        recommendations = []

        # Check for slow endpoints
        slow_endpoints = [e for e in self.endpoints if e.p95_ms > 500]
        if slow_endpoints:
            recommendations.append(
                f"• {len(slow_endpoints)} endpoints have P95 > 500ms. Consider:"
            )
            for endpoint in slow_endpoints[:3]:
                recommendations.append(f"  - Optimize {endpoint.name} (P95: {endpoint.p95_ms:.0f}ms)")

        # Check for high error rates
        error_endpoints = [e for e in self.endpoints if e.failure_rate > 1.0]
        if error_endpoints:
            recommendations.append(
                f"• {len(error_endpoints)} endpoints have error rate > 1%. Investigate:"
            )
            for endpoint in error_endpoints[:3]:
                recommendations.append(f"  - {endpoint.name} ({endpoint.failure_rate:.1f}% errors)")

        # General recommendations
        avg_p95 = sum(e.p95_ms for e in self.endpoints) / len(self.endpoints)
        if avg_p95 > 300:
            recommendations.append("• Overall P95 is high. Consider adding Redis caching")

        if slow_endpoints:
            code_quality_endpoints = [e for e in slow_endpoints if 'code-quality' in e.name.lower()]
            if code_quality_endpoints:
                recommendations.append("• Move code quality checks to async background tasks (Celery)")

        if not recommendations:
            recommendations.append("✅ All endpoints meet performance thresholds. Great job!")

        for rec in recommendations:
            print(rec)
        print()

        print("=" * 80)


def main():
    """Main entry point."""
    if len(sys.argv) != 2:
        print("Usage: python analyze_results.py <csv_stats_file>")
        print()
        print("Example:")
        print("  python analyze_results.py tests/performance/reports/baseline_test_20251114_100000_stats.csv")
        sys.exit(1)

    stats_file = Path(sys.argv[1])

    if not stats_file.exists():
        print(f"❌ Error: File not found: {stats_file}")
        sys.exit(1)

    analyzer = PerformanceAnalyzer(stats_file)
    analyzer.load_stats()
    analyzer.analyze()


if __name__ == "__main__":
    main()
