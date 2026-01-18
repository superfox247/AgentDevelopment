
import argparse
import subprocess
import shutil
import time
from pathlib import Path

def register(subparsers):
    parser = subparsers.add_parser("reset", help="Completely reset the environment (Nuclear Option)")
    parser.add_argument("--hard", action="store_true", help="Also delete .venv (Requires re-sync)")

def run(args):
    print("☢️  INITIATING SYSTEM RESET ☢️")
    print("This will stop all containers, delete volumes, and clean artifacts.")
    
    # Comfirmation
    confirm = input("Are you sure? (y/N): ")
    if confirm.lower() != 'y':
        print("Aborted.")
        return 0

    # 1. Stop Docker with Volumes
    print("\n[1/3] Stopping Docker & Removing Volumes...")
    subprocess.run(["docker-compose", "down", "-v", "--remove-orphans"], shell=True)
    
    # 2. Clean Artifacts
    print("\n[2/3] Cleaning Artifacts...")
    artifacts_dir = Path("artifacts")
    if artifacts_dir.exists():
        try:
            # We preserve the directory but clean contents
            for child in artifacts_dir.iterdir():
                if child.name == ".gitkeep": continue
                if child.is_dir():
                    shutil.rmtree(child)
                else:
                    child.unlink()
            print("✅ Artifacts cleaned.")
        except Exception as e:
            print(f"⚠️  Failed to clean artifacts: {e}")
    
    # 3. Hard Reset (Optional)
    if args.hard:
        print("\n[3/3] Deleting .venv (Hard Reset)...")
        venv_dir = Path(".venv")
        if venv_dir.exists():
            shutil.rmtree(venv_dir)
            print("✅ .venv deleted. Run 'uv sync' next.")
        else:
            print("ℹ️  .venv not found, skipping.")
            
    print("\n✅ RESET COMPLETE.")
    return 0
