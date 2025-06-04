document.addEventListener('DOMContentLoaded', function() {
    // Elements
    const targetInput = document.getElementById('target-input');
    const startScanBtn = document.getElementById('start-scan-btn');
    const resultsContainer = document.querySelector('.results-container');
    const resultsDetails = document.getElementById('results-details');
    const securityScore = document.getElementById('security-score');
    const criticalIssues = document.getElementById('critical-issues');
    const warningIssues = document.getElementById('warning-issues');
    const infoIssues = document.getElementById('info-issues');
    const downloadReportBtn = document.getElementById('download-report-btn');
    const emailReportBtn = document.getElementById('email-report-btn');
    
    // Configuration
    const clientId = 2;
    const defaultDomain = "https://test.com";
    const apiEndpoint = '/api/v1/scan';
    
    // Set default domain if available
    if (defaultDomain) {
        targetInput.value = defaultDomain;
    }
    
    // Set default scan options
    const defaultScans = [];
    if (defaultScans && defaultScans.length > 0) {
        const checkboxes = document.querySelectorAll('input[name="scan_type"]');
        checkboxes.forEach(checkbox => {
            checkbox.checked = defaultScans.includes(checkbox.value);
        });
    }
    
    // Start scan button click handler
    startScanBtn.addEventListener('click', function() {
        const target = targetInput.value.trim();
        
        if (!target) {
            alert('Please enter a target URL or domain');
            return;
        }
        
        // Get selected scan types
        const selectedScans = [];
        document.querySelectorAll('input[name="scan_type"]:checked').forEach(checkbox => {
            selectedScans.push(checkbox.value);
        });
        
        if (selectedScans.length === 0) {
            alert('Please select at least one scan type');
            return;
        }
        
        // Disable start button and show loading
        startScanBtn.disabled = true;
        startScanBtn.textContent = 'Scanning...';
        
        // Prepare scan request
        const scanRequest = {
            target: target,
            scan_types: selectedScans,
            client_id: clientId
        };
        
        // Simulate API call and show results
        simulateScan(scanRequest)
            .then(results => {
                displayResults(results);
                startScanBtn.disabled = false;
                startScanBtn.textContent = 'Start Scan';
            })
            .catch(error => {
                alert('An error occurred during the scan: ' + error.message);
                startScanBtn.disabled = false;
                startScanBtn.textContent = 'Start Scan';
            });
    });
    
    // Download report button click handler
    downloadReportBtn.addEventListener('click', function() {
        alert('Report download functionality will be implemented here');
    });
    
    // Email report button click handler
    emailReportBtn.addEventListener('click', function() {
        alert('Email report functionality will be implemented here');
    });
    
    // Function to simulate a scan (will be replaced with actual API call)
    function simulateScan(scanRequest) {
        return new Promise((resolve, reject) => {
            // Simulate network delay
            setTimeout(() => {
                // Mock results
                const results = {
                    target: scanRequest.target,
                    scan_id: 'scan-' + Date.now(),
                    timestamp: new Date().toISOString(),
                    score: Math.floor(Math.random() * 100),
                    issues: {
                        critical: Math.floor(Math.random() * 5),
                        warnings: Math.floor(Math.random() * 10),
                        info: Math.floor(Math.random() * 15)
                    },
                    findings: []
                };
                
                // Generate mock findings based on selected scan types
                scanRequest.scan_types.forEach(scanType => {
                    switch(scanType) {
                        case 'ssl':
                            results.findings.push({
                                type: 'ssl',
                                title: 'SSL/TLS Configuration',
                                severity: getRandomSeverity(),
                                details: 'The server supports TLS 1.2 and 1.3 but also has older protocols enabled.'
                            });
                            break;
                        case 'headers':
                            results.findings.push({
                                type: 'headers',
                                title: 'HTTP Security Headers',
                                severity: getRandomSeverity(),
                                details: 'Missing important security headers: X-Content-Type-Options, X-Frame-Options'
                            });
                            break;
                        case 'vulnerabilities':
                            results.findings.push({
                                type: 'vulnerabilities',
                                title: 'Web Application Vulnerabilities',
                                severity: getRandomSeverity(),
                                details: 'Potential cross-site scripting (XSS) vulnerability detected in search form'
                            });
                            break;
                        case 'ports':
                            results.findings.push({
                                type: 'ports',
                                title: 'Open Ports',
                                severity: getRandomSeverity(),
                                details: 'Found open ports: 80, 443, 22, 25'
                            });
                            break;
                        case 'malware':
                            results.findings.push({
                                type: 'malware',
                                title: 'Malware Detection',
                                severity: 'info',
                                details: 'No malware detected on the website'
                            });
                            break;
                        case 'dns':
                            results.findings.push({
                                type: 'dns',
                                title: 'DNS Configuration',
                                severity: getRandomSeverity(),
                                details: 'SPF record is present but DMARC policy is missing'
                            });
                            break;
                    }
                });
                
                resolve(results);
            }, 2000);
        });
    }
    
    // Helper function to get random severity
    function getRandomSeverity() {
        const severities = ['critical', 'warning', 'info'];
        return severities[Math.floor(Math.random() * severities.length)];
    }
    
    // Function to display scan results
    function displayResults(results) {
        // Show results container
        resultsContainer.style.display = 'block';
        
        // Update summary
        securityScore.textContent = results.score;
        criticalIssues.textContent = results.issues.critical;
        warningIssues.textContent = results.issues.warnings;
        infoIssues.textContent = results.issues.info;
        
        // Clear previous results
        resultsDetails.innerHTML = '';
        
        // Add findings
        if (results.findings.length > 0) {
            const findingsList = document.createElement('ul');
            findingsList.className = 'findings-list';
            
            results.findings.forEach(finding => {
                const findingItem = document.createElement('li');
                findingItem.className = `finding ${finding.severity}`;
                
                findingItem.innerHTML = `
                    <div class="finding-header">
                        <h3>${finding.title}</h3>
                        <span class="severity ${finding.severity}">${finding.severity.toUpperCase()}</span>
                    </div>
                    <div class="finding-details">
                        <p>${finding.details}</p>
                    </div>
                `;
                
                findingsList.appendChild(findingItem);
            });
            
            resultsDetails.appendChild(findingsList);
            
            // Add some CSS for findings
            const style = document.createElement('style');
            style.textContent = `
                .findings-list {
                    list-style: none;
                    padding: 0;
                }
                
                .finding {
                    margin-bottom: 1rem;
                    padding: 1rem;
                    border-radius: 4px;
                    border-left: 4px solid #ccc;
                }
                
                .finding.critical {
                    border-left-color: #e74c3c;
                    background-color: rgba(231, 76, 60, 0.05);
                }
                
                .finding.warning {
                    border-left-color: #f39c12;
                    background-color: rgba(243, 156, 18, 0.05);
                }
                
                .finding.info {
                    border-left-color: #3498db;
                    background-color: rgba(52, 152, 219, 0.05);
                }
                
                .finding-header {
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    margin-bottom: 0.5rem;
                }
                
                .finding-header h3 {
                    margin: 0;
                }
                
                .severity {
                    padding: 0.25rem 0.5rem;
                    border-radius: 4px;
                    font-size: 0.8rem;
                    font-weight: bold;
                    color: white;
                }
                
                .severity.critical {
                    background-color: #e74c3c;
                }
                
                .severity.warning {
                    background-color: #f39c12;
                }
                
                .severity.info {
                    background-color: #3498db;
                }
                
                .finding-details {
                    margin-top: 0.5rem;
                }
            `;
            
            document.head.appendChild(style);
        } else {
            resultsDetails.innerHTML = '<p>No issues found.</p>';
        }
        
        // Scroll to results
        resultsContainer.scrollIntoView({ behavior: 'smooth' });
    }
});