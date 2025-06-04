# Customize Page Subscription Limits

This document describes the updates made to the scanner customization page to enforce subscription-based scanner limits.

## Overview

The scanner customization page has been updated to enforce and display subscription tier restrictions. Each subscription level has a maximum number of scanners:

- **Basic (Free)**: 1 scanner
- **Starter ($59/month)**: 1 scanner
- **Professional ($99/month)**: 3 scanners
- **Enterprise ($149/month)**: 10 scanners

## Implementation Details

The following files have been updated to implement scanner limits in the customization interface:

### 1. Templates

**File:** `/templates/client/customize_scanner.html`
- Added subscription info alert showing current usage and limits
- Added warning message when limit is reached
- Disabled action buttons when the scanner limit is reached
- Added upgrade button when the limit is reached

### 2. Route Handlers

**File:** `/scanner_routes_fixed.py`
- Updated `customize()` function to include subscription limit information
- Added client authentication check
- Added scanner count check against subscription limits
- Added warning message when scanner limit is reached

**File:** `/app.py`
- `customize_scanner()` function was already updated to include subscription limit information
- GET handler now checks subscription limits and adds alert if limit is reached

### 3. Helper Functions

**File:** `/subscription_constants.py`
- Using helper functions for subscription limits:
  - `get_client_subscription_level(client)`
  - `get_client_scanner_limit(client)`

## User Experience

With these changes, users will now:

1. See their current scanner usage and limits at the top of the customization page
2. Receive a warning message when they've reached their scanner limit
3. Have the buttons disabled when they can't create more scanners
4. See a prominent "Upgrade" button when they've reached their limit

## Verification

The subscription limits are now properly enforced in all scanner creation interfaces:

1. `/client/scanners/create` - Limited based on subscription level
2. `/customize` - Limited based on subscription level
3. `/scanner/customize` - Limited based on subscription level

Users will be unable to create more scanners than their subscription plan allows, and they'll see clear upgrade options when they reach their limit.