import os
import sqlite3
import json
from datetime import datetime
import logging
from pathlib import Path

# Configure database path
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'databases', 'scanner.db')

# Ensure database directory exists
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

def init_db():
    """Initialize the database with required tables"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Create scans table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS scans (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        scan_id TEXT UNIQUE NOT NULL,
        timestamp TEXT,
        email TEXT,
        target TEXT,
        results TEXT,
        status TEXT DEFAULT 'completed',
        created_at TEXT
    )
    ''')

    # Create leads table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS leads (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        email TEXT,
        company TEXT,
        phone TEXT,
        timestamp TEXT,
        scan_id TEXT,
        FOREIGN KEY(scan_id) REFERENCES scans(scan_id)
    )
    ''')

    conn.commit()
    conn.close()
    logging.info("Database initialized successfully")

def save_scan_results(scan_data):
    """Save scan results to database with enhanced client tracking"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Convert scan results to JSON string
        results_json = json.dumps(scan_data)
        timestamp = datetime.now().isoformat()

        cursor.execute('''
        INSERT INTO scans (scan_id, timestamp, email, target, results, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            scan_data.get('scan_id'),
            scan_data.get('timestamp', timestamp),
            scan_data.get('email', ''),
            scan_data.get('target', ''),
            results_json,
            timestamp
        ))

        # Also save to client_scanner.db if client_id is available
        if scan_data.get('client_id'):
            save_client_scan_record(scan_data)
            
            # Save to client-specific database as well
            try:
                from client_database_manager import save_scan_to_client_db
                save_scan_to_client_db(scan_data['client_id'], scan_data)
            except Exception as e:
                logging.error(f"Error saving to client-specific database: {e}")

        conn.commit()
        scan_id = scan_data.get('scan_id')
        conn.close()

        logging.info(f"Scan results saved successfully with ID: {scan_id}")
        return scan_id

    except Exception as e:
        logging.error(f"Error saving scan results: {e}")
        if 'conn' in locals():
            conn.close()
        return None

def save_client_scan_record(scan_data):
    """Save scan record to client database for tracking"""
    try:
        conn = sqlite3.connect('client_scanner.db')
        cursor = conn.cursor()
        
        # Extract client information from scan data
        client_id = scan_data.get('client_id')
        scanner_id = scan_data.get('scanner_id', 'unknown')
        
        # Extract lead/user information
        name = scan_data.get('name', '')
        email = scan_data.get('email', '')
        company = scan_data.get('company', '')
        phone = scan_data.get('phone', '')
        target = scan_data.get('target', '')
        
        # Calculate overall security score
        security_score = 75  # Default
        if 'risk_assessment' in scan_data and 'overall_score' in scan_data['risk_assessment']:
            security_score = scan_data['risk_assessment']['overall_score']
        
        # Get company size (estimate based on email domain or default)
        company_size = scan_data.get('company_size')
        if not company_size:
            # Simple heuristic based on email domain
            if email:
                domain = email.split('@')[-1].lower()
                if domain in ['gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com']:
                    company_size = 'Small'
                elif company and len(company) > 20:
                    company_size = 'Large'
                else:
                    company_size = 'Medium'
            else:
                company_size = 'Unknown'
        
        timestamp = datetime.now().isoformat()
        
        # Insert into scan_history table
        cursor.execute('''
        INSERT INTO scan_history (
            client_id, scanner_id, scan_id, target_url, scan_type, status, 
            lead_name, lead_email, lead_phone, lead_company, company_size,
            security_score, results, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            client_id,
            scanner_id,
            scan_data.get('scan_id'),
            target,
            'comprehensive',
            'completed',
            name,
            email,
            phone, 
            company,
            company_size,
            security_score,
            json.dumps(scan_data),
            timestamp
        ))
        
        conn.commit()
        conn.close()
        
        logging.info(f"Client scan record saved for client {client_id}")
        
    except Exception as e:
        logging.error(f"Error saving client scan record: {e}")
        if 'conn' in locals():
            conn.close()

def get_scan_results(scan_id):
    """Retrieve scan results from database"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        cursor.execute('SELECT results FROM scans WHERE scan_id = ?', (scan_id,))
        row = cursor.fetchone()
        conn.close()

        if row:
            scan_results = json.loads(row[0])
            return scan_results
        return None

    except Exception as e:
        logging.error(f"Error retrieving scan results: {e}")
        if 'conn' in locals():
            conn.close()
        return None

def save_lead_data(lead_data):
    """Save lead information to database"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        cursor.execute('''
        INSERT INTO leads (name, email, company, phone, timestamp, scan_id)
        VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            lead_data.get('name', ''),
            lead_data.get('email', ''),
            lead_data.get('company', ''),
            lead_data.get('phone', ''),
            lead_data.get('timestamp', datetime.now().isoformat()),
            lead_data.get('scan_id')
        ))

        conn.commit()
        lead_id = cursor.lastrowid
        conn.close()

        logging.info(f"Lead data saved successfully with ID: {lead_id}")
        return lead_id

    except Exception as e:
        logging.error(f"Error saving lead data: {e}")
        if 'conn' in locals():
            conn.close()
        return None

# Initialize database when module is imported
init_db()
