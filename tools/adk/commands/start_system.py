
import argparse
import subprocess
import sys
from pathlib import Path

def register(subparsers):
    parser = subparsers.add_parser("start", help="Start the Agent Platform (Docker)")
    parser.add_argument("--build", action="store_true", help="Force build docker containers")
    parser.add_argument("--detach", "-d", action="store_true", help="Run in detached mode (background)")
    parser.add_argument("services", nargs="*", help="Specific services to start (default: all)")

def run(args):
    print("🚀 Starting Agent Platform...")
    
    cmd = ["docker-compose", "up"]
    
    if args.build:
        cmd.append("--build")
        
    if args.detach:
        cmd.append("-d")
        
    if args.services:
        cmd.extend(args.services)
        
    print(f"Running: {' '.join(cmd)}")
    
    try:
        # We use shell=True on Windows for docker-compose usually, or just direct call if in path
        # Using sys.stdout ensures we see output
        subprocess.run(cmd, check=True, shell=True)
        return 0
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to start platform: {e}")
        return e.returncode
    except KeyboardInterrupt:
        print("\n🛑 Stopped.")
        return 0
