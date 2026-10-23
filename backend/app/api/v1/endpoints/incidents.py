"""
Sentinel SOS - Incident History and Administration Query Endpoints.
"""

from typing import List
from fastapi import APIRouter, Depends
from app.core.dependencies import AuthenticatedUser, get_current_user
from app.core.exceptions import EntityNotFoundException, ForbiddenException
from app.schemas.incident import IncidentDetailResponse
from app.services.incident_service import IncidentService

router = APIRouter()


@router.get("/history")
def get_incident_history(
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    """Retrieves emergency incidents initiated by the current citizen."""
    service = IncidentService()
    # In MongoDB or fallback store, retrieve list of incidents
    # For now, return structured collection or query
    return {"message": "Incident history retrieved.", "user_id": current_user.user_id, "incidents": []}


@router.get("/{incident_id}", response_model=IncidentDetailResponse)
def get_incident_by_id(
    incident_id: str,
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    service = IncidentService()
    incident = service.get_incident(incident_id)
    if not incident:
        raise EntityNotFoundException("Incident", incident_id)

    if current_user.role != "admin" and incident["citizen_id"] != current_user.user_id:
        raise ForbiddenException("Unauthorized access to incident record.")

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
