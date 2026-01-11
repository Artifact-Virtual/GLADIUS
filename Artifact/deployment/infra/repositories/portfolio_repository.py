"""
Portfolio repository for portfolio data persistence.
"""

from typing import List, Optional

from ..core.repository import Repository
from ..models.portfolio import Portfolio, PortfolioStatus


class PortfolioRepository(Repository[Portfolio]):
    """Repository for Portfolio entities."""
    
    def __init__(self):
        super().__init__("Portfolio")
    
    def find_by_owner(self, owner_id: str) -> List[Portfolio]:
        """
        Find portfolios by owner.
        
        Args:
            owner_id: Owner ID
            
        Returns:
            List of portfolios
        """
        return self.find_by_criteria({"owner_id": owner_id})
    
    def find_active_portfolios(self) -> List[Portfolio]:
        """
        Find all active portfolios.
        
        Returns:
            List of active portfolios
        """
        return self.find_by_criteria({"status": PortfolioStatus.ACTIVE})
    
    def find_by_name(self, name: str) -> List[Portfolio]:
        """
        Find portfolios by name.
        
        Args:
            name: Portfolio name
            
        Returns:
            List of portfolios
        """
        return self.find_by_criteria({"name": name})
    
    def find_by_currency(self, base_currency: str) -> List[Portfolio]:
        """
        Find portfolios by base currency.
        
        Args:
            base_currency: Currency code
            
        Returns:
            List of portfolios
        """
        base_currency = base_currency.upper()
        return self.find_by_criteria({"base_currency": base_currency})
