#!/usr/bin/env python3
"""
Script to run all unit tests individually to avoid conflicts.
"""

import unittest
import sys
import os
import logging
from pathlib import Path
import subprocess

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("test_runner")

def run_all_tests():
    """Run all unit tests with detailed output."""
    # Print header
    print("\n" + "="*80)
    print(" RUNNING ALL UNIT TESTS ".center(80, "="))
    print("="*80 + "\n")
    
    # Enable test debugging if needed
    os.environ["TEST_DEBUG"] = "true"
    
    # Find test directory
    tests_dir = Path(__file__).parent
    unit_dir = tests_dir / "unit"
    
    # Collect test modules
    test_modules = [f for f in unit_dir.glob("test_*.py")]
    
    all_passed = True
    tests_run = 0
    errors = 0
    failures = 0
    
    # Run each test module separately to avoid conflicts
    for test_module in test_modules:
        module_name = test_module.stem
        print("\n" + "-"*80)
        print(f" RUNNING {module_name.upper()} ".center(80, "-"))
        print("-"*80 + "\n")
        
        # Create test suite for this module
        loader = unittest.TestLoader()
        suite = loader.discover(start_dir=str(unit_dir), pattern=f"{test_module.name}")
        
        # Create a text test runner with verbose output
        runner = unittest.TextTestRunner(verbosity=2)
        
        # Run the tests
        result = runner.run(suite)
        
        # Update stats
        tests_run += result.testsRun
        errors += len(result.errors)
        failures += len(result.failures)
        
        if not result.wasSuccessful():
            all_passed = False
    
    # Print summary
    print("\n" + "="*80)
    print(" TEST RESULTS SUMMARY ".center(80, "="))
    print("="*80)
    print(f"Total tests run: {tests_run}")
    print(f"Total errors: {errors}")
    print(f"Total failures: {failures}")
    
    if all_passed:
        print("\n" + "="*80)
        print(" ALL TESTS PASSED SUCCESSFULLY ".center(80, "="))
        print("="*80 + "\n")
        return 0
    else:
        print("\n" + "="*80)
        print(" SOME TESTS FAILED ".center(80, "="))
        print("="*80 + "\n")
        return 1

if __name__ == "__main__":
    sys.exit(run_all_tests())
