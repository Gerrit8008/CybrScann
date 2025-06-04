# Subscription Level Changes

## Overview

The subscription levels in CybrScann have been updated to match the 4-tier structure in CybrScan_1. The new levels are:

1. **Basic** (default, free)
2. **Starter** ($59/month)
3. **Professional** ($99/month)
4. **Enterprise** ($149/month)

All functionality has been preserved, with the addition of proper limits and details for each subscription level.

## Implementation Details

### New Subscription Levels

| Level        | Price      | Scanners | Scans/Month | White Label | API Access | Support             |
|--------------|------------|----------|-------------|-------------|------------|---------------------|
| Basic        | Free       | 1        | 10          | No          | No         | Community           |
| Starter      | $59/month  | 1        | 50          | Yes         | No         | Email               |
| Professional | $99/month  | 3        | 500         | Yes         | Yes        | Priority Phone      |
| Enterprise   | $149/month | 10       | 1000        | Yes         | Yes        | 24/7 Dedicated      |

### Changes Made

1. **Database Schema Update**
   - Added `subscription_details` column to store JSON details about the subscription
   - Added `scan_limit` and `scanner_limit` columns to enforce limits

2. **Updated Pricing Template**
   - Updated `pricing-cards.html` with the new subscription levels
   - Preserved all styling and design elements

3. **Subscription Constants**
   - Created a new file `subscription_constants.py` to define subscription levels and their features
   - Added helper functions to get subscription limits and features

4. **Limit Enforcement**
   - Added `check_scan_limit` and `check_scanner_limit` functions to enforce subscription limits
   - Created a patch file `subscription_limit_patch.py` that can be integrated into scan.py and scanner.py

5. **Client Registration Update**
   - Updated client registration to set subscription level based on the plan parameter
   - Set appropriate limits based on the subscription level

## How to Apply Changes

1. **Update Database and Subscriptions**
   ```bash
   python update_subscription_levels.py
   ```

2. **Check Current Subscription Status**
   ```bash
   python check_subscription_limits.py
   ```

3. **Integrate Limit Enforcement**
   Add the following to scan.py and scanner.py:
   ```python
   from subscription_limit_patch import check_scan_limit, check_scanner_limit
   
   # Before creating a scan:
   has_reached_limit, limit, count, remaining = check_scan_limit(client_id)
   if has_reached_limit:
       return error_response
   
   # Before creating a scanner:
   has_reached_limit, limit, count, remaining = check_scanner_limit(client_id)
   if has_reached_limit:
       return error_response
   ```

## Preserving Functionality

All existing functionality has been preserved:

1. **Client Management** - All client data and relationships remain unchanged
2. **Scanner Creation** - Scanner creation works as before, but with proper limits
3. **Scanning Functionality** - Scan creation and processing remain unchanged, but with proper limits
4. **Admin Dashboard** - Admin dashboard displays subscription information correctly
5. **Database Structure** - No breaking changes to the database structure

## Additional Features

1. **Subscription Details JSON**
   - Each client now has a `subscription_details` JSON field with detailed information about their subscription
   - This can be used to display subscription features and limits in the UI

2. **Limit Checking Helpers**
   - The `check_subscription_limits.py` script provides a way to check all client subscription limits
   - The `subscription_limit_patch.py` file provides functions to check limits in code

3. **Constants File**
   - The `subscription_constants.py` file provides a centralized place to define subscription levels and their features
   - This makes it easy to update subscription details in the future