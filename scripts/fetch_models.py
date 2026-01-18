import logging
import os
from pathlib import Path
from google import genai
from agent_platform.config import PlatformConfig

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

ROOT_DIR = Path(__file__).parent.parent
DOCS_DIR = ROOT_DIR / "docs"
CATALOGUE_FILE = DOCS_DIR / "available_models.md"

def main():
    logger.info("Fetching available models from Gemini API...")
    try:
        config = PlatformConfig()
        client = genai.Client(api_key=config.gemini_api_key)
        
        # List all models
        models = list(client.models.list())
        
        # Filter/Sort?
        # Let's just dump them all for inspection
        
        print(f"Found {len(models)} models.")
        
        DOCS_DIR.mkdir(parents=True, exist_ok=True)
        
        with open(CATALOGUE_FILE, "w", encoding="utf-8") as f:
            f.write("# Available Models Catalogue\n\n")
            f.write(f"Generated from Gemini API on {os.environ.get('USERNAME', 'User')}'s system.\n\n")
            f.write("| Model Name | Display Name | Capabilities |\n")
            f.write("|Dict Keys | Description | |\n")
            f.write("|---|---|---|\n")
            
            for m in models:
                # GenAI SDK model object structure depends on version, accessing attributes safely
                name = getattr(m, 'name', 'N/A')
                display_name = getattr(m, 'display_name', 'N/A')
                
                # Try to determine capabilities if possible, or just list supported methods
                supported = getattr(m, 'supported_generation_methods', [])
                
                f.write(f"| `{name}` | {display_name} | {supported} |\n")
        
        logger.info(f"Catalogue saved to {CATALOGUE_FILE}")
        
    except Exception as e:
        logger.error(f"Failed to fetch models: {e}")
        raise

if __name__ == "__main__":
    main()
