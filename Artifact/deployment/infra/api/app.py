"""FastAPI HTTP API for the infra services.

Endpoints:
- POST /markets -> create a market
- GET /markets -> list markets
- POST /assets -> create an asset
- GET /assets -> list assets
- POST /prices -> ingest a price update ({symbol, price, timestamp})
"""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List
import os

from ..services.market_service import MarketService
from ..services.asset_service import AssetService
from ..services.portfolio_service import PortfolioService
from ..repositories.sql_repository import MarketSqlRepository, AssetSqlRepository
from ..repositories.portfolio_repository import PortfolioRepository
from ..models.market import MarketType

app = FastAPI(title="Infra API")

# Use SQLite-backed repositories by default
market_repo = MarketSqlRepository()
asset_repo = AssetSqlRepository()
portfolio_repo = PortfolioRepository()  # keep in-memory for now

market_service = MarketService(repository=market_repo)
asset_service = AssetService(repository=asset_repo)
portfolio_service = PortfolioService(repository=portfolio_repo, asset_service=asset_service)


class MarketIn(BaseModel):
    code: str
    name: str
    market_type: str
    timezone: str
    currency: Optional[str] = "USD"


class AssetIn(BaseModel):
    symbol: str
    name: str
    asset_type: str
    market_code: str
    currency: Optional[str] = "USD"


class PriceIn(BaseModel):
    symbol: str
    price: float
    timestamp: Optional[str] = None


@app.post('/markets')
def create_market(payload: MarketIn):
    try:
        mtype = MarketType[payload.market_type]
    except Exception:
        raise HTTPException(status_code=400, detail='Invalid market_type')
    try:
        m = market_service.create_market(code=payload.code, name=payload.name, market_type=mtype, timezone=payload.timezone, currency=payload.currency)
        return {'success': True, 'id': m.id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get('/markets')
def list_markets():
    ms = market_service.list_all_markets()
    return [m.to_dict() for m in ms]


@app.post('/assets')
def create_asset(payload: AssetIn):
    market = market_service.get_market_by_code(payload.market_code)
    if not market:
        raise HTTPException(status_code=404, detail='Market not found')
    from ..models.asset import AssetType
    try:
        atype = AssetType[payload.asset_type]
    except Exception:
        raise HTTPException(status_code=400, detail='Invalid asset_type')
    try:
        a = asset_service.create_asset(symbol=payload.symbol, name=payload.name, asset_type=atype, market_id=market.id, currency=payload.currency)
        return {'success': True, 'id': a.id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get('/assets')
def list_assets():
    assets = asset_service.list_all_assets()
    return [a.to_dict() for a in assets]


@app.post('/prices')
def ingest_price(payload: PriceIn):
    # Find asset
    asset = asset_service.get_asset_by_symbol(payload.symbol)
    if not asset:
        raise HTTPException(status_code=404, detail='Asset not found')

    # Update any portfolio positions that reference this asset
    updated = []
    for p in portfolio_service.list_all_portfolios():
        for pos in p.get_open_positions():
            if pos.asset_id == asset.id:
                portfolio_service.update_position_price(p.id, pos.id, payload.price)
                updated.append({'portfolio_id': p.id, 'position_id': pos.id})

    return {'success': True, 'updated_positions': updated}


# --- Portfolio endpoints ---

class PortfolioIn(BaseModel):
    name: str
    owner_id: str
    initial_capital: float
    base_currency: Optional[str] = "USD"


class PositionIn(BaseModel):
    asset_symbol: str
    position_type: str  # LONG or SHORT
    quantity: float
    price: float


@app.post('/portfolios')
def create_portfolio(payload: PortfolioIn):
    try:
        p = portfolio_service.create_portfolio(name=payload.name, owner_id=payload.owner_id, initial_capital=payload.initial_capital, base_currency=payload.base_currency)
        return {'success': True, 'id': p.id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post('/portfolios/{portfolio_id}/positions')
def open_position(portfolio_id: str, payload: PositionIn):
    asset = asset_service.get_asset_by_symbol(payload.asset_symbol)
    if not asset:
        raise HTTPException(status_code=404, detail='Asset not found')
    from ..models.position import PositionType
    try:
        ptype = PositionType[payload.position_type]
    except Exception:
        raise HTTPException(status_code=400, detail='Invalid position_type')
    try:
        pos = portfolio_service.open_position(portfolio_id=portfolio_id, asset_id=asset.id, position_type=ptype, quantity=payload.quantity, price=payload.price)
        return {'success': True, 'id': pos.id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get('/portfolios/{portfolio_id}')
def get_portfolio(portfolio_id: str):
    try:
        perf = portfolio_service.get_portfolio_performance(portfolio_id)
        return {'success': True, 'performance': perf}
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.get('/portfolios')
def list_portfolios():
    ps = portfolio_service.list_all_portfolios()
    return [p.to_dict() for p in ps]


if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='127.0.0.1', port=int(os.getenv('INFRA_PORT', 7000)))