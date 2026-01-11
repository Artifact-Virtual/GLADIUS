"""
Base ERP connector providing common interface for all ERP systems.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
from datetime import datetime, timezone
import logging


class ERPConnector(ABC):
    """
    Abstract base class for ERP system connectors.
    
    Provides common interface for:
    - Authentication
    - Data synchronization
    - CRUD operations
    - Error handling
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize ERP connector.
        
        Args:
            config: ERP system configuration
        """
        self.config = config
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.connected = False
        self.last_sync = None
    
    @abstractmethod
    async def connect(self) -> bool:
        """
        Establish connection to ERP system.
        
        Returns:
            True if connected successfully
        """
        pass
    
    @abstractmethod
    async def disconnect(self) -> None:
        """Disconnect from ERP system."""
        pass
    
    @abstractmethod
    async def test_connection(self) -> bool:
        """
        Test ERP connection.
        
        Returns:
            True if connection is valid
        """
        pass
    
    @abstractmethod
    async def sync_customers(self) -> List[Dict[str, Any]]:
        """
        Synchronize customer data.
        
        Returns:
            List of customer records
        """
        pass
    
    @abstractmethod
    async def sync_products(self) -> List[Dict[str, Any]]:
        """
        Synchronize product/service data.
        
        Returns:
            List of product records
        """
        pass
    
    @abstractmethod
    async def sync_orders(self) -> List[Dict[str, Any]]:
        """
        Synchronize order/transaction data.
        
        Returns:
            List of order records
        """
        pass
    
    @abstractmethod
    async def sync_inventory(self) -> List[Dict[str, Any]]:
        """
        Synchronize inventory data.
        
        Returns:
            List of inventory records
        """
        pass
    
    @abstractmethod
    async def sync_financials(self) -> Dict[str, Any]:
        """
        Synchronize financial data.
        
        Returns:
            Financial data summary
        """
        pass
    
    @abstractmethod
    async def create_customer(self, data: Dict[str, Any]) -> str:
        """
        Create new customer in ERP.
        
        Args:
            data: Customer data
            
        Returns:
            Customer ID
        """
        pass
    
    @abstractmethod
    async def create_order(self, data: Dict[str, Any]) -> str:
        """
        Create new order in ERP.
        
        Args:
            data: Order data
            
        Returns:
            Order ID
        """
        pass
    
    @abstractmethod
    async def update_inventory(self, product_id: str, quantity: int) -> bool:
        """
        Update product inventory.
        
        Args:
            product_id: Product identifier
            quantity: New quantity
            
        Returns:
            True if updated successfully
        """
        pass
    
    def get_last_sync_time(self) -> Optional[datetime]:
        """Get last synchronization timestamp."""
        return self.last_sync
    
    def is_connected(self) -> bool:
        """Check if connected to ERP."""
        return self.connected
    
    async def sync_entity(self, entity_type: str) -> List[Dict[str, Any]]:
        """
        Synchronize specific entity type.
        
        Args:
            entity_type: Type of entity (customers, products, orders, etc.)
            
        Returns:
            List of synced records
        """
        entity_type = entity_type.lower()
        
        if entity_type == "customers":
            return await self.sync_customers()
        elif entity_type == "products":
            return await self.sync_products()
        elif entity_type == "orders":
            return await self.sync_orders()
        elif entity_type == "inventory":
            return await self.sync_inventory()
        elif entity_type == "financials":
            result = await self.sync_financials()
            return [result] if result else []
        else:
            raise ValueError(f"Unknown entity type: {entity_type}")
