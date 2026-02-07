from qdrant_client import QdrantClient
import agent_platform.config
client = QdrantClient(url="http://localhost:6333")
help(client.query_points)
