"""
Required visualizations: Hourly volume and average price charts.
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

import logging
import duckdb
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd

from ETL_process import config

logger = logging.getLogger(__name__)

# Style settings
plt.style.use('seaborn-v0_8-whitegrid')
COLORS = {'BTC-USD': '#F7931A', 'ETH-USD': '#627EEA'}  # Brand colors


def get_connection() -> duckdb.DuckDBPyConnection:
    """Get database connection."""
    return duckdb.connect(str(config.DB_PATH))


def plot_hourly_volume(output_path: Path = None) -> None:
    """
    Generate hourly volume chart for all trading pairs.

    Args:
        output_path: Path to save chart (default: charts/hourly_volume.png)
    """
    if output_path is None:
        output_path = config.CHARTS_DIR / "hourly_volume.png"

    conn = get_connection()

    df = conn.execute("""
        SELECT product, datetime, volume
        FROM candles
        ORDER BY product, datetime
    """).df()

    conn.close()

    # Check if data exists
    if df.empty:
        logger.warning("No data found in database. Skipping hourly volume chart.")
        return

    # Convert datetime column
    df['datetime'] = pd.to_datetime(df['datetime'])

    # Create figure
    _, ax = plt.subplots(figsize=(14, 6))

    for product in df['product'].unique():
        product_df = df[df['product'] == product]
        ax.plot(
            product_df['datetime'],
            product_df['volume'],
            label=product,
            color=COLORS.get(product, None),
            linewidth=1.5,
            alpha=0.8
        )

    ax.set_xlabel('Date', fontsize=12)
    ax.set_ylabel('Volume', fontsize=12)
    ax.set_title('Hourly Trading Volume by Product', fontsize=14, fontweight='bold')
    ax.legend(loc='upper right')

    # Format x-axis
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
    ax.xaxis.set_major_locator(mdates.DayLocator())
    plt.xticks(rotation=45)

    plt.tight_layout()

    # Save
    output_path.parent.mkdir(exist_ok=True)
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()

    logger.info(f"Hourly volume chart saved to {output_path}")


def plot_average_price(output_path: Path = None) -> None:
    """
    Generate average price chart for all trading pairs.

    Args:
        output_path: Path to save chart (default: charts/avg_price.png)
    """
    if output_path is None:
        output_path = config.CHARTS_DIR / "avg_price.png"

    conn = get_connection()

    df = conn.execute("""
        SELECT product, datetime, avg_price
        FROM candles
        ORDER BY product, datetime
    """).df()

    conn.close()

    # Check if data exists
    if df.empty:
        logger.warning("No data found in database. Skipping average price chart.")
        return

    # Convert datetime column
    df['datetime'] = pd.to_datetime(df['datetime'])

    # Create figure with dual y-axis (BTC and ETH have very different price scales)
    fig, ax1 = plt.subplots(figsize=(14, 6))

    # Plot BTC on left axis
    btc_df = df[df['product'] == 'BTC-USD']
    if not btc_df.empty:
        ax1.plot(
            btc_df['datetime'],
            btc_df['avg_price'],
            label='BTC-USD',
            color=COLORS['BTC-USD'],
            linewidth=1.5
        )
    ax1.set_xlabel('Date', fontsize=12)
    ax1.set_ylabel('BTC-USD Price ($)', fontsize=12, color=COLORS['BTC-USD'])
    ax1.tick_params(axis='y', labelcolor=COLORS['BTC-USD'])

    # Plot ETH on right axis
    ax2 = ax1.twinx()
    eth_df = df[df['product'] == 'ETH-USD']
    if not eth_df.empty:
        ax2.plot(
            eth_df['datetime'],
            eth_df['avg_price'],
            label='ETH-USD',
            color=COLORS['ETH-USD'],
            linewidth=1.5
        )
    ax2.set_ylabel('ETH-USD Price ($)', fontsize=12, color=COLORS['ETH-USD'])
    ax2.tick_params(axis='y', labelcolor=COLORS['ETH-USD'])

    # Title and legend
    fig.suptitle('Average Price by Product (Hourly)', fontsize=14, fontweight='bold')

    # Combine legends
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left')

    # Format x-axis
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
    ax1.xaxis.set_major_locator(mdates.DayLocator())
    plt.xticks(rotation=45)

    plt.tight_layout()

    # Save
    output_path.parent.mkdir(exist_ok=True)
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()

    logger.info(f"Average price chart saved to {output_path}")

