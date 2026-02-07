import datetime
import os

import google.generativeai as genai
from google.ai.generativelanguage_v1beta.types import content
from google.generativeai import caching

api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
genai.configure(api_key=api_key)

print("--- Testing Embeddings ---")
try:
    # Try with gemini-embedding-001
    model = "models/gemini-embedding-001"
    print(f"Embedding with {model}...")
    res = genai.embed_content(
        model=model,
        content="Hello world",
        task_type="retrieval_document"
    )
    print("Embedding success. Length:", len(res['embedding']))
except Exception as e:
    print("Embedding failed:", e)


print("\n--- Testing Context Caching ---")
try:
    # Explicitly constructing Content objects if needed,
    # but let's try strict dict structure first as per some examples.
    # The error "Message must be initialized with a dict" implies we passed a list where a dict was expected or vice versa?
    # caching.CachedContent.create(contents=...)

    # Try explicit Protobuf type construction if simple dicts fail
    valid_content = content.Content(
        parts=[content.Part(text="This is valid content for caching.")]
    )

    print("Creating cache...")
    cache = caching.CachedContent.create(
        model="models/gemini-1.5-flash-001",
        display_name="test_cache_debug",
        contents=[valid_content],
        ttl=datetime.timedelta(minutes=5)
    )
    print("Cache created:", cache.name)

    # Cleanup
    cache.delete()
    print("Cache deleted.")

except Exception as e:
    print("Caching failed:", e)
