#!/usr/bin/env python3

import sqlite3
import os

def add_missing_columns():
    """Add missing columns to customizations table"""
    
    db_path = '/home/ggrun/CybrScan_1/client_scanner.db'
    
    if not os.path.exists(db_path):
        print(f"Database not found at {db_path}")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check existing columns
        cursor.execute("PRAGMA table_info(customizations)")
        existing_columns = [column[1] for column in cursor.fetchall()]
        print(f"Existing columns: {existing_columns}")
        
        # Define new columns to add
        new_columns = {
            'scanner_description': 'TEXT',
            'cta_button_text': 'TEXT DEFAULT "Start Security Scan"',
            'company_tagline': 'TEXT',
            'support_email': 'TEXT',
            'custom_footer_text': 'TEXT'
        }
        
        # Add missing columns
        for column_name, column_type in new_columns.items():
            if column_name not in existing_columns:
                try:
                    cursor.execute(f"""
                        ALTER TABLE customizations 
                        ADD COLUMN {column_name} {column_type}
                    """)
                    print(f"Added {column_name} column")
                except Exception as e:
                    print(f"Error adding {column_name}: {e}")
            else:
                print(f"{column_name} column already exists")
        
        conn.commit()
        conn.close()
        print("Database migration completed successfully")
        
    except Exception as e:
        print(f"Error during migration: {e}")

if __name__ == '__main__':
    add_missing_columns()