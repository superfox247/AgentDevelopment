"""Unit tests for base agent server.py entry point."""

import pytest

from agent_platform.test_utils import TestServerEntryPointBase


class TestServerEntryPoint(TestServerEntryPointBase):
    """Tests for server.py entry point."""

    agent_name = "base_agent"
