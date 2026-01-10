# Cthulu / Herald — Stakeholder Summary

Purpose
- Cthulu (Herald) is an autonomous trading system focused on safe, auditable execution with strong observability, ML event instrumentation, and pluggable signal sources.

Key capabilities
- Real-time market connectivity (MetaTrader5)
- Modular strategy engine + indicator pipeline (RSI, MACD, EMA, ATR, Bollinger, VWAP, etc.)
- Dynamic SL/TP management (ATR-based, breakeven, trailing)
- Trade adoption for manual trades (with audit & protect)
- Advisory / ghost modes for non-destructive testing
- ML instrumentation (non-blocking gzipped JSONL event stream)
- Observability via metrics (Prometheus) and structured logs

Recent priorities
- Hardening dynamic SL/TP calculations and safety guards against tiny SL distances
- Fixing symbol selection mismatches (e.g., `GOLDm#` vs human names) and broker-min-stop checks
- Improving idempotency and single-writer guarantees to avoid duplicate close submissions

Current critical issues (status)
- Trades not being placed: strategies returning NO SIGNAL due to missing indicators (e.g., EMA missing or NaN) and conservative fallback rules. (Investigating)
- Repeated broker "Invalid stops" (10016) from attempts to set SLs inside broker min distance (fixed with pre-checks, more monitoring added).

Immediate next steps (today)
1. Audit commits since `9d428494...` for changes to indicators, strategy signal logic, and order placement paths.
2. Add integration tests for symbol selection, MT5 stop rejections, and indicator edge cases.
3. Fix indicator data path (ensure EMA and required inputs are present and NaN-handling robust); add monitoring alerts for missing indicators.
4. Run a short paper-trade canary with metrics and runbook monitoring.

Runbook highlights
- If strategies produce consecutive "NO SIGNAL": check indicator collector for NaNs and missing inputs; verify data feed and tick/ohlcv alignment.
- If MT5 returns `10016 Invalid stops`: inspect `trade_stops_level` and tick size; confirm SL > min_dist from current price; check logs `dynamic_sltp.skipped_too_close`.
- Emergency disable: set `config['dynamic_sltp']['enabled']=false` and `config['advisory']['log_only']=true` for safe pause.

Contact
- Engineering: ops@cthulu.local (or ping the on-call in Slack #cthulu)
- For urgent production rollback: revert the last deployment and engage the on-call.


*This file was generated automatically. For full technical detail see `_dev/features.md`, `_dev/04_DATA_FORMATS.md`, and `docs/08_POSITION_MANAGEMENT.md`.*
