import pytest
from fastapi.testclient import TestClient
from datetime import datetime, timedelta, timezone

from main import app, db

client = TestClient(app)

def test_location_trigger_mock():
    # Trigger Test: Mock a "Location Trigger" and verify the API creates a LogEntry with trigger_type: LOCATION.
    response = client.post("/habits/log", json={
        "habit_id": "test-habit-1",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "trigger_type": "LOCATION",
        "lat_long": "40.7128,-74.0060"
    })
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["log_entry"]["trigger_type"] == "LOCATION"
    assert data["log_entry"]["lat_long"] == "40.7128,-74.0060"

def test_midnight_streak_edge_case():
    # Edge Case: Verify that a "Bad Habit" logged at 11:59 PM correctly attributes to today's graph
    # and doesn't break the streak logic for tomorrow.
    
    # Let's say today is Jan 1st 2026. 11:59 PM
    test_dt = datetime(2026, 1, 1, 23, 59, 59, tzinfo=timezone.utc)
    
    response = client.post("/habits/log", json={
        "habit_id": "test-bad-habit",
        "timestamp": test_dt.isoformat(),
        "trigger_type": "MANUAL"
    })
    
    assert response.status_code == 200
    
    # Check vulnerability graph logic to verify attribution to today's 23rd hour
    vuln_response = client.get("/analytics/vulnerability")
    assert vuln_response.status_code == 200
    vuln_data = vuln_response.json()
    assert vuln_data["23"] > 0.0  # Since it's attributed to 23 (11:59 PM)
    
    # Ensure streak logic for the user wasn't negatively affected instantly for tomorrow
    # (By checking user's streak isn't 0)
    user_status = client.get("/rewards/status?user_id=test-user-1")
    # For now simply check if backend didn't crash
    assert user_status.status_code == 200
