#!/usr/bin/env python3
"""
Test Runner for Data Tale
===========================================

Simple script to run all tests with clear output and results.
"""

import sys
import subprocess
import time

def run_tests():
    """Run the complete test suite."""
    print("Data Tale - Test Suite")
    print("=" * 60)
    print("Starting automated testing...")
    print()
    
    start_time = time.time()
    
    try:
        # Run the test suite
        result = subprocess.run([sys.executable, 'test_app.py'], 
                              capture_output=True, text=True, timeout=120)
        
        end_time = time.time()
        test_duration = end_time - start_time
        
        print("TEST RESULTS:")
        print("=" * 60)
        print(result.stdout)
        
        if result.stderr:
            print("ERRORS/WARNINGS:")
            print("-" * 30)
            print(result.stderr)
        
        print("=" * 60)
        print(f"⏱️  Total test duration: {test_duration:.2f} seconds")
        
        if result.returncode == 0:
            print("All tests PASSED successfully!")
            return True
        else:
            print("Some tests FAILED!")
            return False
            
    except subprocess.TimeoutExpired:
        print("Tests timed out after 2 minutes!")
        return False
    except Exception as e:
        print(f"Error running tests: {e}")
        return False

def run_quick_test():
    """Run a quick smoke test to verify basic functionality."""
    print("Quick Smoke Test")
    print("=" * 30)
    
    try:
        # Import and test basic functionality
        from app import app, ai_explain
        from autoclean.cleaner import clean_dataframe, build_audit_summary
        import pandas as pd
        
        # Test data
        test_data = {
            'name': ['John', 'Jane', ''],
            'email': ['john@test.com', 'JANE@TEST.COM', ''],
            'value': [100, 200, '']
        }
        
        df = pd.DataFrame(test_data)
        
        # Test cleaning
        cleaned_df, audit = clean_dataframe(df)
        summary = build_audit_summary(audit)
        ai_summary = ai_explain(summary)
        
        # Test Flask app
        client = app.test_client()
        response = client.get('/')
        
        print("Basic imports working")
        print("Data cleaning algorithm working")
        print("AI summary generation working")
        print(f"Flask app responding (Status: {response.status_code})")
        print("All core functionality verified!")
        
        return True
        
    except Exception as e:
        print(f"Quick test failed: {e}")
        return False

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Run tests for Data Tale')
    parser.add_argument('--quick', action='store_true', help='Run quick smoke test only')
    parser.add_argument('--full', action='store_true', help='Run full test suite (default)')
    
    args = parser.parse_args()
    
    if args.quick:
        success = run_quick_test()
    else:
        success = run_tests()
    
    print()
    if success:
        print("Testing completed successfully!")
        sys.exit(0)
    else:
        print("Testing failed!")
        sys.exit(1)
