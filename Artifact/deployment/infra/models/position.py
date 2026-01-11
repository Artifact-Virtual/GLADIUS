"""
Position model representing holdings of assets.

Positions track the quantity and cost basis of assets held.
"""

from enum import Enum
from typing import Optional, Dict, Any
from datetime import datetime, timezone
from decimal import Decimal

from ..core.base_model import BaseModel
from ..core.exceptions import ValidationError, BusinessLogicError


class PositionType(Enum):
    """Types of positions."""
    LONG = "LONG"
    SHORT = "SHORT"


class PositionStatus(Enum):
    """Status of a position."""
    OPEN = "OPEN"
    CLOSED = "CLOSED"
    PENDING = "PENDING"


class Position(BaseModel):
    """
    Represents a position in an asset.
    
    Attributes:
        portfolio_id: ID of the portfolio holding this position
        asset_id: ID of the asset
        position_type: Long or short position
        status: Current status
        quantity: Number of units held
        average_cost: Average cost per unit
        current_price: Current market price per unit
        opened_at: When position was opened
        closed_at: When position was closed (if closed)
        metadata: Additional position-specific data
    """
    
    def __init__(
        self,
        portfolio_id: str,
        asset_id: str,
        position_type: PositionType,
        quantity: Decimal,
        average_cost: Decimal,
        status: PositionStatus = PositionStatus.OPEN,
        current_price: Decimal = None,
        opened_at: datetime = None,
        closed_at: datetime = None,
        metadata: Dict[str, Any] = None,
        id: str = None,
        created_at: datetime = None,
        updated_at: datetime = None
    ):
        """
        Initialize a Position.
        
        Args:
            portfolio_id: Portfolio ID
            asset_id: Asset ID
            position_type: Long or short
            quantity: Quantity held
            average_cost: Average cost per unit
            status: Position status
            current_price: Current market price
            opened_at: Opening timestamp
            closed_at: Closing timestamp
            metadata: Additional metadata
            id: Unique identifier
            created_at: Creation timestamp
            updated_at: Last update timestamp
        """
        super().__init__(id, created_at, updated_at)
        self.portfolio_id = portfolio_id
        self.asset_id = asset_id
        self.position_type = position_type
        self.status = status
        self.quantity = Decimal(str(quantity))
        self.average_cost = Decimal(str(average_cost))
        self.current_price = Decimal(str(current_price)) if current_price is not None else None
        self.opened_at = opened_at or datetime.now(timezone.utc)
        self.closed_at = closed_at
        self.metadata = metadata or {}
    
    def validate(self) -> None:
        """
        Validate position data.
        
        Raises:
            ValidationError: If validation fails
        """
        if not self.portfolio_id or not self.portfolio_id.strip():
            raise ValidationError("portfolio_id", "Portfolio ID cannot be empty", self.portfolio_id)
        
        if not self.asset_id or not self.asset_id.strip():
            raise ValidationError("asset_id", "Asset ID cannot be empty", self.asset_id)
        
        if not isinstance(self.position_type, PositionType):
            raise ValidationError("position_type", "Invalid position type", self.position_type)
        
        if not isinstance(self.status, PositionStatus):
            raise ValidationError("status", "Invalid position status", self.status)
        
        if self.quantity <= 0:
            raise ValidationError("quantity", "Quantity must be positive", self.quantity)
        
        if self.average_cost < 0:
            raise ValidationError("average_cost", "Average cost cannot be negative", self.average_cost)
        
        if self.current_price is not None and self.current_price < 0:
            raise ValidationError("current_price", "Current price cannot be negative", self.current_price)
        
        if self.status == PositionStatus.CLOSED and self.closed_at is None:
            raise ValidationError("closed_at", "Closed position must have closed_at timestamp", None)
    
    def get_cost_basis(self) -> Decimal:
        """
        Calculate total cost basis.
        
        Returns:
            Total cost of the position
        """
        return self.quantity * self.average_cost
    
    def get_market_value(self) -> Optional[Decimal]:
        """
        Calculate current market value.
        
        Returns:
            Current market value or None if price not set
        """
        if self.current_price is None:
            return None
        return self.quantity * self.current_price
    
    def get_unrealized_pnl(self) -> Optional[Decimal]:
        """
        Calculate unrealized profit/loss.
        
        Returns:
            Unrealized P&L or None if current price not set
        """
        market_value = self.get_market_value()
        if market_value is None:
            return None
        
        pnl = market_value - self.get_cost_basis()
        
        # For short positions, profit is inverted
        if self.position_type == PositionType.SHORT:
            pnl = -pnl
        
        return pnl
    
    def get_unrealized_pnl_percent(self) -> Optional[Decimal]:
        """
        Calculate unrealized profit/loss as percentage.
        
        Returns:
            Unrealized P&L percentage or None if current price not set
        """
        pnl = self.get_unrealized_pnl()
        if pnl is None:
            return None
        
        cost_basis = self.get_cost_basis()
        if cost_basis == 0:
            return Decimal('0')
        
        return (pnl / cost_basis) * Decimal('100')
    
    def update_price(self, new_price: Decimal) -> None:
        """
        Update current price.
        
        Args:
            new_price: New market price
        """
        if new_price < 0:
            raise ValidationError("new_price", "Price cannot be negative", new_price)
        
        self.current_price = Decimal(str(new_price))
        self.update_timestamp()
    
    def increase_position(self, quantity: Decimal, cost: Decimal) -> None:
        """
        Increase position size (add to position).
        
        Args:
            quantity: Additional quantity
            cost: Cost per unit of additional quantity
        """
        if quantity <= 0:
            raise ValidationError("quantity", "Quantity must be positive", quantity)
        
        if cost < 0:
            raise ValidationError("cost", "Cost cannot be negative", cost)
        
        # Calculate new average cost
        total_cost = self.get_cost_basis() + (Decimal(str(quantity)) * Decimal(str(cost)))
        new_quantity = self.quantity + Decimal(str(quantity))
        self.average_cost = total_cost / new_quantity
        self.quantity = new_quantity
        self.update_timestamp()
    
    def reduce_position(self, quantity: Decimal) -> None:
        """
        Reduce position size (partial close).
        
        Args:
            quantity: Quantity to reduce
            
        Raises:
            BusinessLogicError: If reduction exceeds position size
        """
        quantity = Decimal(str(quantity))
        
        if quantity <= 0:
            raise ValidationError("quantity", "Quantity must be positive", quantity)
        
        if quantity > self.quantity:
            raise BusinessLogicError(
                "position_size",
                f"Cannot reduce position by {quantity}, only {self.quantity} available"
            )
        
        self.quantity -= quantity
        
        if self.quantity == 0:
            self.close_position()
        else:
            self.update_timestamp()
    
    def close_position(self) -> None:
        """Close the position."""
        self.status = PositionStatus.CLOSED
        self.closed_at = datetime.now(timezone.utc)
        self.update_timestamp()
    
    def is_open(self) -> bool:
        """Check if position is open."""
        return self.status == PositionStatus.OPEN
    
    def is_long(self) -> bool:
        """Check if position is long."""
        return self.position_type == PositionType.LONG
    
    def is_short(self) -> bool:
        """Check if position is short."""
        return self.position_type == PositionType.SHORT
    
    def __repr__(self) -> str:
        return (f"Position(asset_id={self.asset_id}, type={self.position_type.value}, "
                f"quantity={self.quantity}, status={self.status.value})")
