"""Seed script to create markets and assets for Gold and Bitcoin and create a test portfolio.

Usage: python infra/scripts/seed_gold_bitcoin.py
"""
import requests
import time

API = "http://127.0.0.1:7000"

# Create markets
markets = [
    {"code": "COMEX", "name": "COMEX (Gold Futures)", "market_type": "COMMODITIES_EXCHANGE", "timezone": "America/New_York", "currency": "USD"},
    {"code": "BINANCE", "name": "Binance", "market_type": "CRYPTO_EXCHANGE", "timezone": "UTC", "currency": "USD"}
]

for m in markets:
    r = requests.post(f"{API}/markets", json=m)
    print('market', m['code'], r.status_code, r.json())

# Create assets
assets = [
    {"symbol": "GOLD", "name": "Gold Spot", "asset_type": "COMMODITY", "market_code": "COMEX", "currency": "USD"},
    {"symbol": "BTC-USD", "name": "Bitcoin USD", "asset_type": "CRYPTOCURRENCY", "market_code": "BINANCE", "currency": "USD"}
]

for a in assets:
    r = requests.post(f"{API}/assets", json=a)
    print('asset', a['symbol'], r.status_code, r.json())

# Create portfolio
p = {
    "name": "Test Portfolio",
    "owner_id": "tester",
    "initial_capital": 100000
}
resp = requests.post(f"{API}/portfolios", json=p)
print('portfolio', resp.status_code, resp.json())
portfolio_id = resp.json().get('id')

# Open positions: buy 10 oz GOLD at 2000 and 0.5 BTC at 40000
positions = [
    {"asset_symbol": "GOLD", "position_type": "LONG", "quantity": 10, "price": 2000},
    {"asset_symbol": "BTC-USD", "position_type": "LONG", "quantity": 0.5, "price": 40000}
]

for pos in positions:
    r = requests.post(f"{API}/portfolios/{portfolio_id}/positions", json=pos)
    print('open position', pos['asset_symbol'], r.status_code, r.json())

# Give API a moment
time.sleep(0.5)

# Print portfolio
r = requests.get(f"{API}/portfolios/{portfolio_id}")
print('portfolio status', r.status_code, r.json())
