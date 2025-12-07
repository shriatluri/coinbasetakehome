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
| Data validation | Strict for visualization fields | Must have valid prices/volumes; skip malformed records with logging |
| Incremental support | Yes | Query DB for last timestamp, fetch only new data |
| Error handling | Raise exceptions | Fail loudly; log errors but don't silently continue with bad data |

---

## Module Responsibilities

### Extract Layer
Responsible for communicating with the Coinbase API to fetch raw candle data. Preserves raw API responses in `raw_data/` directory for debugging and audit purposes. Handles API errors explicitly and returns data in original API format.

### Transform Layer
Cleans, validates, and enriches raw data. Validates each candle record to ensure all price fields are positive, volume is non-negative, and data integrity checks pass (e.g., high >= low). Skips invalid records with warning logs. Computes derived fields:
- **avg_price**: `(high + low + open + close) / 4` - Required for visualization
- **price_change**: `close - open` - Price movement analysis
- **price_change_pct**: `(close - open) / open * 100` - Percentage change

### Load Layer
Manages DuckDB storage and database operations. Creates tables and indexes on first run. Supports incremental loading by querying the database for the most recent timestamp per product and only fetching new data. Uses upsert operations (INSERT OR REPLACE) to handle overlapping records safely, making the pipeline idempotent.

### Visualization Layer
Generates charts from database data. Organized into three modules for maintainability:
- **`visualize.py`**: Main entry point that coordinates chart generation
- **`required.py`**: Contains required visualizations (hourly volume, average price)
- **`additional.py`**: Contains additional visualizations (volatility, trends, patterns)

Includes empty data validation to gracefully handle missing or empty datasets. Supports generating required charts only, additional charts only, or all charts. Uses brand colors (BTC orange, ETH blue) for consistent visual identity.

**Required Charts:**
- **Hourly Volume**: Line chart showing volume per hour for BTC-USD and ETH-USD
- **Average Price**: Dual-axis line chart for price trends (accounts for BTC/ETH scale difference)

**Additional Charts:**
- **Price Volatility**: High-low price range and volatility as percentage of mid-price (uses dual Y-axes for clarity)
- **Price Change Trends**: Hourly price change percentage and cumulative price change over time

### ETL Orchestrator
Coordinates the ETL stages (Extract, Transform, Load). Handles incremental vs. full refresh modes. Supports custom date ranges and product selection. Returns statistics on records processed at each stage.

### Main Entry Point
Provides a unified interface to run the complete pipeline end-to-end (ETL + Visualizations). Supports flexible execution modes: ETL only, visualizations only, or both. Allows selection of which charts to generate (required, additional, or all).

---

## Database Schema

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

## Key Features

1. **Modular Architecture**: Clean separation between ETL and visualization layers
2. **Incremental Loading**: Efficient data updates without redundant API calls
3. **Data Validation**: Strict validation with graceful handling of invalid records
4. **Error Handling**: Comprehensive error handling with clear logging
5. **Empty Data Handling**: Visualizations gracefully handle missing or empty data
6. **Flexible Entry Points**: Both unified and granular execution options
7. **Additional Insights**: Beyond required charts, includes volatility, trends, and pattern analysis

---

## What Makes This "Data Engineering"

1. **Separation of Concerns**: Each module has one job
2. **Incremental Processing**: Only process new data (streaming-ready)
3. **Data Validation**: Strict validation with clear rules
4. **Idempotency**: Can re-run safely (upserts, not blind inserts)
5. **Auditability**: Raw data preserved for debugging
6. **Configuration Management**: No hardcoded values in logic
7. **Clear Schema**: Typed columns, primary keys, indexes
