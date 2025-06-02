"""
Telegram notification controller
"""

import requests
from typing import Optional
from ..models.telegram import TelegramMessage
from ..models.config import TelegramConfig
from ..utils.logging import setup_logging


logger = setup_logging(__name__)


class TelegramController:
    """Controller for sending Telegram notifications"""

    def __init__(self, config: TelegramConfig):
        """
        Initialize Telegram controller

        Args:
            config: Telegram configuration
        """
        self.config = config
        self.api_url = f"https://api.telegram.org/bot{config.bot_token}/sendMessage"

    def send_message(self, message: TelegramMessage, chat_id: str) -> bool:
        """
        Send a message to Telegram

        Args:
            message: Message to send

        Returns:
            bool: True if message was sent successfully, False otherwise
        """
        try:
            response = requests.post(
                self.api_url,
                json={
                    "chat_id": chat_id,
                    "text": message.text,
                    "parse_mode": message.parse_mode
                }
            )
            response.raise_for_status()
            logger.info(response)
            logger.info(response.content)
            return True
        except Exception as e:
            logger.error(f"Failed to send Telegram message: {e}")
            return False

    def notify_alerts(self, alert_type: str, alerts: list, chat_id: str) -> None:
        """
        Send notification about alert changes

        Args:
            alert_type: Type of alert change ("new", "resolved", or "unresolved")
            alerts: List of alerts to notify about
        """
        if message := TelegramMessage.from_alerts(alert_type, alerts):
            self.send_message(message, chat_id)
