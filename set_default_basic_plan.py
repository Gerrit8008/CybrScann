#!/usr/bin/env python3
"""
Set default basic plan for clients without a valid subscription level
"""
import sqlite3
import os

def set_default_basic_plan():
    """Set basic plan as default for new or clients without valid plan"""
    # Main client database
    databases_to_check = ['client_scanner.db']
    
    valid_plans = ['basic', 'starter', 'professional', 'enterprise']
    
    for db_name in databases_to_check:
        if os.path.exists(db_name):
            print(f"Checking database: {db_name}")
            try:
                conn = sqlite3.connect(db_name)
                cursor = conn.cursor()
                
                # Check if clients table exists
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='clients'")
                if cursor.fetchone():
                    # Get clients with null or invalid subscription levels
                    cursor.execute("""
                        SELECT id, subscription_level FROM clients 
                        WHERE subscription_level IS NULL 
                        OR subscription_level NOT IN ('basic', 'starter', 'professional', 'enterprise')
                    """)
                    clients_to_update = cursor.fetchall()
                    
                    if clients_to_update:
                        print(f"  Found {len(clients_to_update)} clients to update:")
                        for client_id, current_level in clients_to_update:
                            print(f"    Client {client_id}: '{current_level}' → 'basic'")
                        
                        # Update to basic plan
                        cursor.execute("""
                            UPDATE clients 
                            SET subscription_level = 'basic'
                            WHERE subscription_level IS NULL 
                            OR subscription_level NOT IN ('basic', 'starter', 'professional', 'enterprise')
                        """)
                        
                        updated = cursor.rowcount
                        print(f"  ✅ Updated {updated} clients to 'basic' plan")
                    else:
                        print(f"  ✅ All clients already have valid subscription levels")
                    
                    # Show current plan distribution
                    cursor.execute("SELECT subscription_level, COUNT(*) FROM clients GROUP BY subscription_level")
                    plan_distribution = cursor.fetchall()
                    print(f"  Current plan distribution: {plan_distribution}")
                    
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
    print("Setting default basic plan for clients...")
    set_default_basic_plan()
    print("\nDefault plan setup completed!")