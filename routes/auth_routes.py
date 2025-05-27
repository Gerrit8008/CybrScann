"""
Authentication-related routes for CybrScan
Handles login, registration, and auth API endpoints
"""

from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for, flash
import os
import logging
import json
from datetime import datetime

# Create auth blueprint
auth_bp = Blueprint('auth', __name__)

# Configure logging
logger = logging.getLogger(__name__)


@auth_bp.route('/login')
def login():
    """Login page"""
    return render_template('auth/login.html')


@auth_bp.route('/register')
def register():
    """Registration page"""
    return render_template('auth/register.html')


@auth_bp.route('/logout')
def logout():
    """Logout user"""
    session.clear()
    flash('You have been logged out successfully', 'info')
    return redirect(url_for('main.landing_page'))


@auth_bp.route('/auth_status')
def auth_status():
    """Check authentication status"""
    try:
        # Check if user is logged in via session
        session_token = session.get('session_token')
        user_id = session.get('user_id')
        
        if session_token and user_id:
            # Verify session is still valid
            from client_db import verify_session
            result = verify_session(session_token)
            
            if result:
                # Handle different return formats
                if isinstance(result, dict):
                    user_data = result
                elif isinstance(result, tuple) and len(result) >= 2:
                    is_valid, user_data = result
                    if not is_valid:
                        return jsonify({'authenticated': False, 'user': None})
                else:
                    return jsonify({'authenticated': False, 'user': None})
                
                return jsonify({
                    'authenticated': True,
                    'user': {
                        'id': user_data.get('user_id'),
                        'username': user_data.get('username'),
                        'email': user_data.get('email'),
                        'role': user_data.get('role', 'client')
                    }
                })
        
        return jsonify({'authenticated': False, 'user': None})
        
    except Exception as e:
        logging.error(f"Error checking auth status: {e}")
        return jsonify({'authenticated': False, 'user': None, 'error': str(e)})


@auth_bp.route('/auth/api/login-stats')
def login_stats():
    """Get login statistics"""
    try:
        from client_db import get_db_connection
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get total users
        cursor.execute('SELECT COUNT(*) FROM users')
        total_users = cursor.fetchone()[0]
        
        # Get active sessions (sessions created in last 24 hours)
        cursor.execute('''
            SELECT COUNT(*) FROM sessions 
            WHERE created_at > datetime('now', '-1 day')
        ''')
        active_sessions = cursor.fetchone()[0]
        
        conn.close()
        
        return jsonify({
            'total_users': total_users,
            'active_sessions': active_sessions,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logging.error(f"Error getting login stats: {e}")
        return jsonify({
            'total_users': 0,
            'active_sessions': 0,
            'error': str(e)
        })


@auth_bp.route('/auth/api/check-username', methods=['POST'])
def check_username():
    """Check if username is available"""
    try:
        data = request.get_json()
        username = data.get('username', '').strip()
        
        if not username:
            return jsonify({'available': False, 'message': 'Username is required'})
        
        if len(username) < 3:
            return jsonify({'available': False, 'message': 'Username must be at least 3 characters'})
        
        from client_db import get_db_connection
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT id FROM users WHERE username = ?', (username,))
        existing_user = cursor.fetchone()
        conn.close()
        
        if existing_user:
            return jsonify({'available': False, 'message': 'Username is already taken'})
        else:
            return jsonify({'available': True, 'message': 'Username is available'})
            
    except Exception as e:
        logging.error(f"Error checking username: {e}")
        return jsonify({'available': False, 'message': 'Error checking username'})


@auth_bp.route('/auth/api/check-email', methods=['POST'])
def check_email():
    """Check if email is available"""
    try:
        data = request.get_json()
        email = data.get('email', '').strip().lower()
        
        if not email:
            return jsonify({'available': False, 'message': 'Email is required'})
        
        # Basic email validation
        import re
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            return jsonify({'available': False, 'message': 'Invalid email format'})
        
        from client_db import get_db_connection
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT id FROM users WHERE email = ?', (email,))
        existing_user = cursor.fetchone()
        conn.close()
        
        if existing_user:
            return jsonify({'available': False, 'message': 'Email is already registered'})
        else:
            return jsonify({'available': True, 'message': 'Email is available'})
            
    except Exception as e:
        logging.error(f"Error checking email: {e}")
        return jsonify({'available': False, 'message': 'Error checking email'})


@auth_bp.route('/emergency_login', methods=['GET', 'POST'])
def emergency_login():
    """Emergency login for development and testing"""
    if request.method == 'POST':
        try:
            username = request.form.get('username')
            password = request.form.get('password')
            
            if not username or not password:
                flash('Username and password are required', 'danger')
                return render_template('auth/emergency_login.html')
            
            # Try to authenticate
            from auth_utils import authenticate_user, create_session
            auth_result = authenticate_user(username, password)
            
            if auth_result['success']:
                user = auth_result['user']
                
                # Create session
                session_result = create_session(user['id'])
                if session_result['success']:
                    session['session_token'] = session_result['session_token']
                    session['user_id'] = user['id']
                    session['username'] = user['username']
                    session['role'] = user.get('role', 'client')
                    
                    # Redirect based on role
                    if user.get('role') == 'admin':
                        return redirect(url_for('admin.admin_dashboard'))
                    else:
                        return redirect(url_for('client.dashboard'))
                else:
                    flash('Error creating session', 'danger')
            else:
                flash(auth_result.get('message', 'Invalid credentials'), 'danger')
                
        except Exception as e:
            logging.error(f"Emergency login error: {e}")
            flash('Login error occurred', 'danger')
    
    return render_template('auth/emergency_login.html')


@auth_bp.route('/test_redirect')
def test_redirect():
    """Test redirect functionality"""
    next_url = request.args.get('next', '/')
    return f"Would redirect to: {next_url}"