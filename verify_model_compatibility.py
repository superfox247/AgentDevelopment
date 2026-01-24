import sys
from pathlib import Path
sys.path.append(str(Path.cwd()))

from schemas.models.catalogue import ModelInfo

try:
    m = ModelInfo(
        name="models/test",
        display_name="Test",
        description="Desc",
        input_token_limit=100,
        output_token_limit=100,
        top_p=0.9,
        temperature=0.5
    )
    print("ModelInfo Init Success")
    print(m.model_dump())
except Exception as e:
    print(f"ModelInfo Init Failed: {e}")
