from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
import os
import logging
import json
import time
from datetime import datetime
from functools import wraps

# Import authentication utilities and database functions
from client_db import (
    verify_session,
    get_client_by_user_id, 
    get_deployed_scanners_by_client_id,
    get_scan_history_by_client_id,
    get_scanner_by_id,
    update_scanner_config,
    regenerate_scanner_api_key,
    log_scan,
    get_scan_history,
    get_scanner_stats,
    update_client,
    get_client_statistics,
    get_recent_activities,
    get_available_scanners_for_client,
    get_client_dashboard_data,
    format_scan_results_for_client,
    register_client,
    get_scan_reports_for_client,
    get_scan_statistics_for_client,
    get_db_connection
)


def get_color_for_score(score):
    """Get appropriate color based on score"""
    if score >= 90:
        return '#28a745'  # green
    elif score >= 80:
        return '#5cb85c'  # light green
    elif score >= 70:
        return '#17a2b8'  # info blue
    elif score >= 60:
        return '#ffc107'  # warning yellow
    elif score >= 50:
        return '#fd7e14'  # orange
    else:
        return '#dc3545'  # red

# Define client blueprint
client_bp = Blueprint('client', __name__, url_prefix='/client')

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Remove duplicate imports and blueprint definition

# Middleware to require client login with role check
def client_required(f):
    @wraps(f)  # Preserve function metadata
    def decorated_function(*args, **kwargs):
        # Check for session token
        session_token = session.get('session_token')
        
        if not session_token:
            logger.debug("No session token found, redirecting to login")
            return redirect(url_for('auth.login', next=request.url))
        
        # Verify session token
        result = verify_session(session_token)
        
        if result['status'] != 'success':
            logger.debug(f"Invalid session: {result.get('message')}")
            flash('Please log in to access this page', 'danger')
            return redirect(url_for('auth.login', next=request.url))
        
        # Add role check - ensure user is a client or admin (admins can access for testing)
        if result['user']['role'] not in ['client', 'admin']:
            logger.warning(f"Access denied: User {result['user']['username']} with role {result['user']['role']} attempted to access client area")
            flash('Access denied. This area is for clients only.', 'danger')
            return redirect(url_for('auth.login'))
        
        # Log admin access for monitoring
        if result['user']['role'] == 'admin':
            logger.info(f"Admin {result['user']['username']} accessing client area for testing/management")
        
        # Add user info to kwargs
        kwargs['user'] = result['user']
        logger.debug(f"Client access granted for user: {result['user']['username']}")
        return f(*args, **kwargs)
    
    return decorated_function

def get_client_total_scans(client_id):
    """Get total number of scans used by a client in the current billing period"""
    try:
        from client_database_manager import get_client_scan_statistics
        stats = get_client_scan_statistics(client_id)
        total_scans = stats.get('total_scans', 0)
        logger.info(f"Client {client_id} total scans: {total_scans}")
        return total_scans
    except Exception as e:
        logger.error(f"Error getting client total scans for client {client_id}: {e}")
        return 0

def get_client_scan_limit(client):
    """Get scan limit based on client's subscription level"""
    if not client:
        return 10  # Default basic plan
    
    subscription_level = client.get('subscription_level', 'basic').lower()
    
    # Handle legacy plan names
    legacy_plan_mapping = {
        'business': 'professional',
        'pro': 'professional'
    }
    
    if subscription_level in legacy_plan_mapping:
        subscription_level = legacy_plan_mapping[subscription_level]
    
    # Define plan limits
    plan_limits = {
        'basic': 10,
        'starter': 50,
        'professional': 500,
        'enterprise': 1000
    }
    
    return plan_limits.get(subscription_level, 10)

def get_client_scanner_limit(client):
    """Get scanner limit based on client's subscription level"""
    if not client:
        return 1  # Default basic plan
    
    subscription_level = client.get('subscription_level', 'basic').lower()
    
    # Handle legacy plan names
    legacy_plan_mapping = {
        'business': 'professional',
        'pro': 'professional'
    }
    
    if subscription_level in legacy_plan_mapping:
        subscription_level = legacy_plan_mapping[subscription_level]
    
    # Define scanner limits
    scanner_limits = {
        'basic': 1,
        'starter': 1,
        'professional': 3,
        'enterprise': 10
    }
    
    return scanner_limits.get(subscription_level, 1)

@client_bp.route('/dashboard')
@client_required
def dashboard(user):
    """Client dashboard"""
    try:
        # Get client info for this user
        client = get_client_by_user_id(user['user_id'])
        
        # No changes to the create_scanner behavior - the critical part is that we
        # don't redirect to complete_profile, even if client is None
        # We will use default values for the dashboard if client is None
        
        if not client:
            logger.info(f"User {user['username']} has no client profile, using defaults for dashboard")
            # Create a default client object for the template
            client = {
                'id': 0,
                'business_name': user.get('full_name', '') or user.get('username', 'New Client'),
                'subscription_level': 'basic'
            }
            
            # Set default data for the dashboard
            scanners = []
            scan_history = []
            dashboard_data = {
                'client': client,
                'stats': {
                    'scanners_count': 0,
                    'total_scans': 0,
                    'avg_security_score': 0,
                    'reports_count': 0
                },
                'scanners': scanners,
                'scan_history': scan_history,
                'recent_activities': []
            }
        else:
            # Normal flow - get real data for existing client
            # Import scanner functions
            from scanner_db_functions import patch_client_db_scanner_functions, get_scanners_by_client_id
            patch_client_db_scanner_functions()
            
            # Get client's scanners
            try:
                client_scanners = get_scanners_by_client_id(client['id'])
                logger.info(f"Found {len(client_scanners) if client_scanners else 0} scanners for client {client['id']}")
                if client_scanners:
                    logger.info(f"Scanner details: {[s.get('scanner_name', s.get('name', 'Unknown')) for s in client_scanners]}")
                    logger.info(f"Scanner IDs: {[s.get('scanner_id', 'No scanner_id') for s in client_scanners]}")
            except Exception as e:
                logger.error(f"Error fetching scanners for client {client['id']}: {e}")
                client_scanners = []
            
            # Get comprehensive dashboard data - Pass client_id
            try:
                dashboard_data = get_client_dashboard_data(client['id'])
            except Exception as e:
                logger.error(f"Error fetching dashboard data for client {client['id']}: {e}")
                dashboard_data = None
            
            if not dashboard_data:
                # Fallback to basic data if comprehensive fetch fails
                try:
                    scanners = get_deployed_scanners_by_client_id(client['id'])
                    scan_history = get_scan_history_by_client_id(client['id'], limit=5)
                    total_scans = len(get_scan_history_by_client_id(client['id']))
                except Exception as e:
                    logger.error(f"Error in fallback data fetch: {e}")
                    scanners = {'scanners': []}
                    scan_history = []
                    total_scans = 0
                
                dashboard_data = {
                    'client': client,
                    'stats': {
                        'scanners_count': len(scanners.get('scanners', [])),
                        'total_scans': total_scans,
                        'avg_security_score': 75,  # Numeric default
                        'reports_count': 0
                    },
                    'scanners': scanners.get('scanners', []),
                    'scan_history': scan_history,
                    'recent_activities': []
                }
        
        # Ensure all required template variables are present
        stats = dashboard_data['stats']
        
        # FIXED: Ensure avg_security_score is a number
        try:
            avg_security_score = float(stats.get('avg_security_score', 0))
        except (ValueError, TypeError):
            avg_security_score = 0
        
        # DEBUG: Log scan history being passed to template
        scan_history = dashboard_data['scan_history']
        logger.info(f"🔍 DASHBOARD DEBUG - Passing {len(scan_history)} scans to template")
        if scan_history:
            first_scan = scan_history[0]
            logger.info(f"   First scan: ID={first_scan.get('scan_id', 'N/A')[:8]}..., Lead={first_scan.get('lead_name', 'N/A')}, Email={first_scan.get('lead_email', 'N/A')}")
        else:
            logger.warning("   ❌ No scan history to display!")
        
        # Get client data
        client_data = dashboard_data['client']
        
        # Calculate actual scanner count
        actual_scanners = client_scanners if client_scanners else dashboard_data.get('scanners', [])
        stats['scanners_count'] = len(actual_scanners)  # Add the missing scanners_count to stats
        
        template_vars = {
            'user': user,
            'client': client_data,
            'user_client': client_data,
            'stats': stats,  # Add the missing stats variable
            'scanners': client_scanners if client_scanners else dashboard_data.get('scanners', []),
            'scan_history': scan_history,
            'total_scans': stats.get('total_scans', 0),
            'client_stats': stats,
            'recent_activities': dashboard_data.get('recent_activities', []),
            # Add missing variables with proper types
            'scan_trends': {
                'scanner_growth': 0,
                'scan_growth': 0
            },
            'critical_issues': stats.get('critical_issues', 0),
            'avg_security_score': avg_security_score,  # Ensure this is a number
            'critical_issues_trend': 0,
            'security_score_trend': 0,
            'security_status': 'Good' if avg_security_score > 70 else 'Fair' if avg_security_score > 40 else 'Needs Improvement',
            'high_issues': stats.get('high_issues', 0),
            'medium_issues': stats.get('medium_issues', 0),
            'recommendations': [],  # Default empty recommendations
            'scans_used': get_client_total_scans(client_data['id']) if client_data else 0,  # Get actual scans used
            'scans_limit': get_client_scan_limit(client_data) if client_data else 50,  # Get client's scan limit based on plan
            'scanner_limit': get_client_scanner_limit(client_data) if client_data else 1  # Get client's scanner limit based on plan
        }
        
        # IMPORTANT: Ensure the correct URL for the "Create New Scanner" button
        # Make sure the button in the client-dashboard.html has the correct href
        # It should be: href="/customize"
        
        return render_template('client/client-dashboard.html', **template_vars)
        
    except Exception as e:
        logger.error(f"Error displaying client dashboard: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        
        # Fallback to basic dashboard with safe defaults
        return render_template('client/client-dashboard.html', 
                              user=user, 
                              error=str(e),
                              client={},  # Add missing client variable
                              user_client={},
                              stats={},  # Add missing stats variable
                              scanners=[],
                              scan_history=[],
                              total_scans=0,
                              client_stats={},
                              recent_activities=[],
                              scan_trends={'scanner_growth': 0, 'scan_growth': 0},
                              critical_issues=0,
                              avg_security_score=0,  # Numeric default
                              critical_issues_trend=0,
                              security_score_trend=0,
                              security_status='Unknown',
                              high_issues=0,
                              medium_issues=0,
                              recommendations=[],
                              scans_used=0,
                              scans_limit=50,
                              scanner_limit=1)
        
@client_bp.route('/scanners')
@client_required
def scanners(user):
    """List all scanners for the client"""
    try:
        # Get client info
        client = get_client_by_user_id(user['user_id'])
        
        if not client:
            # Instead of redirecting to complete_profile, just show empty scanner list
            flash('Please create your first scanner to get started', 'info')
            return render_template(
                'client/scanners.html',
                user=user,
                client={
                    'id': 0,
                    'business_name': user.get('full_name', '') or user.get('username', 'New Client'),
                    'subscription_level': 'basic'
                },
                scanners=[],
                pagination={'page': 1, 'per_page': 10, 'total_pages': 1, 'total_count': 0},
                filters={},
                scans_used=0,
                scans_limit=50,
                scanner_limit=1
            )
        
        # Get pagination parameters
        page = request.args.get('page', 1, type=int)
        per_page = 10
        
        # Get filters
        filters = {}
        if 'status' in request.args and request.args.get('status'):
            filters['status'] = request.args.get('status')
        if 'search' in request.args and request.args.get('search'):
            filters['search'] = request.args.get('search')
        
        # Get client's scanners - use the same function as the dashboard
        from scanner_db_functions import patch_client_db_scanner_functions, get_scanners_by_client_id
        patch_client_db_scanner_functions()
        
        try:
            client_scanners = get_scanners_by_client_id(client['id'])
            logger.info(f"Found {len(client_scanners) if client_scanners else 0} scanners for client {client['id']}")
            
            # Apply basic pagination to scanner list
            all_scanners = client_scanners or []
            total_count = len(all_scanners)
            start_idx = (page - 1) * per_page
            end_idx = start_idx + per_page
            paginated_scanners = all_scanners[start_idx:end_idx]
            
            # Calculate pagination info
            total_pages = (total_count + per_page - 1) // per_page
            pagination = {
                'page': page,
                'per_page': per_page,
                'total_pages': total_pages,
                'total_count': total_count
            }
            
        except Exception as e:
            logger.error(f"Error fetching scanners for client {client['id']}: {e}")
            paginated_scanners = []
            pagination = {'page': 1, 'per_page': 10, 'total_pages': 1, 'total_count': 0}
        
        # Add scan usage information
        scans_used = get_client_total_scans(client['id']) if client else 0
        scans_limit = get_client_scan_limit(client) if client else 50
        scanner_limit = get_client_scanner_limit(client) if client else 1
        
        return render_template(
            'client/scanners.html',
            user=user,
            client=client,
            scanners=paginated_scanners,
            pagination=pagination,
            filters=filters,
            scans_used=scans_used,
            scans_limit=scans_limit,
            scanner_limit=scanner_limit
        )
    except Exception as e:
        logger.error(f"Error displaying client scanners: {str(e)}")
        flash('An error occurred while loading your scanners', 'danger')
        return redirect(url_for('client.dashboard'))

@client_bp.route('/reports')
@client_required
def scan_reports(user):
    """Display detailed scan reports for the client"""
    try:
        # Get client info
        client = get_client_by_user_id(user['user_id'])
        
        if not client:
            flash('Please complete your client profile', 'info')
            return redirect(url_for('auth.complete_profile'))
        
        # Get pagination parameters
        page = request.args.get('page', 1, type=int)
        per_page = 25
        
        # Get filters
        filters = {}
        if 'search' in request.args and request.args.get('search'):
            filters['search'] = request.args.get('search')
        if 'date_from' in request.args and request.args.get('date_from'):
            filters['date_from'] = request.args.get('date_from')
        if 'date_to' in request.args and request.args.get('date_to'):
            filters['date_to'] = request.args.get('date_to')
        if 'score_min' in request.args and request.args.get('score_min'):
            filters['score_min'] = request.args.get('score_min')
        
        # Try to get scan reports from client-specific database first
        try:
            from client_database_manager import get_client_scan_reports, get_client_scan_statistics, ensure_client_database
            
            # Ensure client database exists and is properly set up
            ensure_client_database(client['id'], client.get('business_name', 'Unknown Client'))
            
            scan_reports, pagination = get_client_scan_reports(client['id'], page, per_page, filters)
            scan_stats = get_client_scan_statistics(client['id'])
            
            # If no data in client-specific database, fall back to main database
            if not scan_reports:
                scan_reports, pagination = get_scan_reports_for_client(client['id'], page, per_page, filters)
                scan_stats = get_scan_statistics_for_client(client['id'])
        except Exception as e:
            logger.error(f"Error getting client-specific scan data: {e}")
            # Fall back to main database
            scan_reports, pagination = get_scan_reports_for_client(client['id'], page, per_page, filters)
            scan_stats = get_scan_statistics_for_client(client['id'])
        
        return render_template(
            'client/scan-reports.html',
            user=user,
            client=client,
            user_client=client,
            scan_reports=scan_reports,
            pagination=pagination,
            filters=filters,
            scan_stats=scan_stats
        )
    except Exception as e:
        logger.error(f"Error displaying scan reports: {str(e)}")
        flash('An error occurred while loading scan reports', 'danger')
        return redirect(url_for('client.dashboard'))
        
@client_bp.route('/scanners/<int:scanner_id>/view')
@client_required
def scanner_view(user, scanner_id):
    """View details of a specific scanner"""
    try:
        # Get client info
        client = get_client_by_user_id(user['user_id'])
        
        if not client:
            flash('Please complete your client profile', 'info')
            return redirect(url_for('auth.complete_profile'))
        
        # Get scanner details
        scanner = get_scanner_by_id(scanner_id)
        
        if not scanner or scanner['client_id'] != client['id']:
            flash('Scanner not found', 'danger')
            return redirect(url_for('client.scanners'))
        
        # Get scan history for this scanner
        scan_history = get_scan_history_by_client_id(client['id'], limit=10)
        
        # Get scanner statistics
        stats = get_scanner_stats(scanner_id)
        
        return render_template(
            'client/scanner-view.html',
            user=user,
            client=client,
            scanner=scanner,
            scan_history=scan_history,
            stats=stats
        )
    except Exception as e:
        logger.error(f"Error displaying scanner details: {str(e)}")
        flash('An error occurred while loading scanner details', 'danger')
        return redirect(url_for('client.scanners'))

@client_bp.route('/scanners/<int:scanner_id>/edit', methods=['GET', 'POST'])
@client_required
def scanner_edit(user, scanner_id):
    """Edit scanner configuration"""
    try:
        # Get client info
        client = get_client_by_user_id(user['user_id'])
        
        if not client:
            flash('Please complete your client profile', 'info')
            return redirect(url_for('auth.complete_profile'))
        
        # Get scanner details
        scanner = get_scanner_by_id(scanner_id)
        
        if not scanner or scanner['client_id'] != client['id']:
            flash('Scanner not found', 'danger')
            return redirect(url_for('client.scanners'))
        
        if request.method == 'POST':
            # Process form submission
            scanner_data = {
                'scanner_name': request.form.get('scanner_name'),
                'business_domain': request.form.get('business_domain'),
                'contact_email': request.form.get('contact_email'),
                'contact_phone': request.form.get('contact_phone'),
                'primary_color': request.form.get('primary_color'),
                'secondary_color': request.form.get('secondary_color'),
                'button_color': request.form.get('button_color'),
                'font_family': request.form.get('font_family', 'Inter'),
                'color_style': request.form.get('color_style', 'gradient'),
                'email_subject': request.form.get('email_subject'),
                'email_intro': request.form.get('email_intro'),
                'scanner_description': request.form.get('scanner_description'),
                'cta_button_text': request.form.get('cta_button_text'),
                'company_tagline': request.form.get('company_tagline'),
                'support_email': request.form.get('support_email'),
                'custom_footer_text': request.form.get('custom_footer_text'),
                'default_scans': request.form.getlist('default_scans[]')
            }
            
            
            # Handle file uploads
            if 'logo_upload' in request.files and request.files['logo_upload'].filename:
                logo_file = request.files['logo_upload']
                try:
                    # Save logo file
                    from werkzeug.utils import secure_filename
                    
                    # Create upload directory if it doesn't exist
                    upload_dir = os.path.join('static', 'uploads')
                    os.makedirs(upload_dir, exist_ok=True)
                    
                    # Generate unique filename
                    filename = secure_filename(logo_file.filename)
                    unique_filename = f"logo_{int(time.time())}_{filename}"
                    file_path = os.path.join(upload_dir, unique_filename)
                    
                    # Save file
                    logo_file.save(file_path)
                    scanner_data['logo_path'] = f"/static/uploads/{unique_filename}"
                    scanner_data['logo_url'] = f"/static/uploads/{unique_filename}"  # Add both for compatibility
                    
                    # Also update the scanner variable for immediate display
                    scanner['logo_path'] = scanner_data['logo_path']
                    
                except Exception as e:
                    print(f"Error saving logo: {e}")
            
            if 'favicon_upload' in request.files and request.files['favicon_upload'].filename:
                favicon_file = request.files['favicon_upload']
                try:
                    # Save favicon file
                    from werkzeug.utils import secure_filename
                    
                    # Create upload directory if it doesn't exist
                    upload_dir = os.path.join('static', 'uploads')
                    os.makedirs(upload_dir, exist_ok=True)
                    
                    # Generate unique filename
                    filename = secure_filename(favicon_file.filename)
                    unique_filename = f"favicon_{int(time.time())}_{filename}"
                    file_path = os.path.join(upload_dir, unique_filename)
                    
                    # Save file
                    favicon_file.save(file_path)
                    scanner_data['favicon_path'] = f"/static/uploads/{unique_filename}"
                    
                    # Also update the scanner variable for immediate display
                    scanner['favicon_path'] = scanner_data['favicon_path']
                    
                except Exception as e:
                    print(f"Error saving favicon: {e}")
            
            # Update scanner
            try:
                result = update_scanner_config(scanner_id, scanner_data, user['user_id'])
                
                if result and result.get('status') == 'success':
                    flash('Scanner updated successfully!', 'success')
                    return redirect(url_for('client.scanners'))
                else:
                    error_msg = result.get('message', 'Unknown error') if result else 'No result returned'
                    flash(f'Failed to update scanner: {error_msg}', 'danger')
                    # If update failed, reload scanner data to show current state
                    scanner = get_scanner_by_id(scanner_id)
            except Exception as e:
                flash(f'Error updating scanner: {str(e)}', 'danger')
                # If exception, reload scanner data to show current state
                scanner = get_scanner_by_id(scanner_id)
        
        return render_template(
            'client/scanner-edit.html',
            user=user,
            client=client,
            scanner=scanner
        )
    except Exception as e:
        logger.error(f"Error editing scanner: {str(e)}")
        flash('An error occurred while editing the scanner', 'danger')
        return redirect(url_for('client.scanners'))
        
@client_bp.route('/scanners/<int:scanner_id>/stats')
@client_required
def scanner_stats(user, scanner_id):
    """View comprehensive scanner statistics"""
    try:
        # Get client info
        client = get_client_by_user_id(user['user_id'])
        
        if not client:
            flash('Please complete your client profile', 'info')
            return redirect(url_for('auth.complete_profile'))
        
        # Get scanner details
        scanner = get_scanner_by_id(scanner_id)
        
        if not scanner or scanner['client_id'] != client['id']:
            flash('Scanner not found', 'danger')
            return redirect(url_for('client.scanners'))
        
        # Get comprehensive dashboard data for enhanced statistics
        dashboard_data = get_client_dashboard_data(client['id'])
        
        # Get scanner-specific statistics
        scanner_stats = get_scanner_stats(scanner_id)
        
        # Enhanced statistics with dashboard data
        try:
            from client_database_manager import get_client_scan_statistics, get_client_scan_reports
            
            # Get all client scans for more detailed analysis
            all_scans, _ = get_client_scan_reports(client['id'], page=1, per_page=100)
            
            # Filter scans for this specific scanner
            scanner_scans = []
            if all_scans:
                scanner_uid = scanner.get('scanner_id', '')
                scanner_scans = [scan for scan in all_scans if scan.get('scanner_id') == scanner_uid or scan.get('scanner_name') == scanner.get('name')]
            
            # Calculate enhanced statistics
            statistics = {
                'total_scans': len(scanner_scans),
                'unique_companies': len(set(scan.get('lead_company', '').strip() for scan in scanner_scans if scan.get('lead_company', '').strip())),
                'avg_security_score': round(sum(scan.get('security_score', 0) for scan in scanner_scans) / len(scanner_scans)) if scanner_scans else 0,
                'conversion_rate': round((len([s for s in scanner_scans if s.get('lead_email')]) / len(scanner_scans)) * 100) if scanner_scans else 0,
                
                # Monthly trends
                'monthly_scans': {},
                
                # Risk distribution
                'risk_distribution': {'Low': 0, 'Medium': 0, 'High': 0},
                
                # Company sizes
                'company_sizes': {},
                
                # Top targets
                'top_targets': []
            }
            
            # Calculate monthly trends
            from datetime import datetime, timedelta
            import calendar
            for i in range(6):
                month_date = datetime.now() - timedelta(days=i*30)
                month_key = month_date.strftime('%Y-%m')
                month_name = calendar.month_abbr[month_date.month]
                statistics['monthly_scans'][month_name] = len([
                    scan for scan in scanner_scans 
                    if scan.get('timestamp', '').startswith(month_key)
                ])
            
            # Calculate risk distribution
            for scan in scanner_scans:
                risk = scan.get('risk_level', 'Medium')
                if risk in statistics['risk_distribution']:
                    statistics['risk_distribution'][risk] += 1
                else:
                    statistics['risk_distribution']['Medium'] += 1
            
            # Calculate company sizes
            for scan in scanner_scans:
                size = scan.get('company_size', 'Unknown')
                statistics['company_sizes'][size] = statistics['company_sizes'].get(size, 0) + 1
            
            # Calculate top targets
            target_counts = {}
            for scan in scanner_scans:
                target = scan.get('target_domain', scan.get('target_url', ''))
                if target:
                    target_counts[target] = target_counts.get(target, 0) + 1
            
            statistics['top_targets'] = sorted(target_counts.items(), key=lambda x: x[1], reverse=True)[:10]
            
            # Recent scans (last 20)
            recent_scans = sorted(scanner_scans, key=lambda x: x.get('timestamp', ''), reverse=True)[:20]
            
        except Exception as e:
            logger.error(f"Error getting enhanced statistics: {e}")
            # Fallback to basic statistics
            statistics = {
                'total_scans': scanner_stats.get('total_scans', 0),
                'unique_companies': 0,
                'avg_security_score': 75,
                'conversion_rate': 0,
                'monthly_scans': {},
                'risk_distribution': {'Low': 0, 'Medium': 0, 'High': 0},
                'company_sizes': {},
                'top_targets': []
            }
            recent_scans = []
        
        return render_template(
            'client/scanner-stats.html',
            user=user,
            client=client,
            scanner=scanner,
            statistics=statistics,
            recent_scans=recent_scans,
            dashboard_data=dashboard_data
        )
    except Exception as e:
        logger.error(f"Error displaying scanner stats: {str(e)}")
        flash('An error occurred while loading scanner statistics', 'danger')
        return redirect(url_for('client.scanners'))

@client_bp.route('/statistics')
@client_required
def client_statistics(user):
    """View comprehensive client statistics across all scanners"""
    try:
        # Get client info
        client = get_client_by_user_id(user['user_id'])
        
        if not client:
            flash('Please complete your client profile', 'info')
            return redirect(url_for('auth.complete_profile'))
        
        # Get comprehensive dashboard data
        dashboard_data = get_client_dashboard_data(client['id'])
        
        if not dashboard_data:
            flash('Unable to load statistics data', 'warning')
            return redirect(url_for('client.dashboard'))
        
        # Enhanced statistics with all client data
        try:
            from client_database_manager import get_client_scan_statistics, get_client_scan_reports
            
            # Get all client scans for comprehensive analysis
            all_scans, total_pages = get_client_scan_reports(client['id'], page=1, per_page=500)
            
            if not all_scans:
                all_scans = []
            
            # Calculate comprehensive statistics
            statistics = {
                'total_scans': len(all_scans),
                'total_scanners': len(dashboard_data['scanners']),
                'unique_companies': len(set(scan.get('lead_company', '').strip() for scan in all_scans if scan.get('lead_company', '').strip())),
                'avg_security_score': round(sum(scan.get('security_score', 0) for scan in all_scans) / len(all_scans)) if all_scans else 0,
                'conversion_rate': round((len([s for s in all_scans if s.get('lead_email')]) / len(all_scans)) * 100) if all_scans else 0,
                'total_leads': len([s for s in all_scans if s.get('lead_email') or s.get('lead_name')]),
                
                # Monthly trends (last 12 months)
                'monthly_scans': {},
                
                # Risk distribution
                'risk_distribution': {'Low': 0, 'Medium': 0, 'High': 0},
                
                # Company sizes
                'company_sizes': {},
                
                # Top targets
                'top_targets': [],
                
                # Scanner performance
                'scanner_performance': {},
                
                # Lead sources
                'lead_sources': {}
            }
            
            # Calculate monthly trends (12 months)
            from datetime import datetime, timedelta
            import calendar
            for i in range(12):
                month_date = datetime.now() - timedelta(days=i*30)
                month_key = month_date.strftime('%Y-%m')
                month_name = month_date.strftime('%b %Y')
                statistics['monthly_scans'][month_name] = len([
                    scan for scan in all_scans 
                    if scan.get('timestamp', '').startswith(month_key)
                ])
            
            # Calculate risk distribution
            for scan in all_scans:
                risk = scan.get('risk_level', 'Medium')
                if risk in statistics['risk_distribution']:
                    statistics['risk_distribution'][risk] += 1
                else:
                    statistics['risk_distribution']['Medium'] += 1
            
            # Calculate company sizes
            for scan in all_scans:
                size = scan.get('company_size', 'Unknown')
                statistics['company_sizes'][size] = statistics['company_sizes'].get(size, 0) + 1
            
            # Calculate top targets
            target_counts = {}
            for scan in all_scans:
                target = scan.get('target_domain', scan.get('target_url', ''))
                if target:
                    target_counts[target] = target_counts.get(target, 0) + 1
            
            statistics['top_targets'] = sorted(target_counts.items(), key=lambda x: x[1], reverse=True)[:15]
            
            # Calculate scanner performance
            scanner_counts = {}
            for scan in all_scans:
                scanner_name = scan.get('scanner_name', 'Unknown')
                scanner_counts[scanner_name] = scanner_counts.get(scanner_name, 0) + 1
            
            statistics['scanner_performance'] = sorted(scanner_counts.items(), key=lambda x: x[1], reverse=True)
            
            # Recent high-value scans (last 50 with lead data)
            recent_scans = [
                scan for scan in sorted(all_scans, key=lambda x: x.get('timestamp', ''), reverse=True)[:50]
                if scan.get('lead_email') or scan.get('lead_name')
            ]
            
        except Exception as e:
            logger.error(f"Error getting comprehensive statistics: {e}")
            # Fallback to dashboard data
            statistics = {
                'total_scans': dashboard_data['stats'].get('total_scans', 0),
                'total_scanners': dashboard_data['stats'].get('scanners_count', 0),
                'unique_companies': 0,
                'avg_security_score': dashboard_data['stats'].get('avg_security_score', 75),
                'conversion_rate': 0,
                'total_leads': 0,
                'monthly_scans': {},
                'risk_distribution': {'Low': 0, 'Medium': 0, 'High': 0},
                'company_sizes': {},
                'top_targets': [],
                'scanner_performance': {},
                'lead_sources': {}
            }
            recent_scans = dashboard_data['scan_history'][:20]
        
        return render_template(
            'client/client-statistics.html',
            user=user,
            client=client,
            statistics=statistics,
            recent_scans=recent_scans,
            dashboard_data=dashboard_data
        )
        
    except Exception as e:
        logger.error(f"Error displaying client statistics: {str(e)}")
        flash('An error occurred while loading statistics', 'danger')
        return redirect(url_for('client.dashboard'))

@client_bp.route('/scanners/<int:scanner_id>/regenerate-api-key', methods=['POST'])
@client_required
def scanner_regenerate_api_key(user, scanner_id):
    """Regenerate API key for a scanner"""
    try:
        # Get client info
        client = get_client_by_user_id(user['user_id'])
        
        if not client:
            return jsonify({'status': 'error', 'message': 'Client not found'})
        
        # Get scanner details
        scanner = get_scanner_by_id(scanner_id)
        
        if not scanner or scanner['client_id'] != client['id']:
            return jsonify({'status': 'error', 'message': 'Scanner not found'})
        
        # Regenerate API key
        result = regenerate_scanner_api_key(scanner_id, user['user_id'])
        
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error regenerating API key: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)})
        
        
@client_bp.route('/scanners/<int:scanner_id>/reports')
@client_required
def scanner_reports(user, scanner_id):
    """Display reports for a specific scanner"""
    try:
        # Get client info
        client = get_client_by_user_id(user['user_id'])
        
        if not client:
            flash('Please complete your client profile', 'info')
            return redirect(url_for('auth.complete_profile'))
        
        # Get scanner details to verify ownership
        scanner = get_scanner_by_id(scanner_id)
        
        if not scanner or scanner['client_id'] != client['id']:
            flash('Scanner not found', 'danger')
            return redirect(url_for('client.scanners'))
        
        # Get pagination parameters
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        # Get scan reports for this specific scanner
        try:
            from client_database_manager import get_scanner_scan_reports
            scan_reports, pagination = get_scanner_scan_reports(client['id'], scanner['scanner_id'], page, per_page)
        except Exception as e:
            logger.error(f"Error getting scanner reports: {e}")
            scan_reports, pagination = [], {'page': 1, 'per_page': per_page, 'total_pages': 1, 'total_count': 0}
        
        return render_template(
            'client/scan-reports.html',
            user=user,
            client=client,
            scanner=scanner,
            scan_reports=scan_reports,
            pagination=pagination,
            page_title=f"Reports for {scanner['name']}"
        )
        
    except Exception as e:
        logger.error(f"Error displaying scanner reports: {str(e)}")
        flash('An error occurred while loading scanner reports', 'danger')
        return redirect(url_for('client.scanners'))

@client_bp.route('/reports/<scan_id>')
@client_required
def report_view(user, scan_id):
    """View a specific scan report"""
    try:
        logger.info(f"🔍 Report view requested for scan_id: {scan_id} by user: {user.get('username', 'unknown')}")
        
        # Get client info
        client = get_client_by_user_id(user['user_id'])
        
        if not client:
            flash('Please complete your client profile', 'info')
            return redirect(url_for('auth.complete_profile'))
        
        # Get scan details from database
        scan = None
        try:
            from database_utils import get_scan_results
            scan = get_scan_results(scan_id)
        except Exception as e:
            logger.error(f"Error getting scan from database_utils: {e}")
        
        # If not found in main database, try client-specific databases
        if not scan:
            try:
                from client_database_manager import get_scan_by_id
                scan = get_scan_by_id(scan_id)
            except Exception as e:
                logger.error(f"Error getting scan from client databases: {e}")
        
        if not scan:
            logger.warning(f"❌ Scan not found for scan_id: {scan_id}")
            flash('Scan report not found', 'danger')
            return redirect(url_for('client.scan_reports'))
        
        logger.info(f"✅ Found scan {scan_id}: {scan.get('lead_email', 'unknown')} -> {scan.get('target_domain', 'unknown')}")
        
        # Verify this scan belongs to the client (basic check)
        if hasattr(scan, 'get') and scan.get('client_id') and scan.get('client_id') != client['id']:
            logger.warning(f"❌ Access denied: scan {scan_id} belongs to client {scan.get('client_id')} but user is client {client['id']}")
            flash('Access denied to this scan report', 'danger')
            return redirect(url_for('client.scan_reports'))
        
        # Get scanner branding information if available
        scanner_branding = None
        if scan and scan.get('scanner_id'):
            try:
                from client_db import get_db_connection
                conn = get_db_connection()
                cursor = conn.cursor()
                cursor.execute('''
                SELECT s.*, c.business_name,
                       COALESCE(s.primary_color, cu.primary_color, '#02054c') as final_primary_color,
                       COALESCE(s.secondary_color, cu.secondary_color, '#35a310') as final_secondary_color,
                       COALESCE(s.logo_url, cu.logo_path, '') as final_logo_url,
                       COALESCE(s.email_subject, cu.email_subject, 'Your Security Scan Report') as final_email_subject,
                       COALESCE(s.email_intro, cu.email_intro, '') as final_email_intro,
                       cu.scanner_description, cu.cta_button_text, cu.company_tagline, 
                       cu.support_email, cu.custom_footer_text, cu.favicon_path
                FROM scanners s 
                JOIN clients c ON s.client_id = c.id 
                LEFT JOIN customizations cu ON c.id = cu.client_id
                WHERE s.scanner_id = ?
                ''', (scan.get('scanner_id'),))
                
                scanner_row = cursor.fetchone()
                conn.close()
                
                if scanner_row:
                    # Convert to dict for easier access
                    scanner_data = dict(scanner_row) if hasattr(scanner_row, 'keys') else dict(zip([col[0] for col in cursor.description], scanner_row))
                    
                    # Create client branding object using COALESCED final values (same as scanner_routes.py)
                    scanner_branding = {
                        'business_name': scanner_data.get('name', scanner_data.get('business_name', '')),  # Use scanner name first
                        'primary_color': scanner_data.get('final_primary_color', '#02054c'),
                        'secondary_color': scanner_data.get('final_secondary_color', '#35a310'),
                        'button_color': scanner_data.get('final_primary_color', '#02054c'),
                        'logo_path': scanner_data.get('final_logo_url', ''),
                        'logo_url': scanner_data.get('final_logo_url', ''),
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
                    
                    logger.info(f"Retrieved scanner branding for scanner {scan.get('scanner_id')}: primary={scanner_branding['primary_color']}, secondary={scanner_branding['secondary_color']}, logo={scanner_branding['logo_url']}")
                else:
                    logger.warning(f"No scanner found for scanner_id: {scan.get('scanner_id')}")
                    
            except Exception as e:
                logger.error(f"Error getting scanner branding: {e}")
                import traceback
                logger.error(traceback.format_exc())
        
        # Format scan data for template - preserve comprehensive scan data
        formatted_scan = process_scan_data(scan)
        if scan and not scan.get('client_info'):
            # Check if this is from parsed_results (comprehensive) or raw database (minimal)
            if scan.get('parsed_results') and scan['parsed_results'].get('findings'):
                # Use the comprehensive parsed_results
                formatted_scan = scan['parsed_results']
                logger.info(f"Using comprehensive parsed_results with {len(formatted_scan.get('findings', []))} findings")
            elif scan.get('scan_results'):
                # Try to parse scan_results JSON field
                try:
                    import json
                    comprehensive_data = json.loads(scan.get('scan_results', '{}'))
                    if comprehensive_data.get('findings'):
                        formatted_scan = comprehensive_data
                        logger.info(f"Using comprehensive scan_results with {len(formatted_scan.get('findings', []))} findings")
                except:
                    pass
            
            # If we still don't have client_info, add it while preserving existing data
            if not formatted_scan.get('client_info'):
                # Copy the original scan data to preserve comprehensive results
                if isinstance(formatted_scan, dict):
                    formatted_scan = dict(formatted_scan)  # Make a copy
                else:
                    formatted_scan = dict(scan)
                
                # Add missing client_info structure without overriding existing comprehensive data
                formatted_scan['client_info'] = {
                    'name': scan.get('lead_name', formatted_scan.get('name', 'N/A')),
                    'email': scan.get('lead_email', formatted_scan.get('email', 'N/A')),
                    'company': scan.get('lead_company', formatted_scan.get('company', 'N/A')),
                    'phone': scan.get('lead_phone', 'N/A'),
                    'os': scan.get('user_agent', 'N/A'),
                    'browser': scan.get('user_agent', 'N/A')
                }
                
                # Ensure risk_assessment has required structure for template
                if not formatted_scan.get('risk_assessment') or not isinstance(formatted_scan.get('risk_assessment'), dict):
                    formatted_scan['risk_assessment'] = {
                        'overall_score': scan.get('security_score', 75),
                        'risk_level': scan.get('risk_level', 'Medium'),
                        'color': get_color_for_score(scan.get('security_score', 75)),
                        'critical_issues': 0,
                        'high_issues': 1,
                        'medium_issues': 1,
                        'low_issues': 1
                    }
                
                logger.info(f"Enhanced scan data: findings={len(formatted_scan.get('findings', []))}, recommendations={len(formatted_scan.get('recommendations', []))}")
        
        return render_template(
            'results.html',
            scan=formatted_scan,
            client_branding=scanner_branding  # Pass scanner branding as client_branding for template compatibility
        )
    except Exception as e:
        logger.error(f"Error displaying report: {str(e)}")
        flash('An error occurred while loading the report', 'danger')
        return redirect(url_for('client.reports'))

@client_bp.route('/settings', methods=['GET', 'POST'])
@client_required
def settings(user):
    """Client settings and profile management"""
    try:
        # Get client info
        client = get_client_by_user_id(user['user_id'])
        
        if not client:
            # Redirect to dashboard for auto-creation
            return redirect(url_for('client.dashboard'))
        
        # Create a default two_factor_secret for the template
        two_factor_secret = "ABCDEFGHIJKLMNOP"  # This would normally be generated
        
        if request.method == 'POST':
            action = request.form.get('action')
            
            # Handle profile update
            if action == 'update_profile':
                # Process profile update
                settings_data = {
                    'business_name': request.form.get('business_name'),
                    'business_domain': request.form.get('business_domain'),
                    'contact_email': request.form.get('contact_email'),
                    'contact_phone': request.form.get('contact_phone')
                }
                
                # Log the data being submitted for debugging
                logger.info(f"Updating client profile with data: {settings_data}")
                
                # Update the client information in the database
                result = update_client(client['id'], settings_data, user['user_id'])
                
                if result['status'] == 'success':
                    flash('Profile updated successfully', 'success')
                    # Refresh client data after update
                    client = get_client_by_user_id(user['user_id'])
                else:
                    flash(f'Failed to update profile: {result.get("message", "Unknown error")}', 'danger')
            
            # Handle notification preferences
            elif action == 'update_notifications':
                # Process notification settings
                notification_data = {
                    'notification_email': request.form.get('notification_email', '0') == '1',
                    'notification_email_address': request.form.get('notification_email_address'),
                    'notify_scan_complete': request.form.get('notify_scan_complete', '0') == '1',
                    'notify_critical_issues': request.form.get('notify_critical_issues', '0') == '1',
                    'notify_weekly_reports': request.form.get('notify_weekly_reports', '0') == '1',
                    'notification_frequency': request.form.get('notification_frequency', 'weekly')
                }
                
                # Update the client notification preferences
                result = update_client(client['id'], notification_data, user['user_id'])
                
                if result['status'] == 'success':
                    flash('Notification preferences updated', 'success')
                    # Refresh client data after update
                    client = get_client_by_user_id(user['user_id'])
                else:
                    flash(f'Failed to update preferences: {result.get("message", "Unknown error")}', 'danger')
            
            # Handle password change
            elif action == 'change_password':
                current_password = request.form.get('current_password')
                new_password = request.form.get('new_password')
                confirm_password = request.form.get('confirm_password')
                
                # Validate passwords
                if not current_password or not new_password or not confirm_password:
                    flash('All password fields are required', 'danger')
                elif new_password != confirm_password:
                    flash('New passwords do not match', 'danger')
                else:
                    # Verify current password and update to new password
                    try:
                        # Get user data for verification
                        conn = get_db_connection()
                        cursor = conn.cursor()
                        cursor.execute("SELECT password_hash, salt FROM users WHERE id = ?", (user['user_id'],))
                        user_data = cursor.fetchone()
                        conn.close()
                        
                        if not user_data:
                            flash('User not found', 'danger')
                        else:
                            # Verify current password
                            from auth_utils import hash_password
                            current_hash, _ = hash_password(current_password, user_data['salt'])
                            
                            if current_hash == user_data['password_hash']:
                                # Current password is correct, update to new password
                                new_hash, new_salt = hash_password(new_password)
                                
                                # Update password in database
                                conn = get_db_connection()
                                cursor = conn.cursor()
                                cursor.execute("""
                                    UPDATE users 
                                    SET password_hash = ?, salt = ? 
                                    WHERE id = ?
                                """, (new_hash, new_salt, user['user_id']))
                                conn.commit()
                                conn.close()
                                
                                flash('Password updated successfully', 'success')
                            else:
                                flash('Current password is incorrect', 'danger')
                    except Exception as e:
                        logger.error(f"Error updating password: {e}")
                        flash('An error occurred while updating your password', 'danger')
            
            # After processing form, redirect to same page to prevent form resubmission
            return redirect(url_for('client.settings'))
        
        # For GET requests, render the settings template with client data
        return render_template(
            'client/settings.html',
            user=user,
            client=client,
            two_factor_secret=two_factor_secret
        )
    except Exception as e:
        logger.error(f"Error in settings: {str(e)}")
        flash('An error occurred while loading settings', 'danger')
        return redirect(url_for('client.dashboard'))

def update_client(client_id, data, user_id):
    """Update client information"""
    try:
        # Log the update operation
        logger.info(f"Updating client {client_id} with data: {data}")
        
        # Connect to database
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Start with an empty update_fields dictionary and params list
        update_fields = []
        params = []
        
        # Add non-empty fields to update
        if 'business_name' in data and data['business_name']:
            update_fields.append("business_name = ?")
            params.append(data['business_name'])
            
        if 'business_domain' in data and data['business_domain']:
            update_fields.append("business_domain = ?")
            params.append(data['business_domain'])
            
        if 'contact_email' in data and data['contact_email']:
            update_fields.append("contact_email = ?")
            params.append(data['contact_email'])
            
        if 'contact_phone' in data:  # Allow empty phone
            update_fields.append("contact_phone = ?")
            params.append(data['contact_phone'])
            
        # Handle subscription changes if present
        if 'subscription_level' in data:
            update_fields.append("subscription_level = ?")
            params.append(data['subscription_level'])
            
        # Handle notification preferences
        if 'notification_email' in data:
            # Convert boolean to integer
            notification_email = 1 if data['notification_email'] else 0
            update_fields.append("notification_email = ?")
            params.append(notification_email)
            
        if 'notification_email_address' in data:
            update_fields.append("notification_email_address = ?")
            params.append(data['notification_email_address'])
            
        if 'notify_scan_complete' in data:
            notify_scan_complete = 1 if data['notify_scan_complete'] else 0
            update_fields.append("notify_scan_complete = ?")
            params.append(notify_scan_complete)
            
        if 'notify_critical_issues' in data:
            notify_critical_issues = 1 if data['notify_critical_issues'] else 0
            update_fields.append("notify_critical_issues = ?")
            params.append(notify_critical_issues)
            
        if 'notify_weekly_reports' in data:
            notify_weekly_reports = 1 if data['notify_weekly_reports'] else 0
            update_fields.append("notify_weekly_reports = ?")
            params.append(notify_weekly_reports)
            
        if 'notification_frequency' in data:
            update_fields.append("notification_frequency = ?")
            params.append(data['notification_frequency'])
        
        # Add timestamp and user_id to update
        update_fields.append("updated_at = ?")
        params.append(datetime.now().isoformat())
        
        update_fields.append("updated_by = ?")
        params.append(user_id)
        
        # Add client_id to params
        params.append(client_id)
        
        # If no fields to update, return success
        if not update_fields:
            return {"status": "success", "message": "No changes detected"}
        
        # Build and execute update query
        update_query = f"UPDATE clients SET {', '.join(update_fields)} WHERE id = ?"
        cursor.execute(update_query, params)
        
        # Log the SQL query for debugging
        logger.debug(f"Executing SQL: {update_query} with params {params}")
        
        conn.commit()
        conn.close()
        
        return {"status": "success", "message": "Client updated successfully"}
    except Exception as e:
        logger.error(f"Error updating client: {e}")
        if conn:
            conn.rollback()
            conn.close()
        return {"status": "error", "message": str(e)}

@client_bp.route('/profile')
@client_required
def profile(user):
    """Client profile page"""
    try:
        # Get client info
        client = get_client_by_user_id(user['user_id'])
        
        if not client:
            flash('Please complete your client profile', 'info')
            return redirect(url_for('auth.complete_profile'))
        
        # Get statistics for profile display
        stats = get_client_statistics(client['id'])
        
        # Get recent activities
        recent_activities = get_recent_activities(client['id'], 5)
        
        # Get available scanners
        scanners = get_available_scanners_for_client(client['id'])
        
        return render_template(
            'client/profile.html',
            user=user,
            client=client,
            client_stats=stats,
            recent_activities=recent_activities,
            scanners=scanners
        )
    except Exception as e:
        logger.error(f"Error displaying client profile: {str(e)}")
        flash('An error occurred while loading your profile', 'danger')
        return redirect(url_for('client.dashboard'))

@client_bp.route('/scanners/create', methods=['GET', 'POST'])
@client_required
def scanner_create(user):
    """Create a new scanner for the client"""
    try:
        # Get client info
        client = get_client_by_user_id(user['user_id'])
        
        if not client:
            flash('Please complete your profile first', 'warning')
            return redirect(url_for('client.profile'))
        
        # Check scanner limits based on subscription
        from client_db import get_db_connection
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM scanners WHERE client_id = ? AND status != "deleted"', (client['id'],))
        current_scanners = cursor.fetchone()[0]
        conn.close()
        
        scanner_limit = get_client_scanner_limit(client)
        
        # If at limit, redirect to upgrade page
        if current_scanners >= scanner_limit:
            flash(f'Scanner limit reached ({current_scanners}/{scanner_limit}). Please upgrade your subscription to create more scanners.', 'warning')
            return redirect(url_for('client.upgrade_subscription'))
        
        if request.method == 'POST':
            # Handle file upload
            logo_url = None
            if 'logo_upload' in request.files and request.files['logo_upload'].filename:
                logo_file = request.files['logo_upload']
                try:
                    from werkzeug.utils import secure_filename
                    import uuid
                    
                    # Create upload directory if it doesn't exist
                    upload_dir = os.path.join('static', 'uploads')
                    os.makedirs(upload_dir, exist_ok=True)
                    
                    # Generate unique filename
                    file_ext = os.path.splitext(logo_file.filename)[1]
                    filename = f"logo_{client['id']}_{uuid.uuid4().hex[:8]}{file_ext}"
                    file_path = os.path.join(upload_dir, filename)
                    
                    logo_file.save(file_path)
                    logo_url = f'/static/uploads/{filename}'
                    logger.info(f"Logo uploaded successfully: {logo_url}")
                except Exception as e:
                    logger.error(f"Error uploading logo: {e}")
                    flash('Error uploading logo, but scanner will be created without it', 'warning')
            
            # Handle favicon upload
            favicon_url = None
            if 'favicon_upload' in request.files and request.files['favicon_upload'].filename:
                favicon_file = request.files['favicon_upload']
                try:
                    from werkzeug.utils import secure_filename
                    import uuid
                    
                    # Create upload directory if it doesn't exist
                    upload_dir = os.path.join('static', 'uploads')
                    os.makedirs(upload_dir, exist_ok=True)
                    
                    # Generate unique filename
                    file_ext = os.path.splitext(favicon_file.filename)[1]
                    filename = f"favicon_{client['id']}_{uuid.uuid4().hex[:8]}{file_ext}"
                    file_path = os.path.join(upload_dir, filename)
                    
                    favicon_file.save(file_path)
                    favicon_url = f'/static/uploads/{filename}'
                    logger.info(f"Favicon uploaded successfully: {favicon_url}")
                except Exception as e:
                    logger.error(f"Error uploading favicon: {e}")
                    flash('Error uploading favicon, but scanner will be created without it', 'warning')
            
            # Get form data
            scanner_data = {
                'name': request.form.get('scanner_name', '').strip(),
                'description': request.form.get('description', '').strip(),
                'domain': request.form.get('domain', '').strip(),
                'contact_email': request.form.get('contact_email', '').strip(),
                'contact_phone': request.form.get('contact_phone', '').strip(),
                'primary_color': request.form.get('primary_color', '#02054c'),
                'secondary_color': request.form.get('secondary_color', '#35a310'),
                'button_color': request.form.get('button_color', '#28a745'),
                'font_family': request.form.get('font_family', 'Inter'),
                'color_style': request.form.get('color_style', 'gradient'),
                'logo_url': logo_url or '',
                'favicon_url': favicon_url or '',
                'contact_email': request.form.get('contact_email', client['contact_email']),
                'contact_phone': request.form.get('contact_phone', client.get('contact_phone', '')),
                'email_subject': request.form.get('email_subject', 'Your Security Scan Report'),
                'email_intro': request.form.get('email_intro', ''),
                'scan_types': request.form.getlist('scan_types[]')
            }
            
            # Validation
            if not scanner_data['name']:
                flash('Scanner name is required', 'danger')
                return render_template('client/scanner-create.html', 
                                     user=user, 
                                     client=client, 
                                     form_data=scanner_data)
            
            # Create scanner in database
            from scanner_db_functions import patch_client_db_scanner_functions, create_scanner_for_client
            patch_client_db_scanner_functions()
            result = create_scanner_for_client(client['id'], scanner_data, user['user_id'])
            
            if result.get('status') == 'success':
                scanner_uid = result.get('scanner_uid')
                flash(f'Scanner "{scanner_data["name"]}" created successfully!', 'success')
                if scanner_uid:
                    # Redirect to package selection after scanner creation
                    return redirect(url_for('client.upgrade_subscription', scanner_created=scanner_uid))
                else:
                    return redirect(url_for('client.scanners'))
            else:
                flash(f'Error creating scanner: {result.get("message", "Unknown error")}', 'danger')
                return render_template('client/scanner-create.html', 
                                     user=user, 
                                     client=client, 
                                     form_data=scanner_data)
        
        # GET request - show creation form
        return render_template('client/scanner-create.html', 
                             user=user, 
                             client=client,
                             current_scanners=current_scanners,
                             scanner_limit=scanner_limit)
        
    except Exception as e:
        logger.error(f"Error creating scanner: {str(e)}")
        flash('An error occurred while creating the scanner', 'danger')

@client_bp.route('/upgrade')
@client_required  
def upgrade_subscription(user):
    """Subscription upgrade page with payment integration"""
    try:
        # Get client info
        client = get_client_by_user_id(user['user_id'])
        
        if not client:
            flash('Please complete your profile first', 'warning')
            return redirect(url_for('client.profile'))
        
        # Get current subscription info
        current_plan = client.get('subscription_level', 'basic').lower()
        
        # Plan details with pricing
        plans = {
            'basic': {'name': 'Basic', 'price': 0, 'scanners': 1, 'scans': 10, 'api_access': False},
            'starter': {'name': 'Starter', 'price': 59, 'scanners': 1, 'scans': 50, 'api_access': True},
            'professional': {'name': 'Professional', 'price': 99, 'scanners': 3, 'scans': 500, 'api_access': True},
            'enterprise': {'name': 'Enterprise', 'price': 149, 'scanners': 10, 'scans': 1000, 'api_access': True}
        }
        
        # Handle legacy plan names - map them to new plans
        legacy_plan_mapping = {
            'business': 'professional',
            'pro': 'professional'
        }
        
        if current_plan in legacy_plan_mapping:
            current_plan = legacy_plan_mapping[current_plan]
        
        # Ensure current_plan exists in plans dictionary
        if current_plan not in plans:
            current_plan = 'basic'
        
        # Get current usage
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM scanners WHERE client_id = ? AND status != "deleted"', (client['id'],))
        current_scanners = cursor.fetchone()[0]
        conn.close()
        
        # Check if coming from scanner creation
        scanner_created = request.args.get('scanner_created')
        
        return render_template('client/upgrade-subscription.html',
                             user=user,
                             client=client,
                             current_plan=current_plan,
                             plans=plans,
                             current_scanners=current_scanners,
                             scanner_created=scanner_created)
        
    except Exception as e:
        logger.error(f"Error loading upgrade page: {str(e)}")
        flash('An error occurred while loading the upgrade page', 'danger')
        return redirect(url_for('client.dashboard'))

@client_bp.route('/process-upgrade', methods=['POST'])
@client_required
def process_upgrade(user):
    """Process subscription upgrade payment"""
    try:
        # Get client info
        client = get_client_by_user_id(user['user_id'])
        
        if not client:
            flash('Please complete your profile first', 'warning')
            return redirect(url_for('client.profile'))
        
        # Get form data
        new_plan = request.form.get('plan')
        
        # Define plan pricing to check if payment is needed
        plans = {
            'basic': {'name': 'Basic', 'price': 0},
            'starter': {'name': 'Starter', 'price': 59},
            'professional': {'name': 'Professional', 'price': 99},
            'enterprise': {'name': 'Enterprise', 'price': 149}
        }
        
        # Check if this is a free plan
        is_free_plan = plans.get(new_plan, {}).get('price', 0) == 0
        
        if not is_free_plan:
            # For paid plans, validate payment fields
            card_name = request.form.get('cardName')
            card_number = request.form.get('cardNumber')
            expiry_date = request.form.get('expiryDate')
            cvv = request.form.get('cvv')
            
            # Validate required fields for paid plans
            if not all([new_plan, card_name, card_number, expiry_date, cvv]):
                flash('All payment fields are required', 'danger')
                return redirect(url_for('client.upgrade_subscription'))
        
        # For free plans or demo purposes, we'll accept test payment data
        if is_free_plan:
            is_test_payment = True
        else:
            is_test_payment = (
                'test' in card_name.lower() or 
                card_number.replace(' ', '') == '4111111111111111' or
                card_number.replace(' ', '') == '1234567890123456'
            )
        
        if is_test_payment:
            # Simulate successful payment for test data
            logger.info(f"Processing test payment for client {client['id']} to upgrade to {new_plan}")
            
            # Update subscription in database
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE clients 
                SET subscription_level = ?, subscription_status = 'active', 
                    subscription_start = ?, updated_at = ?
                WHERE id = ?
            ''', (new_plan, datetime.now().isoformat(), datetime.now().isoformat(), client['id']))
            
            conn.commit()
            conn.close()
            
            if is_free_plan:
                flash(f'Subscription successfully changed to {new_plan.title()}!', 'success')
            else:
                flash(f'Subscription successfully upgraded to {new_plan.title()}!', 'success')
            
            # Check if coming from scanner creation
            scanner_created = request.form.get('scanner_created') or request.args.get('scanner_created')
            if scanner_created:
                # Redirect to the newly created scanner
                return redirect(f'/scanner/{scanner_created}/embed')
            else:
                return redirect(url_for('client.dashboard'))
        else:
            # In a real implementation, integrate with Stripe/PayPal here
            flash('Payment processing is currently in test mode. Please use test data.', 'info')
            return redirect(url_for('client.upgrade_subscription'))
        
    except Exception as e:
        logger.error(f"Error processing upgrade: {str(e)}")
        flash('An error occurred while processing your upgrade', 'danger')
        return redirect(url_for('client.upgrade_subscription'))

@client_bp.route('/debug-dashboard')
@client_required
def debug_dashboard(user):
    """Debug route to test dashboard data"""
    try:
        from client_db import get_client_dashboard_data, get_db_connection
        import sqlite3
        
        # Get user's client
        conn = get_db_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM clients WHERE user_id = ? AND active = 1", (user['id'],))
        client_row = cursor.fetchone()
        conn.close()
        
        if not client_row:
            return f"<h1>DEBUG: No client found for user {user['id']}</h1>"
            
        client = dict(client_row)
        client_id = client['id']
        
        # Get dashboard data
        dashboard_data = get_client_dashboard_data(client_id)
        
        if not dashboard_data:
            return f"<h1>DEBUG: No dashboard data for client {client_id}</h1>"
            
        scan_history = dashboard_data['scan_history']
        
        # Create debug HTML
        html = f"""
        <html>
        <head>
            <title>Dashboard Debug</title>
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
        </head>
        <body>
            <div class="container mt-4">
                <h1>🔍 Dashboard Debug Results</h1>
                <div class="alert alert-info">
                    <h4>User Info</h4>
                    <p>User ID: {user['id']}<br>
                    Username: {user['username']}<br>
                    Client ID: {client_id}<br>
                    Business: {client['business_name']}</p>
                </div>
                
                <div class="alert alert-success">
                    <h4>Dashboard Stats</h4>
                    <p>Total Scans: {dashboard_data['stats']['total_scans']}<br>
                    Scan History Count: {len(scan_history)}<br>
                    Avg Security Score: {dashboard_data['stats']['avg_security_score']}</p>
                </div>
                
                <div class="card">
                    <div class="card-header">
                        <h4>Scan History Data ({len(scan_history)} items)</h4>
                    </div>
                    <div class="card-body">
                        {"<p>No scan history found!</p>" if not scan_history else ""}
                        <table class="table table-striped">
                            <thead>
                                <tr>
                                    <th>Scan ID</th>
                                    <th>Lead Name</th>
                                    <th>Email</th>
                                    <th>Company</th>
                                    <th>Target</th>
                                    <th>Score</th>
                                    <th>Timestamp</th>
                                </tr>
                            </thead>
                            <tbody>
        """
        
        for scan in scan_history[:10]:  # Show first 10
            html += f"""
                                <tr>
                                    <td>{scan.get('scan_id', 'N/A')[:8]}...</td>
                                    <td>{scan.get('lead_name', 'N/A')}</td>
                                    <td>{scan.get('lead_email', 'N/A')}</td>
                                    <td>{scan.get('lead_company', 'N/A')}</td>
                                    <td>{scan.get('target', 'N/A')}</td>
                                    <td>{scan.get('security_score', 'N/A')}</td>
                                    <td>{scan.get('timestamp', 'N/A')}</td>
                                </tr>
            """
            
        html += """
                            </tbody>
                        </table>
                    </div>
                </div>
                
                <div class="mt-4">
                    <a href="/client/dashboard" class="btn btn-primary">Back to Dashboard</a>
                </div>
            </div>
        </body>
        </html>
        """
        
        return html
        
    except Exception as e:
        import traceback
        return f"<h1>ERROR: {str(e)}</h1><pre>{traceback.format_exc()}</pre>"
        return redirect(url_for('client.scanners'))
