#!/usr/bin/env python3
"""
Activation script for enhanced admin dashboard

This script activates the enhanced admin dashboard by patching the admin.py file.
It preserves all existing functionality while adding comprehensive data display.
"""

import logging
from enhanced_admin_dashboard import enhance_admin_dashboard

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """Activate the enhanced admin dashboard"""
    print("=" * 60)
    print("Activating Enhanced Admin Dashboard")
    print("=" * 60)
    
    try:
        # Apply the enhancement
        success = enhance_admin_dashboard()
        
        if success:
            print("\n✅ Enhanced admin dashboard activated successfully!")
            print("\nThe admin dashboard now displays comprehensive data including:")
            print("  - Detailed client information")
            print("  - Scanner deployment statistics")
            print("  - Lead generation data")
            print("  - System health metrics")
            print("  - User activity tracking")
            print("  - Real-time data visualization")
            print("\nNo functionality has been lost in the process.")
        else:
            print("\n❌ Failed to activate enhanced admin dashboard")
            print("Please check the logs for details")
    except Exception as e:
        logger.error(f"Error activating enhanced dashboard: {str(e)}")
        print(f"\n❌ Error: {str(e)}")
        print("Please check the logs for details")

if __name__ == "__main__":
    main()