import logging
from datetime import datetime, timezone

log = logging.getLogger(__name__)


def is_valid(candle):
    """Check if candle data looks reasonable"""
    if len(candle) != 6:
        return False

    ts, low, high, open_, close, vol = candle

    # basic sanity checks
    if ts <= 0:
        return False
    if any(p <= 0 for p in [low, high, open_, close]):
        return False
    if vol < 0:
        return False
    if high < low:
        return False

    return True


def transform_candle(candle, product):
    """Convert raw candle array to dict with computed fields"""
    ts, low, high, open_, close, vol = candle

    dt = datetime.fromtimestamp(ts, tz=timezone.utc)
    avg = (high + low + open_ + close) / 4
    change = close - open_
    change_pct = (change / open_) * 100 if open_ else 0

    return {
        "product": product,
        "timestamp": int(ts),
        "datetime": dt.isoformat(),
        "open": float(open_),
        "high": float(high),
        "low": float(low),
        "close": float(close),
        "volume": float(vol),
        "avg_price": round(avg, 2),
        "price_change": round(change, 2),
        "price_change_pct": round(change_pct, 4),
    }


def transform_product_data(raw_candles, product):
    """Transform and validate all candles for a product"""
    valid = [c for c in raw_candles if is_valid(c)]

    if len(valid) < len(raw_candles):
        log.warning(f"{product}: skipped {len(raw_candles) - len(valid)} bad candles")

    result = [transform_candle(c, product) for c in valid]
    result.sort(key=lambda x: x["timestamp"])

    log.info(f"{product}: transformed {len(result)} candles")
    return result


def transform_all(raw_data):
    """Transform raw data for all products into single list"""
    all_candles = []
    for product, candles in raw_data.items():
        all_candles.extend(transform_product_data(candles, product))

    log.info(f"Total: {len(all_candles)} candles")
    return all_candles
