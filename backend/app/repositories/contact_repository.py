"""
Sentinel SOS - Emergency Contact Repository.

Manages emergency contacts belonging to citizens.
"""

from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.sql.contact import EmergencyContact


class ContactRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id_and_user(self, contact_id: str, user_id: str) -> Optional[EmergencyContact]:
        return (
            self.db.query(EmergencyContact)
            .filter(EmergencyContact.id == contact_id, EmergencyContact.user_id == user_id)
            .first()
        )

    def list_by_user(self, user_id: str) -> List[EmergencyContact]:
        return (
            self.db.query(EmergencyContact)
            .filter(EmergencyContact.user_id == user_id, EmergencyContact.is_active == True)
            .order_by(EmergencyContact.priority_order.asc())
            .all()
        )

    def create(self, contact: EmergencyContact) -> EmergencyContact:
        self.db.add(contact)
        self.db.commit()
        self.db.refresh(contact)
        return contact

    def delete(self, contact: EmergencyContact) -> None:
        self.db.delete(contact)
        self.db.commit()
