# Scanner Limits Update

This document describes the implementation of subscription-based scanner limits in the CybrScann platform.

## Overview

Scanner limits have been implemented to enforce subscription tier restrictions. Each subscription level has a maximum number of scanners and scans per month:

- **Basic (Free)**: 1 scanner, 10 scans/month
- **Starter ($59/month)**: 1 scanner, 50 scans/month
- **Professional ($99/month)**: 3 scanners, 500 scans/month
- **Enterprise ($149/month)**: 10 scanners, 1000 scans/month

## Implementation Details

The following files have been updated to implement scanner limits:

### 1. Subscription Constants

**File:** `/subscription_constants.py`
- Added `LEGACY_PLAN_MAPPING` to map old subscription levels to new ones
- Added helper functions to get client subscription limits:
  - `get_client_subscription_level(client)` - Normalizes the subscription level
  - `get_client_scanner_limit(client)` - Gets the scanner limit for a client
  - `get_client_scan_limit(client)` - Gets the scan limit for a client

### 2. Client Module

**File:** `/client.py`
- Added `get_client_total_scans(client_id)` function to track scan usage
- Updated `scanner_create()` function to check limits before creating scanners
- Updated `scanners()` function to pass limit information to the template

### 3. Templates

**File:** `/templates/client/scanner-create.html`
- Added subscription info alert showing current usage and limits
- Disabled the create button when limit is reached

**File:** `/templates/client/scanners.html`
- Already had subscription limit displays, now using consistent data

### 4. Database Schema Updates

**File:** `/update_scanner_limits.py`
- Added functions to update the database schema with limit columns
- Updates client records with correct limits based on subscription level

## Usage

The system now enforces scanner limits in the following ways:

1. The scanner creation page shows the current usage and limits
2. Users cannot create more scanners than their subscription allows
3. The scanners list page shows usage information

## Legacy Plan Handling

Legacy subscription plans are automatically mapped to the new structure:
- 'business' → 'professional'
- 'pro' → 'professional'

## Testing Instructions

1. Log in as a client with each subscription level
2. Verify the scanner creation page shows correct limits
3. Create scanners up to the limit and verify the limit is enforced
4. Verify the scanners list page shows correct usage information