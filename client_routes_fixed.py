# client_routes_fixed.py
from flask import Blueprint, render_template, redirect, url_for, session, request, flash, jsonify
import sqlite3
import logging
from datetime import datetime
import os
import uuid

# Create client blueprint
client_bp = Blueprint('client', __name__, url_prefix='/client')

# Database path
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'cybrscan.db')

def get_db_connection():
    """Get database connection"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def client_required(f):
    """Decorator to require client authentication"""
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
        
        if not user_data:
            flash('Please log in to access this page', 'danger')
            return redirect(url_for('auth.login'))
        
        # Convert to dict and pass to function
        user = dict(user_data)
        kwargs['user'] = user
        return f(*args, **kwargs)
    
    decorated_function.__name__ = f.__name__
    return decorated_function

@client_bp.route('/dashboard')
@client_required
def dashboard(user):
    """Client dashboard"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get client information
        cursor.execute('''
            SELECT * FROM clients 
            WHERE user_id = ? AND active = 1
        ''', (user['id'],))
        user_client = cursor.fetchone()
        
        if user_client:
            user_client = dict(user_client)
            client_id = user_client['id']
        else:
            # Create a default client profile if none exists
            cursor.execute('''
                INSERT INTO clients (user_id, business_name, business_domain, contact_email, created_at)
                VALUES (?, ?, ?, ?, ?)
            ''', (user['id'], user.get('full_name', user['username']), 
                  user['email'].split('@')[1], user['email'], datetime.now().isoformat()))
            
            client_id = cursor.lastrowid
            conn.commit()
            
            # Get the newly created client
            cursor.execute('SELECT * FROM clients WHERE id = ?', (client_id,))
            user_client = dict(cursor.fetchone())
        
        # Get client's scanners
        cursor.execute('''
            SELECT * FROM deployed_scanners 
            WHERE client_id = ? 
            ORDER BY deploy_date DESC
        ''', (client_id,))
        scanners = [dict(row) for row in cursor.fetchall()]
        
        # Get scan statistics
        cursor.execute('''
            SELECT COUNT(*) as total_scans
            FROM scan_history 
            WHERE client_id = ?
        ''', (client_id,))
        total_scans = cursor.fetchone()['total_scans']
        
        cursor.execute('''
            SELECT COUNT(*) as critical_issues
            FROM scan_history 
            WHERE client_id = ? AND status = 'completed' AND issues_found > 5
        ''', (client_id,))
        critical_issues = cursor.fetchone()['critical_issues']
        
        cursor.execute('''
            SELECT AVG(security_score) as avg_score
            FROM scan_history 
            WHERE client_id = ? AND status = 'completed' AND security_score IS NOT NULL
        ''', (client_id,))
        avg_security_score = cursor.fetchone()['avg_score'] or 0
        
        # Get recent scan history
        cursor.execute('''
            SELECT sh.*, ds.scanner_name
            FROM scan_history sh
            LEFT JOIN deployed_scanners ds ON sh.scanner_id = ds.id
            WHERE sh.client_id = ?
            ORDER BY sh.timestamp DESC
            LIMIT 10
        ''', (client_id,))
        scan_history = [dict(row) for row in cursor.fetchall()]
        
        # Get recent activities (audit log entries for this client)
        cursor.execute('''
            SELECT * FROM audit_log
            WHERE entity_type = 'client' AND entity_id = ?
            ORDER BY timestamp DESC
            LIMIT 10
        ''', (client_id,))
        recent_activities = []
        for row in cursor.fetchall():
            activity = dict(row)
            activity['description'] = f"{activity['action']} on {activity['entity_type']}"
            recent_activities.append(activity)
        
        conn.close()
        
        # Calculate trends (placeholder logic)
        scan_trends = {
            'scanner_growth': 0,
            'scan_growth': 10 if total_scans > 0 else 0
        }
        
        return render_template(
            'client/client-dashboard.html',
            user=user,
            user_client=user_client,
            scanners=scanners,
            total_scans=total_scans,
            critical_issues=critical_issues,
            avg_security_score=int(avg_security_score),
            scan_history=scan_history,
            recent_activities=recent_activities,
            scan_trends=scan_trends,
            security_score_trend=5,  # Placeholder
            critical_issues_trend=-2,  # Placeholder
            scans_used=total_scans,
            scans_limit=50,
            scanner_limit=3,
            security_status='Good' if avg_security_score > 70 else 'Needs Attention'
        )
        
    except Exception as e:
        logging.error(f"Error in client dashboard: {e}")
        flash(f'Error loading dashboard: {str(e)}', 'danger')
        return render_template('client/client-dashboard.html', 
                               user=user, 
                               scanners=[], 
                               total_scans=0,
                               critical_issues=0,
                               avg_security_score=0,
                               scan_history=[],
                               recent_activities=[])

@client_bp.route('/scanners')
@client_required
def scanners(user):
    """Client scanners page"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get client information
        cursor.execute('''
            SELECT * FROM clients 
            WHERE user_id = ? AND active = 1
        ''', (user['id'],))
        user_client = cursor.fetchone()
        
        if not user_client:
            flash('Client profile not found', 'danger')
            return redirect(url_for('client.dashboard'))
        
        user_client = dict(user_client)
        client_id = user_client['id']
        
        # Get client's scanners
        cursor.execute('''
            SELECT * FROM deployed_scanners 
            WHERE client_id = ? 
            ORDER BY deploy_date DESC
        ''', (client_id,))
        scanners_list = [dict(row) for row in cursor.fetchall()]
        
        # Get scan statistics for each scanner
        for scanner in scanners_list:
            cursor.execute('''
                SELECT COUNT(*) as total_scans, AVG(security_score) as avg_score
                FROM scan_history 
                WHERE scanner_id = ? AND status = 'completed'
            ''', (scanner['id'],))
            stats = cursor.fetchone()
            scanner['total_scans'] = stats['total_scans'] or 0
            scanner['avg_security_score'] = int(stats['avg_score'] or 0)
            
            # Get last scan date
            cursor.execute('''
                SELECT timestamp FROM scan_history 
                WHERE scanner_id = ? 
                ORDER BY timestamp DESC 
                LIMIT 1
            ''', (scanner['id'],))
            last_scan = cursor.fetchone()
            scanner['last_scan'] = last_scan['timestamp'] if last_scan else 'Never'
        
        conn.close()
        
        return render_template(
            'client/scanners.html',
            user=user,
            user_client=user_client,
            scanners=scanners_list
        )
        
    except Exception as e:
        logging.error(f"Error in client scanners: {e}")
        flash(f'Error loading scanners: {str(e)}', 'danger')
        return redirect(url_for('client.dashboard'))

@client_bp.route('/scanners/<int:scanner_id>')
@client_required
def scanner_view(user, scanner_id):
    """View scanner details"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get client information to verify ownership
        cursor.execute('''
            SELECT c.* FROM clients c 
            WHERE c.user_id = ? AND c.active = 1
        ''', (user['id'],))
        user_client = cursor.fetchone()
        
        if not user_client:
            flash('Client profile not found', 'danger')
            return redirect(url_for('client.dashboard'))
        
        client_id = user_client['id']
        
        # Get scanner information
        cursor.execute('''
            SELECT * FROM deployed_scanners 
            WHERE id = ? AND client_id = ?
        ''', (scanner_id, client_id))
        scanner = cursor.fetchone()
        
        if not scanner:
            flash('Scanner not found', 'danger')
            return redirect(url_for('client.scanners'))
        
        scanner = dict(scanner)
        
        # Get scan history for this scanner
        cursor.execute('''
            SELECT * FROM scan_history
            WHERE scanner_id = ?
            ORDER BY timestamp DESC
            LIMIT 20
        ''', (scanner_id,))
        scan_history = [dict(row) for row in cursor.fetchall()]
        
        # Get scanner statistics
        cursor.execute('''
            SELECT 
                COUNT(*) as total_scans,
                COUNT(CASE WHEN status = 'completed' THEN 1 END) as completed_scans,
                AVG(security_score) as avg_score,
                SUM(issues_found) as total_issues
            FROM scan_history
            WHERE scanner_id = ?
        ''', (scanner_id,))
        stats = dict(cursor.fetchone())
        
        conn.close()
        
        return render_template(
            'client/scanner-view.html',
            user=user,
            scanner=scanner,
            scan_history=scan_history,
            stats=stats
        )
        
    except Exception as e:
        logging.error(f"Error viewing scanner {scanner_id}: {e}")
        flash(f'Error loading scanner details: {str(e)}', 'danger')
        return redirect(url_for('client.scanners'))

@client_bp.route('/reports')
@client_required
def reports(user):
    """Client reports page"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get client information
        cursor.execute('''
            SELECT * FROM clients 
            WHERE user_id = ? AND active = 1
        ''', (user['id'],))
        user_client = cursor.fetchone()
        
        if not user_client:
            flash('Client profile not found', 'danger')
            return redirect(url_for('client.dashboard'))
        
        client_id = user_client['id']
        
        # Get all scan reports for this client
        cursor.execute('''
            SELECT sh.*, ds.scanner_name
            FROM scan_history sh
            LEFT JOIN deployed_scanners ds ON sh.scanner_id = ds.id
            WHERE sh.client_id = ?
            ORDER BY sh.timestamp DESC
        ''', (client_id,))
        reports_list = [dict(row) for row in cursor.fetchall()]
        
        conn.close()
        
        return render_template(
            'client/reports.html',
            user=user,
            reports=reports_list
        )
        
    except Exception as e:
        logging.error(f"Error in client reports: {e}")
        flash(f'Error loading reports: {str(e)}', 'danger')
        return redirect(url_for('client.dashboard'))

@client_bp.route('/reports/<scan_id>')
@client_required
def report_view(user, scan_id):
    """View specific scan report"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get client information
        cursor.execute('''
            SELECT * FROM clients 
            WHERE user_id = ? AND active = 1
        ''', (user['id'],))
        user_client = cursor.fetchone()
        
        if not user_client:
            flash('Client profile not found', 'danger')
            return redirect(url_for('client.dashboard'))
        
        client_id = user_client['id']
        
        # Get scan report
        cursor.execute('''
            SELECT sh.*, ds.scanner_name
            FROM scan_history sh
            LEFT JOIN deployed_scanners ds ON sh.scanner_id = ds.id
            WHERE sh.scan_id = ? AND sh.client_id = ?
        ''', (scan_id, client_id))
        report = cursor.fetchone()
        
        if not report:
            flash('Report not found', 'danger')
            return redirect(url_for('client.reports'))
        
        report = dict(report)
        
        # Parse results if available
        results = {}
        if report['results']:
            try:
                import json
                results = json.loads(report['results'])
            except:
                results = {'error': 'Could not parse scan results'}
        
        conn.close()
        
        return render_template(
            'client/report-view.html',
            user=user,
            report=report,
            results=results
        )
        
    except Exception as e:
        logging.error(f"Error viewing report {scan_id}: {e}")
        flash(f'Error loading report: {str(e)}', 'danger')
        return redirect(url_for('client.reports'))

@client_bp.route('/settings')
@client_required
def settings(user):
    """Client settings page"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get client information
        cursor.execute('''
            SELECT * FROM clients 
            WHERE user_id = ? AND active = 1
        ''', (user['id'],))
        user_client = cursor.fetchone()
        
        if user_client:
            user_client = dict(user_client)
            
            # Get customization settings
            cursor.execute('''
                SELECT * FROM customizations 
                WHERE client_id = ?
            ''', (user_client['id'],))
            customizations = cursor.fetchone()
            if customizations:
                customizations = dict(customizations)
        else:
            user_client = {}
            customizations = {}
        
        conn.close()
        
        return render_template(
            'client/settings.html',
            user=user,
            user_client=user_client,
            customizations=customizations
        )
        
    except Exception as e:
        logging.error(f"Error in client settings: {e}")
        flash(f'Error loading settings: {str(e)}', 'danger')
        return redirect(url_for('client.dashboard'))

@client_bp.route('/settings/update', methods=['POST'])
@client_required
def update_settings(user):
    """Update client settings"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get client information
        cursor.execute('''
            SELECT * FROM clients 
            WHERE user_id = ? AND active = 1
        ''', (user['id'],))
        user_client = cursor.fetchone()
        
        if not user_client:
            flash('Client profile not found', 'danger')
            return redirect(url_for('client.dashboard'))
        
        client_id = user_client['id']
        
        # Update client information
        business_name = request.form.get('business_name')
        business_domain = request.form.get('business_domain')
        contact_phone = request.form.get('contact_phone')
        
        if business_name and business_domain:
            cursor.execute('''
                UPDATE clients 
                SET business_name = ?, business_domain = ?, contact_phone = ?, updated_at = ?
                WHERE id = ?
            ''', (business_name, business_domain, contact_phone, datetime.now().isoformat(), client_id))
        
        # Update or insert customizations
        primary_color = request.form.get('primary_color', '#007bff')
        secondary_color = request.form.get('secondary_color', '#6c757d')
        email_subject = request.form.get('email_subject', '')
        email_intro = request.form.get('email_intro', '')
        email_footer = request.form.get('email_footer', '')
        
        cursor.execute('''
            INSERT OR REPLACE INTO customizations 
            (client_id, primary_color, secondary_color, email_subject, email_intro, email_footer, last_updated, updated_by)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (client_id, primary_color, secondary_color, email_subject, email_intro, email_footer, 
              datetime.now().isoformat(), user['id']))
        
        conn.commit()
        conn.close()
        
        flash('Settings updated successfully', 'success')
        return redirect(url_for('client.settings'))
        
    except Exception as e:
        logging.error(f"Error updating client settings: {e}")
        flash(f'Error updating settings: {str(e)}', 'danger')
        return redirect(url_for('client.settings'))

# API Routes
@client_bp.route('/api/scanner-stats/<int:scanner_id>')
@client_required
def api_scanner_stats(user, scanner_id):
    """API endpoint for scanner statistics"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Verify scanner ownership
        cursor.execute('''
            SELECT ds.* FROM deployed_scanners ds
            JOIN clients c ON ds.client_id = c.id
            WHERE ds.id = ? AND c.user_id = ?
        ''', (scanner_id, user['id']))
        
        scanner = cursor.fetchone()
        if not scanner:
            return jsonify({'status': 'error', 'message': 'Scanner not found'}), 404
        
        # Get statistics
        cursor.execute('''
            SELECT 
                COUNT(*) as total_scans,
                COUNT(CASE WHEN status = 'completed' THEN 1 END) as completed_scans,
                COUNT(CASE WHEN status = 'running' THEN 1 END) as running_scans,
                AVG(security_score) as avg_score,
                SUM(issues_found) as total_issues
            FROM scan_history
            WHERE scanner_id = ?
        ''', (scanner_id,))
        
        stats = dict(cursor.fetchone())
        conn.close()
        
        return jsonify({
            'status': 'success',
            'data': stats
        })
        
    except Exception as e:
        logging.error(f"Error getting scanner stats: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500