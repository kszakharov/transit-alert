"""
Command-line interface for TTC Alerts
"""

import argparse
import sys
import logging

from ..controllers.fetcher import TTCAlertService
from ..utils.logging import setup_logging


logger = setup_logging(__name__)

def parse_args() -> argparse.Namespace:
    """Initialize script parsers."""

    parser = argparse.ArgumentParser(description='TTC Service Alerts Notifier')
    parser.add_argument('--monitor', action='store_true', help='Monitor alerts continuously')
    parser.add_argument('--debug', action='store_true', help='Enable debug logging')
    parser.set_defaults(func=show_alerts)

    return parser.parse_args()


def show_alerts(args: argparse.Namespace) -> None:
    if args.monitor:
        TTCAlertService.monitor_alerts()
    else:
        TTCAlertService.get_alerts()


def main() -> None:
    """Main entry point for the CLI"""

    args = parse_args()

    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)

    try:
        args.func(args)
    except Exception as e:
        logger.error(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 