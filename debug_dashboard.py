
import sys
from pathlib import Path

# Add root to path
ROOT_DIR = Path(__file__).parent
sys.path.append(str(ROOT_DIR))

try:
    import docker
    client = docker.from_env()
    print("Docker client created.")
    containers = client.containers.list()
    print(f"Found {len(containers)} containers.")
    for c in containers:
        print(f" - {c.name} ({c.status}) image={c.image.tags}")

    # Test imports
    from tools.dashboard.models import DockerContainerInfo, DockerStatsResponse
    print("Models imported.")

    container_infos = []
    for c in containers:
        info = DockerContainerInfo(
            id=c.short_id,
            name=c.name,
            status=c.status,
            image=c.image.tags[0] if c.image.tags else "unknown",
        )
        container_infos.append(info)
    
    response = DockerStatsResponse(containers=container_infos)
    print("DockerStatsResponse created successfully.")
    print(response.model_dump())

except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
