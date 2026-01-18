
import argparse
import subprocess
import sys

def register(subparsers):
    parser = subparsers.add_parser("test", help="Run Automated Tests")
    parser.add_argument("--unit", action="store_true", help="Run only unit tests")
    parser.add_argument("--integration", action="store_true", help="Run only integration tests")
    parser.add_argument("--e2e", action="store_true", help="Run only E2E tests")
    parser.add_argument("args", nargs=argparse.REMAINDER, help="Access extra pytest arguments (e.g. -vv)")

def run(args):
    print("🧪 Running Tests...")
    
    # Base command using uv
    cmd = ["uv", "run", "pytest"]
    
    # Determine path based on flags
    target = "tests/"
    if args.unit:
        target = "tests/unit/"
    elif args.integration:
        target = "tests/integration/"
    elif args.e2e:
        # In our codebase, E2E usually refers to integration/pipeline flows
        # Adjust if we have specific e2e folder
        target = "tests/integration/test_pipeline_flow.py"
        
    cmd.append(target)
    
    # Pass through extra args
    if args.args:
        cmd.extend(args.args)
        
    print(f"Running: {' '.join(cmd)}")
    
    try:
        subprocess.run(cmd, check=True, shell=True)
        return 0
    except subprocess.CalledProcessError as e:
        print("❌ Tests Failed!")
        return e.returncode
