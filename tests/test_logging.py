"""
Tests for the logging utility module
"""

import pytest
import logging
from unittest.mock import patch, Mock
from ttc_alerts.utils.logging import setup_logging

def test_setup_logging_default():
    """Test default logging setup"""
    with patch("logging.basicConfig") as mock_basic_config:
        setup_logging()
        
    mock_basic_config.assert_called_once()
    args, kwargs = mock_basic_config.call_args
    assert kwargs["level"] == logging.INFO
    assert len(kwargs["handlers"]) == 1
    assert isinstance(kwargs["handlers"][0], logging.StreamHandler)

def test_setup_logging_with_file():
    """Test logging setup with file handler"""
    with patch("logging.basicConfig") as mock_basic_config:
        with patch("logging.FileHandler") as mock_file_handler:
            setup_logging(log_file="test.log")
            
    mock_basic_config.assert_called_once()
    args, kwargs = mock_basic_config.call_args
    assert kwargs["level"] == logging.INFO
    assert len(kwargs["handlers"]) == 2
    assert isinstance(kwargs["handlers"][0], logging.StreamHandler)
    mock_file_handler.assert_called_once_with("test.log")

def test_setup_logging_custom_level():
    """Test logging setup with custom level"""
    with patch("logging.basicConfig") as mock_basic_config:
        setup_logging(level=logging.DEBUG)
        
    mock_basic_config.assert_called_once()
    args, kwargs = mock_basic_config.call_args
    assert kwargs["level"] == logging.DEBUG 