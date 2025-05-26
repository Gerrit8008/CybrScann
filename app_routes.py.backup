# app_routes.py - All route handlers and web functions

from flask import render_template, request, jsonify, session, redirect, url_for, flash, send_file
from werkzeug.utils import secure_filename
import os
import sqlite3
import time
import uuid
import logging
from datetime import datetime
import traceback

# Import configuration and utilities
from app_config import (
    logger, CLIENT_DB_PATH, UPLOAD_FOLDER, 
    generate_scan_id, get_client_ip,
    determine_industry_from_data
)

# Define missing utility functions locally
def validate_email(email):
    """Validate email format"""
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def sanitize_input(input_string):
    """Sanitize user input to prevent injection attacks"""
    if not input_string:
        return ""
    
    # Remove potentially dangerous characters
    import re
    cleaned = re.sub(r'[<>"\';]', '', str(input_string))
    return cleaned.strip()

def setup_routes(app):
    """Set up all application routes"""
    
    # Basic routes
    @app.route('/')
    def index():
        """Main landing page"""
        return render_template('index.html')

    @app.route('/pricing')
    def pricing():
        """Pricing page for MSP plans"""
        return render_template('pricing.html')

    @app.route('/health')
    def health():
        """Health check endpoint"""
        return jsonify({
            'status': 'healthy',
            'app': 'CybrScan',
            'blueprints': list(app.blueprints.keys())
        })
        
    @app.route('/auth_status')
    def auth_status():
        """Route to check authentication system status"""
        return {
            "status": "ok",
            "blueprints_registered": list(app.blueprints.keys()),
            "auth_blueprint": {
                "registered": "auth" in app.blueprints,
                "url_prefix": getattr(app.blueprints.get("auth"), "url_prefix", None)
            }
        }

    @app.route('/routes')
    def list_routes():
        """List all registered routes for debugging"""
        routes = []
        for rule in app.url_map.iter_rules():
            routes.append({
                'endpoint': rule.endpoint,
                'methods': list(rule.methods),
                'rule': str(rule)
            })
        return jsonify(routes)

    # API routes for admin functions
    @app.route('/auth/api/login-stats')
    def api_login_stats():
        """API endpoint for login statistics"""
        from client_db import get_login_stats
        
        stats = get_login_stats()
        return jsonify(stats)

    @app.route('/auth/api/check-username', methods=['POST'])
    def api_check_username():
        """API endpoint to check username availability"""
        from client_db import check_username_availability
        
        data = request.get_json()
        username = data.get('username')
        
        if not username:
            return jsonify({'available': False, 'message': 'No username provided'})
        
        result = check_username_availability(username)
        return jsonify(result)

    @app.route('/auth/api/check-email', methods=['POST'])
    def api_check_email():
        """API endpoint to check email availability"""
        from client_db import check_email_availability
        
        data = request.get_json()
        email = data.get('email')
        
        if not email:
            return jsonify({'available': False, 'message': 'No email provided'})
        
        result = check_email_availability(email)
        return jsonify(result)

    @app.route('/db_fix')
    def direct_db_fix():
        """Database fix route for admin user creation"""
        results = []
        try:
            # Define database path
            CLIENT_DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'client_scanner.db')
            results.append(f"Working with database at: {CLIENT_DB_PATH}")
            results.append(f"Database exists: {os.path.exists(CLIENT_DB_PATH)}")
            
            # Connect to the database
            conn = sqlite3.connect(CLIENT_DB_PATH)
            cursor = conn.cursor()
            
            # Check database structure
            results.append("Checking database tables...")
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            results.append(f"Found tables: {[table[0] for table in tables]}")
            
            # Create a new admin user with simple password
            results.append("Creating/updating admin user...")
            
            try:
                import secrets
                import hashlib
                
                # Generate password hash
                salt = secrets.token_hex(16)
                password = 'password123'
                password_hash = hashlib.pbkdf2_hmac(
                    'sha256', 
                    password.encode(), 
                    salt.encode(), 
                    100000
                ).hex()
                
                # Check if admin user exists
                cursor.execute("SELECT id FROM users WHERE username = 'superadmin'")
                admin_user = cursor.fetchone()
                
                if admin_user:
                    # Update existing admin
                    cursor.execute('''
                    UPDATE users SET 
                        password_hash = ?, 
                        salt = ?,
                        role = 'admin',
                        active = 1
                    WHERE username = 'superadmin'
                    ''', (password_hash, salt))
                    results.append("Updated existing superadmin user")
                else:
                    # Create a new admin user
                    cursor.execute('''
                    INSERT INTO users (
                        username, 
                        email, 
                        password_hash, 
                        salt, 
                        role, 
                        full_name, 
                        created_at, 
                        active
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, 1)
                    ''', ('superadmin', 'superadmin@example.com', password_hash, salt, 'admin', 'Super Administrator', datetime.now().isoformat()))
                    results.append("Created new superadmin user")
                
                # Commit changes
                conn.commit()
                
                # Verify creation
                cursor.execute("SELECT id, username, email, role FROM users WHERE username = 'superadmin'")
                user = cursor.fetchone()
                if user:
                    results.append(f"Superadmin user verified: ID={user[0]}, username={user[1]}, email={user[2]}, role={user[3]}")
                
                # Close connection
                conn.close()
                
                results.append("Database fix completed!")
                results.append("You can now login with:")
                results.append("Username: superadmin")
                results.append("Password: password123")
            except Exception as e:
                results.append(f"Error creating admin user: {str(e)}")
            
            return "<br>".join(results)
        except Exception as e:
            results.append(f"Error: {str(e)}")
            return "<br>".join(results)

    @app.errorhandler(404)
    def handle_404(error):
        """Handle 404 errors"""
        from flask_login import current_user
        return render_template('error.html', message="Page not found", current_user=current_user), 404

    @app.route('/login')
    def login_redirect():
        """Redirect to auth login page"""
        return redirect(url_for('auth.login'))

    @app.route('/test_redirect')
    def test_redirect():
        """Test route to verify redirects work"""
        flash('Test redirect successful!', 'success')
        return redirect('/scan')

    @app.route('/customize', methods=['GET', 'POST'])
    def customize_scanner():
        """Admin scanner customization and deployment"""
        if request.method == 'POST':
            # Add debugging at the start
            print("=" * 50)
            print("CUSTOMIZE POST REQUEST RECEIVED")
            print("=" * 50)
            logging.info("Customize POST request started")
            
            try:
                # Check if payment was processed
                payment_processed = request.form.get('payment_processed', '0')
                print(f"Payment processed flag: {payment_processed}")
                logging.info(f"Payment processed flag: {payment_processed}")
                
                # Log all form data for debugging
                print("Form data received:")
                for key, value in request.form.items():
                    print(f"  {key}: {value}")
                    logging.info(f"Form field {key}: {value}")
                
                # Handle file uploads
                logo_path = ''
                favicon_path = ''
                
                # Create uploads directory if it doesn't exist
                uploads_dir = os.path.join('static', 'uploads')
                if not os.path.exists(uploads_dir):
                    os.makedirs(uploads_dir)
                
                # Handle logo upload
                if 'logo' in request.files and request.files['logo'].filename:
                    logo_file = request.files['logo']
                    if logo_file and logo_file.filename:
                        # Validate file type
                        allowed_extensions = {'.png', '.jpg', '.jpeg', '.gif', '.svg', '.webp'}
                        filename = secure_filename(logo_file.filename)
                        name, ext = os.path.splitext(filename)
                        ext_lower = ext.lower()
                        
                        if ext_lower not in allowed_extensions:
                            flash(f'Invalid logo file type. Allowed: {", ".join(allowed_extensions)}', 'danger')
                            return render_template('admin/customization-form.html')
                        
                        # Check file size (max 5MB)
                        logo_file.seek(0, 2)  # Seek to end
                        file_size = logo_file.tell()
                        logo_file.seek(0)  # Reset to beginning
                        
                        max_size = 5 * 1024 * 1024  # 5MB
                        if file_size > max_size:
                            flash('Logo file too large. Maximum size: 5MB', 'danger')
                            return render_template('admin/customization-form.html')
                        
                        # Generate unique filename
                        timestamp = str(int(time.time()))
                        unique_filename = f"logo_{timestamp}_{name}{ext_lower}"
                        logo_file_path = os.path.join(uploads_dir, unique_filename)
                        logo_file.save(logo_file_path)
                        # Store as URL path for database
                        logo_path = f"/static/uploads/{unique_filename}"
                        logging.info(f"Logo uploaded and saved to: {logo_path}")
                
                # Handle favicon upload  
                if 'favicon' in request.files and request.files['favicon'].filename:
                    favicon_file = request.files['favicon']
                    if favicon_file and favicon_file.filename:
                        # Validate file type (more restrictive for favicons)
                        allowed_favicon_extensions = {'.png', '.ico', '.svg'}
                        filename = secure_filename(favicon_file.filename)
                        name, ext = os.path.splitext(filename)
                        ext_lower = ext.lower()
                        
                        if ext_lower not in allowed_favicon_extensions:
                            flash(f'Invalid favicon file type. Allowed: {", ".join(allowed_favicon_extensions)}', 'danger')
                            return render_template('admin/customization-form.html')
                        
                        # Check file size (max 1MB for favicons)
                        favicon_file.seek(0, 2)  # Seek to end
                        file_size = favicon_file.tell()
                        favicon_file.seek(0)  # Reset to beginning
                        
                        max_size = 1 * 1024 * 1024  # 1MB
                        if file_size > max_size:
                            flash('Favicon file too large. Maximum size: 1MB', 'danger')
                            return render_template('admin/customization-form.html')
                        
                        # Generate unique filename
                        timestamp = str(int(time.time()))
                        unique_filename = f"favicon_{timestamp}_{name}{ext_lower}"
                        favicon_file_path = os.path.join(uploads_dir, unique_filename)
                        favicon_file.save(favicon_file_path)
                        # Store as URL path for database
                        favicon_path = f"/static/uploads/{unique_filename}"
                        logging.info(f"Favicon uploaded and saved to: {favicon_path}")
                
                # Extract form data
                scanner_data = {
                    'business_name': request.form.get('business_name', '').strip(),
                    'business_domain': request.form.get('business_domain', '').strip(),
                    'contact_email': request.form.get('contact_email', '').strip(),
                    'contact_phone': request.form.get('contact_phone', '').strip(),
                    'scanner_name': request.form.get('scanner_name', '').strip(),
                    'primary_color': request.form.get('primary_color', '#02054c'),
                    'secondary_color': request.form.get('secondary_color', '#35a310'),
                    'email_subject': request.form.get('email_subject', 'Your Security Scan Report'),
                    'email_intro': request.form.get('email_intro', ''),
                    'subscription': request.form.get('subscription', 'basic'),
                    'default_scans': request.form.getlist('default_scans[]'),
                    'logo_path': logo_path,
                    'favicon_path': favicon_path,
                    'description': request.form.get('description', '')
                }
                
                logging.info(f"Creating new scanner with data: {scanner_data}")
                
                # First, create or get client
                from auth_utils import register_client
                from fix_auth import create_user
                
                # Create user if doesn't exist (for admin-created scanners)
                user_email = scanner_data['contact_email']
                username = scanner_data['business_name'].lower().replace(' ', '')
                temp_password = uuid.uuid4().hex[:12]  # Temporary password
                
                user_result = create_user(username, user_email, temp_password, 'client', scanner_data['business_name'])
                
                if user_result['status'] != 'success':
                    # User might already exist, try to find them
                    from client_db import get_db_connection
                    conn = get_db_connection()
                    cursor = conn.cursor()
                    cursor.execute('SELECT id FROM users WHERE email = ?', (user_email,))
                    user_row = cursor.fetchone()
                    conn.close()
                    
                    if user_row:
                        user_id = user_row[0]
                        logging.info(f"Using existing user with email {user_email}")
                    else:
                        flash(f'Error creating user: {user_result["message"]}', 'danger')
                        return render_template('admin/customization-form.html')
                else:
                    user_id = user_result['user_id']
                    logging.info(f"Created new user with ID: {user_id}")
                
                # Create or get client profile
                client_data = {
                    'business_name': scanner_data['business_name'],
                    'business_domain': scanner_data['business_domain'],
                    'contact_email': scanner_data['contact_email'],
                    'contact_phone': scanner_data['contact_phone'],
                    'scanner_name': scanner_data['scanner_name'],
                    'subscription_level': scanner_data['subscription'],
                    'primary_color': scanner_data['primary_color'],
                    'secondary_color': scanner_data['secondary_color'],
                    'logo_path': scanner_data.get('logo_path', ''),
                    'favicon_path': scanner_data.get('favicon_path', ''),
                    'email_subject': scanner_data['email_subject'],
                    'email_intro': scanner_data['email_intro']
                }
                
                client_result = register_client(user_id, client_data)
                
                if client_result['status'] != 'success':
                    # Try to get existing client
                    from client_db import get_client_by_user_id
                    existing_client = get_client_by_user_id(user_id)
                    if existing_client:
                        client_id = existing_client['id']
                        logging.info(f"Using existing client with ID: {client_id}")
                    else:
                        flash(f'Error creating client: {client_result["message"]}', 'danger')
                        return render_template('admin/customization-form.html')
                else:
                    client_id = client_result['client_id']
                    logging.info(f"Created new client with ID: {client_id}")
                
                # Create the scanner
                from scanner_db_functions import patch_client_db_scanner_functions, create_scanner_for_client
                patch_client_db_scanner_functions()
                
                scanner_creation_data = {
                    'name': scanner_data['scanner_name'],
                    'business_name': scanner_data['business_name'],  # Add business_name for deployment
                    'description': scanner_data.get('description', f"Security scanner for {scanner_data['business_name']}"),
                    'domain': scanner_data['business_domain'],
                    'primary_color': scanner_data['primary_color'],
                    'secondary_color': scanner_data['secondary_color'],
                    'logo_url': scanner_data.get('logo_path', ''),  # Fix: use logo_url to match database column
                    'favicon_path': scanner_data.get('favicon_path', ''),
                    'contact_email': scanner_data['contact_email'],
                    'contact_phone': scanner_data['contact_phone'],
                    'email_subject': scanner_data['email_subject'],
                    'email_intro': scanner_data['email_intro'],
                    'scan_types': scanner_data.get('default_scans', ['port_scan', 'ssl_check'])
                }
                
                scanner_result = create_scanner_for_client(client_id, scanner_creation_data, 1)  # Admin user ID 1
                
                if scanner_result['status'] != 'success':
                    flash(f'Error creating scanner: {scanner_result["message"]}', 'danger')
                    return render_template('admin/customization-form.html')
                
                scanner_id = scanner_result['scanner_id']
                scanner_uid = scanner_result['scanner_uid']
                api_key = scanner_result['api_key']
                
                # Create dedicated database for this client
                try:
                    from client_database_manager import create_client_specific_database
                    db_path = create_client_specific_database(client_id, scanner_data['business_name'])
                    if db_path:
                        logging.info(f"Created dedicated database for client {client_id}: {db_path}")
                    else:
                        logging.warning(f"Failed to create dedicated database for client {client_id}")
                except Exception as e:
                    logging.error(f"Error creating client database: {e}")
                
                logging.info(f"Scanner created successfully: ID {scanner_id}, UID {scanner_uid}")
                print(f"SCANNER CREATED: ID {scanner_id}, UID {scanner_uid}")
                print(f"SCANNER COLORS: {scanner_creation_data['primary_color']}, {scanner_creation_data['secondary_color']}")
                
                # Generate deployable HTML and API endpoints
                from scanner_deployment import generate_scanner_deployment
                print(f"GENERATING DEPLOYMENT FOR: {scanner_uid}")
                deployment_result = generate_scanner_deployment(scanner_uid, scanner_creation_data, api_key)
                print(f"DEPLOYMENT RESULT: {deployment_result['status']}")
                
                if deployment_result['status'] == 'success':
                    # Log the client in automatically after scanner creation
                    from auth_utils import create_session
                    
                    # Create a session for the new client
                    session_result = create_session(user_id, user_email, 'client')
                    if session_result['status'] == 'success':
                        session['session_token'] = session_result['session_token']
                        session['user_id'] = user_id
                        session['user_email'] = user_email
                        session['user_role'] = 'client'
                        flash('Scanner created successfully! You can now manage your scanners.', 'success')
                        
                        # Redirect to client scanners page where they can see their new scanner
                        return redirect('/client/scanners')
                    else:
                        flash('Scanner created and deployed successfully!', 'success')
                        # Redirect to scanner deployment page showing integration options  
                        return redirect(f'/scanner/{scanner_uid}/info')
                else:
                    # Even if deployment fails, log the client in and redirect to scan page
                    from auth_utils import create_session
                    session_result = create_session(user_id, user_email, 'client')
                    if session_result['status'] == 'success':
                        session['session_token'] = session_result['session_token']
                        session['user_id'] = user_id
                        session['user_email'] = user_email
                        session['user_role'] = 'client'
                    
                    flash(f'Scanner created but deployment had issues: {deployment_result["message"]}. You can still use your scanner.', 'warning')
                    return redirect('/client/scanners')
                
            except Exception as e:
                logging.error(f"Error in customize_scanner: {str(e)}")
                flash(f'Error creating scanner: {str(e)}', 'danger')
                return render_template('admin/customization-form.html')
        
        # For GET requests, render the template
        logging.info("Rendering customization form")
        return render_template('admin/customization-form.html')

    # Scan-related routes
    @app.route('/scan', methods=['GET', 'POST'])
    def scan():
        """Main scan interface"""
        if request.method == 'POST':
            # Process scan request
            target = sanitize_input(request.form.get('target', ''))
            lead_name = sanitize_input(request.form.get('lead_name', ''))
            lead_email = sanitize_input(request.form.get('lead_email', ''))
            lead_company = sanitize_input(request.form.get('lead_company', ''))
            
            if not target:
                flash('Please enter a target to scan', 'danger')
                return render_template('scan.html')
            
            if not validate_email(lead_email):
                flash('Please enter a valid email address', 'danger')
                return render_template('scan.html')
            
            # Generate scan ID and start scan
            scan_id = generate_scan_id()
            
            # Store scan data
            scan_data = {
                'scan_id': scan_id,
                'target': target,
                'lead_name': lead_name,
                'lead_email': lead_email,
                'lead_company': lead_company,
                'client_ip': get_client_ip(),
                'timestamp': datetime.now().isoformat(),
                'status': 'started'
            }
            
            # In a real implementation, you would:
            # 1. Start background scan
            # 2. Store in database
            # 3. Redirect to results page
            
            flash(f'Scan started for {target}', 'success')
            return redirect(f'/results/{scan_id}')
        
        return render_template('scan.html')

    @app.route('/results/<scan_id>')
    def results(scan_id):
        """Display scan results"""
        # In a real implementation, you would fetch results from database
        return render_template('results.html', scan_id=scan_id)

    @app.route('/scanner/<scanner_uid>/info')
    def scanner_deployment_info(scanner_uid):
        """Show scanner deployment information and integration options"""
        try:
            # Get scanner details from database
            from scanner_db_functions import patch_client_db_scanner_functions
            from client_db import get_db_connection
            
            patch_client_db_scanner_functions()
            
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute('''
            SELECT s.*, c.business_name, c.contact_email 
            FROM scanners s 
            JOIN clients c ON s.client_id = c.id 
            WHERE s.scanner_id = ?
            ''', (scanner_uid,))
            
            scanner_row = cursor.fetchone()
            conn.close()
            
            if not scanner_row:
                flash('Scanner not found', 'danger')
                return redirect('/admin/dashboard')
            
            # Convert to dict
            if hasattr(scanner_row, 'keys'):
                scanner = dict(scanner_row)
            else:
                columns = ['id', 'client_id', 'scanner_id', 'name', 'description', 'domain', 'api_key', 
                          'primary_color', 'secondary_color', 'logo_url', 'contact_email', 'contact_phone',
                          'email_subject', 'email_intro', 'scan_types', 'status', 'created_at', 'created_by',
                          'updated_at', 'updated_by', 'business_name', 'client_contact_email']
                scanner = dict(zip(columns, scanner_row))
            
            # Generate deployment URLs
            base_url = request.url_root.rstrip('/')
            deployment_info = {
                'embed_url': f"{base_url}/scanner/{scanner_uid}/embed",
                'api_url': f"{base_url}/api/scanner/{scanner_uid}",
                'docs_url': f"{base_url}/scanner/{scanner_uid}/docs",
                'download_url': f"{base_url}/scanner/{scanner_uid}/download"
            }
            
            return render_template('admin/scanner-deployment.html', 
                                 scanner=scanner, 
                                 deployment_info=deployment_info,
                                 base_url=base_url)
            
        except Exception as e:
            logging.error(f"Error loading scanner deployment info: {e}")
            flash('Error loading scanner information', 'danger')
            return redirect('/admin/dashboard')

    @app.route('/scanner/<scanner_uid>/embed')
    def scanner_embed(scanner_uid):
        """Serve the embeddable scanner HTML using main scan template"""
        try:
            # Get scanner data from database to provide branding
            from client_db import get_db_connection
            
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute('''
            SELECT s.*, c.business_name, cu.primary_color, cu.secondary_color, cu.logo_path
            FROM scanners s 
            JOIN clients c ON s.client_id = c.id 
            LEFT JOIN customizations cu ON c.id = cu.client_id
            WHERE s.scanner_id = ?
            ''', (scanner_uid,))
            
            scanner_row = cursor.fetchone()
            conn.close()
            
            if scanner_row:
                # Convert to dict for easier access
                scanner_data = dict(scanner_row) if hasattr(scanner_row, 'keys') else dict(zip([col[0] for col in cursor.description], scanner_row))
                
                # Create client branding object
                client_branding = {
                    'business_name': scanner_data.get('business_name', ''),
                    'primary_color': scanner_data.get('primary_color', '#02054c'),
                    'secondary_color': scanner_data.get('secondary_color', '#35a310'),
                    'logo_path': scanner_data.get('logo_path', ''),
                    'scanner_name': scanner_data.get('name', 'Security Scanner')
                }
                
                # Add client_id and scanner_id to URL parameters for tracking
                import urllib.parse
                client_id = scanner_data.get('client_id')
                scanner_id = scanner_data.get('scanner_id')
                
                # Render the main scan template with client branding
                return render_template('scan.html', 
                                     client_branding=client_branding,
                                     client_id=client_id,
                                     scanner_id=scanner_id,
                                     embed_mode=True)
            else:
                return render_template('scan.html', embed_mode=True)
                
        except Exception as e:
            logging.error(f"Error serving scanner embed: {e}")
            return render_template('scan.html', embed_mode=True)

    @app.route('/api/scanner/save', methods=['POST'])
    def api_scanner_save():
        """API endpoint for saving scanner data from frontend"""
        try:
            data = request.get_json()
            
            if not data:
                return jsonify({
                    'success': False,
                    'error': 'No JSON data provided'
                }), 400
            
            # Validate required fields
            required_fields = ['companyName', 'email', 'phone']
            for field in required_fields:
                if not data.get(field):
                    return jsonify({
                        'success': False,
                        'error': f'Missing required field: {field}'
                    }), 400
            
            # For now, return success with a mock scanner ID
            # In a full implementation, you would save to database
            scanner_id = str(uuid.uuid4())[:8]
            
            # Log the save attempt
            logging.info(f"Scanner save request: {data}")
            
            return jsonify({
                'success': True,
                'scannerId': scanner_id,
                'message': 'Scanner saved successfully'
            })
            
        except Exception as e:
            logging.error(f"Error in api_scanner_save: {str(e)}")
            return jsonify({
                'success': False,
                'error': 'Failed to save scanner'
            }), 500

    @app.route('/api/scanner/<scanner_uid>/scan', methods=['POST', 'OPTIONS'])
    def api_scanner_scan_simple(scanner_uid):
        """Simplified API endpoint for initiating scans"""
        # Immediate response for testing
        response = jsonify({
            'status': 'success',
            'message': 'Scan endpoint is working',
            'scanner_uid': scanner_uid,
            'scan_id': str(uuid.uuid4()),
            'debug': True
        })
        
        # Add CORS headers
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
        
        return response

    @app.route('/api/scanner/scanner_c73b04ed/scan', methods=['POST', 'OPTIONS'])
    def api_scanner_specific():
        """Specific route for the deployed scanner"""
        return jsonify({
            'status': 'success',
            'message': 'Specific scanner endpoint working',
            'scan_id': str(uuid.uuid4()),
            'scanner_uid': 'scanner_c73b04ed'
        })

    @app.route('/api/test', methods=['GET', 'POST'])
    def api_test():
        """Test API endpoint to verify routes are working"""
        return jsonify({
            'status': 'success',
            'message': 'API routes are working correctly',
            'method': request.method,
            'path': request.path
        })

    @app.route('/api/scanner/<path:subpath>', methods=['GET', 'POST', 'OPTIONS'])
    def api_scanner_debug(subpath):
        """Debug route to catch scanner API calls"""
        logging.info(f"=== SCANNER DEBUG ROUTE CALLED ===")
        logging.info(f"Method: {request.method}")
        logging.info(f"Full path: {request.path}")
        logging.info(f"Subpath: {subpath}")
        logging.info(f"Args: {request.args}")
        
        return jsonify({
            'debug': True,
            'message': f'Debug route caught: {request.path}',
            'method': request.method,
            'subpath': subpath,
            'note': 'This is the debug catch-all route'
        })

    # Emergency admin creation route
    @app.route('/emergency_admin')
    def emergency_admin():
        """Emergency admin creation route"""
        try:
            import secrets
            import hashlib
            
            # Connect to database
            conn = sqlite3.connect(CLIENT_DB_PATH)
            cursor = conn.cursor()
            
            # Create emergency admin
            salt = secrets.token_hex(16)
            password = 'emergency123'
            password_hash = hashlib.pbkdf2_hmac(
                'sha256', 
                password.encode(), 
                salt.encode(), 
                100000
            ).hex()
            
            cursor.execute('''
            INSERT OR REPLACE INTO users (
                username, email, password_hash, salt, role, 
                full_name, created_at, active
            ) VALUES (?, ?, ?, ?, ?, ?, ?, 1)
            ''', ('emergency', 'emergency@admin.com', password_hash, salt, 'admin', 
                  'Emergency Admin', datetime.now().isoformat()))
            
            conn.commit()
            conn.close()
            
            return jsonify({
                'status': 'success',
                'message': 'Emergency admin created',
                'username': 'emergency',
                'password': 'emergency123',
                'login_url': '/auth/login'
            })
            
        except Exception as e:
            return jsonify({
                'status': 'error',
                'message': str(e)
            }), 500