import logging
from pathlib import Path

from schemas.prompts.basic_prompts import BASIC_SYSTEM_PROMPT

logger = logging.getLogger(__name__)

# Assumes registry is at repository root.
# From platform/prompts.py -> ../.agent/prompts
ROOT_DIR = Path(__file__).parent.parent
REGISTRY_DIR = ROOT_DIR / ".agent" / "prompts"


def load_instruction(agent_name: str) -> str:
    """
    Loads the system instruction for an agent from the registry.
    Expects a file named `{agent_name}.md` in `.agent/prompts/`.
    """
    prompt_path = REGISTRY_DIR / f"{agent_name}.md"

    try:
        if not prompt_path.exists():
            logger.warning(
                f"Prompt content not found for {agent_name} at {prompt_path}. Using empty string."
            )
            return ""

        return prompt_path.read_text(encoding="utf-8").strip()
    except Exception as e:
        logger.error(f"Failed to load prompt for {agent_name}: {e}")
        return ""
