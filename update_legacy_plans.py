#!/usr/bin/env python3
"""
Update legacy plan names in the database to new plan structure
"""
import sqlite3
import os

def update_legacy_plans():
    """Update legacy plan names in clients database"""
    # Main client database
    databases_to_check = ['cybrscan.db', 'client_scanner.db']
    
    # Plan mapping
    legacy_plan_mapping = {
        'basic': 'starter',
        'business': 'professional',
        'pro': 'professional'
    }
    
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
                    
                    # Update legacy plan names
                    for old_plan, new_plan in legacy_plan_mapping.items():
                        cursor.execute(
                            "UPDATE clients SET subscription_level = ? WHERE subscription_level = ?",
                            (new_plan, old_plan)
                        )
                        updated = cursor.rowcount
                        if updated > 0:
                            print(f"  ✅ Updated {updated} clients from '{old_plan}' to '{new_plan}'")
                    
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
    print("Updating legacy plan names...")
    update_legacy_plans()
    print("\nPlan update completed!")