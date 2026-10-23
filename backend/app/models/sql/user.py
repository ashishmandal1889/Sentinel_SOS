"""
Sentinel SOS - User SQL Model.
"""

from sqlalchemy import Boolean, Column, ForeignKey, String
from sqlalchemy.orm import relationship
from app.db.sql import Base
from app.models.sql.base import TimestampMixin, UUIDPrimaryKeyMixin


class User(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "users"

    email = Column(String(255), unique=True, nullable=False, index=True)
    full_name = Column(String(255), nullable=False)
    phone_number = Column(String(32), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)

    role_id = Column(String(36), ForeignKey("roles.id"), nullable=True)
    role = relationship("Role", back_populates="users")

    # Relationships
    contacts = relationship("EmergencyContact", back_populates="user", cascade="all, delete-orphan")
    responder_profile = relationship("Responder", back_populates="user", uselist=False)
