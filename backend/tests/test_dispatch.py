"""
Sentinel SOS - Dispatch and Responder Matching Tests.
"""

def test_responder_registration_and_dispatch(client, responder_auth_headers, admin_auth_headers):
    # 1. Register responder
    reg_payload = {
        "badge_number": "MED-911",
        "qualifications": "MEDICAL,GENERAL",
        "service_radius_km": 20.0,
    }
    reg_res = client.post("/api/v1/responders/register", json=reg_payload, headers=responder_auth_headers)
    assert reg_res.status_code == 201
    responder_id = reg_res.json()["id"]

    # 2. Update location
    loc_res = client.patch(
        "/api/v1/responders/location",
        json={"latitude": 37.7749, "longitude": -122.4194, "status": "AVAILABLE"},
        headers=responder_auth_headers,
    )
    assert loc_res.status_code == 200

    # 3. Query nearby responders as admin
    nearby_res = client.get(
        "/api/v1/dispatch/nearby?lat=37.7750&lon=-122.4190&emergency_type=MEDICAL",
        headers=admin_auth_headers,
    )
    assert nearby_res.status_code == 200
    candidates = nearby_res.json()
    assert len(candidates) >= 1
    assert candidates[0]["responder_id"] == responder_id
