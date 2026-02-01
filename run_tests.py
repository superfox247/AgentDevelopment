#!/usr/bin/env python3
"""
Test Runner - Smart Test Execution with Early Exit on Failure

Runs tests in a smart order (fastest to slowest, most critical first)
and exits immediately on first failure to allow quick fix-retry cycles.

Usage:
    python run_tests.py [--agent AGENT_NAME] [--skip-evals] [--verbose]
"""

import argparse
import os
import platform
import subprocess
import sys
from pathlib import Path


class Colors:
    """ANSI color codes for terminal output."""

    HEADER = "\033[95m"
    OKBLUE = "\033[94m"
    OKCYAN = "\033[96m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"


def print_header(text: str) -> None:
    """Print a formatted header."""
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'=' * 70}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{text:^70}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'=' * 70}{Colors.ENDC}\n")


def print_step(step: int, total: int, description: str) -> None:
    """Print a test step."""
    print(f"{Colors.OKCYAN}[{step}/{total}]{Colors.ENDC} {description}...")


def print_success(message: str) -> None:
    """Print a success message."""
    try:
        print(f"{Colors.OKGREEN}✓{Colors.ENDC} {message}")
    except UnicodeEncodeError:
        print(f"{Colors.OKGREEN}[OK]{Colors.ENDC} {message}")


def print_failure(message: str) -> None:
    """Print a failure message."""
    try:
        print(f"{Colors.FAIL}✗{Colors.ENDC} {message}")
    except UnicodeEncodeError:
        print(f"{Colors.FAIL}[FAIL]{Colors.ENDC} {message}")


def get_python_executable(project_root: Path) -> str:
    """Get the Python executable to use for running tests."""
    # Try .venv first (most reliable)
    if platform.system() == "Windows":
        venv_python = project_root / ".venv" / "Scripts" / "python.exe"
    else:
        venv_python = project_root / ".venv" / "bin" / "python"

    if venv_python.exists():
        return str(venv_python)

    # Fallback to system Python
    return sys.executable


def get_pytest_command(project_root: Path, test_path: str) -> list[str]:
    """Get the command to run pytest, using venv Python if available."""
    python_exe = get_python_executable(project_root)
    return [python_exe, "-m", "pytest", test_path, "-v"]


def get_adk_command(project_root: Path, args: list[str]) -> list[str]:
    """Get the command to run adk, using venv Python if available."""
    python_exe = get_python_executable(project_root)
    return [python_exe, "-m", "adk", *args]


def run_command(
    cmd: list[str],
    description: str,
    cwd: Path | None = None,
    verbose: bool = False,
) -> tuple[bool, str]:
    """Run a command and return success status and output."""
    try:
        if verbose:
            print(f"  Running: {' '.join(cmd)}")

        # Set environment to UTF-8 for Windows
        env = os.environ.copy()
        if platform.system() == "Windows":
            env["PYTHONIOENCODING"] = "utf-8"

        result = subprocess.run(
            cmd,
            cwd=cwd,
            capture_output=True,
            text=True,
            check=False,
            env=env,
        )

        output = result.stdout + result.stderr

        if result.returncode == 0:
            return True, output
        else:
            return False, output
    except Exception as e:
        return False, str(e)


def run_test_step(
    step: int,
    total: int,
    description: str,
    cmd: list[str],
    cwd: Path | None = None,
    verbose: bool = False,
) -> bool:
    """Run a test step and exit on failure."""
    print_step(step, total, description)

    success, output = run_command(cmd, description, cwd=cwd, verbose=verbose)

    if success:
        print_success(description)
        if verbose and output:
            print(output)
        return True
    else:
        print_failure(description)
        print(f"\n{Colors.FAIL}Error output:{Colors.ENDC}")
        print(output)
        print(f"\n{Colors.FAIL}{'=' * 70}{Colors.ENDC}")
        print(
            f"{Colors.FAIL}Test failed at step {step}/{total}: {description}{Colors.ENDC}"
        )
        print(f"{Colors.FAIL}Fix the issue and run again.{Colors.ENDC}")
        print(f"{Colors.FAIL}{'=' * 70}{Colors.ENDC}\n")
        return False


def main() -> int:
    """Main test runner."""
    parser = argparse.ArgumentParser(
        description="Run tests in smart order with early exit on failure"
    )
    parser.add_argument(
        "--agent",
        type=str,
        help="Run tests for a specific agent (e.g., researcher_agent)",
    )
    parser.add_argument(
        "--skip-evals",
        action="store_true",
        help="Skip evaluation tests (requires API keys)",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Show verbose output",
    )
    parser.add_argument(
        "--skip-verification",
        action="store_true",
        help="Skip verification script",
    )
    parser.add_argument(
        "--skip-frontend",
        action="store_true",
        help="Skip frontend tests",
    )

    args = parser.parse_args()

    project_root = Path(__file__).parent
    steps: list[tuple[str, list[str], Path | None]] = []

    print_header("Test Runner - Smart Test Execution")

    # Step 1: Verification (fastest, checks setup)
    if not args.skip_verification:
        steps.append(
            (
                "Verification - Check setup and agent discovery",
                ["python", "test_verification.py"],
                project_root,
            )
        )

    # Step 2: Unit tests - Core utilities (fast, deterministic)
    steps.append(
        (
            "Unit Tests - Agent Registry",
            get_pytest_command(
                project_root, "dashboard_api/tests/test_agent_registry.py"
            ),
            project_root,
        )
    )

    steps.append(
        (
            "Unit Tests - Models",
            get_pytest_command(project_root, "dashboard_api/tests/test_models.py"),
            project_root,
        )
    )

    # Step 3: API tests (medium speed)
    steps.append(
        (
            "API Tests - Agent Endpoints",
            get_pytest_command(
                project_root, "dashboard_api/tests/test_agents_router.py"
            ),
            project_root,
        )
    )

    # Step 4: Integration tests (medium speed, uses real files)
    steps.append(
        (
            "Integration Tests - Researcher Agent",
            get_pytest_command(
                project_root, "dashboard_api/tests/test_researcher_integration.py"
            ),
            project_root,
        )
    )

    # Step 4.5: Frontend tests (if not skipped)
    if not args.skip_frontend:
        frontend_dir = project_root / "frontend"
        if frontend_dir.exists():
            # Check if pnpm is available
            pnpm_cmd = "pnpm" if platform.system() != "Windows" else "pnpm.cmd"
            steps.append(
                (
                    "Frontend Tests - Component Tests",
                    [pnpm_cmd, "test", "run"],
                    frontend_dir,
                )
            )

    # Step 5: Agent-specific tests
    if args.agent:
        agent_name = args.agent
        agent_tests_dir = project_root / "agents" / agent_name / "tests"

        if agent_tests_dir.exists():
            steps.append(
                (
                    f"Agent Tests - {agent_name}",
                    get_pytest_command(project_root, f"agents/{agent_name}/tests/"),
                    project_root,
                )
            )
        else:
            print(
                f"{Colors.WARNING}Warning: No tests found for agent {agent_name}{Colors.ENDC}"
            )
    else:
        # Run all agent tests
        agents_dir = project_root / "agents"
        if agents_dir.exists():
            for agent_dir in agents_dir.iterdir():
                if agent_dir.is_dir() and not agent_dir.name.startswith("."):
                    agent_tests_dir = agent_dir / "tests"
                    if agent_tests_dir.exists():
                        agent_name = agent_dir.name
                        steps.append(
                            (
                                f"Agent Tests - {agent_name}",
                                get_pytest_command(
                                    project_root, f"agents/{agent_name}/tests/"
                                ),
                                project_root,
                            )
                        )

    # Step 6: Evaluations (slow, requires API keys)
    if not args.skip_evals:

        def _add_eval_steps(agents_to_eval: list[tuple[str, Path]]) -> None:
            for agent_name, agent_path in agents_to_eval:
                evals_dir = agent_path / "evaluations"
                if not evals_dir.exists():
                    continue
                eval_files = sorted(evals_dir.glob("*.test.json"))
                if not eval_files:
                    continue
                eval_file = eval_files[0]
                config_file = evals_dir / "test_config.json"
                cmd_args = [
                    "eval",
                    f"agents/{agent_name}",
                    str(eval_file),
                ]
                if config_file.exists():
                    cmd_args.extend(["--config_file_path", str(config_file)])
                cmd_args.append("--print_detailed_results")
                cmd = get_adk_command(project_root, cmd_args)
                steps.append(
                    (
                        f"Evaluations - {agent_name}",
                        cmd,
                        project_root,
                    )
                )

        if args.agent:
            agent_path = project_root / "agents" / args.agent
            if agent_path.exists() and agent_path.is_dir():
                _add_eval_steps([(args.agent, agent_path)])
        else:
            agents_dir = project_root / "agents"
            if agents_dir.exists():
                agents_to_eval = [
                    (d.name, d)
                    for d in agents_dir.iterdir()
                    if d.is_dir() and not d.name.startswith(".")
                ]
                _add_eval_steps(agents_to_eval)

    # Run all steps
    total_steps = len(steps)
    failed_steps = []

    for step_num, (description, cmd, cwd) in enumerate(steps, start=1):
        success = run_test_step(
            step_num, total_steps, description, cmd, cwd, args.verbose
        )

        if not success:
            failed_steps.append((step_num, description))
            # Continue running all tests instead of exiting early

    # Print summary
    if failed_steps:
        print_header("Test Summary")
        print(
            f"{Colors.FAIL}{Colors.BOLD}✗ {len(failed_steps)}/{total_steps} test steps failed:{Colors.ENDC}"
        )
        for step_num, description in failed_steps:
            print(f"  {Colors.FAIL}[{step_num}] {description}{Colors.ENDC}")
        print(
            f"\n{Colors.OKGREEN}✓ {total_steps - len(failed_steps)}/{total_steps} test steps passed{Colors.ENDC}\n"
        )
        return 1
    else:
        # All tests passed
        print_header("All Tests Passed!")
        try:
            print(
                f"{Colors.OKGREEN}{Colors.BOLD}✓ All {total_steps} test steps completed successfully!{Colors.ENDC}\n"
            )
        except UnicodeEncodeError:
            print(
                f"{Colors.OKGREEN}{Colors.BOLD}[OK] All {total_steps} test steps completed successfully!{Colors.ENDC}\n"
            )
        print(f"{Colors.OKGREEN}Ready to commit.{Colors.ENDC}\n")
        return 0


if __name__ == "__main__":
    sys.exit(main())
