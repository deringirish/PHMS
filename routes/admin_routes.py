"""
Admin management routes
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from models.admin import AdminModel
from utils.decorators import login_required
from utils.validators import validate_admin_data

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

def init_admin_routes(db):
    """Initialize admin management routes with database"""
    admin_model = AdminModel(db)
    
    @admin_bp.route('/manage')
    @login_required
    def manage():
        """Admin management page"""
        admins = admin_model.get_all_admins()
        return render_template('admin_management.html', admins=admins)
    
    @admin_bp.route('/create', methods=['POST'])
    @login_required
    def create():
        """Create new admin"""
        data = {
            'userId': request.form.get('userId', '').strip(),
            'name': request.form.get('name', '').strip(),
            'password': request.form.get('password', ''),
            'secretPassword': request.form.get('secretPassword', '')
        }
        
        # Validate input
        is_valid, error_msg = validate_admin_data(data)
        if not is_valid:
            flash(error_msg, 'error')
            return redirect(url_for('admin.manage'))
        
        # Create admin
        admin_id = admin_model.create_admin(
            data['userId'],
            data['name'],
            data['password'],
            data['secretPassword']
        )
        
        if admin_id:
            flash(f'Admin "{data["name"]}" created successfully!', 'success')
        else:
            flash(f'User ID "{data["userId"]}" already exists', 'error')
        
        return redirect(url_for('admin.manage'))
    
    @admin_bp.route('/delete/<admin_id>', methods=['POST'])
    @login_required
    def delete(admin_id):
        """Delete an admin (cannot delete self)"""
        # Get the logged-in admin's ID from session
        logged_in_admin_id = session.get('admin_id')
        
        # Prevent self-deletion
        if admin_id == logged_in_admin_id:
            flash('You cannot delete your own account!', 'error')
            return redirect(url_for('admin.manage'))
        
        # Get admin details before deletion for the success message
        admin_to_delete = admin_model.find_by_id(admin_id)
        
        if not admin_to_delete:
            flash('Admin not found!', 'error')
            return redirect(url_for('admin.manage'))
        
        # Delete the admin
        if admin_model.delete_admin(admin_id):
            flash(f'Admin "{admin_to_delete["name"]}" has been deleted successfully!', 'success')
        else:
            flash('Failed to delete admin. Please try again.', 'error')
        
        return redirect(url_for('admin.manage'))
    
    return admin_bp
