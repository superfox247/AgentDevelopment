"""Unit tests for context-engine reranking behavior."""

from __future__ import annotations

import copy
from typing import Any

import pytest

from agent_platform.context_engine import rerank as rerank_module


class FakeRanker:
    """Minimal FlashRank-compatible stub."""

    def __init__(self, model_name: str) -> None:
        self.model_name = model_name

    def rerank(self, request: Any) -> list[dict[str, Any]]:
        return [
            {"meta": request.passages[1]["meta"], "score": 0.88},
            {"meta": request.passages[0]["meta"], "score": 0.51},
        ]


def test_rerank_returns_scored_copy_without_mutation(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Ensure reranking does not mutate the original candidate documents."""
    monkeypatch.setattr(rerank_module, "Ranker", FakeRanker)
    reranker = rerank_module.Reranker()

    documents: list[dict[str, Any]] = [
        {"id": "1", "description": "Alpha"},
        {"id": "2", "description": "Bravo"},
    ]
    original_documents = copy.deepcopy(documents)

    results = reranker.rerank("best doc", documents, top_k=1)

    assert documents == original_documents
    assert len(results) == 1
    assert results[0]["id"] == "2"
    assert results[0]["rerank_score"] == 0.88
    assert "rerank_score" not in documents[1]
