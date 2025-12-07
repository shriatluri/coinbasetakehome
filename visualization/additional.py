"""
Additional visualizations: Volatility and price change trends.
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

import logging
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd

from visualization.required import get_connection, COLORS
from ETL_process import config

logger = logging.getLogger(__name__)


def plot_price_volatility(output_path: Path = None) -> None:
    """
    Generate price volatility chart showing high-low spread over time.
    Shows the price range (volatility) for each hour.

    Args:
        output_path: Path to save chart (default: charts/price_volatility.html)
    """
    if output_path is None:
        output_path = config.CHARTS_DIR / "price_volatility.html"

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

    # Create figure with 2 rows
    fig = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.1,
        subplot_titles=('Price Range (High-Low) by Product', 'Price Volatility: Spread as % of Mid Price'),
        specs=[[{"secondary_y": True}], [{"secondary_y": False}]]
    )

    # Top plot: High-Low spread with dual Y-axes
    btc_df = df[df['product'] == 'BTC-USD']
    eth_df = df[df['product'] == 'ETH-USD']

    # BTC range band (primary y-axis)
    if not btc_df.empty:
        fig.add_trace(
            go.Scatter(
                x=btc_df['datetime'],
                y=btc_df['high'],
                name='BTC-USD High',
                line=dict(color=COLORS['BTC-USD'], width=1),
                opacity=0.6,
                showlegend=False,
                hovertemplate='High: $%{y:,.2f}<extra></extra>'
            ),
            row=1, col=1, secondary_y=False
        )
        fig.add_trace(
            go.Scatter(
                x=btc_df['datetime'],
                y=btc_df['low'],
                name='BTC-USD Range',
                line=dict(color=COLORS['BTC-USD'], width=1),
                opacity=0.6,
                fill='tonexty',
                fillcolor=f"rgba(247, 147, 26, 0.3)",
                hovertemplate='Low: $%{y:,.2f}<extra></extra>'
            ),
            row=1, col=1, secondary_y=False
        )

    # ETH range band (secondary y-axis)
    if not eth_df.empty:
        fig.add_trace(
            go.Scatter(
                x=eth_df['datetime'],
                y=eth_df['high'],
                name='ETH-USD High',
                line=dict(color=COLORS['ETH-USD'], width=1),
                opacity=0.6,
                showlegend=False,
                hovertemplate='High: $%{y:,.2f}<extra></extra>'
            ),
            row=1, col=1, secondary_y=True
        )
        fig.add_trace(
            go.Scatter(
                x=eth_df['datetime'],
                y=eth_df['low'],
                name='ETH-USD Range',
                line=dict(color=COLORS['ETH-USD'], width=1),
                opacity=0.6,
                fill='tonexty',
                fillcolor=f"rgba(98, 126, 234, 0.3)",
                hovertemplate='Low: $%{y:,.2f}<extra></extra>'
            ),
            row=1, col=1, secondary_y=True
        )

    # Bottom plot: Spread as percentage of price
    for product in df['product'].unique():
        product_df = df[df['product'] == product]
        mid_price = (product_df['high'] + product_df['low']) / 2
        spread_pct = (product_df['spread'] / mid_price) * 100
        fig.add_trace(
            go.Scatter(
                x=product_df['datetime'],
                y=spread_pct,
                name=product,
                line=dict(color=COLORS.get(product, '#808080'), width=1.5),
                opacity=0.8,
                hovertemplate=f'<b>{product}</b><br>Volatility: %{{y:.3f}}%<extra></extra>'
            ),
            row=2, col=1
        )

    # Update layout
    fig.update_layout(
        title=dict(
            text='Price Volatility Analysis',
            font=dict(size=18, color='#333'),
            x=0.5
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
        height=700
    )

    # Update axes
    fig.update_xaxes(tickformat='%m/%d', row=2, col=1)
    fig.update_yaxes(
        title_text='BTC-USD Price ($)',
        title_font=dict(color=COLORS['BTC-USD']),
        tickfont=dict(color=COLORS['BTC-USD']),
        tickprefix='$',
        row=1, col=1, secondary_y=False
    )
    fig.update_yaxes(
        title_text='ETH-USD Price ($)',
        title_font=dict(color=COLORS['ETH-USD']),
        tickfont=dict(color=COLORS['ETH-USD']),
        tickprefix='$',
        row=1, col=1, secondary_y=True
    )
    fig.update_yaxes(title_text='Volatility (%)', row=2, col=1)

    # Save
    output_path.parent.mkdir(exist_ok=True)
    fig.write_html(output_path, include_plotlyjs=True, full_html=True)

    logger.info(f"Price volatility chart saved to {output_path}")


def plot_price_change_trends(output_path: Path = None) -> None:
    """
    Generate price change percentage trends over time.
    Shows hourly price movements and cumulative trends.

    Args:
        output_path: Path to save chart (default: charts/price_change_trends.html)
    """
    if output_path is None:
        output_path = config.CHARTS_DIR / "price_change_trends.html"

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

    # Create figure with 2 rows
    fig = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.1,
        subplot_titles=('Hourly Price Change Percentage', 'Cumulative Price Change Over Time')
    )

    # Top plot: Hourly price change percentage
    for product in df['product'].unique():
        product_df = df[df['product'] == product]
        color = COLORS.get(product, '#808080')

        # Fill area
        fig.add_trace(
            go.Scatter(
                x=product_df['datetime'],
                y=product_df['price_change_pct'],
                name=product,
                line=dict(color=color, width=1.5),
                mode='lines+markers',
                marker=dict(size=3),
                opacity=0.8,
                fill='tozeroy',
                fillcolor=f"rgba({int(color[1:3], 16)}, {int(color[3:5], 16)}, {int(color[5:7], 16)}, 0.2)",
                hovertemplate=f'<b>{product}</b><br>Change: %{{y:.3f}}%<extra></extra>'
            ),
            row=1, col=1
        )

    # Add zero line
    fig.add_hline(y=0, line_dash="dash", line_color="black", opacity=0.5, row=1, col=1)

    # Bottom plot: Cumulative price change
    for product in df['product'].unique():
        product_df = df[df['product'] == product].copy()
        product_df['cumulative_change'] = product_df['price_change_pct'].cumsum()
        fig.add_trace(
            go.Scatter(
                x=product_df['datetime'],
                y=product_df['cumulative_change'],
                name=f'{product} (Cumulative)',
                line=dict(color=COLORS.get(product, '#808080'), width=2),
                opacity=0.8,
                showlegend=False,
                hovertemplate=f'<b>{product}</b><br>Cumulative: %{{y:.2f}}%<extra></extra>'
            ),
            row=2, col=1
        )

    # Add zero line
    fig.add_hline(y=0, line_dash="dash", line_color="black", opacity=0.5, row=2, col=1)

    # Update layout
    fig.update_layout(
        title=dict(
            text='Price Change Trends',
            font=dict(size=18, color='#333'),
            x=0.5
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
        height=700
    )

    # Update axes
    fig.update_xaxes(tickformat='%m/%d', title_text='Date', row=2, col=1)
    fig.update_yaxes(title_text='Price Change (%)', row=1, col=1)
    fig.update_yaxes(title_text='Cumulative Price Change (%)', row=2, col=1)

    # Save
    output_path.parent.mkdir(exist_ok=True)
    fig.write_html(output_path, include_plotlyjs=True, full_html=True)

    logger.info(f"Price change trends chart saved to {output_path}")
