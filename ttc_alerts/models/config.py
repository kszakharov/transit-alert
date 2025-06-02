"""
Configuration models for TTC Alerts
"""

from dataclasses import dataclass
from typing import Optional
import yaml
import os
from pathlib import Path


@dataclass
class User:
    """User notification configuration"""
    username: str
    chat_id: str
    filters: Optional[list[str]] = None


@dataclass
class TelegramConfig:
    """Telegram notification configuration"""
    bot_token: str


@dataclass
class AppConfig:
    """Application configuration"""
    users: list[User]
    telegram: Optional[TelegramConfig] = None

    @classmethod
    def load(cls, config_path: Optional[str] = None) -> 'AppConfig':
        """
        Load configuration from YAML file

        Args:
            config_path: Path to config file. If None, will look for config.yaml in:
                        1. Current directory
                        2. ~/.config/ttc-alerts/
                        3. /etc/ttc-alerts/
        """
        if config_path is None:
            # Try to find config in standard locations
            possible_paths = [
                Path("config.yaml"),
                Path.home() / ".config" / "ttc-alerts" / "config.yaml",
                Path("/etc/ttc-alerts/config.yaml")
            ]

            for path in possible_paths:
                if path.exists():
                    config_path = str(path)
                    break
            else:
                return cls()  # Return default config if no config file found

        if not os.path.exists(config_path):
            return cls()

        with open(config_path, 'r') as f:
            config_data = yaml.safe_load(f)

        users = [User(**user) for user in config_data["users"]]
        telegram_config = None
        if telegram_data := config_data.get('telegram'):
            telegram_config = TelegramConfig(
                bot_token=telegram_data['bot_token'],
            )

        return cls(users=users, telegram=telegram_config)
