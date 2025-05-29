// Scanner Script
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
