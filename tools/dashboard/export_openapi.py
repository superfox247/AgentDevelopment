
import json
import os
import sys
from pathlib import Path

# Ensure root is in path
ROOT_DIR = Path(__file__).parent.parent.parent
sys.path.append(str(ROOT_DIR))

from tools.dashboard.server import app

def export_openapi():
    """Exports the OpenAPI schema to openapi.json in the dashboard directory."""
    print("Exporting OpenAPI schema...")
    
    # Generate JSON
    openapi_data = app.openapi()
    
    # Define output path
    output_path = Path(__file__).parent / "openapi.json"
    
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(openapi_data, f, indent=2)
        
    print(f"✅ Schema exported to: {output_path}")

if __name__ == "__main__":
    export_openapi()
