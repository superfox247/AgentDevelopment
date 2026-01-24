"""
Model Configuration Verification.

Ensures that all agents defined in YAML are using valid, production-ready
model IDs by checking against the live Gemini API (when keys are available).
"""


import logging
import os
from pathlib import Path

import pytest
import yaml
from dotenv import load_dotenv
from google import genai

logger = logging.getLogger(__name__)

ROOT_DIR = Path(__file__).parent.parent.parent

@pytest.fixture(scope="module")
def valid_models() -> set[str]:
    """Fetches list of valid model names from Gemini API.

    Note: This test requires a real API key. We explicitly load from .env
    to override pytest.ini's fake-key setting.
    """
    # Load real API key from .env, overriding pytest.ini fake key
    env_file = ROOT_DIR / ".env"
    if env_file.exists():
        load_dotenv(env_file, override=True)

    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key or "fake" in api_key.lower():
        pytest.skip("Real GEMINI_API_KEY required for model validation tests")

    try:
        client = genai.Client(api_key=api_key)
        # Type ignore for external library untyped call if needed, but list() usually works
        models = list(client.models.list())
        valid_names = set()
        for m in models:
            if m.name:
                valid_names.add(m.name)
                valid_names.add(m.name.replace("models/", ""))
        return valid_names
    except Exception as e:
        pytest.skip(f"Failed to fetch models from API: {e}")

def get_agent_model_usage() -> list[dict[str, str]]:
    """Scans all agent.yaml files and extracts model usage."""
    agent_files = list(ROOT_DIR.rglob("agent.yaml"))
    results = []

    for yaml_file in agent_files:
        try:
            with open(yaml_file, encoding="utf-8") as f:
                data = yaml.safe_load(f)

            model = data.get("model")
            if model:
                results.append({
                    "file": str(yaml_file.relative_to(ROOT_DIR)),
                    "model": model,
                    "agent": data.get("name", "unknown")
                })
        except Exception as e:
            logger.warning(f"Failed to read {yaml_file}: {e}")

    return results

@pytest.mark.parametrize("usage", get_agent_model_usage())
def test_agent_model_validity(usage: dict[str, str], valid_models: set[str]) -> None:
    """Verifies that the model used by an agent is available in the API."""
    model = usage["model"]
    file_path = usage["file"]

    # Check if model is in the set of valid models
    assert model in valid_models, f"Agent '{usage['agent']}' in '{file_path}' uses invalid model '{model}'."
