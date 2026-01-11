"""
Odoo ERP Connector - Open-source ERP integration.
"""

import os
import logging
from typing import Dict, List, Any
import sys
sys.path.append('..')
from ..base_connector import ERPConnector


class OdooConnector(ERPConnector):
    """Odoo ERP connector using XML-RPC API."""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        
        self.url = config.get('url') or os.getenv('ODOO_URL')
        self.database = config.get('database') or os.getenv('ODOO_DATABASE')
        self.username = config.get('username') or os.getenv('ODOO_USERNAME')
        self.password = config.get('password') or os.getenv('ODOO_PASSWORD')
        
        self.uid = None
        self.sync_count = 0
        self.entities_synced = {}
    
    async def connect(self) -> bool:
        """Connect to Odoo using XML-RPC."""
        try:
            import xmlrpc.client
            
            common = xmlrpc.client.ServerProxy(f'{self.url}/xmlrpc/2/common')
            self.uid = common.authenticate(self.database, self.username, self.password, {})
            
            if self.uid:
                self.connected = True
                self.logger.info("Connected to Odoo")
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Failed to connect to Odoo: {e}")
            return False
    
    async def disconnect(self) -> None:
        self.connected = False
        self.uid = None
    
    async def test_connection(self) -> bool:
        return self.connected and self.uid is not None
    
    async def sync_customers(self) -> Dict[str, Any]:
        """Sync customer data from Odoo."""
        try:
            import xmlrpc.client
            
            models = xmlrpc.client.ServerProxy(f'{self.url}/xmlrpc/2/object')
            customers = models.execute_kw(
                self.database, self.uid, self.password,
                'res.partner', 'search_read',
                [[['customer_rank', '>', 0]]],
                {'fields': ['name', 'email', 'phone'], 'limit': 1000}
            )
            
            self.entities_synced['customers'] = len(customers)
            self.sync_count += 1
            
            return {'success': True, 'count': len(customers), 'customers': customers}
            
        except Exception as e:
            self.logger.error(f"Failed to sync customers: {e}")
            return {'success': False, 'error': str(e)}
    
    async def sync_products(self) -> Dict[str, Any]:
        """Sync products from Odoo."""
        try:
            import xmlrpc.client
            
            models = xmlrpc.client.ServerProxy(f'{self.url}/xmlrpc/2/object')
            products = models.execute_kw(
                self.database, self.uid, self.password,
                'product.product', 'search_read',
                [[]],
                {'fields': ['name', 'list_price', 'qty_available'], 'limit': 1000}
            )
            
            self.entities_synced['products'] = len(products)
            self.sync_count += 1
            
            return {'success': True, 'count': len(products), 'products': products}
            
        except Exception as e:
            self.logger.error(f"Failed to sync products: {e}")
            return {'success': False, 'error': str(e)}
    
    async def sync_orders(self) -> Dict[str, Any]:
        """Sync orders from Odoo."""
        try:
            import xmlrpc.client
            
            models = xmlrpc.client.ServerProxy(f'{self.url}/xmlrpc/2/object')
            orders = models.execute_kw(
                self.database, self.uid, self.password,
                'sale.order', 'search_read',
                [[]],
                {'fields': ['name', 'partner_id', 'amount_total', 'state'], 'limit': 1000}
            )
            
            self.entities_synced['orders'] = len(orders)
            self.sync_count += 1
            
            return {'success': True, 'count': len(orders), 'orders': orders}
            
        except Exception as e:
            self.logger.error(f"Failed to sync orders: {e}")
            return {'success': False, 'error': str(e)}
    
    async def sync_inventory(self) -> Dict[str, Any]:
        return {'success': True, 'count': 0}
    
    async def sync_financials(self) -> Dict[str, Any]:
        return {'success': True, 'count': 0}
