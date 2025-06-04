DROP TABLE IF EXISTS scans;
CREATE TABLE scans (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    scan_id TEXT UNIQUE NOT NULL,
    timestamp TEXT NOT NULL,
    target TEXT,
    results TEXT
);

-- Clients table to store basic client information
CREATE TABLE IF NOT EXISTS clients (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    business_name TEXT NOT NULL,
    business_domain TEXT NOT NULL,
    contact_email TEXT NOT NULL,
    contact_phone TEXT,
    scanner_name TEXT,
    subscription_level TEXT DEFAULT 'basic',
    subscription_status TEXT DEFAULT 'active',
    subscription_start TEXT,
    subscription_end TEXT,
    api_key TEXT UNIQUE,
    created_at TEXT,
    created_by INTEGER,
    updated_at TEXT,
    updated_by INTEGER,
    active BOOLEAN DEFAULT 1,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (created_by) REFERENCES users(id),
    FOREIGN KEY (updated_by) REFERENCES users(id)
);

-- Scanners table to store individual scanner configurations for clients
CREATE TABLE IF NOT EXISTS scanners (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    client_id INTEGER NOT NULL,
    scanner_id TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    domain TEXT,
    api_key TEXT UNIQUE NOT NULL,
    primary_color TEXT DEFAULT '#02054c',
    secondary_color TEXT DEFAULT '#35a310',
    logo_url TEXT,
    contact_email TEXT,
    contact_phone TEXT,
    email_subject TEXT DEFAULT 'Your Security Scan Report',
    email_intro TEXT,
    scan_types TEXT,  -- JSON or comma-separated list of enabled scan types
    status TEXT DEFAULT 'active',  -- active, inactive, deleted
    created_at TEXT NOT NULL,
    created_by INTEGER,
    updated_at TEXT NOT NULL,
    updated_by INTEGER,
    FOREIGN KEY (client_id) REFERENCES clients(id) ON DELETE CASCADE,
    FOREIGN KEY (created_by) REFERENCES users(id),
    FOREIGN KEY (updated_by) REFERENCES users(id)
);

-- Customizations table for client branding and visual options
CREATE TABLE IF NOT EXISTS customizations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    client_id INTEGER NOT NULL,
    primary_color TEXT DEFAULT '#02054c',
    secondary_color TEXT DEFAULT '#35a310',
    logo_path TEXT,
    favicon_path TEXT,
    custom_css TEXT,
    email_subject TEXT DEFAULT 'Your Security Scan Report',
    email_intro TEXT,
    email_signature TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    FOREIGN KEY (client_id) REFERENCES clients(id) ON DELETE CASCADE
);

-- Scan history table to track all scans performed by scanners
CREATE TABLE IF NOT EXISTS scan_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    scanner_id TEXT NOT NULL,
    scan_id TEXT UNIQUE NOT NULL,
    target_url TEXT,
    scan_type TEXT,
    status TEXT DEFAULT 'pending',  -- pending, running, completed, failed
    results TEXT,  -- JSON results
    created_at TEXT NOT NULL,
    completed_at TEXT,
    FOREIGN KEY (scanner_id) REFERENCES scanners(scanner_id) ON DELETE CASCADE
);
