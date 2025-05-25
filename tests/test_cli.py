"""
Tests for the CLI module
"""

import pytest
from unittest.mock import patch, MagicMock
from ttc_alerts.cli import main

@pytest.fixture
def mock_fetcher():
    """Mock TTCAlertsFetcher"""
    with patch("ttc_alerts.cli.TTCAlertsFetcher") as mock:
        instance = mock.return_value
        instance.fetch_alerts.return_value = b"test data"
        instance.get_and_display_alerts.return_value = None
        instance.monitor_alerts.return_value = None
        yield instance

def test_cli_basic(mock_fetcher):
    """Test basic CLI functionality"""
    with patch("sys.argv", ["ttc-alerts"]):
        main()
    mock_fetcher.get_and_display_alerts.assert_called_once()

def test_cli_monitor(mock_fetcher):
    """Test monitor mode"""
    with patch("sys.argv", ["ttc-alerts", "--monitor"]):
        main()
    mock_fetcher.monitor_alerts.assert_called_once_with(5)  # Default interval

def test_cli_monitor_custom_interval(mock_fetcher):
    """Test monitor mode with custom interval"""
    with patch("sys.argv", ["ttc-alerts", "--monitor", "--interval", "10"]):
        main()
    mock_fetcher.monitor_alerts.assert_called_once_with(10)

def test_cli_json_output(mock_fetcher):
    """Test JSON output mode"""
    with patch("sys.argv", ["ttc-alerts", "--json"]):
        with patch("builtins.print") as mock_print:
            main()
            mock_print.assert_called_once()

def test_cli_debug_logging(mock_fetcher):
    """Test debug logging mode"""
    with patch("sys.argv", ["ttc-alerts", "--debug"]):
        with patch("ttc_alerts.cli.setup_logging") as mock_setup:
            with patch("argparse.ArgumentParser.parse_args") as mock_parse:
                mock_parse.return_value = MagicMock(
                    monitor=False,
                    interval=5,
                    json=False,
                    log_file=None,
                    debug=True
                )
                main()
                mock_setup.assert_called_once_with(level="DEBUG", log_file=None)

def test_cli_log_file(mock_fetcher):
    """Test log file option"""
    with patch("sys.argv", ["ttc-alerts", "--log-file", "test.log"]):
        with patch("ttc_alerts.cli.setup_logging") as mock_setup:
            with patch("argparse.ArgumentParser.parse_args") as mock_parse:
                mock_parse.return_value = MagicMock(
                    monitor=False,
                    interval=5,
                    json=False,
                    log_file="test.log",
                    debug=False
                )
                main()
                mock_setup.assert_called_once_with(level="INFO", log_file="test.log") 