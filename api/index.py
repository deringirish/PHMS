"""
Vercel Serverless Function Entry Point
"""
import sys
import os

# Add parent directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

# Import the Flask app
from app import app

# Export for Vercel (WSGI handler looks for 'app' or 'application')
application = app
