"""
Unit tests for Market model and MarketService.
"""

import unittest
import sys
from pathlib import Path
from datetime import time

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from infra.models.market import Market, MarketType, MarketStatus
from infra.services.market_service import MarketService
from infra.core.exceptions import ValidationError, BusinessLogicError, DataNotFoundError


class TestMarketModel(unittest.TestCase):
    """Test cases for Market model."""
    
    def test_create_market(self):
        """Test creating a valid market."""
        market = Market(
            code="NYSE",
            name="New York Stock Exchange",
            market_type=MarketType.STOCK_EXCHANGE,
            timezone="America/New_York",
            currency="USD",
            opening_time=time(9, 30),
            closing_time=time(16, 0)
        )
        
        self.assertEqual(market.code, "NYSE")
        self.assertEqual(market.name, "New York Stock Exchange")
        self.assertEqual(market.market_type, MarketType.STOCK_EXCHANGE)
        self.assertEqual(market.status, MarketStatus.CLOSED)
        self.assertFalse(market.is_open())
    
    def test_market_validation(self):
        """Test market validation."""
        market = Market(
            code="NASDAQ",
            name="NASDAQ",
            market_type=MarketType.STOCK_EXCHANGE,
            timezone="America/New_York"
        )
        
        # Should not raise
        market.validate()
        
        # Test invalid code
        market.code = ""
        with self.assertRaises(ValidationError):
            market.validate()
        
        # Test invalid currency
        market.code = "NASDAQ"
        market.currency = "DOLLAR"
        with self.assertRaises(ValidationError):
            market.validate()
    
    def test_market_status_changes(self):
        """Test market status transitions."""
        market = Market(
            code="NYSE",
            name="New York Stock Exchange",
            market_type=MarketType.STOCK_EXCHANGE,
            timezone="America/New_York"
        )
        
        self.assertFalse(market.is_open())
        
        market.open_market()
        self.assertEqual(market.status, MarketStatus.OPEN)
        self.assertTrue(market.is_open())
        
        market.halt_trading()
        self.assertEqual(market.status, MarketStatus.HALTED)
        
        market.close_market()
        self.assertEqual(market.status, MarketStatus.CLOSED)
    
    def test_trading_days(self):
        """Test trading days functionality."""
        market = Market(
            code="NYSE",
            name="New York Stock Exchange",
            market_type=MarketType.STOCK_EXCHANGE,
            timezone="America/New_York",
            trading_days=[0, 1, 2, 3, 4]  # Monday-Friday
        )
        
        # Monday-Friday should be trading days
        for day in range(5):
            self.assertTrue(market.is_trading_day(day))
        
        # Saturday-Sunday should not be
        self.assertFalse(market.is_trading_day(5))
        self.assertFalse(market.is_trading_day(6))


class TestMarketService(unittest.TestCase):
    """Test cases for MarketService."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.service = MarketService()
    
    def tearDown(self):
        """Clean up after tests."""
        self.service.repository.clear()
    
    def test_create_market(self):
        """Test creating market through service."""
        market = self.service.create_market(
            code="NASDAQ",
            name="NASDAQ Stock Market",
            market_type=MarketType.STOCK_EXCHANGE,
            timezone="America/New_York"
        )
        
        self.assertIsNotNone(market.id)
        self.assertEqual(market.code, "NASDAQ")
        self.assertEqual(market.status, MarketStatus.CLOSED)
    
    def test_create_duplicate_market(self):
        """Test creating market with duplicate code."""
        self.service.create_market(
            code="NYSE",
            name="New York Stock Exchange",
            market_type=MarketType.STOCK_EXCHANGE,
            timezone="America/New_York"
        )
        
        with self.assertRaises(BusinessLogicError):
            self.service.create_market(
                code="NYSE",
                name="NYSE Duplicate",
                market_type=MarketType.STOCK_EXCHANGE,
                timezone="America/New_York"
            )
    
    def test_get_market_by_code(self):
        """Test retrieving market by code."""
        created = self.service.create_market(
            code="LSE",
            name="London Stock Exchange",
            market_type=MarketType.STOCK_EXCHANGE,
            timezone="Europe/London"
        )
        
        retrieved = self.service.get_market_by_code("LSE")
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.id, created.id)
    
    def test_list_open_markets(self):
        """Test listing open markets."""
        market1 = self.service.create_market(
            code="NYSE",
            name="NYSE",
            market_type=MarketType.STOCK_EXCHANGE,
            timezone="America/New_York"
        )
        
        market2 = self.service.create_market(
            code="NASDAQ",
            name="NASDAQ",
            market_type=MarketType.STOCK_EXCHANGE,
            timezone="America/New_York"
        )
        
        # Open first market
        self.service.open_market(market1.id)
        
        open_markets = self.service.list_open_markets()
        self.assertEqual(len(open_markets), 1)
        self.assertEqual(open_markets[0].code, "NYSE")
    
    def test_open_close_market(self):
        """Test opening and closing markets."""
        market = self.service.create_market(
            code="TSE",
            name="Tokyo Stock Exchange",
            market_type=MarketType.STOCK_EXCHANGE,
            timezone="Asia/Tokyo"
        )
        
        # Open
        updated = self.service.open_market(market.id)
        self.assertEqual(updated.status, MarketStatus.OPEN)
        
        # Close
        updated = self.service.close_market(market.id)
        self.assertEqual(updated.status, MarketStatus.CLOSED)
    
    def test_market_status_summary(self):
        """Test getting market status summary."""
        self.service.create_market(
            code="NYSE",
            name="NYSE",
            market_type=MarketType.STOCK_EXCHANGE,
            timezone="America/New_York"
        )
        
        market2 = self.service.create_market(
            code="NASDAQ",
            name="NASDAQ",
            market_type=MarketType.STOCK_EXCHANGE,
            timezone="America/New_York"
        )
        
        self.service.open_market(market2.id)
        
        summary = self.service.get_market_status_summary()
        self.assertEqual(summary[MarketStatus.CLOSED.value], 1)
        self.assertEqual(summary[MarketStatus.OPEN.value], 1)


if __name__ == "__main__":
    unittest.main()
