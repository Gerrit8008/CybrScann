#!/usr/bin/env python3
# wsgi.py - WSGI application entry point
import os
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(name)s - %(message)s'
)
logger = logging.getLogger(__name__)

logger.info("Starting application initialization in WSGI")

try:
    # Import the Flask app
    logger.info("Attempting to import Flask app...")
    from app import app as application
    logger.info("✅ Successfully imported app from app.py")
    
    # Test that the app is properly configured
    if application:
        logger.info(f"✅ App object exists with name: {application.name}")
        logger.info(f"✅ App has {len(application.blueprints)} blueprints registered")
        logger.info(f"✅ Blueprints: {list(application.blueprints.keys())}")
    else:
        raise Exception("App object is None")
        
except Exception as e:
    logger.error(f"❌ Error importing app: {e}")
    import traceback
    logger.error("Full traceback:")
    logger.error(traceback.format_exc())
    
    # Create a minimal application for error reporting
    logger.info("Creating fallback Flask application...")
    from flask import Flask, Response
    application = Flask(__name__)
    
    @application.route('/')
    def error_page():
        return Response(f"""
        <html>
        <head><title>CybrScan - Startup Error</title></head>
        <body>
        <h1>Application Failed to Start</h1>
        <p><strong>Error:</strong> {str(e)}</p>
        <p>Please check the logs for more details.</p>
        <pre>{traceback.format_exc()}</pre>
        </body>
        </html>
        """, mimetype='text/html')
        
    @application.route('/health')
    def health():
        return {"status": "error", "message": f"App failed to start: {str(e)}"}
        
    logger.info("✅ Fallback application created successfully")

# This allows the file to be run directly
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    application.run(host='0.0.0.0', port=port)
