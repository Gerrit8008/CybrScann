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
        
        return jsonify({
            'routes': sorted(routes, key=lambda x: x['path']),
            'total_routes': len(routes),
            'auth_routes': [r for r in routes if 'auth' in r['endpoint']],
            'main_routes': [r for r in routes if 'main' in r['endpoint']]
        })
    except Exception as e:
        logging.error(f"Error listing routes: {e}")
        return jsonify({'error': str(e)}), 500


@main_bp.route('/auth/register', methods=['GET', 'POST'])
def auth_register_fallback():
    """Fallback auth register route"""
    if request.method == 'POST':
        # For now, redirect to existing auth system
        flash('Registration temporarily unavailable. Please try again later.', 'warning')
        return redirect(url_for('main.landing_page'))
    return render_template('auth/register.html')


@main_bp.route('/auth/login', methods=['GET', 'POST'])
def auth_login_fallback():
    """Fallback auth login route"""
    if request.method == 'POST':
        # For now, redirect to existing auth system
        flash('Login temporarily unavailable. Please try again later.', 'warning')
        return redirect(url_for('main.landing_page'))
    return render_template('auth/login.html')


@main_bp.route('/customize', methods=['GET', 'POST'])
def customize():
    """Scanner customization page"""
    if request.method == 'POST':
        try:
            # Process customization form
            from auth_utils import process_scanner_customization
            result = process_scanner_customization(request)
            
            if result['success']:
                flash('Scanner customized successfully!', 'success')
                return redirect(url_for('client.dashboard'))
            else:
                flash(result.get('message', 'Error customizing scanner'), 'danger')
                
        except Exception as e:
            logging.error(f"Error processing customization: {e}")
            flash('An error occurred while customizing your scanner', 'danger')
    
    return render_template('customize.html')