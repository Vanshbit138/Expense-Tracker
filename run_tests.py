#!/usr/bin/env python3
"""
Test runner script for the Expense Tracker application.
"""

import argparse
import subprocess
import sys
from pathlib import Path


def run_command(cmd, description):
    """Run a command and return the result."""
    print(f"\n{'='*60}")
    print(f"Running: {description}")
    print(f"Command: {' '.join(cmd)}")
    print(f"{'='*60}")

    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.stdout:
        print("STDOUT:")
        print(result.stdout)

    if result.stderr:
        print("STDERR:")
        print(result.stderr)

    return result.returncode == 0


def main():
    """Main test runner function."""
    parser = argparse.ArgumentParser(description="Expense Tracker Test Runner")
    parser.add_argument(
        "test_type",
        choices=["unit", "integration", "all", "coverage", "help"],
        help="Type of tests to run",
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Run tests in verbose mode"
    )

    args = parser.parse_args()

    # Base pytest command
    base_cmd = ["python", "-m", "pytest"]

    if args.verbose:
        base_cmd.append("-v")

    # Test type specific commands
    if args.test_type == "unit":
        cmd = base_cmd + ["tests/unit/"]
        success = run_command(cmd, "Unit Tests")

    elif args.test_type == "integration":
        cmd = base_cmd + ["tests/integration/"]
        success = run_command(cmd, "Integration Tests")

    elif args.test_type == "all":
        cmd = base_cmd + ["tests/"]
        success = run_command(cmd, "All Tests")

    elif args.test_type == "coverage":
        cmd = base_cmd + [
            "--cov=src",
            "--cov-report=html",
            "--cov-report=term-missing",
            "tests/",
        ]
        success = run_command(cmd, "Tests with Coverage")
        if success:
            print(
                f"\nCoverage report generated in: {Path.cwd() / 'htmlcov' / 'index.html'}"
            )

    elif args.test_type == "help":
        print("Expense Tracker Test Runner")
        print("=" * 40)
        print("Usage: python run_tests.py <test_type> [options]")
        print("\nTest Types:")
        print("  unit        - Run unit tests only")
        print("  integration - Run integration tests only")
        print("  all         - Run all tests")
        print("  coverage    - Run all tests with coverage report")
        print("  help        - Show this help message")
        print("\nOptions:")
        print("  --verbose, -v  - Run tests in verbose mode")
        print("\nExamples:")
        print("  python run_tests.py unit")
        print("  python run_tests.py integration --verbose")
        print("  python run_tests.py all")
        print("  python run_tests.py coverage")
        return True

    if success:
        print(f"\n✅ {args.test_type.title()} tests completed successfully!")
        return True
    else:
        print(f"\n❌ {args.test_type.title()} tests failed!")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
