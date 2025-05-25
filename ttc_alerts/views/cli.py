"""
Command-line interface for TTC Alerts
"""

import argparse
import json
from typing import Optional
import sys
import logging
from datetime import datetime

from ..controllers.fetcher import TTCAlertService
from ..utils.logging import setup_logging
from ..models import filter_duplicates

logger = logging.getLogger(__name__)

def main() -> None:
    """Main entry point for the CLI"""
    parser = argparse.ArgumentParser(description='TTC Service Alerts Fetcher')
    parser.add_argument('--monitor', action='store_true', 
                       help='Monitor alerts continuously')
    parser.add_argument('--interval', type=int, default=5,
                       help='Check interval in minutes for monitoring (default: 5)')
    parser.add_argument('--json', action='store_true',
                       help='Output alerts in JSON format')
    parser.add_argument('--log-file', type=str,
                       help='Path to log file')
    parser.add_argument('--debug', action='store_true',
                       help='Enable debug logging')
    
    args = parser.parse_args()
    
    # Set up logging
    log_level = 'DEBUG' if args.debug else 'INFO'
    setup_logging(level=log_level, log_file=args.log_file)
    

    try:
        if args.monitor:
            TTCAlertService.monitor_alerts(args.interval)
        else:
            alerts = TTCAlertService.get_alerts()
            if not alerts:
                print("No service alerts found")
            else:
                print(f"\n=== TTC Service Alerts ({len(alerts)} found) ===")
                print(f"Retrieved at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                print("=" * 100)
                logger.info(f"Filtering duplicates from {len(alerts)} alerts")
                alerts = filter_duplicates(alerts, "description")
                print("=" * 100)
                for alert in alerts:
                    #print(f"\nAlert {i}:")
                    print("=" * 60)
                    print(alert.format())
    except Exception as e:
        logger.error(f"Error: {e}")
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 