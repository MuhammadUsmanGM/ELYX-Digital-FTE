#!/usr/bin/env python3
"""
ELYX - Comprehensive Test Suite Runner

Runs all systematic tests for the ELYX AI Employee framework.
Provides detailed reporting and test coverage summary.

Usage:
    python scripts/run_all_tests.py              # Run all tests
    python scripts/run_all_tests.py --unit       # Run only unit tests
    python scripts/run_all_tests.py --integration # Run only integration tests
    python scripts/run_all_tests.py --verbose    # Run with verbose output
    python scripts/run_all_tests.py --help       # Show help
"""

import os
import sys
import unittest
import argparse
import time
from pathlib import Path
from datetime import datetime
from typing import List, Tuple

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

# ANSI Color codes
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def print_banner():
    """Print ELYX test suite banner"""
    print(f"\n{Colors.OKCYAN}{'=' * 80}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.OKCYAN}  ELYX - Comprehensive Test Suite{Colors.ENDC}")
    print(f"{Colors.OKCYAN}{'=' * 80}{Colors.ENDC}")
    print(f"{Colors.BOLD}  Running tests for: Personal AI Employee Framework{Colors.ENDC}")
    print(f"{Colors.BOLD}  Test started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{Colors.ENDC}")
    print(f"{Colors.OKCYAN}{'=' * 80}{Colors.ENDC}\n")


def print_summary(results: unittest.TestResult, duration: float, test_type: str = "All"):
    """Print test summary"""
    print(f"\n{Colors.OKCYAN}{'=' * 80}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.OKCYAN}  TEST SUMMARY - {test_type} Tests{Colors.ENDC}")
    print(f"{Colors.OKCYAN}{'=' * 80}{Colors.ENDC}")
    
    total = results.testsRun
    failures = len(results.failures)
    errors = len(results.errors)
    skipped = len(results.skipped)
    successes = total - failures - errors - skipped
    
    print(f"\n  {Colors.BOLD}Total Tests:{Colors.ENDC}      {total}")
    print(f"  {Colors.OKGREEN}Passed:{Colors.ENDC}           {successes}")
    print(f"  {Colors.FAIL}Failed:{Colors.ENDC}           {failures}")
    print(f"  {Colors.WARNING}Errors:{Colors.ENDC}           {errors}")
    print(f"  {Colors.OKBLUE}Skipped:{Colors.ENDC}          {skipped}")
    print(f"\n  {Colors.BOLD}Duration:{Colors.ENDC}         {duration:.2f} seconds")
    
    if total > 0:
        success_rate = (successes / total) * 100
        print(f"\n  {Colors.BOLD}Success Rate:{Colors.ENDC}     {success_rate:.1f}%")
    
    # Status indicator
    if failures == 0 and errors == 0:
        status = f"{Colors.OKGREEN}✓ ALL TESTS PASSED{Colors.ENDC}"
    else:
        status = f"{Colors.FAIL}✗ SOME TESTS FAILED{Colors.ENDC}"
    
    print(f"\n  {Colors.BOLD}Status:{Colors.ENDC}         {status}")
    print(f"{Colors.OKCYAN}{'=' * 80}{Colors.ENDC}\n")
    
    # Print failures if any
    if results.failures:
        print(f"\n{Colors.FAIL}{'=' * 80}{Colors.ENDC}")
        print(f"{Colors.BOLD}{Colors.FAIL}  FAILURES{Colors.ENDC}")
        print(f"{Colors.FAIL}{'=' * 80}{Colors.ENDC}")
        for test, traceback in results.failures:
            print(f"\n  {Colors.BOLD}Test:{Colors.ENDC} {test}")
            print(f"  {Colors.FAIL}{'─' * 60}{Colors.ENDC}")
            # Show first 500 chars of traceback
            print(f"  {traceback[:500]}...")
    
    if results.errors:
        print(f"\n{Colors.WARNING}{'=' * 80}{Colors.ENDC}")
        print(f"{Colors.BOLD}{Colors.WARNING}  ERRORS{Colors.ENDC}")
        print(f"{Colors.WARNING}{'=' * 80}{Colors.ENDC}")
        for test, traceback in results.errors:
            print(f"\n  {Colors.BOLD}Test:{Colors.ENDC} {test}")
            print(f"  {Colors.WARNING}{'─' * 60}{Colors.ENDC}")
            print(f"  {traceback[:500]}...")


def discover_tests(test_pattern: str = "test_*.py", test_dirs: List[str] = None) -> unittest.TestSuite:
    """Discover test files in specified directories"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    if test_dirs is None:
        test_dirs = [str(project_root / "scripts")]
    
    for test_dir in test_dirs:
        dir_path = Path(test_dir)
        if not dir_path.exists():
            print(f"{Colors.WARNING}[WARNING]{Colors.ENDC} Test directory not found: {test_dir}")
            continue
        
        print(f"{Colors.OKBLUE}[INFO]{Colors.ENDC} Discovering tests in: {test_dir}")
        
        # Discover tests matching pattern
        try:
            # Use explicit test module loading instead of discover for better path handling
            test_files = list(dir_path.glob(test_pattern))
            
            for test_file in test_files:
                try:
                    # Load test module directly
                    spec = __import__(
                        f"scripts.{test_file.stem}",
                        fromlist=['']
                    )
                    tests = loader.loadTestsFromModule(spec)
                    suite.addTests(tests)
                    print(f"  {Colors.OKGREEN}[OK]{Colors.ENDC} Loaded: {test_file.name}")
                except Exception as e:
                    print(f"  {Colors.WARNING}[WARN]{Colors.ENDC} Could not load {test_file.name}: {e}")
                    
        except Exception as e:
            print(f"{Colors.FAIL}[ERROR]{Colors.ENDC} Failed to discover tests in {test_dir}: {e}")
    
    return suite


def filter_tests_by_type(suite: unittest.TestSuite, test_type: str) -> unittest.TestSuite:
    """Filter tests by type (unit, integration, all)"""
    if test_type == "all":
        return suite
    
    filtered_suite = unittest.TestSuite()
    
    for test_group in suite:
        for test in test_group:
            test_name = str(test)
            
            if test_type == "unit":
                # Unit tests don't contain 'integration' in name
                if 'integration' not in test_name.lower():
                    filtered_suite.addTest(test)
            elif test_type == "integration":
                if 'integration' in test_name.lower():
                    filtered_suite.addTest(test)
    
    return filtered_suite if filtered_suite.countTestCases() > 0 else suite


def run_tests(test_type: str = "all", verbose: bool = False, specific_tests: List[str] = None) -> unittest.TestResult:
    """Run tests with specified configuration"""
    print_banner()
    
    # Discover all tests
    suite = discover_tests()
    total_tests = suite.countTestCases()
    print(f"\n{Colors.OKBLUE}[INFO]{Colors.ENDC} Discovered {total_tests} tests")
    
    # Filter by type if needed
    if test_type != "all":
        suite = filter_tests_by_type(suite, test_type)
        filtered_count = suite.countTestCases()
        print(f"{Colors.OKBLUE}[INFO]{Colors.ENDC} Running {filtered_count} {test_type} tests")
    
    # Run specific tests if provided
    if specific_tests:
        loader = unittest.TestLoader()
        specific_suite = unittest.TestSuite()
        for test_name in specific_tests:
            try:
                # Try to load specific test
                test = loader.loadTestsFromName(test_name)
                specific_suite.addTests(test)
            except Exception as e:
                print(f"{Colors.WARNING}[WARNING]{Colors.ENDC} Could not load test: {test_name} - {e}")
        suite = specific_suite if specific_suite.countTestCases() > 0 else suite
    
    # Create test runner
    if verbose:
        runner = unittest.TextTestRunner(
            verbosity=2,
            stream=sys.stdout,
            failfast=False,
            buffer=False
        )
    else:
        runner = unittest.TextTestRunner(
            verbosity=1,
            stream=sys.stdout,
            failfast=False,
            buffer=True
        )
    
    # Run tests
    print(f"\n{Colors.OKGREEN}[RUNNER]{Colors.ENDC} Starting test execution...\n")
    start_time = time.time()
    results = runner.run(suite)
    duration = time.time() - start_time
    
    # Print summary
    test_type_label = test_type.capitalize() if test_type != "all" else "All"
    print_summary(results, duration, test_type_label)
    
    return results


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="ELYX Comprehensive Test Suite Runner",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_all_tests.py                    Run all tests
  python run_all_tests.py --unit             Run only unit tests
  python run_all_tests.py --integration      Run only integration tests
  python run_all_tests.py --verbose          Run with verbose output
  python run_all_tests.py --test test_name   Run specific test
        """
    )
    
    parser.add_argument(
        '--unit',
        action='store_true',
        help='Run only unit tests'
    )
    
    parser.add_argument(
        '--integration',
        action='store_true',
        help='Run only integration tests'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Run tests with verbose output'
    )
    
    parser.add_argument(
        '--test', '-t',
        action='append',
        dest='specific_tests',
        help='Run specific test(s) by name'
    )
    
    parser.add_argument(
        '--help-examples',
        action='store_true',
        help='Show detailed examples'
    )
    
    args = parser.parse_args()
    
    # Determine test type
    if args.unit:
        test_type = "unit"
    elif args.integration:
        test_type = "integration"
    else:
        test_type = "all"
    
    # Run tests
    results = run_tests(
        test_type=test_type,
        verbose=args.verbose,
        specific_tests=args.specific_tests
    )
    
    # Exit with appropriate code
    if results.failures or results.errors:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
