import ast
import os
from pathlib import Path
from typing import NamedTuple

"""
Complexity Scanner.

Scans the codebase for functions and methods with high Cyclomatic Complexity.
Uses a simplified AST-based calculation:
Start = 1
+1 for every If, For, AsyncFor, While, Try, ExceptHandler, With, AsyncWith
+1 for every BoolOp (and/or) in conditions? (Simplified: just control flow structures usually)

Actually, for Cognitive Complexity, it's more nuanced, but McCabe is a good proxy.
We will count: If, For, AsyncFor, While, ExceptHandler.
"""

class FunctionComplexity(NamedTuple):
    name: str
    complexity: int
    lineno: int
    path: str

def get_complexity(node: ast.AST) -> int:
    complexity = 1
    for child in ast.walk(node):
        if isinstance(child, (ast.If, ast.While, ast.For, ast.AsyncFor, ast.ExceptHandler)):
            complexity += 1
        elif isinstance(child, ast.BoolOp):
            # Each boolean operator adds a decision point roughly
            complexity += len(child.values) - 1
    return complexity

def scan_file(path: Path, threshold: int = 10) -> list[FunctionComplexity]:
    try:
        source = path.read_text(encoding="utf-8")
        tree = ast.parse(source)
    except Exception:
        # print(f"Error parsing {path}: {e}")
        return []

    results = []

    # Check top-level functions and class methods
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            cc = get_complexity(node)
            if cc >= threshold:
                results.append(FunctionComplexity(
                    name=node.name,
                    complexity=cc,
                    lineno=node.lineno,
                    path=str(path)
                ))
    return results

def main():
    root_dir = Path(".")
    threshold = 10

    print(f"🔎 Scanning for Cyclomatic Complexity >= {threshold}...")
    print(f"{'Complexity':<10} | {'Location':<60} | {'Name'}")
    print("-" * 100)

    high_complexity_files = []

    for root, dirs, files in os.walk(root_dir):
        # Skip venv, .git, etc.
        if ".venv" in dirs:
            dirs.remove(".venv")
        if ".git" in dirs:
            dirs.remove(".git")
        if "__pycache__" in dirs:
            dirs.remove("__pycache__")

        for file in files:
            if file.endswith(".py"):
                path = Path(root) / file
                issues = scan_file(path, threshold)
                for issue in issues:
                    path_str = f"{issue.path}:{issue.lineno}"
                    print(f"{issue.complexity:<10} | {path_str:<60} | {issue.name}")
                    high_complexity_files.append(issue)

    print("-" * 100)
    print(f"Found {len(high_complexity_files)} functions exceeding threshold.")

if __name__ == "__main__":
    main()
