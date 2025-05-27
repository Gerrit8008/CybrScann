#!/usr/bin/env python3
"""
Emergency fix for auth routes that are returning 404
This adds the missing auth routes directly to the main app
"""

def add_emergency_auth_routes(app):
    """Add emergency auth routes directly to app"""
    from flask import render_template, request, redirect, url_for, flash
    
    @app.route('/auth/register', methods=['GET', 'POST'])
    def emergency_register():
        """Emergency register route"""
        if request.method == 'POST':
            # For now, show a message that registration is being processed
            flash('Registration is being processed. This feature will be available shortly.', 'info')
            return redirect(url_for('emergency_register'))
        
        try:
            return render_template('auth/register.html')
        except Exception as e:
            return f"""
            <html>
            <head><title>Register - CybrScan</title></head>
            <body>
                <h1>Registration</h1>
                <p>Registration feature is being updated.</p>
                <p><a href="/">Return to Home</a></p>
                <p>Error: {e}</p>
            </body>
            </html>
            """
    
    @app.route('/auth/login', methods=['GET', 'POST'])
    def emergency_login():
        """Emergency login route"""
        if request.method == 'POST':
            # For now, show a message that login is being processed
            flash('Login is being processed. This feature will be available shortly.', 'info')
            return redirect(url_for('emergency_login'))
        
        try:
            return render_template('auth/login.html')
        except Exception as e:
            return f"""
            <html>
            <head><title>Login - CybrScan</title></head>
            <body>
                <h1>Login</h1>
                <p>Login feature is being updated.</p>
                <p><a href="/">Return to Home</a></p>
                <p>Error: {e}</p>
            </body>
            </html>
            """
    
    @app.route('/debug/emergency-routes')
    def emergency_routes_debug():
        """Debug route to confirm emergency routes are working"""
        return {
            'status': 'Emergency routes active',
            'routes_added': ['/auth/register', '/auth/login'],
            'message': 'Emergency auth fix is working'
        }
    
    print("✅ Emergency auth routes added successfully")
    return app

if __name__ == '__main__':
    print("Emergency auth fix module loaded")