
import argparse
import os
import sys
import yaml
from pathlib import Path
from dotenv import load_dotenv

# Optional import for API checks (only if --api is used or available)
try:
    from google import genai
    HAS_GENAI = True
except ImportError:
    HAS_GENAI = False

def register(subparsers):
    parser = subparsers.add_parser("debug", help="Verify configuration and system health")
    parser.add_argument("--api", action="store_true", help="Ping Google API to verify keys and models")
    parser.add_argument("--logs", action="store_true", help="Gather docker logs to artifacts/debug_logs/")

def check_env():
    print("\n[1/4] Checking Environment...")
    env_path = Path(".env")
    if not env_path.exists():
        print("❌ .env file missing!")
        return False
    
    load_dotenv()
    
    key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    if not key:
        print("❌ GEMINI_API_KEY (or GOOGLE_API_KEY) not found in env.")
        return False

    print("✅ .env exists and API Key is set.")
    return True

def check_structure():
    print("\n[2/4] Checking Project Structure...")
    
    # Check Domains
    domains_dir = Path("domains")
    if not domains_dir.exists():
        print("❌ domains/ directory missing")
        return False

    print(f"✅ Found domains at {domains_dir}")
    return True

def check_api():
    print("\n[3/4] Checking API Connectivity (Google GenAI)...")
    if not HAS_GENAI:
        print("❌ google-genai package not installed/found. Cannot check API.")
        return False
        
    try:
        load_dotenv()
        key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
        client = genai.Client(api_key=key)
        
        print("   Pinging API with 'models.list'...")
        models = list(client.models.list())
        count = len(models)
        
        print(f"✅ API Connection Successful! Found {count} models.")
        
        # Quick check for our standard models
        standards = ["gemini-2.0-flash-exp", "gemini-1.5-pro"]
        for s in standards:
            found = any(m.name.endswith(s) for m in models)
            status = "✅" if found else "⚠️"
            print(f"   {status} {s}")

        return True
    except Exception as e:
        print(f"❌ API Check Failed: {e}")
        return False

def collect_logs():
    print("\n[4/4] Gathering System Logs...")
    import subprocess
    import time
    import shutil
    
    log_dir = Path("artifacts/debug_logs")
    log_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = int(time.time())
    
    # 1. Docker Logs
    docker_log = log_dir / f"docker_dump_{timestamp}.log"
    try:
        print(f"   Writing full docker logs to {docker_log}...")
        with open(docker_log, "w", encoding="utf-8") as f:
            subprocess.run(["docker-compose", "logs", "--no-color", "--timestamps"], stdout=f, stderr=subprocess.STDOUT, check=True, shell=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to capture docker logs: {e}")
    except Exception as e:
        print(f"❌ Unexpected error writing docker logs: {e}")

    # 2. Local Log Files (e.g. npm-debug.log, or app-specific logs)
    print("   Scanning for local log files (*.log)...")
    root_dir = Path.cwd()
    search_patterns = ["*.log", "npm-debug.log", "yarn-error.log"]
    
    count = 0
    for pattern in search_patterns:
        # Shallow search in root, or potentially recursive if needed (avoiding artifacts/node_modules)
        for log_file in root_dir.glob(pattern):
            if "artifacts" in log_file.parts or "node_modules" in log_file.parts or ".git" in log_file.parts:
                continue
                
            try:
                dest = log_dir / f"local_{log_file.name}_{timestamp}"
                shutil.copy2(log_file, dest)
                print(f"   Saved local log: {log_file.name}")
                count += 1
            except Exception as e:
                print(f"⚠️  Failed to copy {log_file.name}: {e}")
    
    if count == 0:
        print("   No local *.log files found.")

    print("✅ Logs captured successfully.")
    return True

def run(args):
    print("🕵️  Running System Diagnostics...")
    
    ok_env = check_env()
    ok_struct = check_structure()
    
    ok_api = True
    if args.api:
        ok_api = check_api()
    else:
        print("\n[3/4] Skipping API Check (use --api to verify)")

    ok_logs = True
    if args.logs:
        ok_logs = collect_logs()
    else:
        print("\n[4/4] Skipping Log Gathering (use --logs to capture)")
        
    if ok_env and ok_struct and ok_api and ok_logs:
        print("\n✅ System appears healthy.")
        return 0
    else:
        print("\n❌ Issues detected.")
        return 1
