#!/usr/bin/env python3
"""
Test app.py syntax without importing dependencies
"""

import ast
import sys

def check_syntax(filename):
    """Check Python syntax of a file"""
    try:
        with open(filename, 'r') as f:
            content = f.read()
        
        # Parse the AST to check syntax
        ast.parse(content)
        print(f"✅ {filename} syntax is valid")
        return True
        
    except SyntaxError as e:
        print(f"❌ Syntax error in {filename}:")
        print(f"   Line {e.lineno}: {e.text.strip() if e.text else 'Unknown'}")
        print(f"   Error: {e.msg}")
        return False
    except Exception as e:
        print(f"❌ Error checking {filename}: {e}")
        return False

if __name__ == "__main__":
    files_to_check = [
        'app.py',
        'client_db.py',
        'scanner_deployment.py'
    ]
    
    all_valid = True
    for filename in files_to_check:
        try:
            if not check_syntax(filename):
                all_valid = False
        except FileNotFoundError:
            print(f"⚠️ File not found: {filename}")
    
    if all_valid:
        print("\n🎉 All checked files have valid syntax!")
    else:
        print("\n❌ Some files have syntax errors")
        sys.exit(1)