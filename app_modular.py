"""
CybrScan - Modular Flask Application
Main application file with organized route imports
"""

import logging
import os
import sys
from datetime import datetime
import json

# Setup basic logging first
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)
logger.info("Starting CybrScan modular application...")

try:
    from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash
    logger.info("✅ Flask imported successfully")
except ImportError as e:
    logger.error(f"❌ Failed to import Flask: {e}")
    raise

# Import optional dependencies with fallbacks
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
    from dotenv import load_dotenv
    load_dotenv()
    logger.info("✅ Environment variables loaded")
except ImportError as e:
    logger.warning(f"⚠️ python-dotenv not available: {e}")

# Import core modules
try:
    from config import get_config
    logger.info("✅ Config imported successfully")
except ImportError as e:
    logger.warning(f"⚠️ Config module not available: {e}")
    def get_config():
        return type('Config', (), {'DEBUG': False})

try:
    from client_db import init_client_db
    logger.info("✅ Client DB imported successfully")
except ImportError as e:
    logger.warning(f"⚠️ Client DB not available: {e}")
    def init_client_db():
        pass

# Import route blueprints
try:
    from routes.main_routes import main_bp
    from routes.auth_routes import auth_bp
    from routes.scanner_routes import scanner_bp
    from routes.scan_routes import scan_bp
    from routes.admin_routes import admin_bp
    logger.info("✅ All route blueprints imported successfully")
except ImportError as e:
    logger.error(f"❌ Failed to import route blueprints: {e}")
    logger.error("Make sure all route files are properly created in the routes/ directory")
    raise

# Import existing blueprints
try:
    from client import client_bp
    logger.info("✅ Client blueprint imported successfully")
except ImportError as e:
    logger.warning(f"⚠️ Client blueprint not available: {e}")
    client_bp = None

try:
    from auth import auth_blueprint
    logger.info("✅ Auth blueprint imported successfully")
    auth_existing_bp = auth_blueprint
except ImportError as e:
    logger.warning(f"⚠️ Auth blueprint not available: {e}")
    auth_existing_bp = None

try:
    from admin import admin_blueprint
    logger.info("✅ Admin blueprint imported successfully")
    admin_existing_bp = admin_blueprint
except ImportError as e:
    logger.warning(f"⚠️ Admin blueprint not available: {e}")
    admin_existing_bp = None


def create_app():
    """Create and configure the Flask application"""
    app = Flask(__name__)
    
    # Load configuration
    config = get_config()
    app.config.from_object(config)
    
    # Set secret key
    app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    
    # Initialize CORS if available
    if CORS:
        CORS(app)
        logger.info("✅ CORS initialized")
    
    # Initialize rate limiting if available
    if Limiter:
        app.limiter = Limiter(
            app,
            key_func=get_remote_address,
            default_limits=["1000 per hour"]
        )
        logger.info("✅ Rate limiting initialized")
    
    # Initialize database
    try:
        init_client_db()
        logger.info("✅ Database initialized")
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")
    
    # Register new modular blueprints
    app.register_blueprint(main_bp)
    logger.info("✅ Main routes registered")
    
    app.register_blueprint(auth_bp, url_prefix='/auth')
    logger.info("✅ Auth routes registered")
    
    app.register_blueprint(scanner_bp)
    logger.info("✅ Scanner routes registered")
    
    app.register_blueprint(scan_bp)
    logger.info("✅ Scan routes registered")
    
    app.register_blueprint(admin_bp)
    logger.info("✅ Admin routes registered")
    
    # Register existing blueprints if available
    if client_bp:
        app.register_blueprint(client_bp)
        logger.info("✅ Client blueprint registered")
    
    if auth_existing_bp:
        app.register_blueprint(auth_existing_bp, url_prefix='/auth_existing')
        logger.info("✅ Existing auth blueprint registered")
    
    if admin_existing_bp:
        app.register_blueprint(admin_existing_bp, url_prefix='/admin_existing')
        logger.info("✅ Existing admin blueprint registered")
    
    # Add error handlers
    @app.errorhandler(404)
    def not_found(error):
        return render_template('error.html', 
                             error_code=404, 
                             error_message="Page not found"), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        logger.error(f"Internal server error: {error}")
        return render_template('error.html', 
                             error_code=500, 
                             error_message="Internal server error"), 500
    
    @app.errorhandler(403)
    def forbidden(error):
        return render_template('error.html', 
                             error_code=403, 
                             error_message="Access forbidden"), 403
    
    # Add context processors
    @app.context_processor
    def inject_globals():
        return {
            'current_year': datetime.now().year,
            'app_name': 'CybrScan'
        }
    
    logger.info("✅ CybrScan modular application created successfully")
    return app


# Create the application instance
app = create_app()

if __name__ == '__main__':
    # Development server
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('DEBUG', 'False').lower() == 'true'
    
    logger.info(f"🚀 Starting CybrScan on port {port} (debug={debug})")
    app.run(host='0.0.0.0', port=port, debug=debug)