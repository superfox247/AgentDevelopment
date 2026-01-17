import argparse
import sys
import re
import os
from pathlib import Path

# Patterns to hunt for
SECRET_PATTERNS = {
    "API Key": r"(api_key|apikey|secret|token)\s*=\s*['\"][a-zA-Z0-9_\-]{20,}['\"]",
    "Bearer Token": r"Bearer\s+[a-zA-Z0-9\-\._~+/]+=*",
    "Password": r"password\s*=\s*['\"][^'\"]{1,}['\"]",
    "AWS Key": r"AKIA[0-9A-Z]{16}",
}

def check_file_for_secrets(file_path: Path) -> list[str]:
    """Scans a single file for regex matches."""
    violations = []
    try:
        content = file_path.read_text(encoding="utf-8")
        lines = content.splitlines()
        
        for i, line in enumerate(lines, 1):
            line_str = line.strip()
            
            # Skip comments? Maybe NOT for secrets, they shouldn't even be commented out.
            
            for name, pattern in SECRET_PATTERNS.items():
                if re.search(pattern, line_str, re.IGNORECASE):
                     # Obfuscate the secret in output
                     violations.append(f"[{name}] {file_path}:{i}")

    except Exception:
        # Ignore binary files or read errors
        pass
        
    return violations

def check_env_gap(base_dir: Path) -> list[str]:
    """Checks if .env keys are missing from .env.example"""
    violations = []
    env_path = base_dir / ".env"
    example_path = base_dir / ".env.example"
    
    if not env_path.exists() or not example_path.exists():
        return []
        
    try:
        env_keys = {line.split("=")[0].strip() for line in env_path.read_text().splitlines() if "=" in line and not line.startswith("#")}
        example_keys = {line.split("=")[0].strip() for line in example_path.read_text().splitlines() if "=" in line and not line.startswith("#")}
        
        missing = env_keys - example_keys
        if missing:
            violations.append(f"[Env Gap] The following keys are in .env but MISSING from .env.example: {', '.join(missing)}")
            
    except Exception:
        pass
        
    return violations

def audit_security_action():
    print("Running Security Audit...\n")
    all_violations = []
    
    base_dir = Path(os.getcwd())

    # 1. Env Gap Analysis
    print("1. Checking Environment Consistency...")
    all_violations.extend(check_env_gap(base_dir))

    # 2. Secret Scanning
    print("2. Scanning for Secrets (Regex)...")
    for root, dirs, files in os.walk(base_dir):
        # Exclude
        dirs[:] = [d for d in dirs if d not in {".venv", ".git", "__pycache__", "node_modules", "site-packages", ".idea", ".vscode"}]
        
        for file in files:
            # Skip non-text files heavily
            if file.endswith((".png", ".jpg", ".pyc", ".exe", ".dll")):
                continue
                
            file_path = Path(root) / file
            
            # Skip the .env file itself (it's supposed to have secrets)
            if file_path.name == ".env":
                continue
                
            all_violations.extend(check_file_for_secrets(file_path))

    print("\n" + "="*30)
    if all_violations:
        print(f"❌ SECURITY AUDIT FAILED: {len(all_violations)} risks found.")
        for v in all_violations:
            print(v)
        sys.exit(1)
    else:
        print("✅ SECURITY AUDIT PASSED: No secrets found.")
        sys.exit(0)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Scans codebase for security risks.")
    args = parser.parse_args()
    
    audit_security_action()
