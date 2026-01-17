import argparse
import logging
import os
from pathlib import Path

# Configure Logging
logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)

TEST_TEMPLATE = """import pytest
from unittest.mock import MagicMock
from google.adk.agents import InvocationContext
from domains.{domain}.{agent}.agent import {agent}

# Heuristics: {heuristics}
# Verification: {verification}

@pytest.fixture
    # Assert
    # assert result is not None
    assert True # Placeholder
"""


def scaffold_test(domain: str, agent: str, heuristics: str, verification: str):
    # Normalize
    agent = agent.lower().replace("-", "_").replace(" ", "_")
    domain = domain.lower().replace("-", "_").replace(" ", "_")

    base_dir = Path(os.getcwd())

    # Target directory: tests/unit/domains/[domain]/[agent]
    test_dir = base_dir / "tests" / "unit" / "domains" / domain / agent

    if not test_dir.exists():
        logger.info(f"Creating test directory: {test_dir}")
        test_dir.mkdir(parents=True, exist_ok=True)
        (test_dir / "__init__.py").touch()

    test_path = test_dir / "test_agent.py"

    if test_path.exists():
        logger.error(f"Error: Test file already exists: {test_path}")
        return

    # Generate content
    content = TEST_TEMPLATE.format(
        domain=domain, agent=agent, heuristics=heuristics, verification=verification
    )

    with open(test_path, "w") as f:
        f.write(content)

    logger.info(f"Success! Created unit tests at {test_path}")
    logger.info("Run with: uv run pytest")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Scaffold unit tests for an agent.")
    parser.add_argument("--domain", required=True, help="Domain name")
    parser.add_argument("--agent", required=True, help="Agent name")
    parser.add_argument(
        "--heuristics", default="Test typical user flows.", help="Cognitive Policy"
    )
    parser.add_argument(
        "--verification", default="Assert output state.", help="Verification Logic"
    )

    args = parser.parse_args()

    scaffold_test(args.domain, args.agent, args.heuristics, args.verification)
