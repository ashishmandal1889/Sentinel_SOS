"""
Sentinel SOS - Emergency Contact SQL Model.
"""

from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from app.db.sql import Base
from app.models.sql.base import TimestampMixin, UUIDPrimaryKeyMixin


class EmergencyContact(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "emergency_contacts"

    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    contact_name = Column(String(255), nullable=False)
    relationship_label = Column(String(64), nullable=False)  # Parent, Spouse, Sibling, Friend
    phone_number = Column(String(32), nullable=False)
    email = Column(String(255), nullable=True)
    priority_order = Column(Integer, default=1, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)

    user = relationship("User", back_populates="contacts")
