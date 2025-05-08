#!/usr/bin/env python
"""
Test Runner for APE Core Tests

This script runs all unit tests for the APE Core system.
"""

import os
import sys
import unittest
import argparse

# Add the repository root to sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Try to import python-dotenv for environment variables
try:
    from dotenv import load_dotenv
    # Load environment variables from .env file
    load_dotenv()
except ImportError:
    # Manual environment variable loading if python-dotenv isn't available
    def load_env_file():
        """Load environment variables from .env file"""
        env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')
        if os.path.exists(env_path):
            with open(env_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue
                    try:
                        key, value = line.split('=', 1)
                        os.environ[key] = value
                    except ValueError:
                        continue
    
    load_env_file()


def run_tests(pattern=None, verbose=False):
    """
    Run tests matching the specified pattern
    
    Args:
        pattern: Pattern to match test files (default: None which runs all tests)
        verbose: Whether to show verbose output (default: False)
    
    Returns:
        Test result
    """
    # Discover and run tests
    test_loader = unittest.TestLoader()
    
    if pattern:
        test_suite = test_loader.discover('tests', pattern=pattern)
    else:
        test_suite = test_loader.discover('tests')
    
    # Set verbosity level
    verbosity = 2 if verbose else 1
    
    # Run tests
    test_runner = unittest.TextTestRunner(verbosity=verbosity)
    result = test_runner.run(test_suite)
    
    return result


def main():
    """Main function to run tests with command line arguments"""
    # Setup argument parser
    parser = argparse.ArgumentParser(description='Run APE Core tests')
    parser.add_argument(
        '-p', '--pattern', 
        default='test_*.py',
        help='Pattern to match test files (default: test_*.py)'
    )
    parser.add_argument(
        '-v', '--verbose', 
        action='store_true',
        help='Show verbose output'
    )
    parser.add_argument(
        '-m', '--module', 
        help='Run tests for a specific module (e.g. llm_service, jira_agent)'
    )
    
    # Parse arguments
    args = parser.parse_args()
    
    # Determine pattern based on module argument
    if args.module:
        pattern = f'test_{args.module}.py'
    else:
        pattern = args.pattern
    
    # Run tests
    print(f"Running tests with pattern: {pattern}")
    result = run_tests(pattern, args.verbose)
    
    # Return exit code based on test result
    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    sys.exit(main())