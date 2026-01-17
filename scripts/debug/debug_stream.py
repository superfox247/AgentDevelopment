import sys

import requests


def debug_stream() -> None:
    url = "http://localhost:5173/api/benchmark/stream"
    print(f"Connecting to {url}...")

    try:
        with requests.get(url, stream=True) as r:
            print(f"Status Code: {r.status_code}")
            print("--- Stream Start ---")
            for chunk in r.iter_content(chunk_size=None):
                if chunk:
                    sys.stdout.buffer.write(chunk)
                    sys.stdout.flush()
            print("\n--- Stream End ---")

    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    debug_stream()
