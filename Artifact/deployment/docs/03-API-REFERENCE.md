# API Reference

**Gold Standard Enterprise Suite v1.0.0**

---

## Enterprise Automation API

### EnterpriseManager

Main orchestrator for the entire automation system.

```python
from automata import EnterpriseManager

manager = EnterpriseManager()
```

#### Methods

**`async start()`**
- Starts all automation systems
- Returns: `None`

**`async stop()`**
- Stops all systems gracefully
- Returns: `None`

**`get_status() -> Dict[str, Any]`**
- Returns current system status
- Response:
```python
{
    "running": bool,
    "erp_systems": {"enabled": List[str], "sync_status": Dict},
    "social_media": {"queue_size": int, "posts_today": int},
    "ai_engine": {"provider": str, "generated_today": int}
}
```

**`get_analytics() -> Dict[str, Any]`**
- Returns comprehensive analytics
- See full schema in examples

---

### AI Engine API

#### ContentGenerator

```python
from automata.ai_engine import ContentGenerator

generator = ContentGenerator(config)
```

**`async generate(platform, topic=None, content_type="text", style=None, use_tools=False)`**
- Generates platform-specific content
- Parameters:
  - `platform` (str): Target platform
  - `topic` (str, optional): Content topic
  - `content_type` (str): Type of content
  - `style` (str, optional): Brand voice override
  - `use_tools` (bool): Enable tool calling

**`get_analytics() -> Dict[str, Any]`**
- Returns generation analytics

---

### ContextEngine

```python
from automata.ai_engine import ContextEngine

context = ContextEngine(config, provider)
```

**`async add_entry(role, content, metadata=None)`**
- Adds entry to context
- Parameters:
  - `role` (str): "user", "assistant", or "system"
  - `content` (str): Entry content
  - `metadata` (dict, optional): Additional metadata

**`get_context_for_prompt(max_tokens=3000) -> str`**
- Returns formatted context for AI prompt
- Parameters:
  - `max_tokens` (int): Maximum tokens to return

**`get_statistics() -> Dict[str, Any]`**
- Returns context statistics

---

## Business Infrastructure API

### MarketService

```python
from infra import MarketService

market_service = MarketService()
```

**`create_market(code, name, market_type, timezone) -> Market`**
- Creates new market
- Parameters:
  - `code` (str): Market code
  - `name` (str): Market name
  - `market_type` (MarketType): Type of market
  - `timezone` (str): Market timezone

---

### AssetService

```python
from infra import AssetService

asset_service = AssetService()
```

**`create_asset(symbol, name, asset_type, market_id) -> Asset`**
- Creates new asset
- Parameters:
  - `symbol` (str): Asset symbol
  - `name` (str): Asset name
  - `asset_type` (AssetType): Type of asset
  - `market_id` (str): Market identifier

---

### PortfolioService

```python
from infra import PortfolioService

portfolio_service = PortfolioService(asset_service)
```

**`create_portfolio(name, owner_id, initial_capital) -> Portfolio`**
- Creates new portfolio
- Parameters:
  - `name` (str): Portfolio name
  - `owner_id` (str): Owner identifier
  - `initial_capital` (Decimal): Starting capital

**`open_position(portfolio_id, asset_id, position_type, quantity, price) -> Position`**
- Opens a new position
- Parameters:
  - `portfolio_id` (str): Portfolio ID
  - `asset_id` (str): Asset ID
  - `position_type` (PositionType): LONG or SHORT
  - `quantity` (Decimal): Position size
  - `price` (Decimal): Entry price

**`get_portfolio_performance(portfolio_id) -> Dict[str, Any]`**
- Returns portfolio performance metrics
- Response includes: total_pnl, roi, sharpe_ratio, etc.

---

**Complete API documentation available in code docstrings.**

---

**Document Version:** 1.0.0  
**Last Updated:** January 2026
