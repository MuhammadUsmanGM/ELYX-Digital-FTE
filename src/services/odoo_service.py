import xmlrpc.client
import os
import logging
from datetime import datetime
from pathlib import Path

class OdooService:
    """
    Service for interacting with Odoo Accounting via XML-RPC
    """
    def __init__(self):
        self.url = os.getenv('ODOO_URL', 'http://localhost:8069')
        self.db = os.getenv('ODOO_DB', 'elyx_accounting')
        self.username = os.getenv('ODOO_USERNAME', 'admin')
        self.password = os.getenv('ODOO_PASSWORD')
        self.logger = logging.getLogger(__name__)
        self.uid = None

    def authenticate(self):
        """Authenticate with Odoo and get UID"""
        try:
            common = xmlrpc.client.ServerProxy(f'{self.url}/xmlrpc/2/common')
            self.uid = common.authenticate(self.db, self.username, self.password, {})
            if self.uid:
                self.logger.info(f"Odoo authenticated successfully (UID: {self.uid})")
                return True
            else:
                self.logger.warning("Odoo authentication failed")
                return False
        except Exception as e:
            self.logger.error(f"Error authenticating with Odoo: {e}")
            return False

    def get_object_proxy(self):
        """Get the Odoo object proxy for making calls"""
        if not self.uid:
            if not self.authenticate():
                return None
        return xmlrpc.client.ServerProxy(f'{self.url}/xmlrpc/2/object')

    def get_recent_invoices(self, limit=10):
        """Fetch recent customer invoices"""
        models = self.get_object_proxy()
        if not models:
            return []
        
        try:
            # account.move is the model for invoices in Odoo 13+
            invoices = models.execute_kw(self.db, self.uid, self.password, 
                'account.move', 'search_read',
                [[['move_type', '=', 'out_invoice'], ['state', '=', 'posted']]],
                {'fields': ['name', 'partner_id', 'amount_total', 'invoice_date', 'payment_state'], 'limit': limit}
            )
            return invoices
        except Exception as e:
            self.logger.error(f"Error fetching invoices: {e}")
            return []

    def create_briefing_data(self):
        """Generate a summary for the CEO briefing"""
        models = self.get_object_proxy()
        if not models:
            return None

        try:
            # Get total revenue for the current month
            today = datetime.now()
            first_day = today.replace(day=1).strftime('%Y-%m-%d')
            
            invoices = models.execute_kw(self.db, self.uid, self.password,
                'account.move', 'search_read',
                [[['move_type', '=', 'out_invoice'], ['invoice_date', '>=', first_day], ['state', '=', 'posted']]],
                {'fields': ['amount_total']}
            )
            
            total_revenue = sum(inv['amount_total'] for inv in invoices)
            
            # Get pending payments
            pending = models.execute_kw(self.db, self.uid, self.password,
                'account.move', 'search_count',
                [[['move_type', '=', 'out_invoice'], ['payment_state', '!=', 'paid'], ['state', '=', 'posted']]]
            )

            return {
                'month_revenue': total_revenue,
                'pending_invoices_count': pending,
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            self.logger.error(f"Error creating briefing data: {e}")
            return None
