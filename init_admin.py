"""
Initial Admin Setup Script
Run this once to create the first admin account
"""
from pymongo import MongoClient
from models.admin import AdminModel
from config import Config
import getpass

def create_initial_admin():
    """Interactive script to create the first admin"""
    print("=" * 60)
    print("PHMS - Initial Admin Setup")
    print("=" * 60)
    print()
    
    # Connect to MongoDB
    try:
        mongo_client = MongoClient(Config.MONGODB_URI)
        db = mongo_client[Config.DATABASE_NAME]
        admin_model = AdminModel(db)
        print(f"✓ Connected to MongoDB: {Config.DATABASE_NAME}")
        print()
    except Exception as e:
        print(f"✗ Failed to connect to MongoDB: {e}")
        return
    
    # Check if any admins already exist
    existing_admins = admin_model.get_all_admins()
    if existing_admins:
        print(f"⚠ Warning: {len(existing_admins)} admin(s) already exist:")
        for admin in existing_admins:
            print(f"  - {admin['name']} ({admin['userId']})")
        print()
        proceed = input("Do you want to create another admin? (yes/no): ").strip().lower()
        if proceed != 'yes':
            print("Setup cancelled.")
            return
        print()
    
    # Gather admin information
    print("Enter details for the new admin:")
    print()
    
    user_id = input("User ID (username or email): ").strip()
    if not user_id:
        print("✗ User ID is required")
        return
    
    # Check if userId already exists
    if admin_model.find_by_user_id(user_id):
        print(f"✗ User ID '{user_id}' already exists")
        return
    
    name = input("Full Name: ").strip()
    if not name:
        print("✗ Name is required")
        return
    
    password = getpass.getpass("Password (min 6 characters): ")
    if len(password) < 6:
        print("✗ Password must be at least 6 characters")
        return
    
    password_confirm = getpass.getpass("Confirm Password: ")
    if password != password_confirm:
        print("✗ Passwords do not match")
        return
    
    secret_password = getpass.getpass("Secret Password (for admin operations): ")
    if not secret_password:
        print("✗ Secret password is required")
        return
    
    print()
    print("Creating admin account...")
    
    # Create admin
    try:
        admin_id = admin_model.create_admin(user_id, name, password, secret_password)
        if admin_id:
            print()
            print("=" * 60)
            print("✓ Admin created successfully!")
            print("=" * 60)
            print(f"User ID: {user_id}")
            print(f"Name: {name}")
            print()
            print("You can now log in to PHMS using these credentials.")
            print("=" * 60)
        else:
            print("✗ Failed to create admin")
    except Exception as e:
        print(f"✗ Error creating admin: {e}")

if __name__ == '__main__':
    create_initial_admin()
