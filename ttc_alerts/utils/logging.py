"""
Logging configuration module
"""

import logging
import sys
from typing import Optional
from datetime import datetime


BLUE = "\033[94m"
GREEN = "\033[92m"
PURPLE = "\033[95m"
RED = "\033[91m"
YELLOW = "\033[93m"
RESET = "\033[0m"

class ColorFormatter(logging.Formatter):

    COLORS = {
        "DEBUG": BLUE,
        "INFO": GREEN,
        "WARNING": YELLOW,
        "ERROR": RED,
        "CRITICAL": PURPLE,
    }

    def format(self, record):
        levelname = record.levelname
        color = self.COLORS.get(levelname, "")
        reset = RESET
        timestamp = datetime.fromtimestamp(record.created).strftime("%Y-%m-%d %H:%M:%S")
        filename = f"{record.filename}:{record.lineno}"
        message = super().format(record)
        message = message.replace("\\x1b", "\x1b")  # Unescape the ANSI sequences for colour console

        prefix = f"{GREEN}{timestamp}{RESET} [{filename}] {color}{levelname}{reset}"

        return "\n".join(f"{prefix}: {line}" for line in message.splitlines())



def setup_logging(name: str = None, level=logging.INFO) -> logging.Logger:
    logger = logging.getLogger(name)
    if not logger.hasHandlers():
        handler = logging.StreamHandler(sys.stdout)
        formatter = ColorFormatter("%(message)s")
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(level)
        logger.propagate = False

    return logger
