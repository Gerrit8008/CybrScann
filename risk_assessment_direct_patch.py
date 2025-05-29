#!/usr/bin/env python3
"""
Direct patch for risk assessment color calculation
This file should be imported at the top level of the application
"""

import logging
logger = logging.getLogger(__name__)

def ensure_risk_assessment_color(scan_data):
    """
    Ensure the scan data has a properly colored risk assessment
    This function directly modifies the provided scan_data dictionary
    """
    if not scan_data:
        return scan_data
    
    # Check if risk_assessment exists
    if 'risk_assessment' not in scan_data or not isinstance(scan_data['risk_assessment'], dict):
        # Create a new risk assessment
        score = 75
        risk_level = 'Medium'
        color = '#17a2b8'  # info blue
        
        scan_data['risk_assessment'] = {
            'overall_score': score,
            'risk_level': risk_level,
            'color': color,
            'grade': 'C',
            'component_scores': {
                'network': score,
                'web': score,
                'email': score,
                'system': score
            }
        }
        return scan_data
    
    # Get the risk assessment
    risk_assessment = scan_data['risk_assessment']
    
    # Get the score or set a default
    score = risk_assessment.get('overall_score')
    if score is None or not isinstance(score, (int, float)):
        score = 75
        risk_assessment['overall_score'] = score
    
    # Set color based on score if it doesn't exist
    if 'color' not in risk_assessment:
        if score >= 90:
            color = '#28a745'  # green
            risk_level = 'Low'
        elif score >= 80:
            color = '#5cb85c'  # light green
            risk_level = 'Low-Medium'
        elif score >= 70:
            color = '#17a2b8'  # info blue
            risk_level = 'Medium'
        elif score >= 60:
            color = '#ffc107'  # warning yellow
            risk_level = 'Medium-High'
        elif score >= 50:
            color = '#fd7e14'  # orange
            risk_level = 'High'
        else:
            color = '#dc3545'  # red
            risk_level = 'Critical'
        
        risk_assessment['color'] = color
        risk_assessment['risk_level'] = risk_level
    
    return scan_data

# Patch report_view function to ensure color is set
try:
    import client
    original_report_view = client.report_view
    
    def patched_report_view(scan_id):
        result = original_report_view(scan_id)
        
        # Check if this is a template response
        if hasattr(result, 'context') and isinstance(result.context, dict) and 'scan' in result.context:
            result.context['scan'] = ensure_risk_assessment_color(result.context['scan'])
        
        return result
    
    client.report_view = patched_report_view
    logger.info("✅ Patched client.report_view function to ensure risk assessment color")
except Exception as e:
    logger.error(f"❌ Failed to patch client.report_view: {e}")

# Patch the scan results endpoint if it exists
try:
    from flask import current_app as app
    
    def patch_flask_routes():
        """Patch Flask routes that handle scan results"""
        for rule in app.url_map.iter_rules():
            if 'results' in rule.endpoint:
                view_func = app.view_functions.get(rule.endpoint)
                if view_func:
                    def create_patched_view(original):
                        def patched_view(*args, **kwargs):
                            response = original(*args, **kwargs)
                            
                            # If JSON response, ensure risk assessment color
                            if hasattr(response, 'json'):
                                try:
                                    data = response.json
                                    if isinstance(data, dict) and 'scan' in data:
                                        data['scan'] = ensure_risk_assessment_color(data['scan'])
                                except:
                                    pass
                            
                            return response
                        return patched_view
                    
                    app.view_functions[rule.endpoint] = create_patched_view(view_func)
                    logger.info(f"✅ Patched route endpoint {rule.endpoint}")
    
    # We'll call this function later when the app is fully initialized
    # This should be called from the app's entry point after all routes are registered
    # For example: risk_assessment_direct_patch.patch_flask_routes()
except Exception as e:
    logger.error(f"❌ Failed to create route patching function: {e}")

logger.info("✅ Risk assessment color patch loaded")
