"""
TTC Alerts Fetcher module
"""

import requests
import logging
from typing import Optional, List, Dict
from datetime import datetime
import time
import sys
import json
from google.protobuf.json_format import MessageToJson
from google.transit import gtfs_realtime_pb2
from google.transit.gtfs_realtime_pb2 import FeedEntity

from ..models.alert import TTCAlert

logger = logging.getLogger(__name__)

class TTCAlertsError(Exception):
    """Base exception for TTC Alerts errors."""
    pass

class NetworkError(TTCAlertsError):
    """Raised when a network error occurs."""
    pass

class ParseError(TTCAlertsError):
    """Raised when parsing fails."""
    pass

class TTCAlertService:
    """Service for fetching and monitoring TTC alerts."""
    alerts_url = "https://bustime.ttc.ca/gtfsrt/alerts"
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'TTC-Alerts-Monitor/1.0'
    })
    
    #def __init__(self):
    #    self.alerts_url = "https://bustime.ttc.ca/gtfsrt/alerts"
    #    self.session = requests.Session()
    #    self.session.headers.update({
    #        'User-Agent': 'TTC-Alerts-Monitor/1.0'
    #    })
    
    @classmethod
    def get_alerts(cls) -> list[TTCAlert]:
        """Fetch and parse GTFS-RT alerts data, returning a list of TTCAlert objects."""
        try:
            response = cls.session.get(cls.alerts_url, timeout=30)
            response.raise_for_status()
            data = response.content
            feed = gtfs_realtime_pb2.FeedMessage()
            feed.ParseFromString(data)
            alerts = []
            #alerts = [TTCAlert(**json.loads(MessageToJson(entity))["alert"]) for entity in feed.entity if entity.HasField("alert")]
            for entity in feed.entity:
                message = json.loads(MessageToJson(entity))
                if alert := message.get("alert"):
                    ttc_alert = TTCAlert(**alert)
                    alerts.append(ttc_alert)
            return alerts
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to fetch alerts: {e}")
            raise NetworkError(f"Network error: {e}")
        except Exception as e:
            logger.error(f"Failed to parse GTFS-RT data: {e}")
            return []
    
    @classmethod
    def monitor_alerts(cls, interval_minutes: int = 5):
        """Monitor alerts continuously"""
        logger.info(f"Starting alert monitoring (checking every {interval_minutes} minutes)")
        
        while True:
            try:
                alerts = cls.get_alerts()
                if not alerts:
                    print("No service alerts found")
                else:
                    print(f"\n=== TTC Service Alerts ({len(alerts)} found) ===")
                    print(f"Retrieved at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                    print("=" * 50)
                    for i, alert in enumerate(alerts, 1):
                        print(f"\nAlert {i}:")
                        print("-" * 30)
                        print(alert.format())
                print(f"\nNext check in {interval_minutes} minutes...")
                time.sleep(interval_minutes * 60)
            except KeyboardInterrupt:
                logger.info("Monitoring stopped by user")
                break
            except Exception as e:
                logger.error(f"Error during monitoring: {e}")
                print(f"Error: {e}")
                time.sleep(60)  # Wait 1 minute before retrying 
