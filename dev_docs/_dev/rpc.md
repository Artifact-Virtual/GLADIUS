---
title: RPC Interface
description: How to use the local RPC server to control Cthulu at runtime
---

# RPC Interface

Cthulu includes a lightweight, local-only RPC server to allow programmatic control at runtime. This enables external systems, scripts, and monitoring tools to inject trades and query system state.

## Overview

- **Server Address:** `127.0.0.1:8278` (default)
- **Endpoints:**
  - `POST /trade` - Submit a trade order
  - `GET /provenance` - Query order audit trail
- **Authentication:** Bearer token via `CTHULU_API_TOKEN` environment variable or `X-Api-Key` header

## Configuration

Enable RPC in your `config.json`:

```json
{
  "rpc": {
    "enabled": true,
    "host": "127.0.0.1",
    "port": 8278,
    "token": null
  }
}
```

Or set the token via environment variable:
```powershell
$env:CTHULU_API_TOKEN = "your-secret-token"
```

## Quick Start

### 1. Ensure Cthulu is Running

```powershell
python -m cthulu --config config.json --mindset ultra_aggressive --skip-setup
```

The RPC server starts automatically if enabled in config.

### 2. Place a Trade via PowerShell

```powershell
$body = @{
    symbol = "BTCUSD#"
    side = "BUY"
    volume = 0.01
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://127.0.0.1:8278/trade" `
    -Method POST `
    -ContentType "application/json" `
    -Body $body
```

### 3. Place a Trade via curl

```bash
curl -X POST \
  -H "Authorization: Bearer $CTHULU_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"symbol":"BTCUSD#","side":"BUY","volume":0.01}' \
  http://127.0.0.1:8278/trade
```

## API Reference

### POST /trade

Submit a market or limit order.

**Request Body:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `symbol` | string | Yes | Trading symbol (e.g., "BTCUSD#") |
| `side` | string | Yes | "BUY" or "SELL" |
| `volume` | number | Yes | Lot size |
| `price` | number | No | Limit price (omit for market order) |
| `sl` | number | No | Stop loss price |
| `tp` | number | No | Take profit price |

**Response (200 OK):**

```json
{
  "status": "FILLED",
  "order_id": 600994186,
  "fill_price": 89796.4,
  "filled_volume": 0.01,
  "message": null
}
```

**Response (403 Forbidden):**

```json
{
  "error": "Risk rejected",
  "reason": "Spread 2250.0 exceeds limit 5000.0"
}
```

### GET /provenance

Query recent order audit trail.

**Query Parameters:**
- `limit` (int, default 50): Number of records to return

**Response:**
```json
{
  "limit": 50,
  "results": [
    {
      "signal_id": "rpc_manual",
      "timestamp": "2025-12-29T13:30:04",
      "symbol": "BTCUSD#",
      "side": "BUY",
      "volume": 0.01,
      "order_id": 600994186
    }
  ]
}
```

## Behavior

1. **Risk Check:** All trades go through the same `RiskEvaluator` as organic signals. Spread limits, position limits, and circuit breakers apply.

2. **Idempotency:** Duplicate orders (same client_tag) are detected and rejected with a warning.

3. **Provenance:** Every RPC trade is logged with full provenance (signal_id, client_tag, caller, PID, TID, hostname).

4. **Position Tracking:** Filled orders are automatically tracked by `PositionManager` and recorded in the database.

## Security Best Practices

1. **Always use localhost binding** - The server defaults to 127.0.0.1. Never expose to external networks.

2. **Set a strong API token** - In production, always set `CTHULU_API_TOKEN`:
   ```powershell
   $env:CTHULU_API_TOKEN = [System.Guid]::NewGuid().ToString()
   ```

3. **Use firewall rules** - If you must expose to a network, use strict firewall rules.

4. **Monitor access logs** - RPC requests are logged. Review `logs/cthulu.log` for suspicious activity.

## Integration with Monitoring

The RPC server is used by the stress testing infrastructure:

- `monitoring/inject_signals.py` - Burst and pattern injection
- `monitoring/run_stress.ps1` - Full stress test orchestrator

See [observability_guide.md](../../monitoring/observability_guide.md) for complete testing instructions.

## Troubleshooting

### "SIMULATED (RPC down)" in inject logs

The RPC server is not responding. Check:
1. Cthulu is running: `Get-Process python | Where-Object {$_.CommandLine -match 'cthulu'}`
2. RPC port is open: `Test-NetConnection -ComputerName localhost -Port 8278`
3. Config has RPC enabled: `"rpc": {"enabled": true}`

### Connection Reset Errors

Under high load (>10 trades/sec), the HTTP server may timeout. The inject script falls back to simulation mode. For high-frequency testing, reduce injection rate.

### Risk Rejection

If trades are rejected with spread errors, verify:
1. `max_spread_points` is set in config.json (default 5000 for crypto)
2. `max_spread_pct` is set (default 0.05 = 5%)

## Implementation

The RPC server is implemented in `cthulu/rpc/server.py`. It integrates with:
- `ExecutionEngine` - Order placement
- `RiskEvaluator` - Trade approval
- `PositionManager` - Position tracking
- `Database` - Trade recording

---

*For more details, see [ARCHITECTURE.md](../ARCHITECTURE.md) and [OBSERVABILITY.md](../OBSERVABILITY.md).*





