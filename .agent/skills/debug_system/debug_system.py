import argparse
import json
import sys
from typing import Any

import docker

try:
    client = docker.from_env()
except Exception:
    client = None

def check_container_health() -> dict[str, str]:
    """Returns status of all containers."""
    if not client:
        return {"error": "Docker not connected"}
    
    status = {}
    for c in client.containers.list():
        status[c.name] = c.status
    return status

def get_recent_errors(limit: int = 10) -> list[dict[str, Any]]:
    """
    Reads recent logs from containers and filters for structured JSON errors.
    Standard SRE workflow: Log Aggregation.
    """
    if not client:
        return [{"error": "Docker not connected"}]

    errors = []
    # In a real cluster, we'd query Loki/Splunk/Phoenix.
    # For local dev, we scan docker logs for our JSON format.
    for c in client.containers.list():
        try:
            # tailored for performance: only look at last 100 lines
            logs = c.logs(tail=100).decode('utf-8', errors='ignore')
            for line in logs.splitlines():
                if not line.strip():
                    continue
                try:
                    # Attempt to parse our JSONFormatter output
                    entry = json.loads(line)
                    if isinstance(entry, dict) and entry.get("level") == "ERROR":
                        entry["_source_container"] = c.name
                        errors.append(entry)
                except json.JSONDecodeError:
                    pass
        except Exception:
            pass
    
    # Sort by timestamp desc if possible (assuming ISO format)
    errors.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
    return errors[:limit]

def main():
    parser = argparse.ArgumentParser(description="SRE Debug Tool")
    parser.add_argument("--fix", action="store_true", help="Attempt auto-fix")
    parser.add_argument("--analyze", action="store_true", help="Analyze logs")
    args = parser.parse_args()

    if args.fix:
        # Simple auto-heal logic
        health = check_container_health()
        print(f"System Health: {json.dumps(health, indent=2)}")
        
        errors = get_recent_errors(5)
        if errors:
            print("\nRecent Critical Errors:")
            print(json.dumps(errors, indent=2))
        else:
            print("\nNo recent critical structured errors found.")
            
    if args.analyze:
        print(json.dumps(get_recent_errors(20), indent=2))

if __name__ == "__main__":
    main()
