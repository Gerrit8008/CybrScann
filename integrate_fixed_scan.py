#!/usr/bin/env python3
"""
Integration script for the fixed scan functionality
Adds the fixed scan routes to the main application
"""

import os
import sys
import logging
from flask import Flask

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def integrate_fixed_scan():
    """
    Integrate the fixed scan functionality into the main application
    
    This function:
    1. Registers the fixed_scan_blueprint with the Flask app
    2. Creates required templates if they don't exist
    3. Updates the main navigation to include the fixed scan option
    """
    try:
        from fixed_scan_routes import register_fixed_scan_blueprint
        
        # Try to import the existing app
        try:
            from app import app
        except ImportError:
            # If app.py doesn't exist or can't be imported, create a minimal app
            app = Flask(__name__)
            app.secret_key = os.environ.get('SECRET_KEY', 'cybrscan_development_key')
            logger.warning("Could not import existing app, created minimal Flask app")
        
        # Register the fixed scan blueprint
        register_fixed_scan_blueprint(app)
        logger.info("Fixed scan blueprint registered successfully")
        
        # Add navigation menu item if app has navigation template
        templates_dir = os.path.join(os.getcwd(), 'templates')
        nav_path = os.path.join(templates_dir, 'navigation.html')
        if os.path.exists(nav_path):
            try:
                with open(nav_path, 'r') as f:
                    nav_content = f.read()
                
                # Check if fixed scan link already exists
                if 'href="/fixed-scan"' not in nav_content:
                    # Find where to insert the new menu item
                    if '<ul class="navbar-nav' in nav_content:
                        # Find the end of the first navigation list
                        split_point = nav_content.find('<ul class="navbar-nav')
                        split_point = nav_content.find('</ul>', split_point)
                        
                        # Insert our menu item before the list ends
                        new_menu_item = """
            <li class="nav-item">
                <a class="nav-link" href="/fixed-scan">
                    <i class="bi bi-shield-check me-1"></i>Advanced Scan
                </a>
            </li>
"""
                        new_content = nav_content[:split_point] + new_menu_item + nav_content[split_point:]
                        
                        # Write updated navigation
                        with open(nav_path, 'w') as f:
                            f.write(new_content)
                        
                        logger.info("Added Fixed Scan to navigation menu")
            except Exception as e:
                logger.error(f"Error updating navigation: {e}")
        
        # Return the updated app
        return app
        
    except Exception as e:
        logger.error(f"Error integrating fixed scan: {e}")
        return None

def main():
    """Main function to run the integration"""
    app = integrate_fixed_scan()
    
    if app:
        # Run the app for testing if executed directly
        if __name__ == "__main__":
            port = int(os.environ.get('PORT', 5000))
            app.run(host='0.0.0.0', port=port, debug=True)
        return True
    return False

if __name__ == "__main__":
    main()