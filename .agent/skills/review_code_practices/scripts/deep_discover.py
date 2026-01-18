import json
import os
from pathlib import Path

# Constants - assume run from workspace root or similar, but let's be robust
WORKSPACE_ROOT = Path(os.getcwd())

def find_file(filename):
    """Finds a file in the workspace root."""
    fpath = WORKSPACE_ROOT / filename
    return fpath if fpath.exists() else None

def scan_package_json():
    fpath = find_file("package.json")
    if not fpath:
        return {}
    
    try:
        with open(fpath, "r", encoding="utf-8") as f:
            data = json.load(f)
            deps = data.get("dependencies", {})
            dev_deps = data.get("devDependencies", {})
            return {**deps, **dev_deps}
    except Exception as e:
        return {"error": str(e)}

def scan_requirements():
    fpath = find_file("requirements.txt")
    if not fpath:
        return []
    
    try:
        with open(fpath, "r", encoding="utf-8") as f:
            return [line.strip() for line in f if line.strip() and not line.startswith("#")]
    except Exception as e:
        return [f"Error: {str(e)}"]

def scan_docker():
    fpath = find_file("Dockerfile")
    if not fpath:
        return None
    
    try:
        with open(fpath, "r", encoding="utf-8") as f:
            content = f.read()
            # Simple grab of FROM
            for line in content.splitlines():
                if line.startswith("FROM"):
                    return line.strip()
    except Exception:
        pass
    return "Dockerfile found but parse failed"

def print_frontend_summary(npm_deps):
    print("--- Frontend (package.json) ---")
    if npm_deps:
        # Highlight key ones
        keys = ["react", "vue", "next", "tailwindcss", "vite"]
        found = {k: v for k, v in npm_deps.items() if any(key in k for key in keys)}
        if found:
            for k, v in found.items():
                print(f"  - {k}: {v}")
        else:
            print("  (No major frameworks detected in top-level summary)")
            print(f"  Total deps: {len(npm_deps)}")
    else:
        print("  (No package.json found)")
    print("")

def scan_project_toml():
    fpath = find_file("pyproject.toml")
    if not fpath:
        return []
    
    deps = []
    try:
        with open(fpath, "r", encoding="utf-8") as f:
            for line in f:
                # Very basic parsing for [project] dependencies or [tool.poetry.dependencies]
                # Just looking for lines that look like "name = ..." or "name>=..." inside blocks
                # This isn't a full TOML parser but good enough for discovery
                clean = line.strip().replace('"', "").replace("'", "")
                if "=" in clean or ">" in clean or "<" in clean:
                    # heuristic: likely a dep
                    parts = clean.split("=")
                    if len(parts) > 0 and len(parts[0].strip()) > 0 and not parts[0].startswith("["):
                         deps.append(parts[0].strip())
                elif clean and not clean.startswith("[") and not clean.startswith("#"):
                     # might be a list item
                     deps.append(clean.strip(","))
        return deps
    except Exception:
        return []

def print_backend_summary(py_deps, toml_deps):
    print("--- Backend (requirements.txt / pyproject.toml) ---")
    all_deps = list(set((py_deps or []) + (toml_deps or [])))
    
    if all_deps:
        # filter for interesting ones
        keys = ["fastapi", "flask", "django", "pydantic", "google-generativeai", "uvicorn", "docker"]
        found = [d for d in all_deps if any(k in d.lower() for k in keys)]
        if found:
            for d in found:
                print(f"  - {d}")
        else:
            print("  (No major libs detected)")
    else:
        print("  (No requirements.txt or pyproject.toml deps found)")
    print(f"  Total libs detected: {len(all_deps)}")
    print("")

def main():
    print("🔍 Starting Deep Discovery...\n")
    
    print_frontend_summary(scan_package_json())
    print_backend_summary(scan_requirements(), scan_project_toml())

    # Infra
    print("--- Infrastructure ---")
    base_image = scan_docker()
    if base_image:
        print(f"  - Base Image: {base_image}")
    else:
        print("  (No Dockerfile found)")
    
    print("\n✅ Deep Discovery Complete. Use these insights to check `patterns/` directory.")

if __name__ == "__main__":
    main()
