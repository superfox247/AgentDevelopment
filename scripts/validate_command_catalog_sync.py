"""Validate command catalog and wrapper parity across Makefile and make.ps1."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
CATALOG_PATH = REPO_ROOT / "scripts" / "command_catalog.json"
MAKEFILE_PATH = REPO_ROOT / "Makefile"
POWERSHELL_PATH = REPO_ROOT / "make.ps1"


def _load_catalog() -> dict[str, Any]:
    return json.loads(CATALOG_PATH.read_text(encoding="utf-8"))


def _catalog_targets(catalog: dict[str, Any], usage_key: str) -> set[str]:
    targets: set[str] = set()
    for section in catalog["sections"]:
        for command in section["commands"]:
            if command.get(usage_key):
                targets.add(command["id"])
    return targets


def _parse_make_phony_targets() -> set[str]:
    lines = MAKEFILE_PATH.read_text(encoding="utf-8").splitlines()
    parts: list[str] = []
    collecting = False

    for line in lines:
        stripped = line.strip()
        if stripped.startswith(".PHONY:"):
            collecting = True
            stripped = stripped.split(":", 1)[1].strip()
        elif not collecting:
            continue

        if not stripped:
            continue

        continue_collecting = stripped.endswith("\\")
        if continue_collecting:
            stripped = stripped[:-1].strip()

        if stripped:
            parts.extend(stripped.split())

        if collecting and not continue_collecting:
            break

    return set(parts)


def _parse_powershell_targets() -> set[str]:
    text = POWERSHELL_PATH.read_text(encoding="utf-8")
    matches = re.findall(r'^\s*"([^"]+)"\s*=\s*\{', text, flags=re.MULTILINE)
    return set(matches)


def _check_missing(expected: set[str], actual: set[str], label: str) -> list[str]:
    missing = sorted(expected - actual)
    if not missing:
        return []
    return [f"{label} is missing targets: {', '.join(missing)}"]


def main() -> int:
    catalog = _load_catalog()
    expected_make = _catalog_targets(catalog, "make_usage")
    expected_ps = _catalog_targets(catalog, "powershell_usage")

    make_targets = _parse_make_phony_targets()
    ps_targets = _parse_powershell_targets()

    errors: list[str] = []
    errors.extend(_check_missing(expected_make, make_targets, "Makefile .PHONY"))
    errors.extend(_check_missing(expected_ps, ps_targets, "make.ps1 target map"))

    if errors:
        print("Command catalog sync check failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    print("Command catalog sync check passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
