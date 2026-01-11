"""
Portfolio model representing a collection of positions.

Portfolios track overall holdings, performance, and risk metrics.
"""

from enum import Enum
from typing import List, Dict, Any, Optional
from datetime import datetime
from decimal import Decimal

from ..core.base_model import BaseModel
from ..core.exceptions import ValidationError, BusinessLogicError
from .position import Position


class PortfolioStatus(Enum):
    """Status of a portfolio."""
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    FROZEN = "FROZEN"
    LIQUIDATING = "LIQUIDATING"


class Portfolio(BaseModel):
    """
    Represents an investment portfolio.
    
    Attributes:
        name: Portfolio name
        description: Portfolio description
        status: Current status
        owner_id: ID of the owner/manager
        base_currency: Base currency for calculations
        initial_capital: Starting capital
        current_capital: Current available capital
        positions: List of current positions
        metadata: Additional portfolio-specific data
    """
    
    def __init__(
        self,
        name: str,
        owner_id: str,
        initial_capital: Decimal,
        base_currency: str = "USD",
        description: str = "",
        status: PortfolioStatus = PortfolioStatus.ACTIVE,
        current_capital: Decimal = None,
        positions: List[Position] = None,
        metadata: Dict[str, Any] = None,
        id: str = None,
        created_at: datetime = None,
        updated_at: datetime = None
    ):
        """
        Initialize a Portfolio.
        
        Args:
            name: Portfolio name
            owner_id: Owner ID
            initial_capital: Starting capital
            base_currency: Base currency
            description: Description
            status: Portfolio status
            current_capital: Current available capital
            positions: List of positions
            metadata: Additional metadata
            id: Unique identifier
            created_at: Creation timestamp
            updated_at: Last update timestamp
        """
        super().__init__(id, created_at, updated_at)
        self.name = name
        self.description = description
        self.status = status
        self.owner_id = owner_id
        self.base_currency = base_currency.upper() if base_currency else "USD"
        self.initial_capital = Decimal(str(initial_capital))
        self.current_capital = Decimal(str(current_capital)) if current_capital is not None else Decimal(str(initial_capital))
        self.positions = positions or []
        self.metadata = metadata or {}
    
    def validate(self) -> None:
        """
        Validate portfolio data.
        
        Raises:
            ValidationError: If validation fails
        """
        if not self.name or not self.name.strip():
            raise ValidationError("name", "Portfolio name cannot be empty", self.name)
        
        if not self.owner_id or not self.owner_id.strip():
            raise ValidationError("owner_id", "Owner ID cannot be empty", self.owner_id)
        
        if not isinstance(self.status, PortfolioStatus):
            raise ValidationError("status", "Invalid portfolio status", self.status)
        
        if not self.base_currency or len(self.base_currency) != 3:
            raise ValidationError("base_currency", "Currency must be a 3-letter code", self.base_currency)
        
        if self.initial_capital < 0:
            raise ValidationError("initial_capital", "Initial capital cannot be negative", self.initial_capital)
        
        if self.current_capital < 0:
            raise ValidationError("current_capital", "Current capital cannot be negative", self.current_capital)
    
    def add_position(self, position: Position) -> None:
        """
        Add a position to the portfolio.
        
        Args:
            position: Position to add
            
        Raises:
            ValidationError: If position is invalid
            BusinessLogicError: If position already exists
        """
        position.validate()
        
        # Check if position with same asset already exists
        if any(p.asset_id == position.asset_id and p.is_open() for p in self.positions):
            raise BusinessLogicError(
                "duplicate_position",
                f"An open position for asset {position.asset_id} already exists"
            )
        
        self.positions.append(position)
        self.update_timestamp()
    
    def remove_position(self, position_id: str) -> None:
        """
        Remove a position from the portfolio.
        
        Args:
            position_id: ID of position to remove
            
        Raises:
            BusinessLogicError: If position not found
        """
        position = self.get_position(position_id)
        if position is None:
            raise BusinessLogicError("position_not_found", f"Position {position_id} not found")
        
        self.positions.remove(position)
        self.update_timestamp()
    
    def get_position(self, position_id: str) -> Optional[Position]:
        """
        Get a position by ID.
        
        Args:
            position_id: Position ID
            
        Returns:
            Position or None if not found
        """
        for position in self.positions:
            if position.id == position_id:
                return position
        return None
    
    def get_open_positions(self) -> List[Position]:
        """
        Get all open positions.
        
        Returns:
            List of open positions
        """
        return [p for p in self.positions if p.is_open()]
    
    def get_closed_positions(self) -> List[Position]:
        """
        Get all closed positions.
        
        Returns:
            List of closed positions
        """
        return [p for p in self.positions if not p.is_open()]
    
    def get_total_market_value(self) -> Decimal:
        """
        Calculate total market value of all positions.
        
        Returns:
            Total market value (0 if no prices available)
        """
        total = Decimal('0')
        for position in self.get_open_positions():
            market_value = position.get_market_value()
            if market_value is not None:
                total += market_value
        return total
    
    def get_total_cost_basis(self) -> Decimal:
        """
        Calculate total cost basis of all positions.
        
        Returns:
            Total cost basis
        """
        return sum(p.get_cost_basis() for p in self.get_open_positions())
    
    def get_total_unrealized_pnl(self) -> Decimal:
        """
        Calculate total unrealized profit/loss.
        
        Returns:
            Total unrealized P&L (0 if no prices available)
        """
        total = Decimal('0')
        for position in self.get_open_positions():
            pnl = position.get_unrealized_pnl()
            if pnl is not None:
                total += pnl
        return total
    
    def get_total_value(self) -> Decimal:
        """
        Calculate total portfolio value (capital + market value).
        
        Returns:
            Total portfolio value
        """
        return self.current_capital + self.get_total_market_value()
    
    def get_total_pnl(self) -> Decimal:
        """
        Calculate total profit/loss.
        
        Returns:
            Total P&L
        """
        return self.get_total_value() - self.initial_capital
    
    def get_total_pnl_percent(self) -> Decimal:
        """
        Calculate total profit/loss as percentage.
        
        Returns:
            Total P&L percentage
        """
        if self.initial_capital == 0:
            return Decimal('0')
        return (self.get_total_pnl() / self.initial_capital) * Decimal('100')
    
    def allocate_capital(self, amount: Decimal) -> None:
        """
        Allocate capital (reduce available capital).
        
        Args:
            amount: Amount to allocate
            
        Raises:
            BusinessLogicError: If insufficient capital
        """
        amount = Decimal(str(amount))
        
        if amount <= 0:
            raise ValidationError("amount", "Amount must be positive", amount)
        
        if amount > self.current_capital:
            raise BusinessLogicError(
                "insufficient_capital",
                f"Cannot allocate {amount}, only {self.current_capital} available"
            )
        
        self.current_capital -= amount
        self.update_timestamp()
    
    def release_capital(self, amount: Decimal) -> None:
        """
        Release capital (increase available capital).
        
        Args:
            amount: Amount to release
        """
        amount = Decimal(str(amount))
        
        if amount <= 0:
            raise ValidationError("amount", "Amount must be positive", amount)
        
        self.current_capital += amount
        self.update_timestamp()
    
    def is_active(self) -> bool:
        """Check if portfolio is active."""
        return self.status == PortfolioStatus.ACTIVE
    
    def freeze(self) -> None:
        """Freeze the portfolio (no new trades)."""
        self.status = PortfolioStatus.FROZEN
        self.update_timestamp()
    
    def unfreeze(self) -> None:
        """Unfreeze the portfolio."""
        self.status = PortfolioStatus.ACTIVE
        self.update_timestamp()
    
    def deactivate(self) -> None:
        """Deactivate the portfolio."""
        self.status = PortfolioStatus.INACTIVE
        self.update_timestamp()
    
    def __repr__(self) -> str:
        return (f"Portfolio(name={self.name}, status={self.status.value}, "
                f"positions={len(self.get_open_positions())})")
