"""
Sentinel SOS - Dispatch and Assignment Endpoints.
"""

from typing import List
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from app.core.dependencies import AuthenticatedUser, get_current_user, require_roles
from app.core.exceptions import EntityNotFoundException
from app.db.sql import get_db
from app.models.sql.assignment import IncidentAssignment
from app.repositories.responder_repository import ResponderRepository
from app.schemas.responder import AssignmentActionRequest
from app.services.dispatch_service import DispatchService

router = APIRouter()


@router.get("/nearby")
def find_nearby_responders(
    lat: float = Query(..., ge=-90.0, le=90.0),
    lon: float = Query(..., ge=-180.0, le=180.0),
    emergency_type: str = Query("GENERAL"),
    current_user: AuthenticatedUser = Depends(require_roles(["admin", "responder"])),
    db: Session = Depends(get_db),
):
    """Finds eligible nearby emergency responders within their coverage radius."""
    service = DispatchService(db)
    return service.find_eligible_responders(lat, lon, emergency_type=emergency_type)


@router.post("/assign", status_code=status.HTTP_201_CREATED)
def assign_responder(
    incident_id: str,
    responder_id: str,
    current_user: AuthenticatedUser = Depends(require_roles(["admin"])),
    db: Session = Depends(get_db),
):
    """Dispatches an incident assignment to a selected responder."""
    service = DispatchService(db)
    assignment = service.assign_responder(incident_id, responder_id)
    return {"message": "Responder dispatched successfully.", "assignment_id": assignment.id}


@router.post("/assignments/{assignment_id}/respond")
def respond_to_assignment(
    assignment_id: str,
    payload: AssignmentActionRequest,
    current_user: AuthenticatedUser = Depends(require_roles(["responder", "admin"])),
    db: Session = Depends(get_db),
):
    """Accepts or declines a dispatched emergency assignment."""
    assignment = db.query(IncidentAssignment).filter(IncidentAssignment.id == assignment_id).first()
    if not assignment:
        raise EntityNotFoundException("Assignment", assignment_id)

    if payload.action.upper() == "ACCEPT":
        assignment.status = "ACCEPTED"
    elif payload.action.upper() == "DECLINE":
        assignment.status = "DECLINED"
    else:
        assignment.status = payload.action.upper()

    db.commit()
    db.refresh(assignment)
    return {"message": f"Assignment updated to {assignment.status}", "status": assignment.status}
