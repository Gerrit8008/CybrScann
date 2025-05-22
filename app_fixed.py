#!/usr/bin/env python3
"""
CybrScan - MSP Lead Generation Security Scanner Platform
Fixed version with proper route registration and database management
"""

import logging
import os
import sqlite3
import platform
import socket
import re
import uuid
from werkzeug.utils import secure_filename
import urllib.parse
from datetime import datetime
import json
import sys
import traceback
import requests
from datetime import timedelta
from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_login import LoginManager, current_user, login_required
from email_handler import send_email_report
from config import get_config
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Constants
SEVERITY = {
    "Critical": 10,
    "High": 7,
    "Medium": 5,
    "Low": 2,
    "Info": 1
}

SEVERITY_ICONS = {
    "Critical": "❌",
    "High": "⚠️",
    "Medium": "⚠️",
    "Low": "ℹ️"
}

GATEWAY_PORT_WARNINGS = {
    21: ("FTP (insecure)", "High"),
    23: ("Telnet (insecure)", "High"),
    80: ("HTTP (no encryption)", "Medium"),
    443: ("HTTPS", "Low"),
    3389: ("Remote Desktop (RDP)", "Critical"),
    5900: ("VNC", "High"),
    22: ("SSH", "Low"),
}

# Setup logging
def setup_logging():
    """Configure application logging"""
    # Create logs directory
    logs_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs')
    os.makedirs(logs_dir, exist_ok=True)
    
    log_filename = os.path.join(logs_dir, f"security_scan_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
    
    # Configure root logger
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    
    # Remove any existing handlers
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # Create formatters
    file_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(name)s - %(funcName)s - Line %(lineno)d - %(message)s')
    console_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    
    # File handler (detailed)
    file_handler = logging.FileHandler(log_filename)
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(file_formatter)
    
    # Console handler (less detailed)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(console_formatter)
    
    # Add handlers
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    logger.info("Application started")
    logger.info(f"Detailed logs will be saved to: {log_filename}")
    
    return logger

def create_app():
    """Create and configure the Flask application"""
    app = Flask(__name__)
    app.secret_key = os.environ.get('SECRET_KEY', 'your-secret-key-here')
    
    # Enable CORS
    CORS(app)
    
    # Create rate limiter
    limiter = Limiter(
        app=app,
        key_func=get_remote_address,
        default_limits=["200 per day", "50 per hour"],
        storage_uri="memory://"
    )
    
    return app, limiter

def init_unified_database():
    """Initialize a single unified database for all operations"""
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'cybrscan.db')
    
    logging.info(f"Initializing unified database at: {db_path}")
    
    # Create database directory if it doesn't exist
    db_dir = os.path.dirname(db_path)
    if not os.path.exists(db_dir):
        os.makedirs(db_dir)
    
    # Connect to the database
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row  # Enable row factory for dict-like access
    cursor = conn.cursor()
    
    # Create users table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL UNIQUE,
        email TEXT NOT NULL UNIQUE,
        password_hash TEXT NOT NULL,
        salt TEXT NOT NULL,
        role TEXT DEFAULT 'client',
        full_name TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        last_login TEXT,
        active INTEGER DEFAULT 1
    )
    ''')
    
    # Create clients table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS clients (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        business_name TEXT NOT NULL,
        business_domain TEXT NOT NULL,
        contact_email TEXT NOT NULL,
        contact_phone TEXT,
        scanner_name TEXT,
        subscription_level TEXT DEFAULT 'basic',
        subscription_status TEXT DEFAULT 'active',
        subscription_start TEXT,
        subscription_end TEXT,
        api_key TEXT UNIQUE,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        created_by INTEGER,
        updated_at TEXT,
        updated_by INTEGER,
        active INTEGER DEFAULT 1,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
        FOREIGN KEY (created_by) REFERENCES users(id),
        FOREIGN KEY (updated_by) REFERENCES users(id)
    )
    ''')
    
    # Create customizations table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS customizations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        client_id INTEGER NOT NULL,
        primary_color TEXT DEFAULT '#007bff',
        secondary_color TEXT DEFAULT '#6c757d',
        logo_path TEXT,
        favicon_path TEXT,
        email_subject TEXT,
        email_intro TEXT,
        email_footer TEXT,
        default_scans TEXT,
        css_override TEXT,
        html_override TEXT,
        last_updated TEXT DEFAULT CURRENT_TIMESTAMP,
        updated_by INTEGER,
        FOREIGN KEY (client_id) REFERENCES clients(id) ON DELETE CASCADE,
        FOREIGN KEY (updated_by) REFERENCES users(id)
    )
    ''')
    
    # Create deployed_scanners table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS deployed_scanners (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        client_id INTEGER NOT NULL,
        scanner_name TEXT NOT NULL,
        subdomain TEXT UNIQUE,
        domain TEXT,
        deploy_status TEXT DEFAULT 'pending',
        deploy_date TEXT DEFAULT CURRENT_TIMESTAMP,
        last_updated TEXT DEFAULT CURRENT_TIMESTAMP,
        config_path TEXT,
        template_version TEXT,
        api_key TEXT UNIQUE,
        FOREIGN KEY (client_id) REFERENCES clients(id) ON DELETE CASCADE
    )
    ''')
    
    # Create scan_history table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS scan_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        client_id INTEGER NOT NULL,
        scanner_id INTEGER,
        scan_id TEXT UNIQUE NOT NULL,
        timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
        target TEXT NOT NULL,
        scan_type TEXT NOT NULL,
        status TEXT DEFAULT 'pending',
        results TEXT,
        report_path TEXT,
        security_score INTEGER,
        issues_found INTEGER DEFAULT 0,
        FOREIGN KEY (client_id) REFERENCES clients(id) ON DELETE CASCADE,
        FOREIGN KEY (scanner_id) REFERENCES deployed_scanners(id) ON DELETE SET NULL
    )
    ''')
    
    # Create sessions table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS sessions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        session_token TEXT UNIQUE NOT NULL,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        expires_at TEXT,
        ip_address TEXT,
        user_agent TEXT,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
    )
    ''')
    
    # Create audit_log table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS audit_log (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        action TEXT NOT NULL,
        entity_type TEXT NOT NULL,
        entity_id INTEGER NOT NULL,
        changes TEXT,
        timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
        ip_address TEXT,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
    )
    ''')
    
    # Create indices for better performance
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_users_username ON users(username)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_clients_user_id ON clients(user_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_clients_api_key ON clients(api_key)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_sessions_token ON sessions(session_token)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_scan_history_client ON scan_history(client_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_scan_history_scanner ON scan_history(scanner_id)')
    
    conn.commit()
    
    # Verify tables were created
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    logging.info(f"Database tables created/verified: {[table[0] for table in tables]}")
    
    conn.close()
    logging.info("Unified database initialization completed")
    
    return db_path

def register_blueprints(app):
    """Register all blueprints with the Flask application"""
    try:
        # Import blueprints
        from auth_routes import auth_bp
        from admin_routes_fixed import admin_bp
        from client_routes_fixed import client_bp
        from api_routes_fixed import api_bp
        from scanner_routes_fixed import scanner_bp
        
        # Register blueprints
        app.register_blueprint(auth_bp)
        app.register_blueprint(admin_bp)
        app.register_blueprint(client_bp)
        app.register_blueprint(api_bp)
        app.register_blueprint(scanner_bp)
        
        logging.info(f"Registered blueprints: {list(app.blueprints.keys())}")
        
    except Exception as e:
        logging.error(f"Error registering blueprints: {e}")
        logging.error(traceback.format_exc())

# Initialize logging
logger = setup_logging()

# Initialize unified database
DB_PATH = init_unified_database()

# Create the Flask app
app, limiter = create_app()

# Register blueprints
register_blueprints(app)

# Main route
@app.route('/')
def index():
    """Main landing page"""
    return render_template('index.html')

# Health check route
@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'database': 'connected' if os.path.exists(DB_PATH) else 'not found'
    })

if __name__ == '__main__':
    logging.info("Starting CybrScan application...")
    app.run(debug=True, host='0.0.0.0', port=5000)