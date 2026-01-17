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

    success = True

    # 1. Codespell
    logger.info("\n[1/3] Codespell...")
    if not run_command(["uv", "run", "codespell", "--write-changes" if fix else ""]):
        success = False

    # 2. Ruff
    logger.info("\n[2/3] Ruff (Linter & Formatter)...")
    if fix:
        if not run_command(["uv", "run", "ruff", "check", "--fix", "."]):
            success = False
        if not run_command(["uv", "run", "ruff", "format", "."]):
            success = False
    else:
        if not run_command(["uv", "run", "ruff", "check", "."]):
            success = False
        # Check formatting only
        if not run_command(["uv", "run", "ruff", "format", "--check", "."]):
            success = False

    # 3. Mypy
    logger.info("\n[3/3] Mypy (Type Checking)...")
    if not run_command(["uv", "run", "mypy", "."]):
        success = False

    if not success:
        logger.error("\n❌ Smart Lint Failed. See errors above.")
        sys.exit(1)
    else:
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
