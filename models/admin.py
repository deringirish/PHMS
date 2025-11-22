"""
Admin model and database operations
"""
import bcrypt
from datetime import datetime
from bson import ObjectId

class AdminModel:
    """Admin model for MongoDB operations"""
    
    def __init__(self, db):
        self.collection = db.admins
        self._ensure_indexes()
    
    def _ensure_indexes(self):
        """Create indexes for admin collection"""
        self.collection.create_index('userId', unique=True)
    
    def create_admin(self, user_id, name, password, secret_password):
        """
        Create a new admin account
        
        Args:
            user_id: Unique username or email
            name: Full name of admin
            password: Plain text password (will be hashed)
            secret_password: Secret password for admin operations
            
        Returns:
            The inserted admin ID or None if userId already exists
        """
        # Check if userId already exists
        if self.find_by_user_id(user_id):
            return None
        
        # Hash both passwords
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        secret_hash = bcrypt.hashpw(secret_password.encode('utf-8'), bcrypt.gensalt())
        
        admin = {
            'userId': user_id,
            'name': name,
            'passwordHash': password_hash,
            'secretPasswordHash': secret_hash,
            'isActive': True,
            'createdAt': datetime.utcnow(),
            'updatedAt': datetime.utcnow()
        }
        
        result = self.collection.insert_one(admin)
        return result.inserted_id
    
    def find_by_user_id(self, user_id):
        """Find admin by userId"""
        return self.collection.find_one({'userId': user_id})
    
    def find_by_id(self, admin_id):
        """Find admin by _id"""
        return self.collection.find_one({'_id': ObjectId(admin_id)})
    
    def verify_password(self, admin, password):
        """
        Verify admin password
        
        Args:
            admin: Admin document from database
            password: Plain text password to verify
            
        Returns:
            True if password matches, False otherwise
        """
        if not admin or not admin.get('passwordHash'):
            return False
        return bcrypt.checkpw(password.encode('utf-8'), admin['passwordHash'])
    
    def verify_secret_password(self, admin, secret_password):
        """
        Verify admin secret password
        
        Args:
            admin: Admin document from database
            secret_password: Plain text secret password to verify
            
        Returns:
            True if secret password matches, False otherwise
        """
        if not admin or not admin.get('secretPasswordHash'):
            return False
        return bcrypt.checkpw(secret_password.encode('utf-8'), admin['secretPasswordHash'])
    
    def get_all_admins(self):
        """Get all admins (excluding sensitive data)"""
        return list(self.collection.find(
            {},
            {'passwordHash': 0, 'secretPasswordHash': 0}
        ).sort('name', 1))
    
    def delete_admin(self, admin_id):
        """
        Delete an admin account
        
        Args:
            admin_id: The _id of the admin to delete
            
        Returns:
            True if deletion was successful, False otherwise
        """
        try:
            result = self.collection.delete_one({'_id': ObjectId(admin_id)})
            return result.deleted_count > 0
        except Exception as e:
            print(f"Error deleting admin: {e}")
            return False
