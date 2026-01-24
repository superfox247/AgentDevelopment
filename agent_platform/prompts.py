import logging
from pathlib import Path

"""
Prompt loading and registry management.

Handles reading agent instructions from the centralized prompt registry
(.agent/prompts directory).
"""

logger = logging.getLogger(__name__)

# Assumes registry is at repository root.
# From platform/prompts.py -> ../.agent/prompts
ROOT_DIR = Path(__file__).parent.parent
REGISTRY_DIR = ROOT_DIR / ".agent" / "prompts"


def load_instruction(agent_name: str) -> str:
    """
    Loads the system instruction for an agent from the registry.

    Args:
        agent_name: The name of the agent (matches filename in registry).

    Returns:
        str: The content of the instruction file, or empty string if not found.
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
