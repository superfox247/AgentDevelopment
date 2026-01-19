
import pytest
import yaml
import logging
from pathlib import Path
from google import genai
from agent_platform.config import PlatformConfig

logger = logging.getLogger(__name__)

ROOT_DIR = Path(__file__).parent.parent.parent

@pytest.fixture(scope="module")
def valid_models():
    """Fetches list of valid model names from Gemini API."""
    try:
        config = PlatformConfig()
        client = genai.Client(api_key=config.gemini_api_key)
        # We want models that support generateContent
        models = list(client.models.list())
        valid_names = set()
        for m in models:
            if m.name:
                valid_names.add(m.name)
                valid_names.add(m.name.replace("models/", ""))
        return valid_names
    except Exception as e:
        pytest.skip(f"Failed to fetch models from API (API Key missing?): {e}")

def get_agent_model_usage():
    """Scans all agent.yaml files and extracts model usage."""
    agent_files = list(ROOT_DIR.rglob("agent.yaml"))
    results = []
    
    for yaml_file in agent_files:
        try:
            with open(yaml_file, "r", encoding="utf-8") as f:
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
def test_agent_model_validity(usage, valid_models):
    """Verifies that the model used by an agent is available in the API."""
    model = usage["model"]
    file_path = usage["file"]
    
    # Check if model is in the set of valid models
    assert model in valid_models, f"Agent '{usage['agent']}' in '{file_path}' uses invalid model '{model}'."
