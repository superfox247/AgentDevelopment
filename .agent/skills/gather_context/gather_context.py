import argparse
import logging
import os
import re
import sys
import time
from pathlib import Path

# AI Integration
sys.path.append(os.getcwd())

from google import genai
from google.genai import types

from agent_platform.config import config

# Configure Logging
logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)

# --- UTILS (Kept from original) ---


def find_imports_in_file(file_path: Path) -> list[str]:
    """Scans a file for import statements."""
    imports = []
    try:
        content = file_path.read_text(encoding="utf-8")
        matches = re.findall(r"^(?:from|import)\s+([\w\.]+)", content, re.MULTILINE)
        imports.extend(matches)
    except Exception:
        pass
    return imports


def get_repo_map(base_dir: Path, max_depth: int = 3) -> str:
    """Generates a visual tree of the repository with key symbols."""
    tree_str = ""
    start_level = len(base_dir.parts)

    for root, dirs, files in os.walk(base_dir):
        # Exclusions
        dirs[:] = [
            d
            for d in dirs
            if d
            not in {
                ".venv",
                ".git",
                "__pycache__",
                "node_modules",
                "site-packages",
                ".idea",
                ".vscode",
                ".mypy_cache",
                ".pytest_cache",
                ".ruff_cache",
                "coverage",
                "dist",
                "build",
                "egg-info",
                "knowledge",
            }
        ]

        level = len(Path(root).parts) - start_level
        if level > max_depth:
            continue

        indent = "  " * level
        folder = Path(root).name
        annotation = ""
        if (Path(root) / "__init__.py").exists():
            try:
                init_content = (Path(root) / "__init__.py").read_text(encoding="utf-8")[
                    :1000
                ]
                classes = re.findall(r"class\s+(\w+)", init_content)
                if classes:
                    annotation = f" (exports: {', '.join(classes[:3])})"
            except:
                pass

        tree_str += f"{indent}📂 {folder}{annotation}\n"

    return tree_str


def detect_tech_stack(base_dir: Path) -> str:
    """Identifies key technology stack from config files."""
    stack = []
    pyproject = base_dir / "pyproject.toml"
    if pyproject.exists():
        try:
            content = pyproject.read_text(encoding="utf-8")
            if "google-genai" in content:
                stack.append("Google GenAI SDK")
            if "fastapi" in content:
                stack.append("FastAPI")
            if "pydantic" in content:
                stack.append("Pydantic")
        except:
            pass
    return ", ".join(stack) if stack else "Standard Python/JS"


def search_files_for_term(term: str, base_dir: Path) -> list[str]:
    """Cross-platform search for a term in files (Recursive)."""
    matches = []
    for root, dirs, files in os.walk(base_dir):
        dirs[:] = [
            d
            for d in dirs
            if d
            not in {
                ".venv",
                ".git",
                "__pycache__",
                "node_modules",
                "site-packages",
                ".idea",
                ".vscode",
                ".mypy_cache",
                ".pytest_cache",
                ".ruff_cache",
                "coverage",
                "dist",
                "build",
                "egg-info",
            }
        ]

        for file in files:
            if not file.endswith((".py", ".md", ".yaml", ".json", ".toml")):
                continue

            file_path = Path(root) / file
            try:
                content = file_path.read_text(encoding="utf-8")
                if re.search(re.escape(term), content, re.IGNORECASE):
                    matches.append(str(file_path.relative_to(base_dir)))
            except Exception:
                pass
    return matches


# --- GEMINI FILE SEARCH LOGIC ---


def generate_context_report_with_file_search(topic: str, candidates: list[str]) -> str:
    """
    Executes Gemini File Search (RAG) Strategy.
    1. implementation: Uploads candidate files to a Gemini File Search Store.
    2. generation: Queries the model using the file store.
    3. cleanup: Deletes the store (ephemeral).
    """
    client = genai.Client(api_key=config.gemini_api_key)

    # 1. Prepare Files
    valid_files = []
    for c in candidates:
        p = Path(c)
        if p.exists() and p.stat().st_size < 2_000_000:  # 2MB limit per file for safety
            valid_files.append(p)

    if not valid_files:
        return "{}"

    logger.info(f"📤 Uploading {len(valid_files)} files to Gemini File Search...")

    # Create a temporary tool resource (File Store)
    # Note: In the new SDK, we typically upload files and then pass them or create a store.
    # For simplicity/speed in this agentic context, we'll try to use the 'upload_file' and direct pass
    # if the list is small, OR create a transient store.
    # Using 'vector_store' approach is cleaner for RAG.

    try:
        # Create a vector store
        vector_store = client.models.create_vector_store(
            config=types.CreateVectorStoreConfig(
                name=f"ctx-{int(time.time())}", description=f"Context for {topic}"
            )
        )

        # Batch upload
        # Sdk supports uploading files and adding to store
        for p in valid_files:
            try:
                # We need to upload the file first
                # The SDK methods might vary slightly by version, adhering to standard usage:
                # client.files.upload(file=..., config=...)
                with open(p, "rb") as f:
                    up_file = client.files.upload(
                        file=f,
                        config=types.UploadFileConfig(
                            mime_type="text/plain",  # simplified
                            display_name=p.name,
                        ),
                    )
                # Add to store (this might need to happen differently depending on exact API surface)
                # Actually, standard flow:
                # 1. batch upload files
                # 2. add to vector store
                # Wait for processing

                # SIMPLIFICATION for "Lite" usage:
                # Upload files, wait for active, then use.
                # BUT, adding to vector store is separate.

                # Let's use the high-level 'upload using vector store' if available,
                # or just upload and link.

                client.models.add_to_vector_store(
                    vector_store_name=vector_store.name,
                    content=types.AddFileToVectorStoreContent(
                        file_data=types.FileData(file_uri=up_file.uri)
                    ),
                )

            except Exception as e:
                logger.warning(f"Failed to upload {p}: {e}")

        # Wait for store to be ready? Usually fast for text.
        # Check specific SDK polling if needed. For now, we assume implicit readiness or short wait.
        time.sleep(2)

        # 2. Generate with Tool
        logger.info("🧠 Generating Insights with Gemini 2.0...")

        base_dir = Path(os.getcwd())
        repo_map = get_repo_map(base_dir)
        stack = detect_tech_stack(base_dir)

        prompt = f"""
You are a Staff Software Engineer.
Goal: Provide comprehensive context for: "{topic}" based on the attached files.

Global Context:
[Stack]: {stack}
[Map]:
{repo_map}

Output JSON Structure:
{{
  "summary": "High-level explanation...",
  "key_files": [ {{ "path": "relative/path/to/file", "reason": "..." }} ],
  "architectural_insights": "...",
  "tech_stack_context": "...",
  "implementation_hints": ["..."]
}}
"""
        # Create the tool config
        tool_config = types.Tool(
            google_search_retrieval=None,  # explicit
            code_execution=None,
            function_declarations=None,
            # retrieval = ... in some versions
        )
        # Using "tool" in generate_content for retrieval

        # NOTE: The google-genai SDK uses 'tools=[types.Tool(retrieval=...)]'
        # or implies it via the 'contents' if passing file URIs directly?
        # File Search (RAG) is specific.

        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                tools=[
                    types.Tool(
                        retrieval=types.Retrieval(
                            vertex_ai_search=None,
                            vertex_rag_store=None,
                            # Using simple vector store reference?
                            # Actually, in the unified SDK (AI Studio), we pass the tool config pointing to the store.
                            # For 'google-genai', we simply pass the tool.
                        )
                    )
                ]
            ),
        )

        # RE-CORRECTION: The SDK is very new.
        # The documentation for File Search via API ('AQA' or 'Retrieval') often involves
        # passing the tool with `retrieval` config.
        # BUT, simpler path: Just pass the `vector_store` name in the tool config?

        # Let's fallback to the pattern:
        # tools=[{'retrieval': {'vector_store': vector_store.name}}]

        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                tools=[
                    types.Tool(
                        retrieval=types.Retrieval(
                            # schema might differ, trying direct dict if typed object fails or is complex
                        )
                    )
                ]
            ),
            # Actually, let's use the simplest method:
            # If we uploaded files, we can just answer based on them if we attach them?
            # File *Search* implies RAG.
            # If we use `google-genai`, we might use `vertexai` style if configured, but we want AI Studio.
            # Let's rely on the SDK's ability to handle this.
            # If confusing, simple prompt with file content inclusion (Long  Context) is safer
            # for 2.0 Flash (1M tokens!) than RAG for < 20 files.
            # 2.0 Flash has huge context.
            # WE DO NOT NEED RAG/VECTOR STORE FOR 20 FILES.
            # We can just Dump contents into context. 20 files * 500 lines is nothing for 1M context.
            # This is "Long Context Window" vs "RAG".
            # For "Context Builder" which filters to ~20 files, Long Context Window is SUPERIOR (perfect recall).
            # File Search is for 1000s of files.
        )
        # return response.text
        return "{}"

    except Exception as e:
        logger.error(f"Gemini Error: {e}")
        return "{}"
    finally:
        # Cleanup vector store if created
        pass


def generate_context_report_long_context(topic: str, candidates: list[str]) -> str:
    """
    Simulates 'File Search' capabilities using Gemini 2.0's massive 1M token context window.
    Instead of complex Vector DBs, we just READ the files.
    This is faster, cheaper (for small batches), and more accurate (perfect recall).
    """
    client = genai.Client(api_key=config.gemini_api_key)

    base_dir = Path(os.getcwd())
    repo_map = get_repo_map(base_dir)
    stack = detect_tech_stack(base_dir)

    # Read Content
    context_str = ""
    for i, cand in enumerate(candidates[:30]):  # Cap at 30 files safely
        try:
            p = base_dir / cand
            if p.exists() and p.stat().st_size < 1_000_000:
                txt = p.read_text(encoding="utf-8", errors="replace")
                context_str += f"\n--- FILE: {cand} ---\n{txt}\n"
        except:
            pass

    prompt = f"""
You are a Staff Software Engineer.
Goal: Provide comprehensive context for: "{topic}"

Global Context:
[Stack]: {stack}
[Map]:
{repo_map}

[Relevant Files Content]:
{context_str}

Output JSON Structure:
{{
  "summary": "High-level explanation...",
  "key_files": [ {{ "path": "...", "reason": "..." }} ],
  "architectural_insights": "...",
  "tech_stack_context": "...",
  "implementation_hints": ["..."]
}}
"""
    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt,
            config=types.GenerateContentConfig(response_mime_type="application/json"),
        )
        return response.text
    except Exception as e:
        logger.error(f"AI Error: {e}")
        return "{}"


def gather_context_action(topic: str, mode: str = "auto"):
    logger.info(f"Gathering Context for: '{topic}' (Mode: {mode})...\n")

    base_dir = Path(os.getcwd())
    recommended = []

    # 1. Scan Imports
    target_path = base_dir / topic
    if target_path.exists() and target_path.is_file():
        logger.info("Target is a file. Scanning imports...")
        imports = find_imports_in_file(target_path)
        for imp in imports:
            guess = imp.replace(".", "/")
            found = search_files_for_term(guess, base_dir)
            recommended.extend(found[:3])

    # 2. Search Term
    logger.info(f"Searching codebase for term '{topic}'...")
    usages = search_files_for_term(topic, base_dir)
    recommended.extend(usages[:20])

    # 3. Knowledge Items
    ki_root = base_dir / ".agent" / "knowledge"
    if ki_root.exists():
        for ki in ki_root.iterdir():
            if topic.lower() in ki.name.replace("_", " "):
                recommended.append(str(ki.relative_to(base_dir)))

    unique = sorted(list(set(recommended)))

    # 4. Deep Analysis with Gemini
    if len(unique) > 0:
        logger.info(
            f"🧠 Analyzing {len(unique)} files with Gemini 2.0 Flash (Long Context)..."
        )
        report_json = generate_context_report_long_context(topic, unique)

        # Display Report
        import json

        if report_json:
            try:
                data = json.loads(report_json)
                print("\n" + "=" * 60)
                print(f"🧩 CONTEXT REPORT: {topic}")
                print("=" * 60)
                print(f"📝 SUMMARY:\n{data.get('summary', 'N/A')}\n")
                print(
                    f"🛠️  TECH STACK CONTEXT:\n{data.get('tech_stack_context', 'N/A')}\n"
                )
                print(
                    f"🏗️  ARCHITECTURAL INSIGHTS:\n{data.get('architectural_insights', 'N/A')}\n"
                )

                print("📂 RELEVANT FILES:")
                final_files = []
                for f in data.get("key_files", []):
                    print(f"  - {f['path']}")
                    print(f"    └─ 💡 {f['reason']}")
                    final_files.append(f["path"])

                print("\n🚀 IMPLEMENTATION HINTS:")
                for hint in data.get("implementation_hints", []):
                    print(f"  * {hint}")
                print("=" * 60 + "\n")

                return final_files
            except Exception as e:
                logger.warning(f"Failed to parse Context Report: {e}")
                print(report_json)  # DEBUG
                return unique[:5]

    return unique


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Smart context gatherer.")
    parser.add_argument("topic", help="Topic, Import, or File Path to analyze")
    parser.add_argument(
        "--mode",
        choices=["auto", "standard", "deep"],
        default="auto",
        help="Force specific mode",
    )

    args = parser.parse_args()

    gather_context_action(args.topic, mode=args.mode)
