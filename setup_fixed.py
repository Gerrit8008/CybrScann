#!/usr/bin/env python3
"""
Setup script for CybrScan application
Creates default admin user and initializes the database
"""

import os
import sys
from auth_utils_fixed import create_admin_user, get_db_connection
import logging

def setup_admin():
    """Create default admin user"""
    print("Setting up CybrScan Admin User...")
    
    # Check if admin already exists
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) as count FROM users WHERE role = 'admin'")
        admin_count = cursor.fetchone()['count']
        conn.close()
        
        if admin_count > 0:
            print("Admin user already exists. Skipping setup.")
            return True
    except Exception as e:
        print(f"Error checking for existing admin: {e}")
        return False
    
    # Get admin credentials
    username = input("Enter admin username (default: admin): ").strip() or "admin"
    email = input("Enter admin email: ").strip()
    
    if not email:
        print("Email is required!")
        return False
    
    password = input("Enter admin password: ").strip()
    if not password:
        print("Password is required!")
        return False
    
    full_name = input("Enter admin full name (optional): ").strip() or None
    
    # Create admin user
    result = create_admin_user(username, email, password, full_name)
    
    if result['status'] == 'success':
        print(f"✅ Admin user '{username}' created successfully!")
        print(f"Admin ID: {result['user_id']}")
        return True
    else:
        print(f"❌ Error creating admin user: {result['message']}")
        return False

def verify_database():
    """Verify database setup"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if all tables exist
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        
        required_tables = ['users', 'clients', 'deployed_scanners', 'scan_history', 'sessions', 'customizations', 'audit_log']
        missing_tables = [table for table in required_tables if table not in tables]
        
        if missing_tables:
            print(f"❌ Missing tables: {missing_tables}")
            print("Please run the main application first to initialize the database.")
            return False
        
        print("✅ Database tables verified successfully")
        
        # Show statistics
        cursor.execute("SELECT COUNT(*) as count FROM users")
        user_count = cursor.fetchone()['count']
        
        cursor.execute("SELECT COUNT(*) as count FROM clients")
        client_count = cursor.fetchone()['count']
        
        cursor.execute("SELECT COUNT(*) as count FROM deployed_scanners")
        scanner_count = cursor.fetchone()['count']
        
        conn.close()
        
        print(f"📊 Database Statistics:")
        print(f"   Users: {user_count}")
        print(f"   Clients: {client_count}")
        print(f"   Scanners: {scanner_count}")
        
        return True
        
    except Exception as e:
        print(f"❌ Database verification failed: {e}")
        return False

def main():
    """Main setup function"""
    print("🚀 CybrScan Setup Script")
    print("=" * 50)
    
    # Verify database
    if not verify_database():
        print("\n❌ Database setup failed. Please check the error messages above.")
        sys.exit(1)
    
    # Setup admin user
    if not setup_admin():
        print("\n❌ Admin setup failed. Please check the error messages above.")
        sys.exit(1)
    
    print("\n🎉 Setup completed successfully!")
    print("\nYou can now:")
    print("1. Run the application: python app_fixed.py")
    print("2. Login with your admin credentials")
    print("3. Access the admin dashboard at: http://localhost:5000/admin/dashboard")
    print("4. Create client accounts and scanners")

if __name__ == '__main__':
    main()