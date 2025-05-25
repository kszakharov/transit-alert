"""
Tests for the TTC Alerts Fetcher module
"""

import pytest
from unittest.mock import Mock, patch
from ttc_alerts.core.fetcher import TTCAlertsFetcher

@pytest.fixture
def fetcher():
    """Create a TTCAlertsFetcher instance for testing"""
    return TTCAlertsFetcher()

def test_fetcher_initialization(fetcher):
    """Test fetcher initialization"""
    assert fetcher.alerts_url == "https://bustime.ttc.ca/gtfsrt/alerts"
    assert fetcher.session.headers["User-Agent"] == "TTC-Alerts-Monitor/1.0"

@patch("requests.Session.get")
def test_fetch_alerts_success(mock_get, fetcher):
    """Test successful alert fetching"""
    # Mock response
    mock_response = Mock()
    mock_response.content = b"test data"
    mock_response.raise_for_status = Mock()
    mock_get.return_value = mock_response

    result = fetcher.fetch_alerts()
    assert result == b"test data"
    mock_get.assert_called_once_with(fetcher.alerts_url, timeout=30)

@patch("requests.Session.get")
def test_fetch_alerts_failure(mock_get, fetcher):
    """Test failed alert fetching"""
    # Mock request exception
    mock_get.side_effect = Exception("Network error")

    with pytest.raises(Exception, match="Network error"):
        fetcher.fetch_alerts() 