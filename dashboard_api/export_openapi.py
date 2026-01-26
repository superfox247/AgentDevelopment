"""
OpenAPI Export Utility.

Generates the `openapi.json` file from the Dashboard FastAPI application
for use in frontend client generation or documentation.
"""

import json
import sys
from pathlib import Path

# Ensure root is in path
ROOT_DIR = Path(__file__).parent.parent
sys.path.append(str(ROOT_DIR))

from dashboard_api.server import app  # noqa: E402


def export_openapi() -> None:
    """Exports the OpenAPI schema to openapi.json in the dashboard_api directory."""
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
