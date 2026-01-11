"""
Example usage of the Business Infrastructure for Market and Asset Management.

This module demonstrates how to use the business infrastructure components
to manage markets, assets, and portfolios.
"""

from decimal import Decimal
from datetime import time

from infra import (
    # Services
    MarketService,
    AssetService,
    PortfolioService,
    # Models
    MarketType,
    AssetType,
    PositionType,
    # Configuration
    config,
    # Logging
    get_logger,
)


def setup_markets():
    """Example: Setting up markets."""
    logger = get_logger(__name__)
    market_service = MarketService()
    
    # Create NYSE
    nyse = market_service.create_market(
        code="NYSE",
        name="New York Stock Exchange",
        market_type=MarketType.STOCK_EXCHANGE,
        timezone="America/New_York",
        currency="USD",
        opening_time=time(9, 30),
        closing_time=time(16, 0),
        trading_days=[0, 1, 2, 3, 4]  # Monday-Friday
    )
    logger.info(f"Created market: {nyse}")
    
    # Create NASDAQ
    nasdaq = market_service.create_market(
        code="NASDAQ",
        name="NASDAQ Stock Market",
        market_type=MarketType.STOCK_EXCHANGE,
        timezone="America/New_York",
        currency="USD"
    )
    logger.info(f"Created market: {nasdaq}")
    
    # Open markets
    market_service.open_market(nyse.id)
    market_service.open_market(nasdaq.id)
    logger.info("Markets opened for trading")
    
    return market_service


def setup_assets(market_service):
    """Example: Setting up assets."""
    logger = get_logger(__name__)
    asset_service = AssetService()
    
    # Get markets
    nyse = market_service.get_market_by_code("NYSE")
    nasdaq = market_service.get_market_by_code("NASDAQ")
    
    # Create stocks
    assets = []
    
    apple = asset_service.create_asset(
        symbol="AAPL",
        name="Apple Inc.",
        asset_type=AssetType.STOCK,
        market_id=nasdaq.id,
        currency="USD"
    )
    assets.append(apple)
    logger.info(f"Created asset: {apple}")
    
    microsoft = asset_service.create_asset(
        symbol="MSFT",
        name="Microsoft Corporation",
        asset_type=AssetType.STOCK,
        market_id=nasdaq.id,
        currency="USD"
    )
    assets.append(microsoft)
    
    tesla = asset_service.create_asset(
        symbol="TSLA",
        name="Tesla Inc.",
        asset_type=AssetType.STOCK,
        market_id=nasdaq.id,
        currency="USD"
    )
    assets.append(tesla)
    
    # Create ETF
    spy = asset_service.create_asset(
        symbol="SPY",
        name="SPDR S&P 500 ETF",
        asset_type=AssetType.ETF,
        market_id=nyse.id,
        currency="USD"
    )
    assets.append(spy)
    
    logger.info(f"Created {len(assets)} assets")
    return asset_service, assets


def manage_portfolio(asset_service):
    """Example: Managing a portfolio."""
    logger = get_logger(__name__)
    portfolio_service = PortfolioService(asset_service=asset_service)
    
    # Create portfolio
    portfolio = portfolio_service.create_portfolio(
        name="Growth Portfolio",
        owner_id="trader_001",
        initial_capital=Decimal("100000"),
        base_currency="USD",
        description="Long-term growth focused portfolio"
    )
    logger.info(f"Created portfolio: {portfolio}")
    
    # Get assets
    aapl = asset_service.get_asset_by_symbol("AAPL")
    msft = asset_service.get_asset_by_symbol("MSFT")
    tsla = asset_service.get_asset_by_symbol("TSLA")
    
    # Open positions
    position1 = portfolio_service.open_position(
        portfolio_id=portfolio.id,
        asset_id=aapl.id,
        position_type=PositionType.LONG,
        quantity=Decimal("100"),
        price=Decimal("150.00")
    )
    logger.info(f"Opened position: {position1}")
    
    position2 = portfolio_service.open_position(
        portfolio_id=portfolio.id,
        asset_id=msft.id,
        position_type=PositionType.LONG,
        quantity=Decimal("50"),
        price=Decimal("300.00")
    )
    logger.info(f"Opened position: {position2}")
    
    position3 = portfolio_service.open_position(
        portfolio_id=portfolio.id,
        asset_id=tsla.id,
        position_type=PositionType.LONG,
        quantity=Decimal("75"),
        price=Decimal("200.00")
    )
    logger.info(f"Opened position: {position3}")
    
    # Simulate price updates
    logger.info("\n--- Simulating market price changes ---")
    portfolio_service.update_position_price(
        portfolio.id, position1.id, Decimal("165.00")
    )
    portfolio_service.update_position_price(
        portfolio.id, position2.id, Decimal("320.00")
    )
    portfolio_service.update_position_price(
        portfolio.id, position3.id, Decimal("180.00")
    )
    
    # Get portfolio performance
    performance = portfolio_service.get_portfolio_performance(portfolio.id)
    logger.info("\n--- Portfolio Performance ---")
    logger.info(f"Portfolio: {performance['name']}")
    logger.info(f"Status: {performance['status']}")
    logger.info(f"Initial Capital: ${performance['initial_capital']:,.2f}")
    logger.info(f"Current Capital: ${performance['current_capital']:,.2f}")
    logger.info(f"Total Market Value: ${performance['total_market_value']:,.2f}")
    logger.info(f"Total Portfolio Value: ${performance['total_value']:,.2f}")
    logger.info(f"Total Cost Basis: ${performance['total_cost_basis']:,.2f}")
    logger.info(f"Unrealized P&L: ${performance['unrealized_pnl']:,.2f}")
    logger.info(f"Total P&L: ${performance['total_pnl']:,.2f}")
    logger.info(f"Total P&L %: {performance['total_pnl_percent']:.2f}%")
    logger.info(f"Open Positions: {performance['open_positions']}")
    
    # Get individual position details
    logger.info("\n--- Position Details ---")
    for position_id in [position1.id, position2.id, position3.id]:
        details = portfolio_service.get_position_details(portfolio.id, position_id)
        logger.info(f"\n{details['asset_symbol']} ({details['asset_name']}):")
        logger.info(f"  Type: {details['position_type']}")
        logger.info(f"  Quantity: {details['quantity']}")
        logger.info(f"  Avg Cost: ${details['average_cost']:.2f}")
        logger.info(f"  Current Price: ${details['current_price']:.2f}")
        logger.info(f"  Cost Basis: ${details['cost_basis']:,.2f}")
        logger.info(f"  Market Value: ${details['market_value']:,.2f}")
        logger.info(f"  Unrealized P&L: ${details['unrealized_pnl']:,.2f} ({details['unrealized_pnl_percent']:.2f}%)")
    
    # Close one position
    logger.info("\n--- Closing TSLA Position ---")
    closed_position = portfolio_service.close_position(
        portfolio_id=portfolio.id,
        position_id=position3.id,
        closing_price=Decimal("180.00")
    )
    logger.info(f"Closed position: {closed_position}")
    
    # Final performance
    final_performance = portfolio_service.get_portfolio_performance(portfolio.id)
    logger.info("\n--- Final Portfolio Performance ---")
    logger.info(f"Current Capital: ${final_performance['current_capital']:,.2f}")
    logger.info(f"Open Positions: {final_performance['open_positions']}")
    logger.info(f"Closed Positions: {final_performance['closed_positions']}")
    logger.info(f"Total P&L: ${final_performance['total_pnl']:,.2f} ({final_performance['total_pnl_percent']:.2f}%)")
    
    return portfolio_service


def main():
    """Main example execution."""
    logger = get_logger(__name__)
    logger.info("=== Business Infrastructure Example ===\n")
    
    # Configure logging
    config.set("logging.level", "INFO")
    
    # Set up markets
    logger.info("Step 1: Setting up markets")
    market_service = setup_markets()
    
    # Set up assets
    logger.info("\nStep 2: Setting up assets")
    asset_service, assets = setup_assets(market_service)
    
    # Manage portfolio
    logger.info("\nStep 3: Managing portfolio")
    portfolio_service = manage_portfolio(asset_service)
    
    logger.info("\n=== Example Complete ===")


if __name__ == "__main__":
    main()
