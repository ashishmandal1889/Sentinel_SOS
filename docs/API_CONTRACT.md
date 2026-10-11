# SentinelSOS API Contract

## 1. Purpose

This document defines how the SentinelSOS frontend, backend, and machine learning components will communicate. The team should review and agree on the contract before completing integration.

## 2. Component Responsibilities

- Frontend: Displays the user interface and sends requests to the backend.
- Backend: Handles API requests, authentication, data storage, and communication with ML services.
- Machine Learning: Analyzes supported input data and returns safety risk predictions.
- Integration and Testing: Checks API compatibility, error handling, and system behavior.

## 3. Proposed API Endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| POST | /api/auth/register | Register a user |
| POST | /api/auth/login | Authenticate a user |
| GET | /api/health | Check backend availability |
| POST | /api/safety/predict | Request an ML-based safety risk prediction |
| POST | /api/sos | Create an SOS incident and initiate the configured alert workflow |

These endpoints are proposals and must be confirmed by the backend developer.

## 4. Proposed Safety Prediction Response

Example response:

    {
      "risk_level": "moderate",
      "score": 0.65,
      "model_version": "v1"
    }

The ML developer must confirm the input features, score meaning, output fields, and model versioning. A model prediction must not be treated as a guarantee of safety.

## 5. Error Handling

The backend should return a consistent error format, for example:

    {
      "detail": "A descriptive error message"
    }

The team must agree on HTTP status codes and validation rules.

## 6. SOS Reliability

- SOS handling must not depend on a successful ML prediction.
- ML failures must not prevent the system from attempting the configured emergency workflow.
- Tests must use mocked notifications and must never contact real emergency services.
- The backend must clearly report whether an SOS request was accepted and whether alert delivery is confirmed.

## 7. Team Review

- Member 1: Confirm ML input and output requirements.
- Member 2: Confirm frontend API requirements.
- Member 3: Confirm backend endpoints, request schemas, responses, and status codes.
- Member 4: Coordinate review, integration tests, and contract updates.

## 8. Status

Draft — pending team review and approval.