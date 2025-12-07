"""
Required visualizations: Hourly volume and average price charts.
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

import logging
import duckdb
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd

from ETL_process import config

logger = logging.getLogger(__name__)

# Style settings
COLORS = {'BTC-USD': '#F7931A', 'ETH-USD': '#627EEA'}  # Brand colors


def get_connection() -> duckdb.DuckDBPyConnection:
    """Get database connection."""
    return duckdb.connect(str(config.DB_PATH))


def plot_hourly_volume(output_path: Path = None) -> None:
    """
    Generate hourly volume chart for all trading pairs.

    Args:
        output_path: Path to save chart (default: charts/hourly_volume.html)
    """
    if output_path is None:
        output_path = config.CHARTS_DIR / "hourly_volume.html"

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

    # Create figure with secondary y-axis
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    # Plot BTC on primary y-axis
    btc_df = df[df['product'] == 'BTC-USD']
    if not btc_df.empty:
        fig.add_trace(
            go.Scatter(
                x=btc_df['datetime'],
                y=btc_df['volume'],
                name='BTC-USD',
                line=dict(color=COLORS['BTC-USD'], width=2),
                opacity=0.8,
                hovertemplate='<b>BTC-USD</b><br>Date: %{x}<br>Volume: %{y:,.2f}<extra></extra>'
            ),
            secondary_y=False
        )

    # Plot ETH on secondary y-axis
    eth_df = df[df['product'] == 'ETH-USD']
    if not eth_df.empty:
        fig.add_trace(
            go.Scatter(
                x=eth_df['datetime'],
                y=eth_df['volume'],
                name='ETH-USD',
                line=dict(color=COLORS['ETH-USD'], width=2),
                opacity=0.8,
                hovertemplate='<b>ETH-USD</b><br>Date: %{x}<br>Volume: %{y:,.2f}<extra></extra>'
            ),
            secondary_y=True
        )

    # Update layout
    fig.update_layout(
        title=dict(
            text='Hourly Trading Volume by Product',
            font=dict(size=18, color='#333'),
            x=0.5
        ),
        xaxis=dict(
            title='Date',
            tickformat='%m/%d',
            gridcolor='rgba(128,128,128,0.2)',
            showgrid=True
        ),
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=1.02,
            xanchor='right',
            x=1
        ),
        hovermode='x unified',
        template='plotly_white',
        height=500
    )

    # Update y-axes
    fig.update_yaxes(
        title_text='BTC-USD Volume',
        title_font=dict(color=COLORS['BTC-USD']),
        tickfont=dict(color=COLORS['BTC-USD']),
        gridcolor='rgba(128,128,128,0.2)',
        secondary_y=False
    )
    fig.update_yaxes(
        title_text='ETH-USD Volume',
        title_font=dict(color=COLORS['ETH-USD']),
        tickfont=dict(color=COLORS['ETH-USD']),
        secondary_y=True
    )

    # Save
    output_path.parent.mkdir(exist_ok=True)
    fig.write_html(output_path, include_plotlyjs=True, full_html=True)

    logger.info(f"Hourly volume chart saved to {output_path}")


def plot_average_price(output_path: Path = None) -> None:
    """
    Generate average price chart for all trading pairs.

    Args:
        output_path: Path to save chart (default: charts/avg_price.html)
    """
    if output_path is None:
        output_path = config.CHARTS_DIR / "avg_price.html"

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

    # Create figure with secondary y-axis
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    # Plot BTC on primary y-axis
    btc_df = df[df['product'] == 'BTC-USD']
    if not btc_df.empty:
        fig.add_trace(
            go.Scatter(
                x=btc_df['datetime'],
                y=btc_df['avg_price'],
                name='BTC-USD',
                line=dict(color=COLORS['BTC-USD'], width=2.5),
                mode='lines+markers',
                marker=dict(size=4, symbol='circle'),
                opacity=0.9,
                hovertemplate='<b>BTC-USD</b><br>Date: %{x}<br>Price: $%{y:,.2f}<extra></extra>'
            ),
            secondary_y=False
        )

    # Plot ETH on secondary y-axis
    eth_df = df[df['product'] == 'ETH-USD']
    if not eth_df.empty:
        fig.add_trace(
            go.Scatter(
                x=eth_df['datetime'],
                y=eth_df['avg_price'],
                name='ETH-USD',
                line=dict(color=COLORS['ETH-USD'], width=2.5),
                mode='lines+markers',
                marker=dict(size=4, symbol='square'),
                opacity=0.9,
                hovertemplate='<b>ETH-USD</b><br>Date: %{x}<br>Price: $%{y:,.2f}<extra></extra>'
            ),
            secondary_y=True
        )

    # Update layout
    fig.update_layout(
        title=dict(
            text='Average Price by Product (Hourly)',
            font=dict(size=18, color='#333'),
            x=0.5
        ),
        xaxis=dict(
            title='Date',
            tickformat='%m/%d',
            gridcolor='rgba(128,128,128,0.2)',
            showgrid=True
        ),
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=1.02,
            xanchor='right',
            x=1
        ),
        hovermode='x unified',
        template='plotly_white',
        height=500
    )

    # Update y-axes
    fig.update_yaxes(
        title_text='BTC-USD Price ($)',
        title_font=dict(color=COLORS['BTC-USD']),
        tickfont=dict(color=COLORS['BTC-USD']),
        tickprefix='$',
        gridcolor='rgba(128,128,128,0.2)',
        secondary_y=False
    )
    fig.update_yaxes(
        title_text='ETH-USD Price ($)',
        title_font=dict(color=COLORS['ETH-USD']),
        tickfont=dict(color=COLORS['ETH-USD']),
        tickprefix='$',
        secondary_y=True
    )

    # Save
    output_path.parent.mkdir(exist_ok=True)
    fig.write_html(output_path, include_plotlyjs=True, full_html=True)

    logger.info(f"Average price chart saved to {output_path}")
