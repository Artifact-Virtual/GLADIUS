"""
Portfolio service providing business logic for portfolio management.
"""

from typing import List, Optional
from decimal import Decimal

from ..models.portfolio import Portfolio, PortfolioStatus
from ..models.position import Position, PositionType, PositionStatus
from ..models.asset import Asset
from ..repositories.portfolio_repository import PortfolioRepository
from ..services.asset_service import AssetService
from ..core.exceptions import (
    DataNotFoundError,
    ValidationError,
    BusinessLogicError
)


class PortfolioService:
    """
    Service for managing portfolios.
    
    Provides high-level business operations for portfolio and position management.
    """
    
    def __init__(
        self,
        repository: PortfolioRepository = None,
        asset_service: AssetService = None
    ):
        """
        Initialize portfolio service.
        
        Args:
            repository: Portfolio repository (creates new if not provided)
            asset_service: Asset service for asset lookups
        """
        self.repository = repository or PortfolioRepository()
        self.asset_service = asset_service or AssetService()
    
    def create_portfolio(
        self,
        name: str,
        owner_id: str,
        initial_capital: Decimal,
        base_currency: str = "USD",
        description: str = "",
        metadata: dict = None
    ) -> Portfolio:
        """
        Create a new portfolio.
        
        Args:
            name: Portfolio name
            owner_id: Owner ID
            initial_capital: Starting capital
            base_currency: Base currency
            description: Description
            metadata: Additional metadata
            
        Returns:
            Created portfolio
            
        Raises:
            ValidationError: If validation fails
        """
        portfolio = Portfolio(
            name=name,
            owner_id=owner_id,
            initial_capital=initial_capital,
            base_currency=base_currency,
            description=description,
            status=PortfolioStatus.ACTIVE,
            metadata=metadata
        )
        
        return self.repository.create(portfolio)
    
    def get_portfolio(self, portfolio_id: str) -> Portfolio:
        """
        Get portfolio by ID.
        
        Args:
            portfolio_id: Portfolio ID
            
        Returns:
            Portfolio
            
        Raises:
            DataNotFoundError: If portfolio not found
        """
        return self.repository.get_by_id(portfolio_id)
    
    def list_all_portfolios(self) -> List[Portfolio]:
        """
        List all portfolios.
        
        Returns:
            List of all portfolios
        """
        return self.repository.get_all()
    
    def list_active_portfolios(self) -> List[Portfolio]:
        """
        List all active portfolios.
        
        Returns:
            List of active portfolios
        """
        return self.repository.find_active_portfolios()
    
    def list_portfolios_by_owner(self, owner_id: str) -> List[Portfolio]:
        """
        List portfolios by owner.
        
        Args:
            owner_id: Owner ID
            
        Returns:
            List of portfolios
        """
        return self.repository.find_by_owner(owner_id)
    
    def update_portfolio(self, portfolio: Portfolio) -> Portfolio:
        """
        Update a portfolio.
        
        Args:
            portfolio: Portfolio to update
            
        Returns:
            Updated portfolio
            
        Raises:
            DataNotFoundError: If portfolio not found
            ValidationError: If validation fails
        """
        return self.repository.update(portfolio)
    
    def freeze_portfolio(self, portfolio_id: str) -> Portfolio:
        """
        Freeze a portfolio.
        
        Args:
            portfolio_id: Portfolio ID
            
        Returns:
            Updated portfolio
        """
        portfolio = self.get_portfolio(portfolio_id)
        portfolio.freeze()
        return self.repository.update(portfolio)
    
    def unfreeze_portfolio(self, portfolio_id: str) -> Portfolio:
        """
        Unfreeze a portfolio.
        
        Args:
            portfolio_id: Portfolio ID
            
        Returns:
            Updated portfolio
        """
        portfolio = self.get_portfolio(portfolio_id)
        portfolio.unfreeze()
        return self.repository.update(portfolio)
    
    def deactivate_portfolio(self, portfolio_id: str) -> Portfolio:
        """
        Deactivate a portfolio.
        
        Args:
            portfolio_id: Portfolio ID
            
        Returns:
            Updated portfolio
        """
        portfolio = self.get_portfolio(portfolio_id)
        portfolio.deactivate()
        return self.repository.update(portfolio)
    
    def delete_portfolio(self, portfolio_id: str) -> None:
        """
        Delete a portfolio.
        
        Args:
            portfolio_id: Portfolio ID
            
        Raises:
            DataNotFoundError: If portfolio not found
            BusinessLogicError: If portfolio has open positions
        """
        portfolio = self.get_portfolio(portfolio_id)
        
        if portfolio.get_open_positions():
            raise BusinessLogicError(
                "open_positions",
                "Cannot delete portfolio with open positions"
            )
        
        self.repository.delete(portfolio_id)
    
    def open_position(
        self,
        portfolio_id: str,
        asset_id: str,
        position_type: PositionType,
        quantity: Decimal,
        price: Decimal
    ) -> Position:
        """
        Open a new position in a portfolio.
        
        Args:
            portfolio_id: Portfolio ID
            asset_id: Asset ID
            position_type: Long or short
            quantity: Quantity to purchase
            price: Price per unit
            
        Returns:
            Created position
            
        Raises:
            DataNotFoundError: If portfolio or asset not found
            BusinessLogicError: If insufficient capital or duplicate position
            ValidationError: If validation fails
        """
        portfolio = self.get_portfolio(portfolio_id)
        asset = self.asset_service.get_asset(asset_id)
        
        if not portfolio.is_active():
            raise BusinessLogicError(
                "portfolio_inactive",
                f"Portfolio {portfolio_id} is not active"
            )
        
        if not asset.is_active():
            raise BusinessLogicError(
                "asset_inactive",
                f"Asset {asset_id} is not active"
            )
        
        # Calculate cost
        cost = Decimal(str(quantity)) * Decimal(str(price))
        
        # Check sufficient capital
        if cost > portfolio.current_capital:
            raise BusinessLogicError(
                "insufficient_capital",
                f"Insufficient capital: need {cost}, have {portfolio.current_capital}"
            )
        
        # Create position
        position = Position(
            portfolio_id=portfolio_id,
            asset_id=asset_id,
            position_type=position_type,
            quantity=quantity,
            average_cost=price,
            current_price=price,
            status=PositionStatus.OPEN
        )
        
        # Add to portfolio
        portfolio.add_position(position)
        portfolio.allocate_capital(cost)
        
        # Update portfolio
        self.repository.update(portfolio)
        
        return position
    
    def close_position(
        self,
        portfolio_id: str,
        position_id: str,
        closing_price: Decimal
    ) -> Position:
        """
        Close a position.
        
        Args:
            portfolio_id: Portfolio ID
            position_id: Position ID
            closing_price: Closing price per unit
            
        Returns:
            Closed position
            
        Raises:
            DataNotFoundError: If portfolio or position not found
            BusinessLogicError: If position is not open
        """
        portfolio = self.get_portfolio(portfolio_id)
        position = portfolio.get_position(position_id)
        
        if position is None:
            raise BusinessLogicError(
                "position_not_found",
                f"Position {position_id} not found in portfolio"
            )
        
        if not position.is_open():
            raise BusinessLogicError(
                "position_closed",
                f"Position {position_id} is already closed"
            )
        
        # Calculate proceeds
        proceeds = position.quantity * Decimal(str(closing_price))
        
        # Close position
        position.update_price(closing_price)
        position.close_position()
        
        # Release capital
        portfolio.release_capital(proceeds)
        
        # Update portfolio
        self.repository.update(portfolio)
        
        return position
    
    def update_position_price(
        self,
        portfolio_id: str,
        position_id: str,
        new_price: Decimal
    ) -> Position:
        """
        Update position market price.
        
        Args:
            portfolio_id: Portfolio ID
            position_id: Position ID
            new_price: New market price
            
        Returns:
            Updated position
        """
        portfolio = self.get_portfolio(portfolio_id)
        position = portfolio.get_position(position_id)
        
        if position is None:
            raise BusinessLogicError(
                "position_not_found",
                f"Position {position_id} not found in portfolio"
            )
        
        position.update_price(new_price)
        self.repository.update(portfolio)
        
        return position
    
    def get_portfolio_performance(self, portfolio_id: str) -> dict:
        """
        Get portfolio performance metrics.
        
        Args:
            portfolio_id: Portfolio ID
            
        Returns:
            Dictionary with performance metrics
        """
        portfolio = self.get_portfolio(portfolio_id)
        
        return {
            "portfolio_id": portfolio.id,
            "name": portfolio.name,
            "status": portfolio.status.value,
            "initial_capital": float(portfolio.initial_capital),
            "current_capital": float(portfolio.current_capital),
            "total_market_value": float(portfolio.get_total_market_value()),
            "total_value": float(portfolio.get_total_value()),
            "total_cost_basis": float(portfolio.get_total_cost_basis()),
            "unrealized_pnl": float(portfolio.get_total_unrealized_pnl()),
            "total_pnl": float(portfolio.get_total_pnl()),
            "total_pnl_percent": float(portfolio.get_total_pnl_percent()),
            "open_positions": len(portfolio.get_open_positions()),
            "closed_positions": len(portfolio.get_closed_positions()),
        }
    
    def get_position_details(self, portfolio_id: str, position_id: str) -> dict:
        """
        Get detailed position information.
        
        Args:
            portfolio_id: Portfolio ID
            position_id: Position ID
            
        Returns:
            Dictionary with position details
        """
        portfolio = self.get_portfolio(portfolio_id)
        position = portfolio.get_position(position_id)
        
        if position is None:
            raise BusinessLogicError(
                "position_not_found",
                f"Position {position_id} not found in portfolio"
            )
        
        # Get asset info
        asset = self.asset_service.get_asset(position.asset_id)
        
        return {
            "position_id": position.id,
            "asset_symbol": asset.symbol,
            "asset_name": asset.name,
            "position_type": position.position_type.value,
            "status": position.status.value,
            "quantity": float(position.quantity),
            "average_cost": float(position.average_cost),
            "current_price": float(position.current_price) if position.current_price else None,
            "cost_basis": float(position.get_cost_basis()),
            "market_value": float(position.get_market_value()) if position.get_market_value() else None,
            "unrealized_pnl": float(position.get_unrealized_pnl()) if position.get_unrealized_pnl() else None,
            "unrealized_pnl_percent": float(position.get_unrealized_pnl_percent()) if position.get_unrealized_pnl_percent() else None,
            "opened_at": position.opened_at.isoformat(),
            "closed_at": position.closed_at.isoformat() if position.closed_at else None,
        }
