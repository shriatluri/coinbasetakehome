# Coinbase Data Pipeline - Design Document

## Project Goal

Build a production-style data pipeline that:
1. Fetches cryptocurrency price/volume data from Coinbase API (BTC-USD, ETH-USD)
2. Stores data in DuckDB with proper schema
3. Visualizes hourly volume and average price for each trading pair

**Design Philosophy:** Clean, modular, data-engineering best practices. Impress with code quality and architecture, not complexity. We used ETL instead of ELT because it is a set time frame with batch data not stream data.

---

## Architecture Overview

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   EXTRACT   │───▶│  TRANSFORM  │───▶│    LOAD     │───▶│  VISUALIZE  │
│  fetch.py   │    │transform.py │    │   load.py   │    │visualize.py │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
       │                  │                  │                  │
       ▼                  ▼                  ▼                  ▼
   raw_data/         (in-memory)      coinbase.duckdb      charts/
```

**ETL Pattern** with incremental data support for streaming-ready design.

---

## Design Decisions

| Question | Decision | Rationale |
|----------|----------|-----------|
| Derived fields | Yes, in transform layer | Pre-compute `avg_price`, `price_change_pct` for visualization |
| File naming | Overwrite single file | Simpler for this scope; DB handles history |
| Data validation | Strict for visualization fields | Must have valid prices/volumes; skip malformed records with logging |
| Incremental support | Yes | Query DB for last timestamp, fetch only new data |
| Error handling | Raise exceptions | Fail loudly; log errors but don't silently continue with bad data |

---

## Module Specifications

### 1. `config.py` - Configuration

Centralized settings to avoid magic values scattered in code.

```python
# Paths (relative to project root)
ROOT = Path(__file__).parent.parent
DB_PATH = ROOT / 'coinbase.duckdb'
RAW_DATA_DIR = ROOT / 'raw_data'
CHARTS_DIR = ROOT / 'charts'

# Coinbase API
BASE_URL = 'https://api.exchange.coinbase.com'

# Pipeline settings
PRODUCTS = ['BTC-USD', 'ETH-USD']
START_DATE = '2025-11-17T00:00:00Z'
END_DATE = '2025-11-24T23:59:59Z'
GRANULARITY = 3600  # 1 hour candles
```

---

### 2. `fetch.py` - Extract Layer

**Single Responsibility:** Communicate with Coinbase API.

```python
def fetch_candles(product_id: str, start: str, end: str, granularity: int) -> list[list]:
    """
    Fetch raw candle data from Coinbase API.

    Returns: List of [timestamp, low, high, open, close, volume]
    Raises: requests.HTTPError on API failure
    """

def fetch_all_products(products: list[str], start: str, end: str) -> dict[str, list]:
    """
    Fetch candles for multiple products.
    Saves raw data to raw_data/ for debugging/audit.
    """
```

**Key Features:**
- Raw data preservation in `raw_data/` directory
- Clear error propagation (no silent failures)
- Returns data in original API format

---

### 3. `transform.py` - Transform Layer

**Single Responsibility:** Clean, validate, and enrich data.

```python
def is_valid(candle: list) -> bool:
    """
    Validate a single candle record.
    - All price fields must be positive numbers
    - Volume must be non-negative
    - Timestamp must be valid
    - High >= low (sanity check)
    """

def transform_candle(candle: list, product: str) -> dict:
    """
    Transform raw API response to enriched format.

    Input:  [timestamp, low, high, open, close, volume]
    Output: {
        product, timestamp, datetime,
        open, high, low, close, volume,
        avg_price, price_change, price_change_pct
    }
    """

def transform_product_data(raw_candles: list, product: str) -> list[dict]:
    """
    Transform all candles for a product.
    - Validates each record
    - Skips invalid records with warning log
    - Sorts by timestamp ascending
    """
```

**Derived Fields:**
| Field | Calculation | Purpose |
|-------|-------------|---------|
| `avg_price` | `(high + low + open + close) / 4` | Visualization requirement |
| `price_change` | `close - open` | Price movement analysis |
| `price_change_pct` | `(close - open) / open * 100` | Percentage change |

**Validation Rules:**
- `open`, `high`, `low`, `close` must be positive floats
- `volume` must be non-negative
- `high` >= `low` (sanity check)
- `timestamp` must be valid Unix timestamp

---

### 4. `load.py` - Load Layer

**Single Responsibility:** Manage DuckDB storage.

```python
def get_connection(db_path: Path = None) -> duckdb.DuckDBPyConnection:
    """Open database connection and ensure tables exist."""

def get_last_timestamp(conn, product: str) -> int | None:
    """Get most recent timestamp for incremental loads."""

def insert_candles(conn, candles: list[dict]) -> int:
    """
    Insert or update candle records (upsert on conflict).
    Uses (product, timestamp) as unique key.
    Returns number of rows affected.
    """

def get_counts(conn) -> dict:
    """Get row count per product."""
```

**Database Schema:**
```sql
CREATE TABLE IF NOT EXISTS candles (
    product         VARCHAR NOT NULL,
    timestamp       BIGINT NOT NULL,
    datetime        TIMESTAMP NOT NULL,
    open            DOUBLE NOT NULL,
    high            DOUBLE NOT NULL,
    low             DOUBLE NOT NULL,
    close           DOUBLE NOT NULL,
    volume          DOUBLE NOT NULL,
    avg_price       DOUBLE NOT NULL,
    price_change    DOUBLE NOT NULL,
    price_change_pct DOUBLE NOT NULL,

    PRIMARY KEY (product, timestamp)
);

-- Index for time-range queries (visualization)
CREATE INDEX IF NOT EXISTS idx_candles_product_time
ON candles(product, datetime);
```

**Incremental Load Logic:**
1. Query DB for latest timestamp per product
2. Only fetch data after that timestamp
3. Upsert to handle any overlapping records

---

### 5. `visualize.py` - Visualization Layer

**Single Responsibility:** Generate charts from DB data.

```python
def plot_hourly_volume(output_path: Path = None) -> None:
    """Line chart of hourly volume by trading pair."""

def plot_average_price(output_path: Path = None) -> None:
    """Dual-axis line chart of average price over time by trading pair."""

def plot_price_volatility(output_path: Path = None) -> None:
    """Price range (high-low) and volatility percentage charts."""

def plot_price_change_trends(output_path: Path = None) -> None:
    """Hourly price change percentage and cumulative trends."""

def plot_24hour_pattern(output_path: Path = None) -> None:
    """Average price and volume patterns by hour of day."""

def generate_required_charts() -> None:
    """Generate required visualizations (hourly volume, average price)."""

def generate_additional_charts() -> None:
    """Generate additional visualizations (volatility, trends, patterns)."""

def generate_all_charts() -> None:
    """Generate all visualizations (required + additional)."""
```

**Required Charts:**
1. **Hourly Volume:** Line chart showing volume per hour for BTC-USD and ETH-USD
2. **Average Price:** Dual-axis line chart for price trends (accounts for BTC/ETH scale difference)

**Additional Charts:**
3. **Price Volatility:** High-low price range and volatility as percentage of mid-price
4. **Price Change Trends:** Hourly price change percentage and cumulative price change over time
5. **24-Hour Pattern:** Average price and volume patterns by hour of day (UTC)

**Key Features:**
- Empty data validation (gracefully skips if no data in database)
- Handles missing products gracefully
- Uses brand colors (BTC orange, ETH blue)

---

### 6. `pipeline.py` - ETL Orchestrator

**Single Responsibility:** Coordinate ETL stages (Extract, Transform, Load).

```python
def run(
    products: list[str] = None,
    start: str = None,
    end: str = None,
    incremental: bool = True
) -> dict:
    """
    Run full ETL pipeline.

    Args:
        products: List of product IDs (default from config)
        start: Start datetime (default from config, or incremental)
        end: End datetime (default from config)
        incremental: If True, only fetch new data since last load

    Returns:
        Summary dict with records processed per stage
    """
```

**CLI Interface:**
```bash
# Full pipeline (incremental by default)
python ETL_process/pipeline.py

# Full refresh (ignore existing data)
python ETL_process/pipeline.py --full-refresh

# Specific date range
python ETL_process/pipeline.py --start 2025-11-20 --end 2025-11-24
```

### 7. `run.py` - Main Entry Point

**Single Responsibility:** Run complete pipeline end-to-end (ETL + Visualizations).

**CLI Interface:**
```bash
# Run everything (ETL + all visualizations)
python run.py

# Full refresh and generate all charts
python run.py --full-refresh

# Generate only required charts
python run.py --charts required

# Generate only additional charts
python run.py --charts additional

# Skip ETL, only generate visualizations
python run.py --skip-etl

# Run ETL but skip visualizations
python run.py --skip-visualizations
```

---

## Directory Structure

```
coinbasetakehome/
├── run.py               # Main entry point (ETL + visualizations)
├── ETL_process/         # ETL pipeline modules
│   ├── __init__.py
│   ├── pipeline.py      # ETL orchestrator + CLI
│   ├── fetch.py         # Extract layer
│   ├── transform.py     # Transform layer
│   ├── load.py          # Load layer (DuckDB)
│   └── config.py         # Configuration constants
├── visualization/        # Visualization modules
│   ├── __init__.py
│   └── visualize.py     # Visualization layer
│
├── raw_data/            # Raw API responses (for debugging)
│   └── candles_raw.json
│
├── charts/              # Generated visualizations
│   ├── hourly_volume.png      # Required
│   ├── avg_price.png          # Required
│   ├── price_volatility.png   # Additional
│   ├── price_change_trends.png # Additional
│   └── 24hour_pattern.png      # Additional
│
├── coinbase.duckdb      # Database file
│
├── coinbase_data.json   # Original output (keep as reference)
├── requirements.txt     # Python dependencies
├── README.md            # User documentation
└── pipeline.md          # This document
```

---

## Implementation Status

### Phase 1: Core Pipeline ✅
- [x] Create `config.py`
- [x] Create `fetch.py` (extract from fetch_data.py)
- [x] Create `transform.py` (validation + enrichment)
- [x] Create `load.py` (DuckDB integration)
- [x] Create `pipeline.py` (orchestrator)
- [x] Test full ETL flow

### Phase 2: Visualization ✅
- [x] Create `visualize.py`
- [x] Generate hourly volume chart (required)
- [x] Generate average price chart (required)
- [x] Generate price volatility chart (additional)
- [x] Generate price change trends chart (additional)
- [x] Generate 24-hour pattern chart (additional)

### Phase 3: Polish ✅
- [x] Add logging throughout
- [x] Test incremental load
- [x] Add empty data validation
- [x] Create main entry point (`run.py`)
- [x] Add error handling
- [x] Final testing

---

## What Makes This "Data Engineering"

1. **Separation of Concerns:** Each module has one job
2. **Incremental Processing:** Only process new data (streaming-ready)
3. **Data Validation:** Strict validation with clear rules
4. **Idempotency:** Can re-run safely (upserts, not blind inserts)
5. **Auditability:** Raw data preserved for debugging
6. **Configuration Management:** No hardcoded values in logic
7. **Clear Schema:** Typed columns, primary keys, indexes

---

## Key Features Implemented

1. **Modular Architecture:** Clean separation between ETL and visualization layers
2. **Incremental Loading:** Efficient data updates without redundant API calls
3. **Data Validation:** Strict validation with graceful handling of invalid records
4. **Error Handling:** Comprehensive error handling with clear logging
5. **Empty Data Handling:** Visualizations gracefully handle missing or empty data
6. **Flexible Entry Points:** Both unified (`run.py`) and granular (individual modules) execution options
7. **Additional Insights:** Beyond required charts, includes volatility, trends, and pattern analysis
