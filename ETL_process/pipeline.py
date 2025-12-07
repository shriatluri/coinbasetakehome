import argparse
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from ETL_process import config, fetch, transform, load

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
log = logging.getLogger(__name__)


def run(products=None, start=None, end=None, incremental=True):
    """
    Run the ETL pipeline.

    If incremental=True, only fetches data newer than what's already in db.
    """
    products = products or config.PRODUCTS
    end = end or config.END_DATE

    stats = {"fetched": 0, "transformed": 0, "loaded": 0}
    conn = load.get_connection()

    try:
        for product in products:
            log.info(f"Processing {product}")

            # figure out start date
            if start:
                fetch_start = start
            elif incremental:
                last = load.get_last_timestamp(conn, product)
                if last:
                    fetch_start = datetime.fromtimestamp(last + 1, tz=timezone.utc).isoformat()
                    log.info(f"Incremental: starting from {fetch_start}")
                else:
                    fetch_start = config.START_DATE
            else:
                fetch_start = config.START_DATE

            # extract
            raw = fetch.fetch_candles(product, fetch_start, end)
            stats["fetched"] += len(raw)

            if not raw:
                log.info(f"No new data for {product}")
                continue

            # transform
            cleaned = transform.transform_product_data(raw, product)
            stats["transformed"] += len(cleaned)

            # load
            loaded = load.insert_candles(conn, cleaned)
            stats["loaded"] += loaded

        counts = load.get_counts(conn)
        log.info(f"DB totals: {counts}")

    finally:
        conn.close()

    return stats


def main():
    parser = argparse.ArgumentParser(description="Coinbase ETL Pipeline")
    parser.add_argument("--full-refresh", action="store_true",
                        help="Ignore existing data, fetch everything")
    parser.add_argument("--start", help="Start date (ISO format)")
    parser.add_argument("--end", help="End date (ISO format)")
    parser.add_argument("--products", nargs="+", help="Products to fetch (e.g. BTC-USD)")

    args = parser.parse_args()

    log.info("Starting pipeline...")
    stats = run(
        products=args.products,
        start=args.start,
        end=args.end,
        incremental=not args.full_refresh
    )
    log.info(f"Done! {stats}")


if __name__ == "__main__":
    main()
