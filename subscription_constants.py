#!/usr/bin/env python3
"""
Subscription Constants

This file defines the subscription levels and their features.
"""

# Legacy plan mapping
LEGACY_PLAN_MAPPING = {
    'business': 'professional',
    'pro': 'professional'
}

# Subscription level definitions
SUBSCRIPTION_LEVELS = {
    'basic': {
        'name': 'Basic',
        'price': 0.00,  # Free
        'period': 'forever',
        'description': 'Perfect for trying out our platform',
        'features': {
            'scanners': 1,
            'scans_per_month': 10,
            'white_label': False,
            'branding': 'Basic branding',
            'reports': 'Email reports',
            'support': 'Community support',
            'api_access': False,
            'client_portal': False
        }
    },
    'starter': {
        'name': 'Starter',
        'price': 59.00,
        'period': 'month',
        'description': 'Perfect for small MSPs getting started',
        'features': {
            'scanners': 1,
            'scans_per_month': 50,
            'white_label': True,
            'branding': 'White-label branding',
            'reports': 'Basic reporting',
            'support': 'Email support',
            'api_access': False,
            'client_portal': True,
            'integrations': 'Basic integrations'
        }
    },
    'professional': {
        'name': 'Professional',
        'price': 99.00,
        'period': 'month',
        'description': 'Ideal for growing MSPs',
        'popular': True,
        'features': {
            'scanners': 3,
            'scans_per_month': 500,
            'white_label': True,
            'branding': 'Advanced white-labeling',
            'reports': 'Professional reporting',
            'support': 'Priority phone support',
            'api_access': True,
            'client_portal': True,
            'integrations': 'Custom integrations',
            'scheduled_scanning': True
        }
    },
    'enterprise': {
        'name': 'Enterprise',
        'price': 149.00,
        'period': 'month',
        'description': 'For large MSPs and enterprises',
        'features': {
            'scanners': 10,
            'scans_per_month': 1000,
            'white_label': True,
            'branding': 'Complete white-labeling',
            'reports': 'Executive reporting',
            'support': '24/7 dedicated support',
            'api_access': True,
            'client_portal': True,
            'integrations': 'Custom development',
            'scheduled_scanning': True,
            'sla': True,
            'training': True,
            'multi_tenant': True
        }
    }
}

def get_subscription_features(level):
    """Get the features for a subscription level"""
    if level not in SUBSCRIPTION_LEVELS:
        level = 'basic'  # Default to basic if level not found
    return SUBSCRIPTION_LEVELS[level]

def get_subscription_limit(level, limit_type):
    """Get a specific limit for a subscription level"""
    if level not in SUBSCRIPTION_LEVELS:
        level = 'basic'  # Default to basic if level not found
    
    features = SUBSCRIPTION_LEVELS[level]['features']
    if limit_type == 'scanners':
        return features.get('scanners', 1)
    elif limit_type == 'scans':
        return features.get('scans_per_month', 10)
    else:
        return None

def get_subscription_price(level):
    """Get the price for a subscription level"""
    if level not in SUBSCRIPTION_LEVELS:
        level = 'basic'  # Default to basic if level not found
    return SUBSCRIPTION_LEVELS[level]['price']


def get_client_subscription_level(client):
    """Get normalized subscription level for a client"""
    if not client:
        return 'basic'  # Default to basic
    
    subscription_level = client.get('subscription_level', 'basic').lower()
    
    # Handle legacy plan names
    if subscription_level in LEGACY_PLAN_MAPPING:
        subscription_level = LEGACY_PLAN_MAPPING[subscription_level]
    
    # Ensure subscription_level exists in SUBSCRIPTION_LEVELS
    if subscription_level not in SUBSCRIPTION_LEVELS:
        subscription_level = 'basic'
    
    return subscription_level


def get_client_scanner_limit(client):
    """Get scanner limit based on client's subscription level"""
    subscription_level = get_client_subscription_level(client)
    return SUBSCRIPTION_LEVELS[subscription_level]['features']['scanners']


def get_client_scan_limit(client):
    """Get scan limit based on client's subscription level"""
    subscription_level = get_client_subscription_level(client)
    return SUBSCRIPTION_LEVELS[subscription_level]['features']['scans_per_month']