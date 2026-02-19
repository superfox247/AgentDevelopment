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
        # Create constraint for unique File path
        self.graph.query(
            "CREATE CONSTRAINT file_path_unique IF NOT EXISTS FOR (f:File) REQUIRE f.path IS UNIQUE"
        )
        # Create full-text search index on Concept name and description
        try:
            self.graph.query(
                "CREATE FULLTEXT INDEX concept_fulltext IF NOT EXISTS "
                "FOR (c:Concept) ON EACH [c.name, c.description]"
            )
            logger.info("Ensured full-text index on Concept(name, description)")
        except Exception as e:
            logger.warning(f"Full-text index creation skipped: {e}")

    def add_concept(
        self,
        name: str,
        description: str,
        metadata: dict | None = None,
        concept_id: str | None = None,
        source_file: str | None = None,
    ) -> str:
        """
        Creates/Updates a Concept node, indexes its description, and
        optionally links it to a source File via BELONGS_TO relationship.
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

            # 2. Link Concept to source File (if provided)
            if source_file:
                self.graph.query(
                    """
                    MATCH (c:Concept {id: $concept_id})
                    MERGE (f:File {path: $path})
                    MERGE (c)-[:BELONGS_TO]->(f)
                    """,
                    {"concept_id": concept_id, "path": source_file},
                )

            # 3. Add Vector
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

    def find_similar(self, concept_id: str, limit: int = 5) -> list[dict]:
        """
        Finds concepts similar to the given one using Qdrant's recommend API.
        Returns graph-enriched results.
        """
        with tracer.start_as_current_span("find_similar") as span:
            span.set_attribute("concept_id", concept_id)

            results = self.vector.recommend(
                self.COLLECTION_NAME,
                positive_ids=[concept_id],
                limit=limit,
            )

            similar = []
            for hit in results:
                hit_id = hit.payload.get("id")
                graph_data = self.graph.query(
                    "MATCH (c:Concept {id: $id}) RETURN c", {"id": hit_id}
                )
                node_props = graph_data[0]["c"] if graph_data else {}

                similar.append({
                    "id": hit_id,
                    "score": hit.score,
                    "name": hit.payload.get("name"),
                    "description": hit.payload.get("description"),
                    "graph_props": node_props,
                })

            span.set_attribute("results_count", len(similar))
            return similar

    def create_snapshot(self) -> dict[str, Any]:
        """Creates a snapshot of the concepts collection."""
        return self.vector.create_snapshot(self.COLLECTION_NAME)

    def list_snapshots(self) -> list[dict[str, Any]]:
        """Lists all snapshots for the concepts collection."""
        return self.vector.list_snapshots(self.COLLECTION_NAME)

    def fulltext_search_concepts(self, query: str, limit: int = 10) -> list[dict]:
        """Searches concepts by text using Neo4j full-text index."""
        results = self.graph.fulltext_search("concept_fulltext", query, limit)
        return [
            {
                "id": r["node"].get("id"),
                "name": r["node"].get("name"),
                "description": r["node"].get("description"),
                "score": r["score"],
            }
            for r in results
        ]

    def export_graph(self) -> str:
        """Exports the entire graph as Cypher statements."""
        return self.graph.export_cypher()

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
