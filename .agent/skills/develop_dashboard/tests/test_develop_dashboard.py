import pytest
from pathlib import Path
import subprocess

def test_develop_dashboard_script_exists():
    script_path = Path(__file__).parent.parent / "develop_dashboard.py"
    assert script_path.exists()

def test_develop_dashboard_help():
    script_path = Path(__file__).parent.parent / "develop_dashboard.py"
    result = subprocess.run(
        ["uv", "run", str(script_path), "--help"],
        capture_output=True,
        text=True
    )
    assert result.returncode == 0
