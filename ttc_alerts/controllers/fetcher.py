"""
TTC Alerts Fetcher module
"""

import requests
from datetime import datetime
import time
import json
from google.protobuf.json_format import MessageToJson
from google.transit import gtfs_realtime_pb2
from typing import Optional

from ..models.alert import TTCAlert
from ..models import filter_duplicates
from ..models.config import AppConfig
from ..controllers.telegram import TelegramController
from ..utils.logging import setup_logging


logger = setup_logging(__name__)


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
    alerts_url: str = "https://bustime.ttc.ca/gtfsrt/alerts"
    session: requests.Session = requests.Session()
    session.headers.update({
        'User-Agent': 'TTC-Alerts-Monitor/1.0'
    })

    config: Optional[AppConfig] = None

    _telegram_controller: Optional[TelegramController] = None

    @classmethod
    def setup_config(cls, config: AppConfig) -> None:
        """Setup config"""

        cls.config = config


    @classmethod
    def setup_telegram(cls, config: AppConfig) -> None:
        """Setup Telegram notifications"""
        if config.telegram:
            cls._telegram_controller = TelegramController(config.telegram)
            logger.info("Telegram notifications enabled")

    @classmethod
    def get_alerts(cls) -> list[TTCAlert]:
        """Fetch and parse GTFS-RT alerts data, returning a list of TTCAlert objects."""

        try:
            logger.info("=" * 100)
            logger.info("Fetching TTC Alerts")
            response = cls.session.get(cls.alerts_url, timeout=30)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to fetch alerts: {e}")
            raise NetworkError(f"Network error: {e}")
        
        data = response.content
        feed = gtfs_realtime_pb2.FeedMessage()
        feed.ParseFromString(data)

        alerts: list[TTCAlert] = []
        for entity in feed.entity:
            message = json.loads(MessageToJson(entity))
            if alert := message.get("alert"):
                ttc_alert = TTCAlert(**alert)
                alerts.append(ttc_alert)

        alerts_number = len(alerts)
        logger.info(f"Received {alerts_number} TTC Alerts")
        alerts = filter_duplicates(alerts, "description")
        logger.info(f"Filtered out {alerts_number - len(alerts)} duplicates out of {alerts_number} alerts")
        for alert in alerts:
            logger.info("=" * 60)
            logger.info(alert.format())

        return alerts

        #except Exception as e:
        #    logger.error(f"Failed to parse GTFS-RT data: {e}")
        #    return []
    
    @classmethod
    def monitor_alerts(cls, interval_minutes: int = 1) -> None:
        """Monitor alerts continuously"""

        def filter_user_alerts(alerts: dict[str, list[TTCAlert]], user_filters: Optional[list[str]] = None) -> dict[str, list[TTCAlert]]:
            if not user_filters:
                return alerts

            user_alerts = {
                "resolved": [],
                "new": [],
            }
            for alert_state in ["resolved", "new"]:
                for user_filter in user_filters:
                    for alert in alerts[alert_state]:
                        if user_filter in str(alert):
                            user_alerts[alert_state].append(alert)

            return user_alerts

        logger.info(f"Starting alert monitoring (checking every {interval_minutes} minutes)")

        current_alerts = []
        
        while True:
            try:
                previous_alerts = current_alerts
                current_alerts = cls.get_alerts()

                alerts = cls.compare_alerts(previous_alerts, current_alerts)
                logger.info("*" * 100)

                if alerts["resolved"]:
                    logger.info(f"RESOLVED:\n\t{"\n\t".join(str(alert) for alert in alerts["resolved"])}")
                if alerts["unresolved"]:
                    logger.info(f"UNRESOLVED:\n\t{"\n\t".join(str(alert) for alert in alerts["unresolved"])}")
                if alerts["new"]:
                    logger.info(f"NEW:\n\t{"\n\t".join(str(alert) for alert in alerts["new"])}")
                # Send Telegram notifications if enabled
                if cls._telegram_controller:

                    for user in cls.config.users:
                        user_alerts = filter_user_alerts(alerts=alerts, user_filters=user.filters)
                        if user_alerts["resolved"]:
                            cls._telegram_controller.notify_alerts("resolved", user_alerts["resolved"], user.chat_id)
                        if user_alerts["new"]:
                            cls._telegram_controller.notify_alerts("new", user_alerts["new"], user.chat_id)


                logger.info(f"\nNext check in {interval_minutes} minutes...")
                logger.info("*" * 100)
                time.sleep(interval_minutes * 60)
            except KeyboardInterrupt:
                logger.info("Monitoring stopped by user")
                break
            except Exception as e:
                logger.exception(e)
                time.sleep(60)


    def compare_alerts(previous_alerts: TTCAlert, current_alerts: TTCAlert) -> dict[str, list[TTCAlert]]:
        return {
            "resolved": list(set(previous_alerts) - set(current_alerts)),
            "unresolved": list(set(previous_alerts) & set(current_alerts)),
            "new": list(set(current_alerts) - set(previous_alerts)),
        }