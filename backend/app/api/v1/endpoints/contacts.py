"""
Sentinel SOS - Citizen Emergency Contacts Endpoints.
"""

from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.core.dependencies import AuthenticatedUser, get_current_user
from app.db.sql import get_db
from app.schemas.contact import ContactCreate, ContactResponse
from app.services.contact_service import ContactService

router = APIRouter()


@router.get("", response_model=List[ContactResponse])
def get_user_contacts(
    current_user: AuthenticatedUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Lists trusted emergency contacts for current citizen."""
    service = ContactService(db)
    return service.list_contacts(current_user.user_id)


@router.post("", response_model=ContactResponse, status_code=status.HTTP_201_CREATED)
def create_user_contact(
    payload: ContactCreate,
    current_user: AuthenticatedUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Adds a new emergency contact."""
    service = ContactService(db)
    return service.create_contact(current_user.user_id, payload)


@router.delete("/{contact_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user_contact(
    contact_id: str,
    current_user: AuthenticatedUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Deletes an emergency contact."""
    service = ContactService(db)
    service.delete_contact(current_user.user_id, contact_id)
    return None
