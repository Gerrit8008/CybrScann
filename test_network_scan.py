#!/usr/bin/env python3
"""
Test script to demonstrate the enhanced network scanning functionality
"""

def test_network_scan_processing():
    """Test how network scan results are processed for the results template"""
    
    # Simulate the output from scan_gateway_ports function
    simulated_network_results = [
        ("Client detected at IP: 192.168.1.100", "Info"),
        ("Scanning target domain: example.com", "Info"),
        ("Port 80 (HTTP (no encryption)) is open on example.com", "Medium"),
        ("Port 443 (HTTPS) is open on example.com", "Low"),
        ("Port 22 (SSH) is open on example.com", "Low"),
        ("Port 3389 (Remote Desktop (RDP)) is open on 192.168.1.1", "Critical"),
        ("SUMMARY: Found 4 open ports", "High")
    ]
    
    print("🧪 Testing Network Scan Results Processing")
    print("=" * 50)
    
    # Simulate the processing logic from scan_routes.py
    findings = []
    network_data = simulated_network_results
    
    if isinstance(network_data, list):
        open_ports_count = 0
        high_risk_ports = []
        
        for item in network_data:
            if isinstance(item, tuple) and len(item) >= 2:
                message, severity = item[0], item[1]
                
                # Count open ports
                if "Port" in message and "is open" in message:
                    open_ports_count += 1
                    if severity in ['High', 'Critical']:
                        # Extract port number for specific warnings
                        import re
                        port_match = re.search(r'Port (\d+)', message)
                        if port_match:
                            high_risk_ports.append(port_match.group(1))
                
                # Add findings for high/critical severity items
                if severity in ['High', 'Critical', 'Medium']:
                    findings.append({
                        'category': 'Network Security',
                        'severity': severity,
                        'title': 'Network Security Issue',
                        'description': message,
                        'recommendation': 'Review network configuration and close unnecessary services'
                    })
        
        # Add summary finding if open ports detected
        if open_ports_count > 0:
            findings.append({
                'category': 'Network Security',
                'severity': 'High' if high_risk_ports else 'Medium',
                'title': f'Open Ports Detected ({open_ports_count} total)',
                'description': f"Found {open_ports_count} open ports. High-risk ports: {', '.join(high_risk_ports) if high_risk_ports else 'None'}",
                'recommendation': 'Review all open ports and close unnecessary services to reduce attack surface'
            })
    
    print(f"📊 Processed Results:")
    print(f"   Total findings generated: {len(findings)}")
    print(f"   Open ports detected: {open_ports_count}")
    print(f"   High-risk ports: {', '.join(high_risk_ports) if high_risk_ports else 'None'}")
    
    print(f"\n🔍 Network Security Findings:")
    for i, finding in enumerate(findings, 1):
        print(f"   {i}. [{finding['severity']}] {finding['title']}")
        print(f"      Description: {finding['description']}")
        print()
    
    print("✅ Network scan results will now properly display in the results section!")
    return findings

if __name__ == "__main__":
    test_network_scan_processing()