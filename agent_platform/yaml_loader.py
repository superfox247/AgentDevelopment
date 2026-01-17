import importlib
import logging
from pathlib import Path
from typing import Any

import yaml
from google.adk.agents import BaseAgent, LlmAgent

from agent_platform.config import config
from agent_platform.prompts import load_instruction

logger = logging.getLogger(__name__)

def _import_object(path: str) -> Any:
    """Imports an object from a dot-path string (e.g. 'pkg.mod.cls')."""
    try:
        module_path, obj_name = path.rsplit(".", 1)
        module = importlib.import_module(module_path)
        return getattr(module, obj_name)
    except (ValueError, ImportError, AttributeError) as e:
        raise ImportError(f"Could not import object from '{path}': {e}") from e

def _resolve_instruction(data: dict, path: Path) -> str:
    """Helper to resolve instruction text."""
    instruction = data.get("instruction", "")
    if "instruction_key" in data:
        instruction = load_instruction(data["instruction_key"])
    elif "instruction_file" in data:
        inst_path = path.parent / data["instruction_file"]
        if not inst_path.exists():
             inst_path = Path(data["instruction_file"]).resolve()

        if inst_path.exists():
            instruction = inst_path.read_text(encoding="utf-8")
        else:
            raise FileNotFoundError(f"Instruction file '{data['instruction_file']}' not found relative to {path.parent} or as absolute path.")
    return instruction

def _resolve_tools(data: dict) -> list[Any]:
    """Helper to resolve tools list."""
    tools = []
    for tool_ref in data.get("tools", []):
        if tool_ref == "google_search":
            from google.adk.tools import google_search
            tools.append(google_search)
        elif tool_ref == "code_execution":
            from google.adk.tools import code_execution
            tools.append(code_execution)
        elif isinstance(tool_ref, str):
            tools.append(_import_object(tool_ref))
        else:
            logger.warning(f"Unsupported tool definition: {tool_ref}")
    return tools

def load_agent_from_yaml(yaml_path: str, base_dir: str | None = None) -> BaseAgent:
    """
    Loads an LlmAgent from a YAML configuration file.
    """
    path = Path(yaml_path)
    if not path.is_absolute() and base_dir:
        path = Path(base_dir) / path

    if not path.exists():
        raise FileNotFoundError(f"Agent config not found at {path}")

    logger.info(f"Loading agent from {path}")

    with open(path, encoding="utf-8") as f:
        data = yaml.safe_load(f)

    instruction = _resolve_instruction(data, path)
    tools = _resolve_tools(data)

    output_schema = None
    if "output_schema" in data:
        output_schema = _import_object(data["output_schema"])

    input_schema = None
    if "input_schema" in data:
        input_schema = _import_object(data["input_schema"])

    return LlmAgent(
        name=data["name"],
        model=data.get("model", config.default_model),
        description=data.get("description", ""),
        instruction=instruction,
        tools=tools,
        input_schema=input_schema,
        output_schema=output_schema,
        output_key=data.get("output_key", data["name"] + "_result") if output_schema else None,
        # Allow passing through other LlmAgent flags
        disallow_transfer_to_parent=data.get("disallow_transfer_to_parent", False),
        disallow_transfer_to_peers=data.get("disallow_transfer_to_peers", False),
    )
