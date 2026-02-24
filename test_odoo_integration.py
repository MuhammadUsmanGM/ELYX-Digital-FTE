"""
Test Odoo Integration
Verifies connection to Odoo and displays account summary
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from src.services.odoo_service import test_odoo_connection

if __name__ == "__main__":
    print("=" * 70)
    print("ELYX - ODOO INTEGRATION TEST")
    print("=" * 70)
    print()
    
    success = test_odoo_connection()
    
    if success:
        print("\n✅ Odoo integration is working!")
        print("\nNext steps:")
        print("1. Odoo watcher will monitor for invoices automatically")
        print("2. Overdue invoices will create action files in /Needs_Action")
        print("3. Weekly revenue data will be available for CEO briefing")
        print("4. All accounting data is now accessible to Claude Code")
    else:
        print("\n❌ Odoo integration failed")
        print("\nTroubleshooting:")
        print("1. Check .env file has correct Odoo credentials")
        print("2. Verify Odoo URL is accessible")
        print("3. Ensure Odoo user has API access permissions")
        print("4. Check firewall/network connectivity")
    
    print("\n" + "=" * 70)
