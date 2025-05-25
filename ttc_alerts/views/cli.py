"""
Command-line interface for TTC Alerts
"""

import argparse
import sys
import logging
from datetime import datetime
from typing import Callable, cast

from ..controllers.fetcher import TTCAlertService
from ..utils.logging import setup_logging
from ..models import filter_duplicates


logger = setup_logging(__name__)


def parse_args() -> argparse.Namespace:
    """Initialize script parsers."""

    parser = argparse.ArgumentParser(description='TTC Service Alerts Notifier')
    parser.add_argument('--monitor', action='store_true', help='Monitor alerts continuously')
    parser.add_argument('--interval', type=int, default=5, help='Check interval in minutes for monitoring (default: 5)')
    parser.add_argument('--json', action='store_true', help='Output alerts in JSON format')
    parser.add_argument('--log-file', type=str, help='Path to log file')
    parser.add_argument('--debug', action='store_true', help='Enable debug logging')
    parser.set_defaults(func=show_alerts)

    return parser.parse_args()


def show_alerts(args: argparse.Namespace) -> None:
    if args.monitor:
        TTCAlertService.monitor_alerts(args.interval)
    else:
        logger.info("=" * 100)
        logger.info("Fetching TTC Alerts")
        alerts = TTCAlertService.get_alerts()
        alerts_number = len(alerts)
        logger.info(f"Received {alerts_number} TTC Alerts")
        
        if not alerts:
            logger.info("Nothing to do. Skipping...")
        else:
            alerts = filter_duplicates(alerts, "description")
            logger.info(f"Filtered out {alerts_number - len(alerts)} duplicates out of {alerts_number} alerts")
            for alert in alerts:
                logger.info("=" * 60)
                logger.info(alert.format())


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