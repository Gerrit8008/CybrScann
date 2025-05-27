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
        """Emergency register route - redirects to actual auth"""
        # Redirect to the actual auth blueprint route
        if request.method == 'POST':
            # Forward the POST request by rebuilding it
            from werkzeug.datastructures import MultiDict
            form_data = MultiDict(request.form)
            
            # Try to use the actual auth blueprint route
            try:
                from auth import register as auth_register
                # This is a bit hacky but necessary for emergency routing
                import flask
                with app.test_request_context('/auth/register', method='POST', data=form_data):
                    response = auth_register()
                    return response
            except Exception as e:
                flash('Registration temporarily unavailable. Please try again later.', 'warning')
                return redirect('/')
        
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
        """Emergency login route - redirects to actual auth"""
        # Redirect to the actual auth blueprint route
        if request.method == 'POST':
            # Forward the POST request by rebuilding it
            from werkzeug.datastructures import MultiDict
            form_data = MultiDict(request.form)
            
            # Try to use the actual auth blueprint route
            try:
                from auth import login as auth_login
                # This is a bit hacky but necessary for emergency routing
                import flask
                with app.test_request_context('/auth/login', method='POST', data=form_data):
                    response = auth_login()
                    return response
            except Exception as e:
                flash('Login temporarily unavailable. Please try again later.', 'warning')
                return redirect('/')
        
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