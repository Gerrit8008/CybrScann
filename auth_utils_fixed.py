# auth_utils_fixed.py
import sqlite3
import hashlib
import secrets
import uuid
from datetime import datetime, timedelta
import logging
import os

# Database path
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'cybrscan.db')

def get_db_connection():
    """Get database connection"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def hash_password(password, salt=None):
    """Hash a password with salt"""
    if salt is None:
        salt = secrets.token_hex(16)
    
    # Combine password and salt
    password_salt = password + salt
    
    # Hash the combination
    password_hash = hashlib.sha256(password_salt.encode()).hexdigest()
    
    return password_hash, salt

def verify_password(password, stored_hash, salt):
    """Verify a password against stored hash"""
    password_hash, _ = hash_password(password, salt)
    return password_hash == stored_hash

def create_user(username, email, password, full_name=None, role='client'):
    """Create a new user"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if user already exists
        cursor.execute('SELECT id FROM users WHERE username = ? OR email = ?', (username, email))
        if cursor.fetchone():
            return {
                'status': 'error',
                'message': 'Username or email already exists'
            }
        
        # Hash the password
        password_hash, salt = hash_password(password)
        
        # Create user
        cursor.execute('''
            INSERT INTO users (username, email, password_hash, salt, role, full_name, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (username, email, password_hash, salt, role, full_name, datetime.now().isoformat()))
        
        user_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return {
            'status': 'success',
            'message': 'User created successfully',
            'user_id': user_id
        }
        
    except Exception as e:
        logging.error(f"Error creating user: {e}")
        return {
            'status': 'error',
            'message': str(e)
        }

def authenticate_user(username, password, ip_address=None, user_agent=None):
    """Authenticate a user and create session"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Find user by username or email
        cursor.execute('''
            SELECT * FROM users 
            WHERE (username = ? OR email = ?) AND active = 1
        ''', (username, username))
        
        user = cursor.fetchone()
        
        if not user:
            return {
                'status': 'error',
                'message': 'Invalid username or password'
            }
        
        user = dict(user)
        
        # Verify password
        if not verify_password(password, user['password_hash'], user['salt']):
            return {
                'status': 'error',
                'message': 'Invalid username or password'
            }
        
        # Create session token
        session_token = str(uuid.uuid4())
        expires_at = datetime.now() + timedelta(days=30)
        
        # Store session
        cursor.execute('''
            INSERT INTO sessions (user_id, session_token, created_at, expires_at, ip_address, user_agent)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (user['id'], session_token, datetime.now().isoformat(), expires_at.isoformat(), 
              ip_address, user_agent))
        
        # Update last login
        cursor.execute('''
            UPDATE users SET last_login = ? WHERE id = ?
        ''', (datetime.now().isoformat(), user['id']))
        
        conn.commit()
        conn.close()
        
        return {
            'status': 'success',
            'message': 'Authentication successful',
            'session_token': session_token,
            'user_id': user['id'],
            'username': user['username'],
            'email': user['email'],
            'role': user['role'],
            'full_name': user['full_name']
        }
        
    except Exception as e:
        logging.error(f"Error authenticating user: {e}")
        return {
            'status': 'error',
            'message': 'Authentication failed'
        }

def verify_session(session_token):
    """Verify a session token"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT u.*, s.expires_at
            FROM users u
            JOIN sessions s ON u.id = s.user_id
            WHERE s.session_token = ? AND u.active = 1
        ''', (session_token,))
        
        result = cursor.fetchone()
        
        if not result:
            return {
                'status': 'error',
                'message': 'Invalid session'
            }
        
        result = dict(result)
        
        # Check if session has expired
        expires_at = datetime.fromisoformat(result['expires_at'])
        if datetime.now() > expires_at:
            # Clean up expired session
            cursor.execute('DELETE FROM sessions WHERE session_token = ?', (session_token,))
            conn.commit()
            conn.close()
            return {
                'status': 'error',
                'message': 'Session expired'
            }
        
        conn.close()
        
        # Remove sensitive data
        del result['password_hash']
        del result['salt']
        del result['expires_at']
        
        return {
            'status': 'success',
            'user': result
        }
        
    except Exception as e:
        logging.error(f"Error verifying session: {e}")
        return {
            'status': 'error',
            'message': 'Session verification failed'
        }

def logout_user(session_token):
    """Logout a user by removing their session"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM sessions WHERE session_token = ?', (session_token,))
        conn.commit()
        conn.close()
        
        return {
            'status': 'success',
            'message': 'Logged out successfully'
        }
        
    except Exception as e:
        logging.error(f"Error logging out user: {e}")
        return {
            'status': 'error',
            'message': 'Logout failed'
        }

def create_admin_user(username, email, password, full_name=None):
    """Create an admin user"""
    return create_user(username, email, password, full_name, role='admin')

def register_client(user_id, client_data):
    """Register a client profile for a user"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Generate API key
        api_key = hashlib.sha256(f"{user_id}_{datetime.now().isoformat()}_{uuid.uuid4()}".encode()).hexdigest()
        
        # Create client record
        cursor.execute('''
            INSERT INTO clients 
            (user_id, business_name, business_domain, contact_email, contact_phone, 
             scanner_name, subscription_level, api_key, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, client_data['business_name'], client_data['business_domain'],
              client_data['contact_email'], client_data.get('contact_phone', ''),
              client_data.get('scanner_name', ''), client_data.get('subscription_level', 'basic'),
              api_key, datetime.now().isoformat()))
        
        client_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return {
            'status': 'success',
            'message': 'Client registered successfully',
            'client_id': client_id,
            'api_key': api_key
        }
        
    except Exception as e:
        logging.error(f"Error registering client: {e}")
        return {
            'status': 'error',
            'message': str(e)
        }

def clean_expired_sessions():
    """Clean up expired sessions"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM sessions WHERE expires_at < ?', (datetime.now().isoformat(),))
        deleted_count = cursor.rowcount
        
        conn.commit()
        conn.close()
        
        logging.info(f"Cleaned up {deleted_count} expired sessions")
        return deleted_count
        
    except Exception as e:
        logging.error(f"Error cleaning expired sessions: {e}")
        return 0

def get_user_by_id(user_id):
    """Get user by ID"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM users WHERE id = ? AND active = 1', (user_id,))
        user = cursor.fetchone()
        
        if not user:
            return {
                'status': 'error',
                'message': 'User not found'
            }
        
        user = dict(user)
        
        # Remove sensitive data
        del user['password_hash']
        del user['salt']
        
        conn.close()
        
        return {
            'status': 'success',
            'user': user
        }
        
    except Exception as e:
        logging.error(f"Error getting user by ID: {e}")
        return {
            'status': 'error',
            'message': str(e)
        }

def update_user_password(user_id, new_password):
    """Update user password"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Hash the new password
        password_hash, salt = hash_password(new_password)
        
        # Update password
        cursor.execute('''
            UPDATE users 
            SET password_hash = ?, salt = ? 
            WHERE id = ?
        ''', (password_hash, salt, user_id))
        
        conn.commit()
        conn.close()
        
        return {
            'status': 'success',
            'message': 'Password updated successfully'
        }
        
    except Exception as e:
        logging.error(f"Error updating password: {e}")
        return {
            'status': 'error',
            'message': str(e)
        }