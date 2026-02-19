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
        """Returns detailed statistics about the graph database."""
        try:
            # Node counts
            node_result = self.query("MATCH (n) RETURN count(n) as total_nodes")
            total_nodes = node_result[0]["total_nodes"] if node_result else 0

            # Breakdown by label
            label_result = self.query(
                "MATCH (n) RETURN distinct labels(n) as label, count(n) as count"
            )
            node_breakdown = {str(row["label"]): row["count"] for row in label_result}

            # Relationship counts
            rel_result = self.query("MATCH ()-[r]->() RETURN count(r) as total_rels")
            total_rels = rel_result[0]["total_rels"] if rel_result else 0

            # Breakdown by relationship type
            rel_type_result = self.query(
                "MATCH ()-[r]->() RETURN type(r) as type, count(r) as count"
            )
            rel_breakdown = {row["type"]: row["count"] for row in rel_type_result}

            # Indexes
            index_result = self.query(
                "SHOW INDEXES YIELD name, type, labelsOrTypes, properties, state "
                "RETURN name, type, labelsOrTypes, properties, state"
            )
            indexes = [
                {
                    "name": row["name"],
                    "type": row["type"],
                    "labels": row.get("labelsOrTypes"),
                    "properties": row.get("properties"),
                    "state": row.get("state"),
                }
                for row in index_result
            ]

            # Constraints
            constraint_result = self.query(
                "SHOW CONSTRAINTS YIELD name, type, labelsOrTypes, properties "
                "RETURN name, type, labelsOrTypes, properties"
            )
            constraints = [
                {
                    "name": row["name"],
                    "type": row["type"],
                    "labels": row.get("labelsOrTypes"),
                    "properties": row.get("properties"),
                }
                for row in constraint_result
            ]

            return {
                "total_nodes": total_nodes,
                "total_relationships": total_rels,
                "node_breakdown": node_breakdown,
                "relationship_breakdown": rel_breakdown,
                "indexes": indexes,
                "constraints": constraints,
            }
        except Exception as e:
            logger.error(f"Failed to get graph stats: {e}")
            return {"error": str(e)}

    def fulltext_search(
        self, index_name: str, query: str, limit: int = 10
    ) -> list[dict]:
        """Performs a full-text search on the given index."""
        if not self._driver:
            self.connect()

        with tracer.start_as_current_span("neo4j_fulltext_search") as span:
            span.set_attribute("db.index", index_name)
            span.set_attribute("db.query", query)
            try:
                results = self.query(
                    "CALL db.index.fulltext.queryNodes($index, $query) "
                    "YIELD node, score "
                    "RETURN node, score "
                    "LIMIT $limit",
                    {"index": index_name, "query": query, "limit": limit},
                )
                span.set_attribute("db.results_count", len(results))
                return results
            except Exception as e:
                logger.error(f"Full-text search failed: {e}")
                span.record_exception(e)
                raise

    def export_cypher(self) -> str:
        """Exports all nodes and relationships as Cypher CREATE statements."""
        if not self._driver:
            self.connect()

        lines = []

        with tracer.start_as_current_span("neo4j_export"):
            # Export nodes
            nodes = self.query(
                "MATCH (n) RETURN labels(n) as labels, properties(n) as props"
            )
            for node in nodes:
                label_str = ":".join(node["labels"])
                props = node["props"]
                # Escape string values
                prop_parts = []
                for k, v in props.items():
                    if isinstance(v, str):
                        escaped = v.replace("\\", "\\\\").replace("'", "\\'").replace("\n", "\\n")
                        prop_parts.append(f"{k}: '{escaped}'")
                    elif v is None:
                        continue
                    else:
                        prop_parts.append(f"{k}: {v}")
                props_str = ", ".join(prop_parts)
                lines.append(f"CREATE (:{label_str} {{{props_str}}});")

            # Export relationships
            rels = self.query(
                "MATCH (a)-[r]->(b) "
                "RETURN labels(a) as a_labels, properties(a) as a_props, "
                "a.id as a_id, type(r) as rel_type, properties(r) as rel_props, "
                "labels(b) as b_labels, properties(b) as b_props, b.id as b_id"
            )
            for rel in rels:
                a_label = ":".join(rel["a_labels"])
                b_label = ":".join(rel["b_labels"])
                rel_type = rel["rel_type"]
                a_id = rel.get("a_id", "")
                b_id = rel.get("b_id", "")

                # Use id-based matching for relationship creation
                if a_id and b_id:
                    lines.append(
                        f"MATCH (a:{a_label} {{id: '{a_id}'}}), (b:{b_label} {{id: '{b_id}'}}) "
                        f"CREATE (a)-[:{rel_type}]->(b);"
                    )

            return "\n".join(lines)

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
