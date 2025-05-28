"""
CybrScan - Modular Flask Application
Main application file with organized route imports
Updated: 2025-05-27 - Auth routes fixed v3 - Removed conflicting fallback routes
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
    # from routes.auth_routes import auth_bp  # Commented out to avoid conflicts with main auth.py
    from routes.scanner_routes import scanner_bp
    from routes.scan_routes import scan_bp
    from routes.admin_routes import admin_bp
    logger.info("✅ All route blueprints imported successfully (auth_bp excluded to avoid conflicts)")
except ImportError as e:
    logger.error(f"❌ Failed to import route blueprints: {e}")
    logger.error("Make sure all route files are properly created in the routes/ directory")
    raise

# Import enhanced scan routes
try:
    from enhanced_scan_routes import enhanced_scan_bp
    logger.info("✅ Enhanced scan routes imported successfully")
except ImportError as e:
    logger.warning(f"⚠️ Enhanced scan routes not available: {e}")
    enhanced_scan_bp = None

# Import existing blueprints
try:
    from client import client_bp
    logger.info("✅ Client blueprint imported successfully")
except ImportError as e:
    logger.warning(f"⚠️ Client blueprint not available: {e}")
    client_bp = None

try:
    from auth import auth_bp as auth_existing_bp
    logger.info("✅ Auth blueprint imported successfully")
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
    
    # Note: Using existing auth blueprint instead of new auth_bp to maintain compatibility
    # app.register_blueprint(auth_bp)
    # logger.info("✅ Auth routes registered")
    
    app.register_blueprint(scanner_bp)
    logger.info("✅ Scanner routes registered")
    
    app.register_blueprint(scan_bp)
    logger.info("✅ Scan routes registered")
    
    app.register_blueprint(admin_bp)
    logger.info("✅ Admin routes registered")
    
    # Register enhanced scan routes if available
    if enhanced_scan_bp:
        app.register_blueprint(enhanced_scan_bp)
        logger.info("✅ Enhanced scan routes registered")
    
    # Register existing blueprints if available
    if client_bp:
        app.register_blueprint(client_bp)
        logger.info("✅ Client blueprint registered")
    
    # Keep existing auth blueprint as primary since it has more functionality
    if auth_existing_bp:
        app.register_blueprint(auth_existing_bp)  # No url_prefix since it's already defined in the blueprint
        logger.info(f"✅ Existing auth blueprint registered: {auth_existing_bp}")
        logger.info(f"✅ Auth blueprint name: {auth_existing_bp.name}")
    else:
        logger.error("❌ Auth blueprint not available - auth routes will not work!")
    
    # Do not register the old admin blueprint to avoid conflicts
    # if admin_existing_bp:
    #     app.register_blueprint(admin_existing_bp, url_prefix='/admin_existing')
    #     logger.info("✅ Existing admin blueprint registered")
    logger.info("ℹ️ Old admin blueprint skipped to avoid conflicts with new admin routes")
    
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
    
    # Debug: Print all registered routes
    logger.info("📋 Registered routes:")
    for rule in app.url_map.iter_rules():
        methods = ','.join(sorted(rule.methods - {'HEAD', 'OPTIONS'}))
        logger.info(f"  {methods} {rule} -> {rule.endpoint}")
    
    # Emergency auth fix for deployment issues (disabled for now)
    # try:
    #     from emergency_auth_fix import add_emergency_auth_routes
    #     app = add_emergency_auth_routes(app)
    #     logger.info("✅ Emergency auth routes added")
    # except Exception as e:
    #     logger.warning(f"⚠️ Emergency auth fix not applied: {e}")
    
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