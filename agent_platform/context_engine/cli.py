"""
CLI tool for managing the Context Engine.
"""

import argparse
import logging
import sys

from agent_platform.context_engine.hybrid import ContextEngine

# Configure logging for CLI
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser(description="Context Engine CLI")
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # Add Concept
    add_parser = subparsers.add_parser("add", help="Add a concept")
    add_parser.add_argument("--name", required=True, help="Name of the concept")
    add_parser.add_argument("--desc", required=True, help="Description/Content")

    # Search
    search_parser = subparsers.add_parser("search", help="Search concepts")
    search_parser.add_argument("query", help="Query string")

    # Wipe
    subparsers.add_parser("wipe", help="Wipe all data")
    
    # Init
    subparsers.add_parser("init", help="Initialize databases")

    # Ingest
    ingest_parser = subparsers.add_parser("ingest", help="Ingest a directory")
    ingest_parser.add_argument("path", help="Path to directory")

    # Stats Command
    subparsers.add_parser("stats", help="Show database statistics")

    # Analyze
    analyze_parser = subparsers.add_parser("analyze", help="Analyze codebase with Gemini Context Caching")
    analyze_parser.add_argument("prompt", help="Question to ask")
    analyze_parser.add_argument("--path", default=".", help="Root directory to analyze")

    args = parser.parse_args()

    try:
        engine = ContextEngine()
        
        if args.command == "init":
            run_init(engine)
        elif args.command == "add":
            run_add(engine, args)
        elif args.command == "search":
            run_search(engine, args)
        elif args.command == "wipe":
            run_wipe(engine)
        elif args.command == "ingest":
            run_ingest(engine, args)
        elif args.command == "analyze":
            run_analyze(engine, args)
        elif args.command == "stats":
            run_stats(engine)
        else:
            parser.print_help()

    except Exception as e:
        logger.error(f"Error: {e}")
        sys.exit(1)

def run_init(engine):
    engine.initialize()
    print("Initialized Context Engine.")

def run_add(engine, args):
    cid = engine.add_concept(args.name, args.desc)
    print(f"Added concept {cid}")

def run_search(engine, args):
    results = engine.search_concepts(args.query)
    print(f"Found {len(results)} results:")
    for r in results:
        print(f"[{r['score']:.4f}] {r['name']} (ID: {r['id']})")
        print(f"  Desc: {r['description']}")
        print(f"  Graph: {r.get('graph_props', {})}")
        print("-" * 40)

def run_wipe(engine):
    confirm = input("Are you sure you want to WIPE EVERYTHING? (y/n): ")
    if confirm.lower() == 'y':
        engine.wipe_all()
        print("Wiped all data.")
    else:
        print("Aborted.")

def run_ingest(engine, args):
    engine.initialize()
    import os
    import hashlib
    from agent_platform.context_engine.chunker import ChunkerFactory

    root_dir = args.path
    print(f"Ingesting codebase from: {root_dir}")
    
    count = 0
    skipped = 0
    
    # Walk and Chunk
    for dirpath, dirnames, filenames in os.walk(root_dir):
        # Common noisy directories to ignore
        ignore_dirs = {
            '.venv', '.git', '__pycache__', 'node_modules', 
            'build', 'dist', 'coverage', '.pytest_cache', 
            '.next', 'out', 'site-packages', 'venv'
        }
        dirnames[:] = [d for d in dirnames if d not in ignore_dirs]
        
        if any(x in dirpath for x in ignore_dirs):
            continue

        for filename in filenames:
            if filename.endswith(('.py', '.md')):
                filepath = os.path.join(dirpath, filename)
                rel_path = os.path.relpath(filepath, root_dir)
                
                try:
                    process_file(engine, filepath, rel_path, filename, ChunkerFactory)
                    # We can't really track counts easily in this extracted method without passing a mutable counter or refactoring more.
                    # For simplicity, let's keep the count/skipped here or simplify.
                    # Actually, process_file would return (processed, skipped) bools.
                    # But to keep this refactor simple and safe: I will inline the processing logic in run_ingest OR make process_file return ints.
                except Exception as e:
                    logger.error(f"Failed to ingest {rel_path}: {e}")

def process_file(engine, filepath, rel_path, filename, ChunkerFactory):
    import hashlib
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 1. Incremental Check
    current_hash = hashlib.md5(content.encode()).hexdigest()
    stored_hash = engine.get_file_hash(rel_path)
    
    if stored_hash == current_hash:
        return 0, 1 # count=0, skipped=1

    # 2. Chunking
    chunker = ChunkerFactory.get_chunker(filename)
    chunks = chunker.chunk(content, rel_path)
    
    for chunk in chunks:
        # Use the deterministic ID from the chunker
        eng_metadata = chunk.metadata.copy()
        eng_metadata["chunk_type"] = eng_metadata.get("type", "unknown")
        
        engine.add_concept(
            name=f"{rel_path}:{chunk.metadata.get('name', 'uknown')}", 
            description=chunk.content,
            metadata=eng_metadata,
            concept_id=chunk.id
        )
        print(f" {chunk.metadata.get('type'):<8} | {rel_path}:{chunk.metadata.get('name')} -> {chunk.id[:8]}...")
    
    # 3. Update File Hash
    engine.update_file_hash(rel_path, current_hash)
    return len(chunks), 0

def run_ingest(engine, args):
    # Re-implementing with clearer structure
    engine.initialize()
    import os
    from agent_platform.context_engine.chunker import ChunkerFactory

    root_dir = args.path
    print(f"Ingesting codebase from: {root_dir}")
    
    total_upserted = 0
    total_skipped = 0
    
    for dirpath, dirnames, filenames in os.walk(root_dir):
        ignore_dirs = {
            '.venv', '.git', '__pycache__', 'node_modules', 
            'build', 'dist', 'coverage', '.pytest_cache', 
            '.next', 'out', 'site-packages', 'venv'
        }
        dirnames[:] = [d for d in dirnames if d not in ignore_dirs]
        
        if any(x in dirpath for x in ignore_dirs):
            continue

        for filename in filenames:
            if filename.endswith(('.py', '.md')):
                filepath = os.path.join(dirpath, filename)
                rel_path = os.path.relpath(filepath, root_dir)
                try:
                    upserted, skipped = process_file(engine, filepath, rel_path, filename, ChunkerFactory)
                    total_upserted += upserted
                    total_skipped += skipped
                except Exception as e:
                    logger.error(f"Failed to ingest {rel_path}: {e}")

    print(f"Ingestion complete. Upserted {total_upserted} chunks. Skipped {total_skipped} unchanged files.")


def run_analyze(engine, args):
    prompt = args.prompt
    import os
    from agent_platform.context_engine.google_client import GoogleClient
    google_client = GoogleClient()
    
    root_dir = args.path
    print(f"Analysing repo: {root_dir}...")
    
    full_content = []
    for dirpath, dirnames, filenames in os.walk(root_dir):
        ignore_dirs = {
            '.venv', '.git', '__pycache__', 'node_modules', 
            'build', 'dist', 'coverage', '.pytest_cache', 
            '.next', 'out', 'site-packages', 'venv'
        }
        dirnames[:] = [d for d in dirnames if d not in ignore_dirs]
        
        if any(x in dirpath for x in ignore_dirs):
            continue

        for filename in filenames:
            if filename.endswith(('.py', '.md')):
                filepath = os.path.join(dirpath, filename)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        full_content.append(f"--- File: {filepath} ---\n{f.read()}\n")
                except: pass
    
    repo_text = "\n".join(full_content)
    print(f"Total context size: {len(repo_text)} chars")
    
    try:
        cache_model = "models/gemini-2.5-flash" 
        
        cache = google_client.create_cache(
            cache_name="agent_platform_cache",
            content=repo_text,
            ttl_minutes=5,
            model_name=cache_model
        )
        print(f"Cache created: {cache.name} using {cache_model}")
        
        print("Generating analysis...")
        result_text = google_client.generate_with_cache(cache.name, prompt, model_name=cache_model)
        
        print("\n--- Analysis Result ---")
        print(result_text)
        print("-----------------------")
    except Exception as e:
        print(f"\n[WARNING] Context Caching failed: {e}")
        print("Possible causes: Content too short (min 32k tokens), Model not available, or API Key permissions.")

def run_stats(engine):
    print("\n--- Context Engine Statistics ---")
    stats = engine.get_stats()
    
    print(f"Graph Database (Neo4j):")
    g_stats = stats.get("graph", {})
    print(f"  Total Nodes: {g_stats.get('total_nodes', 'N/A')}")
    for label, count in g_stats.get("breakdown", {}).items():
        print(f"  - {label}: {count}")
        
    print(f"\nVector Database (Qdrant):")
    v_stats = stats.get("vector", {})
    print(f"  Total Vectors: {v_stats.get('total_vectors', 'N/A')}")
    print(f"  Collection Status: {v_stats.get('status', 'N/A')}")
    print(f"  Vector Size: {v_stats.get('vector_size', 'N/A')}")
    print("---------------------------------")


if __name__ == "__main__":
    main()
