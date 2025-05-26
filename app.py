# app.py - Main Flask application file

import os
import sys
import traceback
from flask import Flask

# Import configuration and setup
from app_config import (
    logger, setup_logging, log_system_info, check_network_availability,
    CLIENT_DB_PATH, UPLOAD_FOLDER, CORS, Limiter, get_remote_address,
    DatabaseManager, get_config, init_client_db
)

# Import routes
from app_routes import setup_routes

# Initialize database manager
db_manager = DatabaseManager()

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

def create_app():
    """Create and configure Flask application"""
    
    # Initialize Flask app
    app = Flask(__name__)
    
    # Configure app
    config = get_config()
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-change-this')
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
    
    # Setup logging
    setup_logging()
    log_system_info()
    
    # Check network connectivity
    if check_network_availability():
        logger.info("✅ Network connectivity available")
    else:
        logger.warning("⚠️ Limited network connectivity detected")
    
    # Initialize CORS if available
    if CORS:
        CORS(app, resources={
            r"/api/*": {"origins": "*"},
            r"/scan": {"origins": "*"},
            r"/results/*": {"origins": "*"}
        })
        logger.info("✅ CORS initialized")
    
    # Initialize rate limiting if available
    if Limiter:
        limiter = Limiter(
            app,
            key_func=get_remote_address,
            default_limits=["1000 per hour"]
        )
        
        # Add rate limits to specific routes
        @limiter.limit("10 per minute")
        def scan_rate_limit():
            pass
        
        logger.info("✅ Rate limiting initialized")
    
    # Initialize databases
    try:
        from db import init_db
        init_db()
        logger.info("✅ Main database initialized")
    except Exception as e:
        logger.error(f"❌ Failed to initialize main database: {e}")
    
    try:
        init_client_db()
        logger.info("✅ Client database initialized")
    except Exception as e:
        logger.error(f"❌ Failed to initialize client database: {e}")
    
    # Register blueprints
    register_blueprints(app)
    
    # Setup application routes
    setup_routes(app)
    
    # Log final status
    registered_blueprints = list(app.blueprints.keys())
    logger.info(f"🎯 Final registered blueprints: {registered_blueprints}")
    
    if len(registered_blueprints) < 2:
        logger.error("❌ Critical: Less than 2 blueprints registered! App may not work properly.")
    else:
        logger.info("✅ Blueprint registration completed successfully")
    
    return app

def register_blueprints(app):
    """Register all application blueprints"""
    
    # Essential blueprints (auth and admin)
    try:
        from auth_routes import auth_bp
        app.register_blueprint(auth_bp)
        logger.info("✅ Registered auth_bp")
    except Exception as e:
        logger.error(f"❌ Failed to register auth_bp: {e}")
        logger.error(traceback.format_exc())

    try:
        from admin import admin_bp
        app.register_blueprint(admin_bp)
        logger.info("✅ Registered admin_bp")
    except Exception as e:
        logger.error(f"❌ Failed to register admin_bp: {e}")
        logger.error(traceback.format_exc())

    # Optional blueprints - Client blueprint is CRITICAL for login
    try:
        from client import client_bp
        app.register_blueprint(client_bp)
        logger.info("✅ Registered client_bp")
    except Exception as e:
        logger.error(f"❌ CRITICAL: Could not register client_bp: {e}")
        logger.error("This will cause login failures for client users!")
        logger.error(traceback.format_exc())

    try:
        from api import api_bp
        app.register_blueprint(api_bp)
        logger.info("✅ Registered api_bp")
    except Exception as e:
        logger.warning(f"⚠️ Could not register api_bp: {e}")

    try:
        from scanner_router import scanner_bp
        app.register_blueprint(scanner_bp)
        logger.info("✅ Registered scanner_bp")
    except Exception as e:
        logger.warning(f"⚠️ Could not register scanner_bp: {e}")

def apply_route_fixes():
    """Apply all route fixes"""  
    # Disabled to prevent conflicts
    pass

# Create the Flask app
app = create_app()

# Direct database fix function (kept for backwards compatibility)
def direct_db_fix():
    """Direct database fix for admin user creation"""
    try:
        from app_routes import direct_db_fix
        return direct_db_fix()
    except Exception as e:
        logger.error(f"Database fix failed: {e}")
        return f"Database fix failed: {e}"

# ---------------------------- MAIN ENTRY POINT ----------------------------

if __name__ == '__main__':
    try:
        # Get port from environment variable or use default
        port = int(os.environ.get('PORT', 5000))
        
        # Run database fix on startup
        direct_db_fix()
        
        # Use 0.0.0.0 to make the app accessible from any IP
        debug_mode = os.environ.get('FLASK_ENV') == 'development'
        
        logger.info(f"🚀 Starting CybrScan on port {port}, debug={debug_mode}")
        app.run(host='0.0.0.0', port=port, debug=debug_mode)
        
    except Exception as e:
        logger.error(f"❌ Failed to start application: {e}")
        logger.error(traceback.format_exc())
        sys.exit(1)