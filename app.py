"""
Patient Health Data Management System (PHMS)
Main Flask Application
"""
from flask import Flask, render_template, session, redirect, url_for
from pymongo import MongoClient
from config import Config
import os

# Import route initializers
from routes.auth import init_auth_routes
from routes.admin_routes import init_admin_routes
from routes.patient_routes import init_patient_routes
from routes.record_routes import init_record_routes

# Create Flask app
app = Flask(__name__)
app.config.from_object(Config)

# Set up MongoDB connection with Vercel-compatible settings
# Add SSL/TLS parameters to avoid handshake errors in serverless environment
mongo_client = MongoClient(
    Config.MONGODB_URI,
    serverSelectionTimeoutMS=5000,  # Shorter timeout for serverless
    connectTimeoutMS=10000,
    socketTimeoutMS=10000,
    tls=True,  # Explicitly enable TLS
    tlsAllowInvalidCertificates=False,  # Keep certificates valid
    retryWrites=True,
    w='majority'
)
db = mongo_client[Config.DATABASE_NAME]

# Initialize and register blueprints
auth_bp = init_auth_routes(db)
admin_bp = init_admin_routes(db)
patients_bp = init_patient_routes(db)
records_bp = init_record_routes(db)

app.register_blueprint(auth_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(patients_bp)
app.register_blueprint(records_bp)

# Ensure upload folder exists
os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)

# Landing page route
@app.route('/')
def landing():
    """Public landing page"""
    # If already logged in, redirect to dashboard
    if 'admin_id' in session:
        return redirect(url_for('patients.dashboard'))
    return render_template('landing.html')

# Error handlers
@app.errorhandler(404)
def not_found(error):
    """404 error handler"""
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    """500 error handler"""
    return render_template('500.html'), 500

# Context processor to make admin info available in all templates
@app.context_processor
def inject_user():
    """Inject admin info into all templates"""
    return {
        'admin_name': session.get('admin_name'),
        'admin_id': session.get('admin_id'),
        'is_logged_in': 'admin_id' in session
    }

if __name__ == '__main__':
    print("=" * 60)
    print("Patient Health Data Management System (PHMS)")
    print("=" * 60)
    print(f"Database: {Config.DATABASE_NAME}")
    print(f"MongoDB URI: {Config.MONGODB_URI}")
    print(f"Upload Folder: {Config.UPLOAD_FOLDER}")
    print(f"Gemini API Configured: {'Yes' if Config.GEMINI_API_KEY else 'No'}")
    print("=" * 60)
    print("Starting server on http://localhost:5000")
    print("=" * 60)
    
    # app.run(debug=True, host='0.0.0.0', port=5000)
    app.run()
