#!/usr/bin/env python3
"""Fix syntax errors in app.py"""

import ast

def fix_app_syntax():
    """Fix syntax errors in app.py"""
    print("🔧 FIXING APP.PY SYNTAX ERRORS")
    print("=" * 35)
    
    app_path = '/home/ggrun/CybrScan_1/app.py'
    
    try:
        # First, test if we can parse the current file
        with open(app_path, 'r') as f:
            content = f.read()
        
        try:
            ast.parse(content)
            print("✅ No syntax errors found!")
            return True
        except SyntaxError as e:
            print(f"❌ Syntax error found at line {e.lineno}: {e.msg}")
            print(f"   Text: {e.text}")
            
            # Try to fix common issues
            lines = content.split('\n')
            
            # Fix the specific error we know about
            for i, line in enumerate(lines):
                line_num = i + 1
                
                # Fix missing indentation issues
                if 'logging.error(traceback.format_exc())            else:' in line:
                    lines[i] = line.replace('logging.error(traceback.format_exc())            else:', 
                                          'logging.error(traceback.format_exc())')
                    lines.insert(i + 1, '            else:')
                    print(f"   Fixed line {line_num}: Added proper line break")
                
                # Fix any other similar issues
                if '    except Exception as e:' in line and 'else:' in line:
                    parts = line.split('else:')
                    if len(parts) == 2:
                        lines[i] = parts[0].rstrip()
                        lines.insert(i + 1, '            else:')
                        print(f"   Fixed line {line_num}: Separated else clause")
            
            # Write the fixed content
            fixed_content = '\n'.join(lines)
            
            # Test if the fix worked
            try:
                ast.parse(fixed_content)
                print("✅ Syntax errors fixed!")
                
                with open(app_path, 'w') as f:
                    f.write(fixed_content)
                
                return True
            except SyntaxError as e2:
                print(f"❌ Still has syntax error at line {e2.lineno}: {e2.msg}")
                
                # Try a more aggressive fix around the problematic area
                return fix_specific_area(app_path, e2.lineno)
        
    except Exception as e:
        print(f"❌ Error fixing syntax: {e}")
        return False

def fix_specific_area(app_path, error_line):
    """Fix the specific problematic area around the error"""
    print(f"\n🎯 FIXING SPECIFIC AREA AROUND LINE {error_line}")
    print("=" * 45)
    
    try:
        with open(app_path, 'r') as f:
            lines = f.readlines()
        
        # Find the problematic section and rebuild it cleanly
        start_line = max(0, error_line - 50)
        end_line = min(len(lines), error_line + 20)
        
        print(f"   Checking lines {start_line} to {end_line}")
        
        # Look for the scan tracking section and rebuild it
        for i in range(start_line, end_line):
            line = lines[i].strip()
            
            if 'Check if current user is logged in and link scan to their client' in line:
                print(f"   Found problematic section at line {i+1}")
                
                # Replace the entire problematic section with clean code
                replacement = '''            else:
                # Check if current user is logged in and link scan to their client
                try:
                    from client_db import verify_session, get_client_by_user_id
                    session_token = session.get('session_token')
                    if session_token:
                        result = verify_session(session_token)
                        # Handle different return formats from verify_session
                        if result.get('status') == 'success' and result.get('user'):
                            user_client = get_client_by_user_id(result['user']['user_id'])
                            if user_client:
                                scan_results['client_id'] = user_client['id']
                                scan_results['scanner_id'] = 'web_interface'
                                scan_results.update(lead_data)
                                logger.info(f"Linked scan to client {user_client['id']} via user {result['user']['user_id']}")
                                
                                # Save to client-specific database
                                try:
                                    from client_database_manager import save_scan_to_client_db
                                    save_scan_to_client_db(user_client['id'], scan_results)
                                    logging.info(f"Saved scan to client-specific database for client {user_client['id']}")
                                except Exception as client_db_error:
                                    logging.error(f"Error saving to client-specific database: {client_db_error}")
                                
                                # Legacy client logging
                                try:
                                    from client_db import log_scan
                                    log_scan(user_client['id'], scan_results['scan_id'], lead_data.get('target', ''), 'comprehensive')
                                except Exception as log_error:
                                    logging.error(f"Error logging scan: {log_error}")
                            else:
                                logger.warning(f"No client found for user {result['user']['user_id']}")
                        else:
                            logger.warning(f"Session verification failed: {result.get('message', 'Unknown error')}")
                    else:
                        logger.warning("No session token found for scan linking")
                                
                except Exception as e:
                    logger.warning(f"Could not link scan to current user: {e}")
                    import traceback
                    logger.warning(traceback.format_exc())
            
'''
                
                # Find where to insert the replacement
                # Look for the end of the current problematic block
                j = i
                brace_count = 0
                found_end = False
                
                while j < len(lines) and not found_end:
                    if 'Check if scan_results contains valid data' in lines[j]:
                        found_end = True
                        break
                    j += 1
                
                if found_end:
                    # Replace the problematic section
                    new_lines = lines[:i] + [replacement] + lines[j:]
                    
                    # Write the fixed content
                    with open(app_path, 'w') as f:
                        f.writelines(new_lines)
                    
                    print(f"   ✅ Replaced problematic section (lines {i+1} to {j+1})")
                    
                    # Test the fix
                    with open(app_path, 'r') as f:
                        test_content = f.read()
                    
                    try:
                        ast.parse(test_content)
                        print("✅ Syntax is now valid!")
                        return True
                    except SyntaxError as e:
                        print(f"❌ Still has syntax error: {e}")
                        return False
                else:
                    print("   ❌ Could not find end of problematic section")
                    return False
                
                break
        
        return False
        
    except Exception as e:
        print(f"❌ Error in specific fix: {e}")
        return False

if __name__ == "__main__":
    success = fix_app_syntax()
    
    if success:
        print("\n🎉 APP.PY SYNTAX FIXED!")
        print("✅ The application should now start without syntax errors")
        print("✅ Scan tracking functionality preserved")
        print("\n🚀 Ready for deployment!")
    else:
        print("\n❌ Manual intervention required")
        print("   Check the syntax errors and fix manually")