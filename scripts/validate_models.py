
import os
import yaml
import logging
from pathlib import Path
from google import genai
from agent_platform.config import PlatformConfig

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

ROOT_DIR = Path(__file__).parent.parent

def get_valid_models():
    """Fetches list of valid model names from Gemini API."""
    try:
        config = PlatformConfig()
        client = genai.Client(api_key=config.gemini_api_key)
        # We want models that support generateContent
        models = list(client.models.list())
        valid_names = set()
        for m in models:
            # The API returns 'models/gemini-1.5-flash', but users often write 'gemini-1.5-flash'
            # We should support both formats for validation
            if m.name:
                valid_names.add(m.name)
                valid_names.add(m.name.replace("models/", ""))
        return valid_names
    except Exception as e:
        logger.error(f"Failed to fetch models from API: {e}")
        return set()

def scan_agent_yamls():
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
                    "file": yaml_file.relative_to(ROOT_DIR),
                    "model": model,
                    "agent": data.get("name", "unknown")
                })
        except Exception as e:
            logger.warning(f"Failed to read {yaml_file}: {e}")
            
    return results

def main():
    logger.info("Fetching valid models from Gemini API...")
    valid_models = get_valid_models()
    
    if not valid_models:
        logger.error("Could not fetch valid models. Aborting validation.")
        return

    logger.info(f"Found {len(valid_models)} valid models.")
    
    logger.info("Scanning agent configurations...")
    agent_usages = scan_agent_yamls()
    
    issues_found = 0
    
    print("\n--- Model Validation Report ---\n")
    
    for usage in agent_usages:
        model = usage["model"]
        is_valid = model in valid_models
        
        status = "✅ PASSED" if is_valid else "❌ FAILED"
        print(f"{status} | Agent: {usage['agent']:<20} | Model: {model:<20} | File: {usage['file']}")
        
        if not is_valid:
            issues_found += 1
            # Suggest closest match? (Optional optimization)
            
    print("\n-------------------------------")
    if issues_found > 0:
        print(f"\nFound {issues_found} invalid model configurations.")
        exit(1)
    else:
        print("\nAll agent model configurations are valid.")
        exit(0)

if __name__ == "__main__":
    main()
