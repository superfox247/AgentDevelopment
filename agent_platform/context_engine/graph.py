"""
Neo4j Graph Client implementation.
"""

import logging
from typing import Any

from neo4j import GraphDatabase, Result
from opentelemetry import trace

from agent_platform.config import config

logger = logging.getLogger(__name__)
tracer = trace.get_tracer(__name__)


class GraphClient:
    """
    Client for interacting with the Neo4j Graph Database.
    Supports OpenTelemetry tracing for all operations.
    """

    def __init__(self) -> None:
        self.uri = config.neo4j_uri
        self.user = config.neo4j_user
        self.password = config.neo4j_password
        self._driver = None

    def connect(self) -> None:
        """Establishes connection to Neo4j."""
        if not self._driver:
            try:
                self._driver = GraphDatabase.driver(
                    self.uri, auth=(self.user, self.password)
                )
                self._driver.verify_connectivity()
                logger.info(f"Connected to Neo4j at {self.uri}")
            except Exception as e:
                logger.error(f"Failed to connect to Neo4j: {e}")
                raise

    def get_stats(self) -> dict[str, Any]:
        """Returns statistics about the graph database."""
        try:
            query = "MATCH (n) RETURN count(n) as total_nodes"
            result = self.query(query)
            total = result[0]["total_nodes"] if result else 0

            # Breakdown by label
            query_labels = "MATCH (n) RETURN distinct labels(n) as label, count(n) as count"
            label_result = self.query(query_labels)
            breakdown = {str(row["label"]): row["count"] for row in label_result}

            return {"total_nodes": total, "breakdown": breakdown}
        except Exception as e:
            logger.error(f"Failed to get graph stats: {e}")
            return {"error": str(e)}

    def close(self) -> None:
        """Closes the Neo4j driver."""
        if self._driver:
            self._driver.close()
            self._driver = None
            logger.info("Neo4j connection closed.")

    def __enter__(self) -> "GraphClient":
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.close()

    def query(self, cypher: str, params: dict[str, Any] | None = None) -> list[dict]:
        """
        Executes a Cypher query and returns the results as a list of dictionaries.

        Args:
            cypher: The Cypher query string.
            params: Dictionary of query parameters.
        """
        if not self._driver:
            self.connect()

        with tracer.start_as_current_span("neo4j_query") as span:
            span.set_attribute("db.statement", cypher)
            if params:
                span.set_attribute("db.params", str(params))

            try:
                with self._driver.session() as session:
                    result: Result = session.run(cypher, params or {})
                    data = [record.data() for record in result]
                    span.set_attribute("db.rows_returned", len(data))
                    return data
            except Exception as e:
                logger.error(f"Query failed: {cypher} | Error: {e}")
                span.record_exception(e)
                raise

    def wipe(self) -> None:
        """Dangerously wipes the entire database."""
        logger.warning("Wiping functionality called on Neo4j DB.")
        self.query("MATCH (n) DETACH DELETE n")

