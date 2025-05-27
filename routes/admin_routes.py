"""
Admin and debug routes for CybrScan
Handles administrative functions, debugging, and development utilities
"""

from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for, flash
import os
import logging
import json
import traceback
import uuid
from datetime import datetime

# Create admin blueprint
admin_bp = Blueprint('admin', __name__)

# Configure logging
logger = logging.getLogger(__name__)


@admin_bp.route('/admin')
def admin_dashboard():
    """Comprehensive admin dashboard with all client data"""
    try:
        # Check if user is admin
        if not session.get('role') == 'admin':
            flash('Access denied. Admin privileges required.', 'danger')
            return redirect(url_for('auth.login'))
        
        # Get comprehensive dashboard data
        dashboard_data = get_admin_dashboard_data()
        
        # Add datetime for template
        from datetime import datetime
        dashboard_data['datetime'] = datetime
        
        return render_template('admin/admin-dashboard.html', **dashboard_data)
    except Exception as e:
        logging.error(f"Error loading admin dashboard: {e}")
        flash('Error loading admin dashboard', 'danger')
        return redirect(url_for('main.landing_page'))


def get_admin_dashboard_data():
    """Get comprehensive data for admin dashboard"""
    from client_db import get_db_connection
    import sqlite3
    from datetime import datetime, timedelta
    
    data = {}
    
    try:
        conn = get_db_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # === OVERVIEW STATISTICS ===
        
        # Total counts with error handling
        try:
            cursor.execute('SELECT COUNT(*) FROM users')
            result = cursor.fetchone()
            total_users = result[0] if result else 0
        except:
            total_users = 0
        
        try:
            cursor.execute('SELECT COUNT(*) FROM clients')
            result = cursor.fetchone()
            total_clients = result[0] if result else 0
        except:
            total_clients = 0
        
        try:
            cursor.execute('SELECT COUNT(*) FROM scanners')
            result = cursor.fetchone()
            total_scanners = result[0] if result else 0
        except:
            total_scanners = 0
        
        # Get total scans from all client databases
        try:
            total_scans = get_total_scans_across_all_clients()
        except Exception as e:
            logger.warning(f"Error getting total scans: {e}")
            total_scans = 0
        
        # Revenue calculations - only count active subscriptions
        try:
            cursor.execute('''
                SELECT subscription_level, COUNT(*) as count
                FROM clients 
                WHERE active = 1 AND (subscription_status = 'active' OR subscription_status IS NULL)
                GROUP BY subscription_level
            ''')
            subscription_stats = cursor.fetchall()
        except Exception as e:
            logger.warning(f"Error getting subscription stats: {e}")
            subscription_stats = []
        
        # Calculate monthly revenue
        plan_prices = {
            'starter': 29,
            'basic': 59,
            'professional': 129,
            'business': 299,
            'enterprise': 599
        }
        
        monthly_revenue = 0
        subscription_breakdown = {}
        for row in subscription_stats:
            level = (row['subscription_level'] or 'starter').lower()
            count = row['count']
            price = plan_prices.get(level, 29)
            revenue = count * price
            monthly_revenue += revenue
            subscription_breakdown[level] = {
                'count': count,
                'price': price,
                'revenue': revenue
            }
        
        # Recent activity (last 30 days)
        thirty_days_ago = (datetime.now() - timedelta(days=30)).isoformat()
        
        try:
            cursor.execute('SELECT COUNT(*) FROM clients WHERE created_at > ?', (thirty_days_ago,))
            result = cursor.fetchone()
            new_clients_30d = result[0] if result else 0
        except:
            new_clients_30d = 0
        
        try:
            cursor.execute('SELECT COUNT(*) FROM scanners WHERE created_at > ?', (thirty_days_ago,))
            result = cursor.fetchone()
            new_scanners_30d = result[0] if result else 0
        except:
            new_scanners_30d = 0
        
        data['overview'] = {
            'total_users': total_users,
            'total_clients': total_clients,
            'total_scanners': total_scanners,
            'total_scans': total_scans,
            'monthly_revenue': monthly_revenue,
            'new_clients_30d': new_clients_30d,
            'new_scanners_30d': new_scanners_30d,
            'subscription_breakdown': subscription_breakdown
        }
        
        # === CLIENT LIST WITH DETAILS ===
        
        try:
            cursor.execute('''
                SELECT c.*, u.username, u.email as user_email, u.created_at as user_created_at,
                       COUNT(DISTINCT s.id) as scanner_count
                FROM clients c
                LEFT JOIN users u ON c.user_id = u.id
                LEFT JOIN scanners s ON c.id = s.client_id
                WHERE c.active = 1
                GROUP BY c.id
                ORDER BY c.created_at DESC
            ''')
        except Exception as e:
            logger.warning(f"Error querying clients: {e}")
            cursor.execute('''
                SELECT c.*, COUNT(DISTINCT s.id) as scanner_count
                FROM clients c
                LEFT JOIN scanners s ON c.id = s.client_id
                WHERE c.active = 1
                GROUP BY c.id
                ORDER BY c.created_at DESC
            ''')
        clients = []
        for row in cursor.fetchall():
            client = dict(row)
            
            # Get scan count for this client
            try:
                from client import get_client_total_scans
                client['scan_count'] = get_client_total_scans(client['id'])
            except:
                client['scan_count'] = 0
            
            # Calculate client revenue
            level = (client.get('subscription_level') or 'starter').lower()
            client['monthly_revenue'] = plan_prices.get(level, 29)
            
            # Get most recent activity
            cursor.execute('''
                SELECT MAX(created_at) as last_activity
                FROM scanners 
                WHERE client_id = ?
            ''', (client['id'],))
            last_activity = cursor.fetchone()
            client['last_activity'] = last_activity[0] if last_activity and last_activity[0] else client.get('created_at')
            
            clients.append(client)
        
        data['clients'] = clients
        
        # === SCANNER DETAILS ===
        
        cursor.execute('''
            SELECT s.*, c.business_name, c.subscription_level,
                   cu.primary_color, cu.secondary_color, cu.button_color
            FROM scanners s
            LEFT JOIN clients c ON s.client_id = c.id
            LEFT JOIN customizations cu ON c.id = cu.client_id
            ORDER BY s.created_at DESC
            LIMIT 50
        ''')
        scanners = []
        for row in cursor.fetchall():
            scanner = dict(row)
            
            # Get scan count for this scanner
            try:
                from client_database_manager import get_scanner_scan_count
                scanner['scan_count'] = get_scanner_scan_count(scanner['client_id'], scanner['scanner_id'])
            except:
                scanner['scan_count'] = 0
            
            scanners.append(scanner)
        
        data['scanners'] = scanners
        
        # === RECENT LEADS/SCANS ===
        
        recent_leads = get_recent_leads_across_all_clients(limit=50)
        data['recent_leads'] = recent_leads
        
        # === SYSTEM HEALTH ===
        
        # Database sizes
        db_stats = get_database_statistics()
        data['system_health'] = db_stats
        
        # === PAYMENT TRACKING (FUTURE ENHANCEMENT) ===
        # Note: For real payments, add a payments table to track:
        # - payment_id, client_id, amount, date, status, method
        # This will replace the estimated revenue calculations
        
        conn.close()
        
    except Exception as e:
        logging.error(f"Error getting admin dashboard data: {e}")
        data = {
            'overview': {'total_users': 0, 'total_clients': 0, 'total_scanners': 0, 'total_scans': 0, 'monthly_revenue': 0},
            'clients': [],
            'scanners': [],
            'recent_leads': [],
            'system_health': {},
            'error': str(e)
        }
    
    return data


def get_total_scans_across_all_clients():
    """Get total scan count across all client databases"""
    try:
        from client_database_manager import get_all_client_scan_statistics
        total = 0
        
        # Get all client IDs
        from client_db import get_db_connection
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT id FROM clients')
        client_ids = [row[0] for row in cursor.fetchall()]
        conn.close()
        
        # Sum scans from all client databases
        for client_id in client_ids:
            try:
                from client import get_client_total_scans
                client_scans = get_client_total_scans(client_id)
                total += client_scans
            except:
                continue
        
        return total
    except Exception as e:
        logging.error(f"Error getting total scans: {e}")
        return 0


def get_recent_leads_across_all_clients(limit=50):
    """Get recent leads/scans across all client databases"""
    try:
        all_leads = []
        
        # Get all client IDs
        from client_db import get_db_connection
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT id, business_name FROM clients')
        clients = cursor.fetchall()
        conn.close()
        
        # Get recent scans from each client database
        for client_id, business_name in clients:
            try:
                from client_database_manager import get_recent_client_scans
                client_leads = get_recent_client_scans(client_id, limit=10)
                
                # Add client context to each lead
                for lead in client_leads:
                    lead['client_id'] = client_id
                    lead['client_name'] = business_name
                    all_leads.append(lead)
            except Exception as e:
                logging.warning(f"Could not get leads for client {client_id}: {e}")
                continue
        
        # Sort by timestamp and limit
        all_leads.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
        return all_leads[:limit]
        
    except Exception as e:
        logging.error(f"Error getting recent leads: {e}")
        return []


def get_database_statistics():
    """Get database size and health statistics"""
    try:
        import os
        from client_db import get_db_connection
        
        stats = {}
        
        # Main database size
        main_db_path = 'client_scanner.db'
        if os.path.exists(main_db_path):
            stats['main_db_size'] = os.path.getsize(main_db_path)
        
        # Client databases total size
        client_db_dir = 'client_databases'
        total_client_db_size = 0
        client_db_count = 0
        
        if os.path.exists(client_db_dir):
            for filename in os.listdir(client_db_dir):
                if filename.endswith('.db'):
                    filepath = os.path.join(client_db_dir, filename)
                    total_client_db_size += os.path.getsize(filepath)
                    client_db_count += 1
        
        stats['client_db_total_size'] = total_client_db_size
        stats['client_db_count'] = client_db_count
        
        # Database health check
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('PRAGMA integrity_check')
        integrity_result = cursor.fetchone()[0]
        stats['db_integrity'] = integrity_result
        conn.close()
        
        return stats
        
    except Exception as e:
        logging.error(f"Error getting database statistics: {e}")
        return {}


@admin_bp.route('/admin_simplified')
def admin_simplified():
    """Simplified admin interface"""
    try:
        # Basic admin stats
        from client_db import get_db_connection
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get stats
        cursor.execute('SELECT COUNT(*) FROM users')
        total_users = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM clients')
        total_clients = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM scanners')
        total_scanners = cursor.fetchone()[0]
        
        conn.close()
        
        stats = {
            'total_users': total_users,
            'total_clients': total_clients,
            'total_scanners': total_scanners
        }
        
        return render_template('admin/admin-simplified.html', stats=stats)
        
    except Exception as e:
        logging.error(f"Error loading simplified admin: {e}")
        return render_template('admin/admin-simplified.html', stats={}, error=str(e))


@admin_bp.route('/run_dashboard_fix')
def run_dashboard_fix():
    """Run dashboard fix utility"""
    try:
        from dashboard_fix import fix_dashboard_issues
        result = fix_dashboard_issues()
        
        return jsonify({
            'status': 'success',
            'message': 'Dashboard fix completed',
            'details': result
        })
    except Exception as e:
        logging.error(f"Dashboard fix error: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e),
            'traceback': traceback.format_exc()
        }), 500


@admin_bp.route('/run_emergency_admin')
def run_emergency_admin():
    """Run emergency admin setup"""
    try:
        from emergency_access import setup_emergency_admin
        result = setup_emergency_admin()
        
        return jsonify({
            'status': 'success',
            'message': 'Emergency admin setup completed',
            'details': result
        })
    except Exception as e:
        logging.error(f"Emergency admin setup error: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e),
            'traceback': traceback.format_exc()
        }), 500


# Debug routes
@admin_bp.route('/debug')
def debug_info():
    """Debug information page"""
    try:
        debug_data = {
            'session': dict(session),
            'request_info': {
                'method': request.method,
                'url': request.url,
                'remote_addr': request.remote_addr,
                'user_agent': request.headers.get('User-Agent')
            },
            'environment': {
                'python_version': os.sys.version,
                'cwd': os.getcwd(),
                'timestamp': datetime.now().isoformat()
            }
        }
        
        return jsonify(debug_data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/debug_session')
def debug_session():
    """Debug session information"""
    try:
        return jsonify({
            'session_data': dict(session),
            'session_id': session.get('session_token'),
            'user_id': session.get('user_id'),
            'role': session.get('role'),
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/debug_db')
def debug_database():
    """Debug database connectivity and schema"""
    try:
        from client_db import get_db_connection
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Test basic connectivity
        cursor.execute('SELECT 1')
        
        # Get table list
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        
        # Get some basic counts
        stats = {}
        for table in tables:
            try:
                cursor.execute(f'SELECT COUNT(*) FROM {table}')
                stats[table] = cursor.fetchone()[0]
            except Exception:
                stats[table] = 'error'
        
        conn.close()
        
        return jsonify({
            'status': 'connected',
            'tables': tables,
            'stats': stats,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logging.error(f"Database debug error: {e}")
        return jsonify({
            'status': 'error',
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500


@admin_bp.route('/debug_post', methods=['POST'])
def debug_post():
    """Debug POST requests"""
    try:
        return jsonify({
            'method': request.method,
            'form_data': dict(request.form),
            'json_data': request.get_json(),
            'headers': dict(request.headers),
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/debug_submit', methods=['POST'])
def debug_submit():
    """Debug form submission"""
    try:
        form_data = dict(request.form)
        json_data = request.get_json()
        
        return jsonify({
            'status': 'received',
            'form_data': form_data,
            'json_data': json_data,
            'content_type': request.content_type,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500


@admin_bp.route('/debug_scan/<scan_id>')
def debug_scan(scan_id):
    """Debug specific scan"""
    try:
        from database_utils import get_scan_results
        scan_results = get_scan_results(scan_id)
        
        if scan_results:
            return jsonify({
                'status': 'found',
                'scan_id': scan_id,
                'results': scan_results,
                'timestamp': datetime.now().isoformat()
            })
        else:
            return jsonify({
                'status': 'not_found',
                'scan_id': scan_id,
                'timestamp': datetime.now().isoformat()
            }), 404
            
    except Exception as e:
        return jsonify({
            'status': 'error',
            'scan_id': scan_id,
            'error': str(e)
        }), 500


@admin_bp.route('/debug_scan_test')
def debug_scan_test():
    """Test scan functionality"""
    try:
        from security_scanner import run_test_scan
        result = run_test_scan()
        
        return jsonify({
            'status': 'success',
            'test_result': result,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500


@admin_bp.route('/test_scan')
def test_scan():
    """Test scan page"""
    return render_template('test_scan.html')


@admin_bp.route('/db_fix')
def database_fix():
    """Database repair and maintenance"""
    try:
        from db_fix import run_database_fixes
        result = run_database_fixes()
        
        return jsonify({
            'status': 'success',
            'message': 'Database fixes completed',
            'details': result
        })
    except Exception as e:
        logging.error(f"Database fix error: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e),
            'traceback': traceback.format_exc()
        }), 500


@admin_bp.route('/db_check')
def database_check():
    """Check database integrity"""
    try:
        from client_db import get_db_connection
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Run integrity check
        cursor.execute('PRAGMA integrity_check')
        integrity_result = cursor.fetchone()[0]
        
        # Get database info
        cursor.execute('PRAGMA user_version')
        user_version = cursor.fetchone()[0]
        
        conn.close()
        
        return jsonify({
            'status': 'success',
            'integrity_check': integrity_result,
            'user_version': user_version,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logging.error(f"Database check error: {e}")
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500


@admin_bp.route('/test_db_write')
def test_database_write():
    """Test database write operations"""
    try:
        # Create test data
        test_data = {
            'scan_id': str(uuid.uuid4()),
            'timestamp': datetime.now().isoformat(),
            'target': 'test.com',
            'email': 'test@example.com',
            'test_field': 'This is a test'
        }
        
        # Try to save to database
        from database_utils import save_scan_results
        saved_id = save_scan_results(test_data)
        
        if saved_id:
            # Try to retrieve it
            from database_utils import get_scan_results
            retrieved = get_scan_results(saved_id)
            
            return jsonify({
                'status': 'success',
                'message': 'Database write and read successful',
                'saved_id': saved_id,
                'retrieved': retrieved is not None,
                'record_matches': retrieved is not None and retrieved.get('test_field') == test_data['test_field']
            })
        else:
            return jsonify({
                'status': 'error',
                'message': 'Database write failed - save_scan_results returned None or False'
            })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Exception during database test: {str(e)}',
            'traceback': traceback.format_exc()
        })


@admin_bp.route('/admin/client/<int:client_id>')
def view_client_details(client_id):
    """View detailed information for a specific client"""
    try:
        # Check if user is admin
        if not session.get('role') == 'admin':
            flash('Access denied. Admin privileges required.', 'danger')
            return redirect(url_for('auth.login'))
        
        from client_db import get_db_connection
        import sqlite3
        
        conn = get_db_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Get client details
        cursor.execute('''
            SELECT c.*, u.username, u.email as user_email, u.created_at as user_created_at
            FROM clients c
            LEFT JOIN users u ON c.user_id = u.id
            WHERE c.id = ?
        ''', (client_id,))
        
        client_row = cursor.fetchone()
        if not client_row:
            flash('Client not found', 'danger')
            return redirect(url_for('admin.admin_dashboard'))
        
        client = dict(client_row)
        
        # Get client's scanners
        cursor.execute('''
            SELECT s.*, cu.primary_color, cu.secondary_color, cu.button_color
            FROM scanners s
            LEFT JOIN customizations cu ON s.client_id = cu.client_id
            WHERE s.client_id = ?
            ORDER BY s.created_at DESC
        ''', (client_id,))
        
        scanners = [dict(row) for row in cursor.fetchall()]
        
        # Add scan counts to each scanner
        for scanner in scanners:
            try:
                from client_database_manager import get_scanner_scan_count
                scanner['scan_count'] = get_scanner_scan_count(client_id, scanner['scanner_id'])
            except:
                scanner['scan_count'] = 0
        
        # Get recent scans for this client
        try:
            from client_database_manager import get_recent_client_scans
            recent_scans = get_recent_client_scans(client_id, limit=20)
        except:
            recent_scans = []
        
        # Get client scan statistics
        try:
            from client import get_client_total_scans, get_client_scan_limit
            client['total_scans'] = get_client_total_scans(client_id)
            client['scan_limit'] = get_client_scan_limit(client)
        except:
            client['total_scans'] = 0
            client['scan_limit'] = 50
        
        conn.close()
        
        return render_template('admin/client-view.html', 
                             client=client, 
                             scanners=scanners, 
                             recent_scans=recent_scans)
        
    except Exception as e:
        logging.error(f"Error viewing client details: {e}")
        flash('Error loading client details', 'danger')
        return redirect(url_for('admin.admin_dashboard'))


@admin_bp.route('/admin/client/<int:client_id>/scans')
def view_client_scans(client_id):
    """View all scans for a specific client"""
    try:
        # Check if user is admin
        if not session.get('role') == 'admin':
            flash('Access denied. Admin privileges required.', 'danger')
            return redirect(url_for('auth.login'))
        
        # Get client info
        from client_db import get_db_connection
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT business_name FROM clients WHERE id = ?', (client_id,))
        client_row = cursor.fetchone()
        conn.close()
        
        if not client_row:
            flash('Client not found', 'danger')
            return redirect(url_for('admin.admin_dashboard'))
        
        client_name = client_row[0]
        
        # Get all scans for this client
        try:
            from client_database_manager import get_recent_client_scans
            scans = get_recent_client_scans(client_id, limit=100)  # Get more scans for detailed view
        except:
            scans = []
        
        return render_template('admin/client-scans.html', 
                             client_id=client_id,
                             client_name=client_name,
                             scans=scans)
        
    except Exception as e:
        logging.error(f"Error viewing client scans: {e}")
        flash('Error loading client scans', 'danger')
        return redirect(url_for('admin.admin_dashboard'))


@admin_bp.route('/admin/scanner/<scanner_id>/details')
def view_scanner_details(scanner_id):
    """View detailed information for a specific scanner"""
    try:
        # Check if user is admin
        if not session.get('role') == 'admin':
            flash('Access denied. Admin privileges required.', 'danger')
            return redirect(url_for('auth.login'))
        
        from client_db import get_db_connection
        import sqlite3
        
        conn = get_db_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Get scanner details with client info
        cursor.execute('''
            SELECT s.*, c.business_name, c.subscription_level,
                   cu.primary_color, cu.secondary_color, cu.button_color,
                   cu.logo_path, cu.favicon_path, cu.email_subject, cu.email_intro
            FROM scanners s
            LEFT JOIN clients c ON s.client_id = c.id
            LEFT JOIN customizations cu ON c.id = cu.client_id
            WHERE s.scanner_id = ?
        ''', (scanner_id,))
        
        scanner_row = cursor.fetchone()
        if not scanner_row:
            flash('Scanner not found', 'danger')
            return redirect(url_for('admin.admin_dashboard'))
        
        scanner = dict(scanner_row)
        
        # Get scan history for this scanner
        cursor.execute('''
            SELECT * FROM scan_history 
            WHERE scanner_id = ? 
            ORDER BY created_at DESC 
            LIMIT 20
        ''', (scanner_id,))
        
        scan_history = [dict(row) for row in cursor.fetchall()]
        
        # Get scan count
        try:
            from client_database_manager import get_scanner_scan_count
            scanner['total_scans'] = get_scanner_scan_count(scanner['client_id'], scanner_id)
        except:
            scanner['total_scans'] = 0
        
        conn.close()
        
        return render_template('admin/scanner-details.html', 
                             scanner=scanner, 
                             scan_history=scan_history)
        
    except Exception as e:
        logging.error(f"Error viewing scanner details: {e}")
        flash('Error loading scanner details', 'danger')
        return redirect(url_for('admin.admin_dashboard'))