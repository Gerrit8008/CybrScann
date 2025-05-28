"""
Scanner-related routes for CybrScan
Handles scanner deployment, embed, API, and asset serving
"""

from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for, flash, send_file, Response
import os
import logging
import json
import uuid
from datetime import datetime, timedelta
import sqlite3
from werkzeug.utils import secure_filename

# Create scanner blueprint
scanner_bp = Blueprint('scanner', __name__)

# Configure logging
logger = logging.getLogger(__name__)


@scanner_bp.route('/scanner/<scanner_uid>/info')
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
            return redirect(url_for('admin.admin_dashboard'))
        
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
        return redirect(url_for('admin.admin_dashboard'))


@scanner_bp.route('/scanner/<scanner_uid>/embed')
def scanner_embed(scanner_uid):
    """Serve the embeddable scanner HTML using main scan template"""
    try:
        # Get scanner data from database to provide branding
        from client_db import get_db_connection
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
        SELECT s.*, c.business_name,
               COALESCE(s.primary_color, cu.primary_color, '#02054c') as final_primary_color,
               COALESCE(s.secondary_color, cu.secondary_color, '#35a310') as final_secondary_color,
               COALESCE(s.button_color, cu.button_color, '#28a745') as final_button_color,
               COALESCE(s.font_family, cu.font_family, 'Inter') as final_font_family,
               COALESCE(s.color_style, cu.color_style, 'gradient') as final_color_style,
               COALESCE(s.logo_url, cu.logo_path, '') as final_logo_url,
               COALESCE(s.email_subject, cu.email_subject, 'Your Security Scan Report') as final_email_subject,
               COALESCE(s.email_intro, cu.email_intro, '') as final_email_intro,
               cu.scanner_description, cu.cta_button_text, cu.company_tagline, 
               cu.support_email, cu.custom_footer_text, cu.favicon_path
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
            
            # Create client branding object using COALESCED final values
            client_branding = {
                'business_name': scanner_data.get('name', 'Security Scanner'),
                'primary_color': scanner_data.get('final_primary_color', '#02054c'),
                'secondary_color': scanner_data.get('final_secondary_color', '#35a310'),
                'button_color': scanner_data.get('final_button_color', '#28a745'),
                'font_family': scanner_data.get('final_font_family', 'Inter'),
                'color_style': scanner_data.get('final_color_style', 'gradient'),
                'logo_path': scanner_data.get('final_logo_url', ''),
                'logo_url': scanner_data.get('final_logo_url', ''),  # Also set logo_url for template compatibility
                'favicon_path': scanner_data.get('favicon_path', ''),
                'scanner_name': scanner_data.get('name', 'Security Scanner'),
                'email_subject': scanner_data.get('final_email_subject', 'Your Security Scan Report'),
                'email_intro': scanner_data.get('final_email_intro', ''),
                'scanner_description': scanner_data.get('scanner_description', ''),
                'cta_button_text': scanner_data.get('cta_button_text', 'Start Security Scan'),
                'company_tagline': scanner_data.get('company_tagline', ''),
                'support_email': scanner_data.get('support_email', ''),
                'custom_footer_text': scanner_data.get('custom_footer_text', '')
            }
            
            # Debug logging for branding
            logging.info(f"Scanner {scanner_uid} branding: primary={client_branding['primary_color']}, secondary={client_branding['secondary_color']}, logo={client_branding['logo_url']}")
            
            # Add client_id and scanner_id to URL parameters for tracking
            embed_url_params = f"?client_id={scanner_data.get('client_id', '')}&scanner_id={scanner_uid}"
            
            return render_template('scan.html', 
                                 client_branding=client_branding,
                                 scanner_uid=scanner_uid,
                                 scanner_id=scanner_uid,  # Add this for the form
                                 client_id=scanner_data.get('client_id'),  # Add this for the form
                                 is_embedded=True,
                                 embed_url_params=embed_url_params)
        else:
            # Fallback for scanners without branding data
            return render_template('scan.html', 
                                 client_branding=None,
                                 scanner_uid=scanner_uid,
                                 scanner_id=scanner_uid,  # Add this for the form
                                 is_embedded=True,
                                 embed_url_params=f"?scanner_id={scanner_uid}")
    
    except Exception as e:
        logging.error(f"Error serving scanner embed: {e}")
        return render_template('scan.html', 
                             client_branding=None,
                             scanner_uid=scanner_uid,
                             is_embedded=True,
                             embed_url_params=f"?scanner_id={scanner_uid}")


@scanner_bp.route('/scanner/<scanner_uid>/scanner-styles.css')
def scanner_styles(scanner_uid):
    """Serve dynamic CSS for scanner customization"""
    try:
        # Get scanner branding from database
        from client_db import get_db_connection
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
        SELECT cu.primary_color, cu.secondary_color, cu.button_color
        FROM scanners s 
        JOIN clients c ON s.client_id = c.id 
        LEFT JOIN customizations cu ON c.id = cu.client_id
        WHERE s.scanner_id = ?
        ''', (scanner_uid,))
        
        branding_row = cursor.fetchone()
        conn.close()
        
        if branding_row:
            primary_color = branding_row[0] or '#02054c'
            secondary_color = branding_row[1] or '#35a310'  
            button_color = branding_row[2] or primary_color
        else:
            primary_color = '#02054c'
            secondary_color = '#35a310'
            button_color = primary_color
        
        css_content = f"""
        /* Dynamic Scanner Styles */
        :root {{
            --primary-color: {primary_color};
            --secondary-color: {secondary_color};
            --button-color: {button_color};
        }}
        
        .btn-primary {{
            background-color: var(--button-color);
            border-color: var(--button-color);
        }}
        
        .btn-primary:hover {{
            background-color: color-mix(in srgb, var(--button-color) 85%, black);
            border-color: color-mix(in srgb, var(--button-color) 85%, black);
        }}
        
        .text-primary {{
            color: var(--primary-color) !important;
        }}
        
        .navbar-brand {{
            color: var(--primary-color) !important;
        }}
        
        .progress-bar {{
            background-color: var(--secondary-color);
        }}
        """
        
        response = Response(css_content, mimetype='text/css')
        response.headers['Cache-Control'] = 'public, max-age=3600'
        return response
        
    except Exception as e:
        logging.error(f"Error serving scanner styles: {e}")
        return Response("/* Error loading styles */", mimetype='text/css')


@scanner_bp.route('/scanner/<scanner_uid>/scanner-script.js')
def scanner_script(scanner_uid):
    """Serve dynamic JavaScript for scanner functionality"""
    try:
        js_content = f"""
        /* Dynamic Scanner JavaScript */
        console.log('Scanner {scanner_uid} initialized');
        
        // Scanner-specific functionality can be added here
        document.addEventListener('DOMContentLoaded', function() {{
            // Add any scanner-specific JavaScript functionality
            console.log('Scanner script loaded for {scanner_uid}');
        }});
        """
        
        response = Response(js_content, mimetype='application/javascript')
        response.headers['Cache-Control'] = 'public, max-age=3600'
        return response
        
    except Exception as e:
        logging.error(f"Error serving scanner script: {e}")
        return Response("/* Error loading script */", mimetype='application/javascript')


@scanner_bp.route('/scanner/<scanner_uid>/download')
def scanner_download(scanner_uid):
    """Provide downloadable scanner integration package"""
    try:
        # Get scanner details
        from client_db import get_db_connection
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT name, api_key FROM scanners WHERE scanner_id = ?', (scanner_uid,))
        scanner_row = cursor.fetchone()
        conn.close()
        
        if not scanner_row:
            flash('Scanner not found', 'danger')
            return redirect(url_for('admin.admin_dashboard'))
        
        scanner_name = scanner_row[0]
        api_key = scanner_row[1]
        
        # Create deployment package content
        base_url = request.url_root.rstrip('/')
        
        package_content = f"""
# Scanner Integration Package
Scanner: {scanner_name}
Scanner ID: {scanner_uid}

## Integration URLs
Embed URL: {base_url}/scanner/{scanner_uid}/embed
API Endpoint: {base_url}/api/scanner/{scanner_uid}/scan
API Key: {api_key}

## HTML Embed Code
<iframe src="{base_url}/scanner/{scanner_uid}/embed" 
        width="100%" 
        height="600" 
        frameborder="0">
</iframe>

## JavaScript Integration
<script>
fetch('{base_url}/api/scanner/{scanner_uid}/scan', {{
    method: 'POST',
    headers: {{
        'Content-Type': 'application/json',
        'Authorization': 'Bearer {api_key}'
    }},
    body: JSON.stringify({{
        'target_url': 'https://example.com',
        'contact_email': 'user@example.com',
        'scan_types': ['port_scan', 'vulnerability_scan']
    }})
}})
.then(response => response.json())
.then(data => console.log(data));
</script>
"""
        
        # Return as downloadable file
        response = Response(
            package_content,
            mimetype='text/plain',
            headers={'Content-Disposition': f'attachment; filename=scanner_{scanner_uid}_integration.txt'}
        )
        return response
        
    except Exception as e:
        logging.error(f"Error creating scanner download package: {e}")
        flash('Error creating download package', 'danger')
        return redirect(url_for('admin.admin_dashboard'))


@scanner_bp.route('/api/scanner/<scanner_uid>/scan', methods=['POST', 'OPTIONS'])
def api_scanner_scan(scanner_uid):
    """API endpoint to start a scan"""
    # Handle CORS preflight request
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'ok'})
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
        return response
    
    try:
        # Verify API key
        auth_header = request.headers.get('Authorization', '')
        if not auth_header.startswith('Bearer '):
            return jsonify({'status': 'error', 'message': 'Invalid authorization header'}), 401
        
        api_key = auth_header.replace('Bearer ', '')
        
        # Verify scanner and API key
        from client_db import get_db_connection
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT id, name, client_id FROM scanners WHERE scanner_id = ? AND api_key = ?', 
                      (scanner_uid, api_key))
        scanner = cursor.fetchone()
        
        if not scanner:
            conn.close()
            return jsonify({'status': 'error', 'message': 'Invalid scanner or API key'}), 401
        
        # Check scan limits for the client
        client_id = scanner[2]  # client_id is the third column
        try:
            # Get client information
            cursor.execute("SELECT * FROM clients WHERE id = ?", (client_id,))
            client_row = cursor.fetchone()
            
            if client_row:
                # Convert to dict for easier access
                client = dict(zip([col[0] for col in cursor.description], client_row))
                
                # Check scan limits
                from client import get_client_total_scans, get_client_scan_limit
                
                current_scans = get_client_total_scans(client_id)
                scan_limit = get_client_scan_limit(client)
                
                if current_scans >= scan_limit:
                    conn.close()
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
        
        # Get scan data
        scan_data = request.get_json()
        
        if not scan_data or not scan_data.get('target_url') or not scan_data.get('contact_email'):
            conn.close()
            return jsonify({'status': 'error', 'message': 'Missing required fields: target_url, contact_email'}), 400
        
        # Generate scan ID
        scan_id = f"scan_{uuid.uuid4().hex[:12]}"
        
        # Store scan in database (create table if not exists)
        try:
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS scan_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                scanner_id TEXT NOT NULL,
                scan_id TEXT UNIQUE NOT NULL,
                target_url TEXT,
                scan_type TEXT,
                status TEXT DEFAULT 'pending',
                results TEXT,
                created_at TEXT NOT NULL,
                completed_at TEXT
            )
            ''')
            
            cursor.execute('''
            INSERT INTO scan_history (scanner_id, scan_id, target_url, scan_type, status, results, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                scanner_uid,
                scan_id,
                scan_data['target_url'],
                ','.join(scan_data.get('scan_types', ['port_scan'])),
                'pending',
                json.dumps({
                    'contact_email': scan_data['contact_email'],
                    'contact_name': scan_data.get('contact_name', ''),
                    'initiated_at': datetime.now().isoformat()
                }),
                datetime.now().isoformat()
            ))
        except Exception as db_error:
            logging.warning(f"Database error, continuing without storing: {db_error}")
            # Continue without storing in database if there's an issue
        
        conn.commit()
        conn.close()
        
        # Save to client-specific database for proper scan tracking
        try:
            from client_database_manager import save_scan_to_client_db
            
            # Create enhanced scan data for client database
            enhanced_scan_data = {
                'scan_id': scan_id,
                'scanner_id': scanner_uid,
                'timestamp': datetime.now().isoformat(),
                'name': scan_data.get('contact_name', ''),
                'email': scan_data['contact_email'],
                'phone': '',
                'company': '',
                'company_size': 'Unknown',
                'target_domain': scan_data['target_url'],
                'target_url': scan_data['target_url'],
                'security_score': 85,  # Default score - should be calculated from actual scan
                'risk_level': 'Medium',
                'scan_type': 'comprehensive',
                'status': 'completed',
                'vulnerabilities_found': 0,
                'scan_results': json.dumps({
                    'contact_email': scan_data['contact_email'],
                    'contact_name': scan_data.get('contact_name', ''),
                    'initiated_at': datetime.now().isoformat(),
                    'scan_types': scan_data.get('scan_types', ['port_scan'])
                })
            }
            
            save_scan_to_client_db(scanner[2], enhanced_scan_data)  # scanner[2] is client_id
            logging.info(f"Saved API scan to client-specific database: client_id={scanner[2]}, scanner_id={scanner_uid}")
            
        except Exception as client_db_error:
            logging.error(f"Error saving API scan to client-specific database: {client_db_error}")
        
        # TODO: Trigger actual scan process here
        # For now, just return success
        
        response = jsonify({
            'status': 'success',
            'scan_id': scan_id,
            'message': 'Scan started successfully',
            'estimated_completion': (datetime.now() + timedelta(minutes=5)).isoformat()
        })
        
        # Add CORS headers
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
        
        return response
        
    except Exception as e:
        logging.error(f"Error in scanner API: {e}")
        return jsonify({'status': 'error', 'message': 'Internal server error'}), 500


@scanner_bp.route('/api/scanner/<scanner_uid>/scan/<scan_id>')
def api_scanner_scan_status(scanner_uid, scan_id):
    """API endpoint to get scan status"""
    try:
        # Verify API key
        auth_header = request.headers.get('Authorization', '')
        if not auth_header.startswith('Bearer '):
            return jsonify({'status': 'error', 'message': 'Invalid authorization header'}), 401
        
        api_key = auth_header.replace('Bearer ', '')
        
        # Get scan details
        from client_db import get_db_connection
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
        SELECT sh.*, s.api_key 
        FROM scan_history sh 
        JOIN scanners s ON sh.scanner_id = s.scanner_id 
        WHERE sh.scan_id = ? AND sh.scanner_id = ?
        ''', (scan_id, scanner_uid))
        
        scan_row = cursor.fetchone()
        conn.close()
        
        if not scan_row:
            return jsonify({'status': 'error', 'message': 'Scan not found'}), 404
        
        # Verify API key
        if scan_row[-1] != api_key:
            return jsonify({'status': 'error', 'message': 'Invalid API key'}), 401
        
        # Convert to dict
        scan = {
            'scan_id': scan_row[2],
            'target_url': scan_row[3],
            'scan_type': scan_row[4],
            'status': scan_row[5],
            'results': json.loads(scan_row[6]) if scan_row[6] else None,
            'created_at': scan_row[7],
            'completed_at': scan_row[8]
        }
        
        response = jsonify({
            'status': 'success',
            'scan': scan
        })
        
        # Add CORS headers
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
        
        return response
        
    except Exception as e:
        logging.error(f"Error getting scan status: {e}")
        return jsonify({'status': 'error', 'message': 'Internal server error'}), 500