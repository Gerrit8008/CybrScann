#!/usr/bin/env python3
"""
Fix script to ensure the scanner embed route pattern works correctly
"""

import os

def fix_scanner_route_pattern():
    """Fix the route pattern for scanner embed to handle scanner_id prefix"""
    scanner_routes_path = '/home/ggrun/CybrScan_1/scanner_routes.py'
    
    with open(scanner_routes_path, 'r') as f:
        content = f.read()
    
    # Look for the existing route pattern
    route_pattern = "@scanner_bp.route('/<scanner_id>/embed')"
    
    # This pattern will only match scanner IDs with the format scanner_xxxx
    new_pattern = "@scanner_bp.route('/<scanner_id>/embed')"
    
    # Update the route pattern if needed
    if route_pattern in content:
        # No changes needed, the route pattern is already correct
        print("Route pattern is already correct")
    else:
        # This case shouldn't happen as we've already fixed it, but just in case
        content = content.replace("@scanner_bp.route('/embed/<scanner_id>')", new_pattern)
        
        with open(scanner_routes_path, 'w') as f:
            f.write(content)
        
        print("Updated scanner route pattern")
    
    # Now, let's create a static entry point that properly initializes the app
    app_entry_path = '/home/ggrun/CybrScan_1/run_scanner.py'
    
    app_entry_content = """#!/usr/bin/env python3
\"\"\"
Entry point for running the scanner server with proper static files
\"\"\"

import os
from flask import Flask, send_from_directory

def create_app():
    app = Flask(__name__, 
                static_folder='static',
                template_folder='templates')
    
    # Register blueprints
    from scanner_routes import scanner_bp
    app.register_blueprint(scanner_bp)
    
    # Add a favicon route
    @app.route('/favicon.ico')
    def favicon():
        return send_from_directory(os.path.join(app.root_path, 'static'),
                                   'favicon.ico', mimetype='image/vnd.microsoft.icon')
    
    # Add a root route that redirects to a scanner
    @app.route('/')
    def index():
        from flask import redirect, url_for
        return redirect(url_for('scanner.scanner_embed', scanner_id='scanner_919391f3'))
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)
"""
    
    with open(app_entry_path, 'w') as f:
        f.write(app_entry_content)
    
    print("Created run_scanner.py entry point")
    
    # Make the script executable
    os.system('chmod +x /home/ggrun/CybrScan_1/run_scanner.py')
    
    return True

if __name__ == "__main__":
    print("Fixing scanner route pattern...")
    fix_scanner_route_pattern()
    print("Done!")