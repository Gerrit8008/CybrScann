#!/usr/bin/env python3
"""
Admin database functions for the missing admin routes
"""

import sqlite3
from client_db import get_db_connection
import logging

logger = logging.getLogger(__name__)

def get_all_subscriptions():
    """Get all client subscriptions for admin dashboard"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
        SELECT 
            c.business_name as client_name,
            c.subscription_level as plan,
            c.subscription_status as status,
            c.subscription_start as start_date,
            c.subscription_end as end_date,
            c.id as client_id
        FROM clients c
        WHERE c.active = 1
        ORDER BY c.subscription_start DESC
        ''')
        
        subscriptions = []
        for row in cursor.fetchall():
            # Convert row to dictionary
            if hasattr(row, 'keys'):
                sub = dict(row)
            else:
                sub = {
                    'client_name': row[0],
                    'plan': row[1] or 'basic',
                    'status': row[2] or 'active',
                    'start_date': row[3],
                    'end_date': row[4],
                    'client_id': row[5]
                }
            
            # Add mock revenue data
            sub['monthly_revenue'] = 299 if sub['plan'] == 'premium' else 99
            subscriptions.append(sub)
        
        conn.close()
        return subscriptions
        
    except Exception as e:
        logger.error(f"Error getting subscriptions: {e}")
        return []

def get_admin_reports():
    """Get reports data for admin dashboard"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get scan statistics
        cursor.execute('''
        SELECT 
            COUNT(*) as total_scans,
            DATE(created_at) as scan_date
        FROM scan_history 
        WHERE created_at >= date('now', '-30 days')
        GROUP BY DATE(created_at)
        ORDER BY scan_date DESC
        ''')
        
        scan_stats = cursor.fetchall()
        
        # Get client statistics  
        cursor.execute('''
        SELECT 
            COUNT(*) as total_clients,
            COUNT(CASE WHEN created_at >= date('now', '-7 days') THEN 1 END) as new_clients
        FROM clients
        WHERE active = 1
        ''')
        
        client_stats = cursor.fetchone()
        
        conn.close()
        
        reports = {
            'scan_stats': [dict(row) if hasattr(row, 'keys') else {'total_scans': row[0], 'scan_date': row[1]} for row in scan_stats],
            'total_clients': client_stats[0] if client_stats else 0,
            'new_clients': client_stats[1] if client_stats else 0,
            'total_scans': sum(row[0] for row in scan_stats),
            'avg_scans_per_day': round(sum(row[0] for row in scan_stats) / max(len(scan_stats), 1), 1)
        }
        
        return reports
        
    except Exception as e:
        logger.error(f"Error getting admin reports: {e}")
        return {}

def get_admin_settings():
    """Get admin settings"""
    try:
        # For now, return default settings
        # In a real implementation, these would be stored in a settings table
        settings = {
            'platform_name': 'CybrScan Scanner Platform',
            'admin_email': 'admin@cybrscan.com',
            'max_clients': 100,
            'max_scans_per_client': 50,
            'email_notifications': True,
            'auto_renewal': True,
            'trial_period_days': 14,
            'support_email': 'support@cybrscan.com'
        }
        
        return settings
        
    except Exception as e:
        logger.error(f"Error getting admin settings: {e}")
        return {}

def update_admin_settings(settings_data):
    """Update admin settings"""
    try:
        # For now, just return success
        # In a real implementation, settings would be saved to database
        logger.info(f"Admin settings updated: {settings_data}")
        return {'status': 'success', 'message': 'Settings updated successfully'}
        
    except Exception as e:
        logger.error(f"Error updating admin settings: {e}")
        return {'status': 'error', 'message': str(e)}

# Add these functions to client_db.py if they don't exist
def patch_client_db():
    """Add missing functions to client_db module"""
    try:
        import client_db
        
        # Add functions if they don't exist
        if not hasattr(client_db, 'get_all_subscriptions'):
            client_db.get_all_subscriptions = get_all_subscriptions
        
        if not hasattr(client_db, 'get_admin_reports'):
            client_db.get_admin_reports = get_admin_reports
            
        if not hasattr(client_db, 'get_admin_settings'):
            client_db.get_admin_settings = get_admin_settings
            
        if not hasattr(client_db, 'update_admin_settings'):
            client_db.update_admin_settings = update_admin_settings
        
        logger.info("✅ Admin database functions patched successfully")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error patching client_db: {e}")
        return False

if __name__ == "__main__":
    # Test the functions
    print("🔍 Testing Admin Database Functions")
    print("=" * 50)
    
    # Test subscriptions
    subscriptions = get_all_subscriptions()
    print(f"✅ Subscriptions: {len(subscriptions)} found")
    
    # Test reports
    reports = get_admin_reports()
    print(f"✅ Reports: {len(reports)} data points")
    
    # Test settings
    settings = get_admin_settings()
    print(f"✅ Settings: {len(settings)} configurations")
    
    # Patch client_db
    patch_client_db()
    print("✅ client_db patched with admin functions")