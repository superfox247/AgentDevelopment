
from google.adk.models import Gemini
try:
    g = Gemini(model="gemini-1.5-flash", stream=True)
    print("Success with stream=True")
except Exception as e:
    print(f"Failed with stream=True: {e}")

try:
    g = Gemini(model="gemini-1.5-flash", parameters={"stream": True})
    print("Success with parameters={'stream': True}")
except Exception as e:
    print(f"Failed with parameters: {e}")
