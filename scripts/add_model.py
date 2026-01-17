import argparse
import os
from pathlib import Path

def add_model(name: str, fields: list[str], target_file: str = "registry/models/protocol.py"):
    """
    Appends a new Pydantic model to the target file.
    
    Args:
        name: Name of the model.
        fields: List of strings in format "name:type:description".
        target_file: Relative path to the file to modify.
    """
    base_dir = Path(os.getcwd())
    file_path = base_dir / target_file
    
    if not file_path.exists():
        print(f"Error: Target file not found: {file_path}")
        return

    # Build field definitions
    field_lines = []
    for field_def in fields:
        parts = field_def.split(":")
        if len(parts) < 3:
            print(f"Warning: Invalid field format '{field_def}'. Expected 'name:type:description'. Skipping.")
            continue
            
import sys

MODEL_TEMPLATE = """
class {name}(BaseModel):
    \"\"\"
    {description}
    
    Heuristics: {heuristics}
    Verification: {verification}
    \"\"\"
    # TODO: Define fields
    # field_name: str = Field(..., description="...")
    pass
"""

def add_model(name: str, description: str, heuristics: str, verification: str):
    """
    Adds a new Pydantic model to the protocol.py file with docstring injection
    for description, heuristics, and verification.
    
    Args:
        name: Name of the model (will be converted to TitleCase).
        description: Main description for the model's docstring.
        heuristics: Heuristics/Cognitive Policy for the model.
        verification: Verification Logic for the model.
    """
    # Ensure TitleCase
    name = name[0].upper() + name[1:]
    
    protocol_path = Path("registry/models/protocol.py")
    if not protocol_path.exists():
        print(f"Error: {protocol_path} not found.")
        sys.exit(1)
        
    content = protocol_path.read_text(encoding="utf-8")
    
    if f"class {name}" in content:
        print(f"Error: Model '{name}' already exists.")
        sys.exit(1)
        
    new_model = MODEL_TEMPLATE.format(
        name=name, 
        description=description,
        heuristics=heuristics,
        verification=verification
    )
    
    with open(protocol_path, "a") as f:
        f.write("\n" + new_model)
        
    print(f"Success! Added model '{name}' to {protocol_path}.")
    print("Next step: Edit the file to add fields.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Add a new Pydantic model to the protocol.")
    parser.add_argument("--name", required=True, help="Model name (TitleCase)")
    parser.add_argument("--description", required=True, help="Docstring description")
    parser.add_argument("--heuristics", default="Use when defining strictly typed data.", help="Cognitive Policy")
    parser.add_argument("--verification", default="Pydantic validation.", help="Verification Logic")
    
    args = parser.parse_args()
    
    add_model(args.name, args.description, args.heuristics, args.verification)
