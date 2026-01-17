import argparse
import logging
import os
from pathlib import Path

# Configure Logging
logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)

SKILL_MD_TEMPLATE = """---
name: {name_title}
description: {description}
---

# {name_title}

{description}

## 1. Cognitive Heuristics (Policy)
**When to use this skill:**
{heuristics}

## 2. Load Context
- `.agent/skills/{name}/{name}.py`: The automation script.

## 3. Usage (Automated)

Run the script:
```bash
uv run .agent/skills/{name}/{name}.py --help
```

## 4. Verification Logic (Self-Correction)
**How to verify success:**
{verification}

## 5. Implementation Steps (Manual Fallback)
If the script fails, follow the logic in `.agent/skills/{name}/{name}.py`.
"""

SCRIPT_TEMPLATE = """import argparse
import logging
import sys

# Configure Logging
logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)

def {name}_action():
    logger.info("Action '{name}' is not yet implemented.")
    # TODO: Implement logic here (Schema-First)

    # Validation Logic
    # if not verified:
    #     logger.error("Verification failed.")
    #     sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="{description}")
    
    args = parser.parse_args()
    
    {name}_action()
"""

TEST_TEMPLATE = """import pytest
from pathlib import Path
import subprocess

def test_{name}_script_exists():
    script_path = Path(__file__).parent.parent / "{name}.py"
    assert script_path.exists()

def test_{name}_help():
    script_path = Path(__file__).parent.parent / "{name}.py"
    result = subprocess.run(
        ["uv", "run", str(script_path), "--help"],
        capture_output=True,
        text=True
    )
    assert result.returncode == 0
"""


def create_skill(name: str, description: str, heuristics: str, verification: str):
    # Normalize
    name = name.lower().replace("-", "_").replace(" ", "_")
    name_title = name.replace("_", " ").title()

    base_dir = Path(os.getcwd())
    skills_dir = base_dir / ".agent" / "skills" / name

    # 1. Create Skill Directory
    if not skills_dir.exists():
        logger.info(f"Creating skill directory: {skills_dir}")
        skills_dir.mkdir(parents=True, exist_ok=True)

    # 2. Create SKILL.md
    skill_md_path = skills_dir / "SKILL.md"
    if not skill_md_path.exists():
        content = SKILL_MD_TEMPLATE.format(
            name=name,
            name_title=name_title,
            description=description,
            heuristics=heuristics,
            verification=verification,
        )
        with open(skill_md_path, "w") as f:
            f.write(content)
        logger.info(f"Created: {skill_md_path}")
    else:
        logger.info(f"Skipped: {skill_md_path} already exists.")

    # 3. Create Script (Self-Contained)
    script_path = skills_dir / f"{name}.py"
    if not script_path.exists():
        content = SCRIPT_TEMPLATE.format(name=name, description=description)
        with open(script_path, "w") as f:
            f.write(content)
        logger.info(f"Created: {script_path}")
    else:
        logger.info(f"Skipped: {script_path} already exists.")

    # 4. Create Tests
    test_dir = skills_dir / "tests"
    test_dir.mkdir(exist_ok=True)
    (test_dir / "__init__.py").touch()

    test_path = test_dir / f"test_{name}.py"
    if not test_path.exists():
        content = TEST_TEMPLATE.format(name=name)
        with open(test_path, "w") as f:
            f.write(content)
        logger.info(f"Created: {test_path}")

    logger.info(f"\\nSuccess! Cognitive Skill '{name}' created at {skills_dir}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Scaffold a new cognitive skill.")
    parser.add_argument("--name", required=True, help="Skill name (snake_case)")
    parser.add_argument("--description", required=True, help="Short description")
    parser.add_argument(
        "--heuristics",
        default="TODO: Define when to use this skill.",
        help="Cognitive policy (when to use)",
    )
    parser.add_argument(
        "--verification",
        default="TODO: Define success criteria.",
        help="Verification logic",
    )

    args = parser.parse_args()

    create_skill(args.name, args.description, args.heuristics, args.verification)
