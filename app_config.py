# app_config.py - Configuration, imports, and utility functions

import logging
import os
import sqlite3
import platform
import socket
import re
import uuid
import urllib.parse
import time
from datetime import datetime, timedelta
import json
import sys
import traceback

# Setup basic logging first
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)
logger.info("Starting CybrScan application initialization...")

# Import handling with fallbacks
try:
    from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash, send_file
    logger.info("✅ Flask imported successfully")
except ImportError as e:
    logger.error(f"❌ Failed to import Flask: {e}")
    raise

try:
    from werkzeug.utils import secure_filename
    logger.info("✅ Werkzeug imported successfully")
except ImportError as e:
    logger.warning(f"⚠️ Werkzeug not available: {e}")
    # Create a fallback secure_filename function
    def secure_filename(filename):
        return "".join(c for c in filename if c.isalnum() or c in "._-")

try:
    from flask_cors import CORS
    logger.info("✅ Flask-CORS imported successfully")
except ImportError as e:
    logger.warning(f"⚠️ Flask-CORS not available: {e}")
    CORS = None

try:
    from flask_limiter import Limiter
    from flask_limiter.util import get_remote_address
    logger.info("✅ Flask-Limiter imported successfully")
except ImportError as e:
    logger.warning(f"⚠️ Flask-Limiter not available: {e}")
    Limiter = None

try:
    from email_handler import send_email_report
    logger.info("✅ Email handler imported successfully")
except ImportError as e:
    logger.warning(f"⚠️ Email handler not available: {e}")
    def send_email_report(*args, **kwargs):
        return {"status": "error", "message": "Email functionality not available"}

try:
    from config import get_config
    logger.info("✅ Config imported successfully")
except ImportError as e:
    logger.warning(f"⚠️ Config module not available: {e}")
    def get_config():
        return type('Config', (), {'DEBUG': False})

try:
    from dotenv import load_dotenv
    load_dotenv()
    logger.info("✅ Environment variables loaded")
except ImportError as e:
    logger.warning(f"⚠️ python-dotenv not available: {e}")

try:
    from flask_login import LoginManager, current_user, login_required
    logger.info("✅ Flask-Login imported successfully")
except ImportError as e:
    logger.warning(f"⚠️ Flask-Login not available: {e}")
    LoginManager = None
    current_user = None
    def login_required(f):
        return f

try:
    from client_db import init_client_db, CLIENT_DB_PATH
    logger.info("✅ Client DB imported successfully")
except ImportError as e:
    logger.warning(f"⚠️ Client DB not available: {e}")
    CLIENT_DB_PATH = "client_scanner.db"
    def init_client_db():
        pass

try:
    from database_manager import DatabaseManager
    logger.info("✅ Database Manager imported successfully")
except ImportError as e:
    logger.warning(f"⚠️ Database Manager not available: {e}")
    class DatabaseManager:
        def __init__(self):
            pass

# Database fallbacks for missing modules
try:
    import psutil
    logger.info("✅ psutil imported successfully")
except ImportError as e:
    logger.warning(f"⚠️ psutil not available: {e}")

try:
    from security_scanner import perform_comprehensive_scan, generate_html_report, determine_industry, get_industry_benchmarks, calculate_industry_percentile
    logger.info("✅ Security scanner imported successfully")
except ImportError as e:
    logger.warning(f"⚠️ Security scanner not available: {e}")
    def perform_comprehensive_scan(target): 
        return {"status": "error", "message": "Scanner not available"}
    def generate_html_report(results): 
        return "<html><body>Scan not available</body></html>"
    def determine_industry(domain): 
        return "Unknown"
    def get_industry_benchmarks(industry): 
        return {}
    def calculate_industry_percentile(score, industry): 
        return 0

# Define upload folder for file uploads
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Make sure the directory exists
os.makedirs(os.path.dirname(CLIENT_DB_PATH), exist_ok=True)

# Import database functionality
from db import init_db, save_scan_results, get_scan_results, save_lead_data, DB_PATH

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

def log_system_info():
    """Log details about the system environment"""
    logger = logging.getLogger(__name__)
    
    logger.info("----- System Information -----")
    logger.info(f"Python version: {sys.version}")
    logger.info(f"Platform: {platform.platform()}")
    logger.info(f"Working directory: {os.getcwd()}")
    logger.info(f"Database path: {DB_PATH}")
    logger.info(f"Client database path: {CLIENT_DB_PATH}")
    
    # Check database file status
    if os.path.exists(DB_PATH):
        logger.info(f"Main database exists: {DB_PATH}")
    else:
        logger.warning(f"Main database not found: {DB_PATH}")
    
    if os.path.exists(CLIENT_DB_PATH):
        logger.info(f"Client database exists: {CLIENT_DB_PATH}")
    else:
        logger.warning(f"Client database not found: {CLIENT_DB_PATH}")
    
    logger.info("--------------------------------")

def check_network_availability():
    """Check if the system has network connectivity"""
    try:
        socket.create_connection(("8.8.8.8", 53), timeout=3)
        return True
    except (socket.timeout, socket.error):
        return False

def validate_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def sanitize_input(input_string):
    """Sanitize user input to prevent injection attacks"""
    if not input_string:
        return ""
    
    # Remove potentially dangerous characters
    cleaned = re.sub(r'[<>"\';]', '', str(input_string))
    return cleaned.strip()

def generate_scan_id():
    """Generate a unique scan ID"""
    return str(uuid.uuid4())

def get_client_ip():
    """Get the client's IP address"""
    if request.environ.get('HTTP_X_FORWARDED_FOR') is None:
        return request.environ['REMOTE_ADDR']
    else:
        return request.environ['HTTP_X_FORWARDED_FOR']

def determine_industry_from_data(company_name="", email_domain=""):
    """
    Determine the industry type based on company name and email domain.
    
    Args:
        company_name (str): Name of the company
        email_domain (str): Email domain (e.g., 'company.com')
    
    Returns:
        str: Industry type (healthcare, financial, retail, etc.)
    """
    # Convert inputs to lowercase for case-insensitive matching
    company_name = company_name.lower() if company_name else ""
    email_domain = email_domain.lower() if email_domain else ""
    
    # Healthcare indicators
    healthcare_keywords = ['hospital', 'health', 'medical', 'clinic', 'care', 'pharma', 
                          'doctor', 'dental', 'medicine', 'healthcare']
    healthcare_domains = ['hospital.org', 'health.org', 'med.org']
    
    # Financial indicators
    financial_keywords = ['bank', 'finance', 'investment', 'capital', 'financial', 
                         'insurance', 'credit', 'wealth', 'asset', 'accounting']
    financial_domains = ['bank.com', 'invest.com', 'financial.com']
    
    # Retail indicators
    retail_keywords = ['retail', 'shop', 'store', 'market', 'commerce', 'mall', 
                      'sales', 'buy', 'shopping', 'consumer']
    retail_domains = ['shop.com', 'retail.com', 'store.com', 'market.com']
    
    # Education indicators
    education_keywords = ['school', 'university', 'college', 'academy', 'education', 
                         'institute', 'learning', 'teach', 'student', 'faculty']
    education_domains = ['edu', 'education.org', 'university.edu', 'school.org']
    
    # Manufacturing indicators
    manufacturing_keywords = ['manufacturing', 'factory', 'production', 'industrial', 
                             'build', 'maker', 'assembly', 'fabrication']
    manufacturing_domains = ['mfg.com', 'industrial.com', 'production.com']
    
    # Government indicators
    government_keywords = ['government', 'gov', 'federal', 'state', 'municipal', 
                          'county', 'agency', 'authority', 'administration']
    government_domains = ['gov', 'state.gov', 'county.gov', 'city.gov']
    
    # Check company name for industry keywords
    for keyword in healthcare_keywords:
        if keyword in company_name:
            return 'healthcare'
    
    for keyword in financial_keywords:
        if keyword in company_name:
            return 'financial'
    
    for keyword in retail_keywords:
        if keyword in company_name:
            return 'retail'
    
    for keyword in education_keywords:
        if keyword in company_name:
            return 'education'
    
    for keyword in manufacturing_keywords:
        if keyword in company_name:
            return 'manufacturing'
    
    for keyword in government_keywords:
        if keyword in company_name:
            return 'government'
    
    # Check email domain for industry indicators
    for domain in healthcare_domains:
        if domain in email_domain:
            return 'healthcare'
    
    for domain in financial_domains:
        if domain in email_domain:
            return 'financial'
    
    for domain in retail_domains:
        if domain in email_domain:
            return 'retail'
    
    for domain in education_domains:
        if domain in email_domain:
            return 'education'
    
    for domain in manufacturing_domains:
        if domain in email_domain:
            return 'manufacturing'
    
    for domain in government_domains:
        if domain in email_domain:
            return 'government'
    
    # Check TLD for additional clues
    if '.edu' in email_domain:
        return 'education'
    elif '.gov' in email_domain:
        return 'government'
    elif '.mil' in email_domain:
        return 'government'
    elif '.org' in email_domain:
        return 'non-profit'
    
    # Default to technology sector if no clear indicators
    return 'technology'