from src.agents.base_watcher import BaseWatcher
from src.services.odoo_service import OdooService
from pathlib import Path
from datetime import datetime
import os
import time

class OdooWatcher(BaseWatcher):
    """
    Watches Odoo for new invoices and payment status changes
    """
    def __init__(self, vault_path: str):
        interval = int(os.getenv('ODOO_CHECK_INTERVAL', 3600))
        super().__init__(vault_path, check_interval=interval)
        self.odoo = OdooService()
        self.processed_invoices = set()

    def check_for_updates(self) -> list:
        """Check Odoo for recent activity"""
        updates = []
        invoices = self.odoo.get_recent_invoices(limit=5)
        
        for inv in invoices:
            inv_id = inv['id']
            if inv_id not in self.processed_invoices:
                updates.append({
                    'type': 'new_invoice',
                    'data': inv,
                    'timestamp': datetime.now().isoformat()
                })
                self.processed_invoices.add(inv_id)
        
        return updates

    def create_action_file(self, item) -> Path:
        """Create a task in Needs_Action for the invoice"""
        inv_data = item['data']
        content = f'''---
type: accounting
source: Odoo
priority: low
status: pending
invoice_id: {inv_data["name"]}
amount: {inv_data["amount_total"]}
customer: {inv_data["partner_id"][1] if inv_data["partner_id"] else "Unknown"}
---

## New Invoice Detected in Odoo

**Invoice**: {inv_data["name"]}
**Customer**: {inv_data["partner_id"][1] if inv_data["partner_id"] else "Unknown"}
**Amount**: {inv_data["amount_total"]}
**Date**: {inv_data["invoice_date"]}
**Payment Status**: {inv_data["payment_state"]}

## Suggested Actions
- [ ] Verify invoice details
- [ ] Match with bank transaction if paid
- [ ] Archive if already reviewed manually
'''
        filepath = self.needs_action / f'ODOO_INV_{inv_data["name"].replace("/", "_")}.md'
        filepath.write_text(content, encoding='utf-8')
        return filepath
