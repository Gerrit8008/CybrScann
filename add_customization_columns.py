#!/usr/bin/env python3
"""
Add missing columns to customizations table for enhanced customization
"""

import sqlite3
import os

def add_customization_columns():
    """Add missing columns to customizations table"""
    try:
        # Database path
        db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'client_scanner.db')
        
        if not os.path.exists(db_path):
            print(f"❌ Database not found: {db_path}")
            return False
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # List of columns to add if they don't exist
        new_columns = [
            ('button_color', 'TEXT DEFAULT "#28a745"'),
            ('welcome_message', 'TEXT'),
            ('contact_email', 'TEXT'),
            ('scan_timeout', 'INTEGER DEFAULT 300'),
            ('results_retention', 'INTEGER DEFAULT 90'),
            ('language', 'TEXT DEFAULT "en"'),
            ('scan_types', 'TEXT DEFAULT "network,web,email,ssl"'),
            ('logo_url', 'TEXT'),
            ('favicon_url', 'TEXT'),
            ('last_updated', 'TEXT')
        ]
        
        # Check existing columns
        cursor.execute("PRAGMA table_info(customizations)")
        existing_columns = [row[1] for row in cursor.fetchall()]
        print(f"📋 Existing columns: {existing_columns}")
        
        # Add missing columns
        added_count = 0
        for column_name, column_def in new_columns:
            if column_name not in existing_columns:
                try:
                    cursor.execute(f"ALTER TABLE customizations ADD COLUMN {column_name} {column_def}")
                    print(f"✅ Added column: {column_name}")
                    added_count += 1
                except Exception as e:
                    print(f"❌ Error adding column {column_name}: {e}")
            else:
                print(f"ℹ️  Column already exists: {column_name}")
        
        # Also ensure the table exists if it doesn't
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS customizations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                client_id INTEGER NOT NULL,
                primary_color TEXT DEFAULT '#02054c',
                secondary_color TEXT DEFAULT '#35a310',
                button_color TEXT DEFAULT '#28a745',
                logo_path TEXT,
                logo_url TEXT,
                favicon_path TEXT,
                favicon_url TEXT,
                custom_css TEXT,
                email_subject TEXT DEFAULT 'Your Security Scan Report',
                email_intro TEXT,
                email_signature TEXT,
                welcome_message TEXT,
                contact_email TEXT,
                scan_timeout INTEGER DEFAULT 300,
                results_retention INTEGER DEFAULT 90,
                language TEXT DEFAULT 'en',
                scan_types TEXT DEFAULT 'network,web,email,ssl',
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                last_updated TEXT,
                FOREIGN KEY (client_id) REFERENCES clients(id) ON DELETE CASCADE
            )
        """)
        
        conn.commit()
        conn.close()
        
        print(f"🎉 Successfully updated customizations table!")
        print(f"   - Added {added_count} new columns")
        print(f"   - Customization functionality is now ready")
        
        return True
        
    except Exception as e:
        print(f"❌ Error updating customizations table: {e}")
        return False

if __name__ == "__main__":
    add_customization_columns()