# Coinbase Data Pipeline

ETL pipeline that fetches cryptocurrency data from Coinbase, stores it in DuckDB, and generates visualizations.

## Project Structure

```
coinbasetakehome/
├── run.py               # Main entry point (runs ETL + visualizations)
├── ETL_process/         # ETL pipeline modules
│   ├── pipeline.py      # ETL orchestrator + CLI
│   ├── fetch.py         # Extract layer
│   ├── transform.py     # Transform layer
│   ├── load.py          # Load layer (DuckDB)
│   └── config.py        # Configuration constants
├── visualization/       # Visualization modules
│   ├── visualize.py     # Main entry point
│   ├── required.py      # Required charts (hourly volume, average price)
│   └── additional.py    # Additional charts (volatility, trends, patterns)
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
└── pipeline.md          # Detailed pipeline documentation
```

**Why this structure?** Separation of concerns-each module handles one job. Makes testing easier and keeps the codebase maintainable.

## Setup

```bash
# Clone and enter repo
git clone <repo-url>
cd coinbasetakehome

# Install dependencies
pip install -r requirements.txt
```

## Usage

You can run the pipeline in two ways:

### Option 1: Quick Start (Recommended)

Run everything with a single command:

**First time setup (full refresh):**
```bash
python run.py --full-refresh
```

**Subsequent runs (incremental):**
```bash
python run.py
```

This will automatically:
1. Run the ETL pipeline (fetch, transform, and load data)
2. Generate all visualizations

**Additional options:**
```bash
# Generate only required charts (2 charts)
python run.py --charts required

# Generate only additional charts (3 charts)
python run.py --charts additional

# Skip ETL, only generate visualizations
python run.py --skip-etl

# Run ETL but skip visualizations
python run.py --skip-visualizations

# Full refresh with only required charts
python run.py --full-refresh --charts required
```

---

### Option 2: Step-by-Step (For More Control)

If you prefer to run each step individually for more control:

#### Step 1: Run the ETL Pipeline

First time setup (full refresh):
```bash
python ETL_process/pipeline.py --full-refresh
```

For subsequent runs, use incremental load (only fetches new data):
```bash
python ETL_process/pipeline.py
```

This will:
- Fetch cryptocurrency candle data from Coinbase API
- Transform and validate the data
- Load it into DuckDB (`coinbase.duckdb`)

### Step 2: Generate Visualizations

Generate charts from the data. You can choose to generate required charts, additional charts, or all charts:

**Generate all charts (default):**
```bash
python visualization/visualize.py
# or explicitly:
python visualization/visualize.py --type all
```
This generates all 5 visualizations (required + additional).

**Generate only required charts:**
```bash
python visualization/visualize.py --type required
```
Generates the 2 required visualizations:
- `hourly_volume.png` - Trading volume over time
- `avg_price.png` - Price trends (dual-axis for BTC/ETH scale difference)

**Generate only additional charts:**
```bash
python visualization/visualize.py --type additional
```
Generates 3 additional visualizations:
- `price_volatility.png` - Price range (high-low) and volatility percentage
- `price_change_trends.png` - Hourly price changes and cumulative trends
- `24hour_pattern.png` - Average price and volume patterns by hour of day

All charts are saved to the `charts/` directory.

### Step 3: Query the Database

#### Option A: Using DuckDB CLI
```bash
duckdb coinbase.duckdb
```

Example queries:
```sql
SELECT * FROM candles LIMIT 10;
SELECT product, COUNT(*) FROM candles GROUP BY product;
```

#### Option B: Using Harlequin (Interactive SQL IDE)
```bash
# Optional: install harlequin for a better SQL experience
pip install harlequin
harlequin coinbase.duckdb
```

Harlequin provides a user-friendly interface with syntax highlighting, query history, and result viewing.

## Pipeline Details

| Stage | Module | Description |
|-------|--------|-------------|
| Extract | `fetch.py` | Pulls hourly candle data from Coinbase API |
| Transform | `transform.py` | Validates data, computes `avg_price`, `price_change`, `price_change_pct` |
| Load | `load.py` | Upserts into DuckDB with `(product, timestamp)` as primary key |

**Incremental loading**: The pipeline checks the last timestamp in the database and only fetches newer data. This avoids redundant API calls and supports streaming-style updates.

## Data

- **Coins/Products**: BTC-USD, ETH-USD
- **Time Range**: Nov 17-24, 2025
- **Granularity**: Hourly candles (192 per product)

## Visualizations

### Required Visualizations
- `hourly_volume.png` - Trading volume over time for BTC-USD and ETH-USD
- `avg_price.png` - Price trends with dual-axis (accounts for BTC/ETH scale difference)

### Additional Visualizations
- `price_volatility.png` - Price range (high-low spread) and volatility as percentage of mid-price
- `price_change_trends.png` - Hourly price change percentage and cumulative price change over time
- `24hour_pattern.png` - Average price and volume patterns by hour of day (UTC), revealing intraday trading patterns
