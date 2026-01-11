"""
Market repository for market data persistence.
"""

from typing import List, Optional

from ..core.repository import Repository
from ..models.market import Market, MarketType, MarketStatus


class MarketRepository(Repository[Market]):
    """Repository for Market entities."""
    
    def __init__(self):
        super().__init__("Market")
    
    def find_by_code(self, code: str) -> Optional[Market]:
        """
        Find market by code.
        
        Args:
            code: Market code
            
        Returns:
            Market or None if not found
        """
        code = code.upper()
        results = self.find_by_criteria({"code": code})
        return results[0] if results else None
    
    def find_by_type(self, market_type: MarketType) -> List[Market]:
        """
        Find markets by type.
        
        Args:
            market_type: Market type
            
        Returns:
            List of markets
        """
        return self.find_by_criteria({"market_type": market_type})
    
    def find_open_markets(self) -> List[Market]:
        """
        Find all open markets.
        
        Returns:
            List of open markets
        """
        return self.find_by_criteria({"status": MarketStatus.OPEN})
    
    def find_by_currency(self, currency: str) -> List[Market]:
        """
        Find markets by primary currency.
        
        Args:
            currency: Currency code
            
        Returns:
            List of markets
        """
        currency = currency.upper()
        return self.find_by_criteria({"currency": currency})
    
    def find_by_timezone(self, timezone: str) -> List[Market]:
        """
        Find markets by timezone.
        
        Args:
            timezone: Timezone string
            
        Returns:
            List of markets
        """
        return self.find_by_criteria({"timezone": timezone})
