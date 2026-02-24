"""
Odoo Accounting Integration Service
Connects to Odoo via JSON-RPC API with API Key authentication
For: Invoice monitoring, Payment tracking, Revenue reporting

Reference: https://www.odoo.com/documentation/19.0/developer/reference/external/external_api.html
"""

import requests
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from pathlib import Path
import os

logger = logging.getLogger(__name__)


class OdooService:
    """
    Odoo JSON-RPC API Service with API Key authentication
    """
    
    def __init__(self):
        """Initialize Odoo service with configuration from .env"""
        self.url = os.getenv('ODOO_URL', 'https://elyx-ai.odoo.com')
        self.db = os.getenv('ODOO_DB', 'elyx-ai')
        self.username = os.getenv('ODOO_USERNAME', 'elyx.ai.employ@gmail.com')
        self.password = os.getenv('ODOO_PASSWORD', '')
        self.api_key = os.getenv('ODOO_API_KEY', '')  # API Key for better security
        self.company_id = int(os.getenv('ODOO_COMPANY_ID', '1'))
        self.currency_id = int(os.getenv('ODOO_CURRENCY_ID', '2'))
        
        self.uid = None  # User ID after authentication
        self.authenticated = False
        self.session_id = None
        
        # Use API key if available, otherwise use password
        self.auth_method = 'api_key' if self.api_key else 'password'
        logger.info(f"Odoo auth method: {self.auth_method.upper()}")
        
        # Authenticate on initialization
        self.authenticate()
    
    def _json_rpc(self, endpoint: str, method: str, params: Dict = None) -> Dict:
        """
        Make JSON-RPC call to Odoo API with proper authentication
        
        Args:
            endpoint: API endpoint (e.g., '/jsonrpc')
            method: RPC method name
            params: Method parameters
            
        Returns:
            JSON-RPC response
        """
        url = f"{self.url}{endpoint}"
        
        # Build headers with session cookie if authenticated
        headers = {
            "Content-Type": "application/json"
        }
        
        # Add session cookie if we have one
        cookies = {}
        if self.session_id:
            cookies['session_id'] = self.session_id
        
        payload = {
            "jsonrpc": "2.0",
            "method": method,
            "params": params or {},
            "id": 1
        }
        
        try:
            response = requests.post(url, json=payload, headers=headers, cookies=cookies, timeout=30)
            response.raise_for_status()
            result = response.json()
            
            # Save session cookie from response
            if 'session_id' in response.cookies:
                self.session_id = response.cookies['session_id']
            
            if "error" in result:
                error = result["error"]
                # If session expired, try to re-authenticate
                if error.get('code') == 100 or 'Session Expired' in str(error):
                    logger.warning("Session expired, re-authenticating...")
                    if self.authenticate():
                        # Retry the request
                        return self._json_rpc(endpoint, method, params)
                
                logger.error(f"Odoo API Error: {error}")
                raise Exception(f"Odoo API Error: {error.get('message', 'Unknown error')}")
            
            return result.get("result", {})
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Network error calling Odoo: {e}")
            raise
    
    def authenticate(self) -> bool:
        """
        Authenticate with Odoo using API Key (preferred) or password
        
        Returns:
            True if authentication successful
        """
        try:
            url = f"{self.url}/web/session/authenticate"
            
            # Use API key if available, otherwise use password
            if self.api_key:
                # API Key authentication (more secure)
                logger.info("Authenticating with API Key...")
                auth_password = self.api_key
            else:
                # Password authentication (fallback)
                logger.info("Authenticating with Password...")
                auth_password = self.password
            
            payload = {
                "jsonrpc": "2.0",
                "method": "call",
                "params": {
                    "db": self.db,
                    "login": self.username,
                    "password": auth_password,
                    "context": {}
                },
                "id": 1
            }
            
            headers = {"Content-Type": "application/json"}
            
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            response.raise_for_status()
            result = response.json()
            
            if result.get("result", {}).get("uid"):
                self.uid = result["result"]["uid"]
                self.authenticated = True
                
                # Save session cookie
                if 'session_id' in response.cookies:
                    self.session_id = response.cookies['session_id']
                
                logger.info(f"[OK] Odoo authenticated as user ID: {self.uid}")
                logger.info(f"Auth method: {self.auth_method.upper()}")
                logger.info(f"Session ID: {self.session_id[:20] if self.session_id else 'N/A'}...")
                return True
            else:
                logger.error("[ERROR] Odoo authentication failed - no UID returned")
                return False
                
        except Exception as e:
            logger.error(f"[ERROR] Odoo authentication error: {e}")
            self.authenticated = False
            return False
    
    def execute_kw(self, model: str, method: str, args: List = None, kwargs: Dict = None) -> Any:
        """
        Execute a method on an Odoo model using Odoo 19+ API format
        
        Args:
            model: Odoo model name (e.g., 'account.move')
            method: Method to call (e.g., 'search_read')
            args: Positional arguments
            kwargs: Keyword arguments
            
        Returns:
            Method result
        """
        if not self.authenticated:
            if not self.authenticate():
                raise Exception("Not authenticated to Odoo")
        
        # Odoo 19+ JSON-RPC format for execute_kw
        params = {
            "service": "object",
            "method": "execute_kw",
            "args": [
                self.db,
                self.uid,
                self.password,
                model,
                method,
                args or [],
                kwargs or {}
            ]
        }
        
        result = self._json_rpc("/jsonrpc", "call", params)
        return result
    
    def get_invoices(self, domain: List = None, fields: List = None, limit: int = 50) -> List[Dict]:
        """
        Get invoices from Odoo
        
        Args:
            domain: Search domain
            fields: Fields to return
            limit: Maximum number of records
            
        Returns:
            List of invoice records
        """
        if domain is None:
            domain = [['move_type', 'in', ['out_invoice', 'in_invoice']]]
        
        if fields is None:
            fields = [
                'id', 'name', 'move_type', 'state', 'partner_id',
                'invoice_date', 'invoice_date_due', 'amount_total',
                'amount_residual', 'currency_id', 'company_id', 'payment_state'
            ]
        
        try:
            invoices = self.execute_kw(
                'account.move',
                'search_read',
                [domain, fields],
                {'limit': limit, 'order': 'invoice_date desc'}
            )
            
            logger.info(f"Retrieved {len(invoices)} invoices from Odoo")
            return invoices
            
        except Exception as e:
            logger.error(f"Error getting invoices: {e}")
            return []
    
    def get_unpaid_invoices(self) -> List[Dict]:
        """Get all unpaid customer invoices"""
        domain = [
            ['move_type', '=', 'out_invoice'],
            ['state', '=', 'posted'],
            ['payment_state', '!=', 'paid'],
            ['company_id', '=', self.company_id]
        ]
        return self.get_invoices(domain=domain)
    
    def get_overdue_invoices(self) -> List[Dict]:
        """Get overdue customer invoices"""
        today = datetime.now().strftime('%Y-%m-%d')
        domain = [
            ['move_type', '=', 'out_invoice'],
            ['state', '=', 'posted'],
            ['payment_state', '!=', 'paid'],
            ['invoice_date_due', '<', today],
            ['company_id', '=', self.company_id]
        ]
        return self.get_invoices(domain=domain)
    
    def get_revenue_this_week(self) -> float:
        """Get total revenue for current week"""
        today = datetime.now()
        start_of_week = (today - timedelta(days=today.weekday())).strftime('%Y-%m-%d')
        
        domain = [
            ['move_type', '=', 'out_invoice'],
            ['state', '=', 'posted'],
            ['invoice_date', '>=', start_of_week],
            ['company_id', '=', self.company_id]
        ]
        
        invoices = self.get_invoices(domain=domain)
        return sum(inv.get('amount_total', 0) for inv in invoices)
    
    def get_revenue_this_month(self) -> float:
        """Get total revenue for current month"""
        today = datetime.now()
        start_of_month = today.replace(day=1).strftime('%Y-%m-%d')
        
        domain = [
            ['move_type', '=', 'out_invoice'],
            ['state', '=', 'posted'],
            ['invoice_date', '>=', start_of_month],
            ['company_id', '=', self.company_id]
        ]
        
        invoices = self.get_invoices(domain=domain)
        return sum(inv.get('amount_total', 0) for inv in invoices)
    
    def get_account_summary(self) -> Dict[str, Any]:
        """Get comprehensive accounting summary for CEO briefing"""
        unpaid = self.get_unpaid_invoices()
        overdue = self.get_overdue_invoices()
        revenue_week = self.get_revenue_this_week()
        revenue_month = self.get_revenue_this_month()
        
        return {
            'revenue_this_week': revenue_week,
            'revenue_this_month': revenue_month,
            'unpaid_invoices_count': len(unpaid),
            'unpaid_invoices_total': sum(inv.get('amount_residual', 0) for inv in unpaid),
            'overdue_invoices_count': len(overdue),
            'overdue_invoices_total': sum(inv.get('amount_residual', 0) for inv in overdue),
            'overdue_invoices': overdue[:5],
            'generated_at': datetime.now().isoformat()
        }


# Singleton instance
_odoo_service: Optional[OdooService] = None


def get_odoo_service() -> Optional[OdooService]:
    """Get or create Odoo service singleton"""
    global _odoo_service
    if _odoo_service is None:
        _odoo_service = OdooService()
    return _odoo_service


def test_odoo_connection():
    """Test Odoo connection"""
    print("=" * 70)
    print("ODOO CONNECTION TEST")
    print("=" * 70)
    
    try:
        service = get_odoo_service()
        
        if not service.authenticated:
            print("[ERROR] Failed to authenticate with Odoo")
            print(f"URL: {service.url}")
            print(f"DB: {service.db}")
            print(f"Username: {service.username}")
            return False
        
        print(f"[OK] Authenticated successfully!")
        print(f"   User ID: {service.uid}")
        print(f"   URL: {service.url}")
        print(f"   Database: {service.db}")
        
        print("\nACCOUNT SUMMARY")
        print("-" * 70)
        summary = service.get_account_summary()
        
        print(f"Revenue This Week: ${summary['revenue_this_week']:.2f}")
        print(f"Revenue This Month: ${summary['revenue_this_month']:.2f}")
        print(f"Unpaid Invoices: {summary['unpaid_invoices_count']} (${summary['unpaid_invoices_total']:.2f})")
        print(f"Overdue Invoices: {summary['overdue_invoices_count']} (${summary['overdue_invoices_total']:.2f})")
        
        print("\n" + "=" * 70)
        print("[OK] ODOO INTEGRATION WORKING!")
        print("=" * 70)
        
        return True
        
    except Exception as e:
        print(f"\n[ERROR] {e}")
        return False


if __name__ == "__main__":
    test_odoo_connection()
