"""
Sentinel SOS - Incident Assignment and Audit Log SQL Models.
"""

from datetime import datetime, timezone
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from app.db.sql import Base
from app.models.sql.base import TimestampMixin, UUIDPrimaryKeyMixin


class IncidentAssignment(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "incident_assignments"

    incident_id = Column(String(64), nullable=False, index=True)  # Consistent ID across PostgreSQL and MongoDB
    responder_id = Column(String(36), ForeignKey("responders.id"), nullable=False, index=True)
    status = Column(String(32), default="OFFERED", nullable=False)  # OFFERED, ACCEPTED, DECLINED, ARRIVED, COMPLETED

    offered_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    responded_at = Column(DateTime(timezone=True), nullable=True)
    arrived_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)

    eta_seconds = Column(Integer, nullable=True)
    distance_meters = Column(Float, nullable=True)

    responder = relationship("Responder", back_populates="assignments")


class AuditLog(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "audit_logs"

    user_id = Column(String(36), nullable=True, index=True)
    action = Column(String(128), nullable=False, index=True)
    resource_type = Column(String(64), nullable=False)
    resource_id = Column(String(64), nullable=True)
    ip_address = Column(String(45), nullable=True)
    details = Column(Text, nullable=True)
