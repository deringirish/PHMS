"""
Vercel Serverless Function Entry Point - Debug Version
"""
from flask import Flask, jsonify
import sys
import os
import traceback

# Create a simple test app first
app = Flask(__name__)

@app.route('/')
@app.route('/<path:path>')
def test(path=''):
    try:
        # Add parent directory to path
        current_dir = os.path.dirname(os.path.abspath(__file__))
        parent_dir = os.path.dirname(current_dir)
        sys.path.insert(0, parent_dir)
        
        # Try importing the real app
        from app import app as real_app
        
        return jsonify({
            'status': 'success',
            'message': 'App imported successfully! But serving from test handler.',
            'python_version': sys.version,
            'path': sys.path[:3]
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e),
            'type': type(e).__name__,
            'traceback': traceback.format_exc()
        }), 500

# Export for Vercel
application = app
