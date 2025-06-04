# Subscription Limit Enforcement

This document describes how subscription limits are enforced throughout the CybrScann-main application.

## Overview

Each subscription level has specific limits on the number of scanners and scans per month:

- **Basic (Free)**: 1 scanner, 10 scans/month
- **Starter ($59/month)**: 1 scanner, 50 scans/month
- **Professional ($99/month)**: 3 scanners, 500 scans/month
- **Enterprise ($149/month)**: 10 scanners, 1000 scans/month

These limits are enforced in various parts of the application to ensure users stay within their subscription bounds.

## Implementation Details

### 1. Subscription Constants

The file `subscription_constants.py` defines all subscription levels and their features, including scanner and scan limits. It also provides helper functions to retrieve these limits:

```python
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
```

### 2. Scanner Creation Routes

The scanner creation routes in `scanner_routes_fixed.py` check subscription limits before allowing users to create new scanners:

```python
@scanner_bp.route('/customize')
@client_required
def customize(user):
    """Main scanner creation/customization page"""
    # Check for subscription limits
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get client information
        cursor.execute('''
            SELECT * FROM clients 
            WHERE user_id = ? AND active = 1
        ''', (user['id'],))
        user_client = cursor.fetchone()
        
        if not user_client:
            flash('Client profile not found. Please complete your profile first.', 'warning')
            return redirect(url_for('client.settings'))
        
        user_client = dict(user_client)
        
        # Import subscription constants
        from subscription_constants import get_client_scanner_limit
        
        # Get current scanner count
        cursor.execute('SELECT COUNT(*) FROM scanners WHERE client_id = ? AND status != "deleted"', (user_client['id'],))
        current_scanners = cursor.fetchone()[0]
        conn.close()
        
        # Get scanner limit based on subscription level
        scanner_limit = get_client_scanner_limit(user_client)
        
        # Check if client has reached their scanner limit
        if current_scanners >= scanner_limit:
            flash(f'Scanner limit reached ({current_scanners}/{scanner_limit}). Please upgrade your subscription to create more scanners.', 'warning')
    except Exception as e:
        logging.error(f"Error checking subscription limits: {e}")
```

Similarly, the `/create` route checks limits before allowing scanner creation:

```python
# Get scanner limit based on subscription level
scanner_limit = get_client_scanner_limit(user_client)

# Check if client has reached their scanner limit
if current_scanners >= scanner_limit:
    flash(f'Scanner limit reached ({current_scanners}/{scanner_limit}). Please upgrade your subscription to create more scanners.', 'warning')
```

### 3. User Interface Elements

Several templates enforce subscription limits at the UI level:

#### Scanner Creation Form

In `templates/client/scanner-create.html`, the "Create Scanner" button is disabled when the user has reached their scanner limit:

```html
<button type="submit" class="btn btn-primary" 
        {% if current_scanners is defined and scanner_limit is defined and current_scanners >= scanner_limit %}disabled{% endif %}>
    <i class="bi bi-plus-circle"></i> Create Scanner
</button>
```

An alert message is also displayed to inform users of their current usage:

```html
{% if current_scanners is defined and scanner_limit is defined %}
<div class="alert alert-info alert-dismissible fade show" role="alert">
    <h5><i class="bi bi-info-circle me-2"></i>Scanner Usage</h5>
    <div class="row">
        <div class="col-md-6">
            <strong>Current Plan:</strong> 
            {{ client.subscription_level|title if client.subscription_level else 'Basic' }}
        </div>
        <div class="col-md-6">
            <strong>Scanners:</strong> {{ current_scanners }} / {{ scanner_limit }}
            {% if current_scanners >= scanner_limit %}
            <span class="badge bg-warning ms-2">Limit Reached</span>
            {% endif %}
        </div>
    </div>
    
    {% if current_scanners >= scanner_limit %}
    <hr>
    <p class="mb-0">You've reached your scanner limit. Please upgrade your subscription to create more scanners.</p>
    {% endif %}
</div>
{% endif %}
```

#### Scanner List Page

In `templates/client/scanners.html`, the "Create New Scanner" button is disabled when the user has reached their scanner limit:

```html
{% if pagination.total_count >= scanner_limit %}
<button class="btn btn-primary" disabled title="Scanner limit reached ({{ pagination.total_count }}/{{ scanner_limit }}). Please upgrade your plan to create more scanners.">
    <i class="bi bi-plus-circle me-2"></i>Scanner Limit Reached
</button>
{% else %}
<a href="/customize" class="btn btn-primary">
    <i class="bi bi-plus-circle me-2"></i>Create New Scanner
</a>
{% endif %}
```

The page also displays usage statistics to show users their scanner and scan usage:

```html
<div class="col-md-6">
    <div class="card border-0 shadow-sm">
        <div class="card-body">
            <h6 class="card-title mb-3">
                <i class="bi bi-shield-check me-2 text-primary"></i>Scanner Usage
            </h6>
            <div class="mb-3">
                <div class="d-flex justify-content-between align-items-center mb-2">
                    <span class="text-muted">Scanners Active</span>
                    <span class="fw-bold {% if pagination.total_count >= scanner_limit %}text-warning{% else %}text-success{% endif %}">
                        {{ pagination.total_count }}/{{ scanner_limit }}
                    </span>
                </div>
                <div class="progress" style="height: 8px;">
                    <div class="progress-bar {% if pagination.total_count >= scanner_limit %}bg-warning{% else %}bg-success{% endif %}" 
                         role="progressbar" 
                         style="width: {{ (pagination.total_count / scanner_limit * 100) if scanner_limit > 0 else 0 }}%">
                    </div>
                </div>
                {% if pagination.total_count >= scanner_limit %}
                <small class="text-warning">
                    <i class="bi bi-info-circle me-1"></i>
                    Scanner limit reached. <a href="/client/upgrade" class="text-decoration-none">Upgrade</a> to create more scanners.
                </small>
                {% else %}
                <small class="text-muted">
                    {{ scanner_limit - pagination.total_count }} scanner slots available.
                </small>
                {% endif %}
            </div>
        </div>
    </div>
</div>
```

#### Customize Scanner Page

In `templates/client/customize_scanner.html`, an alert message shows subscription information:

```html
<div class="alert alert-info alert-dismissible fade show mb-4" role="alert">
    <h5><i class="bi bi-info-circle me-2"></i>Scanner Usage</h5>
    <div class="row">
        <div class="col-md-6">
            <strong>Current Plan:</strong> 
            {{ subscription_level|title if subscription_level else 'Basic' }}
        </div>
        <div class="col-md-6">
            <strong>Scanners:</strong> {{ current_scanners }} / {{ scanner_limit }}
            {% if current_scanners >= scanner_limit %}
            <span class="badge bg-warning ms-2">Limit Reached</span>
            {% endif %}
        </div>
    </div>
</div>
```

Action buttons are disabled when limits are reached:

```html
<button type="button" class="btn btn-primary" id="saveAndPreviewBtn" 
        {% if current_scanners is defined and scanner_limit is defined and current_scanners >= scanner_limit %}disabled{% endif %}>
    <i class="bi bi-eye me-2"></i>Save & Preview Scanner
</button>

<button type="button" class="btn btn-success" id="saveAndDeployBtn"
        {% if current_scanners is defined and scanner_limit is defined and current_scanners >= scanner_limit %}disabled{% endif %}>
    <i class="bi bi-rocket me-2"></i>Save & Deploy Scanner
</button>
```

### 4. Route Data Passing

All scanner-related routes pass subscription limit information to the templates:

```python
return render_template(
    'scanner_form.html',
    user=user,
    client=user_client,
    customizations=customizations,
    current_scanners=current_scanners,
    scanner_limit=scanner_limit,
    subscription_level=user_client.get('subscription_level', 'basic')
)
```

## Conclusion

The CybrScann-main application has comprehensive subscription limit enforcement throughout its codebase. This ensures that:

1. Users cannot create more scanners than their subscription allows
2. Users are clearly informed of their usage and limits
3. Appropriate warning messages are displayed when limits are reached
4. Upgrade options are presented when users hit their limits

This approach creates a consistent experience across all parts of the application while enforcing business rules related to subscription tiers.