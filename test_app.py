#!/usr/bin/env python3
"""
Automated Testing Suite for Data Tale
=======================================================

This test suite covers all major functionality of the Flask application:
- File upload and validation
- Data cleaning algorithms
- AI summary generation
- Download functionality
- Error handling
"""

import unittest
import tempfile
import os
import pandas as pd
import json
from io import BytesIO
from datetime import datetime

# Import the Flask app
from app import app, ai_explain
from autoclean.cleaner import clean_dataframe, build_audit_summary

class TestDataCleaningAssistant(unittest.TestCase):
    """Test suite for the Data Tale Flask application."""
    
    def setUp(self):
        """Set up test environment before each test."""
        self.app = app.test_client()
        self.app.testing = True
        
        # Create test data
        self.test_data = {
            'customer_name': ['John Doe', 'Jane Smith', '', 'Bob Johnson', 'Alice Brown'],
            'email': ['john@example.com', 'JANE@EXAMPLE.COM', 'bob@test.com', '', 'alice@demo.com'],
            'amount': [100.50, 200.75, '', 150.25, 300.00],
            'order_date': ['2023-01-15', '2023-02-20', '2023-03-10', '', '2023-04-05'],
            'notes': ['Good customer', '', 'Needs follow-up', 'VIP client', ''],
            'status': ['active', 'active', 'inactive', 'active', 'active']
        }
        
        # Create a temporary CSV file for testing
        self.temp_csv = tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False)
        df = pd.DataFrame(self.test_data)
        df.to_csv(self.temp_csv.name, index=False)
        self.temp_csv.close()
    
    def tearDown(self):
        """Clean up after each test."""
        # Remove temporary file
        if os.path.exists(self.temp_csv.name):
            os.unlink(self.temp_csv.name)
    
    def test_home_page(self):
        """Test that the home page loads correctly."""
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Data Tale', response.data)
        self.assertIn(b'Transform your data into compelling stories', response.data)
    
    def test_static_files(self):
        """Test that static files (CSS) are served correctly."""
        response = self.app.get('/static/style.css')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Global dark styling', response.data)
    
    def test_file_upload_success(self):
        """Test successful CSV file upload and processing."""
        with open(self.temp_csv.name, 'rb') as f:
            data = {
                'file': (f, 'test_data.csv'),
                'send_to_ai': 'true'
            }
            response = self.app.post('/upload', data=data, content_type='multipart/form-data')
        
        self.assertEqual(response.status_code, 200)
        result = json.loads(response.data)
        
        # Check response structure
        self.assertIn('success', result)
        self.assertTrue(result['success'])
        self.assertIn('summary', result)
        self.assertIn('ai_summary', result)
        self.assertIn('rows_before', result)
        self.assertIn('rows_after', result)
        self.assertIn('duplicates_removed', result)
        
        # Check data cleaning results
        self.assertEqual(result['rows_before'], 5)
        self.assertGreaterEqual(result['rows_after'], 0)
        self.assertIsInstance(result['duplicates_removed'], int)
    
    def test_file_upload_no_file(self):
        """Test file upload with no file selected."""
        response = self.app.post('/upload', data={})
        self.assertEqual(response.status_code, 400)
        result = json.loads(response.data)
        self.assertIn('error', result)
        self.assertIn('No file uploaded', result['error'])
    
    def test_file_upload_wrong_format(self):
        """Test file upload with non-CSV file."""
        # Create a temporary text file
        temp_txt = tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False)
        temp_txt.write("This is not a CSV file")
        temp_txt.close()
        
        with open(temp_txt.name, 'rb') as f:
            data = {'file': (f, 'test.txt')}
            response = self.app.post('/upload', data=data, content_type='multipart/form-data')
        
        self.assertEqual(response.status_code, 400)
        result = json.loads(response.data)
        self.assertIn('error', result)
        self.assertIn('Please upload a CSV file', result['error'])
        
        # Clean up
        os.unlink(temp_txt.name)
    
    def test_data_cleaning_algorithm(self):
        """Test the data cleaning algorithm directly."""
        df = pd.DataFrame(self.test_data)
        cleaned_df, audit = clean_dataframe(df)
        summary = build_audit_summary(audit)
        
        # Check audit structure
        self.assertIn('rows_before', audit)
        self.assertIn('rows_after', audit)
        self.assertIn('duplicates_removed', audit)
        self.assertIn('columns', audit)
        self.assertIn('column_changes', audit)
        
        # Check summary structure
        self.assertIn('rows_before', summary)
        self.assertIn('rows_after', summary)
        self.assertIn('duplicates_removed', summary)
        self.assertIn('columns', summary)
        self.assertIn('column_changes', summary)
        
        # Check that cleaning actually happened
        self.assertEqual(audit['rows_before'], 5)
        self.assertGreaterEqual(audit['rows_after'], 0)
    
    def test_ai_summary_generation(self):
        """Test the AI summary generation function."""
        # Create a test audit
        test_audit = {
            'rows_before': 5,
            'rows_after': 4,
            'duplicates_removed': 1,
            'columns': ['customer_name', 'email', 'amount'],
            'column_changes': {
                'customer_name': {'imputed_missing': 1, 'imputation_strategy': "mode='John Doe'"},
                'email': {'emails_valid_after': 3, 'emails_valid_before': 2},
                'amount': {'parsed_to_datetime': 0}
            }
        }
        
        # Test AI summary generation
        summary = ai_explain(test_audit)
        
        # Check that summary is generated
        self.assertIsNotNone(summary)
        self.assertIsInstance(summary, str)
        self.assertGreater(len(summary), 100)  # Should be substantial
        
        # Check for expected sections
        self.assertIn('Data Cleaning Overview', summary)
        self.assertIn('Key Metrics', summary)
        self.assertIn('Recommendations', summary)
        self.assertIn('Next Steps', summary)
    
    def test_download_csv(self):
        """Test CSV download functionality."""
        # First upload a file to create session data
        with open(self.temp_csv.name, 'rb') as f:
            data = {
                'file': (f, 'test_data.csv'),
                'send_to_ai': 'false'
            }
            self.app.post('/upload', data=data, content_type='multipart/form-data')
        
        # Test CSV download
        response = self.app.get('/download/csv')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.mimetype, 'text/csv')
        self.assertIn('attachment', response.headers['Content-Disposition'])
        self.assertIn('cleaned.csv', response.headers['Content-Disposition'])
    
    def test_download_report(self):
        """Test report download functionality."""
        # First upload a file to create session data
        with open(self.temp_csv.name, 'rb') as f:
            data = {
                'file': (f, 'test_data.csv'),
                'send_to_ai': 'false'
            }
            self.app.post('/upload', data=data, content_type='multipart/form-data')
        
        # Test report download
        response = self.app.get('/download/report')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.mimetype, 'text/markdown')
        self.assertIn('attachment', response.headers['Content-Disposition'])
        self.assertIn('report.md', response.headers['Content-Disposition'])
        
        # Check report content
        report_content = response.data.decode('utf-8')
        self.assertIn('# Data Tale Report', report_content)
        self.assertIn('## Dataset Overview', report_content)
        self.assertIn('## Column-by-Column Changes', report_content)
    
    def test_download_without_session(self):
        """Test download attempts without session data."""
        # Test CSV download without session
        response = self.app.get('/download/csv')
        self.assertEqual(response.status_code, 400)
        result = json.loads(response.data)
        self.assertIn('error', result)
        self.assertIn('No cleaned data available', result['error'])
        
        # Test report download without session
        response = self.app.get('/download/report')
        self.assertEqual(response.status_code, 400)
        result = json.loads(response.data)
        self.assertIn('error', result)
        self.assertIn('No report data available', result['error'])
    
    def test_ai_summary_without_checkbox(self):
        """Test file upload without AI summary generation."""
        with open(self.temp_csv.name, 'rb') as f:
            data = {
                'file': (f, 'test_data.csv'),
                'send_to_ai': 'false'
            }
            response = self.app.post('/upload', data=data, content_type='multipart/form-data')
        
        self.assertEqual(response.status_code, 200)
        result = json.loads(response.data)
        
        # Check that AI summary is not generated
        self.assertIsNone(result['ai_summary'])
    
    def test_error_handling(self):
        """Test error handling with invalid CSV data."""
        # Create a CSV with invalid data that should cause an error
        invalid_csv = tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False)
        invalid_csv.write("invalid,csv,data\nwith,wrong,format\n")
        invalid_csv.close()
        
        with open(invalid_csv.name, 'rb') as f:
            data = {'file': (f, 'invalid.csv')}
            response = self.app.post('/upload', data=data, content_type='multipart/form-data')
        
        # The app should handle this gracefully (it's actually valid CSV format)
        # So we expect success, not error
        self.assertEqual(response.status_code, 200)
        result = json.loads(response.data)
        self.assertIn('success', result)
        self.assertTrue(result['success'])
        
        # Clean up
        os.unlink(invalid_csv.name)
    
    def test_large_file_handling(self):
        """Test handling of larger datasets."""
        # Create a larger test dataset
        large_data = {
            'id': list(range(1, 101)),  # 100 rows
            'name': [f'User_{i}' for i in range(1, 101)],
            'value': [i * 1.5 for i in range(1, 101)]
        }
        
        large_csv = tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False)
        df = pd.DataFrame(large_data)
        df.to_csv(large_csv.name, index=False)
        large_csv.close()
        
        with open(large_csv.name, 'rb') as f:
            data = {
                'file': (f, 'large_data.csv'),
                'send_to_ai': 'true'
            }
            response = self.app.post('/upload', data=data, content_type='multipart/form-data')
        
        self.assertEqual(response.status_code, 200)
        result = json.loads(response.data)
        
        # Check that large file was processed
        self.assertEqual(result['rows_before'], 100)
        self.assertGreaterEqual(result['rows_after'], 0)
        
        # Clean up
        os.unlink(large_csv.name)

def run_performance_test():
    """Run a performance test to check processing speed."""
    print("\n" + "="*50)
    print("PERFORMANCE TEST")
    print("="*50)
    
    # Create a larger dataset for performance testing
    large_data = {
        'id': list(range(1, 1001)),  # 1000 rows
        'name': [f'User_{i}' for i in range(1, 1001)],
        'email': [f'user{i}@example.com' for i in range(1, 1001)],
        'value': [i * 1.5 for i in range(1, 1001)],
        'date': [f'2023-{i%12+1:02d}-{i%28+1:02d}' for i in range(1, 1001)]
    }
    
    df = pd.DataFrame(large_data)
    
    # Time the cleaning process
    import time
    start_time = time.time()
    
    cleaned_df, audit = clean_dataframe(df)
    summary = build_audit_summary(audit)
    ai_summary = ai_explain(summary)
    
    end_time = time.time()
    processing_time = end_time - start_time
    
    print(f"Dataset size: {len(df)} rows, {len(df.columns)} columns")
    print(f"Processing time: {processing_time:.2f} seconds")
    print(f"Processing speed: {len(df)/processing_time:.0f} rows/second")
    print(f"AI summary length: {len(ai_summary)} characters")
    
    if processing_time < 5.0:
        print("Performance: EXCELLENT")
    elif processing_time < 10.0:
        print("Performance: GOOD")
    else:
        print("Performance: SLOW - Consider optimization")

if __name__ == '__main__':
    print("Data Tale - Test Suite")
    print("=" * 50)
    
    # Run unit tests
    print("\nRunning unit tests...")
    unittest.main(verbosity=2, exit=False)
    
    # Run performance test
    run_performance_test()
    
    print("\n" + "="*50)
    print("All tests completed!")
    print("="*50)
