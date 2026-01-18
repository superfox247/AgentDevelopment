import json
import os
import argparse
from datetime import datetime, timezone
from pathlib import Path

# Constants
SKILL_DIR = Path(__file__).parent.parent
DATA_DIR = SKILL_DIR / "data"
AUDIT_FILE = DATA_DIR / "review_audit.json"

class ReviewTracker:
    def __init__(self):
        self._ensure_data_dir()
        self.data = self._load_data()

    def _ensure_data_dir(self):
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        if not AUDIT_FILE.exists():
            with open(AUDIT_FILE, "w") as f:
                json.dump({"reviews": {}}, f, indent=2)

    def _load_data(self):
        try:
            with open(AUDIT_FILE, "r") as f:
                return json.load(f)
        except json.JSONDecodeError:
            return {"reviews": {}}

    def _save_data(self):
        with open(AUDIT_FILE, "w") as f:
            json.dump(self.data, f, indent=2)

    def log_review(self, file_path: str, status: str, notes: str = "", reviewer: str = "Antigravity"):
        """Logs a review event for a specific file."""
        abs_path = str(Path(file_path).resolve())
        timestamp = datetime.now(timezone.utc).isoformat()
        
        if abs_path not in self.data["reviews"]:
            self.data["reviews"][abs_path] = []

        entry = {
            "timestamp": timestamp,
            "status": status,
            "notes": notes,
            "reviewer": reviewer
        }
        
        self.data["reviews"][abs_path].append(entry)
        # Sort by timestamp desc just in case
        self.data["reviews"][abs_path].sort(key=lambda x: x["timestamp"], reverse=True)
        
        self._save_data()
        print(f"✅ Logged review for {os.path.basename(file_path)}: {status}")

    def get_last_review(self, file_path: str):
        """Returns the last review entry for a file."""
        abs_path = str(Path(file_path).resolve())
        if abs_path in self.data["reviews"] and self.data["reviews"][abs_path]:
            return self.data["reviews"][abs_path][0]
        return None

    def list_recent(self, limit=5):
        """Lists the most recent reviews across all files."""
        all_reviews = []
        for fpath, reviews in self.data["reviews"].items():
            for r in reviews:
                r_copy = r.copy()
                r_copy["file"] = fpath
                all_reviews.append(r_copy)
        
        all_reviews.sort(key=lambda x: x["timestamp"], reverse=True)
        return all_reviews[:limit]

def main():
    parser = argparse.ArgumentParser(description="Track code reviews.")
    subparsers = parser.add_subparsers(dest="command")

    # Log Command
    log_parser = subparsers.add_parser("log", help="Log a new review")
    log_parser.add_argument("--file", required=True, help="Path to the reviewed file")
    log_parser.add_argument("--status", required=True, choices=["PASSED", "FAILED", "WARNING"], help="Review status")
    log_parser.add_argument("--notes", default="", help="Optional notes")

    # Get Command
    get_parser = subparsers.add_parser("get", help="Get last review for a file")
    get_parser.add_argument("--file", required=True, help="Path to the file")

    # List Command
    list_parser = subparsers.add_parser("list", help="List recent reviews")
    list_parser.add_argument("--limit", type=int, default=5, help="Number of reviews to show")

    args = parser.parse_args()
    tracker = ReviewTracker()

    if args.command == "log":
        tracker.log_review(args.file, args.status, args.notes)
    elif args.command == "get":
        last = tracker.get_last_review(args.file)
        if last:
            print(json.dumps(last, indent=2))
        else:
            print("No reviews found.")
    elif args.command == "list":
        recent = tracker.list_recent(args.limit)
        print(json.dumps(recent, indent=2))
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
