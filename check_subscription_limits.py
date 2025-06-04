#!/usr/bin/env python3
"""
Check Subscription Limits

This script checks if a client has reached their scan or scanner limits
based on their subscription level.
"""

import os
import sqlite3
import json
import logging
from datetime import datetime, timedelta
from subscription_constants import SUBSCRIPTION_LEVELS, get_subscription_limit

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def get_db_connection():
    """Get a connection to the database"""
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'cybrscan.db')
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

def check_scan_limit(client_id):
    """
    Check if a client has reached their scan limit
    
    Args:
        client_id (int): The client ID to check
        
    Returns:
        tuple: (has_reached_limit, limit, current_count, remaining)
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get client subscription level and scan limit
        cursor.execute("""
            SELECT id, subscription_level, scan_limit
            FROM clients 
            WHERE id = ?
        """, (client_id,))
        
        client = cursor.fetchone()
        if not client:
            logger.warning(f"Client {client_id} not found")
            return (False, 0, 0, 0)
        
        # Get subscription level
        subscription_level = client['subscription_level']
        
        # Get scan limit from client record or subscription constants
        if client['scan_limit'] is not None:
            scan_limit = client['scan_limit']
        else:
            scan_limit = get_subscription_limit(subscription_level, 'scans')
        
        # Calculate the start of the current month
        current_month_start = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0).isoformat()
        
        # Count scans for this month from scan_history
        cursor.execute("""
            SELECT COUNT(*) as scan_count
            FROM scan_history sh
            JOIN scanners s ON sh.scanner_id = s.scanner_id
            WHERE s.client_id = ? AND sh.created_at >= ?
        """, (client_id, current_month_start))
        
        scan_count_row = cursor.fetchone()
        scan_count = scan_count_row['scan_count'] if scan_count_row else 0
        
        # Also check client-specific database if it exists
        client_db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 
                                      f'client_databases/client_{client_id}_scans.db')
        
        if os.path.exists(client_db_path):
            client_conn = sqlite3.connect(client_db_path)
            client_conn.row_factory = sqlite3.Row
            client_cursor = client_conn.cursor()
            
            # Check if scans table exists
            client_cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='scans'")
            if client_cursor.fetchone():
                # Count scans for this month
                client_cursor.execute("""
                    SELECT COUNT(*) as scan_count
                    FROM scans
                    WHERE timestamp >= ?
                """, (current_month_start,))
                
                client_scan_count_row = client_cursor.fetchone()
                client_scan_count = client_scan_count_row['scan_count'] if client_scan_count_row else 0
                
                # Add to total scan count
                scan_count += client_scan_count
            
            client_conn.close()
        
        # Check if limit is reached
        has_reached_limit = scan_count >= scan_limit
        remaining = max(0, scan_limit - scan_count)
        
        conn.close()
        return (has_reached_limit, scan_limit, scan_count, remaining)
    except Exception as e:
        logger.error(f"Error checking scan limit: {e}")
        return (False, 0, 0, 0)

def check_scanner_limit(client_id):
    """
    Check if a client has reached their scanner limit
    
    Args:
        client_id (int): The client ID to check
        
    Returns:
        tuple: (has_reached_limit, limit, current_count, remaining)
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get client subscription level and scanner limit
        cursor.execute("""
            SELECT id, subscription_level, scanner_limit
            FROM clients 
            WHERE id = ?
        """, (client_id,))
        
        client = cursor.fetchone()
        if not client:
            logger.warning(f"Client {client_id} not found")
            return (False, 0, 0, 0)
        
        # Get subscription level
        subscription_level = client['subscription_level']
        
        # Get scanner limit from client record or subscription constants
        if client['scanner_limit'] is not None:
            scanner_limit = client['scanner_limit']
        else:
            scanner_limit = get_subscription_limit(subscription_level, 'scanners')
        
        # Count active scanners
        cursor.execute("""
            SELECT COUNT(*) as scanner_count
            FROM scanners
            WHERE client_id = ? AND status != 'deleted'
        """, (client_id,))
        
        scanner_count_row = cursor.fetchone()
        scanner_count = scanner_count_row['scanner_count'] if scanner_count_row else 0
        
        # Check if limit is reached
        has_reached_limit = scanner_count >= scanner_limit
        remaining = max(0, scanner_limit - scanner_count)
        
        conn.close()
        return (has_reached_limit, scanner_limit, scanner_count, remaining)
    except Exception as e:
        logger.error(f"Error checking scanner limit: {e}")
        return (False, 0, 0, 0)

def list_client_subscriptions():
    """List all client subscriptions and their limits"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get all clients with their subscription info
        cursor.execute("""
            SELECT id, business_name, subscription_level, subscription_status, scan_limit, scanner_limit
            FROM clients
            ORDER BY id
        """)
        
        clients = cursor.fetchall()
        conn.close()
        
        # Print client subscription info
        print("\nClient Subscription Summary:")
        print("=" * 80)
        print(f"{'ID':<5} {'Business Name':<30} {'Level':<15} {'Status':<10} {'Scan Limit':<12} {'Scanner Limit':<15}")
        print("-" * 80)
        
        for client in clients:
            # Check scan and scanner limits
            scan_result = check_scan_limit(client['id'])
            scanner_result = check_scanner_limit(client['id'])
            
            # Get subscription level details
            level = client['subscription_level'] or 'basic'
            level_name = level.capitalize()
            scan_limit = client['scan_limit'] or get_subscription_limit(level, 'scans')
            scanner_limit = client['scanner_limit'] or get_subscription_limit(level, 'scanners')
            
            # Print client details
            print(f"{client['id']:<5} {client['business_name'][:28]:<30} {level_name:<15} "
                  f"{client['subscription_status']:<10} {scan_result[2]}/{scan_limit:<8} "
                  f"{scanner_result[2]}/{scanner_limit:<10}")
        
        print("=" * 80)
        print("\nSubscription Plans:")
        print("=" * 80)
        for level, details in SUBSCRIPTION_LEVELS.items():
            print(f"{details['name']}: ${details['price']} per {details['period']}")
            features = details['features']
            print(f"  - Scanners: {features.get('scanners', 1)}")
            print(f"  - Scans per month: {features.get('scans_per_month', 10)}")
            print(f"  - White label: {'Yes' if features.get('white_label', False) else 'No'}")
            print(f"  - API access: {'Yes' if features.get('api_access', False) else 'No'}")
            print()
            
    except Exception as e:
        logger.error(f"Error listing client subscriptions: {e}")

def main():
    """Main function"""
    list_client_subscriptions()

if __name__ == "__main__":
    main()