#!/usr/bin/env python3
"""
Main entry point for the Coinbase Data Pipeline.

Runs the complete pipeline end-to-end: ETL → Visualizations
"""

import argparse
import logging
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from ETL_process.pipeline import run as run_etl
from visualization.visualize import (
    generate_required_charts,
    generate_additional_charts,
    generate_all_charts
)
from ETL_process import config

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser(
        description='Coinbase Data Pipeline - Run ETL and generate visualizations',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run everything (ETL + all visualizations)
  python run.py

  # Full refresh and generate all charts
  python run.py --full-refresh

  # Skip ETL, only generate visualizations
  python run.py --skip-etl

  # Run ETL but only generate required charts
  python run.py --charts required
        """
    )
    
    # ETL options
    parser.add_argument(
        '--full-refresh',
        action='store_true',
        help='Ignore existing data, fetch everything from scratch'
    )
    parser.add_argument(
        '--skip-etl',
        action='store_true',
        help='Skip ETL pipeline, only generate visualizations'
    )
    parser.add_argument(
        '--start',
        help='Start date for data fetch (ISO format, e.g., 2025-11-17T00:00:00Z)'
    )
    parser.add_argument(
        '--end',
        help='End date for data fetch (ISO format, e.g., 2025-11-24T23:59:59Z)'
    )
    parser.add_argument(
        '--products',
        nargs='+',
        help='Products to fetch (e.g., BTC-USD ETH-USD)'
    )
    
    # Visualization options
    parser.add_argument(
        '--charts',
        choices=['required', 'additional', 'all'],
        default='all',
        help='Which charts to generate: required (2 charts), additional (3 charts), or all (5 charts, default)'
    )
    parser.add_argument(
        '--skip-visualizations',
        action='store_true',
        help='Skip visualization generation, only run ETL'
    )
    
    args = parser.parse_args()
    
    # Run ETL pipeline
    if not args.skip_etl:
        logger.info("=" * 60)
        logger.info("STEP 1: Running ETL Pipeline")
        logger.info("=" * 60)
        
        try:
            stats = run_etl(
                products=args.products,
                start=args.start,
                end=args.end,
                incremental=not args.full_refresh
            )
            logger.info(f"ETL Pipeline completed successfully!")
            logger.info(f"Statistics: {stats}")
        except Exception as e:
            logger.error(f"ETL Pipeline failed: {e}")
            sys.exit(1)
    else:
        logger.info("Skipping ETL pipeline (--skip-etl specified)")
    
    # Generate visualizations
    if not args.skip_visualizations:
        logger.info("")
        logger.info("=" * 60)
        logger.info("STEP 2: Generating Visualizations")
        logger.info("=" * 60)
        
        try:
            if args.charts == 'required':
                generate_required_charts()
                logger.info(f"Required charts saved to {config.CHARTS_DIR}")
            elif args.charts == 'additional':
                generate_additional_charts()
                logger.info(f"Additional charts saved to {config.CHARTS_DIR}")
            else:  # all
                generate_all_charts()
                logger.info(f"All charts saved to {config.CHARTS_DIR}")
        except Exception as e:
            logger.error(f"Visualization generation failed: {e}")
            sys.exit(1)
    else:
        logger.info("Skipping visualizations (--skip-visualizations specified)")
    
    logger.info("")
    logger.info("=" * 60)
    logger.info("Pipeline completed successfully!")
    logger.info("=" * 60)


if __name__ == "__main__":
    main()

