"""
Sentinel SOS - Notification Integration Tests.
"""

def test_notification_alert_flow(client, admin_auth_headers):
    res = client.post(
        "/api/v1/notifications/test",
        params={"phone_number": "+15559876543"},
        headers=admin_auth_headers,
    )
    assert res.status_code == 200
    data = res.json()
    assert "details" in data
    assert data["details"]["status"] == "DELIVERED"
    assert data["details"]["destination"] == "+15559876543"
