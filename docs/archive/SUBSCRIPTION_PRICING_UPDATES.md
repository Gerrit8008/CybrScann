# Subscription Pricing Updates

This document outlines the changes made to update the subscription pricing and tiers across the application.

## Overview

The subscription pricing model was updated to include the Basic (free) tier and standardize pricing across all parts of the application. The updated subscription tiers are:

- **Basic (Free)**: 1 scanner, 10 scans/month
- **Starter ($59/month)**: 1 scanner, 50 scans/month
- **Professional ($99/month)**: 3 scanners, 500 scans/month
- **Enterprise ($149/month)**: 10 scanners, 1000 scans/month

## Changes Made

### 1. Client Settings Page (`/templates/client/settings.html`)

Updated the subscription cards in the client settings page to:
- Add the Basic (free) tier
- Update pricing for all tiers ($59/$99/$149)
- Update scanner and scan limits for each tier

### 2. Upgrade Subscription Page (`/templates/client/upgrade-subscription.html`)

Created a new upgrade subscription page that:
- Shows all four subscription tiers
- Displays current usage metrics
- Allows users to upgrade or downgrade their subscription
- Includes payment processing for paid tiers

### 3. Scanner Creation Pricing Cards (`/templates/partials/pricing-cards-scanner-creation.html`)

Created a dedicated pricing cards partial template for the scanner creation process, showing all four tiers with correct pricing and features.

### 4. Admin Customization Form (`/templates/admin/customization-form.html`)

Updated the "Brand Your Security Scanner" section to:
- Add the Basic (free) tier
- Update pricing for all tiers ($59/$99/$149)
- Update scanner and scan limits for each tier
- Update JavaScript code to handle the Basic tier and correct pricing

## Technical Details

### JavaScript Updates

The JavaScript code in the admin customization form was updated to handle the Basic tier and display correct pricing:

1. Added initialization for the Basic plan radio button:
```javascript
const basicPlan = document.getElementById('basicPlan');
```

2. Updated the payment summary code to include the Basic tier and correct pricing:
```javascript
if (basicPlan.checked) {
    selectedPlanDisplay.textContent = 'Basic Plan';
    selectedPriceDisplay.textContent = 'Free';
} else if (starterPlan.checked) {
    selectedPlanDisplay.textContent = 'Starter Plan';
    selectedPriceDisplay.textContent = '$59/month';
} else if (professionalPlan.checked) {
    selectedPlanDisplay.textContent = 'Professional Plan';
    selectedPriceDisplay.textContent = '$99/month';
} else if (enterprisePlan.checked) {
    selectedPlanDisplay.textContent = 'Enterprise Plan';
    selectedPriceDisplay.textContent = '$149/month';
}
```

3. Added event listener for the Basic plan radio button:
```javascript
basicPlan.addEventListener('change', function() {
    if (this.checked) {
        selectedPlanDisplay.textContent = 'Basic Plan';
        selectedPriceDisplay.textContent = 'Free';
    }
});
```

### HTML Updates

The HTML structure for the subscription options was updated to:
- Use a 4-column layout (one column per plan)
- Include correct pricing and features for each tier
- Show scanner and scan limits for each tier

## Verification

These changes ensure that:
1. All subscription tiers, including the Basic (free) tier, are shown consistently throughout the application
2. Users can see and select the Basic tier during scanner creation
3. The subscription options match the subscription constants defined in `subscription_constants.py`
4. The pricing is consistent across all templates