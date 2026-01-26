#!/usr/bin/env python3
"""
Health check utility for verifying all services in the dev stack are ready.

Usage:
    python scripts/health_check.py
    python scripts/health_check.py --timeout 60
    python scripts/health_check.py --api-only
"""

import argparse
import subprocess
import sys
import time
from pathlib import Path

import requests

# Add project root to path
ROOT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT_DIR))

# Service endpoints
SERVICES = {
    "dashboard_api": "http://localhost:8010/health",
    "phoenix": "http://localhost:6006/health",
}

# Docker container names to check
DOCKER_CONTAINERS = [
    "content_creation-phoenix",
]


def check_docker_containers() -> bool:
    """Check if Docker containers are running."""
    try:
        import docker
        client = docker.from_env()
        containers = client.containers.list(filters={"status": "running"})
        container_names = {c.name for c in containers}
        
        all_running = True
        for container_name in DOCKER_CONTAINERS:
            if container_name in container_names:
                print(f"✅ Docker container '{container_name}' is running")
            else:
                print(f"❌ Docker container '{container_name}' is not running")
                all_running = False
        
        return all_running
    except ImportError:
        print("⚠️  docker Python package not installed, skipping container check")
        return True
    except Exception as e:
        print(f"⚠️  Error checking Docker containers: {e}")
        return False


def check_service(name: str, url: str, timeout: int = 5) -> bool:
    """Check if a service is healthy."""
    try:
        response = requests.get(url, timeout=timeout)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ {name} is healthy: {data}")
            return True
        else:
            print(f"❌ {name} returned status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print(f"❌ {name} is not reachable at {url}")
        return False
    except requests.exceptions.Timeout:
        print(f"❌ {name} timed out after {timeout}s")
        return False
    except Exception as e:
        print(f"❌ {name} error: {e}")
        return False


def show_docker_logs(container_name: str | None = None, lines: int = 20) -> None:
    """Show recent Docker logs."""
    try:
        cmd = ["docker", "compose", "logs", "--tail", str(lines)]
        if container_name:
            cmd.append(container_name)
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        if result.stdout:
            print(f"\n📋 Recent Docker logs ({container_name or 'all services'}):")
            print("-" * 80)
            print(result.stdout)
            print("-" * 80)
    except Exception as e:
        print(f"⚠️  Could not fetch Docker logs: {e}")


def wait_for_services(
    services: dict[str, str],
    timeout: int = 120,
    check_interval: int = 2,
    api_only: bool = False,
    show_logs: bool = True,
    log_interval: int = 30,  # Show logs every N seconds
) -> bool:
    """Wait for all services to become healthy."""
    print(f"⏳ Waiting for services to be ready (timeout: {timeout}s)...")
    if show_logs:
        print("📋 Showing initial container status and logs...")
        try:
            result = subprocess.run(
                ["docker", "compose", "ps"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            if result.stdout:
                print(result.stdout)
        except Exception:
            pass
        show_docker_logs(lines=10)
    print("")
    
    start_time = time.time()
    elapsed = 0
    last_log_time = 0
    
    while elapsed < timeout:
        all_healthy = True
        
        # Check Docker containers (if not api-only)
        if not api_only:
            if not check_docker_containers():
                all_healthy = False
        
        # Check HTTP services
        for name, url in services.items():
            if not check_service(name, url):
                all_healthy = False
        
        if all_healthy:
            print("")
            print("✅ All services are healthy!")
            if show_logs:
                print("\n📋 Final container status:")
                try:
                    result = subprocess.run(
                        ["docker", "compose", "ps"],
                        capture_output=True,
                        text=True,
                        timeout=5,
                    )
                    if result.stdout:
                        print(result.stdout)
                except Exception:
                    pass
            return True
        
        elapsed = time.time() - start_time
        remaining = timeout - elapsed
        
        # Show logs periodically or if we're getting close to timeout
        if show_logs and (
            elapsed - last_log_time >= log_interval
            or remaining < 30
            or elapsed < 10  # Show early logs
        ):
            print(f"\n📋 Status update (elapsed: {int(elapsed)}s)...")
            show_docker_logs(lines=15)
            last_log_time = elapsed
        
        if remaining > 0:
            print(f"   Retrying in {check_interval}s... (elapsed: {int(elapsed)}s, remaining: {int(remaining)}s)")
            time.sleep(check_interval)
    
    print("")
    print(f"❌ Timeout after {timeout}s. Some services are not healthy.")
    if show_logs:
        print("\n📋 Showing final logs for debugging:")
        show_docker_logs(lines=50)
        print("\n💡 To see live logs, run: make dev-logs")
    return False


def main():
    parser = argparse.ArgumentParser(description="Health check for dev stack services")
    parser.add_argument(
        "--timeout",
        type=int,
        default=120,
        help="Maximum time to wait for services (seconds)",
    )
    parser.add_argument(
        "--api-only",
        action="store_true",
        help="Only check API services, skip Docker containers",
    )
    parser.add_argument(
        "--service",
        type=str,
        help="Check only a specific service (dashboard_api, phoenix)",
    )
    parser.add_argument(
        "--no-logs",
        action="store_true",
        help="Don't show Docker logs during health check",
    )
    parser.add_argument(
        "--log-interval",
        type=int,
        default=30,
        help="Show logs every N seconds during wait (default: 30)",
    )
    
    args = parser.parse_args()
    
    # Filter services if specific service requested
    services_to_check = SERVICES
    if args.service:
        if args.service not in SERVICES:
            print(f"❌ Unknown service: {args.service}")
            print(f"   Available services: {', '.join(SERVICES.keys())}")
            sys.exit(1)
        services_to_check = {args.service: SERVICES[args.service]}
    
    success = wait_for_services(
        services_to_check,
        timeout=args.timeout,
        api_only=args.api_only,
        show_logs=not args.no_logs,
        log_interval=args.log_interval,
    )
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
