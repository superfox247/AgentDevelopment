"""
Debugging tools for Agentic Operations.

Tools exposed to agents (like the SRE/Debug agent) to allow them to
inspect the state of the system or other agents.
"""

import logging
import urllib.error
import urllib.request

logger = logging.getLogger(__name__)


def fetch_container_logs(container_name: str, tail: int = 50) -> str:
    """
    Fetches the recent logs of a specific Docker container.
    Useful for self-diagnosis when a sub-agent fails.

    Args:
        container_name: The name of the container (e.g. 'course_creator-image_generator')
        tail: Number of lines to retrieve (default: 50)

    Returns:
        String containing the logs or an error message.
    """
    # The Dashboard API runs on the host at port 8010.
    # From inside Docker, we use host.docker.internal
    # If running on host (dev), we use localhost

    # Simple heuristic: try host.docker.internal first, then localhost
    urls = [
        f"http://host.docker.internal:8010/api/logs/{container_name}?tail={tail}",
        f"http://localhost:8010/api/logs/{container_name}?tail={tail}",
    ]

    for url in urls:
        try:
            logger.info(f"Attempting to fetch logs from: {url}")
            with urllib.request.urlopen(url, timeout=2) as response:
                if response.status == 200:
                    # The endpoint streams, but read() will get it all if short
                    # or we can just read chunk. For 'tail', it returns text.
                    return response.read().decode("utf-8")
        except urllib.error.URLError:
            continue
        except Exception as e:
            return f"Error fetching logs: {e!s}"

    return "Failed to connect to Log Service (Dashboard API). Is it running?"
