import requests
import time

try:
    print("Creating habit...")
    r1 = requests.post("http://localhost:8000/habits", json={"name": "test new", "category": "GOOD", "target_daily": 1})
    print("POST", r1.status_code, r1.text)

    print("Fetching habits...")
    r2 = requests.get("http://localhost:8000/habits?user_id=test-user-1")
    print("GET", r2.status_code, r2.text)
except Exception as e:
    print(e)
