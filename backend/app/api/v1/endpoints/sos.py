"""
Sentinel SOS - Emergency Incident Management Endpoints.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, status
from app.core.dependencies import AuthenticatedUser, get_current_user
from app.core.exceptions import EntityNotFoundException, ForbiddenException
from app.schemas.incident import (
    IncidentDetailResponse,
    IncidentEventResponse,
    IncidentStatusUpdateRequest,
    SOSCreateRequest,
    SOSCreateResponse,
)
from app.integrations.ai.emergency_classifier import emergency_classifier
from app.services.sos_service import SOSService
from pydantic import BaseModel, Field

router = APIRouter()


class TriageRequest(BaseModel):
    description: str = Field(..., min_length=2, max_length=1000, description="Citizen's free-text emergency description.")


class TriageResponse(BaseModel):
    suggested_type: str
    confidence: float
    summary: str
    is_urgent: bool
    source: str


@router.post("", response_model=SOSCreateResponse, status_code=status.HTTP_201_CREATED)
def trigger_sos(
    payload: SOSCreateRequest,
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    """
    Submits a new citizen emergency SOS alert.
    Authenticates user, validates coordinates, enforces duplicate protection,
    persists incident in MongoDB, and triggers responder matching.
    """
    service = SOSService()
    return service.create_sos(citizen_id=current_user.user_id, payload=payload)


@router.get("/{incident_id}", response_model=IncidentDetailResponse)
def get_incident(
    incident_id: str,
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    """Retrieves current incident details."""
    service = SOSService()
    incident = service.incident_repo.get_incident(incident_id)
    if not incident:
        raise EntityNotFoundException("SOS Incident", incident_id)

    # Authorization: citizen who created it, assigned responder, or admin
    if current_user.role != "admin" and incident["citizen_id"] != current_user.user_id:
        raise ForbiddenException("You are not authorized to view this emergency incident.")

    return IncidentDetailResponse(
        incident_id=incident["incident_id"],
        citizen_id=incident["citizen_id"],
        emergency_type=incident["emergency_type"],
        status=incident["status"],
        latitude=incident["latitude"],
        longitude=incident["longitude"],
        accuracy_meters=incident.get("accuracy_meters"),
        address=incident.get("address"),
        description=incident.get("description"),
        created_at=incident["created_at"],
        updated_at=incident["updated_at"],
    )


@router.get("/{incident_id}/events", response_model=List[IncidentEventResponse])
def get_incident_events(
    incident_id: str,
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    """Retrieves the chronological audit event trail for an incident."""
    service = SOSService()
    incident = service.incident_repo.get_incident(incident_id)
    if not incident:
        raise EntityNotFoundException("SOS Incident", incident_id)

    if current_user.role != "admin" and incident["citizen_id"] != current_user.user_id:
        raise ForbiddenException("You are not authorized to view this incident event log.")

    events = service.incident_repo.get_events_by_incident(incident_id)
    return [
        IncidentEventResponse(
            event_id=e["event_id"],
            incident_id=e["incident_id"],
            event_type=e["event_type"],
            from_status=e.get("from_status"),
            to_status=e.get("to_status"),
            note=e.get("note"),
            timestamp=e["timestamp"],
        )
        for e in events
    ]


@router.post("/{incident_id}/cancel")
def cancel_incident(
    incident_id: str,
    reason: Optional[str] = None,
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    """Cancels an active SOS emergency."""
    service = SOSService()
    updated = service.cancel_incident(incident_id, current_user.user_id, reason=reason)
    return {"message": "Incident cancelled successfully.", "incident": updated}


@router.patch("/{incident_id}/status")
def update_incident_status(
    incident_id: str,
    payload: IncidentStatusUpdateRequest,
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    """Transitions incident status according to the valid state machine."""
    service = SOSService()
    updated = service.transition_status(incident_id, payload.status, note=payload.note)
    return {"message": f"Status updated to {payload.status.value}", "incident": updated}


@router.post("/triage", response_model=TriageResponse)
async def triage_emergency(
    payload: TriageRequest,
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    """
    AI-powered emergency classification and priority triage using Gemini.
    """
    result = await emergency_classifier.classify_emergency_text(payload.description)
    return TriageResponse(**result)
