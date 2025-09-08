#!/usr/bin/env python3
"""
Test runner for API services

Usage:
    python run_tests.py                    # Run all tests
    python run_tests.py --transaction     # Run transaction service tests only
    python run_tests.py --alert-rule      # Run alert rule service tests only
    python run_tests.py --coverage        # Run tests with coverage report
    python run_tests.py --verbose         # Run tests with verbose output
"""

import os
import sys
import argparse
import subprocess
from pathlib import Path


def run_command(cmd, capture_output=False):
    """Run a shell command and return the result"""
    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(
        cmd, 
        capture_output=capture_output, 
        text=True,
        cwd=Path(__file__).parent
    )
    
    if result.returncode != 0:
        print(f"Command failed with exit code {result.returncode}")
        if capture_output:
            print("STDOUT:", result.stdout)
            print("STDERR:", result.stderr)
    
    return result


def install_dependencies():
    """Install required test dependencies"""
    print("Installing test dependencies...")
    
    dependencies = [
        'pytest>=7.0.0',
        'pytest-asyncio>=0.21.0', 
        'pytest-mock>=3.10.0',
        'pytest-cov>=4.0.0'
    ]
    
    for dep in dependencies:
        cmd = [sys.executable, '-m', 'pip', 'install', dep]
        result = run_command(cmd, capture_output=True)
        if result.returncode != 0:
            print(f"Failed to install {dep}")
            return False
    
    print("✅ Dependencies installed successfully")
    return True


def run_tests(test_file=None, coverage=False, verbose=False):
    """Run the tests with specified options"""
    
    # Base pytest command
    cmd = [sys.executable, '-m', 'pytest']
    
    # Add configuration
    cmd.extend(['-c', 'pytest.ini'])
    
    # Add verbosity
    if verbose:
        cmd.append('-vv')
    else:
        cmd.append('-v')
    
    # Add coverage if requested
    if coverage:
        cmd.extend([
            '--cov=../services',
            '--cov-report=html',
            '--cov-report=term-missing',
            '--cov-branch'
        ])
    
    # Add specific test file if specified
    if test_file:
        cmd.append(test_file)
    
    # Run the tests
    result = run_command(cmd)
    
    if result.returncode == 0:
        print("\n✅ All tests passed!")
        if coverage:
            print("\n📊 Coverage report generated in htmlcov/")
    else:
        print(f"\n❌ Tests failed with exit code {result.returncode}")
    
    return result.returncode == 0


def main():
    parser = argparse.ArgumentParser(
        description="Run tests for API services",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_tests.py                    # Run all tests
  python run_tests.py --transaction     # Run transaction service tests only
  python run_tests.py --alert-rule      # Run alert rule service tests only
  python run_tests.py --coverage        # Run tests with coverage report
  python run_tests.py --verbose         # Run tests with verbose output
        """
    )
    
    # Test selection arguments
    test_group = parser.add_mutually_exclusive_group()
    test_group.add_argument(
        '--transaction', 
        action='store_true',
        help='Run transaction service tests only'
    )
    test_group.add_argument(
        '--alert-rule', 
        action='store_true',
        help='Run alert rule service tests only'
    )
    
    # Test options
    parser.add_argument(
        '--coverage', 
        action='store_true',
        help='Generate coverage report'
    )
    parser.add_argument(
        '--verbose', 
        action='store_true',
        help='Verbose test output'
    )
    parser.add_argument(
        '--install-deps', 
        action='store_true',
        help='Install required dependencies before running tests'
    )
    
    args = parser.parse_args()
    
    # Change to the tests directory
    os.chdir(Path(__file__).parent)
    
    # Install dependencies if requested
    if args.install_deps:
        if not install_dependencies():
            sys.exit(1)
    
    # Determine which test file to run
    test_file = None
    if args.transaction:
        test_file = 'test_transaction_service.py'
        print("🔍 Running Transaction Service tests...")
    elif args.alert_rule:
        test_file = 'test_alert_rule_service.py'
        print("🚨 Running Alert Rule Service tests...")
    else:
        print("🧪 Running all service tests...")
    
    # Run the tests
    success = run_tests(
        test_file=test_file,
        coverage=args.coverage,
        verbose=args.verbose
    )
    
    if not success:
        sys.exit(1)
    
    print("\n🎉 Test run completed successfully!")


if __name__ == '__main__':
    main()
