import argparse
import logging
import sys
from pathlib import Path

# Configure Logging
logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)

MODEL_TEMPLATE = """
class {name}(BaseModel):
    \"\"\"
    {description}
    
    Heuristics: {heuristics}
    Verification: {verification}
    \"\"\"
    # TODO: Define fields
    # field_name: str = Field(..., description="...")
    pass
"""


def define_domain_model(
    name: str, description: str, heuristics: str, verification: str
):
    """
    Adds a new Pydantic model to the protocol.py file with docstring injection
    for description, heuristics, and verification.
    """
    # Ensure TitleCase
    name = name[0].upper() + name[1:]

    protocol_path = Path("registry/models/protocol.py")
    if not protocol_path.exists():
        logger.error(f"Error: {protocol_path} not found.")
        sys.exit(1)

    content = protocol_path.read_text(encoding="utf-8")

    if f"class {name}" in content:
        logger.warning(f"Error: Model '{name}' already exists.")
        sys.exit(1)

    new_model = MODEL_TEMPLATE.format(
        name=name,
        description=description,
        heuristics=heuristics,
        verification=verification,
    )

    with open(protocol_path, "a") as f:
        f.write("\n" + new_model)

    logger.info(f"Success! Added model '{name}' to {protocol_path}.")
    logger.info("Next step: Edit the file to add fields.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Add a new Pydantic model to the protocol."
    )
    parser.add_argument("--name", required=True, help="Model name (TitleCase)")
    parser.add_argument("--description", required=True, help="Docstring description")
    parser.add_argument(
        "--heuristics",
        default="Use when defining strictly typed data.",
        help="Cognitive Policy",
    )
    parser.add_argument(
        "--verification", default="Pydantic validation.", help="Verification Logic"
    )

    args = parser.parse_args()

    define_domain_model(args.name, args.description, args.heuristics, args.verification)
