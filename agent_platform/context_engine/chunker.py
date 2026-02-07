import ast
import hashlib
import logging
import re
from abc import ABC, abstractmethod
from collections.abc import Mapping
from dataclasses import dataclass
from types import MappingProxyType
from typing import Any

logger = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class Chunk:
    """Immutable semantic unit produced by chunkers."""

    content: str
    metadata: Mapping[str, Any]
    id: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "metadata", MappingProxyType(dict(self.metadata)))

    def to_dict(self) -> dict[str, Any]:
        """Serialize chunk for boundaries that require dict payloads."""
        return {"content": self.content, "metadata": dict(self.metadata), "id": self.id}

    @classmethod
    def from_dict(cls, payload: Mapping[str, Any]) -> "Chunk":
        """Deserialize chunk from a mapping payload."""
        return cls(
            content=str(payload["content"]),
            metadata=dict(payload["metadata"]),
            id=str(payload["id"]),
        )


class BaseChunker(ABC):
    @abstractmethod
    def chunk(self, content: str, file_path: str) -> list[Chunk]:
        pass

    def generate_id(self, file_path: str, chunk_name: str) -> str:
        """Deterministic ID based on file path and chunk name."""
        raw_id = f"{file_path}:{chunk_name}"
        return hashlib.md5(raw_id.encode()).hexdigest()

class PythonChunker(BaseChunker):
    def chunk(self, content: str, file_path: str) -> list[Chunk]:
        chunks: list[Chunk] = []
        try:
            tree = ast.parse(content)
            lines = content.splitlines()

            # 1. Classes
            for node in [n for n in tree.body if isinstance(n, ast.ClassDef)]:
                start = node.lineno - 1
                end = node.end_lineno
                chunk_content = "\n".join(lines[start:end])

                chunk_id = self.generate_id(file_path, f"class:{node.name}")
                chunks.append(Chunk(
                    content=chunk_content,
                    metadata={"type": "class", "name": node.name, "start_line": start + 1, "file_path": file_path},
                    id=chunk_id
                ))

                # Capture methods within class? For now, let's keep it simple or maybe chunk methods separately if they are large?
                # The "Industry Standard" often chunks methods *inside* classes as separate vectors but links them.
                # Let's chunk top-level functions separately.

            # 2. Top-level Functions
            for node in [n for n in tree.body if isinstance(n, ast.FunctionDef)]:
                start = node.lineno - 1
                end = node.end_lineno
                chunk_content = "\n".join(lines[start:end])

                chunk_id = self.generate_id(file_path, f"func:{node.name}")
                chunks.append(Chunk(
                    content=chunk_content,
                    metadata={"type": "function", "name": node.name, "start_line": start + 1, "file_path": file_path},
                    id=chunk_id
                ))

            # 3. Fallback/Remainder?
            # If the file has no classes/funcs (e.g. script), chunk the whole thing or split by logical blocks.
            # For this MVP, if no chunks found via AST (e.g. simple script), fallback to whole file.
            if not chunks:
                chunk_id = self.generate_id(file_path, "file")
                chunks.append(Chunk(
                    content=content,
                    metadata={"type": "script", "name": "root", "file_path": file_path},
                    id=chunk_id
                ))

        except Exception as e:
            # Fallback for syntax errors or parsing issues
            logger.warning("AST parse failed for %s: %s", file_path, e)
            chunk_id = self.generate_id(file_path, "raw")
            chunks.append(Chunk(
                content=content,
                metadata={"type": "raw", "error": str(e), "file_path": file_path},
                id=chunk_id
            ))

        return chunks

class MarkdownChunker(BaseChunker):
    def chunk(self, content: str, file_path: str) -> list[Chunk]:
        chunks: list[Chunk] = []
        lines = content.splitlines()
        current_header = "root"
        current_chunk_lines: list[str] = []

        for line in lines:
            header_match = re.match(r'^(#{1,3})\s+(.*)', line)
            if header_match:
                # Save previous chunk if it exists
                if current_chunk_lines:
                    chunk_content = "\n".join(current_chunk_lines).strip()
                    if chunk_content:
                        chunk_id = self.generate_id(file_path, current_header)
                        # Avoid duplicates if headers are identical?
                        # Add simple collision handling suffix if needed.
                        chunks.append(Chunk(
                            content=chunk_content,
                            metadata={"type": "section", "name": current_header, "file_path": file_path},
                            id=chunk_id
                        ))

                # Start new chunk
                current_header = header_match.group(2).strip()
                current_chunk_lines = [line]  # Include header in content
            else:
                current_chunk_lines.append(line)

        # Flush last chunk
        if current_chunk_lines:
            chunk_content = "\n".join(current_chunk_lines).strip()
            if chunk_content:
                chunk_id = self.generate_id(file_path, current_header)
                chunks.append(Chunk(
                    content=chunk_content,
                    metadata={"type": "section", "name": current_header, "file_path": file_path},
                    id=chunk_id
                ))

        return chunks

class ChunkerFactory:
    @staticmethod
    def get_chunker(file_path: str) -> BaseChunker:
        if file_path.endswith('.py'):
            return PythonChunker()
        elif file_path.endswith('.md'):
            return MarkdownChunker()
        else:
            # Default generic chunker (whole file for now, or sliding window later)
            return DefaultChunker()

class DefaultChunker(BaseChunker):
    def chunk(self, content: str, file_path: str) -> list[Chunk]:
        # Simple whole-file
        chunk_id = self.generate_id(file_path, "whole")
        return [Chunk(content=content, metadata={"type": "file", "file_path": file_path}, id=chunk_id)]
