#!/usr/bin/env python3
"""
Binance Stream Runner - Entry point for running Binance cryptocurrency data streaming.

Usage:
    python run_binance_stream.py [--symbol SYMBOL] [--duration SECONDS]

Examples:
    python run_binance_stream.py                           # Stream BTCUSDT indefinitely
    python run_binance_stream.py --symbol ETHUSDT          # Stream ETHUSDT indefinitely
    python run_binance_stream.py --duration 300            # Stream for 5 minutes
"""

import argparse
import asyncio
import logging
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backend.app.ingestion.binance_stream import run_binance_stream
from backend.app.core.config import settings


def setup_logging():
    """Configure logging for the stream runner."""
    logging.basicConfig(
        level=getattr(logging, settings.log_level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('binance_stream.log', mode='a')
        ]
    )


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='Run Binance cryptocurrency data stream')
    parser.add_argument('--symbol', default=None, 
                       help=f'Trading symbol to stream (default: {settings.binance_default_symbol})')
    parser.add_argument('--duration', type=int, default=None,
                       help='Run duration in seconds (default: indefinite)')
    parser.add_argument('--verbose', action='store_true',
                       help='Enable verbose logging')
    
    args = parser.parse_args()
    
    # Setup logging
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    setup_logging()
    
    logger = logging.getLogger(__name__)
    
    symbol = args.symbol or settings.binance_default_symbol
    logger.info(f"Starting Binance stream for {symbol}")
    
    if args.duration:
        logger.info(f"Stream will run for {args.duration} seconds")
    else:
        logger.info("Stream will run indefinitely (Ctrl+C to stop)")
    
    try:
        # Run the stream
        asyncio.run(run_binance_stream(symbol=symbol, duration=args.duration))
    except KeyboardInterrupt:
        logger.info("Stream stopped by user")
    except Exception as e:
        logger.error(f"Stream failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()