
import os

"""
Docstring Audit Script.

Randomly samples Python files from the codebase to verify the presence
of Module, Class, and Function docstrings.
"""
import ast
import random
from pathlib import Path


def get_python_files(root_dir):
    py_files = []
    exclude_dirs = {'.venv', '.git', '.mypy_cache', '.ruff_cache', '__pycache__', 'site-packages', 'node_modules'}

    for root, dirs, files in os.walk(root_dir):
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        for file in files:
            if file.endswith('.py'):
                py_files.append(Path(root) / file)
    return py_files

def audit_file(file_path):
    try:
        content = file_path.read_text(encoding='utf-8')
        tree = ast.parse(content)
    except Exception as e:
        return {"error": str(e), "path": str(file_path)}

    module_docstring = ast.get_docstring(tree) is not None

    functions = [n for n in ast.walk(tree) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]
    classes = [n for n in ast.walk(tree) if isinstance(n, ast.ClassDef)]

    func_docs = sum(1 for f in functions if ast.get_docstring(f) is not None)
    class_docs = sum(1 for c in classes if ast.get_docstring(c) is not None)

    return {
        "path": str(file_path),
        "module_doc": module_docstring,
        "total_funcs": len(functions),
        "documented_funcs": func_docs,
        "total_classes": len(classes),
        "documented_classes": class_docs,
    }

def main():
    root = Path(".")
    all_files = get_python_files(root)

    sample_size = min(50, len(all_files))
    sampled_files = random.sample(all_files, sample_size)

    results = []
    print(f"Auditing {sample_size} random files...\n")
    print(f"{'File':<60} | {'Mod':<3} | {'Class':<5} | {'Func':<5}")
    print("-" * 85)

    total_funcs = 0
    total_documented_funcs = 0
    total_classes = 0
    total_documented_classes = 0
    missing_module_docs = 0

    for file_path in sampled_files:
        res = audit_file(file_path)
        if "error" in res:
            print(f"{file_path.relative_to(root)!s:<60} | ERROR: {res['error']}")
            continue

        results.append(res)

        # Stats
        total_funcs += res['total_funcs']
        total_documented_funcs += res['documented_funcs']
        total_classes += res['total_classes']
        total_documented_classes += res['documented_classes']
        if not res['module_doc']:
            missing_module_docs += 1

        # Display
        rel_path = str(Path(res['path']).relative_to(root))
        if len(rel_path) > 59:
            rel_path = "..." + rel_path[-56:]

        mod_mark = "✅" if res['module_doc'] else "❌"
        class_stats = f"{res['documented_classes']}/{res['total_classes']}" if res['total_classes'] > 0 else "-"
        func_stats = f"{res['documented_funcs']}/{res['total_funcs']}" if res['total_funcs'] > 0 else "-"

        print(f"{rel_path:<60} | {mod_mark:<3} | {class_stats:<5} | {func_stats:<5}")

    # Summary
    print("\n" + "=" * 85)
    print(f"Summary for {len(results)} files:")
    print(f"Module Docstring Coverage: {len(results) - missing_module_docs}/{len(results)} ({((len(results) - missing_module_docs)/len(results))*100:.1f}%)")

    if total_classes > 0:
        print(f"Class Docstring Coverage:  {total_documented_classes}/{total_classes} ({(total_documented_classes/total_classes)*100:.1f}%)")
    else:
        print("Class Docstring Coverage:  N/A (No classes found)")

    if total_funcs > 0:
        print(f"Func Docstring Coverage:   {total_documented_funcs}/{total_funcs} ({(total_documented_funcs/total_funcs)*100:.1f}%)")
    else:
        print("Func Docstring Coverage:   N/A (No functions found)")

if __name__ == "__main__":
    main()
