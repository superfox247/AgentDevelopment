
import argparse
import sys
from tools.adk.commands import list_agents, start_system, run_tests, stop_system, reset_system, debug_system

def main():
    parser = argparse.ArgumentParser(
        prog="adk",
        description="Antigravity Development Kit - Internal Developer Platform CLI"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Register Commands
    list_agents.register(subparsers)
    start_system.register(subparsers)
    run_tests.register(subparsers)
    stop_system.register(subparsers)
    reset_system.register(subparsers)
    debug_system.register(subparsers)
    
    # Parse
    args = parser.parse_args()
    
    if args.command == "list":
        return list_agents.run(args)
    elif args.command == "start":
        return start_system.run(args)
    elif args.command == "test":
        return run_tests.run(args)
    elif args.command == "stop":
        return stop_system.run(args)
    elif args.command == "reset":
        return reset_system.run(args)
    elif args.command == "debug":
        return debug_system.run(args)
    else:
        parser.print_help()
        return 1

if __name__ == "__main__":
    sys.exit(main())
