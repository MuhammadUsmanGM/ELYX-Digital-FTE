
import sys
from pathlib import Path

# Add project root to sys.path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.services.odoo_service import OdooService
from src.config.manager import config_manager

def test_odoo():
    print("Testing Odoo Authentication...")
    service = OdooService()
    print(f"URL: {service.url}")
    print(f"DB: {service.db}")
    print(f"Username: {service.username}")
    print(f"Password set: {'Yes' if service.password else 'No'}")
    
    if service.authenticate():
        print("Success! Authenticated with Odoo.")
    else:
        print("Failed to authenticate with Odoo.")

if __name__ == "__main__":
    test_odoo()
