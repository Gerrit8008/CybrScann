# File Splitting Plan for CybrScann-main

This document outlines a plan to split large files in the CybrScann-main codebase into smaller, more manageable files to improve readability, maintainability, and parsing.

## 1. client_db.py (4688 lines)

This file contains database interaction functions for client management and is the largest file in the codebase. It should be split into these modules:

### Proposed Split:

1. `db/core.py` - Core database functionality
   - Database connection functions
   - Transaction decorators
   - Schema definitions

2. `db/client.py` - Client-related database functions
   - get_client_by_user_id
   - list_clients
   - update_client
   - deactivate_client

3. `db/scanner.py` - Scanner-related database functions
   - get_deployed_scanners_by_client_id
   - get_scanner_by_id
   - update_scanner_config
   - regenerate_scanner_api_key

4. `db/scan_results.py` - Scan results and reports
   - get_scan_history_by_client_id
   - get_scan_results
   - format_scan_results_for_client
   - save_scan_results

5. `db/dashboard.py` - Dashboard data functions
   - get_client_dashboard_data
   - get_client_statistics
   - get_dashboard_summary
   - get_recent_activities

6. `db/audit.py` - Audit logging functions
   - add_audit_log
   - track_activity
   - get_audit_logs

7. `db/__init__.py` - Imports and exposes all functions

## 2. app.py (4630 lines)

This file contains the main application logic and is the second largest file. It should be split into these modules:

### Proposed Split:

1. `app/core.py` - Core application setup
   - App initialization
   - Configuration 
   - Blueprint registration
   - Error handlers

2. `app/scan_engine.py` - Scanning functionality
   - scan_gateway_ports
   - check_ssl_certificate
   - check_security_headers
   - detect_cms

3. `app/routes/index.py` - Main routes
   - Home page
   - Landing page
   - Error pages

4. `app/routes/api.py` - API routes
   - /api/scan
   - /api/results
   - /api/email_report

5. `app/email.py` - Email functionality
   - send_email_report
   - send_notification
   - email templates

6. `app/utils.py` - Utility functions
   - extract_domain_from_email
   - secure_filename
   - server_lookup

7. `app/__init__.py` - Initialization code
   - create_app function
   - Import and register all components

## 3. scan.py (2375 lines)

This file contains scanning functionality and should be split into more specialized modules:

### Proposed Split:

1. `scan/core.py` - Core scanning functionality
   - High-level scan coordination
   - Result processing

2. `scan/network.py` - Network scanning
   - get_client_and_gateway_ip
   - scan_gateway_ports
   - get_default_gateway_ip

3. `scan/web.py` - Web scanning
   - check_ssl_certificate
   - check_security_headers
   - detect_cms
   - analyze_cookies
   - detect_web_framework

4. `scan/dns.py` - DNS scanning
   - analyze_dns_configuration
   - check_spf_status
   - check_dmarc_record
   - check_dkim_record

5. `scan/system.py` - System scanning
   - check_os_updates
   - check_firewall_status

6. `scan/risk.py` - Risk assessment
   - determine_industry
   - calculate_industry_percentile
   - categorize_risks_by_services

7. `scan/__init__.py` - Initialization and exports

## Implementation Strategy

### Phase 1: Set Up Directory Structure

```bash
mkdir -p /home/ggrun/CybrScann-main/db
mkdir -p /home/ggrun/CybrScann-main/app/routes
mkdir -p /home/ggrun/CybrScann-main/scan
```

### Phase 2: Split Files and Create Import Proxies

For each major file, create a script that:
1. Extracts relevant functions
2. Creates new module files
3. Creates an `__init__.py` that re-exports all functions
4. Replaces the original file with import statements

### Phase 3: Update Import Statements

Update all files that import from the original files to import from the new modules.

### Phase 4: Testing

Create comprehensive tests to verify that the split files maintain the exact same functionality as the original monolithic files.

## Benefits of This Approach

1. **Improved Readability**: Smaller files focused on specific functionality
2. **Better Maintainability**: Changes to one area won't affect unrelated code
3. **Easier Parsing**: Tools like Claude can more easily analyze smaller files
4. **Better Organization**: Code is organized by functional area
5. **Easier Testing**: Can test specific modules independently
6. **Clearer Dependencies**: Dependencies between modules become explicit

## Initial Implementation Script

A script called `split_large_files.py` will be created to automate this process for the first few modules as a proof of concept.