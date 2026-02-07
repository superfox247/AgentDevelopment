"""Render help text from shared command catalog."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
CATALOG_PATH = REPO_ROOT / "scripts" / "command_catalog.json"
SEPARATOR = "=" * 78


def _load_catalog() -> dict[str, Any]:
    return json.loads(CATALOG_PATH.read_text(encoding="utf-8"))


def _usage_key(shell: str) -> str:
    if shell == "make":
        return "make_usage"
    if shell == "powershell":
        return "powershell_usage"
    raise ValueError(f"Unsupported shell: {shell}")


def render_help(shell: str) -> str:
    catalog = _load_catalog()
    usage_key = _usage_key(shell)

    entries: list[tuple[str, str]] = []
    for section in catalog["sections"]:
        for command in section["commands"]:
            usage = command.get(usage_key)
            if usage:
                entries.append((usage, command["description"]))

    width = min(max((len(usage) for usage, _ in entries), default=24) + 2, 78)

    lines = [SEPARATOR, catalog["title"], SEPARATOR, ""]
    for section in catalog["sections"]:
        section_entries = [
            (cmd[usage_key], cmd["description"])
            for cmd in section["commands"]
            if cmd.get(usage_key)
        ]
        if not section_entries:
            continue

        lines.append(f"{section['title']}:")
        for usage, description in section_entries:
            if len(usage) >= width:
                lines.append(f"  {usage}  {description}")
            else:
                lines.append(f"  {usage:<{width}}{description}")
        lines.append("")

    lines.append(SEPARATOR)
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Render command help text.")
    parser.add_argument(
        "--shell",
        choices=["make", "powershell"],
        required=True,
        help="Shell flavor to render help for.",
    )
    args = parser.parse_args()

    print(render_help(shell=args.shell))
    return 0


if __name__ == "__main__":
    sys.exit(main())
