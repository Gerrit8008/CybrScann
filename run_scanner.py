#!/usr/bin/env python3
"""
Entry point for running the scanner server with proper static files
"""

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
