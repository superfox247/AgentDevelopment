import argparse
import logging
import os
import sys
from pathlib import Path

# Configure Logging
logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)


def check_models_availability():
    """Checks for Google GenAI Model Access."""
    logger.info("Checking Model Availability...")

    # Check for API Key
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        # Check .env if not in env
        env_path = Path(".env")
        if env_path.exists():
            with open(env_path) as f:
                for line in f:
                    if line.startswith("GOOGLE_API_KEY="):
                        api_key = line.strip().split("=", 1)[1]
                        os.environ["GOOGLE_API_KEY"] = api_key
                        break

    if not api_key:
        logger.error("❌ GOOGLE_API_KEY not found in environment or .env.")
        return

    try:
        from google import genai

        client = genai.Client(api_key=api_key)

        # We can try to list models or just get a specific one
        # Let's try listing first
        logger.info("  - Connecting to Vertex AI / Gemini API...")
        try:
            # Just a simple list to verify connectivity
            # list() might be an iterator
            pager = client.models.list()
            count = 0
            for m in pager:
                count += 1
                if count > 5:
                    break  # just prove it works
            logger.info("  - ✅ Connected successfully. Models are listable.")

            # Specific checks
            targets = ["gemini-2.0-flash-exp", "imagen-3.0-generate-001"]
            for t in targets:
                try:
                    client.models.get(model=t)
                    logger.info(f"  - ✅ Access confirmed: {t}")
                except Exception:
                    logger.warning(f"  - ⚠️  Could not verified access to: {t}")

        except Exception as e:
            logger.error(f"❌ Connection failed: {e}")

    except ImportError:
        logger.error("❌ google-genai library not installed. Run `uv sync`.")


def debug_system_action(target: str):
    logger.info(f"Running System Debugger (Target: {target})...\n")

    if target == "models":
        check_models_availability()
    elif target == "all":
        check_models_availability()
        # TODO: Add connectivity checks for Docker services
    else:
        logger.error(f"Unknown target: {target}")
        sys.exit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Debugs system components.")
    parser.add_argument(
        "--target", default="all", choices=["models", "all"], help="Debug target"
    )

    args = parser.parse_args()
    debug_system_action(args.target)
