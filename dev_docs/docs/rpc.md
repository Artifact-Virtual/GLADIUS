# RPC Server

Herald includes a lightweight local RPC server to allow runtime instruction (e.g., placing a manual trade).

- Enabled with CLI flag `--enable-rpc` or by setting the `HERALD_API_TOKEN` env var (the server will also start automatically if a token is in the environment).
- Note: enabling RPC with `--enable-rpc` without `HERALD_API_TOKEN` will run the server **without authentication** (still recommended to bind to localhost only). The server will log a warning in this case.
- Bind address and port: `--rpc-host` (default `127.0.0.1`), `--rpc-port` (default `8181`).
- Authentication: Provide `HERALD_API_TOKEN` as a Bearer token in the `Authorization` header or via `X-Api-Key`.

Security recommendations:

- Only bind to localhost unless you know what you're doing.
- Use a strong token and keep it in an environment variable or a secrets manager.
- Do not expose the RPC port to public networks.

Example usage:

```bash
export HERALD_API_TOKEN=mysecret
herald --config config.json --enable-rpc
python scripts/place_trade_via_rpc.py --symbol BTCUSD#m --side BUY --volume 0.01
````markdown
# RPC Server

Herald includes a lightweight local RPC server to allow runtime instructions (for example, placing a manual trade).

- Default behavior: the RPC server is started by default when Herald launches and binds to `127.0.0.1:8181` (local only).
- Backward-compatibility: older CLI flags such as `--enable-rpc` are still recognized.
- Authentication: provide `HERALD_API_TOKEN` as a Bearer token in the `Authorization` header or via `X-Api-Key`. If `HERALD_API_TOKEN` is not set the server will run unauthenticated but remains bound to localhost (not recommended for production).

Security recommendations:

- Only bind to localhost unless you know what you're doing.
- Use a strong token and keep it in an environment variable or a secrets manager.
- Do not expose the RPC port to public networks.

Example usage:

```bash
export HERALD_API_TOKEN=mysecret
herald --config config.json
python scripts/place_trade_via_rpc.py --symbol BTCUSD#m --side BUY --volume 0.01
```

The RPC endpoint currently implements:
- POST /trade — place a manual trade: {symbol, side, volume, price?, sl?, tp?}

````
