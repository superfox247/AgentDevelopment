"""
Unit tests for Platform Configuration.
"""

import os
from unittest.mock import patch

from agent_platform.config import PlatformConfig, get_config


def test_config_defaults() -> None:
    """Verify default configuration values."""
    config = PlatformConfig()
    assert config.default_model == "models/gemini-2.0-flash"
    assert config.phoenix_collector_endpoint == "http://phoenix:6006/v1/traces"
    # pytest.ini sets GEMINI_API_KEY=fake-key-from-pytest-ini
    assert config.gemini_api_key == "fake-key-from-pytest-ini"


def test_config_env_override() -> None:
    """Verify that environment variables override defaults."""
    with patch.dict(
        os.environ,
        {
            "GEMINI_API_KEY": "test-key",
            "PHOENIX_COLLECTOR_ENDPOINT": "http://localhost:9999",
        },
    ):
        # Must reload or re-instantiate because BaseSettings loads on init
        config = PlatformConfig()
        assert config.gemini_api_key == "test-key"
        assert config.phoenix_collector_endpoint == "http://localhost:9999"


def test_get_config_singleton() -> None:
    """Verify get_config returns a PlatformConfig instance."""
    config = get_config()
    assert isinstance(config, PlatformConfig)
