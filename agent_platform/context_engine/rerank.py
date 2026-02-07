"""
Reranker component using FlashRank.
"""
import logging
from typing import Any

from flashrank import Ranker, RerankRequest
from opentelemetry import trace

logger = logging.getLogger(__name__)
tracer = trace.get_tracer(__name__)

class Reranker:
    def __init__(self, model_name: str = "ms-marco-TinyBERT-L-2-v2"):
        # ms-marco-TinyBERT-L-2-v2 is the default fast model (approx 4MB)
        self.ranker = Ranker(model_name=model_name)
        logger.info(f"Reranker initialized with model: {model_name}")

    def rerank(self, query: str, documents: list[dict[str, Any]], top_k: int = 5) -> list[dict[str, Any]]:
        """
        Reranks a list of documents based on the query.
        documents: List of dicts, each must have 'text' or 'description' (we map to 'text' for FlashRank)
        """
        with tracer.start_as_current_span("rerank_documents") as span:
            if not documents:
                return []

            # Map input docs to FlashRank format (id, text, meta)
            passages = []
            for i, doc in enumerate(documents):
                # ContextEngine uses 'description' as main text usually, or we might use payload
                # Use 'description' if present, else fallback
                text_content = doc.get("description") or doc.get("text") or str(doc)
                passages.append({
                    "id": doc.get("id", str(i)),
                    "text": text_content,
                    "meta": doc
                })

            span.set_attribute("rerank.input_count", len(passages))

            rerank_request = RerankRequest(query=query, passages=passages)
            results = self.ranker.rerank(rerank_request)

            # Sort by score desc and take top_k
            # FlashRank returns list of formatted dicts with 'score'

            # Reconstruct original doc structure with new score
            reranked_docs = []
            for res in results[:top_k]:
                original_doc = res["meta"]
                original_doc["rerank_score"] = res["score"]
                reranked_docs.append(original_doc)

            span.set_attribute("rerank.output_count", len(reranked_docs))
            return reranked_docs
