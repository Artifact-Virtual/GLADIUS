"""
SAP ERP Connector - Enterprise resource planning integration.
"""

import os
import logging
from typing import Dict, List, Any, Optional
import aiohttp
from datetime import datetime, timezone

import sys
sys.path.append('..')
from ..base_connector import ERPConnector


class SAPConnector(ERPConnector):
    """SAP ERP system connector using OData API."""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        
        self.api_url = config.get('api_url') or os.getenv('SAP_API_URL')
        self.client = config.get('client') or os.getenv('SAP_CLIENT')
        self.username = config.get('username') or os.getenv('SAP_USERNAME')
        self.password = config.get('password') or os.getenv('SAP_PASSWORD')
        
        self.session = None
        self.sync_count = 0
        self.entities_synced = {}
    
    async def connect(self) -> bool:
        """Connect to SAP system."""
        try:
            # Create authenticated session
            self.session = aiohttp.ClientSession(
                auth=aiohttp.BasicAuth(self.username, self.password)
            )
            
            # Test connection
            if await self.test_connection():
                self.connected = True
                self.logger.info("Connected to SAP")
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Failed to connect to SAP: {e}")
            return False
    
    async def disconnect(self) -> None:
        """Disconnect from SAP."""
        if self.session:
            await self.session.close()
            self.session = None
        self.connected = False
    
    async def test_connection(self) -> bool:
        """Test SAP connection."""
        if not self.session:
            return False
        
        try:
            async with self.session.get(f"{self.api_url}/sap/opu/odata/sap/API_BUSINESS_PARTNER") as response:
                return response.status == 200
        except Exception:
            return False
    
    async def sync_customers(self) -> Dict[str, Any]:
        """Sync customer data from SAP."""
        self.logger.info("Syncing customers from SAP...")
        
        try:
            url = f"{self.api_url}/sap/opu/odata/sap/API_BUSINESS_PARTNER/A_BusinessPartner"
            params = {
                '$filter': "BusinessPartnerCategory eq '1'",  # Customers
                '$top': 1000
            }
            
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    customers = data.get('d', {}).get('results', [])
                    
                    self.entities_synced['customers'] = len(customers)
                    self.sync_count += 1
                    self.last_sync = datetime.now(timezone.utc)
                    
                    self.logger.info(f"Synced {len(customers)} customers from SAP")
                    
                    return {
                        'success': True,
                        'count': len(customers),
                        'customers': customers
                    }
            
            return {'success': False, 'error': 'Request failed'}
            
        except Exception as e:
            self.logger.error(f"Failed to sync customers: {e}")
            return {'success': False, 'error': str(e)}
    
    async def sync_products(self) -> Dict[str, Any]:
        """Sync product data from SAP."""
        self.logger.info("Syncing products from SAP...")
        
        try:
            url = f"{self.api_url}/sap/opu/odata/sap/API_PRODUCT_SRV/A_Product"
            params = {'$top': 1000}
            
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    products = data.get('d', {}).get('results', [])
                    
                    self.entities_synced['products'] = len(products)
                    self.sync_count += 1
                    
                    return {
                        'success': True,
                        'count': len(products),
                        'products': products
                    }
            
            return {'success': False, 'error': 'Request failed'}
            
        except Exception as e:
            self.logger.error(f"Failed to sync products: {e}")
            return {'success': False, 'error': str(e)}
    
    async def sync_orders(self) -> Dict[str, Any]:
        """Sync order data from SAP."""
        self.logger.info("Syncing orders from SAP...")
        
        try:
            url = f"{self.api_url}/sap/opu/odata/sap/API_SALES_ORDER_SRV/A_SalesOrder"
            params = {'$top': 1000}
            
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    orders = data.get('d', {}).get('results', [])
                    
                    self.entities_synced['orders'] = len(orders)
                    self.sync_count += 1
                    
                    return {
                        'success': True,
                        'count': len(orders),
                        'orders': orders
                    }
            
            return {'success': False, 'error': 'Request failed'}
            
        except Exception as e:
            self.logger.error(f"Failed to sync orders: {e}")
            return {'success': False, 'error': str(e)}
    
    async def sync_inventory(self) -> Dict[str, Any]:
        """Sync inventory data from SAP."""
        return {'success': True, 'count': 0, 'message': 'Inventory sync not yet implemented'}
    
    async def sync_financials(self) -> Dict[str, Any]:
        """Sync financial data from SAP."""
        return {'success': True, 'count': 0, 'message': 'Financial sync not yet implemented'}
