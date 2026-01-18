
import argparse
import subprocess

def register(subparsers):
    parser = subparsers.add_parser("stop", help="Stop the Agent Platform")
    parser.add_argument("--volumes", "-v", action="store_true", help="Remove volumes (CAUTION: Deletes data)")

def run(args):
    print("🛑 Stopping Agent Platform...")
    
    cmd = ["docker-compose", "down", "--remove-orphans"]
    
    if args.volumes:
        print("⚠️  Removing volumes as requested...")
        cmd.append("-v")
        
    print(f"Running: {' '.join(cmd)}")
    
    try:
        subprocess.run(cmd, check=True, shell=True)
        return 0
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to stop platform: {e}")
        return e.returncode
