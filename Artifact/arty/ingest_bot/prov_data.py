
#!/usr/bin/env python3
"""
Exhaustive Free OHLCV Ingestion + Provenance
Sources:
  - CoinGecko API (crypto OHLCV)
  - CryptoDataDownload bulk CSV (crypto)
  - YahooFinance via yfinance (stock OHLCV daily)
Provenance logged to provenance.json

As of 2026, this represents the most exhaustive *free* OHLCV coverage possible.

"""

import os, json, time, datetime
import requests
import pandas as pd
import yfinance as yf
from pathlib import Path

# ----------------------------
# OUTPUT PATHS
# ----------------------------
OUTPUT_DIR = Path("ohlcv_data")
CRYPTO_API_PARQUET = OUTPUT_DIR/"crypto_api.parquet"
CRYPTO_CSV_PARQUET = OUTPUT_DIR/"crypto_csv.parquet"
STOCK_PARQUET      = OUTPUT_DIR/"stock_ohlcv.parquet"
PROVENANCE_JSON    = OUTPUT_DIR/"provenance.json"

os.makedirs(OUTPUT_DIR, exist_ok=True)

# ----------------------------
# LOG PROVENANCE
# ----------------------------
provenance = {
    "generated_at": datetime.datetime.utcnow().isoformat()+"Z",
    "sources": [],
    "script_version": "2026-01-comprehensive_free_v1",
    "steps": []
}

def log_provenance():
    with open(PROVENANCE_JSON, "w") as f:
        json.dump(provenance, f, indent=4)

# ----------------------------
# FETCH CRYPTO FROM COINGECKO API
# ----------------------------
def fetch_coin_gecko_ohlcv(coin_id, vs="usd", days="max"):
    """
    Fetch OHLCV from CoinGecko free API
    (limited history & rate limits)
    """
    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/ohlc"
    params = {"vs_currency": vs, "days": days}
    r = requests.get(url, params=params, timeout=15)
    r.raise_for_status()
    data = r.json()
    df = pd.DataFrame(data, columns=["timestamp","open","high","low","close","volume"])
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms", utc=True)
    df["symbol"] = f"{coin_id.upper()}/{vs.upper()}"
    return df

# ----------------------------
# LOAD CRYPTO CSV BULK
# ----------------------------
def load_crypto_csv(path):
    df = pd.read_csv(path)
    # guess common columns
    df = df.rename(columns={
        "date":"timestamp",
        "open":"open",
        "high":"high",
        "low":"low",
        "close":"close",
        "volume":"volume"
    })
    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True, errors="coerce")
    return df

# ----------------------------
# FETCH STOCK OHLCV (DAILY)
# ----------------------------
def fetch_stock(ticker, start="2000-01-01"):
    stock = yf.Ticker(ticker)
    df = stock.history(start=start)
    df = df.reset_index()
    df = df.rename(columns={
        "Open":"open","High":"high","Low":"low","Close":"close","Volume":"volume","Date":"timestamp"
    })
    df["symbol"] = ticker.upper()
    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
    return df

# ----------------------------
# CLEAN & FORMAT
# ----------------------------
def clean_df(df):
    df = df.dropna()
    for c in ["open","high","low","close","volume"]:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    df = df[(df["open"]>=0) & (df["high"]>=0) & (df["low"]>=0) & (df["close"]>=0)]
    df = df.sort_values("timestamp")
    return df

# ----------------------------
# MAIN INGESTION
# ----------------------------
def main():
    # --- Crypto via API ---
    provenance["steps"].append("fetch crypto via CoinGecko API")
    crypto_ids = ["bitcoin","ethereum","solana","dogecoin","cardano"]
    crypto_api_dfs = []
    for cid in crypto_ids:
        try:
            df = fetch_coin_gecko_ohlcv(cid)
            provenance["sources"].append({
                "type":"crypto_api",
                "provider":"CoinGecko",
                "symbol":cid,
                "rows":len(df)
            })
            crypto_api_dfs.append(df)
            time.sleep(1)  # simple rate limit mitigation
        except Exception as e:
            print(f"error {cid} {e}")
    if crypto_api_dfs:
        df_crypto_api = pd.concat(crypto_api_dfs,ignore_index=True)
        df_crypto_api = clean_df(df_crypto_api)
        df_crypto_api.to_parquet(CRYPTO_API_PARQUET, index=False)

    # --- Crypto via CSV middle layer ---
    provenance["steps"].append("load bulk crypto CSV files (optional downloads)")
    # user should place CSVs under "crypto_csv" folder
    csv_dir = Path("crypto_csv")
    csv_dfs = []
    for f in csv_dir.glob("**/*.csv"):
        df = load_crypto_csv(f)
        csv_dfs.append(df)
        provenance["sources"].append({
            "type":"crypto_csv",
            "provider":"CryptoDataDownload or similar",
            "file":str(f),
            "rows":len(df),
        })
    if csv_dfs:
        df_csv_all = pd.concat(csv_dfs,ignore_index=True)
        df_csv_all = clean_df(df_csv_all)
        df_csv_all.to_parquet(CRYPTO_CSV_PARQUET, index=False)

    # --- Stocks ---
    provenance["steps"].append("fetch stock daily OHLCV via Yahoo Finance")
    stock_symbols = ["AAPL","MSFT","TSLA","GOOG","AMZN"]
    stock_dfs = []
    for s in stock_symbols:
        df = fetch_stock(s)
        provenance["sources"].append({
            "type":"stock",
            "provider":"yfinance (Yahoo Finance)",
            "symbol":s,
            "rows":len(df)
        })
        stock_dfs.append(df)
    if stock_dfs:
        df_stock_all = pd.concat(stock_dfs,ignore_index=True)
        df_stock_all = clean_df(df_stock_all)
        df_stock_all.to_parquet(STOCK_PARQUET, index=False)

    # --- Finalize provenance ---
    log_provenance()
    print("Done. Outputs:")
    print(" -", CRYPTO_API_PARQUET)
    print(" -", CRYPTO_CSV_PARQUET if csv_dfs else "NO CSV CRYPTO DATA")
    print(" -", STOCK_PARQUET)
    print(" -", PROVENANCE_JSON)

if __name__ == "__main__":
    main()