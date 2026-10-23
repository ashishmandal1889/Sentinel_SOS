"""
Sentinel SOS - Authentication Tests.
"""

def test_register_and_login(client):
    reg_payload = {
        "email": "citizen_test@sentinel.org",
        "full_name": "Test Citizen",
        "phone_number": "+12345678901",
        "password": "SuperSecretPassword123!",
        "role": "citizen",
    }
    reg_res = client.post("/api/v1/auth/register", json=reg_payload)
    assert reg_res.status_code == 201
    data = reg_res.json()
    assert "access_token" in data
    assert data["role"] == "citizen"

    # Test login
    login_payload = {
        "email": "citizen_test@sentinel.org",
        "password": "SuperSecretPassword123!",
    }
    login_res = client.post("/api/v1/auth/login", json=login_payload)
    assert login_res.status_code == 200
    token = login_res.json()["access_token"]

    # Test /me
    me_res = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me_res.status_code == 200
    assert me_res.json()["email"] == "citizen_test@sentinel.org"


def test_login_invalid_password(client):
    res = client.post("/api/v1/auth/login", json={
        "email": "citizen_test@sentinel.org",
        "password": "WrongPassword!",
    })
    assert res.status_code == 401
