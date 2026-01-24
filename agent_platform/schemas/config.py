"""
Configuration Schemas for the Agent Platform.

Defines Pydantic models used to parse and validate agent configuration files (YAML),
replacing legacy configuration loading mechanisms.
"""

from pathlib import Path
from typing import Any
import logging

from google.adk.agents import LlmAgent
from google.adk.models import Gemini
from google.genai import types
from pydantic import BaseModel, Field

from agent_platform.config import config as platform_config
from agent_platform.prompts import load_instruction


class ToolConfig(BaseModel):
    """Configuration for a tool."""
    # Can be a simple string (e.g. "google_search") or dict for more complex tools?
    # yaml_loader supports str only.
    # We'll support str for back compat + object import
    path: str





class AgentConfig(BaseModel):
    """
    Standardized Agent Configuration.
    Replaces yaml_loader.py with strict validation.
    """
    # Metadata
    name: str
    description: str = ""

    # Instruction (One of these must be present)
    instruction: str | None = None
    instruction_key: str | None = None
    instruction_file: str | None = None

    # Components
    # "model" should be the model ID string (e.g. "models/gemini-2.0-flash")
    # or an instance of the ADK Gemini model (if passed programmatically)
    model: str | Gemini = platform_config.default_model

    # Generation Configuration (ADK Type)
    generation_config: types.GenerationConfig | None = None

    tools: list[str] = Field(default_factory=list)

    # Capabilities
    input_schema: str | None = None  # Import path
    output_schema: str | None = None # Import path
    output_key: str | None = None

    # Flags
    disallow_transfer_to_parent: bool = False
    disallow_transfer_to_peers: bool = False

    # Internal state for resolution
    _base_path: Path | None = None

    def set_base_path(self, path: Path) -> None:
        """Sets the internal base path for relative file resolution."""
        self._base_path = path

    def resolve_instruction(self) -> str:
        """Resolves the instruction content from string, key, or file."""
        if self.instruction:
            return self.instruction
        if self.instruction_key:
            return load_instruction(self.instruction_key)
        if self.instruction_file:
            if not self._base_path:
                 # Try absolute or relative to cwd
                 p = Path(self.instruction_file)
                 if p.exists():
                     return p.read_text(encoding="utf-8")
                 raise ValueError(f"instruction_file '{self.instruction_file}' requires base path or absolute path")

            p = self._base_path.parent / self.instruction_file
            if not p.exists():
                 p = Path(self.instruction_file).resolve()

            if p.exists():
                return p.read_text(encoding="utf-8")
            raise FileNotFoundError(f"Instruction file not found: {self.instruction_file}")

        return ""

    def resolve_model(self) -> Gemini:
        """Resolves the model configuration into an ADK Gemini model instance."""
        if isinstance(self.model, Gemini):
            return self.model

        # At this point self.model should be a string ID
        model_id = self.model
        if not isinstance(model_id, str):
            # Fallback if somehow it's not a string (should be caught by Pydantic)
            model_id = str(model_id)

        # Create Gemini model with config
        # Note: Gemini model/client might accept config object directly
        # ADK's Gemini model wrapper usually accepts model_name.
        # Client interaction passes config at generation time.
        # But initialization of Gemini model object in ADK looks like: Gemini(model="...")
        # We need to ensure the config is passed appropriately.
        # The ADK `Gemini` class (google.adk.models.Gemini) helps configure the client?
        # Let's check the Gemini ADK class if possible, but for now we assume standard init.

        # If generation_config is present, we might want to attach it?
        # The ADK Gemini model might not persist generation_config on init.
        # But we return the initialized model.
        return Gemini(model=model_id)

    def resolve_tools(self) -> list[Any]:
        """Resolves tool references into executable tool functions/modules."""
        resolved = []
        import importlib

        for tool_ref in self.tools:
            if tool_ref == "google_search":
                from google.adk.tools import google_search
                resolved.append(google_search)
            elif tool_ref == "code_execution":
                from google.adk.tools import code_execution
                resolved.append(code_execution)
            else:
                try:
                    resolved.append(self._resolve_custom_tool(tool_ref, importlib))
                except Exception as e:
                    import logging
                    logging.getLogger(__name__).warning(f"Failed to load tool {tool_ref}: {e}")

        return resolved

    def _resolve_custom_tool(self, tool_ref: str, importlib: Any) -> Any:
        # Custom Import
        if tool_ref.startswith("."):
             # Relative import
             if not self._base_path:
                 raise ImportError("Relative import requires base_path")

             parts = tool_ref.lstrip(".").split(".")
             if len(parts) < 2:
                 raise ImportError(f"Invalid relative tool: {tool_ref}")

             module_name = parts[0]
             func_name = parts[1]

             # Try to resolve relative to project root to allow relative imports within the module
             try:
                 # Find project root (where pyproject.toml is)
                 import os
                 p = self._base_path
                 # logging.getLogger(__name__).warning(f"Resolving base path: {p}")
                 project_root = None
                 for parent in p.parents:
                     if (parent / "pyproject.toml").exists():
                         project_root = parent
                         break
                 
                 if project_root:
                    # logging.getLogger(__name__).warning(f"Found project root: {project_root}")
                     # Calculate full package path
                     # e.g. domains/course_creator/image_generator -> domains.course_creator.image_generator
                     rel_dir = self._base_path.parent.relative_to(project_root)
                     package_path = str(rel_dir).replace(os.sep, ".")
                     
                     full_module_name = f"{package_path}.{module_name}"
                     mod = importlib.import_module(full_module_name)
                     return getattr(mod, func_name)
                 else:
                     logging.getLogger(__name__).warning(f"Project root not found for {p}")
             except Exception as e:
                 logging.getLogger(__name__).warning(f"Project resolution failed for {tool_ref}: {e}")
                 # Fallback to direct file loading if project resolution fails
                 pass

             # Fallback: Construct file path and load directly (limitations with relative imports)
             module_path = self._base_path.parent / f"{module_name}.py"
             spec = importlib.util.spec_from_file_location(module_name, module_path)
             if spec and spec.loader:
                 mod = importlib.util.module_from_spec(spec)
                 spec.loader.exec_module(mod)
                 return getattr(mod, func_name)
        else:
            # Absolute
            if "." not in tool_ref:
                raise ImportError(f"Invalid tool reference: {tool_ref}. Must be 'module.object'")

            mod_str, obj_name = tool_ref.rsplit(".", 1)
            mod = importlib.import_module(mod_str)
            return getattr(mod, obj_name)

    def to_agent(self) -> LlmAgent:
        """Hydrates the configuration into an actual ADK Agent."""
        inst = self.resolve_instruction()
        model_obj = self.resolve_model()
        tool_objs = self.resolve_tools()

        # Schemas
        import importlib
        in_schema = None
        out_schema = None

        if self.input_schema:
            m, c = self.input_schema.rsplit(".", 1)
            in_schema = getattr(importlib.import_module(m), c)

        if self.output_schema:
            m, c = self.output_schema.rsplit(".", 1)
            out_schema = getattr(importlib.import_module(m), c)

        return LlmAgent(
            name=self.name,
            model=model_obj,
            description=self.description,
            instruction=inst,
            tools=tool_objs,
            input_schema=in_schema,
            output_schema=out_schema,
            output_key=self.output_key or (f"{self.name}_result" if out_schema else None),
            disallow_transfer_to_parent=self.disallow_transfer_to_parent,
            disallow_transfer_to_peers=self.disallow_transfer_to_peers
        )
