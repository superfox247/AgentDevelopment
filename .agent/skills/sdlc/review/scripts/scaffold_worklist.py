import json
import os
from pathlib import Path


def get_python_files(root_dir):
    py_files = []
    # Exclude standard junk + the script itself
    exclude_dirs = {
        ".venv",
        ".git",
        ".mypy_cache",
        ".ruff_cache",
        "__pycache__",
        "site-packages",
        "node_modules",
        ".agent",
    }

    for root, dirs, files in os.walk(root_dir):
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        for file in files:
            if file.endswith(".py") and file != "scaffold_worklist.py":
                full_path = Path(root) / file
                # Use absolute paths for the agent's convenience
                py_files.append(str(full_path.absolute()))
    return py_files


def main():
    root = Path(".")
    files = get_python_files(root)
    worklist = {"pending": files, "completed": [], "failed": []}

    # Save to a temporary location
    output_path = Path(".agent/docstring_worklist.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)

    output_path.write_text(json.dumps(worklist, indent=2), encoding="utf-8")
    print(f"Generated worklist with {len(files)} files at {output_path}")


if __name__ == "__main__":
    main()
