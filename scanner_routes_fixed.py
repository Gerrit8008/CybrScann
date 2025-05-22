# scanner_routes_fixed.py
from flask import Blueprint, render_template, redirect, url_for, session, request, flash, jsonify
import sqlite3
import logging
from datetime import datetime
import os
import json
import uuid
import hashlib

# Create scanner blueprint
scanner_bp = Blueprint('scanner', __name__, url_prefix='/scanner')

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

@scanner_bp.route('/create')
@client_required
def create_scanner_form(user):
    """Show scanner creation form"""
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
            flash('Client profile not found. Please complete your profile first.', 'warning')
            return redirect(url_for('client.settings'))
        
        user_client = dict(user_client)
        
        # Get existing customizations
        cursor.execute('''
            SELECT * FROM customizations 
            WHERE client_id = ?
        ''', (user_client['id'],))
        customizations = cursor.fetchone()
        
        if customizations:
            customizations = dict(customizations)
        else:
            customizations = {
                'primary_color': '#007bff',
                'secondary_color': '#6c757d',
                'email_subject': f"{user_client['business_name']} Security Report",
                'email_intro': 'Thank you for using our security scanning service.',
                'email_footer': f"Best regards,\n{user_client['business_name']} Team"
            }
        
        conn.close()
        
        return render_template(
            'scanner_form.html',
            user=user,
            client=user_client,
            customizations=customizations
        )
        
    except Exception as e:
        logging.error(f"Error in create_scanner_form: {e}")
        flash(f'Error loading scanner creation form: {str(e)}', 'danger')
        return redirect(url_for('client.dashboard'))

@scanner_bp.route('/create', methods=['POST'])
@client_required
def create_scanner(user):
    """Create a new scanner"""
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
        
        # Get form data
        scanner_name = request.form.get('scanner_name', f"{user_client['business_name']} Scanner")
        subdomain = request.form.get('subdomain', user_client['business_name'].lower().replace(' ', '-').replace('_', '-'))
        domain = request.form.get('domain', user_client['business_domain'])
        
        # Customization settings
        primary_color = request.form.get('primary_color', '#007bff')
        secondary_color = request.form.get('secondary_color', '#6c757d')
        email_subject = request.form.get('email_subject', f"{user_client['business_name']} Security Report")
        email_intro = request.form.get('email_intro', 'Thank you for using our security scanning service.')
        email_footer = request.form.get('email_footer', f"Best regards,\n{user_client['business_name']} Team")
        
        # Generate unique API key for the scanner
        scanner_api_key = hashlib.sha256(f"scanner_{client_id}_{datetime.now().isoformat()}_{uuid.uuid4()}".encode()).hexdigest()
        
        # Create scanner record
        cursor.execute('''
            INSERT INTO deployed_scanners 
            (client_id, scanner_name, subdomain, domain, deploy_status, api_key, deploy_date)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (client_id, scanner_name, subdomain, domain, 'deployed', scanner_api_key, datetime.now().isoformat()))
        
        scanner_id = cursor.lastrowid
        
        # Update or create customizations
        cursor.execute('''
            INSERT OR REPLACE INTO customizations 
            (client_id, primary_color, secondary_color, email_subject, email_intro, email_footer, last_updated, updated_by)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (client_id, primary_color, secondary_color, email_subject, email_intro, email_footer, 
              datetime.now().isoformat(), user['id']))
        
        # Log the creation in audit log
        cursor.execute('''
            INSERT INTO audit_log 
            (user_id, action, entity_type, entity_id, changes, timestamp, ip_address)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (user['id'], 'create', 'scanner', scanner_id, 
              json.dumps({'scanner_name': scanner_name, 'subdomain': subdomain}),
              datetime.now().isoformat(), request.remote_addr))
        
        conn.commit()
        conn.close()
        
        flash(f'Scanner "{scanner_name}" created successfully!', 'success')
        return redirect(url_for('scanner.scanner_deployed', scanner_id=scanner_id))
        
    except Exception as e:
        logging.error(f"Error creating scanner: {e}")
        flash(f'Error creating scanner: {str(e)}', 'danger')
        return redirect(url_for('scanner.create_scanner_form'))

@scanner_bp.route('/deployed/<int:scanner_id>')
@client_required
def scanner_deployed(user, scanner_id):
    """Show scanner deployment success page"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get scanner information with client verification
        cursor.execute('''
            SELECT ds.*, c.business_name, c.business_domain
            FROM deployed_scanners ds
            JOIN clients c ON ds.client_id = c.id
            WHERE ds.id = ? AND c.user_id = ?
        ''', (scanner_id, user['id']))
        
        scanner = cursor.fetchone()
        
        if not scanner:
            flash('Scanner not found', 'danger')
            return redirect(url_for('client.scanners'))
        
        scanner = dict(scanner)
        
        # Get customizations
        cursor.execute('''
            SELECT * FROM customizations 
            WHERE client_id = ?
        ''', (scanner['client_id'],))
        customizations = cursor.fetchone()
        
        if customizations:
            customizations = dict(customizations)
        
        conn.close()
        
        # Generate the scanner URL
        scanner_url = f"https://{scanner['subdomain']}.yourscannerdomain.com"
        
        return render_template(
            'client/scanner_deployed.html',
            user=user,
            scanner=scanner,
            customizations=customizations,
            scanner_url=scanner_url
        )
        
    except Exception as e:
        logging.error(f"Error in scanner_deployed: {e}")
        flash(f'Error loading scanner information: {str(e)}', 'danger')
        return redirect(url_for('client.scanners'))

@scanner_bp.route('/preview/<int:scanner_id>')
@client_required
def preview_scanner(user, scanner_id):
    """Preview scanner interface"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get scanner information with client verification
        cursor.execute('''
            SELECT ds.*, c.business_name, c.business_domain, c.contact_email
            FROM deployed_scanners ds
            JOIN clients c ON ds.client_id = c.id
            WHERE ds.id = ? AND c.user_id = ?
        ''', (scanner_id, user['id']))
        
        scanner = cursor.fetchone()
        
        if not scanner:
            flash('Scanner not found', 'danger')
            return redirect(url_for('client.scanners'))
        
        scanner = dict(scanner)
        
        # Get customizations
        cursor.execute('''
            SELECT * FROM customizations 
            WHERE client_id = ?
        ''', (scanner['client_id'],))
        customizations = cursor.fetchone()
        
        if customizations:
            customizations = dict(customizations)
        else:
            customizations = {
                'primary_color': '#007bff',
                'secondary_color': '#6c757d',
                'email_subject': f"{scanner['business_name']} Security Report",
                'email_intro': 'Thank you for using our security scanning service.',
                'email_footer': f"Best regards,\n{scanner['business_name']} Team"
            }
        
        conn.close()
        
        return render_template(
            'client/scanner_preview.html',
            user=user,
            scanner=scanner,
            customizations=customizations
        )
        
    except Exception as e:
        logging.error(f"Error in preview_scanner: {e}")
        flash(f'Error loading scanner preview: {str(e)}', 'danger')
        return redirect(url_for('client.scanners'))

@scanner_bp.route('/customize/<int:scanner_id>')
@client_required
def customize_scanner(user, scanner_id):
    """Show scanner customization form"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get scanner information with client verification
        cursor.execute('''
            SELECT ds.*, c.business_name, c.business_domain
            FROM deployed_scanners ds
            JOIN clients c ON ds.client_id = c.id
            WHERE ds.id = ? AND c.user_id = ?
        ''', (scanner_id, user['id']))
        
        scanner = cursor.fetchone()
        
        if not scanner:
            flash('Scanner not found', 'danger')
            return redirect(url_for('client.scanners'))
        
        scanner = dict(scanner)
        
        # Get customizations
        cursor.execute('''
            SELECT * FROM customizations 
            WHERE client_id = ?
        ''', (scanner['client_id'],))
        customizations = cursor.fetchone()
        
        if customizations:
            customizations = dict(customizations)
        
        conn.close()
        
        return render_template(
            'client/customize_scanner.html',
            user=user,
            scanner=scanner,
            customizations=customizations
        )
        
    except Exception as e:
        logging.error(f"Error in customize_scanner: {e}")
        flash(f'Error loading scanner customization: {str(e)}', 'danger')
        return redirect(url_for('client.scanners'))

@scanner_bp.route('/customize/<int:scanner_id>', methods=['POST'])
@client_required
def update_scanner_customization(user, scanner_id):
    """Update scanner customization"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Verify scanner ownership
        cursor.execute('''
            SELECT ds.client_id
            FROM deployed_scanners ds
            JOIN clients c ON ds.client_id = c.id
            WHERE ds.id = ? AND c.user_id = ?
        ''', (scanner_id, user['id']))
        
        result = cursor.fetchone()
        
        if not result:
            flash('Scanner not found', 'danger')
            return redirect(url_for('client.scanners'))
        
        client_id = result['client_id']
        
        # Get form data
        primary_color = request.form.get('primary_color', '#007bff')
        secondary_color = request.form.get('secondary_color', '#6c757d')
        email_subject = request.form.get('email_subject', '')
        email_intro = request.form.get('email_intro', '')
        email_footer = request.form.get('email_footer', '')
        css_override = request.form.get('css_override', '')
        
        # Update customizations
        cursor.execute('''
            INSERT OR REPLACE INTO customizations 
            (client_id, primary_color, secondary_color, email_subject, email_intro, email_footer, css_override, last_updated, updated_by)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (client_id, primary_color, secondary_color, email_subject, email_intro, email_footer, css_override,
              datetime.now().isoformat(), user['id']))
        
        # Update scanner last_updated timestamp
        cursor.execute('''
            UPDATE deployed_scanners 
            SET last_updated = ?
            WHERE id = ?
        ''', (datetime.now().isoformat(), scanner_id))
        
        # Log the update in audit log
        cursor.execute('''
            INSERT INTO audit_log 
            (user_id, action, entity_type, entity_id, changes, timestamp, ip_address)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (user['id'], 'update', 'scanner_customization', scanner_id, 
              json.dumps({'primary_color': primary_color, 'secondary_color': secondary_color}),
              datetime.now().isoformat(), request.remote_addr))
        
        conn.commit()
        conn.close()
        
        flash('Scanner customization updated successfully!', 'success')
        return redirect(url_for('scanner.preview_scanner', scanner_id=scanner_id))
        
    except Exception as e:
        logging.error(f"Error updating scanner customization: {e}")
        flash(f'Error updating customization: {str(e)}', 'danger')
        return redirect(url_for('scanner.customize_scanner', scanner_id=scanner_id))

@scanner_bp.route('/delete/<int:scanner_id>', methods=['POST'])
@client_required
def delete_scanner(user, scanner_id):
    """Delete a scanner"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Verify scanner ownership
        cursor.execute('''
            SELECT ds.*, c.business_name
            FROM deployed_scanners ds
            JOIN clients c ON ds.client_id = c.id
            WHERE ds.id = ? AND c.user_id = ?
        ''', (scanner_id, user['id']))
        
        scanner = cursor.fetchone()
        
        if not scanner:
            flash('Scanner not found', 'danger')
            return redirect(url_for('client.scanners'))
        
        scanner = dict(scanner)
        
        # Delete related scan history
        cursor.execute('DELETE FROM scan_history WHERE scanner_id = ?', (scanner_id,))
        
        # Delete the scanner
        cursor.execute('DELETE FROM deployed_scanners WHERE id = ?', (scanner_id,))
        
        # Log the deletion in audit log
        cursor.execute('''
            INSERT INTO audit_log 
            (user_id, action, entity_type, entity_id, changes, timestamp, ip_address)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (user['id'], 'delete', 'scanner', scanner_id, 
              json.dumps({'scanner_name': scanner['scanner_name']}),
              datetime.now().isoformat(), request.remote_addr))
        
        conn.commit()
        conn.close()
        
        flash(f'Scanner "{scanner["scanner_name"]}" deleted successfully', 'success')
        return redirect(url_for('client.scanners'))
        
    except Exception as e:
        logging.error(f"Error deleting scanner: {e}")
        flash(f'Error deleting scanner: {str(e)}', 'danger')
        return redirect(url_for('client.scanners'))

# Add a route for the main customize page (without scanner_id)
@scanner_bp.route('/customize')
def customize():
    """Main scanner creation/customization page"""
    return redirect(url_for('scanner.create_scanner_form'))