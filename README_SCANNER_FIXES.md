# CybrScan Scanner Fixes

This document details the fixes implemented to address issues with the scanner functionality in the CybrScan platform.

## Issues Fixed

### 1. Scanner Names with "client 6" Prefix

All scanners were being created with "client 6" added to their name, causing confusion and display issues.

**Fix implemented:**
- Direct database updates to remove the prefix from existing scanners
- Patched scanner creation function to prevent adding the prefix to new scanners
- Updated scanner records in all client databases

### 2. Risk Assessment Score and Color Issues

Risk assessment scores were always displaying as 75 with a gray circle instead of the actual score with appropriate coloring.

**Fix implemented:**
- Added proper risk score calculation based on security findings
- Implemented color assignment based on score ranges
- Modified report templates to use the appropriate colors
- Updated existing scan results in databases to include color information

## How the Fixes Work

### Scanner Name Fix

The fix addresses scanner names in three ways:

1. **Existing Scanners**: Directly updates the database to remove "client 6" from scanner names
2. **Scanner Creation**: Patches the `scanner_create` function to prevent adding the prefix to new scanners
3. **Client IDs**: Fixes any incorrect client IDs (changing from 6 to 5 where appropriate)

### Risk Assessment Color Fix

The fix for risk assessment colors:

1. **Color Calculation**: Implements proper color assignment based on score ranges:
   - 90-100: Green (#28a745) - Low Risk
   - 80-89: Light Green (#5cb85c) - Low-Medium Risk
   - 70-79: Info Blue (#17a2b8) - Medium Risk
   - 60-69: Warning Yellow (#ffc107) - Medium-High Risk
   - 50-59: Orange (#fd7e14) - High Risk
   - 0-49: Red (#dc3545) - Critical Risk

2. **Template Updates**: Modifies the results.html template to use the calculated colors
3. **Database Updates**: Updates existing scan results to include color information

## Applied Fixes

The fixes are applied through the `direct_fix.py` script, which:

1. Patches runtime functions using monkey patching
2. Updates database records directly
3. Modifies template files

## Technical Implementation

The implementation uses several approaches:

1. **Runtime Patching**: Using Python's ability to replace functions at runtime
2. **Direct Database Modifications**: Using SQLite connections to update records
3. **Template Modifications**: Updating Jinja2 templates to use dynamic color values

These fixes ensure that:
- All scanner names are displayed correctly without the "client 6" prefix
- Risk assessment scores are properly calculated and displayed with appropriate colors
- The system remains consistent for both existing and new scans

## How to Apply the Fixes

See the `HOW_TO_FIX_SCANNER_AND_RISK_COLOR.md` file for detailed instructions on applying these fixes to your CybrScan installation.