"""
TTC Alerts package
"""

from .models.alert import TTCAlert
from .controllers.fetcher import TTCAlertService
from .views.cli import main

__version__ = "0.1.0" 