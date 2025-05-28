#!/usr/bin/env python3
"""
Add font_family and color_style columns to scanners and customizations tables
"""
import sqlite3
import os
import logging

def add_columns():
    """Add the missing font_family and color_style columns"""
    # Define columns to add
    columns_to_add = [
        ("scanners", "font_family", "TEXT DEFAULT 'Inter'"),
        ("scanners", "color_style", "TEXT DEFAULT 'gradient'"),
        ("scanners", "favicon_url", "TEXT"),
        ("customizations", "font_family", "TEXT DEFAULT 'Inter'"),
        ("customizations", "color_style", "TEXT DEFAULT 'gradient'")
    ]
    
    # Main databases to check
    main_databases = ['cybrscan.db', 'client_scanner.db', 'clients.db']
    
    for main_db_path in main_databases:
        if os.path.exists(main_db_path):
            print(f"Updating main database: {main_db_path}")
            try:
                conn = sqlite3.connect(main_db_path)
                cursor = conn.cursor()
                
                for table, column, definition in columns_to_add:
                    try:
                        cursor.execute(f"ALTER TABLE {table} ADD COLUMN {column} {definition}")
                        print(f"✅ Added {column} to {table} table")
                    except sqlite3.OperationalError as e:
                        if "duplicate column name" in str(e).lower():
                            print(f"⚠️  Column {column} already exists in {table} table")
                        elif "no such table" in str(e).lower():
                            print(f"ℹ️  Table {table} doesn't exist in {main_db_path}")
                        else:
                            print(f"❌ Error adding {column} to {table}: {e}")
                
                conn.commit()
                conn.close()
                print(f"✅ Database {main_db_path} updated successfully")
                
            except Exception as e:
                print(f"❌ Error updating {main_db_path}: {e}")
        else:
            print(f"Database {main_db_path} not found")
    
    # Client-specific databases
    client_db_dir = 'client_databases'
    if os.path.exists(client_db_dir):
        print(f"\nUpdating client databases in {client_db_dir}")
        for filename in os.listdir(client_db_dir):
            if filename.endswith('.db'):
                db_path = os.path.join(client_db_dir, filename)
                print(f"Updating: {db_path}")
                try:
                    conn = sqlite3.connect(db_path)
                    cursor = conn.cursor()
                    
                    # Add columns to scanners table (client databases might have scanners table)
                    for table, column, definition in columns_to_add:
                        try:
                            cursor.execute(f"ALTER TABLE {table} ADD COLUMN {column} {definition}")
                            print(f"  ✅ Added {column} to {table} table")
                        except sqlite3.OperationalError as e:
                            if "duplicate column name" in str(e).lower():
                                print(f"  ⚠️  Column {column} already exists in {table} table")
                            elif "no such table" in str(e).lower():
                                print(f"  ℹ️  Table {table} doesn't exist in this database (normal)")
                            else:
                                print(f"  ❌ Error adding {column} to {table}: {e}")
                    
                    conn.commit()
                    conn.close()
                    print(f"  ✅ Updated {filename}")
                    
                except Exception as e:
                    print(f"  ❌ Error updating {filename}: {e}")

if __name__ == "__main__":
    print("Adding font_family and color_style columns to database tables...")
    add_columns()
    print("\nDatabase migration completed!")