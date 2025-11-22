"""
Authentication routes
"""
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from models.admin import AdminModel

auth_bp = Blueprint('auth', __name__)

def init_auth_routes(db):
    """Initialize authentication routes with database"""
    admin_model = AdminModel(db)
    
    @auth_bp.route('/login', methods=['GET', 'POST'])
    def login():
        """Admin login page"""
        if request.method == 'POST':
            user_id = request.form.get('userId')
            password = request.form.get('password')
            
            # Validate inputs
            if not user_id or not password:
                flash('Please enter both User ID and password', 'error')
                return render_template('login.html')
            
            # Find admin
            admin = admin_model.find_by_user_id(user_id)
            
            # Verify password
            if admin and admin_model.verify_password(admin, password):
                # Check if active
                if not admin.get('isActive', True):
                    flash('This account has been deactivated', 'error')
                    return render_template('login.html')
                
                # Create session
                session['admin_id'] = str(admin['_id'])
                session['admin_name'] = admin['name']
                session['admin_user_id'] = admin['userId']
                
                flash(f'Welcome back, {admin["name"]}!', 'success')
                return redirect(url_for('patients.dashboard'))
            else:
                flash('Invalid User ID or password', 'error')
                return render_template('login.html')
        
        # GET request - show login form
        # If already logged in, redirect to dashboard
        if 'admin_id' in session:
            return redirect(url_for('patients.dashboard'))
        
        return render_template('login.html')
    
    @auth_bp.route('/logout')
    def logout():
        """Logout and clear session"""
        admin_name = session.get('admin_name', 'User')
        session.clear()
        flash(f'Goodbye, {admin_name}!', 'info')
        return redirect(url_for('landing'))
    
    return auth_bp
