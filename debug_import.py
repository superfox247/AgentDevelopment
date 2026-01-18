
import sys
import os

# Add current directory to path just in case
sys.path.append(os.getcwd())

print(f"CWD: {os.getcwd()}")
print(f"Sys Path: {sys.path}")

try:
    print("Attempting import...")
    from domains.course_creator.orchestrator.server import create_app
    print("Import successful")
except Exception as e:
    print(f"Import failed: {e}")
    import traceback
    traceback.print_exc()
