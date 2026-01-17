import argparse
import logging
import os
import re
import sys
from pathlib import Path

import requests

# Configure Logging
logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)

# Patterns to hunt for
SECRET_PATTERNS = {
    "API Key": r"(api_key|apikey|secret|token)\s*=\s*['\"][a-zA-Z0-9_\-]{20,}['\"]",
    "Bearer Token": r"Bearer\s+[a-zA-Z0-9\-\._~+/]+=*",
    "Password": r"password\s*=\s*['\"][^'\"]{1,}['\"]",
    "AWS Key": r"AKIA[0-9A-Z]{16}",
}


def check_file_for_secrets(file_path: Path) -> list[str]:
    """Scans a single file for regex matches."""
    violations = []
    try:
        content = file_path.read_text(encoding="utf-8")
        lines = content.splitlines()

        for i, line in enumerate(lines, 1):
            line_str = line.strip()

            for name, pattern in SECRET_PATTERNS.items():
                if re.search(pattern, line_str, re.IGNORECASE):
                    violations.append(f"[{name}] {file_path}:{i}")

    except Exception:
        pass

    return violations


def check_env_gap(base_dir: Path) -> list[str]:
    """Checks if .env keys are missing from .env.example"""
    violations = []
    env_path = base_dir / ".env"
    example_path = base_dir / ".env.example"

    if not env_path.exists():
        return ["[Env Missing] .env file not found."]
    if not example_path.exists():
        return ["[Env Missing] .env.example file not found."]

    try:
        # Simple parser avoiding comments and empty lines
        env_keys = {
            line.split("=")[0].strip()
            for line in env_path.read_text().splitlines()
            if "=" in line and not line.strip().startswith("#")
        }
        example_keys = {
            line.split("=")[0].strip()
            for line in example_path.read_text().splitlines()
            if "=" in line and not line.strip().startswith("#")
        }

        missing = env_keys - example_keys
        if missing:
            violations.append(
                f"[Env Gap] Keys in .env but missing in .env.example: {', '.join(missing)}"
            )

    except Exception as e:
        logger.warning(f"Env check failed: {e}")
        pass

    return violations


def check_pypi_package(package: str) -> list[str]:
    """Checks PyPI for package existence and basic metadata."""
    violations = []
    url = f"https://pypi.org/pypi/{package}/json"
    try:
        resp = requests.get(url, timeout=3)
        if resp.status_code == 200:
            data = resp.json()
            # Just log info, don't fail unless requested?
            # For audit, maybe we just want to ensure it EXISTS?
            # actually the original script just printed info.
            # We'll treat this as 'Info' logging mostly, ensuring connectivity.
            logger.info(f"   - {package}: {data['info']['version']}")
        else:
            violations.append(
                f"[Dependency Warning] Package {package} not found on PyPI"
            )
    except Exception as e:
        logger.warning(f"   - {package}: Check failed ({e})")
        # Don't fail the audit for connectivity issues usually
    return violations


def audit_security_action(check_deps: bool = False):
    logger.info("Running Unified Security & Health Audit...\n")
    all_violations = []

    base_dir = Path(os.getcwd())

    # 1. Env Gap Analysis
    logger.info("1. Checking Environment Consistency...")
    all_violations.extend(check_env_gap(base_dir))

    # 2. Secret Scanning
    logger.info("2. Scanning for Secrets (Regex)...")
    for root, dirs, files in os.walk(base_dir):
        dirs[:] = [
            d
            for d in dirs
            if d
            not in {
                ".venv",
                ".git",
                "__pycache__",
                "node_modules",
                "site-packages",
                ".idea",
                ".vscode",
            }
        ]
        for file in files:
            if file.endswith((".png", ".jpg", ".pyc", ".exe", ".dll")):
                continue
            file_path = Path(root) / file
            if file_path.name == ".env":
                continue
            all_violations.extend(check_file_for_secrets(file_path))

    # 3. Dependency Check (Optional/Light)
    if check_deps:
        logger.info("3. Checking Key Dependencies (PyPI)...")
        # Check core deps
        deps = ["google-adk", "a2a-sdk"]
        for dep in deps:
            all_violations.extend(check_pypi_package(dep))

    logger.info("\n" + "=" * 30)
    if all_violations:
        logger.error(f"❌ AUDIT FAILED: {len(all_violations)} risks/issues found.")
        for v in all_violations:
            logger.error(v)
        sys.exit(1)
    else:
        logger.info("✅ AUDIT PASSED: System Clean.")
        sys.exit(0)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Scans codebase for security risks, env parity, and dependency health."
    )
    parser.add_argument(
        "--check-deps", action="store_true", help="Perform online dependency checks"
    )
    args = parser.parse_args()

    audit_security_action(args.check_deps)
