import asyncio
import httpx
import json
import sys

BASE_URL = "http://localhost:8010"

async def check_endpoint(client, path, method="GET", payload=None):
    url = f"{BASE_URL}{path}"
    print(f"Checking {method} {url}...")
    try:
        if method == "GET":
            response = await client.get(url, timeout=10.0)
        else:
            response = await client.post(url, json=payload, timeout=10.0)
        
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            try:
                data = response.json()
                # Print a summary or snippet
                data_str = json.dumps(data, indent=2)
                if len(data_str) > 1000:
                    print(f"Response (truncated): {data_str[:1000]}...")
                else:
                    print(f"Response: {data_str}")
                return True
            except Exception as e:
                print(f"Failed to parse JSON: {e}")
                print(f"Raw text: {response.text[:200]}")
        else:
            print(f"Error Response: {response.text[:500]}")
            return False
            
    except Exception as e:
        print(f"Request failed: {e}")
        return False

async def main():
    async with httpx.AsyncClient() as client:
        # Check Status
        print("\n--- System Status ---")
        if not await check_endpoint(client, "/api/status"):
            print("System Status Check Failed!")
        
        # Check Models List
        print("\n--- Available Models ---")
        if not await check_endpoint(client, "/api/models"):
            print("Models List Failed!")
            
        # Check Diagnostics (might take longer)
        print("\n--- Diagnostics ---")
        if not await check_endpoint(client, "/api/diagnostics/models"):
             print("Diagnostics Check Failed!")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
