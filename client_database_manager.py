#!/usr/bin/env python3

import os
import sqlite3
import json
import logging
from datetime import datetime
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_client_specific_database(client_id, business_name):
    """Create a dedicated database for a specific client to track their scans"""
    try:
        # Create databases directory if it doesn't exist
        db_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'client_databases')
        os.makedirs(db_dir, exist_ok=True)
        
        # Database path for this specific client
        db_path = os.path.join(db_dir, f'client_{client_id}_scans.db')
        
        # Create database connection
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Create scans table for this client
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS scans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            scan_id TEXT UNIQUE NOT NULL,
            scanner_id TEXT,
            timestamp TEXT NOT NULL,
            lead_name TEXT,
            lead_email TEXT NOT NULL,
            lead_phone TEXT,
            lead_company TEXT,
            company_size TEXT,
            target_domain TEXT,
            security_score INTEGER DEFAULT 0,
            risk_level TEXT,
            scan_type TEXT DEFAULT 'comprehensive',
            status TEXT DEFAULT 'completed',
            ip_address TEXT,
            user_agent TEXT,
            scan_duration INTEGER,
            vulnerabilities_found INTEGER DEFAULT 0,
            recommendations_count INTEGER DEFAULT 0,
            scan_results TEXT,  -- JSON data
            created_at TEXT NOT NULL,
            updated_at TEXT
        )
        ''')
        
        # Create reports table for generated reports
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            scan_id TEXT NOT NULL,
            report_type TEXT DEFAULT 'pdf',
            report_path TEXT,
            generated_at TEXT NOT NULL,
            email_sent BOOLEAN DEFAULT 0,
            email_sent_at TEXT,
            download_count INTEGER DEFAULT 0,
            FOREIGN KEY (scan_id) REFERENCES scans(scan_id)
        )
        ''')
        
        # Create leads table for lead management
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS leads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            name TEXT,
            phone TEXT,
            company TEXT,
            company_size TEXT,
            industry TEXT,
            first_scan_date TEXT,
            last_scan_date TEXT,
            total_scans INTEGER DEFAULT 1,
            avg_security_score REAL DEFAULT 0,
            lead_status TEXT DEFAULT 'new',  -- new, contacted, qualified, converted
            notes TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT
        )
        ''')
        
        # Create scanner_usage table to track which scanners are used
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS scanner_usage (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            scanner_id TEXT NOT NULL,
            date TEXT NOT NULL,
            scans_count INTEGER DEFAULT 0,
            unique_leads INTEGER DEFAULT 0,
            avg_score REAL DEFAULT 0,
            created_at TEXT NOT NULL
        )
        ''')
        
        # Create indexes for better performance
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_scans_email ON scans(lead_email)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_scans_date ON scans(created_at)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_scans_score ON scans(security_score)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_scans_scanner ON scans(scanner_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_leads_email ON leads(email)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_leads_status ON leads(lead_status)')
        
        # Insert initial metadata
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS database_info (
            key TEXT PRIMARY KEY,
            value TEXT
        )
        ''')
        
        cursor.execute('INSERT OR REPLACE INTO database_info (key, value) VALUES (?, ?)', 
                      ('client_id', str(client_id)))
        cursor.execute('INSERT OR REPLACE INTO database_info (key, value) VALUES (?, ?)', 
                      ('business_name', business_name))
        cursor.execute('INSERT OR REPLACE INTO database_info (key, value) VALUES (?, ?)', 
                      ('created_at', datetime.now().isoformat()))
        cursor.execute('INSERT OR REPLACE INTO database_info (key, value) VALUES (?, ?)', 
                      ('database_version', '1.0'))
        
        conn.commit()
        conn.close()
        
        logger.info(f"Created dedicated database for client {client_id} ({business_name}): {db_path}")
        return db_path
        
    except Exception as e:
        logger.error(f"Error creating client database for {client_id}: {e}")
        return None

def save_scan_to_client_db(client_id, scan_data):
    """Save scan data to client's dedicated database"""
    try:
        # Get client database path
        db_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'client_databases')
        db_path = os.path.join(db_dir, f'client_{client_id}_scans.db')
        
        if not os.path.exists(db_path):
            logger.warning(f"Client database not found for {client_id}, creating new one")
            create_client_specific_database(client_id, scan_data.get('business_name', 'Unknown'))
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Extract scan information
        scan_id = scan_data.get('scan_id')
        scanner_id = scan_data.get('scanner_id', 'web_interface')
        timestamp = scan_data.get('timestamp', datetime.now().isoformat())
        lead_name = scan_data.get('name', '')
        lead_email = scan_data.get('email', '')
        lead_phone = scan_data.get('phone', '')
        lead_company = scan_data.get('company', '')
        company_size = scan_data.get('company_size', 'Unknown')
        target_domain = scan_data.get('target', '')
        
        # Calculate security score
        security_score = 75  # Default
        if 'risk_assessment' in scan_data and 'overall_score' in scan_data['risk_assessment']:
            security_score = scan_data['risk_assessment']['overall_score']
        
        # Determine risk level
        if security_score >= 90:
            risk_level = 'Low'
        elif security_score >= 75:
            risk_level = 'Moderate'
        elif security_score >= 50:
            risk_level = 'High'
        else:
            risk_level = 'Critical'
        
        # Count vulnerabilities and recommendations
        vulnerabilities_found = 0
        recommendations_count = len(scan_data.get('recommendations', []))
        
        # Insert scan record
        cursor.execute('''
        INSERT OR REPLACE INTO scans (
            scan_id, scanner_id, timestamp, lead_name, lead_email, lead_phone,
            lead_company, company_size, target_domain, security_score, risk_level,
            scan_type, status, vulnerabilities_found, recommendations_count,
            scan_results, created_at, updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            scan_id, scanner_id, timestamp, lead_name, lead_email, lead_phone,
            lead_company, company_size, target_domain, security_score, risk_level,
            'comprehensive', 'completed', vulnerabilities_found, recommendations_count,
            json.dumps(scan_data), datetime.now().isoformat(), datetime.now().isoformat()
        ))
        
        # Update or insert lead information
        if lead_email:
            cursor.execute('SELECT * FROM leads WHERE email = ?', (lead_email,))
            existing_lead = cursor.fetchone()
            
            if existing_lead:
                # Update existing lead
                cursor.execute('''
                UPDATE leads SET 
                    name = COALESCE(?, name),
                    phone = COALESCE(?, phone),
                    company = COALESCE(?, company),
                    company_size = COALESCE(?, company_size),
                    last_scan_date = ?,
                    total_scans = total_scans + 1,
                    avg_security_score = (avg_security_score * total_scans + ?) / (total_scans + 1),
                    updated_at = ?
                WHERE email = ?
                ''', (lead_name, lead_phone, lead_company, company_size, 
                     datetime.now().isoformat(), security_score, 
                     datetime.now().isoformat(), lead_email))
            else:
                # Insert new lead
                cursor.execute('''
                INSERT INTO leads (
                    email, name, phone, company, company_size,
                    first_scan_date, last_scan_date, total_scans, avg_security_score,
                    lead_status, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (lead_email, lead_name, lead_phone, lead_company, company_size,
                     datetime.now().isoformat(), datetime.now().isoformat(), 1, security_score,
                     'new', datetime.now().isoformat(), datetime.now().isoformat()))
        
        conn.commit()
        conn.close()
        
        logger.info(f"Saved scan {scan_id} to client {client_id} database")
        return True
        
    except Exception as e:
        logger.error(f"Error saving scan to client database {client_id}: {e}")
        return False

def get_client_scan_reports(client_id, page=1, per_page=25, filters=None):
    """Get scan reports from client's dedicated database"""
    try:
        db_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'client_databases')
        db_path = os.path.join(db_dir, f'client_{client_id}_scans.db')
        
        if not os.path.exists(db_path):
            logger.info(f"Client database not found for client {client_id}, returning empty results")
            return [], {'page': 1, 'per_page': per_page, 'total_pages': 1, 'total_count': 0}
        
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Check if the scans table exists and has the expected schema
        try:
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='scans'")
            if not cursor.fetchone():
                logger.warning(f"Scans table not found in client {client_id} database")
                conn.close()
                return [], {'page': 1, 'per_page': per_page, 'total_pages': 1, 'total_count': 0}
                
            # Check table schema - ensure required columns exist
            cursor.execute("PRAGMA table_info(scans)")
            columns = [col[1] for col in cursor.fetchall()]
            required_columns = ['scan_id', 'timestamp', 'lead_name', 'lead_email', 'target_domain', 'security_score']
            
            missing_columns = [col for col in required_columns if col not in columns]
            if missing_columns:
                logger.warning(f"Client {client_id} database missing columns: {missing_columns}")
                conn.close()
                return [], {'page': 1, 'per_page': per_page, 'total_pages': 1, 'total_count': 0}
                
        except Exception as schema_error:
            logger.error(f"Schema validation error for client {client_id}: {schema_error}")
            conn.close()
            return [], {'page': 1, 'per_page': per_page, 'total_pages': 1, 'total_count': 0}
        
        # Build WHERE clause based on filters
        where_conditions = []
        params = []
        
        if filters:
            if filters.get('search'):
                search_term = f"%{filters['search']}%"
                where_conditions.append("(lead_name LIKE ? OR lead_email LIKE ? OR lead_company LIKE ?)")
                params.extend([search_term, search_term, search_term])
            
            if filters.get('date_from'):
                where_conditions.append("DATE(created_at) >= ?")
                params.append(filters['date_from'])
            
            if filters.get('date_to'):
                where_conditions.append("DATE(created_at) <= ?")
                params.append(filters['date_to'])
            
            if filters.get('score_min'):
                where_conditions.append("security_score >= ?")
                params.append(int(filters['score_min']))
        
        where_clause = " AND ".join(where_conditions) if where_conditions else "1=1"
        
        # Get total count for pagination
        count_query = f"SELECT COUNT(*) FROM scans WHERE {where_clause}"
        cursor.execute(count_query, params)
        total_count = cursor.fetchone()[0]
        
        # Calculate pagination
        total_pages = (total_count + per_page - 1) // per_page
        offset = (page - 1) * per_page
        
        # Get scan reports
        query = f"""
        SELECT 
            scan_id, scanner_id, timestamp, lead_name, lead_email, lead_phone,
            lead_company, company_size, target_domain, security_score, risk_level,
            scan_type, status, created_at
        FROM scans 
        WHERE {where_clause}
        ORDER BY created_at DESC
        LIMIT ? OFFSET ?
        """
        
        cursor.execute(query, params + [per_page, offset])
        scan_reports = [dict(row) for row in cursor.fetchall()]
        
        conn.close()
        
        pagination = {
            'page': page,
            'per_page': per_page,
            'total_pages': total_pages,
            'total_count': total_count
        }
        
        return scan_reports, pagination
        
    except Exception as e:
        logger.error(f"Error getting scan reports for client {client_id}: {e}")
        return [], {'page': 1, 'per_page': per_page, 'total_pages': 1, 'total_count': 0}

def ensure_client_database(client_id, business_name="Unknown Client"):
    """Ensure client database exists and has proper schema"""
    try:
        db_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'client_databases')
        db_path = os.path.join(db_dir, f'client_{client_id}_scans.db')
        
        if not os.path.exists(db_path):
            logger.info(f"Creating missing database for client {client_id}")
            return create_client_specific_database(client_id, business_name)
        else:
            # Validate existing database schema
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Check if scans table exists
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='scans'")
            if not cursor.fetchone():
                logger.warning(f"Recreating database for client {client_id} - missing scans table")
                conn.close()
                os.remove(db_path)  # Remove corrupted database
                return create_client_specific_database(client_id, business_name)
            
            conn.close()
            return db_path
            
    except Exception as e:
        logger.error(f"Error ensuring client database for {client_id}: {e}")
        return None

def get_scanner_scan_count(client_id, scanner_id):
    """Get scan count for a specific scanner"""
    try:
        db_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'client_databases')
        db_path = os.path.join(db_dir, f'client_{client_id}_scans.db')
        
        if not os.path.exists(db_path):
            return 0
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get scan count for this specific scanner
        cursor.execute('SELECT COUNT(*) FROM scans WHERE scanner_id = ?', (scanner_id,))
        result = cursor.fetchone()
        scan_count = result[0] if result else 0
        
        conn.close()
        return scan_count
        
    except Exception as e:
        logging.error(f"Error getting scanner scan count for {scanner_id}: {e}")
        return 0

def get_client_scan_statistics(client_id):
    """Get scan statistics from client's dedicated database"""
    try:
        db_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'client_databases')
        db_path = os.path.join(db_dir, f'client_{client_id}_scans.db')
        
        if not os.path.exists(db_path):
            logger.info(f"Client database not found for client {client_id}, returning zero stats")
            return {
                'total_scans': 0,
                'avg_score': 0,
                'this_month': 0,
                'unique_companies': 0
            }
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Validate database schema
        try:
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='scans'")
            if not cursor.fetchone():
                logger.warning(f"Scans table not found in client {client_id} database")
                conn.close()
                return {
                    'total_scans': 0,
                    'avg_score': 0,
                    'this_month': 0,
                    'unique_companies': 0
                }
        except Exception as schema_error:
            logger.error(f"Schema validation error for client {client_id} statistics: {schema_error}")
            conn.close()
            return {
                'total_scans': 0,
                'avg_score': 0,
                'this_month': 0,
                'unique_companies': 0
            }
        
        # Total scans
        cursor.execute("SELECT COUNT(*) FROM scans")
        total_scans = cursor.fetchone()[0]
        
        # Average security score
        cursor.execute("SELECT AVG(security_score) FROM scans WHERE security_score > 0")
        avg_score_result = cursor.fetchone()[0]
        avg_score = avg_score_result if avg_score_result else 0
        
        # This month's scans
        cursor.execute("""
            SELECT COUNT(*) FROM scans 
            WHERE strftime('%Y-%m', created_at) = strftime('%Y-%m', 'now')
        """)
        this_month = cursor.fetchone()[0]
        
        # Unique companies
        cursor.execute("""
            SELECT COUNT(DISTINCT lead_company) FROM scans 
            WHERE lead_company IS NOT NULL AND lead_company != ''
        """)
        unique_companies = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            'total_scans': total_scans,
            'avg_score': avg_score,
            'this_month': this_month,
            'unique_companies': unique_companies
        }
        
    except Exception as e:
        logger.error(f"Error getting scan statistics for client {client_id}: {e}")
        return {
            'total_scans': 0,
            'avg_score': 0,
            'this_month': 0,
            'unique_companies': 0
        }

if __name__ == "__main__":
    # Test database creation
    test_client_id = 999
    test_business_name = "Test Company"
    
    print(f"Testing database creation for client {test_client_id}")
    db_path = create_client_specific_database(test_client_id, test_business_name)
    
    if db_path:
        print(f"✅ Database created successfully: {db_path}")
    else:
        print("❌ Database creation failed")