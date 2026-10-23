"""
Sentinel SOS - Emergency Workflow Tests.
"""

def test_sos_creation_and_events(client, citizen_auth_headers):
    payload = {
        "emergency_type": "MEDICAL",
        "latitude": 37.7749,
        "longitude": -122.4194,
        "accuracy_meters": 5.0,
        "description": "Chest pain and shortness of breath.",
        "client_request_id": "test_req_unique_001",
    }

    # 1. Trigger SOS
    res = client.post("/api/v1/sos", json=payload, headers=citizen_auth_headers)
    assert res.status_code == 201
    data = res.json()
    assert "incident_id" in data
    assert data["status"] == "CREATED"
    incident_id = data["incident_id"]

    # 2. Duplicate submission with same client_request_id
    dup_res = client.post("/api/v1/sos", json=payload, headers=citizen_auth_headers)
    assert dup_res.status_code == 201
    assert dup_res.json()["incident_id"] == incident_id

    # 3. Retrieve incident details
    get_res = client.get(f"/api/v1/sos/{incident_id}", headers=citizen_auth_headers)
    assert get_res.status_code == 200
    assert get_res.json()["emergency_type"] == "MEDICAL"

    # 4. Retrieve event audit trail
    events_res = client.get(f"/api/v1/sos/{incident_id}/events", headers=citizen_auth_headers)
    assert events_res.status_code == 200
    events = events_res.json()
    assert len(events) >= 1
    assert events[0]["to_status"] == "CREATED"

    # 5. Cancel incident
    cancel_res = client.post(f"/api/v1/sos/{incident_id}/cancel?reason=Resolved", headers=citizen_auth_headers)
    assert cancel_res.status_code == 200
    assert cancel_res.json()["incident"]["status"] == "CANCELLED"


def test_invalid_coordinates(client, citizen_auth_headers):
    payload = {
        "emergency_type": "GENERAL",
        "latitude": 999.0,  # Invalid latitude
        "longitude": -122.4194,
    }
    res = client.post("/api/v1/sos", json=payload, headers=citizen_auth_headers)
    assert res.status_code == 422
