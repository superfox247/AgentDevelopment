"""
Qdrant Vector Client implementation.
"""

import logging
from typing import Any, Dict, List, Optional, Union

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
        self._client: Optional[QClient] = None

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
            except Exception as e:
                logger.error(f"Failed to ensure collection: {e}")
                span.record_exception(e)
                raise

    def upsert_points(self, collection_name: str, points: List[models.PointStruct]) -> None:
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
        vector: List[float],
        limit: int = 5,
        score_threshold: Optional[float] = None,
    ) -> List[models.ScoredPoint]:
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

    def get_stats(self, collection_name: str) -> Dict[str, Any]:
        """Returns statistics about the vector collection."""
        if not self._client:
            self.connect()
        try:
            count_result = self._client.count(collection_name=collection_name)
            info = self._client.get_collection(collection_name=collection_name)
            return {
                "total_vectors": count_result.count,
                "status": str(info.status),
                "vector_size": info.config.params.vectors.size
            }
        except Exception as e:
            logger.error(f"Failed to get vector stats: {e}")
            return {"error": str(e)}

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
