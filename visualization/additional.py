"""
Additional visualizations: Volatility, price change trends, and 24-hour patterns.
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

import logging
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd

from visualization.required import get_connection, COLORS
from ETL_process import config

logger = logging.getLogger(__name__)


def plot_price_volatility(output_path: Path = None) -> None:
    """
    Generate price volatility chart showing high-low spread over time.
    Shows the price range (volatility) for each hour.

    Args:
        output_path: Path to save chart (default: charts/price_volatility.png)
    """
    if output_path is None:
        output_path = config.CHARTS_DIR / "price_volatility.png"

    conn = get_connection()

    df = conn.execute("""
        SELECT product, datetime, high, low, (high - low) as spread
        FROM candles
        ORDER BY product, datetime
    """).df()

    conn.close()

    # Check if data exists
    if df.empty:
        logger.warning("No data found in database. Skipping price volatility chart.")
        return

    # Convert datetime column
    df['datetime'] = pd.to_datetime(df['datetime'])

    # Create figure
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10), sharex=True)

    # Top plot: High-Low spread (absolute) with dual Y-axes
    # Plot BTC on left axis
    btc_df = df[df['product'] == 'BTC-USD']
    if not btc_df.empty:
        ax1.fill_between(
            btc_df['datetime'],
            btc_df['low'],
            btc_df['high'],
            alpha=0.3,
            label='BTC-USD Range',
            color=COLORS['BTC-USD']
        )
        ax1.plot(
            btc_df['datetime'],
            btc_df['high'],
            color=COLORS['BTC-USD'],
            linewidth=1,
            alpha=0.6
        )
        ax1.plot(
            btc_df['datetime'],
            btc_df['low'],
            color=COLORS['BTC-USD'],
            linewidth=1,
            alpha=0.6
        )
    ax1.set_xlabel('Date', fontsize=12)
    ax1.set_ylabel('BTC-USD Price ($)', fontsize=12, color=COLORS['BTC-USD'])
    ax1.tick_params(axis='y', labelcolor=COLORS['BTC-USD'])
    ax1.set_title('Price Range (High-Low) by Product', fontsize=14, fontweight='bold')
    ax1.grid(True, alpha=0.3)

    # Plot ETH on right axis
    ax1_right = ax1.twinx()
    eth_df = df[df['product'] == 'ETH-USD']
    if not eth_df.empty:
        ax1_right.fill_between(
            eth_df['datetime'],
            eth_df['low'],
            eth_df['high'],
            alpha=0.3,
            label='ETH-USD Range',
            color=COLORS['ETH-USD']
        )
        ax1_right.plot(
            eth_df['datetime'],
            eth_df['high'],
            color=COLORS['ETH-USD'],
            linewidth=1,
            alpha=0.6
        )
        ax1_right.plot(
            eth_df['datetime'],
            eth_df['low'],
            color=COLORS['ETH-USD'],
            linewidth=1,
            alpha=0.6
        )
    ax1_right.set_ylabel('ETH-USD Price ($)', fontsize=12, color=COLORS['ETH-USD'])
    ax1_right.tick_params(axis='y', labelcolor=COLORS['ETH-USD'])

    # Combine legends
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax1_right.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left')

    # Bottom plot: Spread as percentage of price
    for product in df['product'].unique():
        product_df = df[df['product'] == product]
        mid_price = (product_df['high'] + product_df['low']) / 2
        spread_pct = (product_df['spread'] / mid_price) * 100
        ax2.plot(
            product_df['datetime'],
            spread_pct,
            label=product,
            color=COLORS.get(product, None),
            linewidth=1.5,
            alpha=0.8
        )

    ax2.set_xlabel('Date', fontsize=12)
    ax2.set_ylabel('Volatility (%)', fontsize=12)
    ax2.set_title('Price Volatility: Spread as % of Mid Price', fontsize=14, fontweight='bold')
    ax2.legend(loc='upper right')
    ax2.grid(True, alpha=0.3)

    # Format x-axis
    ax2.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
    ax2.xaxis.set_major_locator(mdates.DayLocator())
    plt.setp(ax2.xaxis.get_majorticklabels(), rotation=45)

    plt.tight_layout()

    # Save
    output_path.parent.mkdir(exist_ok=True)
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()

    logger.info(f"Price volatility chart saved to {output_path}")


def plot_price_change_trends(output_path: Path = None) -> None:
    """
    Generate price change percentage trends over time.
    Shows hourly price movements and cumulative trends.

    Args:
        output_path: Path to save chart (default: charts/price_change_trends.png)
    """
    if output_path is None:
        output_path = config.CHARTS_DIR / "price_change_trends.png"

    conn = get_connection()

    df = conn.execute("""
        SELECT product, datetime, price_change_pct
        FROM candles
        ORDER BY product, datetime
    """).df()

    conn.close()

    # Check if data exists
    if df.empty:
        logger.warning("No data found in database. Skipping price change trends chart.")
        return

    # Convert datetime column
    df['datetime'] = pd.to_datetime(df['datetime'])

    # Create figure with two subplots
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10), sharex=True)

    # Top plot: Hourly price change percentage
    for product in df['product'].unique():
        product_df = df[df['product'] == product]
        colors_fill = COLORS.get(product, '#808080')
        ax1.fill_between(
            product_df['datetime'],
            0,
            product_df['price_change_pct'],
            alpha=0.3,
            color=colors_fill
        )
        ax1.plot(
            product_df['datetime'],
            product_df['price_change_pct'],
            label=product,
            color=colors_fill,
            linewidth=1.5,
            marker='o',
            markersize=2,
            alpha=0.8
        )

    ax1.axhline(y=0, color='black', linestyle='--', linewidth=1, alpha=0.5)
    ax1.set_ylabel('Price Change (%)', fontsize=12)
    ax1.set_title('Hourly Price Change Percentage', fontsize=14, fontweight='bold')
    ax1.legend(loc='upper right')
    ax1.grid(True, alpha=0.3)

    # Bottom plot: Cumulative price change
    for product in df['product'].unique():
        product_df = df[df['product'] == product].copy()
        product_df['cumulative_change'] = product_df['price_change_pct'].cumsum()
        ax2.plot(
            product_df['datetime'],
            product_df['cumulative_change'],
            label=product,
            color=COLORS.get(product, None),
            linewidth=2,
            alpha=0.8
        )

    ax2.axhline(y=0, color='black', linestyle='--', linewidth=1, alpha=0.5)
    ax2.set_xlabel('Date', fontsize=12)
    ax2.set_ylabel('Cumulative Price Change (%)', fontsize=12)
    ax2.set_title('Cumulative Price Change Over Time', fontsize=14, fontweight='bold')
    ax2.legend(loc='upper left')
    ax2.grid(True, alpha=0.3)

    # Format x-axis
    ax2.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
    ax2.xaxis.set_major_locator(mdates.DayLocator())
    plt.setp(ax2.xaxis.get_majorticklabels(), rotation=45)

    plt.tight_layout()

    # Save
    output_path.parent.mkdir(exist_ok=True)
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()

    logger.info(f"Price change trends chart saved to {output_path}")


def plot_24hour_pattern(output_path: Path = None) -> None:
    """
    Generate 24-hour trading pattern showing average price and volume by hour of day.
    Reveals if there are consistent patterns in trading activity throughout the day.

    Args:
        output_path: Path to save chart (default: charts/24hour_pattern.png)
    """
    if output_path is None:
        output_path = config.CHARTS_DIR / "24hour_pattern.png"

    conn = get_connection()

    df = conn.execute("""
        SELECT product, datetime, avg_price, volume
        FROM candles
        ORDER BY product, datetime
    """).df()

    conn.close()

    # Check if data exists
    if df.empty:
        logger.warning("No data found in database. Skipping 24-hour pattern chart.")
        return

    # Convert datetime column
    df['datetime'] = pd.to_datetime(df['datetime'])
    df['hour'] = df['datetime'].dt.hour

    # Create figure with dual y-axis
    fig, ax1 = plt.subplots(figsize=(14, 6))

    # Calculate average price and volume by hour
    hourly_stats = []
    for product in df['product'].unique():
        product_df = df[df['product'] == product]
        hourly_avg = product_df.groupby('hour').agg({
            'avg_price': 'mean',
            'volume': 'mean'
        }).reset_index()
        hourly_avg['product'] = product
        hourly_stats.append(hourly_avg)

    hourly_df = pd.concat(hourly_stats, ignore_index=True)

    # Plot BTC price on left axis
    btc_hourly = hourly_df[hourly_df['product'] == 'BTC-USD']
    if not btc_hourly.empty:
        ax1.plot(
            btc_hourly['hour'],
            btc_hourly['avg_price'],
            label='BTC-USD Price',
            color=COLORS['BTC-USD'],
            linewidth=2,
            marker='o',
            markersize=6,
            alpha=0.8
        )
    ax1.set_xlabel('Hour of Day (UTC)', fontsize=12)
    ax1.set_ylabel('BTC-USD Price ($)', fontsize=12, color=COLORS['BTC-USD'])
    ax1.tick_params(axis='y', labelcolor=COLORS['BTC-USD'])
    ax1.set_title('24-Hour Trading Pattern: Average Price by Hour', fontsize=14, fontweight='bold')
    ax1.set_xticks(range(24))
    ax1.set_xlim(-0.5, 23.5)
    ax1.grid(True, alpha=0.3, axis='y')

    # Plot ETH price on right axis
    ax1_right = ax1.twinx()
    eth_hourly = hourly_df[hourly_df['product'] == 'ETH-USD']
    if not eth_hourly.empty:
        ax1_right.plot(
            eth_hourly['hour'],
            eth_hourly['avg_price'],
            label='ETH-USD Price',
            color=COLORS['ETH-USD'],
            linewidth=2,
            marker='o',
            markersize=6,
            alpha=0.8
        )
    ax1_right.set_ylabel('ETH-USD Price ($)', fontsize=12, color=COLORS['ETH-USD'])
    ax1_right.tick_params(axis='y', labelcolor=COLORS['ETH-USD'])

    # Add volume bars on a third axis (second twinx from the right axis)
    ax2 = ax1_right.twinx()
    # Offset bars so they don't overlap
    for product in hourly_df['product'].unique():
        product_hourly = hourly_df[hourly_df['product'] == product]
        offset = 0.2 if product == 'ETH-USD' else -0.2
        ax2.bar(
            product_hourly['hour'] + offset,
            product_hourly['volume'],
            width=0.4,
            label=f'{product} Volume',
            color=COLORS.get(product, None),
            alpha=0.3
        )

    ax2.set_ylabel('Average Volume', fontsize=12, color='gray')
    ax2.tick_params(axis='y', labelcolor='gray')
    ax2.spines['right'].set_position(('outward', 60))  # Offset the volume axis

    # Combine legends
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax1_right.get_legend_handles_labels()
    lines3, labels3 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2 + lines3, labels1 + labels2 + labels3, loc='upper left')

    plt.tight_layout()

    # Save
    output_path.parent.mkdir(exist_ok=True)
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()

    logger.info(f"24-hour pattern chart saved to {output_path}")

