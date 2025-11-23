"""
Vercel Serverless Function Entry Point
"""
import sys
import os

# Add parent directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

# Try to import and handle errors gracefully
try:
    from app import app
    application = app
except Exception as e:
    # If there's an error, create a simple Flask app that shows the error
    from flask import Flask, jsonify
    app = Flask(__name__)
    application = app
    
    @app.route('/')
    @app.route('/<path:path>')
    def error_handler(path=''):
        return jsonify({
            'error': 'Application failed to initialize',
            'message': str(e),
            'type': type(e).__name__
        }), 500
