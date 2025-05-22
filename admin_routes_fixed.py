# admin_routes_fixed.py
from flask import Blueprint, render_template, redirect, url_for, session, request, flash, jsonify
import sqlite3
import logging
from datetime import datetime
import os

# Create admin blueprint
admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

# Database path
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'cybrscan.db')

def get_db_connection():
    """Get database connection"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def admin_required(f):
    """Decorator to require admin authentication"""
    def decorated_function(*args, **kwargs):
        session_token = session.get('session_token')
        
        if not session_token:
            flash('Please log in to access this page', 'danger')
            return redirect(url_for('auth.login', next=request.url))
        
        # Verify session and get user info
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT u.*, s.session_token 
            FROM users u 
            JOIN sessions s ON u.id = s.user_id 
            WHERE s.session_token = ? AND s.expires_at > ? AND u.active = 1
        ''', (session_token, datetime.now().isoformat()))
        
        user_data = cursor.fetchone()
        conn.close()
        
        if not user_data or user_data['role'] != 'admin':
            flash('You need administrative privileges to access this page', 'danger')
            return redirect(url_for('auth.login'))
        
        # Convert to dict and pass to function
        user = dict(user_data)
        kwargs['user'] = user
        return f(*args, **kwargs)
    
    decorated_function.__name__ = f.__name__
    return decorated_function

@admin_bp.route('/dashboard')
@admin_required
def dashboard(user):
    """Admin dashboard"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get dashboard statistics
        cursor.execute('SELECT COUNT(*) as total_clients FROM clients WHERE active = 1')
        total_clients = cursor.fetchone()['total_clients']
        
        cursor.execute('SELECT COUNT(*) as active_scans FROM scan_history WHERE status = "running"')
        active_scans = cursor.fetchone()['active_scans']
        
        cursor.execute('SELECT COUNT(*) as deployed_scanners FROM deployed_scanners WHERE deploy_status = "deployed"')
        deployed_scanners = cursor.fetchone()['deployed_scanners']
        
        # Get recent clients
        cursor.execute('''
            SELECT c.*, u.username 
            FROM clients c 
            LEFT JOIN users u ON c.user_id = u.id 
            WHERE c.active = 1 
            ORDER BY c.created_at DESC 
            LIMIT 5
        ''')
        recent_clients = [dict(row) for row in cursor.fetchall()]
        
        # Get recent activities
        cursor.execute('''
            SELECT al.*, u.username 
            FROM audit_log al 
            LEFT JOIN users u ON al.user_id = u.id 
            ORDER BY al.timestamp DESC 
            LIMIT 10
        ''')
        recent_activities = [dict(row) for row in cursor.fetchall()]
        
        # Get recent logins
        cursor.execute('''
            SELECT u.username, u.email, u.role, s.created_at as timestamp, s.ip_address 
            FROM users u 
            JOIN sessions s ON u.id = s.user_id 
            ORDER BY s.created_at DESC 
            LIMIT 10
        ''')
        recent_logins = [dict(row) for row in cursor.fetchall()]
        
        # Get deployed scanners for the table
        cursor.execute('''
            SELECT ds.*, c.business_name, c.business_domain 
            FROM deployed_scanners ds 
            JOIN clients c ON ds.client_id = c.id 
            ORDER BY ds.deploy_date DESC
        ''')
        deployed_scanners_list = [dict(row) for row in cursor.fetchall()]
        
        conn.close()
        
        dashboard_stats = {
            'total_clients': total_clients,
            'active_scans': active_scans,
            'deployed_scanners': deployed_scanners,
            'monthly_revenue': 4250  # Placeholder
        }
        
        return render_template(
            'admin/admin-dashboard.html',
            user=user,
            dashboard_stats=dashboard_stats,
            recent_clients=recent_clients,
            recent_activities=recent_activities,
            recent_logins=recent_logins,
            deployed_scanners=deployed_scanners_list
        )
        
    except Exception as e:
        logging.error(f"Error in admin dashboard: {e}")
        flash(f'Error loading dashboard: {str(e)}', 'danger')
        return render_template('admin/error.html', error=str(e))

@admin_bp.route('/clients')
@admin_required
def clients(user):
    """Client management page"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get all clients with user information
        cursor.execute('''
            SELECT c.*, u.username, u.email as user_email, u.last_login
            FROM clients c 
            LEFT JOIN users u ON c.user_id = u.id 
            WHERE c.active = 1 
            ORDER BY c.created_at DESC
        ''')
        clients_list = [dict(row) for row in cursor.fetchall()]
        
        conn.close()
        
        return render_template(
            'admin/client-management.html',
            user=user,
            clients=clients_list
        )
        
    except Exception as e:
        logging.error(f"Error in admin clients: {e}")
        flash(f'Error loading clients: {str(e)}', 'danger')
        return render_template('admin/error.html', error=str(e))

@admin_bp.route('/clients/<int:client_id>')
@admin_required
def client_view(user, client_id):
    """View client details"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get client information
        cursor.execute('''
            SELECT c.*, u.username, u.email as user_email, u.last_login
            FROM clients c 
            LEFT JOIN users u ON c.user_id = u.id 
            WHERE c.id = ? AND c.active = 1
        ''', (client_id,))
        client = cursor.fetchone()
        
        if not client:
            flash('Client not found', 'danger')
            return redirect(url_for('admin.clients'))
        
        client = dict(client)
        
        # Get client's scanners
        cursor.execute('''
            SELECT * FROM deployed_scanners 
            WHERE client_id = ? 
            ORDER BY deploy_date DESC
        ''', (client_id,))
        scanners = [dict(row) for row in cursor.fetchall()]
        
        # Get client's scan history
        cursor.execute('''
            SELECT * FROM scan_history 
            WHERE client_id = ? 
            ORDER BY timestamp DESC 
            LIMIT 20
        ''', (client_id,))
        scan_history = [dict(row) for row in cursor.fetchall()]
        
        conn.close()
        
        return render_template(
            'admin/client-view.html',
            user=user,
            client=client,
            scanners=scanners,
            scan_history=scan_history
        )
        
    except Exception as e:
        logging.error(f"Error viewing client {client_id}: {e}")
        flash(f'Error loading client details: {str(e)}', 'danger')
        return redirect(url_for('admin.clients'))

@admin_bp.route('/subscriptions')
@admin_required
def subscriptions(user):
    """Subscription management page"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get subscription statistics
        cursor.execute('''
            SELECT subscription_level, COUNT(*) as count
            FROM clients 
            WHERE active = 1 
            GROUP BY subscription_level
        ''')
        subscription_stats = {row['subscription_level']: row['count'] for row in cursor.fetchall()}
        
        # Get all clients with subscription info
        cursor.execute('''
            SELECT c.*, u.username
            FROM clients c 
            LEFT JOIN users u ON c.user_id = u.id 
            WHERE c.active = 1 
            ORDER BY c.subscription_level, c.created_at DESC
        ''')
        clients_list = [dict(row) for row in cursor.fetchall()]
        
        conn.close()
        
        return render_template(
            'admin/subscription-management.html',
            user=user,
            subscription_stats=subscription_stats,
            clients=clients_list
        )
        
    except Exception as e:
        logging.error(f"Error in subscriptions: {e}")
        flash(f'Error loading subscriptions: {str(e)}', 'danger')
        return render_template('admin/error.html', error=str(e))

@admin_bp.route('/reports')
@admin_required
def reports(user):
    """Reports dashboard page"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get scan statistics
        cursor.execute('''
            SELECT 
                COUNT(*) as total_scans,
                COUNT(CASE WHEN status = 'completed' THEN 1 END) as completed_scans,
                COUNT(CASE WHEN status = 'running' THEN 1 END) as running_scans,
                COUNT(CASE WHEN status = 'failed' THEN 1 END) as failed_scans
            FROM scan_history
        ''')
        scan_stats = dict(cursor.fetchone())
        
        # Get recent scans
        cursor.execute('''
            SELECT sh.*, c.business_name
            FROM scan_history sh
            JOIN clients c ON sh.client_id = c.id
            ORDER BY sh.timestamp DESC
            LIMIT 20
        ''')
        recent_scans = [dict(row) for row in cursor.fetchall()]
        
        conn.close()
        
        return render_template(
            'admin/reports-dashboard.html',
            user=user,
            scan_stats=scan_stats,
            recent_scans=recent_scans
        )
        
    except Exception as e:
        logging.error(f"Error in reports: {e}")
        flash(f'Error loading reports: {str(e)}', 'danger')
        return render_template('admin/error.html', error=str(e))

@admin_bp.route('/settings')
@admin_required
def settings(user):
    """Settings dashboard page"""
    return render_template('admin/settings-dashboard.html', user=user)

@admin_bp.route('/scanners')
@admin_required
def scanners(user):
    """Scanner management page"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get all deployed scanners with client info
        cursor.execute('''
            SELECT ds.*, c.business_name, c.business_domain, c.contact_email
            FROM deployed_scanners ds
            JOIN clients c ON ds.client_id = c.id
            ORDER BY ds.deploy_date DESC
        ''')
        scanners_list = [dict(row) for row in cursor.fetchall()]
        
        conn.close()
        
        return render_template(
            'admin/scanner-management.html',
            user=user,
            deployed_scanners={'scanners': scanners_list}
        )
        
    except Exception as e:
        logging.error(f"Error in scanners: {e}")
        flash(f'Error loading scanners: {str(e)}', 'danger')
        return render_template('admin/error.html', error=str(e))

@admin_bp.route('/scanners/<int:scanner_id>/view')
@admin_required
def scanner_view(user, scanner_id):
    """View scanner details"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT ds.*, c.business_name, c.business_domain, c.contact_email
            FROM deployed_scanners ds
            JOIN clients c ON ds.client_id = c.id
            WHERE ds.id = ?
        ''', (scanner_id,))
        
        scanner = cursor.fetchone()
        if not scanner:
            flash('Scanner not found', 'danger')
            return redirect(url_for('admin.scanners'))
        
        scanner = dict(scanner)
        
        # Get scan history for this scanner
        cursor.execute('''
            SELECT * FROM scan_history
            WHERE scanner_id = ?
            ORDER BY timestamp DESC
            LIMIT 20
        ''', (scanner_id,))
        scan_history = [dict(row) for row in cursor.fetchall()]
        
        conn.close()
        
        return render_template(
            'admin/scanner-view.html',
            user=user,
            scanner=scanner,
            scan_history=scan_history
        )
        
    except Exception as e:
        logging.error(f"Error viewing scanner {scanner_id}: {e}")
        flash(f'Error loading scanner details: {str(e)}', 'danger')
        return redirect(url_for('admin.scanners'))

# API Routes for dashboard data
@admin_bp.route('/api/dashboard-stats')
@admin_required
def api_dashboard_stats(user):
    """API endpoint for dashboard statistics"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get various statistics
        stats = {}
        
        cursor.execute('SELECT COUNT(*) as count FROM clients WHERE active = 1')
        stats['total_clients'] = cursor.fetchone()['count']
        
        cursor.execute('SELECT COUNT(*) as count FROM scan_history WHERE status = "running"')
        stats['active_scans'] = cursor.fetchone()['count']
        
        cursor.execute('SELECT COUNT(*) as count FROM deployed_scanners WHERE deploy_status = "deployed"')
        stats['deployed_scanners'] = cursor.fetchone()['count']
        
        cursor.execute('SELECT COUNT(*) as count FROM scan_history WHERE DATE(timestamp) = DATE("now")')
        stats['todays_scans'] = cursor.fetchone()['count']
        
        conn.close()
        
        return jsonify({
            'status': 'success',
            'data': stats
        })
        
    except Exception as e:
        logging.error(f"Error getting dashboard stats: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500