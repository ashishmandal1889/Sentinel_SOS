"""
Sentinel SOS - Emergency (SOS) Service.

Manages emergency lifecycle, state machine transitions, audit trail recording,
and duplicate submission protection.
"""

from datetime import datetime, timezone
import uuid
from typing import Any, Dict, List, Optional
from app.core.exceptions import DuplicateRequestException, IncidentStateException
from app.core.logging import logger
from app.repositories.incident_repository import IncidentRepository
from app.schemas.incident import IncidentStatus, SOSCreateRequest, SOSCreateResponse

# State Machine Transition Table
VALID_TRANSITIONS = {
    IncidentStatus.CREATED: [IncidentStatus.NOTIFYING, IncidentStatus.CANCELLED],
    IncidentStatus.NOTIFYING: [IncidentStatus.ACKNOWLEDGED, IncidentStatus.NO_RESPONDER_AVAILABLE, IncidentStatus.CANCELLED],
    IncidentStatus.ACKNOWLEDGED: [IncidentStatus.DISPATCHED, IncidentStatus.CANCELLED],
    IncidentStatus.DISPATCHED: [IncidentStatus.ON_THE_WAY, IncidentStatus.ESCALATED, IncidentStatus.CANCELLED],
    IncidentStatus.ON_THE_WAY: [IncidentStatus.ARRIVED, IncidentStatus.ESCALATED, IncidentStatus.CANCELLED],
    IncidentStatus.ARRIVED: [IncidentStatus.RESOLVED, IncidentStatus.ESCALATED],
    IncidentStatus.RESOLVED: [IncidentStatus.CLOSED],
    IncidentStatus.NO_RESPONDER_AVAILABLE: [IncidentStatus.ESCALATED, IncidentStatus.CLOSED],
    IncidentStatus.ESCALATED: [IncidentStatus.DISPATCHED, IncidentStatus.CLOSED],
    IncidentStatus.CANCELLED: [],
    IncidentStatus.CLOSED: [],
}

# Duplicate protection cache (client_request_id -> incident_id)
_PROCESSED_CLIENT_REQUESTS: Dict[str, str] = {}


class SOSService:
    def __init__(self, incident_repo: Optional[IncidentRepository] = None):
        self.incident_repo = incident_repo or IncidentRepository()

    def create_sos(self, citizen_id: str, payload: SOSCreateRequest) -> SOSCreateResponse:
        # 1. Idempotency check
        if payload.client_request_id and payload.client_request_id in _PROCESSED_CLIENT_REQUESTS:
            existing_id = _PROCESSED_CLIENT_REQUESTS[payload.client_request_id]
            logger.info(f"Duplicate SOS request detected with client_request_id={payload.client_request_id}. Returning existing incident {existing_id}.")
            existing = self.incident_repo.get_incident(existing_id)
            if existing:
                return SOSCreateResponse(
                    incident_id=existing["incident_id"],
                    status=existing["status"],
                    created_at=existing["created_at"],
                    location_status="ESTIMATED",
                    message="Duplicate emergency request recognized. Returning existing active incident.",
                )

        # 2. Generate unique incident ID
        incident_id = f"inc_{uuid.uuid4().hex[:12]}"
        now = datetime.now(timezone.utc)

        # 3. Formulate document
        incident_doc = {
            "incident_id": incident_id,
            "citizen_id": citizen_id,
            "emergency_type": payload.emergency_type.value,
            "status": IncidentStatus.CREATED.value,
            "latitude": payload.latitude,
            "longitude": payload.longitude,
            "accuracy_meters": payload.accuracy_meters,
            "description": payload.description,
            "metadata": payload.metadata or {},
            "created_at": now,
            "updated_at": now,
        }

        # 4. Persist incident
        self.incident_repo.create_incident(incident_doc)

        # 5. Persist initial audit event
        self.incident_repo.add_event({
            "event_id": f"evt_{uuid.uuid4().hex[:10]}",
            "incident_id": incident_id,
            "event_type": "INCIDENT_CREATED",
            "from_status": None,
            "to_status": IncidentStatus.CREATED.value,
            "note": f"SOS initiated by citizen with type {payload.emergency_type.value}",
            "timestamp": now,
        })

        if payload.client_request_id:
            _PROCESSED_CLIENT_REQUESTS[payload.client_request_id] = incident_id

        return SOSCreateResponse(
            incident_id=incident_id,
            status=IncidentStatus.CREATED,
            created_at=now,
            location_status="VERIFIED",
            message="Emergency incident registered successfully. Responder matching in progress.",
        )

    def transition_status(self, incident_id: str, new_status: IncidentStatus, note: Optional[str] = None) -> Dict[str, Any]:
        incident = self.incident_repo.get_incident(incident_id)
        if not incident:
            raise IncidentStateException(
                f"Incident '{incident_id}' not found.",
                current_state="UNKNOWN",
                attempted_state=new_status.value,
            )

        current_status = IncidentStatus(incident["status"])
        allowed_next = VALID_TRANSITIONS.get(current_status, [])

        if new_status not in allowed_next:
            raise IncidentStateException(
                f"Invalid transition from {current_status.value} to {new_status.value}.",
                current_state=current_status.value,
                attempted_state=new_status.value,
            )

        self.incident_repo.update_incident_status(incident_id, new_status.value)

        now = datetime.now(timezone.utc)
        self.incident_repo.add_event({
            "event_id": f"evt_{uuid.uuid4().hex[:10]}",
            "incident_id": incident_id,
            "event_type": "STATUS_CHANGED",
            "from_status": current_status.value,
            "to_status": new_status.value,
            "note": note or f"Status transitioned to {new_status.value}",
            "timestamp": now,
        })

        incident["status"] = new_status.value
        incident["updated_at"] = now
        return incident

    def cancel_incident(self, incident_id: str, citizen_id: str, reason: Optional[str] = None) -> Dict[str, Any]:
        incident = self.incident_repo.get_incident(incident_id)
        if not incident:
            raise IncidentStateException(f"Incident '{incident_id}' not found.", current_state="UNKNOWN", attempted_state="CANCELLED")

        return self.transition_status(
            incident_id,
            IncidentStatus.CANCELLED,
            note=f"Cancelled by user. Reason: {reason or 'False alarm'}",
        )
