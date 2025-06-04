#!/usr/bin/env python3
"""
Scanner database functions for creating and managing scanners
"""

import sqlite3
import uuid
import logging
from datetime import datetime
from client_db import get_db_connection

logger = logging.getLogger(__name__)

def create_scanner_for_client(client_id, scanner_data, created_by_user_id):
    """Create a new scanner for a client"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Generate unique API key and scanner ID
        api_key = uuid.uuid4().hex
        scanner_id = f"scanner_{uuid.uuid4().hex[:8]}"
        
        # Prepare scanner data
        scanner_name = scanner_data.get('name', 'Untitled Scanner')
        description = scanner_data.get('description', '')
        domain = scanner_data.get('domain', '')
        primary_color = scanner_data.get('primary_color', '#02054c')
        secondary_color = scanner_data.get('secondary_color', '#35a310')
        logo_url = scanner_data.get('logo_url', '')
        contact_email = scanner_data.get('contact_email', '')
        contact_phone = scanner_data.get('contact_phone', '')
        email_subject = scanner_data.get('email_subject', 'Your Security Scan Report')
        email_intro = scanner_data.get('email_intro', '')
        scan_types = ','.join(scanner_data.get('scan_types', ['port_scan', 'ssl_check']))
        
        # Insert into scanners table
        cursor.execute('''
        INSERT INTO scanners (
            client_id, scanner_id, name, description, domain, 
            api_key, primary_color, secondary_color, logo_url,
            contact_email, contact_phone, email_subject, email_intro,
            scan_types, status, created_by, created_at, updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            client_id, scanner_id, scanner_name, description, domain,
            api_key, primary_color, secondary_color, logo_url,
            contact_email, contact_phone, email_subject, email_intro,
            scan_types, 'deployed', created_by_user_id, 
            datetime.now().isoformat(), datetime.now().isoformat()
        ))
        
        scanner_db_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        logger.info(f"Scanner '{scanner_name}' created successfully for client {client_id}")
        
        return {
            'status': 'success',
            'scanner_id': scanner_db_id,
            'scanner_uid': scanner_id,
            'api_key': api_key,
            'message': f'Scanner "{scanner_name}" created successfully'
        }
        
    except Exception as e:
        logger.error(f"Error creating scanner: {e}")
        return {
            'status': 'error',
            'message': str(e)
        }

def get_scanners_by_client_id(client_id):
    """Get all scanners for a specific client with scan counts"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
        SELECT 
            id, scanner_id, name, description, domain, status,
            primary_color, secondary_color, contact_email, 
            created_at, updated_at, scan_types
        FROM scanners 
        WHERE client_id = ? AND status != 'deleted'
        ORDER BY created_at DESC
        ''', (client_id,))
        
        scanners = []
        for row in cursor.fetchall():
            if hasattr(row, 'keys'):
                scanner = dict(row)
            else:
                scanner = {
                    'id': row[0],
                    'scanner_id': row[1],
                    'name': row[2],
                    'description': row[3],
                    'domain': row[4],
                    'status': row[5],
                    'primary_color': row[6],
                    'secondary_color': row[7],
                    'contact_email': row[8],
                    'created_at': row[9],
                    'updated_at': row[10],
                    'scan_types': row[11]
                }
            
            # Add scan count from client-specific database
            try:
                from client_database_manager import get_scanner_scan_count
                scan_count = get_scanner_scan_count(client_id, scanner['scanner_id'])
                scanner['scan_count'] = scan_count
            except Exception as e:
                # Fallback to main database scan_history table
                try:
                    cursor.execute('SELECT COUNT(*) FROM scan_history WHERE scanner_id = ?', (scanner['scanner_id'],))
                    result = cursor.fetchone()
                    scanner['scan_count'] = result[0] if result else 0
                except Exception:
                    scanner['scan_count'] = 0
            
            # Add fields expected by the template (for both dict and tuple cases)
            scanner['scanner_name'] = scanner.get('name', scanner.get('scanner_name', 'Unknown Scanner'))
            scanner['subdomain'] = scanner.get('scanner_id', 'unknown')
            scanner['deploy_status'] = scanner.get('status', 'inactive')
            scanner['last_scan'] = scanner.get('last_scan', 'Never')
            scanner['security_score'] = scanner.get('security_score', 85)
            
            scanners.append(scanner)
        
        conn.close()
        return scanners
        
    except Exception as e:
        logger.error(f"Error getting scanners for client {client_id}: {e}")
        return []

def get_all_scanners_for_admin():
    """Get all scanners for admin dashboard"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
        SELECT 
            s.id, s.scanner_id, s.name, s.description, s.domain, s.status,
            s.created_at, s.updated_at, c.business_name as client_name,
            c.contact_email as client_email, s.client_id
        FROM scanners s
        LEFT JOIN clients c ON s.client_id = c.id
        WHERE s.status != 'deleted'
        ORDER BY s.created_at DESC
        ''')
        
        scanners = []
        for row in cursor.fetchall():
            if hasattr(row, 'keys'):
                scanner = dict(row)
            else:
                scanner = {
                    'id': row[0],
                    'scanner_id': row[1],
                    'name': row[2],
                    'description': row[3],
                    'domain': row[4],
                    'status': row[5],
                    'created_at': row[6],
                    'updated_at': row[7],
                    'client_name': row[8],
                    'client_email': row[9],
                    'client_id': row[10]
                }
            
            # Add scan count from client-specific database
            try:
                from client_database_manager import get_scanner_scan_count
                scan_count = get_scanner_scan_count(scanner['client_id'], scanner['scanner_id'])
                scanner['scan_count'] = scan_count
            except Exception as e:
                # Fallback to main database scan_history table
                try:
                    cursor.execute('SELECT COUNT(*) FROM scan_history WHERE scanner_id = ?', (scanner['scanner_id'],))
                    result = cursor.fetchone()
                    scanner['scan_count'] = result[0] if result else 0
                except Exception:
                    scanner['scan_count'] = 0
            
            scanners.append(scanner)
        
        conn.close()
        return scanners
        
    except Exception as e:
        logger.error(f"Error getting all scanners for admin: {e}")
        return []

def patch_client_db_scanner_functions():
    """Add scanner functions to client_db module"""
    try:
        import client_db
        
        # Add functions if they don't exist
        if not hasattr(client_db, 'create_scanner_for_client'):
            client_db.create_scanner_for_client = create_scanner_for_client
        
        if not hasattr(client_db, 'get_scanners_by_client_id'):
            client_db.get_scanners_by_client_id = get_scanners_by_client_id
            
        if not hasattr(client_db, 'get_all_scanners_for_admin'):
            client_db.get_all_scanners_for_admin = get_all_scanners_for_admin
        
        logger.info("✅ Scanner database functions patched successfully")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error patching scanner functions: {e}")
        return False

if __name__ == "__main__":
    # Test the functions
    print("🔍 Testing Scanner Database Functions")
    print("=" * 50)
    
    # Test scanner creation
    test_scanner_data = {
        'name': 'Test Scanner',
        'description': 'A test scanner',
        'domain': 'test.com',
        'primary_color': '#02054c',
        'secondary_color': '#35a310',
        'contact_email': 'test@test.com',
        'scan_types': ['port_scan', 'ssl_check']
    }
    
    # Patch client_db
    patch_client_db_scanner_functions()
    print("✅ client_db patched with scanner functions")