"""
Unit tests for Portfolio model and PortfolioService.
"""

import unittest
import sys
from pathlib import Path
from decimal import Decimal

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from infra.models.portfolio import Portfolio, PortfolioStatus
from infra.models.position import Position, PositionType, PositionStatus
from infra.models.asset import Asset, AssetType, AssetStatus
from infra.services.portfolio_service import PortfolioService
from infra.services.asset_service import AssetService
from infra.core.exceptions import ValidationError, BusinessLogicError, DataNotFoundError


class TestPortfolioModel(unittest.TestCase):
    """Test cases for Portfolio model."""
    
    def test_create_portfolio(self):
        """Test creating a valid portfolio."""
        portfolio = Portfolio(
            name="Growth Portfolio",
            owner_id="user123",
            initial_capital=Decimal("100000"),
            base_currency="USD"
        )
        
        self.assertEqual(portfolio.name, "Growth Portfolio")
        self.assertEqual(portfolio.owner_id, "user123")
        self.assertEqual(portfolio.initial_capital, Decimal("100000"))
        self.assertEqual(portfolio.current_capital, Decimal("100000"))
        self.assertTrue(portfolio.is_active())
    
    def test_portfolio_validation(self):
        """Test portfolio validation."""
        portfolio = Portfolio(
            name="Test Portfolio",
            owner_id="user123",
            initial_capital=Decimal("50000")
        )
        
        # Should not raise
        portfolio.validate()
        
        # Test invalid name
        portfolio.name = ""
        with self.assertRaises(ValidationError):
            portfolio.validate()
        
        # Test invalid currency
        portfolio.name = "Test"
        portfolio.base_currency = "DOLLAR"
        with self.assertRaises(ValidationError):
            portfolio.validate()
    
    def test_capital_allocation(self):
        """Test capital allocation and release."""
        portfolio = Portfolio(
            name="Test Portfolio",
            owner_id="user123",
            initial_capital=Decimal("100000")
        )
        
        # Allocate capital
        portfolio.allocate_capital(Decimal("10000"))
        self.assertEqual(portfolio.current_capital, Decimal("90000"))
        
        # Release capital
        portfolio.release_capital(Decimal("5000"))
        self.assertEqual(portfolio.current_capital, Decimal("95000"))
        
        # Try to allocate more than available
        with self.assertRaises(BusinessLogicError):
            portfolio.allocate_capital(Decimal("100000"))
    
    def test_position_management(self):
        """Test adding and removing positions."""
        portfolio = Portfolio(
            name="Test Portfolio",
            owner_id="user123",
            initial_capital=Decimal("100000")
        )
        
        position = Position(
            portfolio_id=portfolio.id,
            asset_id="asset1",
            position_type=PositionType.LONG,
            quantity=Decimal("100"),
            average_cost=Decimal("50")
        )
        
        portfolio.add_position(position)
        self.assertEqual(len(portfolio.get_open_positions()), 1)
        
        portfolio.remove_position(position.id)
        self.assertEqual(len(portfolio.get_open_positions()), 0)
    
    def test_portfolio_performance(self):
        """Test portfolio performance calculations."""
        portfolio = Portfolio(
            name="Test Portfolio",
            owner_id="user123",
            initial_capital=Decimal("100000")
        )
        
        # Add position
        position = Position(
            portfolio_id=portfolio.id,
            asset_id="asset1",
            position_type=PositionType.LONG,
            quantity=Decimal("100"),
            average_cost=Decimal("50"),
            current_price=Decimal("60")
        )
        portfolio.add_position(position)
        portfolio.allocate_capital(Decimal("5000"))
        
        # Check performance metrics
        self.assertEqual(portfolio.get_total_cost_basis(), Decimal("5000"))
        self.assertEqual(portfolio.get_total_market_value(), Decimal("6000"))
        self.assertEqual(portfolio.get_total_unrealized_pnl(), Decimal("1000"))
        self.assertEqual(portfolio.current_capital, Decimal("95000"))
        self.assertEqual(portfolio.get_total_value(), Decimal("101000"))
        self.assertEqual(portfolio.get_total_pnl(), Decimal("1000"))


class TestPortfolioService(unittest.TestCase):
    """Test cases for PortfolioService."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.portfolio_service = PortfolioService()
        self.asset_service = AssetService()
        self.portfolio_service.asset_service = self.asset_service
        
        # Create test assets
        self.asset1 = self.asset_service.create_asset(
            symbol="AAPL",
            name="Apple Inc.",
            asset_type=AssetType.STOCK,
            market_id="NASDAQ"
        )
        
        self.asset2 = self.asset_service.create_asset(
            symbol="GOOGL",
            name="Alphabet Inc.",
            asset_type=AssetType.STOCK,
            market_id="NASDAQ"
        )
    
    def tearDown(self):
        """Clean up after tests."""
        self.portfolio_service.repository.clear()
        self.asset_service.repository.clear()
    
    def test_create_portfolio(self):
        """Test creating portfolio through service."""
        portfolio = self.portfolio_service.create_portfolio(
            name="My Portfolio",
            owner_id="user123",
            initial_capital=Decimal("50000")
        )
        
        self.assertIsNotNone(portfolio.id)
        self.assertEqual(portfolio.name, "My Portfolio")
        self.assertTrue(portfolio.is_active())
    
    def test_open_position(self):
        """Test opening a position."""
        portfolio = self.portfolio_service.create_portfolio(
            name="Test Portfolio",
            owner_id="user123",
            initial_capital=Decimal("100000")
        )
        
        position = self.portfolio_service.open_position(
            portfolio_id=portfolio.id,
            asset_id=self.asset1.id,
            position_type=PositionType.LONG,
            quantity=Decimal("100"),
            price=Decimal("150")
        )
        
        self.assertIsNotNone(position.id)
        self.assertEqual(position.quantity, Decimal("100"))
        self.assertEqual(position.average_cost, Decimal("150"))
        
        # Check capital was allocated
        updated_portfolio = self.portfolio_service.get_portfolio(portfolio.id)
        self.assertEqual(updated_portfolio.current_capital, Decimal("85000"))
    
    def test_open_position_insufficient_capital(self):
        """Test opening position with insufficient capital."""
        portfolio = self.portfolio_service.create_portfolio(
            name="Small Portfolio",
            owner_id="user123",
            initial_capital=Decimal("1000")
        )
        
        with self.assertRaises(BusinessLogicError):
            self.portfolio_service.open_position(
                portfolio_id=portfolio.id,
                asset_id=self.asset1.id,
                position_type=PositionType.LONG,
                quantity=Decimal("100"),
                price=Decimal("150")
            )
    
    def test_close_position(self):
        """Test closing a position."""
        portfolio = self.portfolio_service.create_portfolio(
            name="Test Portfolio",
            owner_id="user123",
            initial_capital=Decimal("100000")
        )
        
        # Open position
        position = self.portfolio_service.open_position(
            portfolio_id=portfolio.id,
            asset_id=self.asset1.id,
            position_type=PositionType.LONG,
            quantity=Decimal("100"),
            price=Decimal("150")
        )
        
        # Close position at higher price
        closed_position = self.portfolio_service.close_position(
            portfolio_id=portfolio.id,
            position_id=position.id,
            closing_price=Decimal("180")
        )
        
        self.assertEqual(closed_position.status, PositionStatus.CLOSED)
        self.assertIsNotNone(closed_position.closed_at)
        
        # Check capital was released
        updated_portfolio = self.portfolio_service.get_portfolio(portfolio.id)
        self.assertEqual(updated_portfolio.current_capital, Decimal("103000"))
    
    def test_update_position_price(self):
        """Test updating position price."""
        portfolio = self.portfolio_service.create_portfolio(
            name="Test Portfolio",
            owner_id="user123",
            initial_capital=Decimal("100000")
        )
        
        position = self.portfolio_service.open_position(
            portfolio_id=portfolio.id,
            asset_id=self.asset1.id,
            position_type=PositionType.LONG,
            quantity=Decimal("100"),
            price=Decimal("150")
        )
        
        updated_position = self.portfolio_service.update_position_price(
            portfolio_id=portfolio.id,
            position_id=position.id,
            new_price=Decimal("160")
        )
        
        self.assertEqual(updated_position.current_price, Decimal("160"))
    
    def test_get_portfolio_performance(self):
        """Test getting portfolio performance."""
        portfolio = self.portfolio_service.create_portfolio(
            name="Performance Test",
            owner_id="user123",
            initial_capital=Decimal("100000")
        )
        
        # Open two positions
        position1 = self.portfolio_service.open_position(
            portfolio_id=portfolio.id,
            asset_id=self.asset1.id,
            position_type=PositionType.LONG,
            quantity=Decimal("100"),
            price=Decimal("150")
        )
        
        position2 = self.portfolio_service.open_position(
            portfolio_id=portfolio.id,
            asset_id=self.asset2.id,
            position_type=PositionType.LONG,
            quantity=Decimal("50"),
            price=Decimal("200")
        )
        
        # Update prices
        self.portfolio_service.update_position_price(
            portfolio.id, position1.id, Decimal("160")
        )
        self.portfolio_service.update_position_price(
            portfolio.id, position2.id, Decimal("220")
        )
        
        performance = self.portfolio_service.get_portfolio_performance(portfolio.id)
        
        self.assertEqual(performance["initial_capital"], 100000.0)
        self.assertEqual(performance["open_positions"], 2)
        self.assertGreater(performance["total_pnl"], 0)
    
    def test_get_position_details(self):
        """Test getting position details."""
        portfolio = self.portfolio_service.create_portfolio(
            name="Details Test",
            owner_id="user123",
            initial_capital=Decimal("100000")
        )
        
        position = self.portfolio_service.open_position(
            portfolio_id=portfolio.id,
            asset_id=self.asset1.id,
            position_type=PositionType.LONG,
            quantity=Decimal("100"),
            price=Decimal("150")
        )
        
        details = self.portfolio_service.get_position_details(
            portfolio.id,
            position.id
        )
        
        self.assertEqual(details["asset_symbol"], "AAPL")
        self.assertEqual(details["quantity"], 100.0)
        self.assertEqual(details["average_cost"], 150.0)
        self.assertEqual(details["status"], "OPEN")


if __name__ == "__main__":
    unittest.main()
