"""
Unit tests for Observability utilities.
"""
import json
import logging
from unittest.mock import MagicMock, patch
from agent_platform.observability import JSONFormatter

def test_json_formatter_structure() -> None:
    """Verify JSONFormatter produces valid JSON with required fields."""
    formatter = JSONFormatter()
    record = logging.LogRecord(
        name="test_logger",
        level=logging.INFO,
        pathname=__file__,
        lineno=10,
        msg="Test message",
        args=(),
        exc_info=None
    )
    
    formatted = formatter.format(record)
    data = json.loads(formatted)
    
    # Check standard fields
    assert data["level"] == "INFO"
    assert data["logger"] == "test_logger"
    assert data["message"] == "Test message"
    assert "timestamp" in data

def test_json_formatter_with_exception() -> None:
    """Verify exception info is included in the JSON output."""
    formatter = JSONFormatter()
    try:
        raise ValueError("Test error")
    except ValueError:
        # Create a record with exception info
        record = logging.LogRecord(
            name="test_logger",
            level=logging.ERROR,
            pathname=__file__,
            lineno=30,
            msg="Error occurred",
            args=(),
            exc_info=None  # We'll set it manually logic-wise but LogRecord captures it if passing exc_info=True usually
        )
        # Manually capture exc_info for the test
        import sys
        record.exc_info = sys.exc_info()
    
    formatted = formatter.format(record)
    data = json.loads(formatted)
    
    assert data["message"] == "Error occurred"
    assert "exception" in data
    assert "ValueError: Test error" in data["exception"]
