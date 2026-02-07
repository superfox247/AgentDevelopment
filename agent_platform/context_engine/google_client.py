"""
Google Client for Context Engine (v2 - google-genai SDK).
Handles Embeddings (gemini-embedding-001) and Context Caching.
"""
import logging
import os
from typing import Any

from google import genai
from google.genai import types
from opentelemetry import trace

# Setup logger
logger = logging.getLogger(__name__)
tracer = trace.get_tracer(__name__)

class GoogleClient:
    def __init__(self):
        self.api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GOOGLE_API_KEY or GEMINI_API_KEY not found in environment variables.")

        # Initialize the new v2 Client
        self.client = genai.Client(api_key=self.api_key)

        self.embedding_model = "models/gemini-embedding-001"
        self.cache_model = "models/gemini-pro-latest" # Verified supported

        logger.info(f"GoogleClient initialized (v2) with embed_model: {self.embedding_model}")

    def embed_content(self, text: str, task_type: str = "retrieval_document") -> list[float]:
        """
        Generates embeddings using the new google-genai SDK.
        """
        with tracer.start_as_current_span("google_embed_content") as span:
            try:
                # task_type mapping if necessary, or pass as config
                # The new SDK might handle task_type differently or auto-infer.
                # For basic embedding, we pass contents.

                response = self.client.models.embed_content(
                    model=self.embedding_model,
                    contents=text,
                    config=types.EmbedContentConfig(
                        task_type=task_type,
                        title="Code Snippet" if task_type == "retrieval_document" else None
                    )
                )

                # Extract vector
                embedding = response.embeddings[0].values
                span.set_attribute("embedding.length", len(embedding))
                return embedding
            except Exception as e:
                logger.error(f"Failed to generate embedding: {e}")
                span.record_exception(e)
                raise

    def create_cache(self, cache_name: str, content: str, ttl_minutes: int = 60, system_instruction: str = "", model_name: str | None = None) -> Any:
        """
        Creates a Context Cache for the given content.
        """
        target_model = model_name or self.cache_model

        with tracer.start_as_current_span("google_create_cache") as span:
            try:
                # Current verified pattern: contents must be inside config
                cache = self.client.caches.create(
                    model=target_model,
                    config=types.CreateCachedContentConfig(
                        display_name=cache_name,
                        system_instruction=system_instruction,
                        ttl=f"{ttl_minutes * 60}s",
                        contents=[
                            types.Content(
                                role="user",
                                parts=[types.Part(text=content)]
                            )
                        ]
                    )
                )
                logger.info(f"Created cache: {cache.name} with model {target_model}")
                return cache
            except Exception as e:
                logger.error(f"Failed to create cache: {e}")
                span.record_exception(e)
                raise

    def generate_with_cache(self, cache_name: str, prompt: str, model_name: str | None = None) -> str:
        """
        Generates content using a specific cache.
        Replaces 'get_generative_model_from_cache'.
        """
        target_model = model_name or self.cache_model

        with tracer.start_as_current_span("google_generate_cached") as span:
            try:
                response = self.client.models.generate_content(
                    model=target_model,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        cached_content=cache_name
                    )
                )
                return response.text
            except Exception as e:
                logger.error(f"Failed to generate from cache: {e}")
                span.record_exception(e)
                raise
