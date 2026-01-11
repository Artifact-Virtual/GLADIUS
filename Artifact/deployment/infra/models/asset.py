"""
Asset model representing financial instruments.

Assets can be stocks, bonds, commodities, cryptocurrencies, etc.
"""

from enum import Enum
from typing import Optional, Dict, Any
from datetime import datetime

from ..core.base_model import BaseModel
from ..core.exceptions import ValidationError


class AssetType(Enum):
    """Types of assets."""
    STOCK = "STOCK"
    BOND = "BOND"
    COMMODITY = "COMMODITY"
    CRYPTOCURRENCY = "CRYPTOCURRENCY"
    FOREX = "FOREX"
    INDEX = "INDEX"
    FUTURE = "FUTURE"
    OPTION = "OPTION"
    ETF = "ETF"
    MUTUAL_FUND = "MUTUAL_FUND"


class AssetStatus(Enum):
    """Status of an asset."""
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    SUSPENDED = "SUSPENDED"
    DELISTED = "DELISTED"


class Asset(BaseModel):
    """
    Represents a financial asset.
    
    Attributes:
        symbol: Ticker symbol (e.g., "AAPL", "BTC-USD")
        name: Full name of the asset
        asset_type: Type of asset
        status: Current status
        market_id: ID of the market this asset trades on
        currency: Currency the asset is denominated in
        metadata: Additional asset-specific data
    """
    
    def __init__(
        self,
        symbol: str,
        name: str,
        asset_type: AssetType,
        market_id: str,
        currency: str = "USD",
        status: AssetStatus = AssetStatus.ACTIVE,
        metadata: Dict[str, Any] = None,
        id: str = None,
        created_at: datetime = None,
        updated_at: datetime = None
    ):
        """
        Initialize an Asset.
        
        Args:
            symbol: Ticker symbol
            name: Full name
            asset_type: Type of asset
            market_id: Market ID
            currency: Currency code (default: USD)
            status: Asset status (default: ACTIVE)
            metadata: Additional metadata
            id: Unique identifier
            created_at: Creation timestamp
            updated_at: Last update timestamp
        """
        super().__init__(id, created_at, updated_at)
        self.symbol = symbol.upper() if symbol else None
        self.name = name
        self.asset_type = asset_type
        self.status = status
        self.market_id = market_id
        self.currency = currency.upper() if currency else "USD"
        self.metadata = metadata or {}
    
    def validate(self) -> None:
        """
        Validate asset data.
        
        Raises:
            ValidationError: If validation fails
        """
        if not self.symbol or not self.symbol.strip():
            raise ValidationError("symbol", "Symbol cannot be empty", self.symbol)
        
        if len(self.symbol) > 20:
            raise ValidationError("symbol", "Symbol cannot exceed 20 characters", self.symbol)
        
        if not self.name or not self.name.strip():
            raise ValidationError("name", "Name cannot be empty", self.name)
        
        if not isinstance(self.asset_type, AssetType):
            raise ValidationError("asset_type", "Invalid asset type", self.asset_type)
        
        if not isinstance(self.status, AssetStatus):
            raise ValidationError("status", "Invalid asset status", self.status)
        
        if not self.market_id or not self.market_id.strip():
            raise ValidationError("market_id", "Market ID cannot be empty", self.market_id)
        
        if not self.currency or len(self.currency) != 3:
            raise ValidationError("currency", "Currency must be a 3-letter code", self.currency)
    
    def is_active(self) -> bool:
        """Check if asset is active."""
        return self.status == AssetStatus.ACTIVE
    
    def activate(self) -> None:
        """Activate the asset."""
        self.status = AssetStatus.ACTIVE
        self.update_timestamp()
    
    def deactivate(self) -> None:
        """Deactivate the asset."""
        self.status = AssetStatus.INACTIVE
        self.update_timestamp()
    
    def suspend(self) -> None:
        """Suspend the asset."""
        self.status = AssetStatus.SUSPENDED
        self.update_timestamp()
    
    def delist(self) -> None:
        """Delist the asset."""
        self.status = AssetStatus.DELISTED
        self.update_timestamp()
    
    def __repr__(self) -> str:
        return f"Asset(symbol={self.symbol}, name={self.name}, type={self.asset_type.value})"
