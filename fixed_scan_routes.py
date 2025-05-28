"""
Fixed Scan Routes with Proper Detection and Display of All Scan Types
Ensures that all scan types are properly detected and displayed in the results
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
import traceback

# Create fixed scan blueprint
fixed_scan_bp = Blueprint('fixed_scan', __name__)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Global storage for scan progress (in production, use Redis or database)
scan_progress_storage = {}
scan_results_storage = {}

@fixed_scan_bp.route('/fixed-scan', methods=['GET', 'POST'])
def fixed_scan_page():
    """Fixed scan page with comprehensive scan capabilities"""
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
                'user_agent': request.headers.get('User-Agent', ''),
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
                # Remove any path component
                if '/' in company_website:
                    company_website = company_website.split('/', 1)[0]
                target_domain = company_website
            elif lead_data["email"] and '@' in lead_data["email"]:
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
            scan_id = f"fixed_scan_{uuid.uuid4().hex[:12]}"
            
            # Save lead data to database
            try:
                from database_utils import save_lead_data
                lead_id = save_lead_data(lead_data)
            except Exception as e:
                logger.error(f"Error saving lead data: {e}")
                lead_id = None
            
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
                'task': 'Initializing comprehensive security scan...',
                'status': 'starting',
                'start_time': datetime.now().isoformat()
            }
            
            # Start scan in background thread
            scan_thread = threading.Thread(
                target=run_fixed_scan_background,
                args=(scan_id, target_domain, scan_options, lead_data, client_id, scanner_id, request)
            )
            scan_thread.daemon = True
            scan_thread.start()
            
            return jsonify({
                'status': 'started',
                'scan_id': scan_id,
                'message': 'Comprehensive scan started successfully!'
            })
            
        except Exception as e:
            logger.error(f"Error starting fixed scan: {e}")
            logger.error(traceback.format_exc())
            return jsonify({
                'status': 'error',
                'message': f'Failed to start scan: {str(e)}'
            }), 500
    
    # GET request - show fixed scan form
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
    
    return render_template('fixed_scan.html', 
                         client_id=client_id,
                         scanner_id=scanner_id,
                         client_branding=client_branding)

@fixed_scan_bp.route('/fixed-scan-progress/<scan_id>')
def get_fixed_scan_progress(scan_id):
    """Get real-time scan progress"""
    if scan_id in scan_progress_storage:
        return jsonify(scan_progress_storage[scan_id])
    else:
        return jsonify({
            'progress': 0,
            'task': 'Scan not found',
            'status': 'error'
        }), 404

@fixed_scan_bp.route('/fixed-scan-results/<scan_id>')
def get_fixed_scan_results(scan_id):
    """Get scan results"""
    if scan_id in scan_results_storage:
        return jsonify(scan_results_storage[scan_id])
    else:
        return jsonify({
            'status': 'error',
            'message': 'Scan results not found'
        }), 404

@fixed_scan_bp.route('/scan-report/<scan_id>')
def view_scan_report(scan_id):
    """View detailed scan report"""
    # Check if scan exists in local storage
    if scan_id in scan_results_storage:
        scan_results = scan_results_storage[scan_id]
    else:
        # Try to look up in database
        try:
            from client_db import get_db_connection
            conn = get_db_connection()
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("SELECT * FROM scans WHERE scan_id = ?", (scan_id,))
            scan_row = cursor.fetchone()
            
            if scan_row and scan_row['results']:
                try:
                    scan_results = json.loads(scan_row['results'])
                except:
                    scan_results = None
            else:
                scan_results = None
                
            conn.close()
        except Exception as e:
            logger.error(f"Error retrieving scan from database: {e}")
            scan_results = None
    
    if not scan_results:
        flash('Scan results not found', 'error')
        return redirect(url_for('fixed_scan.fixed_scan_page'))
    
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
    
    # Determine company domain and calculate industry type
    target_domain = scan_results.get('target')
    client_email = scan_results.get('client_info', {}).get('email', '')
    company_name = scan_results.get('client_info', {}).get('company', '')
    
    # Add industry analysis
    try:
        from scan import determine_industry, calculate_industry_percentile, get_industry_benchmarks
        email_domain = target_domain or (client_email.split('@')[1] if '@' in client_email else '')
        industry_type = determine_industry(company_name, email_domain) if (company_name or email_domain) else 'default'
        score = scan_results.get('risk_assessment', {}).get('overall_score', 75)
        industry_benchmarks = calculate_industry_percentile(score, industry_type)
        
        # Add industry data to scan results
        scan_results['industry'] = {
            'name': get_industry_benchmarks()[industry_type]['name'],
            'type': industry_type,
            'benchmarks': industry_benchmarks
        }
    except Exception as e:
        logger.error(f"Error calculating industry benchmarks: {e}")
    
    # Add client gateway info if network scanning was done
    if 'network' in scan_results:
        try:
            # Make sure gateway info is properly formatted
            if 'gateway' in scan_results['network'] and isinstance(scan_results['network']['gateway'], dict):
                if 'info' not in scan_results['network']['gateway']:
                    scan_results['network']['gateway']['info'] = f"Target: {target_domain}"
        except Exception as e:
            logger.error(f"Error formatting gateway info: {e}")
    
    # Return the rendered template with scan results
    return render_template('results.html',
                         scan=scan_results,
                         client_branding=client_branding)

def run_fixed_scan_background(scan_id, target_domain, scan_options, lead_data, client_id=None, scanner_id=None, request=None):
    """
    Run fixed scan in background with progress updates
    """
    try:
        logger.info(f"Starting fixed scan {scan_id} for {target_domain}")
        
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
        
        # Client info with user agent
        client_info = {
            'name': lead_data.get('name', ''),
            'email': lead_data.get('email', ''),
            'company': lead_data.get('company', ''),
            'phone': lead_data.get('phone', ''),
            'user_agent': lead_data.get('user_agent', '')
        }
        
        # Get gateway information for network scanning
        try:
            if scan_options.get('network_scan', True) and request:
                from scan import get_default_gateway_ip
                gateway_info = {
                    'client_ip': request.remote_addr,
                    'target_domain': target_domain,
                    'gateway_ip': None
                }
                
                # Try to determine gateway info
                gateway_detail = get_default_gateway_ip(request)
                if gateway_detail:
                    gateway_info['gateway_detail'] = gateway_detail
                    # Extract likely gateway IPs
                    if "Likely gateways:" in gateway_detail:
                        try:
                            gateways = gateway_detail.split("Likely gateways:")[1].strip()
                            if "|" in gateways:
                                gateways = gateways.split("|")[0].strip()
                            gateway_ips = [g.strip() for g in gateways.split(",")]
                            if gateway_ips and gateway_ips[0]:
                                gateway_info['gateway_ip'] = gateway_ips[0]
                        except:
                            pass
        except Exception as e:
            logger.error(f"Error getting gateway info: {e}")
            gateway_info = {'target_domain': target_domain}
        
        # Import and run fixed scanner
        from fixed_scan_core import run_fixed_scan
        
        # Run the scan
        scan_results = run_fixed_scan(
            target_domain, 
            scan_options=scan_options, 
            client_info=client_info, 
            progress_callback=progress_callback
        )
        
        # Add metadata
        scan_results.update({
            'scan_id': scan_id,
            'email': lead_data.get('email', ''),
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
                    scan_type='fixed_comprehensive',
                    results=scan_results,
                    user_info=lead_data
                )
                logger.info(f"Scan logged for client {client_id}")
            except Exception as e:
                logger.error(f"Error logging scan for client: {e}")
        
        # Send email report (if configured)
        try:
            send_scan_report(scan_results, lead_data, client_id)
        except Exception as e:
            logger.error(f"Error sending scan report email: {e}")
            
        logger.info(f"Fixed scan {scan_id} completed successfully")
        
    except Exception as e:
        logger.error(f"Fixed scan {scan_id} failed: {e}")
        logger.error(traceback.format_exc())
        
        # Update progress to failed
        scan_progress_storage[scan_id] = {
            'progress': 0,
            'task': f'Scan failed: {str(e)}',
            'status': 'failed',
            'error': str(e),
            'scan_id': scan_id
        }

def send_scan_report(scan_results, lead_data, client_id=None):
    """
    Send scan report via email
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
        
        # Send email
        from email_utils import send_scan_report_email
        send_scan_report_email(
            to_email=lead_data['email'],
            to_name=lead_data.get('name', 'Security Scan User'),
            company_name=lead_data.get('company', 'Your Company'),
            scan_results=scan_results,
            client_branding=client_branding
        )
        
        logger.info(f"Scan report sent to {lead_data['email']}")
        
    except Exception as e:
        logger.error(f"Error sending scan report: {e}")

# Create template for fixed scan
def create_fixed_scan_template():
    """Create HTML template for the fixed scan page"""
    template_dir = os.path.join(os.getcwd(), 'templates')
    template_path = os.path.join(template_dir, 'fixed_scan.html')
    
    if not os.path.exists(template_path):
        try:
            from enhanced_scan_routes import enhanced_scan_bp
            template_content = """{% extends "base.html" %}

{% block title %}Comprehensive Security Scan{% endblock %}

{% block content %}
<div class="container">
    <div class="row justify-content-center">
        <div class="col-md-10">
            <div class="card">
                <div class="card-header">
                    <h2>Comprehensive Security Scan</h2>
                    <p class="mb-0">Identify vulnerabilities across your network, web, and email security</p>
                </div>
                <div class="card-body">
                    <form id="fixedScanForm" method="post">
                        <input type="hidden" name="csrf_token" value="{{ csrf_token() }}">
                        {% if client_id %}
                        <input type="hidden" name="client_id" value="{{ client_id }}">
                        {% endif %}
                        {% if scanner_id %}
                        <input type="hidden" name="scanner_id" value="{{ scanner_id }}">
                        {% endif %}
                        
                        <div class="row mb-4">
                            <div class="col-md-6">
                                <h4>Your Information</h4>
                                <div class="mb-3">
                                    <label for="name" class="form-label">Name</label>
                                    <input type="text" class="form-control" id="name" name="name" required>
                                </div>
                                <div class="mb-3">
                                    <label for="email" class="form-label">Email Address</label>
                                    <input type="email" class="form-control" id="email" name="email" required>
                                </div>
                                <div class="mb-3">
                                    <label for="company" class="form-label">Company Name</label>
                                    <input type="text" class="form-control" id="company" name="company">
                                </div>
                                <div class="mb-3">
                                    <label for="phone" class="form-label">Phone Number</label>
                                    <input type="tel" class="form-control" id="phone" name="phone">
                                </div>
                            </div>
                            <div class="col-md-6">
                                <h4>Target Information</h4>
                                <div class="mb-3">
                                    <label for="company_website" class="form-label">Website to Scan</label>
                                    <input type="text" class="form-control" id="company_website" name="company_website" 
                                           placeholder="example.com" required>
                                    <div class="form-text">Enter the domain you want to scan (e.g., example.com)</div>
                                </div>
                                <div class="mb-3">
                                    <label for="industry" class="form-label">Industry</label>
                                    <select class="form-select" id="industry" name="industry">
                                        <option value="default">General Business</option>
                                        <option value="healthcare">Healthcare</option>
                                        <option value="financial">Financial Services</option>
                                        <option value="retail">Retail</option>
                                        <option value="education">Education</option>
                                        <option value="manufacturing">Manufacturing</option>
                                        <option value="government">Government</option>
                                    </select>
                                </div>
                                <div class="mb-3">
                                    <label for="company_size" class="form-label">Company Size</label>
                                    <select class="form-select" id="company_size" name="company_size">
                                        <option value="1-10">1-10 employees</option>
                                        <option value="11-50">11-50 employees</option>
                                        <option value="51-200">51-200 employees</option>
                                        <option value="201-500">201-500 employees</option>
                                        <option value="501-1000">501-1000 employees</option>
                                        <option value="1000+">1000+ employees</option>
                                    </select>
                                </div>
                            </div>
                        </div>
                        
                        <div class="row mb-4">
                            <div class="col-12">
                                <h4>Scan Options</h4>
                                <div class="row">
                                    <div class="col-md-3">
                                        <div class="form-check">
                                            <input class="form-check-input" type="checkbox" id="network_scan" name="network_scan" checked>
                                            <label class="form-check-label" for="network_scan">
                                                Network Security
                                            </label>
                                        </div>
                                    </div>
                                    <div class="col-md-3">
                                        <div class="form-check">
                                            <input class="form-check-input" type="checkbox" id="web_scan" name="web_scan" checked>
                                            <label class="form-check-label" for="web_scan">
                                                Web Security
                                            </label>
                                        </div>
                                    </div>
                                    <div class="col-md-3">
                                        <div class="form-check">
                                            <input class="form-check-input" type="checkbox" id="email_scan" name="email_scan" checked>
                                            <label class="form-check-label" for="email_scan">
                                                Email Security
                                            </label>
                                        </div>
                                    </div>
                                    <div class="col-md-3">
                                        <div class="form-check">
                                            <input class="form-check-input" type="checkbox" id="ssl_scan" name="ssl_scan" checked>
                                            <label class="form-check-label" for="ssl_scan">
                                                SSL/TLS Security
                                            </label>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                        
                        <div class="row">
                            <div class="col-12">
                                <div class="d-grid">
                                    <button type="submit" class="btn btn-primary btn-lg" id="startScanBtn">
                                        <i class="bi bi-shield-check me-2"></i>Start Security Scan
                                    </button>
                                </div>
                            </div>
                        </div>
                    </form>
                    
                    <!-- Progress Section (initially hidden) -->
                    <div id="scanProgress" style="display: none;">
                        <div class="text-center mb-4 mt-4">
                            <div class="spinner-border text-primary" role="status">
                                <span class="visually-hidden">Loading...</span>
                            </div>
                            <h4 class="mt-3" id="progressTask">Initializing scan...</h4>
                        </div>
                        
                        <div class="progress" style="height: 25px;">
                            <div id="progressBar" class="progress-bar progress-bar-striped progress-bar-animated" 
                                 role="progressbar" style="width: 0%;" aria-valuenow="0" aria-valuemin="0" aria-valuemax="100">0%</div>
                        </div>
                        
                        <div class="d-flex justify-content-between mt-2">
                            <span id="progressTime">Elapsed: 0s</span>
                            <span id="progressPercentage">0%</span>
                        </div>
                        
                        <div class="alert alert-info mt-4">
                            <i class="bi bi-info-circle-fill me-2"></i>
                            <span id="progressMessage">We're scanning your systems for security vulnerabilities. This may take a few minutes.</span>
                        </div>
                    </div>
                    
                    <!-- Results Section (initially hidden) -->
                    <div id="scanResults" style="display: none;">
                        <div class="text-center mt-4 mb-4">
                            <i class="bi bi-check-circle-fill text-success" style="font-size: 3rem;"></i>
                            <h3 class="mt-3">Scan Completed!</h3>
                            <p>Your security scan has completed successfully.</p>
                            
                            <div class="d-grid gap-2 col-md-8 mx-auto mt-4">
                                <a href="#" id="viewReportBtn" class="btn btn-success btn-lg">
                                    <i class="bi bi-file-earmark-text me-2"></i>View Detailed Report
                                </a>
                                <button id="newScanBtn" class="btn btn-outline-primary">
                                    <i class="bi bi-arrow-repeat me-2"></i>Run Another Scan
                                </button>
                            </div>
                        </div>
                    </div>
                    
                    <!-- Error Section (initially hidden) -->
                    <div id="scanError" style="display: none;">
                        <div class="text-center mt-4 mb-4">
                            <i class="bi bi-exclamation-triangle-fill text-danger" style="font-size: 3rem;"></i>
                            <h3 class="mt-3">Scan Error</h3>
                            <p id="errorMessage">There was an error during the scan.</p>
                            
                            <div class="d-grid gap-2 col-md-8 mx-auto mt-4">
                                <button id="tryAgainBtn" class="btn btn-primary btn-lg">
                                    <i class="bi bi-arrow-repeat me-2"></i>Try Again
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}

{% block scripts %}
<script>
    document.addEventListener('DOMContentLoaded', function() {
        const scanForm = document.getElementById('fixedScanForm');
        const scanProgress = document.getElementById('scanProgress');
        const scanResults = document.getElementById('scanResults');
        const scanError = document.getElementById('scanError');
        const progressBar = document.getElementById('progressBar');
        const progressTask = document.getElementById('progressTask');
        const progressTime = document.getElementById('progressTime');
        const progressPercentage = document.getElementById('progressPercentage');
        const progressMessage = document.getElementById('progressMessage');
        const viewReportBtn = document.getElementById('viewReportBtn');
        const newScanBtn = document.getElementById('newScanBtn');
        const tryAgainBtn = document.getElementById('tryAgainBtn');
        const errorMessage = document.getElementById('errorMessage');
        
        let scanId = null;
        let progressInterval = null;
        let startTime = null;
        
        // Form submission
        scanForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            // Show progress section
            scanForm.style.display = 'none';
            scanProgress.style.display = 'block';
            scanResults.style.display = 'none';
            scanError.style.display = 'none';
            
            // Reset progress
            progressBar.style.width = '0%';
            progressBar.textContent = '0%';
            progressTask.textContent = 'Initializing scan...';
            
            // Record start time
            startTime = new Date();
            
            // Submit form data
            const formData = new FormData(scanForm);
            
            fetch('/fixed-scan', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'started') {
                    scanId = data.scan_id;
                    // Start progress polling
                    startProgressPolling();
                } else {
                    // Show error
                    showError(data.message || 'Failed to start scan');
                }
            })
            .catch(error => {
                showError('Error: ' + error.message);
            });
        });
        
        // Start progress polling
        function startProgressPolling() {
            if (progressInterval) {
                clearInterval(progressInterval);
            }
            
            progressInterval = setInterval(checkProgress, 1000);
        }
        
        // Check scan progress
        function checkProgress() {
            if (!scanId) return;
            
            fetch('/fixed-scan-progress/' + scanId)
            .then(response => response.json())
            .then(data => {
                // Update progress UI
                const progress = data.progress || 0;
                progressBar.style.width = progress + '%';
                progressBar.textContent = progress + '%';
                progressPercentage.textContent = progress + '%';
                
                if (data.task) {
                    progressTask.textContent = data.task;
                }
                
                // Update elapsed time
                const elapsed = Math.floor((new Date() - startTime) / 1000);
                progressTime.textContent = 'Elapsed: ' + formatTime(elapsed);
                
                // Update message based on progress
                if (progress < 25) {
                    progressMessage.textContent = 'We are analyzing your network security. This may take a few minutes.';
                } else if (progress < 50) {
                    progressMessage.textContent = 'Checking web security configuration and vulnerabilities...';
                } else if (progress < 75) {
                    progressMessage.textContent = 'Analyzing email security measures and DNS configurations...';
                } else {
                    progressMessage.textContent = 'Almost done! Finalizing security assessment and generating recommendations...';
                }
                
                // Check if scan is complete or failed
                if (data.status === 'completed') {
                    clearInterval(progressInterval);
                    showResults();
                } else if (data.status === 'failed') {
                    clearInterval(progressInterval);
                    showError(data.task || 'Scan failed');
                }
            })
            .catch(error => {
                console.error('Error checking progress:', error);
            });
        }
        
        // Format time in seconds to MM:SS
        function formatTime(seconds) {
            const minutes = Math.floor(seconds / 60);
            const remainingSeconds = seconds % 60;
            return minutes + ':' + (remainingSeconds < 10 ? '0' : '') + remainingSeconds;
        }
        
        // Show results section
        function showResults() {
            scanProgress.style.display = 'none';
            scanResults.style.display = 'block';
            
            // Set report URL
            viewReportBtn.href = '/scan-report/' + scanId;
        }
        
        // Show error section
        function showError(message) {
            scanProgress.style.display = 'none';
            scanError.style.display = 'block';
            errorMessage.textContent = message;
        }
        
        // New scan button
        newScanBtn.addEventListener('click', function() {
            scanForm.reset();
            scanForm.style.display = 'block';
            scanResults.style.display = 'none';
        });
        
        // Try again button
        tryAgainBtn.addEventListener('click', function() {
            scanForm.style.display = 'block';
            scanError.style.display = 'none';
        });
    });
</script>
{% endblock %}"""
            
            with open(template_path, 'w') as f:
                f.write(template_content)
                
            logger.info(f"Created fixed scan template at {template_path}")
            return True
        except Exception as e:
            logger.error(f"Error creating fixed scan template: {e}")
            return False
    
    return True

# Register the blueprint with the app
def register_fixed_scan_blueprint(app):
    """Register the fixed scan blueprint with Flask app"""
    app.register_blueprint(fixed_scan_bp)
    
    # Create template if needed
    create_fixed_scan_template()
    
    logger.info("Fixed scan blueprint registered successfully")
    
    return True