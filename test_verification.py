#!/usr/bin/env python3
"""
Test Verification Script

Verifies the current test setup, baseline (base_agent), and researcher agent.
Run this to check that everything is working before making improvements.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from dashboard_api.utils.agent_registry import AgentRegistry

# Baseline and production agents we expect to be discoverable
REQUIRED_AGENTS = [
    ("base_agent", "Baseline", "Baseline agent for testing"),
    ("researcher_agent", "Research assistant", "browses"),
]


def _check_agent_metadata(
    meta: object, expected_name: str, desc_substr: str
) -> list[tuple[str, object, object]]:
    """Build metadata checks for an agent. meta has name, description, model, has_server, path."""
    m = meta
    path = getattr(m, "path", None)
    path_ok = path.exists() if path is not None else False
    return [
        ("name", getattr(m, "name", None), expected_name),
        ("description", getattr(m, "description", None), desc_substr),
        ("has_server", getattr(m, "has_server", None), True),
        ("path exists", path_ok, True),
    ]


def verify_agents() -> tuple[bool, list[str]]:
    """Verify base_agent (baseline) and researcher_agent are discoverable with correct metadata."""
    errors = []
    success = True

    print("=" * 60)
    print("1. Verifying Agent Discovery (base_agent + researcher_agent)")
    print("=" * 60)

    try:
        agents_dir = project_root / "agents"
        registry = AgentRegistry(agents_dir)
        agents = registry.get_agents(refresh=True)

        if not agents:
            errors.append("No agents discovered")
            success = False
            print("[FAIL] No agents found")
            return success, errors

        print(f"[PASS] Found {len(agents)} agent(s)")

        for expected_name, _label, desc_substr in REQUIRED_AGENTS:
            agent_meta = registry.get_agent(expected_name)
            if not agent_meta:
                errors.append(f"{expected_name} not found")
                success = False
                print(f"   [FAIL] {expected_name} not discovered")
                continue

            print(f"   - {expected_name}: OK")

            checks = _check_agent_metadata(agent_meta, expected_name, desc_substr)
            for check_name, actual, expected in checks:
                if isinstance(expected, bool):
                    match = actual == expected
                elif isinstance(expected, str):
                    match = expected in str(actual) if actual else False
                else:
                    match = actual == expected

                if match:
                    print(f"   [PASS] {expected_name} {check_name}: {actual}")
                else:
                    print(f"   [FAIL] {expected_name} {check_name}: expected {expected}, got {actual}")
                    errors.append(f"{expected_name} {check_name}: expected {expected}, got {actual}")
                    success = False

        # Verify agent files (agent.py, server.py) and syntax for each required agent
        print("\n2. Verifying Agent Files")
        print("-" * 60)

        for expected_name, _label, _desc in REQUIRED_AGENTS:
            agent_meta = registry.get_agent(expected_name)
            if not agent_meta:
                continue

            agent_py = agent_meta.path / "agent.py"
            server_py = agent_meta.path / "server.py"

            if not agent_py.exists():
                errors.append(f"{expected_name}: agent.py not found")
                success = False
                print(f"   [FAIL] {expected_name} agent.py not found")
            else:
                print(f"   [PASS] {expected_name} agent.py exists")

            if not server_py.exists():
                errors.append(f"{expected_name}: server.py not found")
                success = False
                print(f"   [FAIL] {expected_name} server.py not found")
            else:
                print(f"   [PASS] {expected_name} server.py exists")

            if agent_py.exists():
                try:
                    with open(agent_py, "r", encoding="utf-8") as f:
                        code = f.read()
                    compile(code, agent_py, "exec")
                    print(f"   [PASS] {expected_name} agent.py syntax valid")
                except SyntaxError as e:
                    errors.append(f"{expected_name} agent.py syntax error: {e}")
                    success = False
                    print(f"   [FAIL] {expected_name} agent.py syntax error: {e}")
                except Exception as e:
                    print(f"   [WARN] {expected_name} agent.py import skipped (env): {e}")

    except Exception as e:
        errors.append(f"Error during verification: {e}")
        success = False
        print(f"[FAIL] Exception during verification: {e}")
        import traceback

        traceback.print_exc()

    return success, errors


def verify_test_files() -> tuple[bool, list[str]]:
    """Verify that test files exist and are structured correctly."""
    errors = []
    success = True

    print("\n" + "=" * 60)
    print("4. Verifying Test Files")
    print("=" * 60)

    test_files = [
        ("Agent Registry Tests", project_root / "frontend" / "utils" / "test_agent_registry.py"),
        ("API Router Tests", project_root / "frontend" / "routers" / "test_agents.py"),
        ("Model Tests", project_root / "frontend" / "test_models.py"),
        ("Base Agent Tests", project_root / "agents" / "base_agent" / "tests" / "test_tools.py"),
        ("Researcher Tools Tests", project_root / "agents" / "researcher_agent" / "tests" / "test_tools.py"),
    ]

    for name, test_file in test_files:
        if test_file.exists():
            print(f"   [PASS] {name}: {test_file}")
        else:
            print(f"   [FAIL] {name}: Missing at {test_file}")
            errors.append(f"Missing test file: {test_file}")
            success = False

    return success, errors


def verify_evaluation_files() -> tuple[bool, list[str]]:
    """Verify evaluation files exist for base_agent and researcher_agent."""
    errors = []
    success = True

    print("\n" + "=" * 60)
    print("5. Verifying Evaluation Files")
    print("=" * 60)

    eval_checks = [
        ("base_agent test", project_root / "agents" / "base_agent" / "evaluations" / "base_baseline.test.json"),
        ("base_agent config", project_root / "agents" / "base_agent" / "evaluations" / "test_config.json"),
        ("researcher_agent test", project_root / "agents" / "researcher_agent" / "evaluations" / "researcher_basic.test.json"),
        ("researcher_agent config", project_root / "agents" / "researcher_agent" / "evaluations" / "test_config.json"),
    ]

    for name, path in eval_checks:
        if path.exists():
            print(f"   [PASS] {name}: {path}")
        else:
            print(f"   [FAIL] {name}: Missing at {path}")
            errors.append(f"Missing evaluation file: {path}")
            success = False

    return success, errors


def main() -> int:
    """Run all verification checks."""
    print("\n" + "=" * 60)
    print("Test Setup Verification")
    print("=" * 60)
    print()

    all_errors = []
    all_success = True

    # Run checks
    success, errors = verify_agents()
    all_success = all_success and success
    all_errors.extend(errors)

    success, errors = verify_test_files()
    all_success = all_success and success
    all_errors.extend(errors)

    success, errors = verify_evaluation_files()
    all_success = all_success and success
    all_errors.extend(errors)

    # Summary
    print("\n" + "=" * 60)
    print("Summary")
    print("=" * 60)

    if all_success:
        print("[PASS] All checks passed!")
        return 0
    else:
        print("[FAIL] Some checks failed:")
        for error in all_errors:
            print(f"   - {error}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
