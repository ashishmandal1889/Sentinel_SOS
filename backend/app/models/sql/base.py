"""
Sentinel SOS - Base SQL Model.

Provides timestamp tracking and standard identifier mixins for all SQL entities.
"""

from datetime import datetime, timezone
import uuid
from sqlalchemy import Column, DateTime, String
from app.db.sql import Base


class TimestampMixin:
    """Provides created_at and updated_at UTC timestamps."""
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )


class UUIDPrimaryKeyMixin:
    """Provides a standard string UUID primary key."""
    id = Column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        index=True,
    )
