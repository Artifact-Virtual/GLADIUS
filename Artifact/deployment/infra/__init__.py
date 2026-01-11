"""
Business Infrastructure for Market and Asset Management

A comprehensive, production-grade business layer for managing market data,
assets, portfolios, and trading operations in the Gold Standard system.

This package provides:
- Domain models for market entities (Asset, Market, Portfolio, Position)
- Repository pattern for data persistence
- Service layer for business logic
- Configuration management
- Logging and monitoring
- Error handling and validation
"""

__version__ = "1.0.0"
__author__ = "Gold Standard System"

from .core.exceptions import (
    BusinessInfrastructureError,
    ValidationError,
    DataNotFoundError,
    ConfigurationError,
    DataIntegrityError,
    BusinessLogicError,
    RepositoryError,
)
from .models.asset import Asset, AssetType, AssetStatus
from .models.market import Market, MarketStatus, MarketType
from .models.portfolio import Portfolio, PortfolioStatus
from .models.position import Position, PositionType, PositionStatus
from .services.market_service import MarketService
from .services.asset_service import AssetService
from .services.portfolio_service import PortfolioService
from .config.settings import config
from .utils.logging import get_logger

__all__ = [
    # Version
    "__version__",
    
    # Exceptions
    "BusinessInfrastructureError",
    "ValidationError",
    "DataNotFoundError",
    "ConfigurationError",
    "DataIntegrityError",
    "BusinessLogicError",
    "RepositoryError",
    
    # Models
    "Asset",
    "AssetType",
    "AssetStatus",
    "Market",
    "MarketStatus",
    "MarketType",
    "Portfolio",
    "PortfolioStatus",
    "Position",
    "PositionType",
    "PositionStatus",
    
    # Services
    "MarketService",
    "AssetService",
    "PortfolioService",
    
    # Configuration
    "config",
    
    # Utilities
    "get_logger",
]


# Initialize logging
logger = get_logger(__name__)
logger.info(f"Business Infrastructure v{__version__} initialized")
