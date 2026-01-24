
import json
import sys
from pathlib import Path

def main():
    if len(sys.argv) < 2:
        print("Usage: python advance_worklist.py <num_files>")
        return

    num_files = int(sys.argv[1])
    worklist_path = Path(".agent/docstring_worklist.json")
    
    if not worklist_path.exists():
        print("Worklist not found")
        return

    data = json.loads(worklist_path.read_text(encoding='utf-8'))
    
    pending = data.get("pending", [])
    completed = data.get("completed", [])
    
    if not pending:
        print("No pending files.")
        return

    to_move = pending[:num_files]
    remaining = pending[num_files:]
    
    data["pending"] = remaining
    data["completed"] = completed + to_move
    
    worklist_path.write_text(json.dumps(data, indent=2), encoding='utf-8')
    print(f"Moved {len(to_move)} files to completed. Remaining: {len(remaining)}")

if __name__ == "__main__":
    main()
