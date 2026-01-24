"""
Unit tests for Agent Structure verification.
"""
import os
from pathlib import Path

def test_base_agent_structure() -> None:
    """Verify Base Agent has required files."""
    base_agent_dir = Path("agents/base_agent")
    
    assert (base_agent_dir / "agent.yaml").exists(), "agent.yaml missing"
    assert (base_agent_dir / "tools.py").exists(), "tools.py missing"
    assert (base_agent_dir / "README.md").exists(), "README.md missing"
