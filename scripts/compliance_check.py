import argparse
import sys
import re
import os
from pathlib import Path

def check_file(file_path: Path) -> list[str]:
    """Scans a single file for violations."""
    violations = []
    try:
        content = file_path.read_text(encoding="utf-8")
        lines = content.splitlines()
        
        for i, line in enumerate(lines, 1):
            line_str = line.strip()
            
            # 1. Print Statements (but allow simple comments, though regex is better)
            if "print(" in line_str and not line_str.startswith("#"):
                violations.append(f"[Print Violation] {file_path}:{i}: {line_str}")
                
            # 2. Hardcoded Env
            if "os.getenv" in line_str:
                violations.append(f"[Config Violation] {file_path}:{i}: {line_str}")
                
            # 3. Global Agent Instantiation (Heuristic: Top-level assignment)
            # Must start at the beginning of the line (no indentation)
            if re.search(r"^[a-zA-Z_]\w*\s*=\s*.*Agent\(", line):
                 violations.append(f"[Architecture Violation] {file_path}:{i}: {line_str}")
                 
            # 4. Any Type
            if "Any" in line_str:
                 violations.append(f"[Type Violation] {file_path}:{i}: {line_str}")
                 
    except Exception as e:
        print(f"Warning: Could not read {file_path}: {e}")
        
    return violations

def compliance_check_action():
    print("Running GEMINI.md Compliance Check (Pure Python)...\n")
    all_violations = []
    
    # Define scope
    base_dir = Path("domains")
    if not base_dir.exists():
         print("Warning: 'domains/' directory not found. Scanning current directory instead.")
         base_dir = Path(".")

    # Walk recursively with os.walk to handle permissions and exclusions
    print(f"Scanning {base_dir.absolute()}...")
    
    for root, dirs, files in os.walk(base_dir):
        # Modify dirs in-place to skip ignored directories
        dirs[:] = [d for d in dirs if d not in {".venv", ".git", "__pycache__", "node_modules", "site-packages"}]
        
        for file in files:
            if not file.endswith(".py"):
                continue
                
            file_path = Path(root) / file
            all_violations.extend(check_file(file_path))

    print("\n" + "="*30)
    if all_violations:
        print(f"❌ COMPLIANCE FAILED: {len(all_violations)} violations found.")
        for v in all_violations:
            print(v)
        sys.exit(1)
    else:
        print("✅ COMPLIANCE PASSED: No violations found.")
        sys.exit(0)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Scans codebase for GEMINI.md violations (Print, Any, Hardcoded Env).")
    args = parser.parse_args()
    
    compliance_check_action()
