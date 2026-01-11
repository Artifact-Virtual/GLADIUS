"""
Market service providing business logic for market management.
"""

from typing import List, Optional
from datetime import datetime, time

from ..models.market import Market, MarketType, MarketStatus
from ..repositories.market_repository import MarketRepository
from ..core.exceptions import (
    DataNotFoundError,
    ValidationError,
    BusinessLogicError
)


class MarketService:
    """
    Service for managing markets.
    
    Provides high-level business operations for market management.
    """
    
    def __init__(self, repository: MarketRepository = None):
        """
        Initialize market service.
        
        Args:
            repository: Market repository (creates new if not provided)
        """
        self.repository = repository or MarketRepository()
    
    def create_market(
        self,
        code: str,
        name: str,
        market_type: MarketType,
        timezone: str,
        currency: str = "USD",
        opening_time: time = None,
        closing_time: time = None,
        trading_days: List[int] = None,
        metadata: dict = None
    ) -> Market:
        """
        Create a new market.
        
        Args:
            code: Market code
            name: Market name
            market_type: Type of market
            timezone: Timezone
            currency: Primary currency
            opening_time: Opening time
            closing_time: Closing time
            trading_days: Trading days (0=Monday, 6=Sunday)
            metadata: Additional metadata
            
        Returns:
            Created market
            
        Raises:
            ValidationError: If validation fails
            BusinessLogicError: If market with code already exists
        """
        # Check if market with code already exists
        existing = self.repository.find_by_code(code)
        if existing:
            raise BusinessLogicError(
                "duplicate_market",
                f"Market with code '{code}' already exists"
            )
        
        market = Market(
            code=code,
            name=name,
            market_type=market_type,
            timezone=timezone,
            currency=currency,
            status=MarketStatus.CLOSED,
            opening_time=opening_time,
            closing_time=closing_time,
            trading_days=trading_days,
            metadata=metadata
        )
        
        return self.repository.create(market)
    
    def get_market(self, market_id: str) -> Market:
        """
        Get market by ID.
        
        Args:
            market_id: Market ID
            
        Returns:
            Market
            
        Raises:
            DataNotFoundError: If market not found
        """
        return self.repository.get_by_id(market_id)
    
    def get_market_by_code(self, code: str) -> Optional[Market]:
        """
        Get market by code.
        
        Args:
            code: Market code
            
        Returns:
            Market or None if not found
        """
        return self.repository.find_by_code(code)
    
    def list_all_markets(self) -> List[Market]:
        """
        List all markets.
        
        Returns:
            List of all markets
        """
        return self.repository.get_all()
    
    def list_open_markets(self) -> List[Market]:
        """
        List all open markets.
        
        Returns:
            List of open markets
        """
        return self.repository.find_open_markets()
    
    def list_markets_by_type(self, market_type: MarketType) -> List[Market]:
        """
        List markets by type.
        
        Args:
            market_type: Market type
            
        Returns:
            List of markets
        """
        return self.repository.find_by_type(market_type)
    
    def list_markets_by_timezone(self, timezone: str) -> List[Market]:
        """
        List markets by timezone.
        
        Args:
            timezone: Timezone
            
        Returns:
            List of markets
        """
        return self.repository.find_by_timezone(timezone)
    
    def update_market(self, market: Market) -> Market:
        """
        Update a market.
        
        Args:
            market: Market to update
            
        Returns:
            Updated market
            
        Raises:
            DataNotFoundError: If market not found
            ValidationError: If validation fails
        """
        return self.repository.update(market)
    
    def open_market(self, market_id: str) -> Market:
        """
        Open a market.
        
        Args:
            market_id: Market ID
            
        Returns:
            Updated market
        """
        market = self.get_market(market_id)
        market.open_market()
        return self.repository.update(market)
    
    def close_market(self, market_id: str) -> Market:
        """
        Close a market.
        
        Args:
            market_id: Market ID
            
        Returns:
            Updated market
        """
        market = self.get_market(market_id)
        market.close_market()
        return self.repository.update(market)
    
    def halt_market(self, market_id: str) -> Market:
        """
        Halt trading on a market.
        
        Args:
            market_id: Market ID
            
        Returns:
            Updated market
        """
        market = self.get_market(market_id)
        market.halt_trading()
        return self.repository.update(market)
    
    def delete_market(self, market_id: str) -> None:
        """
        Delete a market.
        
        Args:
            market_id: Market ID
            
        Raises:
            DataNotFoundError: If market not found
        """
        self.repository.delete(market_id)
    
    def is_trading_day(self, market_id: str, date: datetime) -> bool:
        """
        Check if a given date is a trading day for the market.
        
        Args:
            market_id: Market ID
            date: Date to check
            
        Returns:
            True if trading day, False otherwise
        """
        market = self.get_market(market_id)
        return market.is_trading_day(date.weekday())
    
    def get_market_status_summary(self) -> dict:
        """
        Get summary of market statuses.
        
        Returns:
            Dictionary with counts by status
        """
        markets = self.list_all_markets()
        summary = {status: 0 for status in MarketStatus}
        
        for market in markets:
            summary[market.status] += 1
        
        return {status.value: count for status, count in summary.items()}
