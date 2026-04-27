from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

print("Testing frontend identical POST request (no target_daily)...")
res = client.post("/habits", json={"name": "test frontend", "category": "GOOD"})
print("Status:", res.status_code)
print("Response:", res.json())
