#!/usr/bin/env python3
"""
Master script to restructure the CybrScann-main codebase by splitting large files
"""
import os
import sys
import subprocess
import time

def print_header(message):
    """Print a header message"""
    print("\n" + "=" * 80)
    print(f" {message}")
    print("=" * 80)

def run_command(command, description=None):
    """Run a command and print its output"""
    if description:
        print(f"\n--- {description} ---")
    
    try:
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            shell=True,
            universal_newlines=True
        )
        
        for line in process.stdout:
            print(line, end="")
        
        process.wait()
        
        if process.returncode != 0:
            print(f"❌ Command failed with return code {process.returncode}")
            return False
        
        return True
    except Exception as e:
        print(f"❌ Error running command: {str(e)}")
        return False

def backup_project():
    """Create a backup of the entire project"""
    backup_dir = f"../CybrScann-backup-{int(time.time())}"
    print(f"Creating backup at {backup_dir}...")
    
    if not run_command(f"cp -r . {backup_dir}", "Creating backup"):
        print("❌ Backup failed, aborting.")
        sys.exit(1)
    
    print(f"✅ Backup created at {backup_dir}")

def split_files():
    """Run all the file splitting scripts"""
    scripts = [
        {"file": "./split_client_db.py", "description": "Splitting client_db.py into modules"},
        {"file": "./split_app.py", "description": "Splitting app.py into modules"},
        {"file": "./split_scan.py", "description": "Splitting scan.py into modules"}
    ]
    
    for script in scripts:
        print_header(script["description"])
        if not run_command(f"python3 {script['file']}", script["description"]):
            print(f"❌ Failed to run {script['file']}")
            return False
    
    return True

def verify_structure():
    """Verify the new directory structure"""
    print_header("Verifying new directory structure")
    
    expected_dirs = ["app", "app/routes", "db", "scanner"]
    for directory in expected_dirs:
        if not os.path.isdir(directory):
            print(f"❌ Directory {directory} not found")
            return False
        print(f"✅ Directory {directory} exists")
    
    return True

def update_imports():
    """Create a script to update imports in other files"""
    update_imports_script = """#!/usr/bin/env python3
\"\"\"
Script to update import statements to use the new modular structure
\"\"\"
import os
import re

def update_file_imports(file_path):
    \"\"\"Update imports in a single file\"\"\"
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Replace direct imports from the monolithic files
    replacements = [
        (r'from client_db import ([^\\n]+)', r'from db import \\1'),
        (r'import client_db', r'import db'),
        (r'from scan import ([^\\n]+)', r'from scanner import \\1'),
        (r'import scan', r'import scanner')
    ]
    
    modified = False
    for pattern, replacement in replacements:
        if re.search(pattern, content):
            content = re.sub(pattern, replacement, content)
            modified = True
    
    if modified:
        with open(file_path, 'w') as f:
            f.write(content)
        print(f"✅ Updated imports in {file_path}")
        return True
    return False

def main():
    \"\"\"Update imports in all Python files\"\"\"
    print("Updating import statements in Python files...")
    
    # Get all Python files except in the restructured modules
    excluded_dirs = ['db', 'app', 'scanner', '__pycache__']
    python_files = []
    
    for root, dirs, files in os.walk('.'):
        dirs[:] = [d for d in dirs if d not in excluded_dirs]
        for file in files:
            if file.endswith('.py'):
                python_files.append(os.path.join(root, file))
    
    # Update imports in each file
    updated_files = 0
    for file_path in python_files:
        if update_file_imports(file_path):
            updated_files += 1
    
    print(f"\\n✅ Updated imports in {updated_files} files")

if __name__ == "__main__":
    main()
"""
    
    with open("update_imports.py", "w") as f:
        f.write(update_imports_script)
    
    os.chmod("update_imports.py", 0o755)
    print("✅ Created update_imports.py script")
    
    return run_command("python3 update_imports.py", "Updating imports in Python files")

def finalize_changes():
    """Replace the original files with the new ones"""
    print_header("Finalizing changes")
    
    commands = [
        "mv app.py.new app.py",
        "mv scan.py.new scan.py",
        "mv client_db.py.new client_db.py"
    ]
    
    for command in commands:
        if not run_command(command, f"Executing: {command}"):
            return False
    
    return True

def create_readme():
    """Create a README file explaining the new structure"""
    readme_content = """# CybrScann-main Restructured

## New Directory Structure

The codebase has been reorganized into a modular structure for better maintainability:

### Database Module (`db/`)
- `db/core.py` - Core database functionality 
- `db/client.py` - Client management functions
- `db/scanner.py` - Scanner configuration functions
- `db/scan_results.py` - Scan results processing
- `db/dashboard.py` - Dashboard data functions
- `db/audit.py` - Audit logging functions
- `db/auth.py` - Authentication functions

### Application Module (`app/`)
- `app/core.py` - Application initialization and configuration
- `app/scan_engine.py` - Scanning functionality
- `app/utils.py` - Utility functions
- `app/email.py` - Email functionality
- `app/routes/index.py` - Main routes
- `app/routes/api.py` - API endpoints

### Scanner Module (`scanner/`)
- `scanner/core.py` - Core scanning functionality
- `scanner/network.py` - Network scanning
- `scanner/web.py` - Web scanning
- `scanner/dns.py` - DNS scanning
- `scanner/system.py` - System scanning
- `scanner/risk.py` - Risk assessment

## Entry Points

- `app.py` - Main application entry point (imports from app)
- `wsgi.py` - WSGI entry point for production deployment

## Backwards Compatibility

The original files (`client_db.py`, `app.py`, `scan.py`) now act as proxies that import from the new modular structure. This ensures backwards compatibility with existing code.
"""
    
    with open("MODULAR_STRUCTURE.md", "w") as f:
        f.write(readme_content)
    
    print("✅ Created MODULAR_STRUCTURE.md")

def main():
    """Main function to restructure the codebase"""
    print_header("Starting CybrScann-main Codebase Restructuring")
    
    # Create backup
    backup_project()
    
    # Split files
    if not split_files():
        print("❌ File splitting failed, aborting.")
        return
    
    # Verify structure
    if not verify_structure():
        print("❌ Structure verification failed, aborting.")
        return
    
    # Update imports
    if not update_imports():
        print("❌ Import updates failed, aborting.")
        return
    
    # Finalize changes
    if not finalize_changes():
        print("❌ Finalizing changes failed, aborting.")
        return
    
    # Create README
    create_readme()
    
    print_header("Restructuring Complete")
    print("""
The CybrScann-main codebase has been successfully restructured into a modular format.
Key files have been split into smaller, focused modules organized by functionality.

Next steps:
1. Run tests to verify everything works correctly
2. Review the new structure in MODULAR_STRUCTURE.md
3. Start using the new modular imports in new code

For more information, see the MODULAR_STRUCTURE.md file.
""")

if __name__ == "__main__":
    main()