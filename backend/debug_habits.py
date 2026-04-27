from fastapi.testclient import TestClient
from main import app, db

client = TestClient(app)

print("Before:", db["habits"])
r1 = client.post("/habits", json={"name": "test new", "category": "GOOD", "target_daily": 1})
print("POST status:", r1.status_code)
print("POST res:", r1.json())

r2 = client.get("/habits?user_id=test-user-1")
print("GET status:", r2.status_code)
print("GET res:", r2.json())
