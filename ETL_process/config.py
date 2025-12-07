from pathlib import Path

# paths
ROOT = Path(__file__).parent.parent
DB_PATH = ROOT / 'coinbase.duckdb'
RAW_DATA_DIR = ROOT / 'raw_data'
CHARTS_DIR = ROOT / 'charts'

# coinbase api
BASE_URL = 'https://api.exchange.coinbase.com'

# pipeline settings
PRODUCTS = ['BTC-USD', 'ETH-USD']
START_DATE = '2025-11-17T00:00:00Z'
END_DATE = '2025-11-24T23:59:59Z'
GRANULARITY = 3600  # hourly candles
