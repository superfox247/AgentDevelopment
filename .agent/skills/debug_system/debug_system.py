import argparse
import logging
import subprocess
import sys
import json
import re

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
    if args.fix:
        attempt_fix()
        return

    check_docker_health()
    
    if args.target:
        analyze_logs(args.target)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Debugs system components.")
    parser.add_argument("--target", default="all", help="Target service to analyze (or 'all')")
    parser.add_argument("--fix", action="store_true", help="Attempt to fix common issues")
    
    args = parser.parse_args()
    debug_system_action(args)
