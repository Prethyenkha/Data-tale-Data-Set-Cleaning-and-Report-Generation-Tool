#!/usr/bin/env python3
"""
Data Tale - AI-Powered Data Story Generator
==========================================

A modern web interface for automatic CSV data cleaning with AI-powered story generation.

Usage:
    python run.py

Then open http://localhost:5000 in your browser.
"""

import os
import sys
from app import app

def main():
    print("📊 Data Tale")
    print("=" * 40)
    print("Starting Flask web server...")
    print("Open your browser and go to: http://localhost:5000")
    print("Press Ctrl+C to stop the server")
    print("=" * 40)
    
    try:
        app.run(debug=True, host='0.0.0.0', port=5000)
    except KeyboardInterrupt:
        print("\n👋 Server stopped. Goodbye!")
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
