"""
Visualization layer: Main entry point for generating charts from DuckDB data.
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

import logging
import webbrowser

from visualization.required import plot_hourly_volume, plot_average_price
from visualization.additional import (
    plot_price_volatility,
    plot_price_change_trends
)
from ETL_process import config

logger = logging.getLogger(__name__)


def open_charts(chart_files: list) -> None:
    """Open chart files in the default web browser."""
    for chart_file in chart_files:
        chart_path = config.CHARTS_DIR / chart_file
        if chart_path.exists():
            webbrowser.open(f"file://{chart_path.resolve()}")


def generate_required_charts(open_browser: bool = False) -> None:
    """Generate required visualizations (hourly volume and average price)."""
    logger.info("Generating required visualizations...")

    plot_hourly_volume()
    plot_average_price()

    logger.info(f"Required charts saved to {config.CHARTS_DIR}")

    if open_browser:
        open_charts(["hourly_volume.html", "avg_price.html"])


def generate_additional_charts(open_browser: bool = False) -> None:
    """Generate additional visualizations (volatility and price change trends)."""
    logger.info("Generating additional visualizations...")

    plot_price_volatility()
    plot_price_change_trends()

    logger.info(f"Additional charts saved to {config.CHARTS_DIR}")

    if open_browser:
        open_charts(["price_volatility.html", "price_change_trends.html"])


def generate_all_charts(open_browser: bool = False) -> None:
    """Generate all visualizations (required + additional)."""
    logger.info("Generating all visualizations...")

    generate_required_charts(open_browser=False)
    generate_additional_charts(open_browser=False)

    logger.info(f"All charts saved to {config.CHARTS_DIR}")

    if open_browser:
        open_charts([
            "hourly_volume.html",
            "avg_price.html",
            "price_volatility.html",
            "price_change_trends.html"
        ])


if __name__ == "__main__":
    import argparse

    logging.basicConfig(level=logging.INFO)

    parser = argparse.ArgumentParser(description='Generate cryptocurrency trading visualizations')
    parser.add_argument(
        '--type',
        choices=['required', 'additional', 'all'],
        default='all',
        help='Type of visualizations to generate: required (hourly volume, avg price), additional (volatility, trends), or all (default)'
    )

    parser.add_argument(
        '--no-open',
        action='store_true',
        help='Do not automatically open charts in browser'
    )

    args = parser.parse_args()
    open_browser = not args.no_open

    if args.type == 'required':
        generate_required_charts(open_browser=open_browser)
        print(f"Required charts saved to {config.CHARTS_DIR}")
    elif args.type == 'additional':
        generate_additional_charts(open_browser=open_browser)
        print(f"Additional charts saved to {config.CHARTS_DIR}")
    else:  # all
        generate_all_charts(open_browser=open_browser)
        print(f"All charts saved to {config.CHARTS_DIR}")
