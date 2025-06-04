# Scanner Subscription Level Fixes

This document outlines the changes made to fix the subscription options shown during scanner creation.

## Issue

During scanner creation, after adding logo and colors, the system showed a subscription options page that only displayed three tiers (Starter, Professional, and Enterprise) but was missing the Basic (free) tier. This was inconsistent with the subscription constants defined in `subscription_constants.py`, which includes all four tiers including the Basic (free) tier.

## Changes Made

1. **Added Basic Tier to Client Settings Page**

   The client settings page (`/templates/client/settings.html`) has been updated to include all four subscription tiers:
   - Basic (Free): 1 scanner, 10 scans/month
   - Starter ($59/month): 1 scanner, 50 scans/month
   - Professional ($99/month): 3 scanners, 500 scans/month
   - Enterprise ($149/month): 10 scanners, 1000 scans/month

   All subscription options now properly show the correct features and prices consistent with the subscription constants.

2. **Created Dedicated Upgrade Subscription Page**

   A new template has been created at `/templates/client/upgrade-subscription.html` that shows all four subscription tiers when a user needs to upgrade their subscription. This page:
   - Shows the user's current subscription plan
   - Displays scanner and scan usage metrics
   - Provides detailed information about each plan's features
   - Shows appropriate upgrade/downgrade options based on the user's current plan
   - Handles both free and paid tiers appropriately

3. **Created Partial Template for Scanner Creation**

   A new partial template has been created at `/templates/partials/pricing-cards-scanner-creation.html` specifically for showing subscription options during scanner creation. This partial includes all four tiers with their correct prices and features.

## Implementation Details

1. The client settings page now uses a 4-column layout (one column per plan) instead of the previous 3-column layout.

2. The upgrade subscription page includes:
   - Current plan indicator
   - Usage metrics visualization
   - All four subscription tiers with their features
   - Special handling for the case when a scanner was just created
   - Payment form for upgrading to paid plans

3. All templates consistently show the same features and pricing for each plan:
   - Basic (Free): 1 scanner, 10 scans/month
   - Starter ($59/month): 1 scanner, 50 scans/month
   - Professional ($99/month): 3 scanners, 500 scans/month
   - Enterprise ($149/month): 10 scanners, 1000 scans/month

## Verification

These changes ensure that:
1. All subscription tiers, including the Basic (free) tier, are shown consistently throughout the application
2. Users can see and select the Basic tier during scanner creation
3. The subscription options match the subscription constants defined in `subscription_constants.py`
4. Existing functionality is preserved while fixing the missing Basic tier issue

## Future Considerations

To maintain consistency, any future changes to subscription tiers, prices, or features should be updated in:
1. The subscription constants file (`subscription_constants.py`)
2. The client settings template (`templates/client/settings.html`)
3. The upgrade subscription template (`templates/client/upgrade-subscription.html`)
4. The pricing cards partial templates