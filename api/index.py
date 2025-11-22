"""
Vercel Entry Point for PHMS Flask Application
"""
import sys
import os

# Add the parent directory to path so we can import app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the Flask app
from app import app

# Export for Vercel
# Vercel will use this as the WSGI application
if __name__ == "__main__":
    app.run()
