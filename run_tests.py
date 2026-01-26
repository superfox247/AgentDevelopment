#!/usr/bin/env python3
"""
Test Runner - Smart Test Execution with Early Exit on Failure

Runs tests in a smart order (fastest to slowest, most critical first)
and exits immediately on first failure to allow quick fix-retry cycles.

Usage:
    python run_tests.py [--agent AGENT_NAME] [--skip-evals] [--verbose]
"""

import argparse
import subprocess
import sys
from pathlib import Path
from typing import Optional


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
    print(f"{Colors.OKGREEN}✓{Colors.ENDC} {message}")


def print_failure(message: str) -> None:
    """Print a failure message."""
    print(f"{Colors.FAIL}✗{Colors.ENDC} {message}")


def run_command(
    cmd: list[str],
    description: str,
    cwd: Optional[Path] = None,
    verbose: bool = False,
) -> tuple[bool, str]:
    """Run a command and return success status and output."""
    try:
        if verbose:
            print(f"  Running: {' '.join(cmd)}")
        
        result = subprocess.run(
            cmd,
            cwd=cwd,
            capture_output=True,
            text=True,
            check=False,
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
    cwd: Optional[Path] = None,
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
        print(f"{Colors.FAIL}Test failed at step {step}/{total}: {description}{Colors.ENDC}")
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
    
    args = parser.parse_args()
    
    project_root = Path(__file__).parent
    steps: list[tuple[str, list[str], Optional[Path]]] = []
    
    print_header("Test Runner - Smart Test Execution")
    
    # Step 1: Verification (fastest, checks setup)
    if not args.skip_verification:
        steps.append((
            "Verification - Check setup and agent discovery",
            ["python", "test_verification.py"],
            project_root,
        ))
    
    # Step 2: Unit tests - Core utilities (fast, deterministic)
    steps.append((
        "Unit Tests - Agent Registry",
        ["uv", "run", "pytest", "dashboard_api/tests/test_agent_registry.py", "-v"],
        project_root,
    ))
    
    steps.append((
        "Unit Tests - Models",
        ["uv", "run", "pytest", "dashboard_api/tests/test_models.py", "-v"],
        project_root,
    ))
    
    # Step 3: API tests (medium speed)
    steps.append((
        "API Tests - Agent Endpoints",
        ["uv", "run", "pytest", "dashboard_api/tests/test_agents_router.py", "-v"],
        project_root,
    ))
    
    # Step 4: Integration tests (medium speed, uses real files)
    steps.append((
        "Integration Tests - Researcher Agent",
        ["uv", "run", "pytest", "dashboard_api/tests/test_researcher_integration.py", "-v"],
        project_root,
    ))
    
    # Step 5: Agent-specific tests
    if args.agent:
        agent_name = args.agent
        agent_tests_dir = project_root / "agents" / agent_name / "tests"
        
        if agent_tests_dir.exists():
            steps.append((
                f"Agent Tests - {agent_name}",
                ["uv", "run", "pytest", f"agents/{agent_name}/tests/", "-v"],
                project_root,
            ))
        else:
            print(f"{Colors.WARNING}Warning: No tests found for agent {agent_name}{Colors.ENDC}")
    else:
        # Run all agent tests
        agents_dir = project_root / "agents"
        if agents_dir.exists():
            for agent_dir in agents_dir.iterdir():
                if agent_dir.is_dir() and not agent_dir.name.startswith("."):
                    agent_tests_dir = agent_dir / "tests"
                    if agent_tests_dir.exists():
                        agent_name = agent_dir.name
                        steps.append((
                            f"Agent Tests - {agent_name}",
                            ["uv", "run", "pytest", f"agents/{agent_name}/tests/", "-v"],
                            project_root,
                        ))
    
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
                cmd = [
                    "uv", "run", "adk", "eval",
                    f"agents/{agent_name}",
                    str(eval_file),
                ]
                if config_file.exists():
                    cmd.extend(["--config_file_path", str(config_file)])
                cmd.append("--print_detailed_results")
                steps.append((
                    f"Evaluations - {agent_name}",
                    cmd,
                    project_root,
                ))

        if args.agent:
            agent_path = project_root / "agents" / args.agent
            if agent_path.exists() and agent_path.is_dir():
                _add_eval_steps([(args.agent, agent_path)])
        else:
            agents_dir = project_root / "agents"
            if agents_dir.exists():
                agents_to_eval = [
                    (d.name, d) for d in agents_dir.iterdir()
                    if d.is_dir() and not d.name.startswith(".")
                ]
                _add_eval_steps(agents_to_eval)
    
    # Run all steps
    total_steps = len(steps)
    
    for step_num, (description, cmd, cwd) in enumerate(steps, start=1):
        success = run_test_step(step_num, total_steps, description, cmd, cwd, args.verbose)
        
        if not success:
            return 1
    
    # All tests passed
    print_header("All Tests Passed!")
    print(f"{Colors.OKGREEN}{Colors.BOLD}✓ All {total_steps} test steps completed successfully!{Colors.ENDC}\n")
    print(f"{Colors.OKGREEN}Ready to commit.{Colors.ENDC}\n")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
