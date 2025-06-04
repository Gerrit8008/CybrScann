# Scanner Customization Limits Implementation

This document describes how subscription-based limits are enforced in the scanner customization interface.

## Overview

Scanner creation and customization are now limited based on the client's subscription level. Each plan has specific scanner limits:

- **Basic (Free)**: 1 scanner
- **Starter ($59/month)**: 1 scanner
- **Professional ($99/month)**: 3 scanners
- **Enterprise ($149/month)**: 10 scanners

## Implementation Details

### Updated Files

1. **Template Files:**
   - `/templates/client/customize_scanner.html` - Added subscription limit warning and disabled buttons when limit is reached
   - `/templates/admin/customization-form.html` - Added subscription limit warning and disabled the create button when limit is reached

2. **Route Handlers:**
   - `/scanner_routes_fixed.py` - Added subscription limit checks to the `create_scanner_form()` and `customize_scanner()` functions
   - `/app.py` - Updated the main `/customize` route to check subscription limits

3. **Helper Functions:**
   - Using subscription limit functions from `subscription_constants.py`:
     - `get_client_subscription_level(client)`
     - `get_client_scanner_limit(client)`

### Functionality

1. **Subscription Limit Checking:**
   - When a user accesses any scanner creation or customization page, the system checks how many scanners they currently have
   - It compares this count with their subscription limit based on their plan level
   - If they've reached their limit, they're shown a warning and the create buttons are disabled

2. **Visual Indicators:**
   - Warning messages appear at the top of the page showing current usage and limits
   - Create/Save buttons are disabled when the limit is reached
   - An "Upgrade Plan" button appears when the limit is reached

3. **Subscription Level Mapping:**
   - Legacy subscription levels are automatically mapped to the new structure:
     - 'business' → 'professional'
     - 'pro' → 'professional'

## User Experience

With these changes:
1. Users see their current scanner usage and limits
2. They're prevented from creating more scanners than their plan allows
3. They're provided with clear upgrade options when they reach their limit

## Testing

To test these changes:
1. Log in as a client with each subscription level
2. Check that the correct scanner limit is displayed
3. Create scanners up to the limit and verify you cannot create more
4. Verify that the upgrade button appears when you reach your limit
5. Verify that error messages are shown when attempting to exceed limits

## Related Documentation

- See also: `SCANNER_LIMITS_UPDATE.md` for more information about the overall scanner limit implementation
- See also: `SUBSCRIPTION_LEVEL_CHANGES.md` for details about the subscription level structure