"""
Qdrant Vector Client implementation.
"""

import logging
from typing import Any

from opentelemetry import trace
from qdrant_client import QdrantClient as QClient
from qdrant_client.http import models

from agent_platform.config import config

logger = logging.getLogger(__name__)
tracer = trace.get_tracer(__name__)


class VectorClient:
    """
    Client for interacting with the Qdrant Vector Database.
    Supports OpenTelemetry tracing.
    """

    def __init__(self) -> None:
        self.url = config.qdrant_url
        self.api_key = config.qdrant_api_key
        self._client: QClient | None = None

    def connect(self) -> None:
        """Establishes connection to Qdrant."""
        if not self._client:
            try:
                self._client = QClient(url=self.url, api_key=self.api_key)
                # Cheap check? Qdrant client doesn't explicitly 'connect' until request usually,
                # but we can check collection list.
                logger.info(f"Initialized Qdrant client at {self.url}")
            except Exception as e:
                logger.error(f"Failed to initialize Qdrant client: {e}")
                raise

    def ensure_collection(self, collection_name: str, vector_size: int = 768) -> None:
        """Ensures a collection exists with the given vector size."""
        if not self._client:
            self.connect()

        with tracer.start_as_current_span("qdrant_ensure_collection") as span:
            span.set_attribute("db.collection", collection_name)
            try:
                if not self._client.collection_exists(collection_name):
                    self._client.create_collection(
                        collection_name=collection_name,
                        vectors_config=models.VectorParams(
                            size=vector_size, distance=models.Distance.COSINE
                        ),
                    )
                    logger.info(f"Created collection '{collection_name}'")
                # Ensure payload indexes exist for efficient filtering
                self._ensure_payload_indexes(collection_name)
            except Exception as e:
                logger.error(f"Failed to ensure collection: {e}")
                span.record_exception(e)
                raise

    def _ensure_payload_indexes(self, collection_name: str) -> None:
        """Creates payload indexes on commonly filtered fields for faster queries."""
        index_fields = {
            "name": models.PayloadSchemaType.KEYWORD,
            "id": models.PayloadSchemaType.KEYWORD,
        }
        for field_name, field_type in index_fields.items():
            try:
                self._client.create_payload_index(
                    collection_name=collection_name,
                    field_name=field_name,
                    field_schema=field_type,
                )
                logger.info(f"Ensured payload index on '{field_name}' ({field_type})")
            except Exception:
                # Index may already exist — Qdrant returns an error for duplicates
                pass

    def upsert_points(self, collection_name: str, points: list[models.PointStruct]) -> None:
        """Upserts points into a collection."""
        if not self._client:
            self.connect()

        with tracer.start_as_current_span("qdrant_upsert") as span:
            span.set_attribute("db.collection", collection_name)
            span.set_attribute("db.points_count", len(points))
            try:
                self._client.upsert(
                    collection_name=collection_name,
                    points=points,
                )
            except Exception as e:
                logger.error(f"Upsert failed: {e}")
                span.record_exception(e)
                raise

    def search(
        self,
        collection_name: str,
        vector: list[float],
        limit: int = 5,
        score_threshold: float | None = None,
    ) -> list[models.ScoredPoint]:
        """Searches for nearest neighbors."""
        if not self._client:
            self.connect()

        with tracer.start_as_current_span("qdrant_search") as span:
            span.set_attribute("db.collection", collection_name)
            try:
                results = self._client.query_points(
                    collection_name=collection_name,
                    query=vector,
                    limit=limit,
                    score_threshold=score_threshold,
                ).points
                span.set_attribute("db.results_count", len(results))
                return results
            except Exception as e:
                logger.error(f"Search failed: {e}")
                span.record_exception(e)
                raise

    def recommend(
        self,
        collection_name: str,
        positive_ids: list[str],
        negative_ids: list[str] | None = None,
        limit: int = 5,
    ) -> list[models.ScoredPoint]:
        """Finds similar points using Qdrant's recommend API (via query_points)."""
        if not self._client:
            self.connect()

        with tracer.start_as_current_span("qdrant_recommend") as span:
            span.set_attribute("db.collection", collection_name)
            span.set_attribute("db.positive_ids", str(positive_ids))
            try:
                results = self._client.query_points(
                    collection_name=collection_name,
                    query=models.RecommendQuery(
                        recommend=models.RecommendInput(
                            positive=positive_ids,
                            negative=negative_ids or [],
                        ),
                    ),
                    limit=limit,
                ).points
                span.set_attribute("db.results_count", len(results))
                return results
            except Exception as e:
                logger.error(f"Recommend failed: {e}")
                span.record_exception(e)
                raise

    def get_stats(self, collection_name: str) -> dict[str, Any]:
        """Returns detailed statistics about the vector collection."""
        if not self._client:
            self.connect()
        try:
            count_result = self._client.count(collection_name=collection_name)
            info = self._client.get_collection(collection_name=collection_name)
            return {
                "total_vectors": count_result.count,
                "indexed_vectors": info.indexed_vectors_count,
                "segments_count": info.segments_count,
                "status": str(info.status),
                "optimizer_status": str(info.optimizer_status),
                "vector_size": info.config.params.vectors.size,
                "distance": str(info.config.params.vectors.distance),
                "on_disk_payload": info.config.params.on_disk_payload,
                "hnsw_config": {
                    "m": info.config.hnsw_config.m,
                    "ef_construct": info.config.hnsw_config.ef_construct,
                },
                "payload_schema": {
                    k: str(v.data_type) for k, v in (info.payload_schema or {}).items()
                },
            }
        except Exception as e:
            logger.error(f"Failed to get vector stats: {e}")
            return {"error": str(e)}

    def create_snapshot(self, collection_name: str) -> dict[str, Any]:
        """Creates a snapshot of the collection for backup."""
        if not self._client:
            self.connect()
        try:
            snapshot = self._client.create_snapshot(collection_name=collection_name)
            logger.info(f"Created snapshot for '{collection_name}': {snapshot.name}")
            return {
                "name": snapshot.name,
                "size": snapshot.size,
                "created_at": str(snapshot.creation_time),
            }
        except Exception as e:
            logger.error(f"Failed to create snapshot: {e}")
            return {"error": str(e)}

    def list_snapshots(self, collection_name: str) -> list[dict[str, Any]]:
        """Lists all snapshots for a collection."""
        if not self._client:
            self.connect()
        try:
            snapshots = self._client.list_snapshots(collection_name=collection_name)
            return [
                {
                    "name": s.name,
                    "size": s.size,
                    "created_at": str(s.creation_time),
                }
                for s in snapshots
            ]
        except Exception as e:
            logger.error(f"Failed to list snapshots: {e}")
            return []

    def delete_collection(self, collection_name: str) -> None:
        """Deletes a collection."""
        if not self._client:
            self.connect()
        try:
            self._client.delete_collection(collection_name)
            logger.warning(f"Deleted collection '{collection_name}'")
        except Exception as e:
            logger.error(f"Failed to delete collection: {e}")
            raise
