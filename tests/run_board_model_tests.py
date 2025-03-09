#!/usr/bin/env python3
"""
Script to run only Board model tests with detailed output.
"""

import unittest
import sys
import os
import logging
from pathlib import Path

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("test_runner")

def run_board_model_tests():
    """Run Board model tests with detailed output."""
    # Print header
    print("\n" + "="*80)
    print(" RUNNING BOARD MODEL TESTS ".center(80, "="))
    print("="*80 + "\n")
    
    # Enable test debugging if needed
    os.environ["TEST_DEBUG"] = "true"
    
    # Find the test file
    tests_dir = Path(__file__).parent
    test_file = tests_dir / "unit" / "test_board_models.py"
    
    if not test_file.exists():
        print(f"Test file not found: {test_file}")
        return 1
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = loader.discover(start_dir=str(tests_dir / "unit"), pattern="test_board_models.py")
    
    # Create a text test runner with verbose output
    runner = unittest.TextTestRunner(verbosity=2)
    
    # Run the tests
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "="*80)
    print(" TEST RESULTS ".center(80, "="))
    print("="*80)
    print(f"Tests run: {result.testsRun}")
    print(f"Errors: {len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Skipped: {len(result.skipped)}")
    
    if result.wasSuccessful():
        print("\n" + "="*80)
        print(" ALL TESTS PASSED SUCCESSFULLY ".center(80, "="))
        print("="*80 + "\n")
        return 0
    else:
        print("\n" + "="*80)
        print(" TESTS FAILED ".center(80, "="))
        print("="*80 + "\n")
        return 1

if __name__ == "__main__":
    sys.exit(run_board_model_tests())
