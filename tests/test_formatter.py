"""
Tests for the Alert Formatter module
"""

import pytest
from datetime import datetime
from ttc_alerts.core.formatter import format_alert

@pytest.fixture
def sample_alert():
    """Create a sample alert for testing"""
    return {
        "id": "test_alert_1",
        "cause": 3,  # Technical Problem
        "effect": 3,  # Significant Delays
        "header_text": "Test Alert",
        "description_text": "Test Description",
        "url": "https://example.com",
        "active_period": [
            {
                "start": datetime(2024, 1, 1, 12, 0),
                "end": datetime(2024, 1, 1, 13, 0)
            }
        ],
        "informed_entity": [
            {"route_id": "501"},
            {"stop_id": "1234"}
        ]
    }

def test_format_alert_basic(sample_alert):
    """Test basic alert formatting"""
    result = format_alert(sample_alert)
    
    # Check that all expected fields are present
    assert "Alert ID: test_alert_1" in result
    assert "Header: Test Alert" in result
    assert "Description: Test Description" in result
    assert "URL: https://example.com" in result
    assert "Cause: Technical Problem" in result
    assert "Effect: Significant Delays" in result
    
    # Check active period formatting
    assert "Active Periods:" in result
    assert "From: 2024-01-01 12:00:00" in result
    assert "To: 2024-01-01 13:00:00" in result
    
    # Check affected entities
    assert "Affected: Route 501, Stop 1234" in result

def test_format_alert_minimal():
    """Test formatting of minimal alert data"""
    minimal_alert = {
        "id": "test_alert_2",
        "cause": 1,  # Unknown
        "effect": 8,  # Unknown Effect
        "header_text": "Minimal Alert",
        "description_text": "",
        "url": "",
        "active_period": [],
        "informed_entity": []
    }
    
    result = format_alert(minimal_alert)
    
    assert "Alert ID: test_alert_2" in result
    assert "Header: Minimal Alert" in result
    assert "Description:" not in result
    assert "URL:" not in result
    assert "Cause: Unknown" in result
    assert "Effect: Unknown Effect" in result
    assert "Active Periods:" not in result
    assert "Affected:" not in result

def test_format_alert_unknown_cause_effect():
    """Test formatting of alert with unknown cause/effect"""
    alert = {
        "id": "test_alert_3",
        "cause": 999,  # Unknown cause
        "effect": 999,  # Unknown effect
        "header_text": "Unknown Alert",
        "description_text": "",
        "url": "",
        "active_period": [],
        "informed_entity": []
    }
    
    result = format_alert(alert)
    
    assert "Cause: Unknown" in result
    assert "Effect: Unknown" in result 