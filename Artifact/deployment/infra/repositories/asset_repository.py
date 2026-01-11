"""
Asset repository for asset data persistence.
"""

from typing import List, Optional

from ..core.repository import Repository
from ..models.asset import Asset, AssetType, AssetStatus


class AssetRepository(Repository[Asset]):
    """Repository for Asset entities."""
    
    def __init__(self):
        super().__init__("Asset")
    
    def find_by_symbol(self, symbol: str) -> Optional[Asset]:
        """
        Find asset by symbol.
        
        Args:
            symbol: Asset symbol
            
        Returns:
            Asset or None if not found
        """
        symbol = symbol.upper()
        results = self.find_by_criteria({"symbol": symbol})
        return results[0] if results else None
    
    def find_by_market(self, market_id: str) -> List[Asset]:
        """
        Find all assets for a given market.
        
        Args:
            market_id: Market ID
            
        Returns:
            List of assets
        """
        return self.find_by_criteria({"market_id": market_id})
    
    def find_by_type(self, asset_type: AssetType) -> List[Asset]:
        """
        Find assets by type.
        
        Args:
            asset_type: Asset type
            
        Returns:
            List of assets
        """
        return self.find_by_criteria({"asset_type": asset_type})
    
    def find_active_assets(self) -> List[Asset]:
        """
        Find all active assets.
        
        Returns:
            List of active assets
        """
        return self.find_by_criteria({"status": AssetStatus.ACTIVE})
    
    def find_by_currency(self, currency: str) -> List[Asset]:
        """
        Find assets by currency.
        
        Args:
            currency: Currency code
            
        Returns:
            List of assets
        """
        currency = currency.upper()
        return self.find_by_criteria({"currency": currency})
