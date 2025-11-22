"""
Decorators for route protection
"""
from functools import wraps
from flask import session, redirect, url_for, flash

def login_required(f):
    """
    Decorator to require admin login for routes
    
    Usage:
        @app.route('/protected')
        @login_required
        def protected_route():
            return 'This is protected'
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'admin_id' not in session:
            flash('Please log in to access this page.', 'error')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function
