from contextlib import contextmanager
import sqlite3
import logging
import uuid
from datetime import datetime

@contextmanager
def get_db_connection(db_path=None):
    """Context manager for database connections with improved error handling"""
    if db_path is None:
        from client_db import CLIENT_DB_PATH
        db_path = CLIENT_DB_PATH
        
    conn = None
    try:
        conn = sqlite3.connect(db_path, timeout=20.0)  # Increase timeout value
        conn.row_factory = sqlite3.Row
        yield conn
        conn.commit()  # Auto-commit if no exceptions
    except sqlite3.OperationalError as oe:
        if conn:
            conn.rollback()
        if "database is locked" in str(oe):
            # Add specific handling for locked database errors
            logging.error("Database lock error: Increase timeout or implement retry logic")
        raise
    except Exception as e:
        if conn:
            conn.rollback()
        logging.error(f"Database error: {str(e)}")
        raise
    finally:
        if conn:
            conn.close()

@contextmanager
def get_client_db(db_manager, client_id):
    """Context manager for client database connections"""
    conn = None
    try:
        conn = db_manager.get_client_connection(client_id)
        conn.row_factory = sqlite3.Row
        yield conn
    finally:
        if conn:
            conn.close()

def save_lead_data(lead_data):
    """Save lead data to the leads database"""
    try:
        # Use leads.db for storing lead data
        conn = sqlite3.connect('leads.db', timeout=20.0)
        cursor = conn.cursor()
        
        # Create leads table if it doesn't exist - check existing schema first
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='leads'")
        table_exists = cursor.fetchone()
        
        if not table_exists:
            cursor.execute('''
            CREATE TABLE leads (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                lead_id TEXT UNIQUE,
                name TEXT,
                email TEXT,
                company TEXT,
                phone TEXT,
                industry TEXT,
                company_size TEXT,
                company_website TEXT,
                target TEXT,
                client_os TEXT,
                client_browser TEXT,
                windows_version TEXT,
                timestamp TEXT,
                created_at TEXT
            )
            ''')
        else:
            # Check if required columns exist, if not add them
            cursor.execute("PRAGMA table_info(leads)")
            columns = [column[1] for column in cursor.fetchall()]
            
            if 'lead_id' not in columns:
                cursor.execute("ALTER TABLE leads ADD COLUMN lead_id TEXT")
                logging.info("Added lead_id column to existing leads table")
            
            if 'industry' not in columns:
                cursor.execute("ALTER TABLE leads ADD COLUMN industry TEXT")
                logging.info("Added industry column to existing leads table")
            
            if 'company_size' not in columns:
                cursor.execute("ALTER TABLE leads ADD COLUMN company_size TEXT")
                logging.info("Added company_size column to existing leads table")
            
            if 'company_website' not in columns:
                cursor.execute("ALTER TABLE leads ADD COLUMN company_website TEXT")
                logging.info("Added company_website column to existing leads table")
            
            if 'target' not in columns:
                cursor.execute("ALTER TABLE leads ADD COLUMN target TEXT")
                logging.info("Added target column to existing leads table")
            
            if 'client_os' not in columns:
                cursor.execute("ALTER TABLE leads ADD COLUMN client_os TEXT")
                logging.info("Added client_os column to existing leads table")
            
            if 'client_browser' not in columns:
                cursor.execute("ALTER TABLE leads ADD COLUMN client_browser TEXT")
                logging.info("Added client_browser column to existing leads table")
            
            if 'windows_version' not in columns:
                cursor.execute("ALTER TABLE leads ADD COLUMN windows_version TEXT")
                logging.info("Added windows_version column to existing leads table")
            
            if 'timestamp' not in columns:
                cursor.execute("ALTER TABLE leads ADD COLUMN timestamp TEXT")
                logging.info("Added timestamp column to existing leads table")
        
        # Generate unique lead ID
        lead_id = f"lead_{uuid.uuid4().hex[:12]}"
        
        # Insert lead data
        cursor.execute('''
        INSERT INTO leads (
            lead_id, name, email, company, phone, industry, 
            company_size, company_website, target, client_os, 
            client_browser, windows_version, timestamp, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            lead_id,
            lead_data.get('name', ''),
            lead_data.get('email', ''),
            lead_data.get('company', ''),
            lead_data.get('phone', ''),
            lead_data.get('industry', ''),
            lead_data.get('company_size', ''),
            lead_data.get('company_website', ''),
            lead_data.get('target', ''),
            lead_data.get('client_os', ''),
            lead_data.get('client_browser', ''),
            lead_data.get('windows_version', ''),
            lead_data.get('timestamp', datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
            datetime.now().isoformat()
        ))
        
        conn.commit()
        conn.close()
        
        logging.info(f"Lead data saved successfully with ID: {lead_id}")
        return lead_id
        
    except Exception as e:
        logging.error(f"Error saving lead data: {e}")
        return None

def get_scan_results(scan_id):
    """Get scan results by scan ID"""
    try:
        # Check multiple databases for scan results
        
        # First check leads.db
        conn = sqlite3.connect('leads.db', timeout=20.0)
        cursor = conn.cursor()
        
        # Try to find by lead_id
        cursor.execute('SELECT * FROM leads WHERE lead_id = ?', (scan_id,))
        lead_row = cursor.fetchone()
        conn.close()
        
        if lead_row:
            # Convert lead data to scan results format
            columns = ['id', 'lead_id', 'name', 'email', 'company', 'phone', 'industry', 
                      'company_size', 'company_website', 'target', 'client_os', 
                      'client_browser', 'windows_version', 'timestamp', 'created_at']
            lead_data = dict(zip(columns[:len(lead_row)], lead_row))
            
            return {
                'scan_id': scan_id,
                'timestamp': lead_data.get('timestamp', ''),
                'email': lead_data.get('email', ''),
                'name': lead_data.get('name', ''),
                'company': lead_data.get('company', ''),
                'target': lead_data.get('target', ''),
                'risk_assessment': {
                    'overall_score': 75,
                    'risk_level': 'Medium'
                },
                'recommendations': [
                    'Implement comprehensive security monitoring',
                    'Regular security assessments',
                    'Employee training programs'
                ]
            }
        
        return None
        
    except Exception as e:
        logging.error(f"Error getting scan results for {scan_id}: {e}")
        return None
