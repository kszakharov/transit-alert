#!/usr/bin/env python3
"""
TTC Service Alerts Fetcher
Retrieves and processes service alerts from TTC's GTFS-RT feed
"""

import requests
import json
from datetime import datetime
import time
import logging
from typing import Dict, List, Optional

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class TTCAlertsFetcher:
    def __init__(self):
        self.alerts_url = "https://bustime.ttc.ca/gtfsrt/alerts"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'TTC-Alerts-Monitor/1.0'
        })
    
    def fetch_alerts(self) -> Optional[bytes]:
        """Fetch raw GTFS-RT alerts data"""
        try:
            response = self.session.get(self.alerts_url, timeout=30)
            response.raise_for_status()
            return response.content
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to fetch alerts: {e}")
            return None
    
    def parse_gtfs_rt_alerts(self, data: bytes) -> List[Dict]:
        """
        Parse GTFS-RT protobuf data
        Note: This requires the gtfs-realtime-bindings library
        Install with: pip install gtfs-realtime-bindings
        """
        try:
            from google.transit import gtfs_realtime_pb2
            
            feed = gtfs_realtime_pb2.FeedMessage()
            feed.ParseFromString(data)
            
            alerts = []
            for entity in feed.entity:
                if entity.HasField('alert'):
                    alert = entity.alert
                    alert_data = {
                        'id': entity.id,
                        'cause': alert.cause,
                        'effect': alert.effect,
                        'url': getattr(alert.url, 'translation', [{}])[0].get('text', '') if alert.HasField('url') else '',
                        'header_text': '',
                        'description_text': '',
                        'active_period': [],
                        'informed_entity': []
                    }
                    
                    # Extract header text
                    if alert.HasField('header_text'):
                        for translation in alert.header_text.translation:
                            if translation.language == 'en' or not alert_data['header_text']:
                                alert_data['header_text'] = translation.text
                    
                    # Extract description text
                    if alert.HasField('description_text'):
                        for translation in alert.description_text.translation:
                            if translation.language == 'en' or not alert_data['description_text']:
                                alert_data['description_text'] = translation.text
                    
                    # Extract active periods
                    for period in alert.active_period:
                        period_data = {}
                        if period.HasField('start'):
                            period_data['start'] = datetime.fromtimestamp(period.start)
                        if period.HasField('end'):
                            period_data['end'] = datetime.fromtimestamp(period.end)
                        alert_data['active_period'].append(period_data)
                    
                    # Extract informed entities (routes, stops, etc.)
                    for entity_selector in alert.informed_entity:
                        entity_data = {}
                        if entity_selector.HasField('route_id'):
                            entity_data['route_id'] = entity_selector.route_id
                        if entity_selector.HasField('stop_id'):
                            entity_data['stop_id'] = entity_selector.stop_id
                        if entity_selector.HasField('agency_id'):
                            entity_data['agency_id'] = entity_selector.agency_id
                        alert_data['informed_entity'].append(entity_data)
                    
                    alerts.append(alert_data)
            
            return alerts
            
        except ImportError:
            logger.error("gtfs-realtime-bindings not installed. Install with: pip install gtfs-realtime-bindings")
            return []
        except Exception as e:
            logger.error(f"Failed to parse GTFS-RT data: {e}")
            return []
    
    def format_alert(self, alert: Dict) -> str:
        """Format an alert for display"""
        lines = []
        lines.append(f"Alert ID: {alert['id']}")
        lines.append(f"Header: {alert['header_text']}")
        
        if alert['description_text']:
            lines.append(f"Description: {alert['description_text']}")
        
        if alert['url']:
            lines.append(f"URL: {alert['url']}")
        
        # Format cause and effect
        cause_map = {
            1: "Unknown", 2: "Other", 3: "Technical Problem", 4: "Strike", 5: "Demonstration",
            6: "Accident", 7: "Holiday", 8: "Weather", 9: "Maintenance", 10: "Construction",
            11: "Police Activity", 12: "Medical Emergency"
        }
        effect_map = {
            1: "No Service", 2: "Reduced Service", 3: "Significant Delays", 4: "Detour",
            5: "Additional Service", 6: "Modified Service", 7: "Other Effect", 8: "Unknown Effect",
            9: "Stop Moved"
        }
        
        lines.append(f"Cause: {cause_map.get(alert['cause'], 'Unknown')}")
        lines.append(f"Effect: {effect_map.get(alert['effect'], 'Unknown')}")
        
        # Format active periods
        if alert['active_period']:
            lines.append("Active Periods:")
            for period in alert['active_period']:
                start = period.get('start', 'Not specified')
                end = period.get('end', 'Not specified')
                lines.append(f"  From: {start} To: {end}")
        
        # Format affected routes/stops
        if alert['informed_entity']:
            affected = []
            for entity in alert['informed_entity']:
                if 'route_id' in entity:
                    affected.append(f"Route {entity['route_id']}")
                if 'stop_id' in entity:
                    affected.append(f"Stop {entity['stop_id']}")
            if affected:
                lines.append(f"Affected: {', '.join(affected)}")
        
        return '\n'.join(lines)
    
    def get_and_display_alerts(self):
        """Fetch and display all current alerts"""
        logger.info("Fetching TTC service alerts...")
        
        data = self.fetch_alerts()
        if not data:
            logger.error("Failed to fetch alerts data")
            return
        
        alerts = self.parse_gtfs_rt_alerts(data)
        
        if not alerts:
            print("No service alerts found")
            return
        
        print(f"\n=== TTC Service Alerts ({len(alerts)} found) ===")
        print(f"Retrieved at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 50)
        
        for i, alert in enumerate(alerts, 1):
            print(f"\nAlert {i}:")
            print("-" * 30)
            print(self.format_alert(alert))
    
    def monitor_alerts(self, interval_minutes: int = 5):
        """Monitor alerts continuously"""
        logger.info(f"Starting alert monitoring (checking every {interval_minutes} minutes)")
        
        while True:
            try:
                self.get_and_display_alerts()
                print(f"\nNext check in {interval_minutes} minutes...")
                time.sleep(interval_minutes * 60)
            except KeyboardInterrupt:
                logger.info("Monitoring stopped by user")
                break
            except Exception as e:
                logger.error(f"Error during monitoring: {e}")
                time.sleep(60)  # Wait 1 minute before retrying

def main():
    """Main function with command line options"""
    import argparse
    
    parser = argparse.ArgumentParser(description='TTC Service Alerts Fetcher')
    parser.add_argument('--monitor', action='store_true', 
                       help='Monitor alerts continuously')
    parser.add_argument('--interval', type=int, default=5,
                       help='Check interval in minutes for monitoring (default: 5)')
    parser.add_argument('--json', action='store_true',
                       help='Output alerts in JSON format')
    
    args = parser.parse_args()
    
    fetcher = TTCAlertsFetcher()
    
    if args.monitor:
        fetcher.monitor_alerts(args.interval)
    else:
        if args.json:
            # JSON output mode
            data = fetcher.fetch_alerts()
            if data:
                alerts = fetcher.parse_gtfs_rt_alerts(data)
                print(json.dumps(alerts, indent=2, default=str))
        else:
            fetcher.get_and_display_alerts()

if __name__ == "__main__":
    main()
