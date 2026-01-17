
try:
    from google.adk.artifacts.file_artifact_service import (
        FileArtifactService,  # noqa: F401
    )
    print("SUCCESS: FileArtifactService imported successfully")
except Exception as e:
    print(f"FAILURE: {e}")
