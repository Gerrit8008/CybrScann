"""
Enhanced Scan Report Generator
Generates beautiful, comprehensive security reports with visual elements
"""

import json
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

def generate_enhanced_html_report(scan_results, client_branding=None):
    """
    Generate comprehensive HTML report for enhanced scan results
    
    Args:
        scan_results (dict): Complete scan results
        client_branding (dict): Client branding customizations
        
    Returns:
        str: HTML report content
    """
    try:
        # Extract key metrics
        risk_assessment = scan_results.get('risk_assessment', {})
        overall_score = risk_assessment.get('overall_score', 75)
        risk_level = risk_assessment.get('risk_level', 'Medium')
        grade = risk_assessment.get('grade', 'C')
        
        # Get component scores
        component_scores = risk_assessment.get('component_scores', {})
        
        # Branding variables
        primary_color = client_branding.get('primary_color', '#1a237e') if client_branding else '#1a237e'
        secondary_color = client_branding.get('secondary_color', '#d96c33') if client_branding else '#d96c33'
        business_name = client_branding.get('business_name', 'CybrScan') if client_branding else 'CybrScan'
        logo_path = client_branding.get('logo_path', '') if client_branding else ''
        
        # Start building HTML
        html = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Enhanced Security Assessment Report - {business_name}</title>
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
            <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.0/font/bootstrap-icons.css">
            <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
            
            <style>
                :root {{
                    --primary-color: {primary_color};
                    --secondary-color: {secondary_color};
                    --gradient: linear-gradient(135deg, {primary_color}, {secondary_color});
                }}
                
                body {{
                    font-family: 'Inter', sans-serif;
                    line-height: 1.6;
                    color: #333;
                    background: #f8f9fa;
                }}
                
                .report-header {{
                    background: var(--gradient);
                    color: white;
                    padding: 3rem 0;
                    margin-bottom: 3rem;
                }}
                
                .score-circle {{
                    width: 120px;
                    height: 120px;
                    border-radius: 50%;
                    background: conic-gradient(
                        var(--primary-color) 0deg, 
                        var(--secondary-color) {overall_score * 3.6}deg,
                        rgba(255,255,255,0.3) {overall_score * 3.6}deg
                    );
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    margin: 0 auto 1rem;
                }}
                
                .score-inner {{
                    width: 90px;
                    height: 90px;
                    background: white;
                    border-radius: 50%;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    flex-direction: column;
                }}
                
                .score-number {{
                    font-size: 1.8rem;
                    font-weight: 700;
                    color: var(--primary-color);
                    line-height: 1;
                }}
                
                .score-grade {{
                    font-size: 0.8rem;
                    color: #666;
                    text-transform: uppercase;
                    letter-spacing: 1px;
                }}
                
                .section-card {{
                    background: white;
                    border-radius: 15px;
                    padding: 2rem;
                    margin-bottom: 2rem;
                    box-shadow: 0 5px 20px rgba(0,0,0,0.08);
                }}
                
                .section-title {{
                    color: var(--primary-color);
                    font-weight: 600;
                    margin-bottom: 1.5rem;
                    border-bottom: 2px solid var(--primary-color);
                    padding-bottom: 0.5rem;
                }}
                
                .metric-card {{
                    background: #f8f9fa;
                    border-radius: 10px;
                    padding: 1.5rem;
                    text-align: center;
                    margin-bottom: 1rem;
                }}
                
                .metric-score {{
                    font-size: 2rem;
                    font-weight: 700;
                    margin-bottom: 0.5rem;
                }}
                
                .metric-label {{
                    color: #666;
                    font-size: 0.9rem;
                    text-transform: uppercase;
                    letter-spacing: 1px;
                }}
                
                .finding-item {{
                    background: white;
                    border-left: 4px solid;
                    padding: 1rem;
                    margin-bottom: 1rem;
                    border-radius: 0 8px 8px 0;
                }}
                
                .severity-critical {{ border-left-color: #dc3545; }}
                .severity-high {{ border-left-color: #fd7e14; }}
                .severity-medium {{ border-left-color: #ffc107; }}
                .severity-low {{ border-left-color: #20c997; }}
                
                .progress-bar-custom {{
                    height: 25px;
                    border-radius: 12px;
                    background: #e9ecef;
                    overflow: hidden;
                    margin: 0.5rem 0;
                }}
                
                .progress-fill {{
                    height: 100%;
                    background: var(--gradient);
                    transition: width 0.3s ease;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    color: white;
                    font-weight: 600;
                    font-size: 0.9rem;
                }}
                
                .recommendation-item {{
                    background: #e8f5e8;
                    border: 1px solid #d4edda;
                    border-radius: 8px;
                    padding: 1rem;
                    margin-bottom: 1rem;
                }}
                
                .priority-high {{
                    border-left: 4px solid #dc3545;
                }}
                
                .priority-medium {{
                    border-left: 4px solid #ffc107;
                }}
                
                .priority-low {{
                    border-left: 4px solid #28a745;
                }}
                
                @media print {{
                    .no-print {{ display: none; }}
                    body {{ background: white; }}
                    .section-card {{ box-shadow: none; border: 1px solid #ddd; }}
                }}
            </style>
        </head>
        <body>
            <!-- Report Header -->
            <div class="report-header">
                <div class="container">
                    <div class="row align-items-center">
                        <div class="col-md-8">
                            {"<img src='" + logo_path + "' alt='" + business_name + "' style='height: 60px; margin-bottom: 1rem;'>" if logo_path else ""}
                            <h1>Enhanced Security Assessment Report</h1>
                            <p class="lead">Comprehensive cybersecurity analysis for {scan_results.get('target', 'your domain')}</p>
                            <p>Generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}</p>
                        </div>
                        <div class="col-md-4 text-center">
                            <div class="score-circle">
                                <div class="score-inner">
                                    <div class="score-number">{int(overall_score)}</div>
                                    <div class="score-grade">Grade {grade}</div>
                                </div>
                            </div>
                            <h4>Security Score</h4>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="container">
                <!-- Executive Summary -->
                <div class="section-card">
                    <h2 class="section-title"><i class="bi bi-clipboard-data me-2"></i>Executive Summary</h2>
                    <div class="row">
                        <div class="col-md-6">
                            <h5>Overall Assessment</h5>
                            <p>Your security posture has been rated as <strong>{risk_level} Risk</strong> with an overall score of <strong>{int(overall_score)}/100</strong>.</p>
                            <p>This comprehensive assessment evaluated {len([k for k in scan_results.keys() if k.endswith('_security')])} key security domains across your infrastructure.</p>
                        </div>
                        <div class="col-md-6">
                            <h5>Key Metrics</h5>
                            <ul class="list-unstyled">
                                <li><i class="bi bi-check-circle text-success me-2"></i>Scan completed successfully</li>
                                <li><i class="bi bi-clock me-2"></i>Assessment duration: Real-time analysis</li>
                                <li><i class="bi bi-shield-check me-2"></i>Security grade: {grade}</li>
                                <li><i class="bi bi-graph-up me-2"></i>Risk level: {risk_level}</li>
                            </ul>
                        </div>
                    </div>
                </div>
        """
        
        # Security Component Scores
        html += f"""
                <!-- Component Scores -->
                <div class="section-card">
                    <h2 class="section-title"><i class="bi bi-bar-chart me-2"></i>Security Component Analysis</h2>
                    <div class="row">
        """
        
        # Add component score cards
        components = [
            ('network', 'Network Security', 'hdd-network'),
            ('web', 'Web Security', 'globe'),
            ('email', 'Email Security', 'envelope'),
            ('ssl', 'SSL/TLS Security', 'shield-lock')
        ]
        
        for comp_key, comp_name, icon in components:
            score = component_scores.get(comp_key, 75)
            color = get_score_color(score)
            
            html += f"""
                        <div class="col-md-6 col-lg-3 mb-3">
                            <div class="metric-card">
                                <i class="bi bi-{icon}" style="font-size: 2rem; color: {color}; margin-bottom: 1rem;"></i>
                                <div class="metric-score" style="color: {color};">{int(score)}</div>
                                <div class="metric-label">{comp_name}</div>
                                <div class="progress-bar-custom">
                                    <div class="progress-fill" style="width: {score}%; background: {color};">
                                        {int(score)}%
                                    </div>
                                </div>
                            </div>
                        </div>
            """
        
        html += """
                    </div>
                </div>
        """
        
        # Add detailed findings for each security component
        security_components = ['network_security', 'web_security', 'email_security', 'ssl_security']
        
        for component in security_components:
            if component in scan_results:
                html += generate_component_section(component, scan_results[component])
        
        # Recommendations Section
        recommendations = scan_results.get('recommendations', [])
        if recommendations:
            html += f"""
                <!-- Recommendations -->
                <div class="section-card">
                    <h2 class="section-title"><i class="bi bi-lightbulb me-2"></i>Security Recommendations</h2>
                    <p>Based on our analysis, here are prioritized recommendations to improve your security posture:</p>
            """
            
            for i, rec in enumerate(recommendations[:10], 1):  # Show top 10 recommendations
                priority_class = f"priority-{rec.get('priority', 'medium').lower()}"
                html += f"""
                    <div class="recommendation-item {priority_class}">
                        <div class="d-flex justify-content-between align-items-start">
                            <div>
                                <h6><span class="badge bg-primary me-2">{i}</span>{rec.get('title', 'Security Improvement')}</h6>
                                <p class="mb-1">{rec.get('description', 'Implement security best practices')}</p>
                                <small class="text-muted">Category: {rec.get('category', 'General Security')}</small>
                            </div>
                            <span class="badge bg-{get_priority_color(rec.get('priority', 'medium'))}">{rec.get('priority', 'Medium')}</span>
                        </div>
                    </div>
                """
            
            html += """
                </div>
            """
        
        # Technical Details Section
        html += f"""
                <!-- Technical Details -->
                <div class="section-card">
                    <h2 class="section-title"><i class="bi bi-gear me-2"></i>Technical Details</h2>
                    <div class="row">
                        <div class="col-md-6">
                            <h5>Scan Information</h5>
                            <table class="table table-sm">
                                <tr><td><strong>Scan ID:</strong></td><td>{scan_results.get('scan_id', 'N/A')}</td></tr>
                                <tr><td><strong>Target:</strong></td><td>{scan_results.get('target', 'N/A')}</td></tr>
                                <tr><td><strong>Scan Type:</strong></td><td>Enhanced Comprehensive</td></tr>
                                <tr><td><strong>Timestamp:</strong></td><td>{scan_results.get('timestamp', 'N/A')}</td></tr>
                            </table>
                        </div>
                        <div class="col-md-6">
                            <h5>Assessment Coverage</h5>
                            <ul class="list-unstyled">
                                <li><i class="bi bi-check text-success me-2"></i>Network Infrastructure</li>
                                <li><i class="bi bi-check text-success me-2"></i>Web Application Security</li>
                                <li><i class="bi bi-check text-success me-2"></i>Email Security Configuration</li>
                                <li><i class="bi bi-check text-success me-2"></i>SSL/TLS Implementation</li>
                                <li><i class="bi bi-check text-success me-2"></i>System Security Analysis</li>
                            </ul>
                        </div>
                    </div>
                </div>
                
                <!-- Footer -->
                <div class="section-card text-center">
                    <h5>Need Help Implementing These Recommendations?</h5>
                    <p>Contact {business_name} for professional cybersecurity consulting and implementation services.</p>
                    <div class="no-print">
                        <button onclick="window.print()" class="btn btn-primary me-2">
                            <i class="bi bi-printer me-2"></i>Print Report
                        </button>
                        <button onclick="window.close()" class="btn btn-outline-secondary">
                            <i class="bi bi-x-circle me-2"></i>Close
                        </button>
                    </div>
                </div>
            </div>
            
            <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
        </body>
        </html>
        """
        
        return html
        
    except Exception as e:
        logger.error(f"Error generating enhanced HTML report: {e}")
        return generate_error_report(str(e))

def generate_component_section(component_name, component_data):
    """Generate detailed section for each security component"""
    
    # Component display names and icons
    component_info = {
        'network_security': ('Network Security Analysis', 'hdd-network'),
        'web_security': ('Web Security Analysis', 'globe'),
        'email_security': ('Email Security Analysis', 'envelope'),
        'ssl_security': ('SSL/TLS Security Analysis', 'shield-lock'),
        'system_security': ('System Security Analysis', 'cpu')
    }
    
    display_name, icon = component_info.get(component_name, (component_name.replace('_', ' ').title(), 'gear'))
    
    html = f"""
        <div class="section-card">
            <h2 class="section-title"><i class="bi bi-{icon} me-2"></i>{display_name}</h2>
    """
    
    # Add findings if available
    findings = component_data.get('findings', [])
    if findings:
        html += """
            <h5>Key Findings</h5>
        """
        for finding in findings:
            severity = finding.get('severity', 'Medium').lower()
            html += f"""
                <div class="finding-item severity-{severity}">
                    <div class="d-flex justify-content-between align-items-start">
                        <div>
                            <h6>{finding.get('title', 'Security Finding')}</h6>
                            <p class="mb-1">{finding.get('description', 'Security issue detected')}</p>
                            <small class="text-muted">Recommendation: {finding.get('recommendation', 'Review and remediate')}</small>
                        </div>
                        <span class="badge bg-{get_severity_color(severity)}">{finding.get('severity', 'Medium')}</span>
                    </div>
                </div>
            """
    
    # Add component-specific details
    if component_name == 'network_security':
        html += generate_network_details(component_data)
    elif component_name == 'web_security':
        html += generate_web_details(component_data)
    elif component_name == 'email_security':
        html += generate_email_details(component_data)
    elif component_name == 'ssl_security':
        html += generate_ssl_details(component_data)
    
    html += """
        </div>
    """
    
    return html

def generate_network_details(data):
    """Generate network security details"""
    html = "<h5>Network Analysis Details</h5>"
    
    open_ports = data.get('open_ports', [])
    if open_ports:
        html += """
            <h6>Open Ports Detected</h6>
            <div class="table-responsive">
                <table class="table table-sm">
                    <thead>
                        <tr><th>Port</th><th>Service</th><th>Status</th></tr>
                    </thead>
                    <tbody>
        """
        for port in open_ports:
            html += f"""
                        <tr>
                            <td>{port.get('port', 'N/A')}</td>
                            <td>{port.get('service', 'Unknown')}</td>
                            <td><span class="badge bg-warning">{port.get('status', 'Open')}</span></td>
                        </tr>
            """
        html += """
                    </tbody>
                </table>
            </div>
        """
    
    return html

def generate_web_details(data):
    """Generate web security details"""
    html = "<h5>Web Security Analysis</h5>"
    
    security_headers = data.get('security_headers', {})
    if security_headers:
        html += f"""
            <h6>Security Headers Assessment</h6>
            <p>Security Headers Score: <strong>{security_headers.get('security_score', 'N/A')}%</strong></p>
        """
        
        missing_headers = security_headers.get('missing_headers', [])
        if missing_headers:
            html += "<h6>Missing Security Headers</h6><ul>"
            for header in missing_headers:
                html += f"<li><strong>{header.get('header', 'Unknown')}</strong>: {header.get('description', 'Security header not implemented')}</li>"
            html += "</ul>"
    
    return html

def generate_email_details(data):
    """Generate email security details"""
    html = "<h5>Email Security Configuration</h5>"
    
    # SPF Analysis
    spf_analysis = data.get('spf_analysis', {})
    if spf_analysis:
        status_color = 'success' if spf_analysis.get('status') == 'PASS' else 'danger'
        html += f"""
            <h6>SPF Record</h6>
            <p><span class="badge bg-{status_color}">{spf_analysis.get('status', 'Unknown')}</span> 
            {spf_analysis.get('description', 'SPF record analysis')}</p>
        """
    
    # DKIM Analysis  
    dkim_analysis = data.get('dkim_analysis', {})
    if dkim_analysis:
        status_color = 'success' if dkim_analysis.get('status') == 'PASS' else 'danger'
        html += f"""
            <h6>DKIM Configuration</h6>
            <p><span class="badge bg-{status_color}">{dkim_analysis.get('status', 'Unknown')}</span> 
            {dkim_analysis.get('description', 'DKIM configuration analysis')}</p>
        """
    
    # DMARC Analysis
    dmarc_analysis = data.get('dmarc_analysis', {})
    if dmarc_analysis:
        status_color = 'success' if dmarc_analysis.get('status') == 'PASS' else 'danger'
        html += f"""
            <h6>DMARC Policy</h6>
            <p><span class="badge bg-{status_color}">{dmarc_analysis.get('status', 'Unknown')}</span> 
            {dmarc_analysis.get('description', 'DMARC policy analysis')}</p>
        """
    
    return html

def generate_ssl_details(data):
    """Generate SSL/TLS security details"""
    html = "<h5>SSL/TLS Configuration</h5>"
    
    cert_analysis = data.get('certificate_analysis', {})
    if cert_analysis:
        if cert_analysis.get('status') == 'valid':
            days_left = cert_analysis.get('days_until_expiry', 0)
            expiry_color = 'success' if days_left > 30 else 'warning' if days_left > 0 else 'danger'
            
            html += f"""
                <h6>Certificate Information</h6>
                <ul>
                    <li><strong>Status:</strong> <span class="badge bg-success">Valid</span></li>
                    <li><strong>Days until expiry:</strong> <span class="badge bg-{expiry_color}">{days_left} days</span></li>
                    <li><strong>Valid from:</strong> {cert_analysis.get('not_before', 'N/A')}</li>
                    <li><strong>Valid until:</strong> {cert_analysis.get('not_after', 'N/A')}</li>
                </ul>
            """
        else:
            html += f"""
                <h6>Certificate Status</h6>
                <p><span class="badge bg-danger">Invalid or Error</span> {cert_analysis.get('error', 'Certificate validation failed')}</p>
            """
    
    return html

def get_score_color(score):
    """Get color based on score"""
    if score >= 80:
        return '#28a745'
    elif score >= 60:
        return '#ffc107' 
    elif score >= 40:
        return '#fd7e14'
    else:
        return '#dc3545'

def get_severity_color(severity):
    """Get Bootstrap color class for severity"""
    severity_colors = {
        'critical': 'danger',
        'high': 'warning',
        'medium': 'info',
        'low': 'success'
    }
    return severity_colors.get(severity.lower(), 'secondary')

def get_priority_color(priority):
    """Get Bootstrap color class for priority"""
    priority_colors = {
        'critical': 'danger',
        'high': 'warning', 
        'medium': 'info',
        'low': 'success'
    }
    return priority_colors.get(priority.lower(), 'secondary')

def generate_error_report(error_message):
    """Generate error report HTML"""
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Report Generation Error</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    </head>
    <body class="bg-light">
        <div class="container mt-5">
            <div class="alert alert-danger">
                <h4>Report Generation Error</h4>
                <p>An error occurred while generating your security report: {error_message}</p>
                <p>Please try again or contact support.</p>
            </div>
        </div>
    </body>
    </html>
    """