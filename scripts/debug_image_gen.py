import requests
import json

def test_gen():
    url = "http://localhost:8010/api/generate/image"
    payload = {
        "prompt": "A small red cube",
        "model": "models/imagen-4.0-generate-001",
        "session_id": "debug-session-123"
    }
    
    try:
        print("Sending request...")
        res = requests.post(url, json=payload, timeout=30)
        print(f"Status: {res.status_code}")
        try:
            print(json.dumps(res.json(), indent=2))
        except:
            print("Response text:", res.text)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_gen()
