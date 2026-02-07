"""Tests for context-engine chunk model and chunkers."""

from __future__ import annotations

from dataclasses import FrozenInstanceError

import pytest

from agent_platform.context_engine.chunker import Chunk, MarkdownChunker, PythonChunker


def test_chunk_is_immutable_and_serializable() -> None:
    """Chunk fields and metadata should be immutable once created."""
    chunk = Chunk(content="hello", metadata={"type": "section", "name": "Intro"}, id="abc")

    with pytest.raises(FrozenInstanceError):
        chunk.content = "updated"  # type: ignore[misc]

    with pytest.raises(TypeError):
        chunk.metadata["type"] = "other"  # type: ignore[index]

    serialized = chunk.to_dict()
    assert serialized["content"] == "hello"
    assert serialized["metadata"]["name"] == "Intro"
    assert serialized["id"] == "abc"

    roundtrip = Chunk.from_dict(serialized)
    assert roundtrip == chunk


def test_python_chunker_returns_typed_chunks() -> None:
    """Python chunker should emit immutable Chunk instances."""
    content = "class A:\n    pass\n\ndef fn():\n    return 1\n"
    chunks = PythonChunker().chunk(content, "sample.py")

    assert len(chunks) == 2
    assert all(isinstance(chunk, Chunk) for chunk in chunks)
    assert chunks[0].metadata["type"] == "class"
    assert chunks[1].metadata["type"] == "function"


def test_markdown_chunker_returns_typed_chunks() -> None:
    """Markdown chunker should split by headers into Chunk instances."""
    content = "# Intro\nBody\n## Details\nMore\n"
    chunks = MarkdownChunker().chunk(content, "sample.md")

    assert len(chunks) == 2
    assert all(isinstance(chunk, Chunk) for chunk in chunks)
    assert chunks[0].metadata["name"] == "Intro"
    assert chunks[1].metadata["name"] == "Details"
