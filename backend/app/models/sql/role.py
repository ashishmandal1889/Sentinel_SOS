"""
Sentinel SOS - Role and Permission SQL Models.
"""

from sqlalchemy import Column, String, ForeignKey, Table
from sqlalchemy.orm import relationship
from app.db.sql import Base
from app.models.sql.base import UUIDPrimaryKeyMixin, TimestampMixin


class Role(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "roles"

    name = Column(String(50), unique=True, nullable=False, index=True)  # e.g., 'citizen', 'responder', 'admin'
    description = Column(String(255), nullable=True)

    users = relationship("User", back_populates="role")
