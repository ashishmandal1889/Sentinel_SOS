"""
Sentinel SOS - Emergency Contact Service.

Manages emergency contacts for citizens with strict ownership validation.
"""

from typing import List, Optional
from sqlalchemy.orm import Session
from app.core.exceptions import EntityNotFoundException, ForbiddenException
from app.models.sql.contact import EmergencyContact
from app.repositories.contact_repository import ContactRepository
from app.schemas.contact import ContactCreate, ContactUpdate


class ContactService:
    def __init__(self, db: Session):
        self.db = db
        self.contact_repo = ContactRepository(db)

    def list_contacts(self, user_id: str) -> List[EmergencyContact]:
        return self.contact_repo.list_by_user(user_id)

    def create_contact(self, user_id: str, data: ContactCreate) -> EmergencyContact:
        contact = EmergencyContact(
            user_id=user_id,
            contact_name=data.contact_name,
            relationship_label=data.relationship_label,
            phone_number=data.phone_number,
            email=data.email,
            priority_order=data.priority_order,
            is_active=True,
        )
        return self.contact_repo.create(contact)

    def delete_contact(self, user_id: str, contact_id: str) -> None:
        contact = self.contact_repo.get_by_id_and_user(contact_id, user_id)
        if not contact:
            raise EntityNotFoundException("EmergencyContact", contact_id)
        self.contact_repo.delete(contact)
