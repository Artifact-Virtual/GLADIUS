"""SQLite-backed repository implementations for infra.

Provides AssetSqlRepository and MarketSqlRepository that mirror the
in-memory repository API but persist to a SQLite database file.
"""
import sqlite3
import json
from typing import Optional, List
from pathlib import Path
from datetime import datetime

from ..models.asset import Asset
from ..models.market import Market
from ..core.exceptions import RepositoryError, DataNotFoundError

DB_PATH = Path.home() / ".automata_infra" / "infra.db"
DB_PATH.parent.mkdir(parents=True, exist_ok=True)

def _now_iso():
    return datetime.utcnow().isoformat()

class SQLiteBase:
    def __init__(self, db_path: Optional[str] = None):
        self.db_path = str(db_path or DB_PATH)
        self._conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self._conn.execute("PRAGMA foreign_keys = ON")
        self._ensure_tables()

    def _ensure_tables(self):
        # markets
        self._conn.execute("""
        CREATE TABLE IF NOT EXISTS markets (
            id TEXT PRIMARY KEY,
            code TEXT UNIQUE,
            name TEXT,
            market_type TEXT,
            timezone TEXT,
            currency TEXT,
            status TEXT,
            opening_time TEXT,
            closing_time TEXT,
            trading_days TEXT,
            metadata TEXT,
            created_at TEXT,
            updated_at TEXT
        )
        """)

        # assets
        self._conn.execute("""
        CREATE TABLE IF NOT EXISTS assets (
            id TEXT PRIMARY KEY,
            symbol TEXT UNIQUE,
            name TEXT,
            asset_type TEXT,
            status TEXT,
            market_id TEXT,
            currency TEXT,
            metadata TEXT,
            created_at TEXT,
            updated_at TEXT,
            FOREIGN KEY(market_id) REFERENCES markets(id) ON DELETE SET NULL
        )
        """)
        self._conn.commit()

    def close(self):
        self._conn.close()


class MarketSqlRepository(SQLiteBase):
    def create(self, market: Market) -> Market:
        if not hasattr(market, 'id'):
            raise RepositoryError('create', 'Market missing id')
        try:
            now = _now_iso()
            self._conn.execute(
                "INSERT INTO markets (id, code, name, market_type, timezone, currency, status, opening_time, closing_time, trading_days, metadata, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (market.id, market.code, market.name, market.market_type.value, market.timezone, market.currency, market.status.value, market.opening_time.isoformat() if market.opening_time else None, market.closing_time.isoformat() if market.closing_time else None, json.dumps(market.trading_days), json.dumps(market.metadata), now, now)
            )
            self._conn.commit()
            return market
        except Exception as e:
            raise RepositoryError('create', str(e))

    def get_by_code(self, code: str) -> Optional[Market]:
        cur = self._conn.execute("SELECT * FROM markets WHERE code = ?", (code.upper(),))
        row = cur.fetchone()
        if not row:
            return None
        return self._row_to_market(row)

    # Backwards compatible alias used by service layer
    def find_by_code(self, code: str) -> Optional[Market]:
        return self.get_by_code(code)

    def get_by_id(self, id: str) -> Market:
        cur = self._conn.execute("SELECT * FROM markets WHERE id = ?", (id,))
        row = cur.fetchone()
        if not row:
            raise DataNotFoundError('Market', id)
        return self._row_to_market(row)

    def list_all(self) -> List[Market]:
        cur = self._conn.execute("SELECT * FROM markets")
        rows = cur.fetchall()
        return [self._row_to_market(r) for r in rows]

    # Backwards compatible alias for Repository.get_all
    def get_all(self) -> List[Market]:
        return self.list_all()

    def _row_to_market(self, row):
        (id, code, name, market_type, timezone, currency, status, opening_time, closing_time, trading_days, metadata, created_at, updated_at) = row
        m = Market(code=code, name=name, market_type=MarketTypeFromString(market_type), timezone=timezone, currency=currency, status=MarketStatusFromString(status))
        m.id = id
        m.trading_days = json.loads(trading_days) if trading_days else []
        m.metadata = json.loads(metadata) if metadata else {}
        # created_at/updated_at are stored but BaseModel will set its own timestamps
        return m


class AssetSqlRepository(SQLiteBase):
    def create(self, asset: Asset) -> Asset:
        try:
            now = _now_iso()
            self._conn.execute(
                "INSERT INTO assets (id, symbol, name, asset_type, status, market_id, currency, metadata, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (asset.id, asset.symbol, asset.name, asset.asset_type.value, asset.status.value, asset.market_id, asset.currency, json.dumps(asset.metadata), now, now)
            )
            self._conn.commit()
            return asset
        except Exception as e:
            raise RepositoryError('create', str(e))

    def find_by_symbol(self, symbol: str) -> Optional[Asset]:
        cur = self._conn.execute("SELECT * FROM assets WHERE symbol = ?", (symbol.upper(),))
        row = cur.fetchone()
        if not row:
            return None
        return self._row_to_asset(row)

    def list_all(self) -> List[Asset]:
        cur = self._conn.execute("SELECT * FROM assets")
        rows = cur.fetchall()
        return [self._row_to_asset(r) for r in rows]

    # Backwards compatible aliases used by service layer
    def get_by_id(self, id: str) -> Asset:
        cur = self._conn.execute("SELECT * FROM assets WHERE id = ?", (id,))
        row = cur.fetchone()
        if not row:
            raise DataNotFoundError('Asset', id)
        return self._row_to_asset(row)

    def get_all(self) -> List[Asset]:
        return self.list_all()

    def _row_to_asset(self, row):
        (id, symbol, name, asset_type, status, market_id, currency, metadata, created_at, updated_at) = row
        a = Asset(symbol=symbol, name=name, asset_type=AssetTypeFromString(asset_type), market_id=market_id, currency=currency, status=AssetStatusFromString(status))
        a.id = id
        a.metadata = json.loads(metadata) if metadata else {}
        return a


# Helpers to map enums without importing circularly in top
from ..models.market import MarketType as MT, MarketStatus
from ..models.asset import AssetType, AssetStatus


def MarketTypeFromString(s: str) -> MT:
    try:
        return MT(s)
    except Exception:
        return MT.STOCK_EXCHANGE


def MarketStatusFromString(s: str) -> MarketStatus:
    try:
        return MarketStatus(s)
    except Exception:
        return MarketStatus.CLOSED


def AssetTypeFromString(s: str) -> AssetType:
    try:
        return AssetType(s)
    except Exception:
        return AssetType.STOCK


def AssetStatusFromString(s: str) -> AssetStatus:
    try:
        return AssetStatus(s)
    except Exception:
        return AssetStatus.ACTIVE
