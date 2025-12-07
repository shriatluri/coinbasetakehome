import logging
from datetime import datetime
import duckdb
from . import config

log = logging.getLogger(__name__)

CREATE_TABLE = """
CREATE TABLE IF NOT EXISTS candles (
    product          VARCHAR NOT NULL,
    timestamp        BIGINT NOT NULL,
    datetime         TIMESTAMP NOT NULL,
    open             DOUBLE NOT NULL,
    high             DOUBLE NOT NULL,
    low              DOUBLE NOT NULL,
    close            DOUBLE NOT NULL,
    volume           DOUBLE NOT NULL,
    avg_price        DOUBLE NOT NULL,
    price_change     DOUBLE NOT NULL,
    price_change_pct DOUBLE NOT NULL,
    PRIMARY KEY (product, timestamp)
)
"""

CREATE_INDEX = """
CREATE INDEX IF NOT EXISTS idx_candles_time
ON candles(product, datetime)
"""


def get_connection(db_path=None):
    """Open db connection and ensure tables exist"""
    path = db_path or config.DB_PATH
    conn = duckdb.connect(str(path))
    conn.execute(CREATE_TABLE)
    conn.execute(CREATE_INDEX)
    log.info(f"Connected to {path}")
    return conn


def get_last_timestamp(conn, product):
    """Get most recent timestamp we have for a product"""
    result = conn.execute(
        "SELECT MAX(timestamp) FROM candles WHERE product = ?", [product]
    ).fetchone()
    return result[0] if result[0] else None


def insert_candles(conn, candles):
    """Insert candles into db (upsert on conflict)"""
    if not candles:
        return 0

    rows = []
    for c in candles:
        dt = datetime.fromisoformat(c["datetime"].replace("Z", "+00:00"))
        rows.append((
            c["product"], c["timestamp"], dt,
            c["open"], c["high"], c["low"], c["close"],
            c["volume"], c["avg_price"], c["price_change"], c["price_change_pct"]
        ))

    conn.executemany("""
        INSERT OR REPLACE INTO candles
        (product, timestamp, datetime, open, high, low, close,
         volume, avg_price, price_change, price_change_pct)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, rows)

    log.info(f"Inserted {len(rows)} candles")
    return len(rows)


def get_counts(conn):
    """Get row count per product"""
    rows = conn.execute(
        "SELECT product, COUNT(*) FROM candles GROUP BY product"
    ).fetchall()
    return {r[0]: r[1] for r in rows}
