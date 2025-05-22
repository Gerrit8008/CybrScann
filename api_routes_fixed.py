# api_routes_fixed.py
from flask import Blueprint, request, jsonify, session
import sqlite3
import logging
from datetime import datetime
import os
import json
import uuid
import hashlib

# Create API blueprint
api_bp = Blueprint('api', __name__, url_prefix='/api')

# Database path
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'cybrscan.db')

def get_db_connection():
    """Get database connection"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def verify_api_key(api_key):
    """Verify API key and return client information"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT c.*, u.username, u.email
            FROM clients c
            LEFT JOIN users u ON c.user_id = u.id
            WHERE c.api_key = ? AND c.active = 1
        ''', (api_key,))
        
        client = cursor.fetchone()
        conn.close()
        
        return dict(client) if client else None
        
    except Exception as e:
        logging.error(f"Error verifying API key: {e}")
        return None

def verify_session_token(session_token):
    """Verify session token and return user information"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT u.*, s.session_token 
            FROM users u 
            JOIN sessions s ON u.id = s.user_id 
            WHERE s.session_token = ? AND s.expires_at > ? AND u.active = 1
        ''', (session_token, datetime.now().isoformat()))
        
        user = cursor.fetchone()
        conn.close()
        
        return dict(user) if user else None
        
    except Exception as e:
        logging.error(f"Error verifying session token: {e}")
        return None

@api_bp.route('/run_scan', methods=['POST'])
def run_scan():
    """API endpoint to run a new scan"""
    try:
        # Check authentication
        session_token = session.get('session_token')
        api_key = request.headers.get('X-API-Key') or request.form.get('api_key')
        
        client_info = None
        user_info = None
        
        if api_key:
            client_info = verify_api_key(api_key)
        elif session_token:
            user_info = verify_session_token(session_token)
            if user_info:
                # Get client info for the user
                conn = get_db_connection()
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT * FROM clients 
                    WHERE user_id = ? AND active = 1
                ''', (user_info['id'],))
                client_info = cursor.fetchone()
                if client_info:
                    client_info = dict(client_info)
                conn.close()
        
        if not client_info:
            return jsonify({
                'status': 'error',
                'message': 'Authentication required'
            }), 401
        
        # Get scan parameters
        target = request.form.get('target') or request.json.get('target') if request.is_json else None
        scan_type = request.form.get('scan_type', 'quick') or (request.json.get('scan_type', 'quick') if request.is_json else 'quick')
        scanner_id = request.form.get('scanner_id') or (request.json.get('scanner_id') if request.is_json else None)
        
        if not target:
            return jsonify({
                'status': 'error',
                'message': 'Target is required'
            }), 400
        
        # Generate unique scan ID
        scan_id = str(uuid.uuid4())
        
        # Create scan record
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO scan_history 
            (client_id, scanner_id, scan_id, target, scan_type, status, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (client_info['id'], scanner_id, scan_id, target, scan_type, 'pending', datetime.now().isoformat()))
        
        conn.commit()
        conn.close()
        
        # Here you would typically queue the scan for processing
        # For now, we'll just return the scan ID
        
        return jsonify({
            'status': 'success',
            'message': 'Scan started successfully',
            'scan_id': scan_id,
            'target': target,
            'scan_type': scan_type
        })
        
    except Exception as e:
        logging.error(f"Error running scan: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@api_bp.route('/quick_scan', methods=['POST'])
def quick_scan():
    """API endpoint for quick scan"""
    try:
        # Check authentication
        session_token = session.get('session_token')
        user_info = verify_session_token(session_token)
        
        if not user_info:
            return jsonify({
                'status': 'error',
                'message': 'Authentication required'
            }), 401
        
        # Get client info
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM clients 
            WHERE user_id = ? AND active = 1
        ''', (user_info['id'],))
        client_info = cursor.fetchone()
        
        if not client_info:
            return jsonify({
                'status': 'error',
                'message': 'Client profile not found'
            }), 404
        
        client_info = dict(client_info)
        
        # Get scan parameters
        data = request.get_json() or {}
        scanner_id = data.get('scanner_id')
        target = data.get('target')
        
        # If no target specified, use the scanner's default target
        if not target and scanner_id:
            cursor.execute('''
                SELECT * FROM deployed_scanners 
                WHERE id = ? AND client_id = ?
            ''', (scanner_id, client_info['id']))
            scanner = cursor.fetchone()
            if scanner:
                target = scanner['domain'] or client_info['business_domain']
        
        if not target:
            target = client_info['business_domain']
        
        # Generate unique scan ID
        scan_id = str(uuid.uuid4())
        
        # Create scan record
        cursor.execute('''
            INSERT INTO scan_history 
            (client_id, scanner_id, scan_id, target, scan_type, status, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (client_info['id'], scanner_id, scan_id, target, 'quick', 'running', datetime.now().isoformat()))
        
        conn.commit()
        
        # Simulate scan completion (in a real app, this would be asynchronous)
        import time
        import random
        
        # Simulate some processing time
        time.sleep(1)
        
        # Generate mock results
        security_score = random.randint(60, 95)
        issues_found = random.randint(0, 8)
        
        results = {
            'security_score': security_score,
            'issues_found': issues_found,
            'scan_type': 'quick',
            'target': target,
            'timestamp': datetime.now().isoformat(),
            'details': {
                'ssl_check': {'status': 'pass', 'score': 10},
                'port_scan': {'status': 'warning', 'open_ports': [80, 443], 'score': 8},
                'security_headers': {'status': 'pass', 'score': 9}
            }
        }
        
        # Update scan record with results
        cursor.execute('''
            UPDATE scan_history 
            SET status = ?, results = ?, security_score = ?, issues_found = ?
            WHERE scan_id = ?
        ''', ('completed', json.dumps(results), security_score, issues_found, scan_id))
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'status': 'success',
            'message': 'Quick scan completed',
            'scan_id': scan_id,
            'results': results
        })
        
    except Exception as e:
        logging.error(f"Error running quick scan: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@api_bp.route('/scan_status/<scan_id>')
def scan_status(scan_id):
    """Get scan status"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM scan_history 
            WHERE scan_id = ?
        ''', (scan_id,))
        
        scan = cursor.fetchone()
        conn.close()
        
        if not scan:
            return jsonify({
                'status': 'error',
                'message': 'Scan not found'
            }), 404
        
        scan = dict(scan)
        
        # Parse results if available
        results = None
        if scan['results']:
            try:
                results = json.loads(scan['results'])
            except:
                results = None
        
        return jsonify({
            'status': 'success',
            'data': {
                'scan_id': scan['scan_id'],
                'target': scan['target'],
                'scan_type': scan['scan_type'],
                'status': scan['status'],
                'timestamp': scan['timestamp'],
                'security_score': scan['security_score'],
                'issues_found': scan['issues_found'],
                'results': results
            }
        })
        
    except Exception as e:
        logging.error(f"Error getting scan status: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@api_bp.route('/generate_api_key', methods=['POST'])
def generate_api_key():
    """Generate new API key for client"""
    try:
        # Check authentication
        session_token = session.get('session_token')
        user_info = verify_session_token(session_token)
        
        if not user_info:
            return jsonify({
                'status': 'error',
                'message': 'Authentication required'
            }), 401
        
        # Generate new API key
        api_key = hashlib.sha256(f"{user_info['id']}{datetime.now().isoformat()}{uuid.uuid4()}".encode()).hexdigest()
        
        # Update client record
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE clients 
            SET api_key = ?, updated_at = ?
            WHERE user_id = ? AND active = 1
        ''', (api_key, datetime.now().isoformat(), user_info['id']))
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'status': 'success',
            'message': 'API key generated successfully',
            'api_key': api_key
        })
        
    except Exception as e:
        logging.error(f"Error generating API key: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@api_bp.route('/create_scanner', methods=['POST'])
def create_scanner():
    """Create a new scanner for a client"""
    try:
        # Check authentication
        session_token = session.get('session_token')
        user_info = verify_session_token(session_token)
        
        if not user_info:
            return jsonify({
                'status': 'error',
                'message': 'Authentication required'
            }), 401
        
        # Get client info
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM clients 
            WHERE user_id = ? AND active = 1
        ''', (user_info['id'],))
        client_info = cursor.fetchone()
        
        if not client_info:
            return jsonify({
                'status': 'error',
                'message': 'Client profile not found'
            }), 404
        
        client_info = dict(client_info)
        
        # Get scanner parameters
        data = request.get_json() or {}
        scanner_name = data.get('scanner_name', f"{client_info['business_name']} Scanner")
        subdomain = data.get('subdomain', client_info['business_name'].lower().replace(' ', '-'))
        domain = data.get('domain', client_info['business_domain'])
        
        # Generate API key for scanner
        scanner_api_key = hashlib.sha256(f"scanner_{client_info['id']}_{datetime.now().isoformat()}_{uuid.uuid4()}".encode()).hexdigest()
        
        # Create scanner record
        cursor.execute('''
            INSERT INTO deployed_scanners 
            (client_id, scanner_name, subdomain, domain, deploy_status, api_key)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (client_info['id'], scanner_name, subdomain, domain, 'pending', scanner_api_key))
        
        scanner_id = cursor.lastrowid
        
        # Create customization record
        cursor.execute('''
            INSERT INTO customizations 
            (client_id, primary_color, secondary_color, updated_by)
            VALUES (?, ?, ?, ?)
        ''', (client_info['id'], '#007bff', '#6c757d', user_info['id']))
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'status': 'success',
            'message': 'Scanner created successfully',
            'scanner_id': scanner_id,
            'scanner_name': scanner_name,
            'subdomain': subdomain,
            'api_key': scanner_api_key
        })
        
    except Exception as e:
        logging.error(f"Error creating scanner: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@api_bp.route('/scanner_stats')
def scanner_stats():
    """Get overall scanner statistics"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get various statistics
        cursor.execute('SELECT COUNT(*) as total_scanners FROM deployed_scanners')
        total_scanners = cursor.fetchone()['total_scanners']
        
        cursor.execute('SELECT COUNT(*) as active_scanners FROM deployed_scanners WHERE deploy_status = "deployed"')
        active_scanners = cursor.fetchone()['active_scanners']
        
        cursor.execute('SELECT COUNT(*) as total_scans FROM scan_history')
        total_scans = cursor.fetchone()['total_scans']
        
        cursor.execute('SELECT COUNT(*) as completed_scans FROM scan_history WHERE status = "completed"')
        completed_scans = cursor.fetchone()['completed_scans']
        
        cursor.execute('SELECT AVG(security_score) as avg_score FROM scan_history WHERE status = "completed" AND security_score IS NOT NULL')
        avg_security_score = cursor.fetchone()['avg_score'] or 0
        
        conn.close()
        
        return jsonify({
            'status': 'success',
            'data': {
                'total_scanners': total_scanners,
                'active_scanners': active_scanners,
                'total_scans': total_scans,
                'completed_scans': completed_scans,
                'avg_security_score': round(avg_security_score, 2)
            }
        })
        
    except Exception as e:
        logging.error(f"Error getting scanner stats: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500