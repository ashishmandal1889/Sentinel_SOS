"""
Sentinel SOS - Responder and Qualification SQL Models.
"""

from datetime import datetime, timezone
from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from app.db.sql import Base
from app.models.sql.base import TimestampMixin, UUIDPrimaryKeyMixin


class Responder(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "responders"

    user_id = Column(String(36), ForeignKey("users.id"), unique=True, nullable=False)
    badge_number = Column(String(64), unique=True, nullable=True)
    status = Column(String(32), default="OFFLINE", nullable=False, index=True)  # AVAILABLE, BUSY, OFFLINE
    is_verified = Column(Boolean, default=False, nullable=False)
    service_radius_km = Column(Float, default=15.0, nullable=False)

    # Latest reported coordinates
    current_latitude = Column(Float, nullable=True)
    current_longitude = Column(Float, nullable=True)
    location_updated_at = Column(DateTime(timezone=True), nullable=True)

    # Qualified emergency types: e.g. "MEDICAL,FIRE,POLICE"
    qualifications = Column(String(255), default="GENERAL", nullable=False)

    user = relationship("User", back_populates="responder_profile")
    assignments = relationship("IncidentAssignment", back_populates="responder")
