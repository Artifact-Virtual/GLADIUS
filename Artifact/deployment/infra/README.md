# Business Infrastructure for Market and Asset Management

A comprehensive business layer for managing market data, assets, portfolios, and trading operations in the ARTIFACT VIRTUAL system.

- **Market**: Represents trading venues (NYSE, NASDAQ, etc.)
- **Asset**: Represents financial instruments (stocks, bonds, cryptocurrencies, etc.)
- **Portfolio**: Manages collections of positions with performance tracking
- **Position**: Tracks individual asset holdings with P&L calculations

### Business Services
- **MarketService**: High-level operations for market management
- **AssetService**: Asset lifecycle management and queries
- **PortfolioService**: Complete portfolio and position management

### Infrastructure Components
- **Repository Pattern**: Abstracted data persistence layer
- **Configuration Management**: Centralized, environment-aware configuration
- **Logging System**: Structured logging with flexible output options
- **Validation Framework**: Comprehensive input validation
- **Exception Hierarchy**: Well-defined error handling

## Architecture

```
infra/
├── core/                   # Core infrastructure components
│   ├── base_model.py      # Base class for all domain models
│   ├── repository.py      # Repository pattern implementation
│   └── exceptions.py      # Custom exception hierarchy
├── models/                 # Domain models
│   ├── asset.py
│   ├── market.py
│   ├── portfolio.py
│   └── position.py
├── repositories/           # Data persistence layer
│   ├── asset_repository.py
│   ├── market_repository.py
│   └── portfolio_repository.py
├── services/              # Business logic layer
│   ├── asset_service.py
│   ├── market_service.py
│   └── portfolio_service.py
├── config/                # Configuration management
│   └── settings.py
├── utils/                 # Utility functions
│   ├── logging.py
│   └── validators.py
└── tests/                 # Comprehensive test suite
    ├── test_asset.py
    ├── test_market.py
    └── test_portfolio.py
```

## Quick Start

### Installation

```bash
# No external dependencies required - pure Python implementation
cd infra
```

### Basic Usage

```python
from decimal import Decimal
from infra import (
    MarketService,
    AssetService,
    PortfolioService,
    MarketType,
    AssetType,
    PositionType,
)

# Create services
market_service = MarketService()
asset_service = AssetService()
portfolio_service = PortfolioService(asset_service=asset_service)

# Create a market
nasdaq = market_service.create_market(
    code="NASDAQ",
    name="NASDAQ Stock Market",
    market_type=MarketType.STOCK_EXCHANGE,
    timezone="America/New_York",
    currency="USD"
)

# Create an asset
apple = asset_service.create_asset(
    symbol="AAPL",
    name="Apple Inc.",
    asset_type=AssetType.STOCK,
    market_id=nasdaq.id,
    currency="USD"
)

# Create a portfolio
portfolio = portfolio_service.create_portfolio(
    name="My Portfolio",
    owner_id="trader_001",
    initial_capital=Decimal("100000"),
    base_currency="USD"
)

# Open a position
position = portfolio_service.open_position(
    portfolio_id=portfolio.id,
    asset_id=apple.id,
    position_type=PositionType.LONG,
    quantity=Decimal("100"),
    price=Decimal("150.00")
)

# Update price and get performance
portfolio_service.update_position_price(
    portfolio.id,
    position.id,
    Decimal("165.00")
)

performance = portfolio_service.get_portfolio_performance(portfolio.id)
print(f"Total P&L: ${performance['total_pnl']:,.2f}")
print(f"P&L %: {performance['total_pnl_percent']:.2f}%")
```

## Running Examples

```bash
# Run the comprehensive example
cd /home/runner/work/_dev/_dev
python -m infra.example_usage
```

## Running Tests

```bash
# Run all tests
cd /home/runner/work/_dev/_dev
python -m unittest discover infra/tests -v

# Run specific test module
python -m unittest infra.tests.test_asset
python -m unittest infra.tests.test_market
python -m unittest infra.tests.test_portfolio
```

## Key Design Principles

### 1. **Separation of Concerns**
- Clear separation between models, repositories, and services
- Each layer has a single, well-defined responsibility

### 2. **Type Safety**
- Extensive use of enums for status and type fields
- Decimal type for all financial calculations (avoiding float precision issues)

### 3. **Validation**
- All models validate themselves before persistence
- Business logic enforced at service layer
- Comprehensive error messages with context

### 4. **Immutability of History**
- Timestamps track creation and updates
- Closed positions preserve historical data
- Audit trail through model lifecycle

### 5. **Extensibility**
- Easy to add new asset types, market types, etc.
- Repository pattern allows swapping storage backends
- Configuration system supports multiple environments

## Domain Models

### Market
Represents a trading venue where assets are traded.

**Attributes:**
- Code, Name, Type (Stock Exchange, Crypto Exchange, etc.)
- Timezone, Currency
- Trading hours and trading days
- Status (Open, Closed, Halted, etc.)

### Asset
Represents a financial instrument that can be traded.

**Attributes:**
- Symbol, Name, Type (Stock, Bond, Cryptocurrency, etc.)
- Market ID, Currency
- Status (Active, Inactive, Suspended, Delisted)
- Metadata for asset-specific information

### Portfolio
Manages a collection of positions with performance tracking.

**Attributes:**
- Name, Description, Owner ID
- Initial and current capital
- Base currency
- Status (Active, Inactive, Frozen, Liquidating)
- List of positions

**Key Methods:**
- `get_total_market_value()`: Current value of all positions
- `get_total_pnl()`: Total profit/loss
- `get_total_pnl_percent()`: P&L as percentage
- `allocate_capital()`: Lock capital for new positions
- `release_capital()`: Free up capital from closed positions

### Position
Tracks an individual holding of an asset.

**Attributes:**
- Portfolio ID, Asset ID
- Type (Long, Short)
- Quantity, Average Cost, Current Price
- Status (Open, Closed, Pending)
- Opened/Closed timestamps

**Key Methods:**
- `get_cost_basis()`: Total cost of position
- `get_market_value()`: Current market value
- `get_unrealized_pnl()`: Profit/loss (unrealized)
- `get_unrealized_pnl_percent()`: P&L as percentage
- `increase_position()`: Add to existing position
- `reduce_position()`: Partial close

## Configuration

The system supports configuration through:
1. Environment variables
2. JSON configuration files
3. Default values

```python
from infra import config

# Get configuration
log_level = config.get("logging.level")
max_positions = config.get("portfolio.max_positions_per_portfolio")

# Set configuration
config.set("logging.level", "DEBUG")

# Load from file
config.load_from_file("config.json")
```

## Error Handling

Comprehensive exception hierarchy:

- `BusinessInfrastructureError`: Base exception
  - `ValidationError`: Data validation failures
  - `DataNotFoundError`: Entity not found
  - `ConfigurationError`: Configuration issues
  - `DataIntegrityError`: Data integrity violations
  - `BusinessLogicError`: Business rule violations
  - `RepositoryError`: Repository operation failures

All exceptions include detailed context and error messages.

## Testing

The system includes comprehensive unit tests covering:

- Model validation and business logic
- Service layer operations
- Repository functionality
- Edge cases and error conditions
- Performance calculations

Test coverage includes:
- Happy path scenarios
- Error conditions
- Boundary cases
- Integration between components

## Integration with Gold Standard

This business infrastructure is designed to integrate seamlessly with the Gold Standard market analysis system:

1. **Market Data Pipeline**: Assets and markets provide the foundation for data ingestion
2. **Portfolio Analysis**: Track performance of trading strategies
3. **Herald Trading Agent**: Position management for automated trading
4. **Reporting**: Portfolio performance feeds into analysis reports
5. **Risk Management**: Position and portfolio constraints enforce risk limits

## Future Enhancements

Potential areas for expansion:

1. **Persistence Layer**: Database integration (PostgreSQL, MongoDB, etc.)
2. **Market Data Integration**: Real-time price feeds
3. **Order Management**: Order placement and execution tracking
4. **Risk Metrics**: VaR, Sharpe ratio, drawdown calculations
5. **Tax Reporting**: Capital gains tracking and reporting
6. **Multi-Currency**: Currency conversion and FX positions
7. **Performance Attribution**: Analyze sources of returns
8. **Backtesting Integration**: Historical portfolio simulation

## License

This is a private development repository. All rights reserved.

## Disclaimer

This system is not financial advice and is provided for informational and operational purposes only. Use at your own risk.
