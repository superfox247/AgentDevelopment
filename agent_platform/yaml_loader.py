import importlib
import importlib.util
import logging
from pathlib import Path
from typing import Any

import yaml
from google.adk.agents import BaseAgent, LlmAgent
from google.adk.models import Gemini

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
            raise FileNotFoundError(
                f"Instruction file '{data['instruction_file']}' not found relative to {path.parent} or as absolute path."
            )
    return instruction


def _import_relative(path: str, yaml_path: Path) -> Any:
    """Import a function relative to the YAML file's directory.
    
    Args:
        path: Relative import path like '.tools.generate_image_from_prompt'
        yaml_path: Path to the agent.yaml file
    
    Returns:
        The imported function/object
    """
    # .tools.func_name -> module='tools', func='func_name'
    parts = path.lstrip(".").split(".")
    if len(parts) < 2:
        raise ImportError(f"Invalid relative import path: {path}")
    
    module_name = parts[0]
    func_name = parts[1]
    
    module_path = yaml_path.parent / f"{module_name}.py"
    if not module_path.exists():
        raise ImportError(f"Module not found: {module_path}")
    
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Could not load module spec from: {module_path}")
    
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return getattr(module, func_name)


def _resolve_tools(data: dict, yaml_path: Path) -> list[Any]:
    """Helper to resolve tools list.
    
    Supports:
    - Built-in ADK tools: 'google_search', 'code_execution'
    - Absolute imports: 'package.module.function'
    - Relative imports: '.tools.function' (from agent directory)
    """
    tools = []
    for tool_ref in data.get("tools", []):
        if tool_ref == "google_search":
            from google.adk.tools import google_search
            tools.append(google_search)
        elif tool_ref == "code_execution":
            from google.adk.tools import code_execution
            tools.append(code_execution)
        elif isinstance(tool_ref, str):
            if tool_ref.startswith("."):
                # Relative import from agent directory
                tools.append(_import_relative(tool_ref, yaml_path))
            else:
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
    tools = _resolve_tools(data, path)

    output_schema = None
    if "output_schema" in data:
        output_schema = _import_object(data["output_schema"])

    input_schema = None
    if "input_schema" in data:
        input_schema = _import_object(data["input_schema"])

    model_config = data.get("model", config.default_model)
    if isinstance(model_config, str):
        # Default to Gemini with streaming enabled
        model = Gemini(model=model_config, stream=True)
    else:
        model = model_config

    return LlmAgent(
        name=data["name"],
        model=model,
        description=data.get("description", ""),
        instruction=instruction,
        tools=tools,
        input_schema=input_schema,
        output_schema=output_schema,
        output_key=data.get("output_key", data["name"] + "_result")
        if output_schema
        else None,
        # Allow passing through other LlmAgent flags
        disallow_transfer_to_parent=data.get("disallow_transfer_to_parent", False),
        disallow_transfer_to_peers=data.get("disallow_transfer_to_peers", False),
    )
