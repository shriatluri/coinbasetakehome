"""
Visualization layer: Main entry point for generating charts from DuckDB data.
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

import logging

from visualization.required import plot_hourly_volume, plot_average_price
from visualization.additional import (
    plot_price_volatility,
    plot_price_change_trends
)
from ETL_process import config

logger = logging.getLogger(__name__)


def generate_required_charts() -> None:
    """Generate required visualizations (hourly volume and average price)."""
    logger.info("Generating required visualizations...")

    plot_hourly_volume()
    plot_average_price()

    logger.info(f"Required charts saved to {config.CHARTS_DIR}")


def generate_additional_charts() -> None:
    """Generate additional visualizations (volatility and price change trends)."""
    logger.info("Generating additional visualizations...")

    plot_price_volatility()
    plot_price_change_trends()

    logger.info(f"Additional charts saved to {config.CHARTS_DIR}")


def generate_all_charts() -> None:
    """Generate all visualizations (required + additional)."""
    logger.info("Generating all visualizations...")

    generate_required_charts()
    generate_additional_charts()

    logger.info(f"All charts saved to {config.CHARTS_DIR}")


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

    args = parser.parse_args()

    if args.type == 'required':
        generate_required_charts()
        print(f"Required charts saved to {config.CHARTS_DIR}")
    elif args.type == 'additional':
        generate_additional_charts()
        print(f"Additional charts saved to {config.CHARTS_DIR}")
    else:  # all
        generate_all_charts()
        print(f"All charts saved to {config.CHARTS_DIR}")
