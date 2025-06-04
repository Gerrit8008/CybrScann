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
    get_scan_statistics_for_client
)

# Define client blueprint
client_bp = Blueprint('client', __name__, url_prefix='/client')

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_client_total_scans(client_id):
    """Get total number of scans used by a client in the current billing period"""
    try:
        # Connect to database
        from client_db import get_db_connection
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # First try to query the scan_history table
        try:
            cursor.execute(
                "SELECT COUNT(*) FROM scan_history WHERE client_id = ?", 
                (client_id,)
            )
            total_scans = cursor.fetchone()[0]
        except:
            # If scan_history table doesn't exist or doesn't have client_id column
            # try the scans table
            try:
                cursor.execute(
                    "SELECT COUNT(*) FROM scans WHERE client_id = ?", 
                    (client_id,)
                )
                total_scans = cursor.fetchone()[0]
            except:
                total_scans = 0
        
        conn.close()
        return total_scans
    except Exception as e:
        logger.error(f"Error getting client total scans for client {client_id}: {e}")
        return 0

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
        
        # Add role check - ensure user is a client
        if result['user']['role'] != 'client':
            logger.warning(f"Access denied: User {result['user']['username']} with role {result['user']['role']} attempted to access client area")
            flash('Access denied. This area is for clients only.', 'danger')
            
            # Redirect admins to their dashboard
            if result['user']['role'] == 'admin':
                return redirect(url_for('admin.dashboard'))
            else:
                return redirect(url_for('auth.login'))
        
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
        return stats.get('total_scans', 0)
    except Exception as e:
        logger.error(f"Error getting client total scans: {e}")
        return 0

def get_client_scan_limit(client):
    """Get scan limit based on client's subscription level"""
    if not client:
        return 50  # Default starter plan
    
    subscription_level = client.get('subscription_level', 'starter').lower()
    
    # Define plan limits
    plan_limits = {
        'starter': 50,
        'basic': 100,
        'professional': 250,
        'business': 500,
        'enterprise': 1000
    }
    
    return plan_limits.get(subscription_level, 50)

def get_client_scanner_limit(client):
    """Get scanner limit based on client's subscription level"""
    if not client:
        return 1  # Default starter plan
    
    subscription_level = client.get('subscription_level', 'starter').lower()
    
    # Define scanner limits
    scanner_limits = {
        'starter': 1,
        'basic': 3,
        'professional': 5,
        'business': 10,
        'enterprise': 25
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
        # Import subscription constants
        from subscription_constants import get_client_scan_limit, get_client_scanner_limit
        
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
        
        
@client_bp.route('/reports/<scan_id>')
@client_required
def report_view(user, scan_id):
    """View a specific scan report"""
    try:
        # Get client info
        client = get_client_by_user_id(user['user_id'])
        
        if not client:
            flash('Please complete your client profile', 'info')
            return redirect(url_for('auth.complete_profile'))
        
        # Get scan details
        from db import get_scan_results
        scan = get_scan_results(scan_id)
        
        if not scan:
            flash('Scan report not found', 'danger')
            return redirect(url_for('client.reports'))
        
        # Verify this scan belongs to the client
        # TODO: Implement proper ownership verification
        
        # Format scan results for client-friendly display
        formatted_scan = format_scan_results_for_client(scan)
        
        return render_template(
            'client/report-view.html',
            user=user,
            client=client,
            scan=formatted_scan or scan
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
        from subscription_constants import get_client_scanner_limit
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM scanners WHERE client_id = ? AND status != "deleted"', (client['id'],))
        current_scanners = cursor.fetchone()[0]
        conn.close()
        
        # Get scanner limit based on client's subscription level
        scanner_limit = get_client_scanner_limit(client)
        
        # If at limit, redirect to upgrade page
        if current_scanners >= scanner_limit:
            flash(f'Scanner limit reached ({current_scanners}/{scanner_limit}). Please upgrade your subscription to create more scanners.', 'warning')
            return redirect(url_for('client.scanners'))
        
        if request.method == 'POST':
            # Get form data
            scanner_data = {
                'name': request.form.get('scanner_name', '').strip(),
                'description': request.form.get('description', '').strip(),
                'domain': request.form.get('domain', '').strip(),
                'primary_color': request.form.get('primary_color', '#02054c'),
                'secondary_color': request.form.get('secondary_color', '#35a310'),
                'logo_url': request.form.get('logo_url', ''),
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
                flash(f'Scanner "{scanner_data["name"]}" created successfully!', 'success')
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
