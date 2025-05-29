#!/usr/bin/env python3
"""
Fix script to update the scanner_template.html with proper resource paths
and add scanner styles and javascript
"""

import os

def fix_scanner_template():
    """Update scanner_template.html with proper resource paths"""
    template_path = '/home/ggrun/CybrScan_1/templates/scanner_template.html'
    
    with open(template_path, 'r') as f:
        content = f.read()
    
    # Fix CSS and JS paths to use absolute URLs
    content = content.replace('<link rel="stylesheet" href="styles.css">', 
                             '<link rel="stylesheet" href="{{ url_for(\'static\', filename=\'css/scanner_styles.css\') }}">')
    
    content = content.replace('<script src="scanner.js"></script>', 
                             '<script src="{{ url_for(\'static\', filename=\'js/scanner_script.js\') }}"></script>')
    
    # Add styling for primary color, etc. from client data
    style_block = """
    <style>
        :root {
            --primary-color: {{ scanner.primary_color or '#02054c' }};
            --secondary-color: {{ scanner.secondary_color or '#35a310' }};
            --button-color: {{ scanner.button_color or '#28a745' }};
            --font-family: {{ scanner.font_family or 'Inter, sans-serif' }};
        }
        
        body {
            font-family: var(--font-family);
        }
        
        .primary-btn {
            background-color: var(--button-color);
        }
        
        header {
            background-color: var(--primary-color);
        }
        
        footer {
            background-color: var(--primary-color);
            color: white;
        }
    </style>
    """
    
    # Insert style block after the head section
    if '</head>' in content:
        content = content.replace('</head>', f'{style_block}\n</head>')
    
    # Add current year for footer copyright
    content = content.replace('{{ year }}', "{{ current_year or '2025' }}")
    
    with open(template_path, 'w') as f:
        f.write(content)
    
    print("Updated scanner_template.html with proper resource paths")
    
    # Now create/update the embed route to include current_year
    scanner_routes_path = '/home/ggrun/CybrScan_1/scanner_routes.py'
    
    with open(scanner_routes_path, 'r') as f:
        routes_content = f.read()
    
    # Find the render_template line in the embed route
    render_line = 'return render_template(\n            \'scanner_template.html\',\n            scanner=scanner,\n            client=client,\n            scan_data=scan_data,\n            standalone=True\n        )'
    
    # Update it to include current_year
    updated_render = 'return render_template(\n            \'scanner_template.html\',\n            scanner=scanner,\n            client=client,\n            scan_data=scan_data,\n            standalone=True,\n            current_year=datetime.now().year\n        )'
    
    if render_line in routes_content:
        routes_content = routes_content.replace(render_line, updated_render)
        
        with open(scanner_routes_path, 'w') as f:
            f.write(routes_content)
        
        print("Updated scanner_routes.py to include current_year in template context")
    
    # Create CSS file
    static_css_dir = '/home/ggrun/CybrScan_1/static/css'
    os.makedirs(static_css_dir, exist_ok=True)
    
    css_content = """/* Scanner Styles */
body {
    margin: 0;
    padding: 0;
    font-family: var(--font-family, 'Inter, sans-serif');
    color: #333;
    background-color: #f5f7fa;
}

header {
    background-color: var(--primary-color, #02054c);
    color: white;
    padding: 15px 20px;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.logo-container {
    display: flex;
    align-items: center;
}

.logo {
    max-height: 40px;
    margin-right: 15px;
}

nav ul {
    display: flex;
    list-style-type: none;
    margin: 0;
    padding: 0;
}

nav li {
    margin: 0 15px;
}

nav a {
    color: white;
    text-decoration: none;
    font-weight: 500;
    padding: 5px 0;
    transition: all 0.3s ease;
}

nav a.active {
    border-bottom: 2px solid var(--secondary-color, #35a310);
}

main {
    max-width: 1200px;
    margin: 0 auto;
    padding: 30px 20px;
}

.scanner-container {
    background-color: white;
    border-radius: 8px;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
    padding: 25px;
    margin-bottom: 30px;
}

.scan-form {
    display: flex;
    flex-direction: column;
    gap: 20px;
}

#target-input {
    padding: 12px 15px;
    border: 1px solid #ddd;
    border-radius: 4px;
    font-size: 16px;
    width: 100%;
}

.scan-options {
    background-color: #f9f9f9;
    padding: 20px;
    border-radius: 8px;
}

.options-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 15px;
    margin-top: 15px;
}

.options-grid label {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 14px;
}

.primary-btn {
    background-color: var(--button-color, #28a745);
    color: white;
    border: none;
    border-radius: 4px;
    padding: 12px 20px;
    font-size: 16px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.3s ease;
    align-self: flex-start;
}

.primary-btn:hover {
    opacity: 0.9;
    transform: translateY(-2px);
}

.results-container {
    background-color: white;
    border-radius: 8px;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
    padding: 25px;
}

.results-summary {
    display: flex;
    justify-content: space-between;
    margin-bottom: 30px;
}

.summary-item {
    text-align: center;
    padding: 20px;
    background-color: #f9f9f9;
    border-radius: 8px;
    flex: 1;
    margin: 0 10px;
}

.score {
    font-size: 36px;
    font-weight: 700;
    color: var(--primary-color, #02054c);
}

.issues {
    display: flex;
    flex-direction: column;
    gap: 5px;
    font-size: 16px;
}

.actions {
    display: flex;
    gap: 15px;
    margin-top: 30px;
    justify-content: center;
}

.secondary-btn {
    background-color: white;
    color: var(--primary-color, #02054c);
    border: 1px solid var(--primary-color, #02054c);
    border-radius: 4px;
    padding: 10px 20px;
    font-size: 14px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.3s ease;
}

.secondary-btn:hover {
    background-color: var(--primary-color, #02054c);
    color: white;
}

footer {
    background-color: var(--primary-color, #02054c);
    color: white;
    text-align: center;
    padding: 20px;
    margin-top: 50px;
}

footer p {
    margin: 0;
    font-size: 14px;
}

/* Results details styling */
.results-details {
    margin-top: 30px;
}

.result-section {
    margin-bottom: 25px;
}

.result-section h3 {
    border-bottom: 1px solid #eee;
    padding-bottom: 10px;
    margin-bottom: 15px;
}

.finding {
    background-color: #f9f9f9;
    border-left: 4px solid #ddd;
    padding: 15px;
    margin-bottom: 15px;
    border-radius: 0 4px 4px 0;
}

.finding.critical {
    border-left-color: #dc3545;
}

.finding.warning {
    border-left-color: #ffc107;
}

.finding.info {
    border-left-color: #17a2b8;
}

.finding-header {
    display: flex;
    justify-content: space-between;
    margin-bottom: 10px;
}

.finding-title {
    font-weight: 600;
    font-size: 16px;
}

.finding-severity {
    font-size: 12px;
    padding: 3px 8px;
    border-radius: 12px;
    background-color: #eee;
}

.finding-severity.critical {
    background-color: #dc3545;
    color: white;
}

.finding-severity.warning {
    background-color: #ffc107;
    color: #333;
}

.finding-severity.info {
    background-color: #17a2b8;
    color: white;
}

.finding-description {
    font-size: 14px;
    line-height: 1.5;
}

/* Loading indicator */
.loading {
    display: none;
    text-align: center;
    padding: 30px;
}

.loading-spinner {
    border: 5px solid #f3f3f3;
    border-top: 5px solid var(--primary-color, #02054c);
    border-radius: 50%;
    width: 50px;
    height: 50px;
    animation: spin 2s linear infinite;
    margin: 0 auto 20px;
}

@keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
}

@media (max-width: 768px) {
    header {
        flex-direction: column;
        text-align: center;
    }
    
    nav ul {
        margin-top: 15px;
    }
    
    .results-summary {
        flex-direction: column;
        gap: 15px;
    }
    
    .summary-item {
        margin: 0;
    }
    
    .actions {
        flex-direction: column;
    }
}
"""
    
    with open(os.path.join(static_css_dir, 'scanner_styles.css'), 'w') as f:
        f.write(css_content)
    
    print("Created scanner_styles.css")
    
    # Create JS file
    static_js_dir = '/home/ggrun/CybrScan_1/static/js'
    os.makedirs(static_js_dir, exist_ok=True)
    
    js_content = """// Scanner Script
document.addEventListener('DOMContentLoaded', function() {
    // Elements
    const targetInput = document.getElementById('target-input');
    const startScanBtn = document.getElementById('start-scan-btn');
    const scannerContainer = document.querySelector('.scanner-container');
    const resultsContainer = document.querySelector('.results-container');
    const resultsDetails = document.getElementById('results-details');
    const securityScore = document.getElementById('security-score');
    const criticalIssues = document.getElementById('critical-issues');
    const warningIssues = document.getElementById('warning-issues');
    const infoIssues = document.getElementById('info-issues');
    const downloadReportBtn = document.getElementById('download-report-btn');
    const emailReportBtn = document.getElementById('email-report-btn');

    // Start scan
    startScanBtn.addEventListener('click', function() {
        const target = targetInput.value.trim();
        if (!target) {
            alert('Please enter a target URL or domain');
            return;
        }

        // Get selected scan types
        const scanTypes = [];
        document.querySelectorAll('input[name="scan_type"]:checked').forEach(checkbox => {
            scanTypes.push(checkbox.value);
        });

        if (scanTypes.length === 0) {
            alert('Please select at least one scan type');
            return;
        }

        // Show loading state
        startScanBtn.disabled = true;
        startScanBtn.textContent = 'Scanning...';

        // In a real implementation, you would send this data to your backend
        // For now, we'll simulate a scan with mock data
        setTimeout(function() {
            // Simulate scan completion
            const mockScanResults = generateMockScanResults(target, scanTypes);
            displayScanResults(mockScanResults);
            
            // Reset button
            startScanBtn.disabled = false;
            startScanBtn.textContent = 'Start Scan';
        }, 2000);
    });

    // Generate mock scan results for demo purposes
    function generateMockScanResults(target, scanTypes) {
        const results = {
            target: target,
            scan_types: scanTypes,
            timestamp: new Date().toISOString(),
            security_score: Math.floor(Math.random() * 40) + 60, // Random score between 60-99
            findings: []
        };

        // Add SSL/TLS findings
        if (scanTypes.includes('ssl')) {
            results.findings.push({
                category: 'SSL/TLS',
                title: 'TLS 1.2 Supported',
                description: 'The server supports TLS 1.2, which is considered secure.',
                severity: 'info'
            });
            
            if (Math.random() > 0.5) {
                results.findings.push({
                    category: 'SSL/TLS',
                    title: 'TLS 1.0 Supported',
                    description: 'The server supports TLS 1.0, which is deprecated and considered insecure.',
                    severity: 'warning'
                });
            }
        }

        // Add HTTP Header findings
        if (scanTypes.includes('headers')) {
            results.findings.push({
                category: 'HTTP Headers',
                title: 'Missing Content Security Policy',
                description: 'The website does not implement a Content Security Policy header, which helps prevent XSS attacks.',
                severity: 'warning'
            });
            
            if (Math.random() > 0.7) {
                results.findings.push({
                    category: 'HTTP Headers',
                    title: 'Missing X-Frame-Options Header',
                    description: 'The X-Frame-Options header is not set, which can lead to clickjacking vulnerabilities.',
                    severity: 'warning'
                });
            }
        }

        // Add Vulnerability findings
        if (scanTypes.includes('vulnerabilities')) {
            if (Math.random() > 0.8) {
                results.findings.push({
                    category: 'Vulnerabilities',
                    title: 'Cross-Site Scripting (XSS) Vulnerability',
                    description: 'Potential XSS vulnerability detected in form submission.',
                    severity: 'critical'
                });
            }
            
            results.findings.push({
                category: 'Vulnerabilities',
                title: 'Outdated jQuery Version',
                description: 'The website is using an outdated version of jQuery which may contain known vulnerabilities.',
                severity: 'warning'
            });
        }

        // Add Port Scan findings
        if (scanTypes.includes('ports')) {
            results.findings.push({
                category: 'Port Scan',
                title: 'Open Port: 80 (HTTP)',
                description: 'Port 80 is open and serving HTTP content.',
                severity: 'info'
            });
            
            results.findings.push({
                category: 'Port Scan',
                title: 'Open Port: 443 (HTTPS)',
                description: 'Port 443 is open and serving HTTPS content.',
                severity: 'info'
            });
            
            if (Math.random() > 0.7) {
                results.findings.push({
                    category: 'Port Scan',
                    title: 'Open Port: 22 (SSH)',
                    description: 'Port 22 (SSH) is open to the public internet. Consider restricting access if not needed.',
                    severity: 'warning'
                });
            }
        }

        // Add Malware findings
        if (scanTypes.includes('malware')) {
            if (Math.random() > 0.9) {
                results.findings.push({
                    category: 'Malware',
                    title: 'Suspicious JavaScript',
                    description: 'Suspicious JavaScript code detected that may be used for malicious purposes.',
                    severity: 'critical'
                });
            } else {
                results.findings.push({
                    category: 'Malware',
                    title: 'No Malware Detected',
                    description: 'No malware or suspicious code detected on the scanned pages.',
                    severity: 'info'
                });
            }
        }

        // Add DNS findings
        if (scanTypes.includes('dns')) {
            results.findings.push({
                category: 'DNS',
                title: 'Missing DMARC Record',
                description: 'No DMARC record found. DMARC helps prevent email spoofing and phishing.',
                severity: 'warning'
            });
            
            results.findings.push({
                category: 'DNS',
                title: 'SPF Record Found',
                description: 'SPF record is properly configured to help prevent email spoofing.',
                severity: 'info'
            });
        }

        return results;
    }

    // Display scan results
    function displayScanResults(results) {
        // Show results container
        scannerContainer.style.display = 'block';
        resultsContainer.style.display = 'block';

        // Update summary
        securityScore.textContent = results.security_score;
        
        // Count issues by severity
        let critical = 0, warning = 0, info = 0;
        results.findings.forEach(finding => {
            if (finding.severity === 'critical') critical++;
            else if (finding.severity === 'warning') warning++;
            else if (finding.severity === 'info') info++;
        });
        
        criticalIssues.textContent = critical;
        warningIssues.textContent = warning;
        infoIssues.textContent = info;

        // Group findings by category
        const categories = {};
        results.findings.forEach(finding => {
            if (!categories[finding.category]) {
                categories[finding.category] = [];
            }
            categories[finding.category].push(finding);
        });

        // Clear previous results
        resultsDetails.innerHTML = '';

        // Add findings by category
        for (const category in categories) {
            const sectionEl = document.createElement('div');
            sectionEl.className = 'result-section';
            
            const headingEl = document.createElement('h3');
            headingEl.textContent = category;
            sectionEl.appendChild(headingEl);
            
            categories[category].forEach(finding => {
                const findingEl = document.createElement('div');
                findingEl.className = `finding ${finding.severity}`;
                
                const headerEl = document.createElement('div');
                headerEl.className = 'finding-header';
                
                const titleEl = document.createElement('div');
                titleEl.className = 'finding-title';
                titleEl.textContent = finding.title;
                
                const severityEl = document.createElement('div');
                severityEl.className = `finding-severity ${finding.severity}`;
                severityEl.textContent = finding.severity.charAt(0).toUpperCase() + finding.severity.slice(1);
                
                headerEl.appendChild(titleEl);
                headerEl.appendChild(severityEl);
                
                const descEl = document.createElement('div');
                descEl.className = 'finding-description';
                descEl.textContent = finding.description;
                
                findingEl.appendChild(headerEl);
                findingEl.appendChild(descEl);
                sectionEl.appendChild(findingEl);
            });
            
            resultsDetails.appendChild(sectionEl);
        }

        // Scroll to results
        resultsContainer.scrollIntoView({ behavior: 'smooth' });
    }

    // Download report
    downloadReportBtn.addEventListener('click', function() {
        alert('Download functionality would be implemented here.');
    });

    // Email report
    emailReportBtn.addEventListener('click', function() {
        alert('Email functionality would be implemented here.');
    });
});
"""
    
    with open(os.path.join(static_js_dir, 'scanner_script.js'), 'w') as f:
        f.write(js_content)
    
    print("Created scanner_script.js")
    
    return True

if __name__ == "__main__":
    print("Fixing scanner embed resources...")
    fix_scanner_template()
    print("Done!")