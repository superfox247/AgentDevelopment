from pathlib import Path
from typing import Any

from google.adk.agents import LlmAgent
from google.adk.models import Gemini
from pydantic import BaseModel, Field

from agent_platform.config import config as platform_config
from agent_platform.prompts import load_instruction


class ToolConfig(BaseModel):
    """Configuration for a tool."""
    # Can be a simple string (e.g. "google_search") or dict for more complex tools?
    # yaml_loader supports str only.
    # We'll support str for back compat + object import
    path: str


class ModelConfig(BaseModel):
    """Configuration for LLM Model."""
    name: str = "models/gemini-2.0-flash"
    temperature: float = 0.7
    top_p: float = 0.95
    stream: bool = True

    # Allow simple string alias "gemini-..."
    @staticmethod
    def from_string(model_name: str) -> "ModelConfig":
        return ModelConfig(name=model_name)


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
    model: str | ModelConfig = platform_config.default_model
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
        self._base_path = path

    def resolve_instruction(self) -> str:
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
        if isinstance(self.model, str):
            # Use defaults from platform config if needed, or simple init
            return Gemini(model=self.model)

        return Gemini(
            model=self.model.name
        )

    def resolve_tools(self) -> list[Any]:
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

             # Construct file path
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
