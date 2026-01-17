import argparse
import json
import logging
import os
from datetime import datetime, timezone
from pathlib import Path

# Configure Logging
logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)

METADATA_TEMPLATE = """{{
  "name": "{title}",
  "description": "{description}",
  "created_at": "{now}",
  "updated_at": "{now}",
  "sources": {sources}
}}"""

OVERVIEW_TEMPLATE = """# {title}

**Created**: {now}
**Description**: {description}

## Problem
[Describe the problem or context that triggered this Knowledge Item]

## Solution
[Describe the solution, pattern, or knowledge captured]

## Related KIs
- [Link to other KIs]
"""


def create_knowledge_item(title: str, description: str, sources: list[str]):
    # Normalize title to snake_case for directory
    topic_name = title.lower().replace(" ", "_").replace("-", "_")

    base_dir = Path(os.getcwd())
    ki_dir = base_dir / ".agent" / "knowledge" / topic_name
    artifacts_dir = ki_dir / "artifacts"

    # 1. Create Directories
    if ki_dir.exists():
        logger.warning(f"Warning: Knowledge Item '{topic_name}' already exists.")
    else:
        logger.info(f"Creating directory: {ki_dir}")
        artifacts_dir.mkdir(parents=True, exist_ok=True)

    # 2. Generate metadata.json
    now_iso = datetime.now(timezone.utc).isoformat()
    metadata_content = METADATA_TEMPLATE.format(
        title=title, description=description, now=now_iso, sources=json.dumps(sources)
    )

    metadata_path = ki_dir / "metadata.json"
    with open(metadata_path, "w") as f:
        f.write(metadata_content)
    logger.info(f"Created: {metadata_path}")

    # 3. Generate overview.md
    overview_path = artifacts_dir / "overview.md"
    if not overview_path.exists():
        overview_content = OVERVIEW_TEMPLATE.format(
            title=title, now=now_iso, description=description
        )
        with open(overview_path, "w") as f:
            f.write(overview_content)
        logger.info(f"Created: {overview_path}")

    logger.info(f"\\nSuccess! Knowledge Item '{topic_name}' created.")
    logger.info("Next step: Edit the artifacts in .agent/knowledge/")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create a new Knowledge Item.")
    parser.add_argument("--title", required=True, help="Human readable title")
    parser.add_argument("--description", required=True, help="One sentence summary")
    parser.add_argument(
        "--sources", nargs="*", default=[], help="List of source URLs or IDs"
    )

    args = parser.parse_args()

    create_knowledge_item(args.title, args.description, args.sources)
