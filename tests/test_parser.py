"""
Tests for the GTFS-RT Parser module
"""

import pytest
from unittest.mock import patch, Mock
from datetime import datetime
from ttc_alerts.core.parser import parse_gtfs_rt_alerts

@pytest.fixture
def mock_gtfs_message():
    """Create a mock GTFS-RT message for testing"""
    mock_message = Mock()
    mock_entity = Mock()
    mock_alert = Mock()
    
    # Set up alert data
    mock_alert.cause = 3  # Technical Problem
    mock_alert.effect = 3  # Significant Delays
    
    # Set up header text
    mock_header = Mock()
    mock_header.translation = [Mock(language="en", text="Test Alert")]
    mock_alert.header_text = mock_header
    
    # Set up description text
    mock_description = Mock()
    mock_description.translation = [Mock(language="en", text="Test Description")]
    mock_alert.description_text = mock_description
    
    # Set up active period
    mock_period = Mock()
    mock_period.start = int(datetime.now().timestamp())
    mock_period.end = int(datetime.now().timestamp()) + 3600
    mock_alert.active_period = [mock_period]
    
    # Set up informed entity
    mock_entity_selector = Mock()
    mock_entity_selector.route_id = "501"
    mock_alert.informed_entity = [mock_entity_selector]
    
    mock_alert.HasField = Mock(side_effect=lambda field: field in ["header_text", "description_text", "active_period"])
    
    mock_entity.alert = mock_alert
    mock_entity.id = "test_alert_1"
    mock_message.entity = [mock_entity]
    
    return mock_message

@patch("google.transit.gtfs_realtime_pb2.FeedMessage")
def test_parse_gtfs_rt_alerts_success(mock_feed_message, mock_gtfs_message):
    """Test successful parsing of GTFS-RT alerts"""
    mock_feed_message.return_value = mock_gtfs_message
    
    result = parse_gtfs_rt_alerts(b"test data")
    
    assert len(result) == 1
    alert = result[0]
    assert alert["id"] == "test_alert_1"
    assert alert["cause"] == 3
    assert alert["effect"] == 3
    assert alert["header_text"] == "Test Alert"
    assert alert["description_text"] == "Test Description"
    assert len(alert["active_period"]) == 1
    assert len(alert["informed_entity"]) == 1
    assert alert["informed_entity"][0]["route_id"] == "501"

def test_parse_gtfs_rt_alerts_import_error():
    """Test handling of missing gtfs-realtime-bindings"""
    with patch("google.transit.gtfs_realtime_pb2", None):
        result = parse_gtfs_rt_alerts(b"test data")
        assert result == []

def test_parse_gtfs_rt_alerts_parse_error():
    """Test handling of parsing errors"""
    with patch("google.transit.gtfs_realtime_pb2.FeedMessage") as mock_feed:
        mock_feed.return_value.ParseFromString.side_effect = Exception("Parse error")
        result = parse_gtfs_rt_alerts(b"test data")
        assert result == [] 