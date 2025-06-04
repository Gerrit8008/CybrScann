#!/usr/bin/env python3
"""
Safe restructuring script for CybrScann-main that preserves scan report functionality

This script:
1. Creates comprehensive backups
2. Sets up the modular scan processor first
3. Integrates the scan processor with existing code
4. Tests that scan functionality is maintained
5. Only then proceeds with the full restructuring

This ensures that critical scan report functionality is preserved throughout the process.
"""

import os
import sys
import subprocess
import shutil
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

def create_comprehensive_backup():
    """Create a comprehensive backup of the entire project"""
    timestamp = int(time.time())
    backup_dir = f"../CybrScann-backup-{timestamp}"
    
    print(f"Creating comprehensive backup at {backup_dir}...")
    
    if not os.path.exists("../"):
        os.makedirs("../", exist_ok=True)
    
    if not run_command(f"cp -r . {backup_dir}", "Creating backup"):
        print("❌ Backup failed, aborting.")
        sys.exit(1)
    
    print(f"✅ Comprehensive backup created at {backup_dir}")
    
    # Create a restore script in the backup
    restore_script = f"""#!/bin/bash
echo "Restoring CybrScann-main from backup..."
rsync -av --delete {backup_dir}/ /home/ggrun/CybrScann-main/
echo "Restoration complete!"
"""
    
    with open(f"{backup_dir}/restore.sh", "w") as f:
        f.write(restore_script)
    
    os.chmod(f"{backup_dir}/restore.sh", 0o755)
    
    print(f"✅ Created restore script at {backup_dir}/restore.sh")
    return backup_dir

def run_with_verification(step_name, command, verification_command=None):
    """Run a command with verification"""
    print_header(f"Step: {step_name}")
    
    success = run_command(command, f"Running {step_name}")
    if not success:
        print(f"❌ {step_name} failed")
        return False
    
    if verification_command:
        print(f"\nVerifying {step_name}...")
        success = run_command(verification_command, "Verification")
        if not success:
            print(f"❌ Verification of {step_name} failed")
            return False
    
    return True

def confirm_continue():
    """Ask the user if they want to continue"""
    response = input("\nDo you want to continue with the next step? (y/n): ")
    return response.lower() in ['y', 'yes']

def main():
    """Main function to safely restructure the codebase"""
    print_header("Starting Safe Restructuring of CybrScann-main")
    
    # Step 1: Create comprehensive backup
    backup_dir = create_comprehensive_backup()
    print(f"If anything goes wrong, you can restore from: {backup_dir}")
    
    # Step 2: Set up the modular scan processor
    if not os.path.exists("scanner"):
        os.makedirs("scanner", exist_ok=True)
    
    if not run_with_verification(
        "Set up modular scan processor", 
        "python3 test_scan_processor.py",
        "ls -la scanner/data_processor.py"
    ):
        print("❌ Failed to set up modular scan processor, aborting.")
        sys.exit(1)
    
    if not confirm_continue():
        print("Aborting the process. No changes have been made.")
        sys.exit(0)
    
    # Step 3: Integrate scan processor with existing code
    if not run_with_verification(
        "Integrate scan processor", 
        "python3 integrate_scan_processor.py",
        "python3 test_scan_processor.py"
    ):
        print("❌ Failed to integrate scan processor, aborting.")
        sys.exit(1)
    
    if not confirm_continue():
        print("Aborting the process. Only scan processor changes have been applied.")
        sys.exit(0)
    
    # Step 4: Split client_db.py
    if not run_with_verification(
        "Split client_db.py", 
        "python3 split_client_db.py",
        "ls -la db/"
    ):
        print("❌ Failed to split client_db.py, aborting.")
        sys.exit(1)
    
    if not confirm_continue():
        print("Aborting further splitting. client_db.py has been split.")
        sys.exit(0)
    
    # Step 5: Split app.py
    if not run_with_verification(
        "Split app.py", 
        "python3 split_app.py",
        "ls -la app/"
    ):
        print("❌ Failed to split app.py, aborting.")
        sys.exit(1)
    
    if not confirm_continue():
        print("Aborting further splitting. app.py and client_db.py have been split.")
        sys.exit(0)
    
    # Step 6: Split scan.py
    if not run_with_verification(
        "Split scan.py", 
        "python3 split_scan.py",
        "ls -la scanner/"
    ):
        print("❌ Failed to split scan.py, aborting.")
        sys.exit(1)
    
    # Step 7: Apply the changes
    print_header("Finalizing Changes")
    print("""
IMPORTANT: This step will replace the original files with the new modular versions.
Make sure all previous steps completed successfully before proceeding.
    """)
    
    if not confirm_continue():
        print("Aborting finalization. The restructured files exist but haven't replaced the originals.")
        sys.exit(0)
    
    # Apply the changes
    apply_commands = [
        "mv -v client_db.py.new client_db.py",
        "mv -v app.py.new app.py", 
        "mv -v scan.py.new scan.py"
    ]
    
    for cmd in apply_commands:
        success = run_command(cmd, f"Running: {cmd}")
        if not success:
            print(f"❌ Failed to execute: {cmd}")
            print(f"Please restore from backup at: {backup_dir}")
            sys.exit(1)
    
    # Run a final test
    if not run_with_verification(
        "Final verification of scan processor", 
        "python3 test_scan_processor.py"
    ):
        print("❌ Final verification failed.")
        print(f"Please restore from backup at: {backup_dir}")
        sys.exit(1)
    
    print_header("Restructuring Completed Successfully")
    print(f"""
The CybrScann-main codebase has been successfully restructured into a modular format.
All files have been split into smaller, focused modules organized by functionality.

Most importantly, the scan report functionality has been preserved through this process.

If you encounter any issues:
1. Restore from the backup at: {backup_dir}/restore.sh
2. Read the SCAN_REPORT_ARCHITECTURE.md file for details on the scan report system

To verify everything works correctly, start the application and test generating reports.
    """)

if __name__ == "__main__":
    main()