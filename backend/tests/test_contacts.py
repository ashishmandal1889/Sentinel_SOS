"""
Sentinel SOS - Emergency Contacts Tests.
"""

def test_emergency_contacts_crud(client, citizen_auth_headers):
    # 1. List contacts (initially empty)
    list_res = client.get("/api/v1/contacts", headers=citizen_auth_headers)
    assert list_res.status_code == 200
    assert list_res.json() == []

    # 2. Add contact
    create_payload = {
        "contact_name": "Mom",
        "relationship_label": "Parent",
        "phone_number": "+15551234567",
        "priority_order": 1,
    }
    create_res = client.post("/api/v1/contacts", json=create_payload, headers=citizen_auth_headers)
    assert create_res.status_code == 201
    contact_id = create_res.json()["id"]

    # 3. List contacts now has 1
    list_res2 = client.get("/api/v1/contacts", headers=citizen_auth_headers)
    assert len(list_res2.json()) == 1

    # 4. Delete contact
    del_res = client.delete(f"/api/v1/contacts/{contact_id}", headers=citizen_auth_headers)
    assert del_res.status_code == 204
