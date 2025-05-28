"""
Enhanced Scan Routes with Real-time Progress Tracking
Provides amazing GUI experience with live progress updates
"""

from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for, flash
import os
import logging
import json
import uuid
from datetime import datetime
import sqlite3
import threading
import time

# Create enhanced scan blueprint
enhanced_scan_bp = Blueprint('enhanced_scan', __name__)

# Configure logging
logger = logging.getLogger(__name__)

# Global storage for scan progress (in production, use Redis or database)
scan_progress_storage = {}
scan_results_storage = {}

@enhanced_scan_bp.route('/enhanced-scan', methods=['GET', 'POST'])
def enhanced_scan_page():
    """Enhanced scan page with real-time progress tracking"""
    if request.method == 'POST':
        try:
            # Get form data
            lead_data = {
                'name': request.form.get('name', ''),
                'email': request.form.get('email', ''),
                'company': request.form.get('company', ''),
                'phone': request.form.get('phone', ''),
                'industry': request.form.get('industry', ''),
                'company_size': request.form.get('company_size', ''),
                'company_website': request.form.get('company_website', ''),
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }
            
            # Get scan options
            scan_options = {
                'network_scan': request.form.get('network_scan') == 'on',
                'web_scan': request.form.get('web_scan') == 'on',
                'email_scan': request.form.get('email_scan') == 'on',
                'ssl_scan': request.form.get('ssl_scan') == 'on',
                'advanced_options': request.form.get('advanced_options') == 'on'
            }
            
            # Determine target domain
            target_domain = None
            company_website = request.form.get('company_website', '').strip()
            if company_website:
                if company_website.startswith(('http://', 'https://')):
                    company_website = company_website.split('://', 1)[1]
                target_domain = company_website
            elif lead_data["email"]:
                target_domain = lead_data["email"].split('@')[1]
            
            if not target_domain:
                return jsonify({
                    'status': 'error',
                    'message': 'Please provide a valid domain or email address to scan.'
                }), 400
            
            # Basic validation
            if not lead_data["email"]:
                return jsonify({
                    'status': 'error',
                    'message': 'Please enter your email address to receive the scan report.'
                }), 400
            
            # Generate scan ID
            scan_id = f"enhanced_scan_{uuid.uuid4().hex[:12]}"
            
            # Save lead data to database
            from database_utils import save_lead_data
            lead_id = save_lead_data(lead_data)
            
            # Check client limits if applicable
            client_id = request.args.get('client_id') or request.form.get('client_id')
            scanner_id = request.args.get('scanner_id') or request.form.get('scanner_id')
            
            if client_id:
                try:
                    from client import get_client_total_scans, get_client_scan_limit
                    from client_db import get_db_connection
                    
                    conn = get_db_connection()
                    conn.row_factory = sqlite3.Row
                    cursor = conn.cursor()
                    cursor.execute("SELECT * FROM clients WHERE id = ?", (client_id,))
                    client_row = cursor.fetchone()
                    conn.close()
                    
                    if client_row:
                        client = dict(client_row)
                        current_scans = get_client_total_scans(client_id)
                        scan_limit = get_client_scan_limit(client)
                        
                        if current_scans >= scan_limit:
                            return jsonify({
                                'status': 'error',
                                'message': f'You have reached your scan limit of {scan_limit} scans for this billing period.'
                            }), 403
                except Exception as e:
                    logger.error(f"Error checking client limits: {e}")
            
            # Initialize progress tracking
            scan_progress_storage[scan_id] = {
                'progress': 0,
                'task': 'Initializing enhanced security scan...',
                'status': 'starting',
                'start_time': datetime.now().isoformat()
            }
            
            # Start scan in background thread
            scan_thread = threading.Thread(
                target=run_enhanced_scan_background,
                args=(scan_id, target_domain, scan_options, lead_data, client_id, scanner_id)
            )
            scan_thread.daemon = True
            scan_thread.start()
            
            return jsonify({
                'status': 'started',
                'scan_id': scan_id,
                'message': 'Enhanced scan started successfully!'
            })
            
        except Exception as e:
            logger.error(f"Error starting enhanced scan: {e}")
            return jsonify({
                'status': 'error',
                'message': f'Failed to start scan: {str(e)}'
            }), 500
    
    # GET request - show enhanced scan form
    client_id = request.args.get('client_id')
    scanner_id = request.args.get('scanner_id')
    
    # Get client branding if applicable
    client_branding = None
    if client_id:
        try:
            from client_db import get_db_connection
            conn = get_db_connection()
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Get client and customization data
            cursor.execute("""
                SELECT c.*, cu.* FROM clients c
                LEFT JOIN customizations cu ON c.id = cu.client_id
                WHERE c.id = ?
            """, (client_id,))
            
            result = cursor.fetchone()
            if result:
                client_branding = dict(result)
            conn.close()
        except Exception as e:
            logger.error(f"Error getting client branding: {e}")
    
    return render_template('enhanced_scan.html', 
                         client_id=client_id,
                         scanner_id=scanner_id,
                         client_branding=client_branding)

@enhanced_scan_bp.route('/scan-progress/<scan_id>')
def get_scan_progress(scan_id):
    """Get real-time scan progress"""
    if scan_id in scan_progress_storage:
        return jsonify(scan_progress_storage[scan_id])
    else:
        return jsonify({
            'progress': 0,
            'task': 'Scan not found',
            'status': 'error'
        }), 404

@enhanced_scan_bp.route('/scan-results/<scan_id>')
def get_scan_results(scan_id):
    """Get scan results"""
    if scan_id in scan_results_storage:
        return jsonify(scan_results_storage[scan_id])
    else:
        return jsonify({
            'status': 'error',
            'message': 'Scan results not found'
        }), 404

@enhanced_scan_bp.route('/scan-report/<scan_id>')
def view_scan_report(scan_id):
    """View detailed scan report"""
    if scan_id not in scan_results_storage:
        flash('Scan results not found', 'error')
        return redirect(url_for('enhanced_scan.enhanced_scan_page'))
    
    scan_results = scan_results_storage[scan_id]
    
    # Get client branding if applicable
    client_branding = None
    client_id = scan_results.get('client_id')
    if client_id:
        try:
            from client_db import get_db_connection
            conn = get_db_connection()
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT c.*, cu.* FROM clients c
                LEFT JOIN customizations cu ON c.id = cu.client_id
                WHERE c.id = ?
            """, (client_id,))
            
            result = cursor.fetchone()
            if result:
                client_branding = dict(result)
            conn.close()
        except Exception as e:
            logger.error(f"Error getting client branding: {e}")
    
    return render_template('enhanced_scan_report.html',
                         scan_results=scan_results,
                         client_branding=client_branding)

def run_enhanced_scan_background(scan_id, target_domain, scan_options, lead_data, client_id=None, scanner_id=None):
    """
    Run enhanced scan in background with progress updates
    """
    try:
        logger.info(f"Starting enhanced scan {scan_id} for {target_domain}")
        
        # Progress callback function
        def progress_callback(progress_data):
            scan_progress_storage[scan_id] = {
                'progress': progress_data['progress'],
                'task': progress_data['task'],
                'status': 'running',
                'step': progress_data['step'],
                'total': progress_data['total'],
                'elapsed_time': progress_data['elapsed_time'],
                'scan_id': scan_id
            }
        
        # Import and run enhanced scanner
        from enhanced_scan import run_enhanced_scan
        
        # Run the scan
        scan_results = run_enhanced_scan(target_domain, scan_options, progress_callback)
        
        # Add metadata
        scan_results.update({
            'scan_id': scan_id,
            'lead_data': lead_data,
            'client_id': client_id,
            'scanner_id': scanner_id,
            'completed_at': datetime.now().isoformat()
        })
        
        # Store results
        scan_results_storage[scan_id] = scan_results
        
        # Update progress to completed
        scan_progress_storage[scan_id] = {
            'progress': 100,
            'task': 'Scan completed successfully!',
            'status': 'completed',
            'scan_id': scan_id,
            'completed_at': datetime.now().isoformat()
        }
        
        # Log scan completion for client tracking
        if client_id:
            try:
                from client_db import log_scan
                log_scan(
                    client_id=client_id,
                    scanner_id=scanner_id,
                    target_domain=target_domain,
                    scan_type='enhanced_comprehensive',
                    results=scan_results,
                    user_info=lead_data
                )
                logger.info(f"Scan logged for client {client_id}")
            except Exception as e:
                logger.error(f"Error logging scan for client: {e}")
        
        # Send email report (if configured)
        try:
            send_enhanced_scan_report(scan_results, lead_data, client_id)
        except Exception as e:
            logger.error(f"Error sending scan report email: {e}")
            
        logger.info(f"Enhanced scan {scan_id} completed successfully")
        
    except Exception as e:
        logger.error(f"Enhanced scan {scan_id} failed: {e}")
        
        # Update progress to failed
        scan_progress_storage[scan_id] = {
            'progress': 0,
            'task': f'Scan failed: {str(e)}',
            'status': 'failed',
            'error': str(e),
            'scan_id': scan_id
        }

def send_enhanced_scan_report(scan_results, lead_data, client_id=None):
    """
    Send enhanced scan report via email
    """
    try:
        # Get client customizations if applicable
        client_branding = None
        if client_id:
            from client_db import get_db_connection
            conn = get_db_connection()
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT c.*, cu.* FROM clients c
                LEFT JOIN customizations cu ON c.id = cu.client_id
                WHERE c.id = ?
            """, (client_id,))
            
            result = cursor.fetchone()
            if result:
                client_branding = dict(result)
            conn.close()
        
        # Generate HTML report
        from enhanced_scan_report_generator import generate_enhanced_html_report
        html_report = generate_enhanced_html_report(scan_results, client_branding)
        
        # Send email
        from email_utils import send_scan_report_email
        send_scan_report_email(
            to_email=lead_data['email'],
            to_name=lead_data.get('name', 'Security Scan User'),
            company_name=lead_data.get('company', 'Your Company'),
            scan_results=scan_results,
            html_report=html_report,
            client_branding=client_branding
        )
        
        logger.info(f"Enhanced scan report sent to {lead_data['email']}")
        
    except Exception as e:
        logger.error(f"Error sending enhanced scan report: {e}")

# Real-time progress endpoint for WebSocket-like updates
@enhanced_scan_bp.route('/live-progress/<scan_id>')
def live_progress_updates(scan_id):
    """
    Server-Sent Events endpoint for real-time progress updates
    """
    def generate_progress_events():
        while True:
            if scan_id in scan_progress_storage:
                progress_data = scan_progress_storage[scan_id]
                yield f"data: {json.dumps(progress_data)}\n\n"
                
                # Stop streaming if scan is completed or failed
                if progress_data.get('status') in ['completed', 'failed']:
                    break
            else:
                yield f"data: {json.dumps({'error': 'Scan not found'})}\n\n"
                break
                
            time.sleep(1)  # Update every second
    
    return jsonify({
        'status': 'streaming',
        'message': 'Use Server-Sent Events for live updates'
    }), 200

# Enhanced scan status endpoint
@enhanced_scan_bp.route('/scan-status/<scan_id>')
def get_scan_status(scan_id):
    """Get comprehensive scan status"""
    progress_data = scan_progress_storage.get(scan_id, {})
    results_available = scan_id in scan_results_storage
    
    return jsonify({
        'scan_id': scan_id,
        'progress': progress_data,
        'results_available': results_available,
        'status': progress_data.get('status', 'unknown')
    })

# Cleanup old scan data (call periodically)
def cleanup_old_scans():
    """Clean up old scan data to prevent memory leaks"""
    try:
        current_time = datetime.now()
        cleanup_time = timedelta(hours=24)  # Keep data for 24 hours
        
        scan_ids_to_remove = []
        for scan_id, progress_data in scan_progress_storage.items():
            if 'start_time' in progress_data:
                start_time = datetime.fromisoformat(progress_data['start_time'])
                if current_time - start_time > cleanup_time:
                    scan_ids_to_remove.append(scan_id)
        
        for scan_id in scan_ids_to_remove:
            if scan_id in scan_progress_storage:
                del scan_progress_storage[scan_id]
            if scan_id in scan_results_storage:
                del scan_results_storage[scan_id]
            logger.info(f"Cleaned up old scan data for {scan_id}")
            
    except Exception as e:
        logger.error(f"Error during scan cleanup: {e}")