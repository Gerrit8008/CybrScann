#!/usr/bin/env python3
"""
Scanner deployment system that generates HTML, CSS, JS and API endpoints
for clients to integrate scanners into their websites
"""

import os
import logging
from jinja2 import Template

logger = logging.getLogger(__name__)

def generate_scanner_deployment(scanner_uid, scanner_data, api_key):
    """Generate all deployment files for a scanner"""
    try:
        # Create deployment directory
        deployment_dir = os.path.join('static', 'deployments', scanner_uid)
        os.makedirs(deployment_dir, exist_ok=True)
        
        # Generate HTML embed code
        html_result = generate_scanner_html(deployment_dir, scanner_uid, scanner_data, api_key)
        
        # Generate CSS styles
        css_result = generate_scanner_css(deployment_dir, scanner_data)
        
        # Generate JavaScript
        js_result = generate_scanner_js(deployment_dir, scanner_uid, api_key)
        
        # Generate API documentation
        api_result = generate_api_docs(deployment_dir, scanner_uid, api_key, scanner_data)
        
        if all([html_result, css_result, js_result, api_result]):
            return {
                'status': 'success',
                'deployment_path': deployment_dir,
                'embed_url': f'/scanner/{scanner_uid}/embed',
                'api_url': f'/api/scanner/{scanner_uid}',
                'docs_url': f'/scanner/{scanner_uid}/docs'
            }
        else:
            return {
                'status': 'error',
                'message': 'Failed to generate some deployment files'
            }
            
    except Exception as e:
        logger.error(f"Error generating scanner deployment: {e}")
        return {
            'status': 'error',
            'message': str(e)
        }

def generate_scanner_html(deployment_dir, scanner_uid, scanner_data, api_key):
    """Generate HTML embed code for the scanner"""
    try:
        html_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ scanner_name }} - Security Scanner</title>
    {% if favicon_url %}
    <!-- Custom Favicon -->
    <link rel="icon" type="image/png" sizes="32x32" href="{{ favicon_url }}">
    <link rel="icon" type="image/png" sizes="16x16" href="{{ favicon_url }}">
    <link rel="shortcut icon" href="{{ favicon_url }}">
    {% else %}
    <!-- Default Favicon -->
    <link rel="icon" type="image/png" sizes="32x32" href="/static/images/favicon.png">
    <link rel="icon" type="image/png" sizes="16x16" href="/static/images/favicon.png">
    <link rel="shortcut icon" href="/static/images/favicon.png">
    {% endif %}
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="./scanner-styles.css">
    <style>
        :root {
            --primary-color: {{ primary_color }};
            --secondary-color: {{ secondary_color }};
            --button-color: {{ button_color }};
        }
    </style>
</head>
<body>
    <div class="scanner-container">
        <div class="scanner-header">
            {% if logo_url %}
            <img src="{{ logo_url }}" alt="{{ business_name }} Logo" class="scanner-logo">
            {% endif %}
            <h2 class="scanner-title">{{ scanner_name }}</h2>
            <p class="scanner-description">Free security scan for {{ business_name }}</p>
        </div>
        
        <div class="scanner-form-container">
            <form id="scannerForm" class="scanner-form">
                <div class="form-group mb-3">
                    <label for="target_url" class="form-label">Website URL to Scan</label>
                    <input type="url" 
                           id="target_url" 
                           name="target_url" 
                           class="form-control scanner-input" 
                           placeholder="https://example.com" 
                           required>
                    <div class="form-text">Enter your website URL for a comprehensive security analysis</div>
                </div>
                
                <div class="form-group mb-3">
                    <label for="contact_email" class="form-label">Email Address</label>
                    <input type="email" 
                           id="contact_email" 
                           name="contact_email" 
                           class="form-control scanner-input" 
                           placeholder="your@email.com" 
                           required>
                    <div class="form-text">We'll send your security report to this email</div>
                </div>
                
                <div class="form-group mb-3">
                    <label for="contact_name" class="form-label">Name (Optional)</label>
                    <input type="text" 
                           id="contact_name" 
                           name="contact_name" 
                           class="form-control scanner-input" 
                           placeholder="Your Name">
                </div>
                
                <div class="scan-types mb-3">
                    <label class="form-label">Scan Types</label>
                    {% for scan_type in scan_types %}
                    <div class="form-check">
                        <input class="form-check-input" type="checkbox" name="scan_types[]" value="{{ scan_type }}" id="{{ scan_type }}" checked>
                        <label class="form-check-label" for="{{ scan_type }}">
                            {{ scan_type.replace('_', ' ').title() }}
                        </label>
                    </div>
                    {% endfor %}
                </div>
                
                <button type="submit" class="btn scanner-submit-btn w-100">
                    <span class="btn-text">Start Free Security Scan</span>
                    <span class="btn-spinner d-none">
                        <span class="spinner-border spinner-border-sm me-2"></span>
                        Scanning...
                    </span>
                </button>
            </form>
            
            <div id="scanResults" class="scan-results d-none">
                <div class="alert alert-info">
                    <h5>Scan Initiated!</h5>
                    <p>Your security scan has been started. Results will be emailed to you shortly.</p>
                    <div class="scan-id">Scan ID: <span id="scanIdDisplay"></span></div>
                </div>
            </div>
            
            <div id="scanError" class="scan-error d-none">
                <div class="alert alert-danger">
                    <h5>Scan Failed</h5>
                    <p id="errorMessage">An error occurred during the scan. Please try again.</p>
                </div>
            </div>
        </div>
        
        <div class="scanner-footer">
            <p class="text-muted small">
                Powered by {{ business_name }} | 
                <a href="mailto:{{ contact_email }}" class="text-decoration-none">Contact Support</a>
            </p>
        </div>
    </div>
    
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    <script src="./scanner-script.js"></script>
    <script>
        // Initialize scanner with configuration
        window.ScannerConfig = {
            apiKey: '{{ api_key }}',
            scannerUid: '{{ scanner_uid }}',
            apiBaseUrl: window.location.origin + '/api/scanner/{{ scanner_uid }}'
        };
    </script>
</body>
</html>
        """
        
        template = Template(html_template)
        html_content = template.render(
            scanner_uid=scanner_uid,
            scanner_name=scanner_data.get('name', 'Security Scanner'),
            business_name=scanner_data.get('business_name', 'Security Services'),
            primary_color=scanner_data.get('primary_color', '#02054c'),
            secondary_color=scanner_data.get('secondary_color', '#35a310'),
            button_color=scanner_data.get('button_color', scanner_data.get('primary_color', '#02054c')),
            logo_url=scanner_data.get('logo_url', ''),
            favicon_url=scanner_data.get('favicon_path', scanner_data.get('favicon_url', '')),
            contact_email=scanner_data.get('contact_email', 'support@example.com'),
            scan_types=scanner_data.get('scan_types', ['port_scan', 'ssl_check']),
            api_key=api_key
        )
        
        # Save HTML file
        html_path = os.path.join(deployment_dir, 'index.html')
        with open(html_path, 'w') as f:
            f.write(html_content)
        
        # Generate embed snippet
        embed_snippet = f"""
<!-- Embed this code in your website -->
<iframe src="{os.environ.get('BASE_URL', '')}/scanner/{scanner_uid}/embed" 
        width="100%" 
        height="600" 
        frameborder="0"
        style="border: 1px solid #ddd; border-radius: 8px;">
</iframe>
        """
        
        embed_path = os.path.join(deployment_dir, 'embed-snippet.html')
        with open(embed_path, 'w') as f:
            f.write(embed_snippet)
        
        logger.info(f"Generated HTML files for scanner {scanner_uid}")
        return True
        
    except Exception as e:
        logger.error(f"Error generating scanner HTML: {e}")
        return False

def generate_scanner_css(deployment_dir, scanner_data):
    """Generate CSS styles for the scanner"""
    try:
        css_content = f"""
/* Scanner Styles */
.scanner-container {{
    max-width: 600px;
    margin: 0 auto;
    padding: 2rem;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    background: white;
    border-radius: 12px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.1);
}}

.scanner-header {{
    text-align: center;
    margin-bottom: 2rem;
    padding-bottom: 1.5rem;
    border-bottom: 2px solid {scanner_data.get('primary_color', '#02054c')};
}}

.scanner-logo {{
    max-height: 60px;
    margin-bottom: 1rem;
}}

.scanner-title {{
    color: {scanner_data.get('primary_color', '#02054c')};
    font-size: 2rem;
    font-weight: 700;
    margin-bottom: 0.5rem;
}}

.scanner-description {{
    color: {scanner_data.get('secondary_color', '#35a310')};
    font-size: 1.1rem;
    margin: 0;
}}

.scanner-form-container {{
    margin-bottom: 2rem;
}}

.scanner-input {{
    border: 2px solid #e9ecef;
    border-radius: 8px;
    padding: 0.75rem 1rem;
    font-size: 1rem;
    transition: all 0.3s ease;
}}

.scanner-input:focus {{
    border-color: {scanner_data.get('primary_color', '#02054c')};
    box-shadow: 0 0 0 0.2rem {scanner_data.get('primary_color', '#02054c')}33;
}}

.scanner-submit-btn {{
    background: linear-gradient(135deg, {scanner_data.get('button_color', scanner_data.get('primary_color', '#02054c'))}, {scanner_data.get('secondary_color', '#35a310')});
    border: none;
    border-radius: 8px;
    padding: 1rem 2rem;
    font-size: 1.1rem;
    font-weight: 600;
    color: white;
    transition: all 0.3s ease;
    position: relative;
    overflow: hidden;
}}

.scanner-submit-btn:hover {{
    background: linear-gradient(135deg, {scanner_data.get('button_color', scanner_data.get('primary_color', '#02054c'))}dd, {scanner_data.get('secondary_color', '#35a310')}dd);
    transform: translateY(-2px);
    box-shadow: 0 8px 25px rgba(0,0,0,0.15);
}}

.scanner-submit-btn:active {{
    transform: translateY(0);
}}

.scanner-submit-btn:disabled {{
    opacity: 0.7;
    cursor: not-allowed;
    transform: none;
}}

.scan-results {{
    margin-top: 1.5rem;
    padding: 1.5rem;
    background: #f8f9fa;
    border-radius: 8px;
    border-left: 4px solid {scanner_data.get('primary_color', '#02054c')};
}}

.scan-error {{
    margin-top: 1.5rem;
}}

.scan-id {{
    font-family: 'Courier New', monospace;
    font-weight: 600;
    margin-top: 1rem;
    padding: 0.5rem;
    background: white;
    border-radius: 4px;
    border: 1px solid #dee2e6;
}}

.scanner-footer {{
    text-align: center;
    padding-top: 1.5rem;
    border-top: 1px solid #e9ecef;
}}

.form-check-input:checked {{
    background-color: {scanner_data.get('primary_color', '#02054c')};
    border-color: {scanner_data.get('primary_color', '#02054c')};
}}

.form-check-input:focus {{
    border-color: {scanner_data.get('primary_color', '#02054c')};
    box-shadow: 0 0 0 0.25rem {scanner_data.get('primary_color', '#02054c')}33;
}}

/* Responsive design */
@media (max-width: 768px) {{
    .scanner-container {{
        margin: 1rem;
        padding: 1.5rem;
    }}
    
    .scanner-title {{
        font-size: 1.5rem;
    }}
}}

/* Loading animation */
@keyframes pulse {{
    0% {{ opacity: 1; }}
    50% {{ opacity: 0.5; }}
    100% {{ opacity: 1; }}
}}

.loading {{
    animation: pulse 1.5s ease-in-out infinite;
}}
        """
        
        css_path = os.path.join(deployment_dir, 'scanner-styles.css')
        with open(css_path, 'w') as f:
            f.write(css_content)
        
        logger.info(f"Generated CSS for scanner")
        return True
        
    except Exception as e:
        logger.error(f"Error generating scanner CSS: {e}")
        return False

def generate_scanner_js(deployment_dir, scanner_uid, api_key):
    """Generate JavaScript for the scanner"""
    try:
        js_content = f"""
// Scanner JavaScript
class SecurityScanner {{
    constructor(config) {{
        this.config = config;
        this.form = document.getElementById('scannerForm');
        this.submitBtn = this.form.querySelector('.scanner-submit-btn');
        this.btnText = this.submitBtn.querySelector('.btn-text');
        this.btnSpinner = this.submitBtn.querySelector('.btn-spinner');
        this.resultsDiv = document.getElementById('scanResults');
        this.errorDiv = document.getElementById('scanError');
        
        this.init();
    }}
    
    init() {{
        this.form.addEventListener('submit', (e) => this.handleSubmit(e));
        this.setupValidation();
    }}
    
    setupValidation() {{
        const urlInput = document.getElementById('target_url');
        const emailInput = document.getElementById('contact_email');
        
        urlInput.addEventListener('input', () => {{
            this.validateUrl(urlInput);
        }});
        
        emailInput.addEventListener('input', () => {{
            this.validateEmail(emailInput);
        }});
    }}
    
    validateUrl(input) {{
        const url = input.value;
        if (!url) return true;
        
        try {{
            new URL(url);
            input.classList.remove('is-invalid');
            input.classList.add('is-valid');
            return true;
        }} catch {{
            input.classList.remove('is-valid');
            input.classList.add('is-invalid');
            return false;
        }}
    }}
    
    validateEmail(input) {{
        const email = input.value;
        if (!email) return true;
        
        const emailRegex = /^[^\\s@]+@[^\\s@]+\\.[^\\s@]+$/;
        if (emailRegex.test(email)) {{
            input.classList.remove('is-invalid');
            input.classList.add('is-valid');
            return true;
        }} else {{
            input.classList.remove('is-valid');
            input.classList.add('is-invalid');
            return false;
        }}
    }}
    
    async handleSubmit(e) {{
        e.preventDefault();
        
        if (!this.validateForm()) {{
            return;
        }}
        
        this.setLoading(true);
        this.hideMessages();
        
        try {{
            const formData = new FormData(this.form);
            const scanData = {{
                target_url: formData.get('target_url'),
                contact_email: formData.get('contact_email'),
                contact_name: formData.get('contact_name') || '',
                scan_types: formData.getAll('scan_types[]'),
                scanner_uid: this.config.scannerUid
            }};
            
            const response = await fetch(this.config.apiBaseUrl + '/scan', {{
                method: 'POST',
                headers: {{
                    'Content-Type': 'application/json',
                    'Authorization': 'Bearer ' + this.config.apiKey
                }},
                body: JSON.stringify(scanData)
            }});
            
            const result = await response.json();
            
            if (result.status === 'success') {{
                this.showSuccess(result.scan_id);
            }} else {{
                this.showError(result.message || 'Scan failed. Please try again.');
            }}
            
        }} catch (error) {{
            console.error('Scan error:', error);
            this.showError('Network error. Please check your connection and try again.');
        }} finally {{
            this.setLoading(false);
        }}
    }}
    
    validateForm() {{
        const urlInput = document.getElementById('target_url');
        const emailInput = document.getElementById('contact_email');
        
        let isValid = true;
        
        if (!this.validateUrl(urlInput)) {{
            isValid = false;
        }}
        
        if (!this.validateEmail(emailInput)) {{
            isValid = false;
        }}
        
        if (!urlInput.value.trim()) {{
            urlInput.classList.add('is-invalid');
            isValid = false;
        }}
        
        if (!emailInput.value.trim()) {{
            emailInput.classList.add('is-invalid');
            isValid = false;
        }}
        
        return isValid;
    }}
    
    setLoading(loading) {{
        this.submitBtn.disabled = loading;
        
        if (loading) {{
            this.btnText.classList.add('d-none');
            this.btnSpinner.classList.remove('d-none');
        }} else {{
            this.btnText.classList.remove('d-none');
            this.btnSpinner.classList.add('d-none');
        }}
    }}
    
    hideMessages() {{
        this.resultsDiv.classList.add('d-none');
        this.errorDiv.classList.add('d-none');
    }}
    
    showSuccess(scanId) {{
        document.getElementById('scanIdDisplay').textContent = scanId;
        this.resultsDiv.classList.remove('d-none');
        this.form.reset();
        
        // Clear validation classes
        this.form.querySelectorAll('.is-valid, .is-invalid').forEach(el => {{
            el.classList.remove('is-valid', 'is-invalid');
        }});
    }}
    
    showError(message) {{
        document.getElementById('errorMessage').textContent = message;
        this.errorDiv.classList.remove('d-none');
    }}
}}

// Initialize scanner when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {{
    if (window.ScannerConfig) {{
        new SecurityScanner(window.ScannerConfig);
    }}
}});

// Export for module use
if (typeof module !== 'undefined' && module.exports) {{
    module.exports = SecurityScanner;
}}
        """
        
        js_path = os.path.join(deployment_dir, 'scanner-script.js')
        with open(js_path, 'w') as f:
            f.write(js_content)
        
        logger.info(f"Generated JavaScript for scanner")
        return True
        
    except Exception as e:
        logger.error(f"Error generating scanner JavaScript: {e}")
        return False

def generate_api_docs(deployment_dir, scanner_uid, api_key, scanner_data=None):
    """Generate API documentation for the scanner"""
    try:
        contact_email = scanner_data.get('contact_email', 'support@example.com') if scanner_data else 'support@example.com'
        
        api_docs = f"""
# Scanner API Documentation

## Scanner: {scanner_uid}

### Base URL
```
{os.environ.get('BASE_URL', 'https://your-domain.com')}/api/scanner/{scanner_uid}
```

### Authentication
All API requests require the API key in the Authorization header:
```
Authorization: Bearer {api_key}
```

### Start a Scan

**POST** `/scan`

Start a new security scan.

#### Request Body
```json
{{
    "target_url": "https://example.com",
    "contact_email": "user@example.com",
    "contact_name": "John Doe",
    "scan_types": ["port_scan", "ssl_check", "vulnerability_scan"]
}}
```

#### Response
```json
{{
    "status": "success",
    "scan_id": "scan_abc123def456",
    "message": "Scan started successfully",
    "estimated_completion": "2024-01-01T12:00:00Z"
}}
```

### Get Scan Status

**GET** `/scan/{{scan_id}}`

Get the status and results of a scan.

#### Response
```json
{{
    "status": "success",
    "scan_id": "scan_abc123def456",
    "scan_status": "completed",
    "progress": 100,
    "results": {{
        "security_score": 85,
        "findings": [...],
        "recommendations": [...]
    }},
    "created_at": "2024-01-01T12:00:00Z",
    "completed_at": "2024-01-01T12:05:00Z"
}}
```

### Integration Examples

#### HTML Embed
```html
<iframe src="{os.environ.get('BASE_URL', '')}/scanner/{scanner_uid}/embed" 
        width="100%" 
        height="600" 
        frameborder="0">
</iframe>
```

#### JavaScript Integration
```javascript
// Include the scanner script
<script src="{os.environ.get('BASE_URL', '')}/scanner/{scanner_uid}/scanner-script.js"></script>

// Initialize
const scanner = new SecurityScanner({{
    apiKey: '{api_key}',
    scannerUid: '{scanner_uid}',
    apiBaseUrl: '{os.environ.get('BASE_URL', '')}/api/scanner/{scanner_uid}'
}});
```

#### Direct API Call
```javascript
fetch('{os.environ.get('BASE_URL', '')}/api/scanner/{scanner_uid}/scan', {{
    method: 'POST',
    headers: {{
        'Content-Type': 'application/json',
        'Authorization': 'Bearer {api_key}'
    }},
    body: JSON.stringify({{
        target_url: 'https://example.com',
        contact_email: 'user@example.com',
        scan_types: ['port_scan', 'ssl_check']
    }})
}})
.then(response => response.json())
.then(data => console.log(data));
```

### Error Codes

- `400` - Bad Request (invalid parameters)
- `401` - Unauthorized (invalid API key)
- `404` - Scanner not found
- `429` - Rate limit exceeded
- `500` - Internal server error

### Rate Limits

- 10 scans per hour per IP address
- 100 API calls per hour per API key

### Support

For technical support, contact: {contact_email}
        """
        
        docs_path = os.path.join(deployment_dir, 'api-docs.md')
        with open(docs_path, 'w') as f:
            f.write(api_docs)
        
        logger.info(f"Generated API documentation for scanner")
        return True
        
    except Exception as e:
        logger.error(f"Error generating API docs: {e}")
        return False

if __name__ == "__main__":
    # Test deployment generation
    test_scanner_data = {
        'name': 'Test Security Scanner',
        'business_name': 'Test Business',
        'primary_color': '#007bff',
        'secondary_color': '#6c757d',
        'contact_email': 'support@test.com',
        'scan_types': ['port_scan', 'ssl_check']
    }
    
    result = generate_scanner_deployment('test_scanner_123', test_scanner_data, 'test_api_key_456')
    print(f"Deployment result: {result}")

def regenerate_scanner_if_needed(scanner_id, client_id):
    """Regenerate scanner deployment if customizations have changed recently"""
    try:
        from client_db import get_db_connection
        import sqlite3
        from datetime import datetime, timedelta
        
        conn = get_db_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Get scanner info
        cursor.execute('SELECT scanner_id FROM scanners WHERE id = ?', (scanner_id,))
        scanner = cursor.fetchone()
        
        if not scanner:
            return False
            
        scanner_uid = scanner['scanner_id']
        
        # Check if customizations were updated recently (within last hour)
        cursor.execute('SELECT updated_at FROM customizations WHERE client_id = ?', (client_id,))
        custom = cursor.fetchone()
        
        if custom and custom['updated_at']:
            # Parse the updated_at timestamp
            try:
                updated_time = datetime.fromisoformat(custom['updated_at'])
                one_hour_ago = datetime.now() - timedelta(hours=1)
                
                # If customizations were updated recently, regenerate
                if updated_time > one_hour_ago:
                    logger.info(f"Customizations updated recently, regenerating scanner {scanner_uid}")
                    
                    # Get full scanner data for regeneration
                    cursor.execute('''
                        SELECT s.*, c.primary_color, c.secondary_color, c.button_color, 
                               c.logo_path, c.favicon_path, cl.business_name
                        FROM scanners s
                        JOIN clients cl ON s.client_id = cl.id
                        LEFT JOIN customizations c ON cl.id = c.client_id
                        WHERE s.id = ?
                    ''', (scanner_id,))
                    
                    full_scanner = cursor.fetchone()
                    if full_scanner:
                        fs = dict(full_scanner)
                        scanner_data = {
                            'name': fs['name'],
                            'business_name': fs['business_name'],
                            'primary_color': fs['primary_color'] or '#02054c',
                            'secondary_color': fs['secondary_color'] or '#35a310',
                            'button_color': fs['button_color'] or fs['primary_color'] or '#02054c',
                            'logo_url': fs['logo_path'] or '',
                            'favicon_url': fs['favicon_path'] or '',
                        }
                        
                        # Regenerate deployment
                        success = generate_scanner_deployment(scanner_uid, scanner_data, fs['api_key'])
                        conn.close()
                        return success
            except Exception as parse_error:
                logger.warning(f"Could not parse customization timestamp: {parse_error}")
        
        conn.close()
        return False
        
    except Exception as e:
        logger.warning(f"Error checking if scanner regeneration needed: {e}")
        return False