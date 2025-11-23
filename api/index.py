"""
Vercel Serverless Function Entry Point
This file is required for Vercel to run the Flask application as a serverless function.
"""
import sys
import os

# Add the parent directory to the path so we can import app
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app

# Vercel will use this 'app' object to handle requests
# The app is already configured in app.py with all routes and settings
