import requests
import time

try:
    print("Triggering /api/start-analysis...")
    response = requests.post("http://localhost:8000/api/start-analysis", timeout=5)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    
    time.sleep(2)
    
    print("\nChecking /api/analysis-status...")
    response = requests.get("http://localhost:8000/api/analysis-status", timeout=5)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")

except Exception as e:
    print(f"Error: {e}")
