"""
Main routes for CybrScan
Handles landing pages, static content, and basic functionality
"""

from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for, flash
import os
import logging
import json
from datetime import datetime

# Create main blueprint
main_bp = Blueprint('main', __name__)

# Configure logging
logger = logging.getLogger(__name__)


@main_bp.route('/')
def landing_page():
    """Landing page"""
    return render_template('index.html')


@main_bp.route('/pricing')
def pricing():
    """Pricing page"""
    return render_template('pricing.html')


@main_bp.route('/about')
def about():
    """About page"""
    return render_template('about.html')


@main_bp.route('/contact')
def contact():
    """Contact page"""
    return render_template('contact.html')


@main_bp.route('/privacy')
def privacy():
    """Privacy policy page"""
    return render_template('privacy.html')


@main_bp.route('/terms')
def terms():
    """Terms of service page"""
    return render_template('terms.html')


@main_bp.route('/health')
def health_check():
    """Health check endpoint"""
    try:
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'service': 'CybrScan',
            'version': 'modular-v2.0',
            'structure': 'modular'
        })
    except Exception as e:
        logging.error(f"Health check error: {e}")
        return jsonify({
            'status': 'error',
            'timestamp': datetime.now().isoformat(),
            'error': str(e)
        }), 500


@main_bp.route('/api/healthcheck')
def api_healthcheck():
    """API health check endpoint"""
    try:
        # Test database connectivity
        from client_db import get_db_connection
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT 1')
        result = cursor.fetchone()
        conn.close()
        
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'database': 'connected',
            'service': 'CybrScan API'
        })
    except Exception as e:
        logging.error(f"API health check error: {e}")
        return jsonify({
            'status': 'error',
            'timestamp': datetime.now().isoformat(),
            'database': 'error',
            'error': str(e)
        }), 500


@main_bp.route('/routes')
def list_routes():
    """List all available routes (development helper)"""
    try:
        from flask import current_app
        
        routes = []
        for rule in current_app.url_map.iter_rules():
            methods = ','.join(sorted(rule.methods - {'HEAD', 'OPTIONS'}))
            routes.append({
                'endpoint': rule.endpoint,
                'methods': methods,
                'path': str(rule)
            })
        
        return jsonify({
            'routes': sorted(routes, key=lambda x: x['path']),
            'total_routes': len(routes)
        })
    except Exception as e:
        logging.error(f"Error listing routes: {e}")
        return jsonify({'error': str(e)}), 500


@main_bp.route('/api/service_inquiry', methods=['POST'])
def service_inquiry():
    """Handle service inquiry form submissions"""
    try:
        data = request.get_json() or request.form.to_dict()
        
        # Extract form data
        inquiry_data = {
            'name': data.get('name', '').strip(),
            'email': data.get('email', '').strip(),
            'company': data.get('company', '').strip(),
            'phone': data.get('phone', '').strip(),
            'message': data.get('message', '').strip(),
            'service_type': data.get('service_type', '').strip(),
            'timestamp': datetime.now().isoformat(),
            'ip_address': request.remote_addr,
            'user_agent': request.headers.get('User-Agent', '')
        }
        
        # Basic validation
        if not inquiry_data['name'] or not inquiry_data['email']:
            return jsonify({
                'status': 'error',
                'message': 'Name and email are required'
            }), 400
        
        # Email validation
        import re
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, inquiry_data['email']):
            return jsonify({
                'status': 'error',
                'message': 'Invalid email format'
            }), 400
        
        # Save inquiry to database
        try:
            from database_utils import save_service_inquiry
            inquiry_id = save_service_inquiry(inquiry_data)
            
            # Send notification email (optional)
            try:
                from email_handler import send_inquiry_notification
                send_inquiry_notification(inquiry_data)
            except Exception as email_error:
                logging.warning(f"Could not send inquiry notification: {email_error}")
            
            return jsonify({
                'status': 'success',
                'message': 'Thank you for your inquiry. We will contact you soon.',
                'inquiry_id': inquiry_id
            })
            
        except Exception as db_error:
            logging.error(f"Error saving service inquiry: {db_error}")
            return jsonify({
                'status': 'error',
                'message': 'Error processing your inquiry. Please try again.'
            }), 500
        
    except Exception as e:
        logging.error(f"Error processing service inquiry: {e}")
        return jsonify({
            'status': 'error',
            'message': 'An error occurred processing your request'
        }), 500


@main_bp.route('/clear_session')
def clear_session():
    """Clear the current session to start fresh"""
    try:
        # Clear existing session data
        session.clear()
        
        return jsonify({
            'status': 'success',
            'message': 'Session cleared successfully'
        })
    except Exception as e:
        logging.error(f"Error clearing session: {e}")
        return jsonify({
            'status': 'error',
            'message': 'Error clearing session'
        }), 500


@main_bp.route('/debug/routes')
def debug_routes():
    """Debug route to show all available routes"""
    try:
        from flask import current_app
        
        routes = []
        for rule in current_app.url_map.iter_rules():
            methods = ','.join(sorted(rule.methods - {'HEAD', 'OPTIONS'}))
            routes.append({
                'endpoint': rule.endpoint,
                'methods': methods,
                'path': str(rule)
            })
        
        auth_routes = [r for r in routes if 'auth' in r['endpoint'] or '/auth' in r['path']]
        admin_routes = [r for r in routes if 'admin' in r['endpoint'] or '/admin' in r['path']]
        
        return jsonify({
            'routes': sorted(routes, key=lambda x: x['path']),
            'total_routes': len(routes),
            'auth_routes': auth_routes,
            'admin_routes': admin_routes,
            'main_routes': [r for r in routes if 'main' in r['endpoint']],
            'has_auth_login': any('/auth/login' in r['path'] for r in routes),
            'has_auth_register': any('/auth/register' in r['path'] for r in routes),
            'has_admin_dashboard': any('/admin' in r['path'] and 'admin_dashboard' in r['endpoint'] for r in routes)
        })
    except Exception as e:
        logging.error(f"Error listing routes: {e}")
        return jsonify({'error': str(e)}), 500


# Removed fallback auth routes that were conflicting with the real auth.py blueprint
# These were causing form submissions to redirect to landing page instead of processing login/register


@main_bp.route('/customize', methods=['GET', 'POST'])
def customize():
    """Comprehensive scanner customization page with detailed options"""
    # Check if user is logged in
    session_token = session.get('session_token')
    if not session_token:
        flash('Please log in to customize your scanner', 'info')
        return redirect(url_for('auth.login'))
    
    # Verify session and get user info
    from auth_utils import verify_session
    result = verify_session(session_token)
    if result['status'] != 'success':
        flash('Please log in to access customization', 'danger')
        return redirect(url_for('auth.login'))
    
    user = result['user']
    
    # Get client information
    try:
        from client_db import get_client_by_user_id, get_db_connection
        client = get_client_by_user_id(user['user_id'])
        
        if not client:
            flash('Please complete your profile setup first', 'warning')
            return redirect(url_for('auth.complete_profile'))
        
        # Get existing customization settings
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get scanner info
        cursor.execute('SELECT * FROM scanners WHERE client_id = ? ORDER BY created_at DESC LIMIT 1', (client['id'],))
        scanner = cursor.fetchone()
        
        # Get customization settings
        cursor.execute('SELECT * FROM customizations WHERE client_id = ?', (client['id'],))
        customization = cursor.fetchone()
        
        conn.close()
        
        if request.method == 'POST':
            # Process customization form submission
            try:
                import os
                from werkzeug.utils import secure_filename
                
                # Handle file uploads
                logo_url = None
                favicon_url = None
                
                if 'logo' in request.files and request.files['logo'].filename:
                    logo_file = request.files['logo']
                    if logo_file and allowed_file(logo_file.filename):
                        filename = secure_filename(f"logo_{client['id']}_{logo_file.filename}")
                        logo_path = os.path.join('static/uploads', filename)
                        os.makedirs(os.path.dirname(logo_path), exist_ok=True)
                        logo_file.save(logo_path)
                        logo_url = f'/static/uploads/{filename}'
                
                if 'favicon' in request.files and request.files['favicon'].filename:
                    favicon_file = request.files['favicon']
                    if favicon_file and allowed_file(favicon_file.filename):
                        filename = secure_filename(f"favicon_{client['id']}_{favicon_file.filename}")
                        favicon_path = os.path.join('static/uploads', filename)
                        os.makedirs(os.path.dirname(favicon_path), exist_ok=True)
                        favicon_file.save(favicon_path)
                        favicon_url = f'/static/uploads/{filename}'
                
                # Get form data
                customization_data = {
                    'scanner_name': request.form.get('scanner_name', ''),
                    'company_name': request.form.get('company_name', ''),
                    'primary_color': request.form.get('primary_color', '#02054c'),
                    'secondary_color': request.form.get('secondary_color', '#35a310'),
                    'button_color': request.form.get('button_color', '#28a745'),
                    'welcome_message': request.form.get('welcome_message', ''),
                    'email_subject': request.form.get('email_subject', 'Your Security Scan Report'),
                    'email_intro': request.form.get('email_intro', ''),
                    'contact_email': request.form.get('contact_email', ''),
                    'scan_timeout': request.form.get('scan_timeout', 300),
                    'results_retention': request.form.get('results_retention', 90),
                    'language': request.form.get('language', 'en'),
                    'scan_types': request.form.getlist('scan_types')
                }
                
                # Save customization to database
                conn = get_db_connection()
                cursor = conn.cursor()
                
                # Update or insert customization settings
                if customization:
                    cursor.execute('''
                        UPDATE customizations SET
                            primary_color = ?, secondary_color = ?, button_color = ?,
                            email_subject = ?, email_intro = ?, welcome_message = ?,
                            contact_email = ?, scan_timeout = ?, results_retention = ?,
                            language = ?, scan_types = ?, logo_url = COALESCE(?, logo_url),
                            favicon_url = COALESCE(?, favicon_url), last_updated = ?
                        WHERE client_id = ?
                    ''', (
                        customization_data['primary_color'],
                        customization_data['secondary_color'], 
                        customization_data['button_color'],
                        customization_data['email_subject'],
                        customization_data['email_intro'],
                        customization_data['welcome_message'],
                        customization_data['contact_email'],
                        customization_data['scan_timeout'],
                        customization_data['results_retention'],
                        customization_data['language'],
                        ','.join(customization_data['scan_types']),
                        logo_url, favicon_url,
                        datetime.now().isoformat(),
                        client['id']
                    ))
                else:
                    cursor.execute('''
                        INSERT INTO customizations (
                            client_id, primary_color, secondary_color, button_color,
                            email_subject, email_intro, welcome_message, contact_email,
                            scan_timeout, results_retention, language, scan_types,
                            logo_url, favicon_url, last_updated
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        client['id'],
                        customization_data['primary_color'],
                        customization_data['secondary_color'],
                        customization_data['button_color'],
                        customization_data['email_subject'],
                        customization_data['email_intro'],
                        customization_data['welcome_message'],
                        customization_data['contact_email'],
                        customization_data['scan_timeout'],
                        customization_data['results_retention'],
                        customization_data['language'],
                        ','.join(customization_data['scan_types']),
                        logo_url, favicon_url,
                        datetime.now().isoformat()
                    ))
                
                # Update scanner info if exists
                if scanner:
                    cursor.execute('''
                        UPDATE scanners SET
                            name = ?, contact_email = ?, primary_color = ?, 
                            secondary_color = ?, logo_url = COALESCE(?, logo_url)
                        WHERE id = ?
                    ''', (
                        customization_data['scanner_name'],
                        customization_data['contact_email'],
                        customization_data['primary_color'],
                        customization_data['secondary_color'],
                        logo_url,
                        scanner['id']
                    ))
                
                conn.commit()
                conn.close()
                
                flash('Scanner customization saved successfully!', 'success')
                return redirect(url_for('client.dashboard'))
                
            except Exception as e:
                logging.error(f"Error saving customization: {e}")
                flash('Error saving customization. Please try again.', 'danger')
        
        # Convert database rows to dictionaries for template
        scanner_dict = dict(scanner) if scanner else None
        customization_dict = dict(customization) if customization else None
        client_dict = dict(client) if client else None
        
        return render_template('customize.html', 
                             scanner=scanner_dict,
                             customization=customization_dict,
                             client=client_dict,
                             user=user)
        
    except Exception as e:
        logging.error(f"Error in customize route: {e}")
        flash('An error occurred while loading customization page', 'danger')
        return redirect(url_for('client.dashboard'))

def allowed_file(filename):
    """Check if file type is allowed"""
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'ico'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS