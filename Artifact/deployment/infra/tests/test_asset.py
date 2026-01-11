"""
Unit tests for Asset model and AssetService.
"""

import unittest
import sys
from pathlib import Path
from decimal import Decimal

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from infra.models.asset import Asset, AssetType, AssetStatus
from infra.services.asset_service import AssetService
from infra.core.exceptions import ValidationError, BusinessLogicError, DataNotFoundError


class TestAssetModel(unittest.TestCase):
    """Test cases for Asset model."""
    
    def test_create_asset(self):
        """Test creating a valid asset."""
        asset = Asset(
            symbol="AAPL",
            name="Apple Inc.",
            asset_type=AssetType.STOCK,
            market_id="NYSE",
            currency="USD"
        )
        
        self.assertEqual(asset.symbol, "AAPL")
        self.assertEqual(asset.name, "Apple Inc.")
        self.assertEqual(asset.asset_type, AssetType.STOCK)
        self.assertEqual(asset.status, AssetStatus.ACTIVE)
        self.assertTrue(asset.is_active())
    
    def test_asset_validation(self):
        """Test asset validation."""
        asset = Asset(
            symbol="AAPL",
            name="Apple Inc.",
            asset_type=AssetType.STOCK,
            market_id="NYSE"
        )
        
        # Should not raise
        asset.validate()
        
        # Test invalid symbol
        asset.symbol = ""
        with self.assertRaises(ValidationError):
            asset.validate()
        
        # Test invalid currency
        asset.symbol = "AAPL"
        asset.currency = "US"
        with self.assertRaises(ValidationError):
            asset.validate()
    
    def test_asset_status_changes(self):
        """Test asset status transitions."""
        asset = Asset(
            symbol="AAPL",
            name="Apple Inc.",
            asset_type=AssetType.STOCK,
            market_id="NYSE"
        )
        
        self.assertTrue(asset.is_active())
        
        asset.deactivate()
        self.assertEqual(asset.status, AssetStatus.INACTIVE)
        
        asset.activate()
        self.assertEqual(asset.status, AssetStatus.ACTIVE)
        
        asset.suspend()
        self.assertEqual(asset.status, AssetStatus.SUSPENDED)
        
        asset.delist()
        self.assertEqual(asset.status, AssetStatus.DELISTED)


class TestAssetService(unittest.TestCase):
    """Test cases for AssetService."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.service = AssetService()
    
    def tearDown(self):
        """Clean up after tests."""
        self.service.repository.clear()
    
    def test_create_asset(self):
        """Test creating asset through service."""
        asset = self.service.create_asset(
            symbol="MSFT",
            name="Microsoft Corporation",
            asset_type=AssetType.STOCK,
            market_id="NASDAQ"
        )
        
        self.assertIsNotNone(asset.id)
        self.assertEqual(asset.symbol, "MSFT")
        self.assertTrue(asset.is_active())
    
    def test_create_duplicate_asset(self):
        """Test creating asset with duplicate symbol."""
        self.service.create_asset(
            symbol="GOOGL",
            name="Alphabet Inc.",
            asset_type=AssetType.STOCK,
            market_id="NASDAQ"
        )
        
        with self.assertRaises(BusinessLogicError):
            self.service.create_asset(
                symbol="GOOGL",
                name="Google",
                asset_type=AssetType.STOCK,
                market_id="NASDAQ"
            )
    
    def test_get_asset_by_symbol(self):
        """Test retrieving asset by symbol."""
        created = self.service.create_asset(
            symbol="TSLA",
            name="Tesla Inc.",
            asset_type=AssetType.STOCK,
            market_id="NASDAQ"
        )
        
        retrieved = self.service.get_asset_by_symbol("TSLA")
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.id, created.id)
        
        # Test non-existent symbol
        none_asset = self.service.get_asset_by_symbol("NONEXISTENT")
        self.assertIsNone(none_asset)
    
    def test_list_assets_by_type(self):
        """Test listing assets by type."""
        self.service.create_asset(
            symbol="AAPL",
            name="Apple",
            asset_type=AssetType.STOCK,
            market_id="NASDAQ"
        )
        
        self.service.create_asset(
            symbol="BTC-USD",
            name="Bitcoin",
            asset_type=AssetType.CRYPTOCURRENCY,
            market_id="COINBASE"
        )
        
        stocks = self.service.list_assets_by_type(AssetType.STOCK)
        self.assertEqual(len(stocks), 1)
        
        crypto = self.service.list_assets_by_type(AssetType.CRYPTOCURRENCY)
        self.assertEqual(len(crypto), 1)
    
    def test_activate_deactivate_asset(self):
        """Test activating and deactivating assets."""
        asset = self.service.create_asset(
            symbol="AMZN",
            name="Amazon",
            asset_type=AssetType.STOCK,
            market_id="NASDAQ"
        )
        
        # Deactivate
        updated = self.service.deactivate_asset(asset.id)
        self.assertEqual(updated.status, AssetStatus.INACTIVE)
        
        # Activate
        updated = self.service.activate_asset(asset.id)
        self.assertEqual(updated.status, AssetStatus.ACTIVE)
    
    def test_search_assets(self):
        """Test searching assets."""
        self.service.create_asset(
            symbol="AAPL",
            name="Apple Inc.",
            asset_type=AssetType.STOCK,
            market_id="NASDAQ"
        )
        
        self.service.create_asset(
            symbol="MSFT",
            name="Microsoft Corporation",
            asset_type=AssetType.STOCK,
            market_id="NASDAQ"
        )
        
        results = self.service.search_assets("apple")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].symbol, "AAPL")


if __name__ == "__main__":
    unittest.main()
