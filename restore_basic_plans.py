#!/usr/bin/env python3
"""
Restore basic plans - convert any 'starter' plans back to 'basic' 
since they were incorrectly converted by the legacy plan mapping
"""
import sqlite3
import os

def restore_basic_plans():
    """Restore all clients to basic plan as the default free tier"""
    # Main client database
    databases_to_check = ['client_scanner.db']
    
    for db_name in databases_to_check:
        if os.path.exists(db_name):
            print(f"Checking database: {db_name}")
            try:
                conn = sqlite3.connect(db_name)
                cursor = conn.cursor()
                
                # Check if clients table exists
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='clients'")
                if cursor.fetchone():
                    # Get current plan distribution
                    cursor.execute("SELECT subscription_level, COUNT(*) FROM clients GROUP BY subscription_level")
                    current_plans = cursor.fetchall()
                    print(f"  Current plan distribution: {current_plans}")
                    
                    # Convert all 'starter' plans back to 'basic' since they were incorrectly mapped
                    cursor.execute(
                        "UPDATE clients SET subscription_level = 'basic' WHERE subscription_level = 'starter'",
                    )
                    updated = cursor.rowcount
                    if updated > 0:
                        print(f"  ✅ Restored {updated} clients from 'starter' back to 'basic'")
                    
                    # Get updated plan distribution
                    cursor.execute("SELECT subscription_level, COUNT(*) FROM clients GROUP BY subscription_level")
                    updated_plans = cursor.fetchall()
                    print(f"  Updated plan distribution: {updated_plans}")
                    
                    conn.commit()
                else:
                    print(f"  ℹ️  No clients table found in {db_name}")
                
                conn.close()
                print(f"  ✅ {db_name} processed successfully")
                
            except Exception as e:
                print(f"  ❌ Error processing {db_name}: {e}")
        else:
            print(f"  ⚠️  Database {db_name} not found")

if __name__ == "__main__":
    print("Restoring basic plans...")
    restore_basic_plans()
    print("\nBasic plan restoration completed!")