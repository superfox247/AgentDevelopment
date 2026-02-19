"""
Context Engine Router.

Endpoints for interacting with the Context Engine:
- Semantic search across indexed codebase
- Database statistics (Qdrant + Neo4j)
- List of indexed files
- Find similar concepts
- Full-text search on concept names/descriptions
- Snapshot management
- Graph export (Cypher backup)
"""

import logging
from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel, Field

from agent_platform.context_engine.hybrid import ContextEngine

router = APIRouter(prefix="/api/context-engine", tags=["context-engine"])
logger = logging.getLogger(__name__)

# Lazy singleton — initialized on first request
_engine: ContextEngine | None = None


def _get_engine() -> ContextEngine:
    global _engine
    if _engine is None:
        _engine = ContextEngine()
        _engine.initialize()
        logger.info("Context Engine initialized for dashboard API")
    return _engine


# --- Request / Response Models ---


class SearchRequest(BaseModel):
    query: str
    limit: int = Field(default=10, ge=1, le=50)


class SearchResult(BaseModel):
    id: str
    name: str | None = None
    description: str | None = None
    score: float | None = None
    rerank_score: float | None = None
    graph_props: dict[str, Any] = {}


class SearchResponse(BaseModel):
    query: str
    results: list[SearchResult]
    count: int


class StatsResponse(BaseModel):
    graph: dict[str, Any]
    vector: dict[str, Any]


class IndexedFile(BaseModel):
    path: str
    hash: str | None = None
    updated_at: int | None = None


class FilesResponse(BaseModel):
    files: list[IndexedFile]
    count: int


class SnapshotInfo(BaseModel):
    name: str
    size: int | None = None
    created_at: str | None = None


class SnapshotsResponse(BaseModel):
    snapshots: list[SnapshotInfo]
    count: int


class SimilarRequest(BaseModel):
    limit: int = Field(default=5, ge=1, le=20)


class FulltextSearchRequest(BaseModel):
    query: str
    limit: int = Field(default=10, ge=1, le=50)


class ExportResponse(BaseModel):
    cypher: str
    lines: int


# --- Endpoints ---


@router.post("/search", response_model=SearchResponse)
def search(req: SearchRequest) -> SearchResponse:
    """Search the indexed codebase using hybrid search."""
    engine = _get_engine()
    raw_results = engine.search_concepts(req.query, limit=req.limit)

    results = [
        SearchResult(
            id=r.get("id", ""),
            name=r.get("name"),
            description=r.get("description"),
            score=r.get("score"),
            rerank_score=r.get("rerank_score"),
            graph_props=r.get("graph_props", {}),
        )
        for r in raw_results
    ]

    return SearchResponse(query=req.query, results=results, count=len(results))


@router.get("/stats", response_model=StatsResponse)
def stats() -> StatsResponse:
    """Get Context Engine database statistics."""
    engine = _get_engine()
    raw = engine.get_stats()
    return StatsResponse(graph=raw.get("graph", {}), vector=raw.get("vector", {}))


@router.get("/files", response_model=FilesResponse)
def files() -> FilesResponse:
    """List all indexed files from the knowledge graph."""
    engine = _get_engine()
    raw = engine.graph.query(
        "MATCH (f:File) RETURN f.path as path, f.hash as hash, f.updated_at as updated_at ORDER BY f.path"
    )
    items = [
        IndexedFile(
            path=row.get("path", ""),
            hash=row.get("hash"),
            updated_at=row.get("updated_at"),
        )
        for row in raw
    ]
    return FilesResponse(files=items, count=len(items))


@router.get("/similar/{concept_id}", response_model=SearchResponse)
def similar(concept_id: str, limit: int = 5) -> SearchResponse:
    """Find concepts similar to the given one using Qdrant's recommend API."""
    engine = _get_engine()
    raw_results = engine.find_similar(concept_id, limit=limit)

    results = [
        SearchResult(
            id=r.get("id", ""),
            name=r.get("name"),
            description=r.get("description"),
            score=r.get("score"),
            graph_props=r.get("graph_props", {}),
        )
        for r in raw_results
    ]

    return SearchResponse(query=f"similar:{concept_id}", results=results, count=len(results))


@router.get("/snapshots", response_model=SnapshotsResponse)
def list_snapshots() -> SnapshotsResponse:
    """List all snapshots for the concepts collection."""
    engine = _get_engine()
    raw = engine.list_snapshots()
    items = [
        SnapshotInfo(
            name=s.get("name", ""),
            size=s.get("size"),
            created_at=s.get("created_at"),
        )
        for s in raw
    ]
    return SnapshotsResponse(snapshots=items, count=len(items))


@router.post("/snapshots", response_model=SnapshotInfo)
def create_snapshot() -> SnapshotInfo:
    """Create a snapshot of the concepts collection for backup."""
    engine = _get_engine()
    result = engine.create_snapshot()
    return SnapshotInfo(
        name=result.get("name", ""),
        size=result.get("size"),
        created_at=result.get("created_at"),
    )


@router.post("/fulltext-search", response_model=SearchResponse)
def fulltext_search(req: FulltextSearchRequest) -> SearchResponse:
    """Search concepts using Neo4j full-text index (text matching, not vector)."""
    engine = _get_engine()
    raw_results = engine.fulltext_search_concepts(req.query, limit=req.limit)

    results = [
        SearchResult(
            id=r.get("id", ""),
            name=r.get("name"),
            description=r.get("description"),
            score=r.get("score"),
        )
        for r in raw_results
    ]

    return SearchResponse(query=req.query, results=results, count=len(results))


@router.get("/export")
def export_graph() -> ExportResponse:
    """Export the entire graph as portable Cypher CREATE statements."""
    engine = _get_engine()
    cypher = engine.export_graph()
    line_count = cypher.count("\n") + 1 if cypher else 0
    return ExportResponse(cypher=cypher, lines=line_count)
