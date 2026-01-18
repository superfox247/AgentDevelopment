import argparse
import logging
import subprocess
import sys
import json
import re
import urllib.request
import urllib.error

# Configure Logging
logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)

def run_command(command):
    """Runs a shell command and returns output."""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, encoding='utf-8', errors='replace')
        return result.stdout.strip(), result.stderr.strip(), result.returncode
    except Exception as e:
        return "", str(e), 1

def check_docker_health():
    """Checks the status of all docker containers."""
    logger.info("🏥 Checking Docker Health...")
    stdout, stderr, code = run_command("docker compose ps --format json")
    
    if code != 0:
        logger.error(f"❌ Failed to run docker compose ps: {stderr}")
        return []

    services = []
    try:
        # Docker compose ps json output can be a stream of objects or a list
        for line in stdout.splitlines():
            if not line.strip(): continue
            service = json.loads(line)
            services.append(service)
            
            state = service.get("State", "Unknown")
            status = service.get("Status", "Unknown")
            name = service.get("Service", "Unknown")
            
            icon = "✅" if state == "running" else "⚠️ "
            logger.info(f"  {icon} {name:<20} | {state:<10} | {status}")
            
    except json.JSONDecodeError:
        logger.warning("Could not parse docker output JSON.")
    
    return services

def check_web_servers():
    """Checks the health of local web servers."""
    logger.info("🌐 Checking Web Servers...")
    
    targets = [
        ("Dashboard Backend", "http://localhost:8010/api/status"),
        ("Dashboard Frontend", "http://localhost:4173"), # Preview Port
        ("ADK Web UI", "http://localhost:8000"),
        ("Phoenix UI", "http://localhost:6006"),
    ]

    for name, url in targets:
        try:
            with urllib.request.urlopen(url, timeout=2) as response:
                if response.status < 400:
                    logger.info(f"  ✅ {name:<20} | {url} | Online ({response.status})")
                else:
                    logger.warning(f"  ⚠️  {name:<20} | {url} | Status {response.status}")
        except urllib.error.URLError:
             logger.error(f"  ❌ {name:<20} | {url} | Unreachable")
        except Exception as e:
             logger.error(f"  ❌ {name:<20} | {url} | Error: {e}")

def analyze_logs(target="all"):
    """Analyzes logs for errors and exceptions."""
    logger.info(f"🕵️  Analyzing Logs (Target: {target})...")
    
    services = [target] if target != "all" else ["orchestrator", "researcher", "content_builder", "image_generator", "customer_service", "phoenix"]
    
    error_patterns = [
        r"Traceback \(most recent call last\):",
        r"ERROR:",
        r"CRITICAL:",
        r"Exception:",
        r"Error:"
    ]
    
    issues_found = False
    
    for service in services:
        # Get last 50 lines
        stdout, _, _ = run_command(f"docker compose logs --tail=50 {service}")
        
        service_issues = []
        lines = stdout.splitlines()
        
        for i, line in enumerate(lines):
            for pattern in error_patterns:
                if re.search(pattern, line):
                    # Capture context (this line + next 5 lines)
                    context = lines[i:i+5]
                    service_issues.append("\n".join(context))
                    break
        
        if service_issues:
            issues_found = True
            logger.warning(f"🚩 Issues found in '{service}':")
            for issue in service_issues[-3:]: # Show last 3 errors
                logger.warning(f"    ---\n    {issue}\n    ---")
        else:
            if target != "all":
                logger.info(f"  ✅ No recent errors found in {service}")

    if not issues_found and target == "all":
        logger.info("  ✅ No recent errors found in core services.")

def rebuild_service(target):
    """Forcefully rebuilds and recreates a service/container to clear stale state."""
    logger.info(f"🚧 Rebuilding Service: {target}")
    
    if target == "all":
        cmd = "docker compose up -d --build --force-recreate --remove-orphans"
    else:
        cmd = f"docker compose up -d --build --force-recreate --remove-orphans {target}"
    
    logger.info(f"  Running: {cmd}")
    stdout, stderr, code = run_command(cmd)
    
    if code == 0:
        logger.info(f"  ✅ Successfully rebuilt {target}")
        # Wait a moment for it to start?
    else:
        logger.error(f"  ❌ Rebuild failed: {stderr}")

def attempt_fix():
    """Attempts simple fixes for common issues."""
    logger.info("🔧 Attempting Auto-Fixes...")
    
    services = check_docker_health()
    
    for service in services:
        state = service.get("State", "")
        name = service.get("Service", "")
        
        if state in ["exited", "dead"]:
            logger.info(f"  🔄 Restarting dead service: {name}")
            run_command(f"docker compose restart {name}")
            logger.info(f"     Done.")

def debug_system_action(args):
    if args.rebuild:
        rebuild_service(args.rebuild)
        return

    if args.fix:
        attempt_fix()
        return

    check_docker_health()
    check_web_servers()
    
    if args.target:
        analyze_logs(args.target)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Debugs system components.")
    parser.add_argument("--target", default="all", help="Target service to analyze (or 'all')")
    parser.add_argument("--fix", action="store_true", help="Attempt to fix common issues")
    parser.add_argument("--rebuild", help="Target service to rebuild and force-recreate (or 'all')")
    
    args = parser.parse_args()
    debug_system_action(args)
