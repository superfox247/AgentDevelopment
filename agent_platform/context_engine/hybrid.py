import logging
import uuid
from typing import Any

from opentelemetry import trace
from qdrant_client.http import models

from agent_platform.context_engine.google_client import GoogleClient
from agent_platform.context_engine.graph import GraphClient
from agent_platform.context_engine.rerank import Reranker
from agent_platform.context_engine.vector import VectorClient

logger = logging.getLogger(__name__)
tracer = trace.get_tracer(__name__)


class ContextEngine:
    """
    Hybrid Search Engine managing Concept nodes in Neo4j and their embeddings in Qdrant.
    Now enhanced with Google Embeddings and FlashRank Reranking.
    """

    COLLECTION_NAME = "concepts"

    def __init__(self) -> None:
        self.graph = GraphClient()
        self.vector = VectorClient()
        self.google = GoogleClient()
        self.reranker = Reranker() # Default model
        logger.info("Initialized ContextEngine with GoogleClient and FlashRank.")

    def _embed(self, text: str) -> list[float]:
        return self.google.embed_content(text)

    def initialize(self) -> None:
        """Sets up connections and ensures schema."""
        self.graph.connect()
        self.vector.ensure_collection(self.COLLECTION_NAME, vector_size=3072) # gemini-embedding-001 is 3072
        # Create constraint for unique Concept ID
        self.graph.query(
            "CREATE CONSTRAINT concept_id_unique IF NOT EXISTS FOR (c:Concept) REQUIRE c.id IS UNIQUE"
        )

    def add_concept(self, name: str, description: str, metadata: dict | None = None, concept_id: str | None = None) -> str:
        """
        Creates/Updates a Concept node and indexes its description.
        Returns the Concept ID.
        """
        if not concept_id:
            concept_id = str(uuid.uuid4())

        vector = self._embed(f"{name}: {description}")
        metadata = metadata or {}

        with tracer.start_as_current_span("add_concept"):
            # 1. Add Node to Graph (Idempotent Merge on ID)
            self.graph.query(
                """
                MERGE (c:Concept {id: $id})
                ON CREATE SET c.name = $name, c.description = $desc, c.created_at = timestamp(), c.updated_at = timestamp()
                ON MATCH SET c.name = $name, c.description = $desc, c.updated_at = timestamp()
                RETURN c.id
                """,
                {"name": name, "id": concept_id, "desc": description},
            )

            # 2. Add Vector
            payload = {"name": name, "description": description, "id": concept_id, **metadata}
            point = models.PointStruct(
                id=concept_id,
                vector=vector,
                payload=payload
            )
            self.vector.upsert_points(self.COLLECTION_NAME, [point])

            logger.info(f"Upserted concept: {name} ({concept_id})")
            return concept_id

    def search_concepts(self, query: str, limit: int = 10) -> list[dict]:
        """
        Performs hybrid search: Vector Search -> Graph Enrichment -> Reranking.
        """
        vector = self._embed(query)

        with tracer.start_as_current_span("search_concepts") as span:
            # 1. Vector Search (Retrieve more candidates for reranking, e.g. 2x)
            candidate_limit = limit * 2
            results = self.vector.search(self.COLLECTION_NAME, vector, limit=candidate_limit)

            candidates = []
            for hit in results:
                concept_id = hit.payload.get("id")
                # 2. Graph Lookup (Enrichment)
                graph_data = self.graph.query(
                    "MATCH (c:Concept {id: $id}) RETURN c", {"id": concept_id}
                )
                node_props = graph_data[0]["c"] if graph_data else {}

                candidates.append({
                    "id": concept_id,
                    "score": hit.score, # Qdrant score
                    "name": hit.payload.get("name"),
                    "description": hit.payload.get("description"),
                    "graph_props": node_props
                })

            span.set_attribute("search.candidates_count", len(candidates))

            # 3. Reranking
            reranked = self.reranker.rerank(query, candidates, top_k=limit)

            return reranked

    def get_stats(self) -> dict[str, Any]:
        """Returns unified stats from Graph and Vector DBs."""
        return {
            "graph": self.graph.get_stats(),
            "vector": self.vector.get_stats(self.COLLECTION_NAME)
        }

    def wipe_all(self) -> None:
        """Wipes both stores."""
        self.graph.wipe()
        self.vector.delete_collection(self.COLLECTION_NAME)

    def get_file_hash(self, file_path: str) -> str | None:
        """Retrieves the stored hash for a file from the Graph."""
        results = self.graph.query(
            "MATCH (f:File {path: $path}) RETURN f.hash as hash",
            {"path": file_path}
        )
        if results:
            return results[0].get("hash")
        return None

    def update_file_hash(self, file_path: str, file_hash: str) -> None:
        """Updates or creates a File node with the new hash."""
        self.graph.query(
            """
            MERGE (f:File {path: $path})
            SET f.hash = $hash, f.updated_at = timestamp()
            """,
            {"path": file_path, "hash": file_hash}
        )
