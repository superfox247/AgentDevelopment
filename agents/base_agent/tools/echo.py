"""Minimal echo tool for baseline agent testing.

Provides a single, dependency-free tool so we can verify tool callbacks,
schema inference, and eval harness without external APIs.
"""

from __future__ import annotations


def echo(text: str | None = None) -> str:
    """Return the input text unchanged.

    Use this for baseline tool tests and callback verification.
    No external APIs or side effects.

    Args:
        text: Any string to echo back. Defaults to empty string if None.

    Returns:
        The same string, or empty string if None.
    """
    return text if text is not None else ""
