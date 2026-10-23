"""
Sentinel SOS - Responder Repository.

Handles relational database queries and spatial filtering for Responders.
"""

from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.sql.responder import Responder


class ResponderRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, responder_id: str) -> Optional[Responder]:
        return self.db.query(Responder).filter(Responder.id == responder_id).first()

    def get_by_user_id(self, user_id: str) -> Optional[Responder]:
        return self.db.query(Responder).filter(Responder.user_id == user_id).first()

    def get_available_responders(self, emergency_type: str = "GENERAL") -> List[Responder]:
        return (
            self.db.query(Responder)
            .filter(Responder.status == "AVAILABLE")
            .filter(Responder.is_verified == True)
            .all()
        )

    def update_location(self, responder_id: str, lat: float, lon: float, status: Optional[str] = None) -> Optional[Responder]:
        responder = self.get_by_id(responder_id)
        if not responder:
            return None
        responder.current_latitude = lat
        responder.current_longitude = lon
        responder.location_updated_at = datetime.now(timezone.utc)
        if status:
            responder.status = status
        self.db.commit()
        self.db.refresh(responder)
        return responder

    def create(self, responder: Responder) -> Responder:
        self.db.add(responder)
        self.db.commit()
        self.db.refresh(responder)
        return responder
