# Sentinel SOS — API Reference (v1)

All v1 endpoints are prefixed with `/api/v1`. Interactive OpenAPI Swagger UI is accessible at `/docs`.

---

## 1. Health & Diagnostics

### `GET /api/v1/health`
Liveness probe.
- **Response**: `200 OK`
```json
{
  "status": "ok",
  "app_name": "Sentinel SOS Emergency Response API",
  "environment": "development",
  "timestamp": "2026-10-11T11:20:00Z"
}
```

### `GET /api/v1/health/readiness`
Readiness probe verifying SQL and MongoDB database connectivity.
- **Response**: `200 OK`
```json
{
  "status": "ready",
  "uptime_seconds": 124.5,
  "checks": {
    "sql_database": "connected",
    "mongo_database": "connected"
  },
  "version": "1.0.0",
  "environment": "development"
}
```

---

## 2. Authentication

### `POST /api/v1/auth/register`
Enrolls a new citizen or responder user.
- **Request**:
```json
{
  "email": "citizen@example.com",
  "full_name": "John Doe",
  "phone_number": "+12345678901",
  "password": "StrongPassword123!",
  "role": "citizen"
}
```
- **Response**: `201 Created`
```json
{
  "access_token": "eyJhbGciOiJIUzI1...",
  "token_type": "bearer",
  "expires_in_minutes": 60,
  "role": "citizen",
  "user_id": "060d5b4a-b5e1-4c17-91a1-3fc5e8e89fbc"
}
```

### `POST /api/v1/auth/login`
Authenticates existing credentials.
- **Request**:
```json
{
  "email": "citizen@example.com",
  "password": "StrongPassword123!"
}
```

### `GET /api/v1/auth/me`
Retrieves identity of the caller from the supplied Bearer token.

---

## 3. SOS Emergency Lifecycle

### `POST /api/v1/sos`
Initiates a new SOS emergency request.
- **Headers**: `Authorization: Bearer <TOKEN>`
- **Request**:
```json
{
  "emergency_type": "MEDICAL",
  "latitude": 37.7749,
  "longitude": -122.4194,
  "accuracy_meters": 4.5,
  "description": "Severe difficulty breathing and chest pain.",
  "client_request_id": "req-uuid-client-12345"
}
```
- **Response**: `201 Created`
```json
{
  "incident_id": "inc_a8f9c102b4d1",
  "status": "CREATED",
  "created_at": "2026-10-11T11:25:00Z",
  "location_status": "VERIFIED",
  "message": "Emergency incident registered successfully. Responder matching in progress."
}
```

### `GET /api/v1/sos/{incident_id}`
Retrieves current incident status and telemetry details.

### `GET /api/v1/sos/{incident_id}/events`
Returns chronological audit events log for the incident.

### `POST /api/v1/sos/{incident_id}/cancel?reason=False+alarm`
Cancels the emergency incident.

---

## 4. Responder Management & Dispatch

### `POST /api/v1/responders/register`
Registers the authenticated user with a responder profile and emergency qualifications.

### `PATCH /api/v1/responders/location`
Pushes live GPS coordinates and operational availability.
- **Request**:
```json
{
  "latitude": 37.7833,
  "longitude": -122.4167,
  "status": "AVAILABLE"
}
```

### `GET /api/v1/dispatch/nearby?lat=37.7749&lon=-122.4194&emergency_type=MEDICAL`
Searches verified responders within coverage radius sorted by proximity.

### `POST /api/v1/dispatch/assignments/{assignment_id}/respond`
Accepts or declines a dispatched assignment (`"ACCEPT"` or `"DECLINE"`).

---

## 5. Emergency Contacts

- `GET /api/v1/contacts`: Returns list of caller's active emergency contacts.
- `POST /api/v1/contacts`: Creates an emergency contact.
- `DELETE /api/v1/contacts/{contact_id}`: Removes an emergency contact.
