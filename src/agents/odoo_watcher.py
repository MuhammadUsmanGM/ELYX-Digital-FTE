"""
Odoo Accounting Watcher
Monitors Odoo for:
- New invoices
- Overdue invoices
- Payment confirmations
- Accounting anomalies

Creates action files in /Needs_Action for Claude to process
"""

from ..base_watcher import BaseWatcher
from ..services.odoo_service import get_odoo_service
from pathlib import Path
from datetime import datetime, timedelta
import os
import time


class OdooWatcher(BaseWatcher):
    """
    Monitors Odoo accounting for important events
    """
    
    def __init__(self, vault_path: str):
        interval = int(os.getenv('ODOO_CHECK_INTERVAL', 3600))
        super().__init__(vault_path, check_interval=interval, use_chrome_profile=False)
        self.odoo = get_odoo_service()
        self.processed_invoices = self._load_processed_ids("odoo")
        self.last_revenue_check = None
    
    def check_for_updates(self) -> list:
        """
        Check Odoo for accounting events that need attention
        
        Returns:
            List of items to process
        """
        updates = []
        
        if not self.odoo or not self.odoo.authenticated:
            self.logger.warning("Odoo not authenticated, skipping check")
            return updates
        
        try:
            # Check for overdue invoices (HIGH PRIORITY)
            overdue = self._check_overdue_invoices()
            updates.extend(overdue)
            
            # Check for new unpaid invoices
            new_invoices = self._check_new_invoices()
            updates.extend(new_invoices)
            
            # Check for payments received
            payments = self._check_payments()
            updates.extend(payments)
            
            # Weekly revenue check (for CEO briefing)
            revenue_update = self._check_weekly_revenue()
            if revenue_update:
                updates.append(revenue_update)
            
        except Exception as e:
            self.logger.error(f"Error checking Odoo: {e}")
        
        return updates
    
    def _check_overdue_invoices(self) -> list:
        """Check for overdue customer invoices"""
        updates = []
        
        try:
            overdue = self.odoo.get_overdue_invoices()
            
            for inv in overdue:
                inv_id = inv.get('id')
                if inv_id not in self.processed_invoices:
                    self.processed_invoices.add(inv_id)
                    
                    partner = inv.get('partner_id', ['Unknown', ''])[1] if inv.get('partner_id') else 'Unknown'
                    amount = inv.get('amount_residual', 0)
                    due_date = inv.get('invoice_date_due', 'Unknown')
                    
                    updates.append({
                        'type': 'overdue_invoice',
                        'priority': 'high',
                        'invoice_id': inv_id,
                        'invoice_name': inv.get('name', 'N/A'),
                        'partner': partner,
                        'amount': amount,
                        'due_date': due_date,
                        'days_overdue': self._calculate_days_overdue(due_date),
                        'timestamp': datetime.now().isoformat()
                    })
                    
                    self.logger.warning(f"Overdue invoice detected: {inv.get('name')} - ${amount:.2f} ({partner})")

            if updates:
                self._save_processed_ids("odoo", self.processed_invoices)

        except Exception as e:
            self.logger.error(f"Error checking overdue invoices: {e}")
        
        return updates
    
    def _check_new_invoices(self) -> list:
        """Check for new vendor invoices (bills we need to pay)"""
        updates = []
        
        try:
            # Get vendor bills from last 24 hours
            yesterday = (datetime.now() - timedelta(hours=24)).strftime('%Y-%m-%d')
            
            domain = [
                ['move_type', '=', 'in_invoice'],
                ['state', '=', 'posted'],
                ['invoice_date', '>=', yesterday],
                ['payment_state', '!=', 'paid']
            ]
            
            bills = self.odoo.get_invoices(domain=domain)
            
            for bill in bills:
                bill_id = bill.get('id')
                if bill_id not in self.processed_invoices:
                    self.processed_invoices.add(bill_id)
                    
                    partner = bill.get('partner_id', ['Unknown', ''])[1] if bill.get('partner_id') else 'Unknown'
                    amount = bill.get('amount_total', 0)
                    due_date = bill.get('invoice_date_due', 'Unknown')
                    
                    updates.append({
                        'type': 'vendor_bill',
                        'priority': 'medium',
                        'invoice_id': bill_id,
                        'invoice_name': bill.get('name', 'N/A'),
                        'vendor': partner,
                        'amount': amount,
                        'due_date': due_date,
                        'timestamp': datetime.now().isoformat()
                    })
                    
                    self.logger.info(f"New vendor bill: {bill.get('name')} - ${amount:.2f} ({partner})")

            if updates:
                self._save_processed_ids("odoo", self.processed_invoices)

        except Exception as e:
            self.logger.error(f"Error checking new invoices: {e}")
        
        return updates
    
    def _check_payments(self) -> list:
        """Check for recently paid invoices (received payments in last 24 hours)"""
        updates = []

        try:
            yesterday = (datetime.now() - timedelta(hours=24)).strftime('%Y-%m-%d')

            # Query customer invoices that were paid recently
            domain = [
                ['move_type', '=', 'out_invoice'],
                ['payment_state', 'in', ['paid', 'in_payment']],
                ['write_date', '>=', yesterday],
            ]

            paid_invoices = self.odoo.get_invoices(domain=domain)

            for inv in paid_invoices:
                inv_id = f"payment_{inv.get('id')}"
                if inv_id not in self.processed_invoices:
                    self.processed_invoices.add(inv_id)

                    partner = inv.get('partner_id', ['Unknown', ''])[1] if inv.get('partner_id') else 'Unknown'
                    amount = inv.get('amount_total', 0)

                    updates.append({
                        'type': 'payment_received',
                        'priority': 'low',
                        'invoice_id': inv.get('id'),
                        'invoice_name': inv.get('name', 'N/A'),
                        'partner': partner,
                        'amount': amount,
                        'timestamp': datetime.now().isoformat()
                    })

                    self.logger.info(f"Payment received: {inv.get('name')} - ${amount:.2f} ({partner})")

            if updates:
                self._save_processed_ids("odoo", self.processed_invoices)

        except Exception as e:
            self.logger.error(f"Error checking payments: {e}")

        return updates
    
    def _check_weekly_revenue(self) -> dict:
        """Generate weekly revenue update for CEO briefing"""
        # Only check once per week
        today = datetime.now()
        week_key = today.strftime('%Y-W%W')
        
        if self.last_revenue_check == week_key:
            return None
        
        self.last_revenue_check = week_key
        
        try:
            revenue = self.odoo.get_revenue_this_week()
            
            return {
                'type': 'weekly_revenue',
                'priority': 'low',
                'week': week_key,
                'revenue': revenue,
                'timestamp': datetime.now().isoformat()
            }
        
        except Exception as e:
            self.logger.error(f"Error checking weekly revenue: {e}")
            return None
    
    def _calculate_days_overdue(self, due_date_str: str) -> int:
        """Calculate days overdue from due date string"""
        try:
            due_date = datetime.strptime(due_date_str, '%Y-%m-%d')
            delta = datetime.now() - due_date
            return max(0, delta.days)
        except:
            return 0
    
    def create_action_file(self, item) -> Path:
        """
        Create action file in Needs_Action folder
        
        Args:
            item: Item to create action file for
            
        Returns:
            Path to created file
        """
        item_type = item['type']
        
        if item_type == 'overdue_invoice':
            content = self._create_overdue_invoice_action(item)
        elif item_type == 'vendor_bill':
            content = self._create_vendor_bill_action(item)
        elif item_type == 'weekly_revenue':
            content = self._create_revenue_action(item)
        else:
            content = self._create_generic_action(item)
        
        filepath = self.needs_action / f'ODOO_{item_type.upper()}_{item.get("invoice_id", hash(item["timestamp"]))}.md'
        filepath.write_text(content, encoding='utf-8')
        return filepath
    
    def _create_overdue_invoice_action(self, item: dict) -> str:
        """Create action file for overdue invoice"""
        return f'''---
type: overdue_invoice
priority: {item['priority']}
status: pending
received: {item["timestamp"]}
invoice_id: {item['invoice_id']}
invoice_name: {item['invoice_name']}
customer: {item['partner']}
amount: {item['amount']:.2f}
due_date: {item['due_date']}
days_overdue: {item['days_overdue']}
---

# ⚠️ OVERDUE INVOICE ALERT

## Invoice Details
- **Invoice**: {item['invoice_name']}
- **Customer**: {item['partner']}
- **Amount Due**: ${item['amount']:.2f}
- **Due Date**: {item['due_date']}
- **Days Overdue**: {item['days_overdue']} days

## Urgency Level
{"🔴 CRITICAL" if item['days_overdue'] > 30 else "🟠 HIGH" if item['days_overdue'] > 14 else "🟡 MEDIUM"}

## Suggested Actions
- [ ] Send payment reminder email to customer
- [ ] Call customer to follow up
- [ ] Consider late fees (if applicable)
- [ ] Update cash flow forecast
- [ ] Escalate if > 30 days overdue

## Company Handbook Rules
- Invoices > 30 days overdue: Escalate to management
- Invoices > 60 days overdue: Consider collections agency
- Always maintain professional communication

---
*Generated by ELYX Odoo Monitor*
'''
    
    def _create_vendor_bill_action(self, item: dict) -> str:
        """Create action file for vendor bill"""
        return f'''---
type: vendor_bill
priority: {item['priority']}
status: pending
received: {item["timestamp"]}
invoice_id: {item['invoice_id']}
invoice_name: {item['invoice_name']}
vendor: {item['vendor']}
amount: {item['amount']:.2f}
due_date: {item['due_date']}
---

# 📄 VENDOR BILL RECEIVED

## Bill Details
- **Bill**: {item['invoice_name']}
- **Vendor**: {item['vendor']}
- **Amount**: ${item['amount']:.2f}
- **Due Date**: {item['due_date']}

## Suggested Actions
- [ ] Verify bill against purchase order
- [ ] Approve for payment
- [ ] Schedule payment (if approved)
- [ ] File for accounting records

## Approval Required
- Bills > $100: Manager approval
- Bills > $1000: Executive approval

---
*Generated by ELYX Odoo Monitor*
'''
    
    def _create_revenue_action(self, item: dict) -> str:
        """Create action file for weekly revenue update"""
        return f'''---
type: weekly_revenue
priority: {item['priority']}
status: pending
received: {item["timestamp"]}
week: {item['week']}
revenue: {item['revenue']:.2f}
---

# 📊 WEEKLY REVENUE UPDATE

## Week {item['week']}

**Total Revenue**: ${item['revenue']:.2f}

## Suggested Actions
- [ ] Review revenue trends
- [ ] Update CEO briefing document
- [ ] Compare against weekly targets
- [ ] Identify any anomalies

## For CEO Briefing
Add this data to the Monday Morning CEO Briefing:
- Week: {item['week']}
- Revenue: ${item['revenue']:.2f}
- Compare to previous week and monthly target

---
*Generated by ELYX Odoo Monitor*
'''
    
    def _create_generic_action(self, item: dict) -> str:
        """Create generic action file"""
        return f'''---
type: {item['type']}
priority: {item.get('priority', 'medium')}
status: pending
received: {item["timestamp"]}
---

# Odoo Accounting Update

**Type**: {item['type']}

**Details**: {item}

## Suggested Actions
- [ ] Review Odoo accounting update
- [ ] Take appropriate action
- [ ] Update records if needed

---
*Generated by ELYX Odoo Monitor*
'''


def run_odoo_watcher(vault_path: str):
    """
    Convenience function to run the Odoo watcher continuously
    """
    watcher = OdooWatcher(vault_path)
    
    watcher.logger.info("Starting Odoo Watcher...")
    watcher.logger.info(f"Odoo URL: {watcher.odoo.url if watcher.odoo else 'N/A'}")
    watcher.logger.info(f"Authenticated: {watcher.odoo.authenticated if watcher.odoo else False}")
    
    while True:
        try:
            items = watcher.check_for_updates()
            for item in items:
                action_file = watcher.create_action_file(item)
                watcher.logger.info(f'Created action file: {action_file}')
        except Exception as e:
            watcher.logger.error(f'Error in Odoo Watcher: {e}')
        
        time.sleep(watcher.check_interval)


if __name__ == "__main__":
    # Test Odoo watcher
    import sys
    vault = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("obsidian_vault")
    watcher = OdooWatcher(str(vault))
    
    print(f"Odoo Authenticated: {watcher.odoo.authenticated}")
    if watcher.odoo.authenticated:
        items = watcher.check_for_updates()
        print(f"Found {len(items)} items to process")
        for item in items:
            print(f"  - {item['type']}: {item.get('invoice_name', 'N/A')}")