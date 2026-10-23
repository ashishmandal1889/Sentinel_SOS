"""
Sentinel SOS - Responder Management Endpoints.
"""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.core.dependencies import AuthenticatedUser, get_current_user, require_roles
from app.core.exceptions import EntityNotFoundException
from app.db.sql import get_db
from app.models.sql.responder import Responder
from app.repositories.responder_repository import ResponderRepository
from app.schemas.responder import (
    ResponderLocationUpdate,
    ResponderRegisterRequest,
    ResponderResponse,
    ResponderStatus,
)

router = APIRouter()


@router.post("/register", response_model=ResponderResponse, status_code=status.HTTP_201_CREATED)
def register_responder(
    payload: ResponderRegisterRequest,
    current_user: AuthenticatedUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Enrolls current authenticated user as an emergency responder."""
    repo = ResponderRepository(db)
    existing = repo.get_by_user_id(current_user.user_id)
    if existing:
        return existing

    responder = Responder(
        user_id=current_user.user_id,
        badge_number=payload.badge_number,
        qualifications=payload.qualifications,
        service_radius_km=payload.service_radius_km,
        status="AVAILABLE",
        is_verified=True,
    )
    return repo.create(responder)


@router.patch("/location", response_model=ResponderResponse)
def update_location(
    payload: ResponderLocationUpdate,
    current_user: AuthenticatedUser = Depends(require_roles(["responder", "admin"])),
    db: Session = Depends(get_db),
):
    """Updates responder GPS coordinates and operational availability."""
    repo = ResponderRepository(db)
    responder = repo.get_by_user_id(current_user.user_id)
    if not responder:
        raise EntityNotFoundException("Responder profile", current_user.user_id)

    status_str = payload.status.value if payload.status else None
    updated = repo.update_location(responder.id, payload.latitude, payload.longitude, status=status_str)
    return updated


@router.get("/me", response_model=ResponderResponse)
def get_responder_profile(
    current_user: AuthenticatedUser = Depends(require_roles(["responder", "admin"])),
    db: Session = Depends(get_db),
):
    """Retrieves authenticated responder's current telemetry profile."""
    repo = ResponderRepository(db)
    responder = repo.get_by_user_id(current_user.user_id)
    if not responder:
        raise EntityNotFoundException("Responder profile", current_user.user_id)
    return responder
