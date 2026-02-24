"""
Test Odoo Integration - Force Reload
"""

import sys
import os
from pathlib import Path

# Force reload .env file
from dotenv import load_dotenv
env_path = Path(__file__).parent / '.env'
load_dotenv(env_path, override=True)

# NOW import the Odoo service (after .env is loaded)
from src.services.odoo_service import OdooService

print("=" * 70)
print("ELYX - ODOO INTEGRATION TEST")
print("=" * 70)
print()

# Show configuration
print("Configuration from .env:")
print(f"  ODOO_URL: {os.getenv('ODOO_URL')}")
print(f"  ODOO_DB: {os.getenv('ODOO_DB')}")
print(f"  ODOO_USERNAME: {os.getenv('ODOO_USERNAME')}")
print(f"  ODOO_PASSWORD: {'*' * len(os.getenv('ODOO_PASSWORD', ''))}")
print()

try:
    print("Connecting to Odoo...")
    print()
    
    service = OdooService()
    
    if service.authenticated:
        print("[OK] Authenticated successfully!")
        print(f"   User ID: {service.uid}")
        print(f"   URL: {service.url}")
        print(f"   Database: {service.db}")
        print()
        
        # Get account summary
        print("ACCOUNT SUMMARY")
        print("-" * 70)
        summary = service.get_account_summary()
        
        print(f"Revenue This Week: ${summary['revenue_this_week']:.2f}")
        print(f"Revenue This Month: ${summary['revenue_this_month']:.2f}")
        print(f"Unpaid Invoices: {summary['unpaid_invoices_count']} (${summary['unpaid_invoices_total']:.2f})")
        print(f"Overdue Invoices: {summary['overdue_invoices_count']} (${summary['overdue_invoices_total']:.2f})")
        
        if summary['overdue_invoices']:
            print()
            print("[WARNING] OVERDUE INVOICES:")
            for inv in summary['overdue_invoices'][:3]:
                partner = inv.get('partner_id', ['Unknown', ''])[1] if inv.get('partner_id') else 'Unknown'
                print(f"  - {inv.get('name', 'N/A')}: ${inv.get('amount_residual', 0):.2f} ({partner})")
        
        print()
        print("=" * 70)
        print("[OK] ODOO INTEGRATION WORKING!")
        print("=" * 70)
        
    else:
        print("[ERROR] Authentication failed")
        print(f"URL: {service.url}")
        print(f"DB: {service.db}")
        print(f"Username: {service.username}")
        
except Exception as e:
    print(f"[ERROR] {e}")
    print()
    print("Troubleshooting:")
    print("1. Check Odoo URL is correct")
    print("2. Verify database name")
    print("3. Check username/password")
    print("4. Ensure Odoo user has API access")

print()
print("=" * 70)
