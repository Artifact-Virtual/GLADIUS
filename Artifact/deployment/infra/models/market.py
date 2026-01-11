"""
Market model representing trading venues.

Markets are where assets are traded (e.g., NYSE, NASDAQ, CME).
"""

from enum import Enum
from typing import Optional, Dict, Any, List
from datetime import datetime, time

from ..core.base_model import BaseModel
from ..core.exceptions import ValidationError


class MarketType(Enum):
    """Types of markets."""
    STOCK_EXCHANGE = "STOCK_EXCHANGE"
    COMMODITIES_EXCHANGE = "COMMODITIES_EXCHANGE"
    CRYPTO_EXCHANGE = "CRYPTO_EXCHANGE"
    FOREX_MARKET = "FOREX_MARKET"
    DERIVATIVES_EXCHANGE = "DERIVATIVES_EXCHANGE"
    OTC = "OTC"  # Over-the-counter


class MarketStatus(Enum):
    """Status of a market."""
    OPEN = "OPEN"
    CLOSED = "CLOSED"
    PRE_MARKET = "PRE_MARKET"
    POST_MARKET = "POST_MARKET"
    HALTED = "HALTED"
    HOLIDAY = "HOLIDAY"


class Market(BaseModel):
    """
    Represents a trading market/exchange.
    
    Attributes:
        code: Market code (e.g., "NYSE", "NASDAQ", "BINANCE")
        name: Full name of the market
        market_type: Type of market
        status: Current market status
        timezone: Timezone of the market
        currency: Primary currency
        opening_time: Market opening time
        closing_time: Market closing time
        trading_days: Days of the week market is open
        metadata: Additional market-specific data
    """
    
    def __init__(
        self,
        code: str,
        name: str,
        market_type: MarketType,
        timezone: str,
        currency: str = "USD",
        status: MarketStatus = MarketStatus.CLOSED,
        opening_time: time = None,
        closing_time: time = None,
        trading_days: List[int] = None,
        metadata: Dict[str, Any] = None,
        id: str = None,
        created_at: datetime = None,
        updated_at: datetime = None
    ):
        """
        Initialize a Market.
        
        Args:
            code: Market code
            name: Full name
            market_type: Type of market
            timezone: Timezone (e.g., "America/New_York")
            currency: Primary currency
            status: Current status
            opening_time: Opening time
            closing_time: Closing time
            trading_days: List of trading days (0=Monday, 6=Sunday)
            metadata: Additional metadata
            id: Unique identifier
            created_at: Creation timestamp
            updated_at: Last update timestamp
        """
        super().__init__(id, created_at, updated_at)
        self.code = code.upper() if code else None
        self.name = name
        self.market_type = market_type
        self.status = status
        self.timezone = timezone
        self.currency = currency.upper() if currency else "USD"
        self.opening_time = opening_time
        self.closing_time = closing_time
        self.trading_days = trading_days or [0, 1, 2, 3, 4]  # Monday-Friday default
        self.metadata = metadata or {}
    
    def validate(self) -> None:
        """
        Validate market data.
        
        Raises:
            ValidationError: If validation fails
        """
        if not self.code or not self.code.strip():
            raise ValidationError("code", "Market code cannot be empty", self.code)
        
        if len(self.code) > 10:
            raise ValidationError("code", "Market code cannot exceed 10 characters", self.code)
        
        if not self.name or not self.name.strip():
            raise ValidationError("name", "Market name cannot be empty", self.name)
        
        if not isinstance(self.market_type, MarketType):
            raise ValidationError("market_type", "Invalid market type", self.market_type)
        
        if not isinstance(self.status, MarketStatus):
            raise ValidationError("status", "Invalid market status", self.status)
        
        if not self.timezone or not self.timezone.strip():
            raise ValidationError("timezone", "Timezone cannot be empty", self.timezone)
        
        if not self.currency or len(self.currency) != 3:
            raise ValidationError("currency", "Currency must be a 3-letter code", self.currency)
        
        if self.trading_days:
            if not all(isinstance(day, int) and 0 <= day <= 6 for day in self.trading_days):
                raise ValidationError("trading_days", "Trading days must be integers 0-6", self.trading_days)
    
    def is_open(self) -> bool:
        """Check if market is currently open."""
        return self.status == MarketStatus.OPEN
    
    def open_market(self) -> None:
        """Open the market."""
        self.status = MarketStatus.OPEN
        self.update_timestamp()
    
    def close_market(self) -> None:
        """Close the market."""
        self.status = MarketStatus.CLOSED
        self.update_timestamp()
    
    def halt_trading(self) -> None:
        """Halt trading on the market."""
        self.status = MarketStatus.HALTED
        self.update_timestamp()
    
    def is_trading_day(self, day: int) -> bool:
        """
        Check if given day is a trading day.
        
        Args:
            day: Day of week (0=Monday, 6=Sunday)
            
        Returns:
            True if trading day, False otherwise
        """
        return day in self.trading_days
    
    def __repr__(self) -> str:
        return f"Market(code={self.code}, name={self.name}, type={self.market_type.value})"
