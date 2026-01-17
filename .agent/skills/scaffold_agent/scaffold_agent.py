import argparse
import logging
import os
from pathlib import Path

# Configure Logging
logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)

AGENT_PY_TEMPLATE = """from pathlib import Path
from agent_platform.yaml_loader import load_agent_from_yaml

def create_app():
    return load_agent_from_yaml(str(Path(__file__).parent / "agent.yaml"))
"""

AGENT_YAML_TEMPLATE = """name: {name}
model: gemini-2.0-flash-exp
system_prompt: |
  You are the {name_title}.
  Your goal is... [TODO: Define Goal]
input_schema: registry.models.protocol.TODORequest
output_schema: registry.models.protocol.TODOResponse
tools: [] # Optional
#   - registry.tools.some_tool
"""


def scaffold_agent(
    agent_name: str, domain: str, role: str, heuristics: str, verification: str
):
    # Normalize names
    name = agent_name.lower().replace("-", "_").replace(" ", "_")
    domain = domain.lower().replace("-", "_").replace(" ", "_")

    # Paths
    base_dir = Path(os.getcwd())
    domain_dir = base_dir / "domains" / domain
    agent_dir = domain_dir / name

    logger.info(f"Scaffolding agent '{name}' in '{domain}'...")

    # 1. Ensure domain exists
    if not domain_dir.exists():
        logger.info(f"Creating domain directory: {domain_dir}")
        domain_dir.mkdir(parents=True, exist_ok=True)
        (domain_dir / "__init__.py").touch()

    # 2. Create agent directory
    if agent_dir.exists():
        logger.warning(f"Agent directory already exists: {agent_dir}")
    else:
        agent_dir.mkdir(parents=True)

    # 3. Create __init__.py
    (agent_dir / "__init__.py").touch()

    # 4. Create agent.yaml
    yaml_content = AGENT_YAML_TEMPLATE.format(
        name=agent_name, name_title=agent_name.replace("_", " ").title()
    )
    yaml_path = agent_dir / "agent.yaml"
    with open(yaml_path, "w") as f:
        f.write(yaml_content)
    logger.info(f"Created: {yaml_path}")

    # 3. Create instruction.md (Cognitive)
    instruction_path = agent_dir / "instruction.md"
    instruction_content = f"""# {agent_name} Instruction

## Role
{role}

## Cognitive Heuristics (When to run)
{heuristics}

## Verification (Success Criteria)
{verification}

## Core Logic
[Describe the step-by-step logic here]
"""
    with open(instruction_path, "w") as f:
        f.write(instruction_content)
    logger.info(f"Created: {instruction_path}")

    # 4. Create agent.py (Factory)
    agent_py_path = agent_dir / "agent.py"
    agent_py_content = AGENT_PY_TEMPLATE
    with open(agent_py_path, "w") as f:
        f.write(agent_py_content)
    logger.info(f"Created: {agent_py_path}")

    logger.info(f"\\nSuccess! Agent '{agent_name}' scaffolded in '{domain}'.")
    logger.info("Next steps:")
    logger.info("1. Edit agent.yaml to define tools.")
    logger.info("2. Edit instruction.md to refine logic.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Scaffold a new agent.")
    parser.add_argument("--name", required=True, help="Agent name (snake_case)")
    parser.add_argument("--domain", required=True, help="Domain name (snake_case)")
    parser.add_argument("--role", required=True, help="Agent role description")
    parser.add_argument(
        "--heuristics",
        default="TODO: Define when this agent should be called.",
        help="Cognitive Policy",
    )
    parser.add_argument(
        "--verification",
        default="TODO: Define how to verify this agent's output.",
        help="Verification Logic",
    )

    args = parser.parse_args()

    scaffold_agent(
        args.name, args.domain, args.role, args.heuristics, args.verification
    )
