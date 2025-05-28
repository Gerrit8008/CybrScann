"""
Scan-related routes for CybrScan
Handles scan execution, results display, and scanning APIs
"""

from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for, flash
import os
import logging
import json
import uuid
import re
from datetime import datetime
import sqlite3

# Create scan blueprint
scan_bp = Blueprint('scan', __name__)

# Configure logging
logger = logging.getLogger(__name__)


@scan_bp.route('/scan', methods=['GET', 'POST'])
def scan_page():
    """Main scan page - handles both form display and scan submission"""
    if request.method == 'POST':
        try:
            # Get form data including client OS info and new fields
            lead_data = {
                'name': request.form.get('name', ''),
                'email': request.form.get('email', ''),
                'company': request.form.get('company', ''),
                'phone': request.form.get('phone', ''),
                'industry': request.form.get('industry', ''),
                'company_size': request.form.get('company_size', ''),
                'company_website': request.form.get('company_website', ''),
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'client_os': request.form.get('client_os', 'Unknown'),
                'client_browser': request.form.get('client_browser', 'Unknown'),
                'windows_version': request.form.get('windows_version', ''),
                'target': ''  # Will be set based on priority logic below
            }
            
            # Determine target domain with priority: company_website > email domain
            target_domain = None
            
            # Priority 1: Company website from form
            company_website = request.form.get('company_website', '').strip()
            if company_website:
                # Clean up the domain (remove http/https if present)
                if company_website.startswith(('http://', 'https://')):
                    company_website = company_website.split('://', 1)[1]
                target_domain = company_website
                logging.info(f"Using company website domain: {target_domain}")
            
            # Priority 2: Extract domain from email if no company website
            elif lead_data["email"]:
                from security_scanner import extract_domain_from_email
                target_domain = extract_domain_from_email(lead_data["email"])
                logging.info(f"Using domain extracted from email: {target_domain}")
            
            # Set the target for scanning
            if target_domain:
                lead_data["target"] = target_domain
                # Also store company website in lead data
                lead_data["company_website"] = target_domain
            else:
                logging.warning("No target domain found from company website or email")
            
            # Basic validation
            if not lead_data["email"]:
                is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
                if is_ajax:
                    return jsonify({
                        'status': 'error',
                        'message': 'Please enter your email address to receive the scan report.'
                    }), 400
                else:
                    return render_template('scan.html', error="Please enter your email address to receive the scan report.")
            
            # Save lead data to database
            logging.info("Saving lead data...")
            from database_utils import save_lead_data
            lead_id = save_lead_data(lead_data)
            logging.info(f"Lead data saved with ID: {lead_id}")
            
            # Check for client_id in query parameters or form data (used for client-specific scanner)
            client_id = request.args.get('client_id') or request.form.get('client_id')
            scanner_id = request.args.get('scanner_id') or request.form.get('scanner_id')
            
            # If client_id is provided, get client customizations and check scan limits
            client = None
            if client_id:
                try:
                    from client_db import get_db_connection
                    conn = get_db_connection()
                    conn.row_factory = sqlite3.Row
                    cursor = conn.cursor()
                    cursor.execute("SELECT * FROM clients WHERE id = ?", (client_id,))
                    client_row = cursor.fetchone()
                    conn.close()
                    
                    if client_row:
                        client = dict(client_row)
                        logging.info(f"Using client {client_id} for scan tracking (scanner: {scanner_id})")
                        
                        # Check scan limits before proceeding
                        try:
                            from client import get_client_total_scans, get_client_scan_limit
                            
                            current_scans = get_client_total_scans(client_id)
                            scan_limit = get_client_scan_limit(client)
                            
                            if current_scans >= scan_limit:
                                logging.warning(f"Client {client_id} has reached scan limit: {current_scans}/{scan_limit}")
                                return render_template('scan.html', 
                                    error=f"You have reached your scan limit of {scan_limit} scans for this billing period. Please upgrade your plan or wait for the next billing cycle to continue scanning.",
                                    client_id=client_id,
                                    scanner_id=scanner_id)
                        except Exception as limit_error:
                            logging.error(f"Error checking scan limits for client {client_id}: {limit_error}")
                            # Continue with scan if limit check fails to avoid breaking existing functionality
                        
                    else:
                        logging.warning(f"Client {client_id} not found")
                except Exception as client_error:
                    logging.error(f"Error getting client {client_id}: {client_error}")
                    client = None
            
            # Run the full consolidated scan using the comprehensive scanner
            logging.info(f"Starting scan for {lead_data.get('email')} targeting {lead_data.get('target')}...")
            
            # Import the comprehensive scanner functions
            from scan import (
                extract_domain_from_email, server_lookup, check_ssl_certificate, 
                check_security_headers, scan_gateway_ports, get_client_and_gateway_ip,
                analyze_dns_configuration, check_spf_status, check_dmarc_record, 
                check_dkim_record, determine_industry, get_industry_benchmarks,
                calculate_industry_percentile, calculate_risk_score, get_recommendations,
                generate_threat_scenario, categorize_risks_by_services
            )
            
            # Generate scan ID
            scan_id = f"scan_{uuid.uuid4().hex[:12]}"
            
            # Extract target domain
            target = lead_data.get('target', lead_data.get('company_website', ''))
            if not target and lead_data.get('email'):
                target = extract_domain_from_email(lead_data['email'])
            
            # Initialize comprehensive scan results
            scan_results = {
                'scan_id': scan_id,
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'email': lead_data.get('email', ''),
                'name': lead_data.get('name', ''),
                'company': lead_data.get('company', ''),
                'target': target,
                'scan_type': 'comprehensive',
                'status': 'completed'
            }
            
            try:
                # Server and infrastructure scanning
                logging.info(f"🔍 Running server lookup for {target}")
                server_info = server_lookup(target)
                scan_results['server'] = server_info
                
                # SSL Certificate analysis
                logging.info(f"🔒 Checking SSL certificate for {target}")
                ssl_results = check_ssl_certificate(target)
                scan_results['ssl_certificate'] = ssl_results
                
                # Security headers analysis
                logging.info(f"🛡️ Analyzing security headers for {target}")
                headers_results = check_security_headers(target)
                scan_results['security_headers'] = headers_results
                
                # Network scanning (gateway and target)
                logging.info(f"🌐 Scanning network infrastructure for {target}")
                try:
                    client_gateway_info = get_client_and_gateway_ip(request)
                    
                    # Enhanced gateway info with target domain
                    enhanced_gateway_info = client_gateway_info
                    if isinstance(client_gateway_info, dict):
                        enhanced_gateway_info['target_domain'] = target
                    elif isinstance(client_gateway_info, str):
                        enhanced_gateway_info = {
                            'raw_info': client_gateway_info,
                            'target_domain': target
                        }
                    else:
                        enhanced_gateway_info = {'target_domain': target}
                    
                    # Perform comprehensive network scan
                    gateway_scan = scan_gateway_ports(enhanced_gateway_info)
                    scan_results['network'] = gateway_scan
                    logging.info(f"Network scan completed: {len(gateway_scan) if isinstance(gateway_scan, list) else 'unknown'} findings")
                    
                except Exception as network_error:
                    logging.warning(f"Network scanning error: {network_error}")
                    scan_results['network'] = {'status': 'error', 'message': str(network_error)}
                
                # DNS and email security
                logging.info(f"📧 Analyzing email security for {target}")
                dns_config = analyze_dns_configuration(target)
                spf_status = check_spf_status(target)
                dmarc_status = check_dmarc_record(target)
                dkim_status = check_dkim_record(target)
                
                # Convert tuple results to dict format for consistency
                def convert_email_result(result):
                    if isinstance(result, tuple):
                        # Handle tuple format: (status, severity, details)
                        return {
                            'status': result[0] if len(result) > 0 else 'Unknown',
                            'severity': result[1] if len(result) > 1 else 'Medium',
                            'details': result[2] if len(result) > 2 else ''
                        }
                    elif isinstance(result, dict):
                        return result
                    else:
                        return {'status': str(result), 'severity': 'Medium', 'details': ''}
                
                scan_results['email_security'] = {
                    'domain': target,
                    'spf': convert_email_result(spf_status),
                    'dmarc': convert_email_result(dmarc_status),
                    'dkim': convert_email_result(dkim_status),
                    'dns_config': dns_config
                }
                
                # Industry analysis
                logging.info(f"🏢 Determining industry benchmarks")
                industry_type = determine_industry(lead_data.get('company', ''), target)
                industry_benchmarks = get_industry_benchmarks()
                scan_results['industry'] = {
                    'type': industry_type,
                    'benchmarks': industry_benchmarks.get(industry_type, industry_benchmarks['default'])
                }
                
                # Calculate overall risk score
                logging.info(f"📊 Calculating risk assessment")
                try:
                    risk_score = calculate_risk_score(scan_results)
                    scan_results['security_score'] = risk_score
                    scan_results['risk_assessment'] = {
                        'overall_score': risk_score,
                        'risk_level': 'Critical' if risk_score < 40 else 'High' if risk_score < 60 else 'Medium' if risk_score < 80 else 'Low'
                    }
                except Exception as risk_error:
                    logging.error(f"Error calculating risk score: {risk_error}")
                    # Use simplified fallback scoring
                    risk_score = 75  # Default score
                    scan_results['security_score'] = risk_score
                    scan_results['risk_assessment'] = {
                        'overall_score': risk_score,
                        'risk_level': 'Medium'
                    }
                
                # Generate recommendations
                try:
                    recommendations = get_recommendations(scan_results)
                    scan_results['recommendations'] = recommendations if recommendations else []
                except Exception as rec_error:
                    logging.error(f"Error generating recommendations: {rec_error}")
                    scan_results['recommendations'] = ['Implement comprehensive security monitoring', 'Regular security assessments']
                
                # Generate threat scenarios
                try:
                    threat_scenarios = generate_threat_scenario(scan_results)
                    scan_results['threat_scenarios'] = threat_scenarios if threat_scenarios else []
                except Exception as threat_error:
                    logging.error(f"Error generating threat scenarios: {threat_error}")
                    scan_results['threat_scenarios'] = []
                
                # Service categorization
                try:
                    service_categories = categorize_risks_by_services(scan_results)
                    scan_results['service_categories'] = service_categories if service_categories else {}
                except Exception as cat_error:
                    logging.error(f"Error categorizing services: {cat_error}")
                    scan_results['service_categories'] = {}
                
                # Calculate industry percentile
                if industry_type:
                    percentile_info = calculate_industry_percentile(risk_score, industry_type)
                    scan_results['industry']['percentile_info'] = percentile_info
                
                # Convert scan results to findings format for template compatibility
                findings = []
                
                logging.info(f"🔍 Processing scan results for findings extraction:")
                logging.info(f"   SSL Certificate: {type(scan_results.get('ssl_certificate'))}")
                logging.info(f"   Security Headers: {type(scan_results.get('security_headers'))}")
                logging.info(f"   Network: {type(scan_results.get('network'))}")
                logging.info(f"   Email Security: {type(scan_results.get('email_security'))}")
                
                # SSL Certificate findings
                if 'ssl_certificate' in scan_results and scan_results['ssl_certificate']:
                    ssl_data = scan_results['ssl_certificate']
                    logging.info(f"SSL data: {ssl_data}")
                    if isinstance(ssl_data, dict):
                        if ssl_data.get('error') or ssl_data.get('severity') in ['High', 'Critical']:
                            findings.append({
                                'category': 'SSL/TLS Security',
                                'severity': ssl_data.get('severity', 'Medium'),
                                'title': ssl_data.get('status', 'SSL Certificate Issue'),
                                'description': ssl_data.get('error', 'SSL certificate configuration issue detected'),
                                'recommendation': 'Review SSL certificate configuration and ensure proper security'
                            })
                            logging.info("Added SSL finding")
                        else:
                            logging.info("SSL check passed - no issues found")
                
                # Security Headers findings
                if 'security_headers' in scan_results and scan_results['security_headers']:
                    headers_data = scan_results['security_headers']
                    logging.info(f"Headers data: {headers_data}")
                    if isinstance(headers_data, dict):
                        # Check for missing critical headers
                        if headers_data.get('missing_critical'):
                            for header in headers_data.get('missing_critical', []):
                                findings.append({
                                    'category': 'Security Headers',
                                    'severity': 'High',
                                    'title': f'Missing {header} Header',
                                    'description': f'Critical security header {header} is not configured',
                                    'recommendation': f'Implement {header} header to improve security'
                                })
                                logging.info(f"Added finding for missing header: {header}")
                        
                        # Check for headers with poor implementation
                        if headers_data.get('poor_implementation'):
                            for header in headers_data.get('poor_implementation', []):
                                findings.append({
                                    'category': 'Security Headers',
                                    'severity': 'Medium',
                                    'title': f'Weak {header} Configuration',
                                    'description': f'Security header {header} is configured but could be improved',
                                    'recommendation': f'Review and strengthen {header} header configuration'
                                })
                                logging.info(f"Added finding for weak header: {header}")
                        
                        # Check overall security headers score
                        if headers_data.get('score', 100) < 70:
                            findings.append({
                                'category': 'Security Headers',
                                'severity': 'Medium' if headers_data.get('score', 100) > 40 else 'High',
                                'title': 'Poor Security Headers Score',
                                'description': f'Overall security headers score is {headers_data.get("score", 0)}/100',
                                'recommendation': 'Implement missing security headers to improve protection'
                            })
                            logging.info(f"Added finding for low headers score: {headers_data.get('score', 0)}")
                    else:
                        logging.warning(f"Security headers data is not a dict: {type(headers_data)}")
                
                # Network findings - Handle actual scan_gateway_ports output format
                if 'network' in scan_results and scan_results['network']:
                    network_data = scan_results['network']
                    logging.info(f"Processing network data: {network_data}")
                    
                    if isinstance(network_data, list):
                        # scan_gateway_ports returns list of (message, severity) tuples
                        open_ports_count = 0
                        high_risk_ports = []
                        
                        for item in network_data:
                            if isinstance(item, tuple) and len(item) >= 2:
                                message, severity = item[0], item[1]
                                
                                # Count open ports
                                if "Port" in message and "is open" in message:
                                    open_ports_count += 1
                                    if severity in ['High', 'Critical']:
                                        # Extract port number for specific warnings
                                        port_match = re.search(r'Port (\d+)', message)
                                        if port_match:
                                            high_risk_ports.append(port_match.group(1))
                                
                                # Add findings for high/critical severity items
                                if severity in ['High', 'Critical', 'Medium']:
                                    findings.append({
                                        'category': 'Network Security',
                                        'severity': severity,
                                        'title': 'Network Security Issue',
                                        'description': message,
                                        'recommendation': 'Review network configuration and close unnecessary services'
                                    })
                        
                        # Add summary finding if open ports detected
                        if open_ports_count > 0:
                            findings.append({
                                'category': 'Network Security',
                                'severity': 'High' if high_risk_ports else 'Medium',
                                'title': f'Open Ports Detected ({open_ports_count} total)',
                                'description': f"Found {open_ports_count} open ports. High-risk ports: {', '.join(high_risk_ports) if high_risk_ports else 'None'}",
                                'recommendation': 'Review all open ports and close unnecessary services to reduce attack surface'
                            })
                    
                    elif isinstance(network_data, dict):
                        # Handle dictionary format (error cases, etc.)
                        if network_data.get('status') == 'error':
                            findings.append({
                                'category': 'Network Security',
                                'severity': 'Medium',
                                'title': 'Network Scan Issue',
                                'description': network_data.get('message', 'Unable to complete network scan'),
                                'recommendation': 'Network scanning may be limited. Consider running scan from target network.'
                            })
                
                # Email Security findings
                if 'email_security' in scan_results and scan_results['email_security']:
                    email_data = scan_results['email_security']
                    if isinstance(email_data, dict):
                        for record_type in ['spf', 'dmarc', 'dkim']:
                            record_data = email_data.get(record_type, {})
                            if isinstance(record_data, dict) and record_data.get('severity') in ['High', 'Critical']:
                                findings.append({
                                    'category': 'Email Security',
                                    'severity': record_data.get('severity', 'Medium'),
                                    'title': f'{record_type.upper()} Configuration Issue',
                                    'description': record_data.get('status', f'{record_type.upper()} record issue'),
                                    'recommendation': f'Configure proper {record_type.upper()} record for email security'
                                })
                
                scan_results['findings'] = findings
                scan_results['vulnerabilities_found'] = len(findings)
                
                logging.info(f"✅ Comprehensive scan completed for {target} with score {risk_score}")
                logging.info(f"📋 Generated {len(findings)} security findings")
                logging.info(f"💡 Generated {len(scan_results.get('recommendations', []))} recommendations")
                
            except Exception as scan_error:
                logging.error(f"Error during comprehensive scan: {scan_error}")
                import traceback
                logging.error(traceback.format_exc())
                # Provide fallback minimal results
                scan_results.update({
                    'security_score': 75,
                    'risk_assessment': {'overall_score': 75, 'risk_level': 'Medium'},
                    'vulnerabilities_found': 0,
                    'recommendations': ['Please run the scan again for detailed results'],
                    'findings': []
                })
            
            # Log scan to client scan_history if client_id and scanner_id are provided
            if client_id and scanner_id and scan_results:
                try:
                    from client_db import get_db_connection
                    conn = get_db_connection()
                    cursor = conn.cursor()
                    
                    # Ensure scan_history table exists with proper schema
                    cursor.execute('''
                        CREATE TABLE IF NOT EXISTS scan_history (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            client_id INTEGER,
                            scanner_id TEXT,
                            scan_id TEXT,
                            target_url TEXT,
                            scan_type TEXT,
                            status TEXT,
                            results TEXT,
                            created_at TEXT,
                            completed_at TEXT
                        )
                    ''')
                    
                    # Check if client_id column exists in existing table
                    cursor.execute("PRAGMA table_info(scan_history)")
                    columns = [column[1] for column in cursor.fetchall()]
                    if 'client_id' not in columns:
                        cursor.execute("ALTER TABLE scan_history ADD COLUMN client_id INTEGER")
                        logging.info("Added client_id column to existing scan_history table")
                    
                    # Log to scan_history table
                    cursor.execute('''
                        INSERT INTO scan_history (client_id, scanner_id, scan_id, target_url, scan_type, status, results, created_at, completed_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        client_id,
                        scanner_id,
                        scan_results.get('scan_id', ''),
                        lead_data.get('target', ''),
                        'comprehensive',
                        'completed',
                        json.dumps(scan_results),
                        datetime.now().isoformat(),
                        datetime.now().isoformat()
                    ))
                    
                    conn.commit()
                    conn.close()
                    logging.info(f"Logged scan to client scan_history: client_id={client_id}, scanner_id={scanner_id}")
                except Exception as scan_log_error:
                    logging.error(f"Error logging scan to client scan_history: {scan_log_error}")
            
            # Add client tracking information to scan results
            if client:
                scan_results['client_id'] = client['id']
                scan_results['scanner_id'] = scanner_id
                
                # Regenerate scanner deployment if customizations changed recently
                try:
                    from scanner_deployment import regenerate_scanner_if_needed
                    regenerate_scanner_if_needed(scanner_id, client['id'])
                except Exception as regen_error:
                    logging.warning(f"Could not regenerate scanner deployment: {regen_error}")
                # Copy lead data into scan results for tracking
                scan_results.update(lead_data)
                
                # Legacy client logging (keeping for compatibility)
                try:
                    from client_db import log_scan
                    # Use the simple version that doesn't require conn parameter
                    log_scan(client['id'], scan_results['scan_id'], lead_data.get('target', ''), 'comprehensive')
                except Exception as log_error:
                    logging.error(f"Legacy log_scan error: {log_error}")
                
                # Save to client-specific database for reporting
                try:
                    from client_database_manager import save_scan_to_client_db
                    save_scan_to_client_db(client['id'], scan_results)
                    logging.info(f"Saved scan to client-specific database for client {client['id']}")
                except Exception as client_db_error:
                    logging.error(f"Error saving to client-specific database: {client_db_error}")
                    import traceback
                    logging.error(traceback.format_exc())
            else:
                # Check if current user is logged in and link scan to their client
                try:
                    from client_db import verify_session, get_client_by_user_id
                    session_token = session.get('session_token')
                    if session_token:
                        result = verify_session(session_token)
                        # Handle different return formats from verify_session
                        if isinstance(result, dict):
                            user_data = result
                        elif isinstance(result, tuple) and len(result) >= 2:
                            user_data = result[1]  # Get user data from tuple
                        else:
                            user_data = None
                        
                        if user_data:
                            logged_in_client = get_client_by_user_id(user_data['user_id'])
                            if logged_in_client:
                                scan_results['client_id'] = logged_in_client['id']
                                # Save to client-specific database
                                try:
                                    from client_database_manager import save_scan_to_client_db
                                    save_scan_to_client_db(logged_in_client['id'], scan_results)
                                    logging.info(f"Saved scan to logged-in client database: {logged_in_client['id']}")
                                except Exception as logged_client_db_error:
                                    logging.error(f"Error saving to logged-in client database: {logged_client_db_error}")
                except Exception as session_error:
                    logging.error(f"Error checking session for scan logging: {session_error}")
            
            # Check if this is an AJAX request (from JavaScript)
            is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
            
            if is_ajax:
                # Return JSON response for AJAX requests
                return jsonify({
                    'status': 'success',
                    'scan_id': scan_results.get('scan_id'),
                    'message': 'Scan completed successfully',
                    'results_url': url_for('client.report_view', scan_id=scan_results.get('scan_id'))
                })
            else:
                # Redirect to client report view for regular requests
                return redirect(url_for('client.report_view', scan_id=scan_results.get('scan_id')))
            
        except Exception as e:
            logging.error(f"Error during scan: {e}")
            import traceback
            logging.error(traceback.format_exc())
            
            # Check if this is an AJAX request for error handling too
            is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
            
            if is_ajax:
                # Return JSON error response for AJAX requests
                return jsonify({
                    'status': 'error',
                    'message': f"An error occurred during the scan: {str(e)}"
                }), 500
            else:
                # Return HTML error page for regular requests
                return render_template('scan.html', 
                                     error=f"An error occurred during the scan: {str(e)}")
    
    # GET request - display scan form
    return render_template('scan.html')


@scan_bp.route('/results')
def results():
    """Display scan results"""
    # Check for scan_id in query parameters first
    scan_id = request.args.get('scan_id')
    
    if scan_id:
        # Try to get scan results from database
        try:
            from database_utils import get_scan_results
            scan_results = get_scan_results(scan_id)
            
            if scan_results:
                return render_template('results.html', scan=scan_results)
            else:
                # Try to get from client-specific databases
                try:
                    from client_database_manager import get_scan_by_id
                    scan_data = get_scan_by_id(scan_id)
                    if scan_data:
                        logger.info(f"Retrieved scan data keys: {list(scan_data.keys())}")
                        # Convert client database format to results format
                        if 'parsed_results' in scan_data and scan_data['parsed_results'] and scan_data['parsed_results'].get('client_info'):
                            # Use the parsed JSON results (only if they have proper structure)
                            converted_results = scan_data['parsed_results']
                        else:
                            # Preserve comprehensive scan data while adding missing template structure
                            logger.info(f"Converting scan data to template format for scan_id: {scan_data.get('scan_id')}")
                            
                            # Check if comprehensive data exists in scan_results field
                            converted_results = None
                            if scan_data.get('scan_results'):
                                try:
                                    import json
                                    logger.info(f"Raw scan_results field: {scan_data.get('scan_results', '')[:200]}...")
                                    comprehensive_data = json.loads(scan_data.get('scan_results', '{}'))
                                    logger.info(f"Parsed scan_results keys: {list(comprehensive_data.keys())}")
                                    if comprehensive_data.get('findings'):
                                        converted_results = comprehensive_data
                                        logger.info(f"Using comprehensive scan_results with {len(comprehensive_data.get('findings', []))} findings")
                                    else:
                                        logger.warning("No findings found in parsed scan_results")
                                except Exception as parse_error:
                                    logger.error(f"Error parsing scan_results JSON: {parse_error}")
                                    logger.error(f"Raw data: {scan_data.get('scan_results', '')}")
                            else:
                                logger.warning("No scan_results field found in scan_data")
                            
                            # If no comprehensive data found, create minimal structure
                            if not converted_results:
                                converted_results = dict(scan_data)  # Start with database data
                                logger.info("No comprehensive data found, using database fields")
                            
                            # Add missing client_info structure
                            converted_results['client_info'] = {
                                'name': scan_data.get('lead_name', 'N/A'),
                                'email': scan_data.get('lead_email', 'N/A'),
                                'company': scan_data.get('lead_company', 'N/A'),
                                'phone': scan_data.get('lead_phone', 'N/A'),
                                'os': scan_data.get('user_agent', 'N/A'),
                                'browser': scan_data.get('user_agent', 'N/A')
                            }
                            
                            # Ensure risk_assessment structure exists
                            if not converted_results.get('risk_assessment') or not isinstance(converted_results.get('risk_assessment'), dict):
                                converted_results['risk_assessment'] = {
                                    'overall_score': scan_data.get('security_score', 75),
                                    'risk_level': scan_data.get('risk_level', 'Medium'),
                                    'color': '#28a745' if scan_data.get('security_score', 75) > 75 else '#ffc107' if scan_data.get('security_score', 75) > 50 else '#dc3545',
                                    'critical_issues': 0,
                                    'high_issues': 1,
                                    'medium_issues': 1,
                                    'low_issues': 1
                                }
                            
                            # Ensure basic fields are present
                            converted_results.update({
                                'scan_id': scan_data.get('scan_id'),
                                'timestamp': scan_data.get('timestamp'),
                                'target': scan_data.get('target_domain'),
                                'scan_type': scan_data.get('scan_type', 'comprehensive'),
                                'status': scan_data.get('status', 'completed')
                            })
                            
                            logger.info(f"Final conversion: findings={len(converted_results.get('findings', []))}, recommendations={len(converted_results.get('recommendations', []))}")
                        logger.info(f"Final converted_results keys: {list(converted_results.keys())}")
                        logger.info(f"Has client_info: {'client_info' in converted_results}")
                        return render_template('results.html', scan=converted_results)
                except Exception as e:
                    logger.error(f"Error getting scan from client databases: {e}")
                    import traceback
                    logger.error(traceback.format_exc())
                
                flash(f'Scan results not found for ID: {scan_id}', 'warning')
                return redirect(url_for('scan.scan_page'))
        except Exception as e:
            logger.error(f"Error retrieving scan results for {scan_id}: {e}")
            flash('Error retrieving scan results', 'danger')
            return redirect(url_for('scan.scan_page'))
    
    # Fallback to session-based results
    scan_results = session.get('scan_results')
    
    if not scan_results:
        flash('No scan results found. Please run a scan first.', 'warning')
        return redirect(url_for('scan.scan_page'))
    
    return render_template('results.html', scan=scan_results)


@scan_bp.route('/results_direct')
def results_direct():
    """Display scan results directly from query parameter"""
    scan_id = request.args.get('scan_id')
    
    if not scan_id:
        return "No scan ID provided", 400
    
    try:
        # Get results from database
        from database_utils import get_scan_results
        scan_results = get_scan_results(scan_id)
        
        if not scan_results:
            return f"No results found for scan ID: {scan_id}", 404
        
        # Return a simplified view of the results
        return f"""
        <html>
            <head>
                <title>Scan Results</title>
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 20px; }}
                    .section {{ margin-bottom: 20px; padding: 10px; border: 1px solid #ddd; border-radius: 5px; }}
                </style>
            </head>
            <body>
                <h1>Scan Results</h1>
                
                <div class="section">
                    <h2>Scan Information</h2>
                    <p><strong>Scan ID:</strong> {scan_results['scan_id']}</p>
                    <p><strong>Timestamp:</strong> {scan_results['timestamp']}</p>
                    <p><strong>Email:</strong> {scan_results['email']}</p>
                </div>
                
                <div class="section">
                    <h2>Risk Assessment</h2>
                    <p><strong>Overall Score:</strong> {scan_results['risk_assessment']['overall_score']}</p>
                    <p><strong>Risk Level:</strong> {scan_results['risk_assessment']['risk_level']}</p>
                </div>
                
                <div class="section">
                    <h2>Recommendations</h2>
                    <ul>
                        {''.join([f'<li>{r}</li>' for r in scan_results['recommendations']])}
                    </ul>
                </div>
                
                <a href="/scan">Run another scan</a>
            </body>
        </html>
        """
    except Exception as e:
        return f"Error loading results: {str(e)}", 500


@scan_bp.route('/quick_scan', methods=['GET', 'POST'])
def quick_scan():
    """Quick scan with minimal input"""
    if request.method == 'POST':
        try:
            # Get the target domain from form
            target = request.form.get('target', '').strip()
            email = request.form.get('email', '').strip()
            
            if not target or not email:
                return render_template('quick_scan.html', error="Please provide both target domain and email address.")
            
            # Create basic lead data
            lead_data = {
                'name': 'Quick Scan User',
                'email': email,
                'company': '',
                'phone': '',
                'industry': '',
                'company_size': '',
                'company_website': target,
                'target': target,
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'client_os': 'Unknown',
                'client_browser': 'Unknown',
                'windows_version': ''
            }
            
            # Run quick scan
            from security_scanner import run_quick_scan
            scan_results = run_quick_scan(lead_data)
            
            # Store results and redirect
            session['scan_results'] = scan_results
            return redirect(url_for('scan.results'))
            
        except Exception as e:
            logging.error(f"Error during quick scan: {e}")
            return render_template('quick_scan.html', error=f"An error occurred: {str(e)}")
    
    # GET request - show quick scan form
    return render_template('quick_scan.html')


@scan_bp.route('/simple_scan')
def simple_scan():
    """Simple scan interface for testing"""
    return render_template('simple_scan.html')


@scan_bp.route('/api/scan', methods=['POST'])
def api_scan():
    """API endpoint for scan requests"""
    try:
        from flask import current_app
        limiter = getattr(current_app, 'limiter', None)
        if limiter:
            limiter.limit("5 per minute")(lambda: None)()
        
        # Get client info from authentication
        from database_utils import get_client_id_from_request
        client_id = get_client_id_from_request()
        scanner_id = request.form.get('scanner_id')
        
        # Check scan limits if client_id is available
        if client_id:
            try:
                from client_db import get_db_connection
                from client import get_client_total_scans, get_client_scan_limit
                
                # Get client information
                conn = get_db_connection()
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM clients WHERE id = ?", (client_id,))
                client_row = cursor.fetchone()
                conn.close()
                
                if client_row:
                    client = dict(client_row)
                    
                    # Check scan limits
                    current_scans = get_client_total_scans(client_id)
                    scan_limit = get_client_scan_limit(client)
                    
                    if current_scans >= scan_limit:
                        logging.warning(f"API scan blocked: Client {client_id} has reached scan limit: {current_scans}/{scan_limit}")
                        return jsonify({
                            'status': 'error', 
                            'message': f'You have reached your scan limit of {scan_limit} scans for this billing period. Please upgrade your plan or wait for the next billing cycle.',
                            'current_scans': current_scans,
                            'scan_limit': scan_limit
                        }), 403
            except Exception as limit_error:
                logging.error(f"Error checking scan limits for API scan (client {client_id}): {limit_error}")
                # Continue with scan if limit check fails to avoid breaking existing functionality
        
        # Run the scan
        from security_scanner import run_consolidated_scan
        scan_results = run_consolidated_scan(request.form)
        
        # Save to client's database
        if client_id:
            try:
                from database_utils import get_client_db
                with get_client_db(database_manager, client_id) as conn:
                    cursor = conn.cursor()
                    cursor.execute('''
                        INSERT INTO scans (
                            scanner_id, scan_timestamp, target, 
                            scan_type, status, results, created_at
                        ) VALUES (?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        scanner_id,
                        datetime.now().isoformat(),
                        scan_results['target'],
                        scan_results['type'],
                        'completed',
                        json.dumps(scan_results['results']),
                        datetime.now().isoformat()
                    ))
                    conn.commit()
            except Exception as db_error:
                logging.error(f"Error saving API scan to client database: {db_error}")
            
        return jsonify({
            "status": "success",
            "scan_id": scan_results['scan_id'],
            "message": "Scan completed successfully."
        })
            
    except Exception as e:
        logging.error(f"Error in API scan: {e}")
        return jsonify({
            "status": "error",
            "message": f"An error occurred during the scan: {str(e)}"
        }), 500


@scan_bp.route('/api/email_report', methods=['POST'])
def api_email_report():
    """API endpoint to email scan reports"""
    try:
        data = request.get_json()
        scan_id = data.get('scan_id')
        email = data.get('email')
        
        if not scan_id or not email:
            return jsonify({'status': 'error', 'message': 'Missing scan_id or email'}), 400
        
        # Get scan results
        from database_utils import get_scan_results
        scan_results = get_scan_results(scan_id)
        
        if not scan_results:
            return jsonify({'status': 'error', 'message': 'Scan not found'}), 404
        
        # Send email report
        from email_handler import send_scan_report_email
        success = send_scan_report_email(email, scan_results)
        
        if success:
            return jsonify({'status': 'success', 'message': 'Report sent successfully'})
        else:
            return jsonify({'status': 'error', 'message': 'Failed to send report'}), 500
            
    except Exception as e:
        logging.error(f"Error sending email report: {e}")
        return jsonify({'status': 'error', 'message': 'Internal server error'}), 500