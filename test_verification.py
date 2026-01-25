#!/usr/bin/env python3
"""
Test Verification Script

Verifies the current test setup and researcher agent functionality.
Run this to check that everything is working before making improvements.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from frontend.utils.agent_registry import AgentRegistry


def verify_researcher_agent() -> tuple[bool, list[str]]:
    """Verify researcher agent is discoverable and has correct metadata."""
    errors = []
    success = True

    print("=" * 60)
    print("1. Verifying Researcher Agent Discovery")
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

        researcher = registry.get_agent("researcher_agent")
        if not researcher:
            errors.append("researcher_agent not found")
            success = False
            print("[FAIL] researcher_agent not discovered")
            return success, errors

        print(f"[PASS] Found {len(agents)} agent(s)")
        print(f"   - researcher_agent: OK")

        # Verify metadata
        print("\n2. Verifying Researcher Agent Metadata")
        print("-" * 60)

        checks = [
            ("name", researcher.name, "researcher_agent"),
            ("description", researcher.description, "Research assistant that browses"),
            ("model", researcher.model, "gemini-2.0-flash"),
            ("has_server", researcher.has_server, True),
            ("path exists", researcher.path.exists(), True),
        ]

        for check_name, actual, expected in checks:
            if isinstance(expected, bool):
                match = actual == expected
            elif isinstance(expected, str):
                match = expected in str(actual) if actual else False
            else:
                match = actual == expected

            if match:
                print(f"   [PASS] {check_name}: {actual}")
            else:
                print(f"   [FAIL] {check_name}: expected {expected}, got {actual}")
                errors.append(f"{check_name}: expected {expected}, got {actual}")
                success = False

        # Verify agent.py exists and is parseable
        print("\n3. Verifying Agent Files")
        print("-" * 60)

        agent_py = researcher.path / "agent.py"
        if not agent_py.exists():
            errors.append("agent.py not found")
            success = False
            print(f"   [FAIL] agent.py not found at {agent_py}")
        else:
            print(f"   [PASS] agent.py exists: {agent_py}")

        server_py = researcher.path / "server.py"
        if not server_py.exists():
            errors.append("server.py not found (expected for researcher_agent)")
            success = False
            print(f"   [FAIL] server.py not found at {server_py}")
        else:
            print(f"   [PASS] server.py exists: {server_py}")

        # Verify agent.py can be imported (syntax check)
        try:
            import importlib.util
            spec = importlib.util.spec_from_file_location("agent", agent_py)
            if spec and spec.loader:
                # Just check syntax, don't actually load (might need env vars)
                with open(agent_py, "r", encoding="utf-8") as f:
                    code = f.read()
                compile(code, agent_py, "exec")
                print(f"   [PASS] agent.py syntax is valid")
            else:
                errors.append("Could not create spec for agent.py")
                success = False
        except SyntaxError as e:
            errors.append(f"agent.py has syntax error: {e}")
            success = False
            print(f"   [FAIL] agent.py syntax error: {e}")
        except Exception as e:
            # Might fail due to missing imports, that's okay for syntax check
            print(f"   [WARN] agent.py import check skipped (may need env vars): {e}")

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
    """Verify evaluation files exist for researcher agent."""
    errors = []
    success = True

    print("\n" + "=" * 60)
    print("5. Verifying Evaluation Files")
    print("=" * 60)

    eval_dir = project_root / "agents" / "researcher_agent" / "evaluations"
    eval_files = [
        ("Test file", eval_dir / "researcher_basic.test.json"),
        ("Test config", eval_dir / "test_config.json"),
    ]

    for name, eval_file in eval_files:
        if eval_file.exists():
            print(f"   [PASS] {name}: {eval_file}")
        else:
            print(f"   [FAIL] {name}: Missing at {eval_file}")
            errors.append(f"Missing evaluation file: {eval_file}")
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
    success, errors = verify_researcher_agent()
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
