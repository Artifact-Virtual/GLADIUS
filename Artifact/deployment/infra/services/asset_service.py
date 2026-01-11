"""
Asset service providing business logic for asset management.
"""

from typing import List, Optional
from decimal import Decimal

from ..models.asset import Asset, AssetType, AssetStatus
from ..repositories.asset_repository import AssetRepository
from ..core.exceptions import (
    DataNotFoundError,
    ValidationError,
    BusinessLogicError
)


class AssetService:
    """
    Service for managing assets.
    
    Provides high-level business operations for asset management.
    """
    
    def __init__(self, repository: AssetRepository = None):
        """
        Initialize asset service.
        
        Args:
            repository: Asset repository (creates new if not provided)
        """
        self.repository = repository or AssetRepository()
    
    def create_asset(
        self,
        symbol: str,
        name: str,
        asset_type: AssetType,
        market_id: str,
        currency: str = "USD",
        metadata: dict = None
    ) -> Asset:
        """
        Create a new asset.
        
        Args:
            symbol: Asset symbol
            name: Asset name
            asset_type: Type of asset
            market_id: Market ID
            currency: Currency code
            metadata: Additional metadata
            
        Returns:
            Created asset
            
        Raises:
            ValidationError: If validation fails
            BusinessLogicError: If asset with symbol already exists
        """
        # Check if asset with symbol already exists
        existing = self.repository.find_by_symbol(symbol)
        if existing:
            raise BusinessLogicError(
                "duplicate_asset",
                f"Asset with symbol '{symbol}' already exists"
            )
        
        asset = Asset(
            symbol=symbol,
            name=name,
            asset_type=asset_type,
            market_id=market_id,
            currency=currency,
            status=AssetStatus.ACTIVE,
            metadata=metadata
        )
        
        return self.repository.create(asset)
    
    def get_asset(self, asset_id: str) -> Asset:
        """
        Get asset by ID.
        
        Args:
            asset_id: Asset ID
            
        Returns:
            Asset
            
        Raises:
            DataNotFoundError: If asset not found
        """
        return self.repository.get_by_id(asset_id)
    
    def get_asset_by_symbol(self, symbol: str) -> Optional[Asset]:
        """
        Get asset by symbol.
        
        Args:
            symbol: Asset symbol
            
        Returns:
            Asset or None if not found
        """
        return self.repository.find_by_symbol(symbol)
    
    def list_all_assets(self) -> List[Asset]:
        """
        List all assets.
        
        Returns:
            List of all assets
        """
        return self.repository.get_all()
    
    def list_active_assets(self) -> List[Asset]:
        """
        List all active assets.
        
        Returns:
            List of active assets
        """
        return self.repository.find_active_assets()
    
    def list_assets_by_market(self, market_id: str) -> List[Asset]:
        """
        List assets for a specific market.
        
        Args:
            market_id: Market ID
            
        Returns:
            List of assets
        """
        return self.repository.find_by_market(market_id)
    
    def list_assets_by_type(self, asset_type: AssetType) -> List[Asset]:
        """
        List assets by type.
        
        Args:
            asset_type: Asset type
            
        Returns:
            List of assets
        """
        return self.repository.find_by_type(asset_type)
    
    def update_asset(self, asset: Asset) -> Asset:
        """
        Update an asset.
        
        Args:
            asset: Asset to update
            
        Returns:
            Updated asset
            
        Raises:
            DataNotFoundError: If asset not found
            ValidationError: If validation fails
        """
        return self.repository.update(asset)
    
    def activate_asset(self, asset_id: str) -> Asset:
        """
        Activate an asset.
        
        Args:
            asset_id: Asset ID
            
        Returns:
            Updated asset
        """
        asset = self.get_asset(asset_id)
        asset.activate()
        return self.repository.update(asset)
    
    def deactivate_asset(self, asset_id: str) -> Asset:
        """
        Deactivate an asset.
        
        Args:
            asset_id: Asset ID
            
        Returns:
            Updated asset
        """
        asset = self.get_asset(asset_id)
        asset.deactivate()
        return self.repository.update(asset)
    
    def suspend_asset(self, asset_id: str) -> Asset:
        """
        Suspend an asset.
        
        Args:
            asset_id: Asset ID
            
        Returns:
            Updated asset
        """
        asset = self.get_asset(asset_id)
        asset.suspend()
        return self.repository.update(asset)
    
    def delist_asset(self, asset_id: str) -> Asset:
        """
        Delist an asset.
        
        Args:
            asset_id: Asset ID
            
        Returns:
            Updated asset
        """
        asset = self.get_asset(asset_id)
        asset.delist()
        return self.repository.update(asset)
    
    def delete_asset(self, asset_id: str) -> None:
        """
        Delete an asset.
        
        Args:
            asset_id: Asset ID
            
        Raises:
            DataNotFoundError: If asset not found
        """
        self.repository.delete(asset_id)
    
    def search_assets(self, query: str) -> List[Asset]:
        """
        Search assets by symbol or name.
        
        Args:
            query: Search query
            
        Returns:
            List of matching assets
        """
        query = query.upper()
        assets = self.list_all_assets()
        return [
            asset for asset in assets
            if query in asset.symbol.upper() or query in asset.name.upper()
        ]
