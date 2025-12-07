import json
import logging
import requests
from . import config

log = logging.getLogger(__name__)


def fetch_candles(product_id, start, end, granularity=config.GRANULARITY):
    """
    Grab candle data from Coinbase for a single product.
    Returns list of [timestamp, low, high, open, close, volume]
    """
    url = f"{config.BASE_URL}/products/{product_id}/candles"
    params = {"start": start, "end": end, "granularity": granularity}

    log.info(f"Fetching {product_id} from {start} to {end}")

    resp = requests.get(url, params=params)
    resp.raise_for_status()

    data = resp.json()
    log.info(f"Got {len(data)} candles for {product_id}")

    return data


def fetch_all(products=None, start=config.START_DATE, end=config.END_DATE, save=True):
    """Fetch candles for all products, optionally saving raw json"""
    products = products or config.PRODUCTS

    results = {}
    for prod in products:
        results[prod] = fetch_candles(prod, start, end)

    if save:
        config.RAW_DATA_DIR.mkdir(exist_ok=True)
        with open(config.RAW_DATA_DIR / "candles_raw.json", "w") as f:
            json.dump(results, f, indent=2)
        log.info(f"Saved raw data to {config.RAW_DATA_DIR}")

    return results


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    data = fetch_all()
    for prod, candles in data.items():
        print(f"{prod}: {len(candles)} candles")
