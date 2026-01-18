import argparse
import logging
import subprocess
import sys

# Configure Logging
logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)


def run_command(command: list[str], ignore_error: bool = False) -> bool:
    try:
        logger.info(f"Running: {' '.join(command)}")
        subprocess.run(command, check=True)
        return True
    except subprocess.CalledProcessError:
        if not ignore_error:
            logger.error(f"❌ Command failed: {' '.join(command)}")
        return False


def smart_lint_action(fix: bool = False):
    logger.info("Running Smart Lint...")

    # 1. Codespell
    logger.info("\n[1/4] Codespell...")
    if not run_command(["uv", "run", "codespell", "--write-changes" if fix else ""]):
        logger.error("❌ Codespell failed.")
        sys.exit(1)

    # 2. Ruff
    logger.info("\n[2/4] Ruff (Linter & Formatter)...")
    if fix:
        if not run_command(["uv", "run", "ruff", "check", "--fix", "."]):
            logger.error("❌ Ruff check --fix failed.")
            sys.exit(1)
        if not run_command(["uv", "run", "ruff", "format", "."]):
            logger.error("❌ Ruff format failed.")
            sys.exit(1)
    else:
        if not run_command(["uv", "run", "ruff", "check", "."]):
            logger.error("❌ Ruff check failed.")
            sys.exit(1)
        # Check formatting only
        if not run_command(["uv", "run", "ruff", "format", "--check", "."]):
            logger.error("❌ Ruff formatting check failed.")
            sys.exit(1)

    # 3. Mypy
    logger.info("\n[3/4] Mypy (Type Checking)...")
    if not run_command(["uv", "run", "mypy", "."]):
        logger.error("❌ Mypy failed.")
        sys.exit(1)

    # 4. Deptry (Dependency Check)
    logger.info("\n[4/4] Deptry (Dependency Check)...")
    # Exclude certain rules if needed (customizable via pyproject.toml later)
    if not run_command(["uv", "run", "deptry", "."]):
        logger.error("❌ Deptry failed.")
        sys.exit(1)

    logger.info("\n✅ Smart Lint Passed!")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Runs smart linting (codespell, ruff, mypy)."
    )
    parser.add_argument(
        "--fix", action="store_true", help="Auto-fix issues where possible."
    )

    args = parser.parse_args()

    smart_lint_action(args.fix)
