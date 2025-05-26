#!/usr/bin/env python3

import sqlite3
import os

def add_button_color_column():
    """Add button_color column to customizations table"""
    
    db_path = '/home/ggrun/CybrScan_1/client_scanner.db'
    
    if not os.path.exists(db_path):
        print(f"Database not found at {db_path}")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if button_color column already exists
        cursor.execute("PRAGMA table_info(customizations)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'button_color' in columns:
            print("button_color column already exists")
        else:
            # Add the button_color column
            cursor.execute("""
                ALTER TABLE customizations 
                ADD COLUMN button_color TEXT DEFAULT '#02054c'
            """)
            print("Added button_color column to customizations table")
        
        # Check if updated_by column exists  
        if 'updated_by' not in columns:
            cursor.execute("""
                ALTER TABLE customizations 
                ADD COLUMN updated_by INTEGER
            """)
            print("Added updated_by column to customizations table")
        
        conn.commit()
        conn.close()
        print("Database migration completed successfully")
        
    except Exception as e:
        print(f"Error during migration: {e}")

if __name__ == '__main__':
    add_button_color_column()